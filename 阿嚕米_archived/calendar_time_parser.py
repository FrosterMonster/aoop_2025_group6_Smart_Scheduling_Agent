import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

from google import genai
from dotenv import load_dotenv
from google.genai.errors import ClientError


# ---------- 基本設定 ----------
load_dotenv()

# ✅ 新 SDK 初始化方式（重點）
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# ✅ 使用你帳號確定能用、最穩的模型
MODEL_NAME = "models/gemini-flash-latest"
TZ = "Asia/Taipei"


CHINESE_NUM_MAP = {
    "零": 0,
    "一": 1,
    "二": 2,
    "兩": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}

# ---------- 公開介面 ----------
def parse_with_ai(nl_text: str) -> Dict[str, Any]:
    """
    AI-first + rule-based fallback
    """
    try:
        raw = _llm_parse(nl_text)
        events = _post_process_and_validate(raw, nl_text)
        return {"events": events}

    except ClientError as e:
        # 👉 AI quota / client error
        if e.code == 429:
            print("[AI QUOTA EXCEEDED] fallback used")
        else:
            print("[AI CLIENT ERROR]", e)

    except Exception as e:
        # 👉 其他 parsing 錯誤
        print("[AI PARSE ERROR]", e)

    # ✅ 關鍵：一定要回 fallback
    return _rule_based_fallback(nl_text)


def _rule_based_fallback(nl_text: str) -> Dict[str, Any]:

    text = nl_text  # 用副本，不污染原始輸入

    """
    AI quota / error 時的最小可用 parser
    """
    today = datetime.now().date()

    # 日期
    date = today
    if "明天" in nl_text:
        date = today + timedelta(days=1)

    start_time = None
    is_flexible = True

    for zh, num in CHINESE_NUM_MAP.items():
        text = text.replace(f"{zh}點", f"{num}點")

    for zh, num in CHINESE_NUM_MAP.items():
        text = text.replace(f"{zh}小時", f"{num}小時")

    time_match = re.search(r'(\d{1,2})\s*(?:點|:)(\d{1,2})?', text)
    duration_match = re.search(r'(\d+)\s*小時', text)

    
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)

        # 中文時間語意修正
        if "下午" in nl_text or "晚上" in nl_text:
            if hour < 12:
                hour += 12

        if "早上" in nl_text or "上午" in nl_text:
            if hour == 12:
                hour = 0

        start_time = f"{hour:02d}:{minute:02d}"
        is_flexible = False

    # --- duration 解析（小時） ---
    duration = 60  # 預設 1 小時

    # 中文數字先轉成阿拉伯數字（兩小時 → 2小時）
    for zh, num in CHINESE_NUM_MAP.items():
        nl_text = nl_text.replace(f"{zh}小時", f"{num}小時")

    duration_match = re.search(r'(\d+)\s*小時', nl_text)
    if duration_match:
        duration = int(duration_match.group(1)) * 60

    return {
        "events": [
            {
                "title": re.sub(
                    r"(明天|今天|後天|早上|下午|晚上|上午|中午|凌晨|\d+點|\d+:\d+)", 
                    "",
                    nl_text
                ).strip(),
                "date": date.strftime("%Y-%m-%d"),
                "start_time": start_time,
                "duration": duration,
                "is_flexible": is_flexible,
                "is_recurring": False,
                "recurrence": None
            }
        ]
    }


# ---------- Step 1：LLM 解析（只負責 AI） ----------
def _llm_parse(nl_text: str) -> Dict[str, Any]:
    """
    呼叫 Gemini，將自然語言轉為 JSON
    """
    prompt = f"""
現在時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
使用者指令：「{nl_text}」

請將指令解析為 JSON，允許多個事件。

規則：
1. 沒有明確時間 → is_flexible = true
2. 有明確時間 → is_flexible = false
3. duration 單位：分鐘
4. date 格式：YYYY-MM-DD
5. start_time 若沒有請填 null
6. recurrence 只允許 DAILY / WEEKLY / null

只輸出 JSON：

{{
  "events": [
    {{
      "title": "活動名稱",
      "date": "YYYY-MM-DD",
      "start_time": "HH:MM 或 null",
      "duration": 60,
      "is_flexible": true,
      "is_recurring": false,
      "recurrence": null
    }}
  ]
}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("LLM 未回傳合法 JSON")

    return json.loads(match.group())


# ---------- Step 2：後處理 + 規則修正 ----------
def _post_process_and_validate(raw: Dict[str, Any], nl_text: str) -> List[Dict[str, Any]]:
    """
    修正 AI 結果，確保符合系統規則
    """
    if "events" not in raw or not isinstance(raw["events"], list):
        raise ValueError("AI 回傳格式錯誤，缺少 events")

    today = datetime.now().date()
    results = []

    for ev in raw["events"]:
        fallback_event = _rule_based_fallback(nl_text)["events"][0]

        raw_title = ev.get("title") or nl_text

        # ① 移除時間相關詞
        title = re.sub(
            r"(明天|今天|後天|本週|下週|早上|下午|晚上|上午|中午|凌晨|"
            r"\d+點|\d+:\d+|"
            r"[一二兩三四五六七八九十\d]+小時)",
            "",
            raw_title
        )

        # ② 移除結構詞，只保留事件核心
        title = re.sub(r"(有|的)", "", title).strip()

        # 日期
        date_str = ev.get("date")
        date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else today
        if "明天" in nl_text:
            date = today + timedelta(days=1)

        # 時間
        start_time = ev.get("start_time")

        # AI 沒抓到時間，但文字裡有時間 → 用 rule-based 補
        if not start_time:
            fallback = _rule_based_fallback(nl_text)
            fb_event = fallback["events"][0]
            start_time = fb_event.get("start_time")

        has_explicit_time = start_time not in (None, "", "null")
        is_flexible = not has_explicit_time

        # 時長
        duration = int(ev.get("duration") or 60)

        # 如果 AI 沒抓到「小時語意」，用 fallback 補
        if "小時" in nl_text:
            fb = _rule_based_fallback(nl_text)["events"][0]
            duration = fb.get("duration", duration)

        # recurrence
        recurrence = ev.get("recurrence")
        if recurrence not in ("DAILY", "WEEKLY"):
            recurrence = None

        results.append({
            "title": title,
            "date": date.strftime("%Y-%m-%d"),
            "start_time": start_time if has_explicit_time else None,
            "duration": duration,
            "is_flexible": is_flexible,
            "is_recurring": recurrence is not None,
            "recurrence": recurrence,
        })

    return results
