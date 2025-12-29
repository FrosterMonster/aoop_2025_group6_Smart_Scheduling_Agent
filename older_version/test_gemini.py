# test_gemini.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"🔑 API Key found: {'Yes' if api_key else 'No'}")

try:
    # Initialize the model directly
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    print("🤖 Sending test message to Gemini 1.5 Flash...")
    result = llm.invoke("Hello! Are you working?")
    
    print("-" * 20)
    print(f"✅ SUCCESS! Response: {result.content}")
    print("-" * 20)
    
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")