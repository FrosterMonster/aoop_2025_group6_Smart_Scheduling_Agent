import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
    exit()

print(f"🔑 Testing API Key: {api_key[:5]}...{api_key[-3:]}")

try:
    genai.configure(api_key=api_key)
    
    print("\n📡 Connecting to Google to fetch available models...")
    models = genai.list_models()
    
    found_any = False
    print("\n✅ AVAILABLE MODELS:")
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"   - {m.name}")
            found_any = True
            
    if not found_any:
        print("❌ No models found that support 'generateContent'.")
        print("   This usually means the API key is valid but has no permissions.")
        print("   Check: Did you create the key in AI Studio (aistudio.google.com)?")

except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")