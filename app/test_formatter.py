from app.loaders import load_document
from app.response_formatter import format_response
from app.state import (
    AgentState,
    ToolResultRecord,
)


document = load_document(
    "data/input/test.docx"
)


state = AgentState(
    user_request="What is the budget allocation?",
    document=document,
    status="completed",
)


state.tool_results.append(
    ToolResultRecord(
        tool_name="answer_question",
        result={
            "answer": "Rs. 150 crore",
            "evidence": "Budget Allocation: Rs. 150 crore",
            "source": document.source,
        },
        iteration=0,
    )
)


print(format_response(state))