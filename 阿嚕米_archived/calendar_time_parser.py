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
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        現在日期時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
        使用者指令："{nl_time_str}"
        請解析並輸出 JSON：
        - title: 事件名稱
        - date: YYYY-MM-DD
        - start_time: HH:MM
        - duration: 分鐘(數字)
        - is_recurring: 布林值
        """
        response = model.generate_content(prompt)
        # 簡單過濾掉 Markdown 標籤
        clean_json = re.sub(r'```json|```', '', response.text).strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"AI 解析失敗: {e}")
        return None