from app.llm import LLMClient


llm = LLMClient()

response = llm.generate(
    "Explain what an AI agent is in exactly three sentences."
)

print("\nLLM Response:")
print(response)