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
        # 修正模型為 flash 以獲取更高額度
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        prompt = f"""
        現在日期時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
        使用者指令："{nl_time_str}"
        
        請解析指令並「僅」輸出一個 JSON 格式，不要包含 Markdown 標記：
        {{
          "title": "事件名稱",
          "date": "YYYY-MM-DD",
          "start_time": "HH:MM",
          "duration": 分鐘數字,
          "is_recurring": true/false,
          "is_flexible": true (若提及找時間/幫我排) / false (若指定幾點)
        }}
        """
        response = model.generate_content(prompt)
        
        # 提取 JSON 的強健邏輯
        text = response.text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except Exception as e:
        # 當額度爆掉或失敗時，回傳預設值讓前端不當機
        print(f"AI 解析失敗 (可能是 Quota 限制): {e}")
        return {
            "title": nl_time_str,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "start_time": "10:00",
            "duration": 60,
            "is_flexible": False
        }