import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Fetching your available Llama models...\n")
models = client.models.list().data

for model in models:
    if "llama" in model.id.lower():
        print(f"✅ Use this exact string: {model.id}")