import json
from typing import Any

from app.llm import LLMClient
from app.models import Document
from app.response_formatter import format_response
from app.state import (
    AgentState,
    ToolCallRecord,
    ToolResultRecord,
)
from app.tools import (
    answer_question,
    extract_information,
    summarize_document,
)


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "extract_information",
            "description": (
                "Extract multiple explicitly requested fields or attributes "
                "from the document and return structured data. "
                "Use this when the user says things like 'extract', "
                "'list the following fields', or asks for multiple attributes. "
                "Do not use this for a single factual question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": (
                            "The fields that should be extracted "
                            "from the document."
                        ),
                    }
                },
                "required": ["fields"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_document",
            "description": (
                "Summarize the document and return its main findings. "
                "Use this for requests such as summary, briefing, overview, "
                "or key findings."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "answer_question",
            "description": (
                "Answer a specific factual question using only the document. "
                "Use this for questions such as What, Who, When, Where, Why, "
                "How, or Which. Do not use this for multi-field extraction."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": (
                            "The user's question about the document."
                        ),
                    }
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        },
    },
]


SYSTEM_PROMPT = """
You are TrainingDataAgent, an AI agent for processing government documents.

You have access to three tools:

1. extract_information
   Use ONLY when the user explicitly asks to extract multiple
   fields, attributes, entities, or structured information.

2. summarize_document
   Use when the user asks for a summary, briefing, overview,
   key findings, or similar document-level synthesis.

3. answer_question
   Use when the user asks a specific question about information
   contained in the document, including questions such as:
   What, Who, When, Where, Why, How, Which, or similar factual questions.

Tool selection rules:

- A specific factual question should normally use answer_question.
- A request for multiple named fields should use extract_information.
- A request for a document-level summary should use summarize_document.
- Use multiple tools only when the user's request genuinely requires
  multiple operations.

Grounding rules:

- Use only information supported by the document and tool results.
- Never add facts from your general knowledge.
- Never infer details that are not explicitly supported.
- If information is missing, say that it is not available in the document.

Final response rules:

- The final response will be generated from the tool results.
- Do not introduce new facts during the final response.
- Do not expand, reinterpret, or embellish the tool results.
- Preserve uncertainty or missing values returned by the tools.
"""


class TrainingDataAgent:
    """
    Agent that decides which document-processing tools to use
    and tracks execution through AgentState.
    """

    def __init__(
        self,
        llm: LLMClient | None = None,
        max_iterations: int = 5,
    ):
        self.llm = llm or LLMClient()
        self.max_iterations = max_iterations

    def _execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        document: Document,
    ) -> dict[str, Any]:

        if tool_name == "extract_information":
            return extract_information(
                document=document,
                fields=arguments["fields"],
            )

        if tool_name == "summarize_document":
            return summarize_document(
                document=document,
            )

        if tool_name == "answer_question":
            return answer_question(
                document=document,
                question=arguments["question"],
            )

        raise ValueError(
            f"Unknown tool requested by agent: {tool_name}"
        )

    def run(
        self,
        document: Document,
        user_request: str,
    ) -> AgentState:
        """
        Run the agent and return the complete execution state.
        """

        state = AgentState(
            user_request=user_request,
            document=document,
            status="running",
        )

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"User request:\n{user_request}\n\n"
                    f"Document source:\n{document.source}\n\n"
                    f"Document content:\n{document.text}"
                ),
            },
        ]

        try:
            for iteration in range(self.max_iterations):

                state.iteration = iteration

                response = self.llm.chat(
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                )

                tool_calls = response.message.tool_calls

                # The model has finished deciding what tools are needed.
                if not tool_calls:
                    state.final_response = format_response(state)
                    state.status = "completed"

                    return state

                messages.append(
                    response.message.model_dump(
                        exclude_none=True
                    )
                )

                for tool_call in tool_calls:

                    tool_name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)

                    print(
                        f"\n[Agent] Selected tool: {tool_name}"
                    )
                    print(
                        f"[Agent] Arguments: {arguments}"
                    )

                    call_record = ToolCallRecord(
                        tool_name=tool_name,
                        arguments=arguments,
                        iteration=iteration,
                        status="requested",
                    )

                    state.tool_calls.append(call_record)

                    try:
                        result = self._execute_tool(
                            tool_name=tool_name,
                            arguments=arguments,
                            document=document,
                        )

                        call_record.status = "completed"

                        state.tool_results.append(
                            ToolResultRecord(
                                tool_name=tool_name,
                                result=result,
                                iteration=iteration,
                            )
                        )

                        print(
                            "[Agent] Tool execution completed."
                        )

                        messages.append(
                            {
                                "role": "tool",
                                "content": json.dumps(
                                    result,
                                    ensure_ascii=False,
                                ),
                            }
                        )

                    except Exception as error:

                        call_record.status = "failed"

                        state.error = str(error)
                        state.status = "failed"

                        return state

            state.status = "failed"
            state.error = (
                "Agent exceeded maximum number of iterations."
            )

            return state

        except Exception as error:

            state.status = "failed"
            state.error = str(error)

            return state