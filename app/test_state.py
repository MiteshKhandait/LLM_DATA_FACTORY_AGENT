from app.loaders import load_document
from app.state import (
    AgentState,
    ToolCallRecord,
    ToolResultRecord,
)


document = load_document(
    "data/input/test.docx"
)


state = AgentState(
    user_request="What is the budget allocation?",
    document=document,
    status="running",
)


print("\nInitial state:")
print(state)


tool_call = ToolCallRecord(
    tool_name="answer_question",
    arguments={
        "question": "What is the budget allocation?"
    },
    iteration=0,
    status="completed",
)

state.tool_calls.append(tool_call)


tool_result = ToolResultRecord(
    tool_name="answer_question",
    result={
        "answer": "Rs. 150 crore",
        "evidence": "Budget Allocation: Rs. 150 crore",
        "source": document.source,
    },
    iteration=0,
)

state.tool_results.append(tool_result)

state.iteration = 1
state.status = "completed"
state.final_response = "The budget allocation is Rs. 150 crore."


print("\nUpdated state:")
print(state)


print("\nTool calls:")
for call in state.tool_calls:
    print(call)


print("\nTool results:")
for result in state.tool_results:
    print(result)