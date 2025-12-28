import os
from dotenv import load_dotenv
import google.generativeai as genai

# 載入 .env 裡的 API Key
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
    exit()

print(f"🔑 Using API Key: {api_key[:5]}...{api_key[-5:]}")

# 設定 API
genai.configure(api_key=api_key)

print("\n📡 Connecting to Google to list available models...\n")

try:
    found_any = False
    for m in genai.list_models():
        # 我們只關心能產生文字 (generateContent) 的模型
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found: {m.name}")
            found_any = True
            
    if not found_any:
        print("⚠️ No models found. Check your API Key permissions.")
        
except Exception as e:
    print(f"❌ Error listing models: {e}")