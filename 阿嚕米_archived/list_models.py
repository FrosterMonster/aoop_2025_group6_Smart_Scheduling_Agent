import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models = genai.list_models()

print("=== Available Models ===")
for m in models:
    print(f"- {m.name}")
    print(f"  supported methods: {m.supported_generation_methods}")
