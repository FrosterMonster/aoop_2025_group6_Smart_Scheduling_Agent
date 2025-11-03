import os
#from langchain_openai import ChatOpenAI#
from langchain_google_genai import ChatGoogleGenerativeAI # <-- 新增這行
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from pydantic import BaseModel, Field
from datetime import datetime
import pytz

# 引入您剛才成功測試的核心日曆函式
from calendar_tools import create_calendar_event

# 確保設定 OpenAI 金鑰（將 YOUR_API_KEY 替換成您的 OpenAI 或 Gemini API 金鑰）
# 註：如果使用 Gemini，請安裝 langchain-google-genai 並使用 ChatGoogleGenerativeAI
os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"

# --- 1. 定義工具的輸入結構 (Pydantic) ---
# 這告訴 LLM 呼叫函式時需要提供哪些參數，以及參數的資料型態
class CreateEventInput(BaseModel):
    """建立 Google Calendar 活動所需的輸入參數"""
    summary: str = Field(description="活動標題或摘要。")
    start_time_str: str = Field(description="活動開始時間，必須是精確的 'YYYY-MM-DD HH:MM:SS' 格式。Agent 必須將使用者的自然語言時間轉換成這個格式。")
    end_time_str: str = Field(description="活動結束時間，必須是精確的 'YYYY-MM-DD HH:MM:SS' 格式。")
    description: str = Field(default="", description="活動的詳細描述或備註。")

# --- 2. 將核心函式包裝成 LangChain Tool ---
@tool(args_schema=CreateEventInput)
def schedule_calendar_event(summary: str, start_time_str: str, end_time_str: str, description: str = "") -> str:
    """
    使用此工具在 Google Calendar 中建立一個新的行程或活動。
    只有當使用者明確要求安排或新增行程時才調用。
    請務必將使用者請求的時間轉換為 'YYYY-MM-DD HH:MM:SS' 格式後再傳遞給此工具。
    """
    # 調用您在 calendar_tools.py 中定義的實際功能
    return create_calendar_event(summary, description, start_time_str, end_time_str, calendar_id='primary')

# 匯出所有工具
tools = [schedule_calendar_event]

# --- 3. 建立 Agent 核心 ---
def run_agent(user_query: str):
    # 初始化 LLM（使用 gpt-4o 或 gpt-3.5-turbo 等支援 Tool Calling 的模型）
    #llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0) 
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0) 

    # 設置 Agent 的個性/系統提示
    current_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
    system_message = (
        "您是一位專業的 Google Calendar AI 助理。您的主要職責是根據使用者的請求管理他們的行程。 "
        "您擁有建立行程的工具。請始終保持禮貌和專業。"
        "您當前的時間是: {current_time}。您必須使用當前時間作為計算基礎。"
        "在調用工具時，您**絕對必須**將所有自然語言的時間描述（例如「明天下午兩點」）轉換為精確的 'YYYY-MM-DD HH:MM:SS' 格式，然後再呼叫工具。"
    ).format(current_time=current_time)

    # 建立 Agent Prompt Template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            # {chat_history} 佔位符，留給後續加入記憶體功能
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"), 
        ]
    )

    # 建立 Agent 執行器
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 運行並返回結果
    return agent_executor.invoke({"input": user_query})

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