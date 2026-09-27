import os

from dotenv import load_dotenv


load_dotenv()


ollama_host = os.getenv("OLLAMA_HOST")
model_name = os.getenv("MODEL_NAME")

print("Ollama host:", ollama_host)
print("Model name:", model_name)