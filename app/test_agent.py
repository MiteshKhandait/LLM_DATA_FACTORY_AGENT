from app.agent import TrainingDataAgent
from app.loaders import load_document


document = load_document(
    "data/input/test.docx"
)

agent = TrainingDataAgent()


requests = [
    "Extract the department, budget, target beneficiaries, and districts covered.",
    "Give me a concise summary of this document.",
    "What is the budget allocation?",
    "Create a concise briefing from this document. Include the department, budget allocation, target beneficiaries, and districts covered, and then summarize the main findings."
]


for request in requests:

    print("\n" + "=" * 70)
    print("USER REQUEST")
    print("=" * 70)

    print(request)

    print("\n" + "=" * 70)
    print("AGENT RESPONSE")
    print("=" * 70)

    try:
        state = agent.run(
            document=document,
            user_request=request,
        )

        print("\nFinal response:")
        print(state.final_response)

        print("\nStatus:")
        print(state.status)

        print("\nTool calls:")
        for call in state.tool_calls:
            print(call.tool_name)

        print("\nTool results:")
        for result in state.tool_results:
            print(result.tool_name)

    except Exception as error:
        print("ERROR:", error)