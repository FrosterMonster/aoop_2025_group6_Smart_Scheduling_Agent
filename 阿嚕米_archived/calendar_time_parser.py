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

def normalize_chinese_duration(text: str) -> str:
    def repl(match):
        zh_num = match.group(1)
        return f"{chinese_to_int(zh_num)}小時"

    return re.sub(r'([一二兩三四五六七八九十]{1,3})小時', repl, text)

def normalize_chinese_time(text: str) -> str:
    def repl(match):
        zh_num = match.group(1)
        return f"{chinese_to_int(zh_num)}點"

    return re.sub(r'([一二兩三四五六七八九十]{1,3})點', repl, text)

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
    """
    Rule-based fallback parser
    - 只解析「文字中明確出現」的資訊
    - 不做推測
    """

    # ---------- 前處理（中文數字正規化） ----------
    text = normalize_chinese_time(nl_text)
    text = normalize_chinese_duration(text)

    today = datetime.now().date()

    # ---------- 日期 ----------
    date = today
    if "明天" in nl_text:
        date = today + timedelta(days=1)
    elif "後天" in nl_text:
        date = today + timedelta(days=2)

    # ---------- 開始時間 ----------
    start_time = None
    is_flexible = True

    time_match = re.search(r'(\d{1,2})\s*(?:點|:)(\d{1,2})?', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)

        # 中文時段語意修正
        if "中午" in nl_text:
            if hour < 11:
                hour = 12
        elif "下午" in nl_text or "晚上" in nl_text:
            if hour < 12:
                hour += 12
        elif "早上" in nl_text or "上午" in nl_text:
            if hour == 12:
                hour = 0

        start_time = f"{hour:02d}:{minute:02d}"
        is_flexible = False
    # ---------- 語意型彈性事件 ----------
    # 像是「找空時間 / 幫我找 / 有空的時候」
    SEMANTIC_FLEXIBLE_KEYWORDS = [
        "找空時間", "找有空", "有空時間", "幫我找", "空檔", "空時間"
    ]

    if any(k in nl_text for k in SEMANTIC_FLEXIBLE_KEYWORDS):
        start_time = None
        is_flexible = True

    # ---------- 時長（分鐘） ----------
    duration = 60  # 預設 1 小時

    # 阿拉伯數字：3小時
    m = re.search(r'(\d+)\s*小時', text)
    if m:
        duration = int(m.group(1)) * 60
    else:
        # 中文數字：三小時
        m = re.search(r'([一二兩三四五六七八九十]+)小時', text)
        if m:
            duration = chinese_to_int(m.group(1)) * 60

    # ---------- 活動標題 ----------
    title = re.sub(
        r"(明天|今天|後天|早上|上午|中午|下午|晚上|凌晨|"
        r"找空時間|找空間時間|找有空|幫我找|有空時間|空檔|空時間|"
        r"\d+點|\d+:\d+|"
        r"[一二兩三四五六七八九十]+點|"
        r"[一二兩三四五六七八九十\d]+小時)",
        "",
        nl_text
    )
    title = re.sub(r"(有|的)", "", title).strip()

    # 保底
    if not title:
        title = "未命名活動"

    return {
        "events": [
            {
                "title": title,
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
    fallback_event = _rule_based_fallback(nl_text)["events"][0]

    for ev in raw["events"]:

        raw_title = ev.get("title") or nl_text

        # ① 移除時間相關詞
        title = re.sub(
            r"(明天|今天|後天|本週|下週|早上|下午|晚上|上午|中午|凌晨|"
            r"找空時間|找空間時間|找有空|幫我找|有空時間|空檔|空時間|"
            r"\d+點|\d+:\d+|"
            r"[一二兩三四五六七八九十]+點|"
            r"[一二兩三四五六七八九十\d]+小時)",
            "",
            raw_title
        )
        title = re.sub(r"(有|的)", "", title).strip()

        # ---------- 活動名稱語意修正（關鍵） ----------

        # 常見「調度語意」開頭（不是活動本身）
        SCHEDULING_PREFIXES = [
            "找空閒時間",
            "找時間",
            "幫我找",
            "安排",
            "幫我安排",
        ]

        for prefix in SCHEDULING_PREFIXES:
            if title.startswith(prefix):
                title = title.replace(prefix, "").strip()

        # 日期
        date_str = ev.get("date")
        date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else today
        if "明天" in nl_text:
            date = today + timedelta(days=1)

        # 時間
        start_time = ev.get("start_time")

        # ---------- 時間補強 ----------
        # AI 沒抓到時間，但文字裡有 → 用 fallback 補
        if not start_time:
            start_time = fallback_event.get("start_time")

        has_explicit_time = start_time not in (None, "", "null")

        # 如果語意上是找空時間，一定是彈性
        if any(k in nl_text for k in [
            "找空時間", "找空間時間", "找有空", "幫我找", "空檔", "空時間"
        ]):
            is_flexible = True
            start_time = None
        else:
            is_flexible = not has_explicit_time

        # ---------- 時長補強（最終正解版） ----------

        # 一律先用 fallback（語意確定）
        duration = fallback_event.get("duration")

        # 如果 fallback 沒算到，再退回 AI
        if not duration:
            duration = ev.get("duration")

        # 防呆
        duration = int(duration or 60)

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

def chinese_to_int(s: str) -> int:
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CHINESE_NUM_MAP.get(s[1], 0)
    if s.endswith("十"):
        return CHINESE_NUM_MAP.get(s[0], 0) * 10
    if "十" in s:
        left, right = s.split("十")
        return CHINESE_NUM_MAP.get(left, 0) * 10 + CHINESE_NUM_MAP.get(right, 0)
    return CHINESE_NUM_MAP.get(s, 0)
