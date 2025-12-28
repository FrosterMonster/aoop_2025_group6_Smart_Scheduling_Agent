import os
import json
import re
import pytz
from datetime import datetime, timedelta
import dateparser
import google.generative_ai as genai
from dotenv import load_dotenv

# 載入環境變數 (API Key)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

DEFAULT_TZ = 'Asia/Taipei'

def parse_with_gemini(nl_time_str: str):
    """使用 Gemini 解析意圖，回傳結構化 JSON"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        prompt = f"""
        你是一個專業的行程助理。請解析以下輸入並轉換為 JSON 格式。
        目前時間：{now} (台北時區)
        使用者輸入："{nl_time_str}"

        請輸出以下欄位的 JSON (不要輸出任何額外文字)：
        - title: (字串) 事件標題
        - date: (YYYY-MM-DD) 事件日期
        - start_time: (HH:MM)
        - duration: (分鐘，整數)
        - is_recurring: (布林值)
        - rrule: (如果 is_recurring 為 true，請提供 RRULE 字串，例如 RRULE:FREQ=DAILY)
        """
        
        response = model.generate_content(prompt)
        # 移除 Markdown 語法標籤
        clean_text = re.sub(r'```json|```', '', response.text).strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Gemini 解析失敗: {e}")
        return None

def parse_nl_time(nl_time_str: str, prefer_future: bool = True):
    """
    整合邏輯：
    1. 嘗試 AI 解析 (回傳 Dictionary)
    2. 若失敗，走原本的 Rule-based 解析 (回傳 datetime)
    """
    # --- 1. 嘗試 AI 解析 ---
    ai_data = parse_with_gemini(nl_time_str)
    if ai_data:
        return ai_data  # 回傳完整的字典，方便 UI 填表

    # --- 2. 備援：原有的 Heuristic 規則 (簡化版) ---
    try:
        s = nl_time_str.strip()
        now = datetime.now()
        tz = pytz.timezone(DEFAULT_TZ)
        base = None
        if '明天' in s or '明日' in s:
            base = now + timedelta(days=1)
        elif '今天' in s or '今日' in s:
            base = now
        elif '後天' in s:
            base = now + timedelta(days=2)

        if base is not None:
            m = re.search(r"(\d{1,2})", s)
            if m:
                hour = int(m.group(1))
                if ('下午' in s or '晚上' in s) and 1 <= hour <= 11:
                    hour += 12
                dt = datetime(base.year, base.month, base.day, hour, 0)
                return tz.localize(dt)
    except:
        pass

    # --- 3. 終極墊後：Dateparser ---
    settings = {
        'PREFER_DATES_FROM': 'future' if prefer_future else 'past',
        'RETURN_AS_TIMEZONE_AWARE': True,
        'TIMEZONE': DEFAULT_TZ,
    }
    dt = dateparser.parse(nl_time_str, settings=settings, languages=['zh'])
    return dt

if __name__ == "__main__":
    # 測試執行
    test_input = "每天晚上九點到十點要運動"
    print(f"測試輸入: {test_input}")
    result = parse_nl_time(test_input)
    print("解析結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))