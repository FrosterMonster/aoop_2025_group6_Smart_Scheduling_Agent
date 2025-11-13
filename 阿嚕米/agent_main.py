import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from openai import OpenAI, APIError, RateLimitError
from dotenv import load_dotenv
from datetime import datetime
import pytz

# logging 設定
logger = logging.getLogger("agent")
if not logger.handlers:
    # 終端輸出處理器
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # 檔案輸出（滾動檔案）
    try:
        from logging.handlers import RotatingFileHandler
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler('logs/agent.log', maxBytes=1_000_000, backupCount=5, encoding='utf-8')
        file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s [%(filename)s:%(lineno)d]: %(message)s", "%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except Exception as _e:
        # 若檔案 handler 無法建立，仍繼續使用 terminal handler
        handler.setLevel(logging.DEBUG)
        logger.debug("無法建立檔案日誌處理器：%s", _e)

# 使用 DEBUG 作為預設等級以便收集詳細啟動資訊
logger.setLevel(logging.DEBUG)

# 新增：引入自然語言時間解析器（在同一資料夾下）
from calendar_time_parser import parse_nl_time

# 引入您剛才成功測試的核心日曆函式
from calendar_tools import create_calendar_event

# 從 .env 或系統環境變數讀取 GEMINI_API_KEY（請在專案根目錄創建 .env，或在系統環境中設定）
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key

# 記錄啟動時的環境狀態（不印出實際 API key）
logger.info("Loaded .env (if present)")
logger.info("OPENAI_API_KEY present: %s", bool(os.getenv("OPENAI_API_KEY")))
logger.info("GEMINI_API_KEY present: %s", bool(gemini_key))
logger.info("DRY_RUN=%s", os.getenv("DRY_RUN"))
logger.info("credentials.json exists: %s", os.path.exists("credentials.json"))
logger.info("token.pickle exists: %s", os.path.exists("token.pickle"))

# --- 1. 定義 calendar_tool 為一個 OpenAI function ---
def schedule_calendar_event(summary: str, start_time_str: str, end_time_str: str, description: str = "") -> str:
    """
    使用此工具在 Google Calendar 中建立一個新的行程或活動。
    只有當使用者明確要求安排或新增行程時才調用。
    請務必將使用者請求的時間轉換為 'YYYY-MM-DD HH:MM:SS' 格式後再傳遞給此工具。
    """
    # 如果傳入的時間已經是 'YYYY-MM-DD HH:MM:SS' 格式，直接使用；否則嘗試解析自然語言時間
    def _ensure_formatted(ts: str) -> str:
        from datetime import datetime
        try:
            # 嘗試解析為指定格式
            datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
            return ts
        except Exception:
            # 嘗試使用自然語言解析器
            parsed = parse_nl_time(ts)
            if not parsed:
                raise ValueError(f"無法解析時間字串: {ts}")
            # 轉換為 Asia/Taipei 時區，並格式化為字串
            tz = pytz.timezone('Asia/Taipei')
            try:
                parsed = parsed.astimezone(tz)
            except Exception:
                parsed = tz.localize(parsed.replace(tzinfo=None)) if parsed.tzinfo else tz.localize(parsed)
            return parsed.strftime('%Y-%m-%d %H:%M:%S')

    try:
        start_fmt = _ensure_formatted(start_time_str)
        end_fmt = _ensure_formatted(end_time_str)
    except Exception as e:
        logger.error("時間解析失敗 for summary=%s start=%s end=%s: %s", summary, start_time_str, end_time_str, e)
        return f"時間解析失敗: {e}"

    # 記錄即將建立的活動資訊（不包含機密）
    logger.info("Scheduling event: summary=%s start=%s end=%s description_len=%d", summary, start_fmt, end_fmt, len(description or ""))

    # 調用您在 calendar_tools.py 中定義的實際功能
    return create_calendar_event(summary, description, start_fmt, end_fmt, calendar_id='primary')

# 匯出所有工具
tools = [schedule_calendar_event]

