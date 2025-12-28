from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

resp = client.models.generate_content(
    model="models/gemini-flash-latest",
    contents="明天早上七點吃飯"
)

print(resp.text)
