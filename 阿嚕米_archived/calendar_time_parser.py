import os
import json
import re
import google.generativeai as genai  # 注意：如果安裝的是新版，這行可能略有不同
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def parse_with_ai(nl_time_str: str):
    """強化版解析器：精確抓取名稱、日期與時間"""
    try:
        # 使用你清單中有的模型
        model = genai.GenerativeModel('gemini-2.0-flash') 
        
        # 極簡化的 Prompt，降低 AI 亂跑的機率
        prompt = f"""
        現在時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
        指令："{nl_time_str}"
        
        請將上述指令轉化為 JSON，規則如下：
        1. title: 提取指令中的主體活動（例如：運動、開會）。
        2. date: 計算指令中的日期（今天/明天/後天）。
        3. start_time: 若指令有時間（如五點），轉化為 HH:MM（如 05:00）。
        4. is_flexible: 指令有具體時間(如:五點) 必須設為 false。
        
        僅輸出 JSON 格式：
        {{
          "title": "活動名稱",
          "date": "YYYY-MM-DD",
          "start_time": "HH:MM",
          "duration": 60,
          "is_flexible": false
        }}
        """
        response = model.generate_content(prompt)
        text = response.text
        
        # 增加正則表達式，確保只拿 {} 裡面的資料
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            
            # --- 後處理補強 (Double Check) ---
            # 如果 AI 沒讀到名稱，從原始字串抓
            if not data.get('title') or data['title'] == '事件':
                data['title'] = nl_time_str.split(' ')[0]
            
            # 強制日期計算補強
            if '明天' in nl_time_str:
                data['date'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 強制時間補強
            if '五點' in nl_time_str:
                data['start_time'] = '05:00'
                data['is_flexible'] = False
                
            return data
            
        return None
    except Exception as e:
        print(f"AI 解析失敗: {e}")
        return None