# --- 3. 建立 Agent 核心 ---
def run_agent(user_query: str) -> Dict:
    # 定義 mock 處理函式，作為 OpenAI 調用失敗時的備用選項
    def mock_handle(query: str) -> dict:
        import re
        # 嘗試抓取引號或書名號中的 summary
        summary = None
        m = re.search(r'["\u201c\u201d\u300c\u300d](.+?)["\u201c\u201d\u300c\u300d]', query)
        if m:
            summary = m.group(1)
        else:
            m2 = re.search(r'安排(?:一個|個)?(?:「([^」]+)」|(.+?)(?:，|,|。|$))', query)
            if m2:
                summary = m2.group(1) or m2.group(2)
        if not summary:
            summary = '行程'

        # 解析時間
        start_str = None
        end_str = None
        if '到' in query:
            parts = query.split('到')
            start_str = parts[0].split('時間是')[-1].strip()
            end_str = parts[1].split('。')[0].strip()
        else:
            m3 = re.search(r'(今天|明天|後天|本週\S*|下週\S*).*?(\d{1,2})\s*點', query)
            if m3:
                start_str = m3.group(0)

        # 解析時間字串
        start_fmt = None
        end_fmt = None
        try:
            if start_str:
                ds = parse_nl_time(start_str)
                if ds:
                    start_fmt = ds.astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
            if end_str:
                de = parse_nl_time(end_str)
                if de:
                    end_fmt = de.astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass

        # 如果只有開始時間，假設結束時間是一小時後
        if start_fmt and not end_fmt:
            try:
                sdt = datetime.strptime(start_fmt, '%Y-%m-%d %H:%M:%S')
                edt = sdt + timedelta(hours=1)
                end_fmt = edt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                end_fmt = None

        if not start_fmt or not end_fmt:
            return {'output': f"Mock: 無法解析時間。summary={summary}, start={start_fmt}, end={end_fmt}"}

        try:
            res = create_calendar_event(summary, '由 Mock 建立', start_fmt, end_fmt, calendar_id='primary')
            return {'output': f"Mock 已執行: {res}"}
        except Exception as e:
            return {'output': f"Mock 執行失敗: {e}"}

    try:
        # 載入 OpenAI API key
        load_dotenv()
        client = OpenAI()

        # 設置當前時間（台北時區）
        current_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')

        # 定義 function calling 的描述
        tools = [{
            "type": "function",
            "function": {
                "name": "schedule_calendar_event",
                "description": "使用此工具在 Google Calendar 中建立一個新的行程或活動。只有當使用者明確要求安排或新增行程時才調用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "活動標題或摘要"
                        },
                        "start_time_str": {
                            "type": "string",
                            "description": "活動開始時間，必須是 'YYYY-MM-DD HH:MM:SS' 格式"
                        },
                        "end_time_str": {
                            "type": "string",
                            "description": "活動結束時間，必須是 'YYYY-MM-DD HH:MM:SS' 格式"
                        },
                        "description": {
                            "type": "string",
                            "description": "活動的詳細描述或備註"
                        }
                    },
                    "required": ["summary", "start_time_str", "end_time_str"]
                }
            }
        }]

        # 系統提示詞
        messages = [
            {
                "role": "system",
                "content": (
                    "您是一位專業的 Google Calendar AI 助理。您的主要職責是根據使用者的請求管理他們的行程。\n"
                    "您擁有建立行程的工具。請始終保持禮貌和專業。\n"
                    f"您當前的時間是: {current_time}。您必須使用當前時間作為計算基礎。\n"
                    "在調用工具時，您必須將所有自然語言的時間描述（例如「明天下午兩點」）轉換為精確的 'YYYY-MM-DD HH:MM:SS' 格式。"
                )
            },
            {
                "role": "user",
                "content": user_query
            }
        ]

        # OpenAI API 調用邏輯，包含重試機制
        max_retries = 2
        retry_delay = 1
        completion = None
        
        for attempt in range(max_retries + 1):
            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo-16k",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.3,
                    max_tokens=1000
                )
                break
            except (APIError, RateLimitError) as e:
                if attempt < max_retries:
                    print(f"嘗試 {attempt + 1} 失敗: {e}")
                    print(f"等待 {retry_delay} 秒後重試...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                print(f"重試 {max_retries} 次後仍然失敗")
                raise

        if not completion:
            print("無法獲得 OpenAI 回應")
            return mock_handle(user_query)

        # 解析 OpenAI 回應並處理工具調用
        try:
            response_message = completion.choices[0].message

        # 如果 AI 選擇調用工具
            if response_message.tool_calls:
                # 處理每個工具調用
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "schedule_calendar_event":
                        # 解析參數
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # 調用實際的日曆函數
                        result = schedule_calendar_event(
                            function_args.get("summary"),
                            function_args.get("start_time_str"),
                            function_args.get("end_time_str"),
                            function_args.get("description", "")
                        )

                        # 將工具執行結果加入對話
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call],
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        })

                # 使用重試邏輯再次調用 API 以獲取最終回覆
                for attempt in range(max_retries + 1):
                    try:
                        second_completion = client.chat.completions.create(
                            model="gpt-3.5-turbo-16k",
                            messages=messages,
                            temperature=0.3,
                            max_tokens=500
                        )
                        final_response = second_completion.choices[0].message.content
                        return {"output": final_response}
                    except (APIError, RateLimitError) as e:
                        if attempt < max_retries:
                            print(f"獲取最終回覆時嘗試 {attempt + 1} 失敗: {e}")
                            print(f"等待 {retry_delay} 秒後重試...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                        print("無法獲取最終回覆，使用工具執行結果作為回應")
                        return {"output": f"已執行: {result}"}
            else:
                # 如果 AI 選擇直接回覆
                return {"output": response_message.content}

        except Exception as e:
            print(f"處理 OpenAI 回應時發生錯誤: {e}")
            return mock_handle(user_query)

    except Exception as e:
        logger.error("與 OpenAI API 通信時發生錯誤: %s", e)
        logger.info("轉用 Mock 模式...")
        def mock_handle(query: str) -> dict:
            import re
            # 嘗試抓取引號或書名號中的 summary
            summary = None
            m = re.search(r'["\u201c\u201d\u300c\u300d](.+?)["\u201c\u201d\u300c\u300d]', query)
            if m:
                summary = m.group(1)
            else:
                m2 = re.search(r'安排(?:一個|個)?(?:「([^」]+)」|(.+?)(?:，|,|。|$))', query)
                if m2:
                    summary = m2.group(1) or m2.group(2)
            if not summary:
                summary = '行程'

            logger.info("Mock extracted summary='%s'", summary)

            # 解析時間
            start_str = None
            end_str = None
            if '到' in query:
                parts = query.split('到')
                start_str = parts[0].split('時間是')[-1].strip()
                end_str = parts[1].split('。')[0].strip()
            else:
                m3 = re.search(r'(今天|明天|後天|本週\S*|下週\S*).*?(\d{1,2})\s*點', query)
                if m3:
                    start_str = m3.group(0)

            # 解析時間字串
            start_fmt = None
            end_fmt = None
            try:
                if start_str:
                    ds = parse_nl_time(start_str)
                    if ds:
                        start_fmt = ds.astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
                if end_str:
                    de = parse_nl_time(end_str)
                    if de:
                        end_fmt = de.astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass

            # 如果只有開始時間，假設結束時間是一小時後
            if start_fmt and not end_fmt:
                try:
                    sdt = datetime.strptime(start_fmt, '%Y-%m-%d %H:%M:%S')
                    edt = sdt + timedelta(hours=1)
                    end_fmt = edt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    end_fmt = None

            if not start_fmt or not end_fmt:
                logger.warning("Mock failed to parse full times: start=%s end=%s", start_fmt, end_fmt)
                return {'output': f"Mock: 無法解析時間。summary={summary}, start={start_fmt}, end={end_fmt}"}

            try:
                logger.info("Mock calling create_calendar_event: summary=%s start=%s end=%s", summary, start_fmt, end_fmt)
                res = create_calendar_event(summary, '由 Mock 建立', start_fmt, end_fmt, calendar_id='primary')
                logger.info("Mock create_calendar_event result: %s", res)
                return {'output': f"Mock 已執行: {res}"}
            except Exception as e:
                logger.error("Mock create_calendar_event failed: %s", e)
                return {'output': f"Mock 執行失敗: {e}"}
        
        # 實際執行 mock_handle
        return mock_handle(user_query)

# --- 4. 運行測試 ---
if __name__ == '__main__':
    # 複雜請求：讓 Agent 必須計算「明天」和時間區間
    user_request = "請幫我安排一個「與導師會面」的活動，時間是今天晚上 8 點到 9 點。"
    
    print(f"--- 處理請求: {user_request} ---")
    try:
        response = run_agent(user_request)
        print("\n--- Agent 最終回覆 ---")
        print(response['output'])
    except Exception as e:
        print(f"\n運行 Agent 時發生錯誤: {e}")