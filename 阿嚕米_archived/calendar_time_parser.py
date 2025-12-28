import os
import json
import re
import google.generativeai as genai  # 注意：如果安裝的是新版，這行可能略有不同
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def parse_with_ai(nl_time_str: str):
    """使用 Gemini 解析意圖並回傳 JSON"""
    try:
        model = genai.GenerativeModel('gemini-pro-latest')
        prompt = f"""
        現在日期時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
        使用者指令："{nl_time_str}"
        
        請解析指令並嚴格輸出 JSON 格式，不要包含 ```json 等 Markdown 標記：
        - title: 事件名稱
        - date: YYYY-MM-DD
        - start_time: HH:MM
        - duration: 分鐘數字
        - is_recurring: true/false
        - is_flexible: 如果指令有具體時間點(如:五點)設為 false；如果要 AI "找時間"設為 true
        """
        response = model.generate_content(prompt)
        # 移除可能出現的 Markdown 標籤
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"AI 解析失敗: {e}")
        return None