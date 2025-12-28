import streamlit as st
import time
import datetime
from dotenv import load_dotenv

# 嘗試匯入真實的 Agent
try:
    from src.tools.calendar import CalendarTool
    from src.agent.scheduling_agent import SchedulingAgent
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False

# 載入環境變數
load_dotenv()

# --- 1. 設定頁面 ---
st.set_page_config(page_title="Smart Scheduling Agent", page_icon="🤖", layout="wide")

st.title("🤖 Smart Scheduling Agent")

# --- 2. 側邊欄：顯示即將到來的行程 ---
with st.sidebar:
    st.header("📅 Upcoming Events")
    
    # 這裡未來可以呼叫 agent.list_events()
    # 目前我們先用假資料展示 UI 效果
    st.write("*(Simulated Calendar Data)*")
    
    events = [
        {"time": "Tomorrow 10:00 AM", "title": "Team Standup"},
        {"time": "Tomorrow 02:00 PM", "title": "Client Meeting"},
        {"time": "Friday 06:00 PM", "title": "Dinner with Mom"},
    ]
    
    for event in events:
        with st.expander(f"{event['time']}"):
            st.write(f"**{event['title']}**")
    
    st.divider()
    st.caption("Backend Status:")
    
    # 初始化 Agent (如果額度爆了，這裡可能會報錯，所以我們做個開關)
    if "agent" not in st.session_state:
        try:
            # 嘗試初始化真實 Agent
            # 注意：如果 API Quota 還是爆的，這裡可能會失敗
            calendar_tool = CalendarTool()
            st.session_state.agent = SchedulingAgent(tools=[calendar_tool])
            st.success("✅ Online (Real AI)")
            st.session_state.is_mock = False
        except Exception as e:
            st.error(f"⚠️ Offline: {e}")
            st.warning("Using Mock Mode (UI Only)")
            st.session_state.is_mock = True
    elif st.session_state.is_mock:
         st.warning("⚠️ Mode: UI Test (Mock)")
    else:
         st.success("✅ Mode: Real AI Agent")

# --- 3. 初始化聊天紀錄 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your scheduling assistant. How can I help you today?"}
    ]

# --- 4. 顯示歷史訊息 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. 處理使用者輸入 ---
if user_input := st.chat_input("Type your request here (e.g., 'Book a meeting')..."):
    # A. 顯示使用者的話
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # B. Agent 思考與回應
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤖 Thinking...")
        
        response = ""
        
        # --- 關鍵分支：判斷是用真 AI 還是假回應 ---
        if st.session_state.is_mock:
            # === Mock Logic (給你看 UI 效果用) ===
            time.sleep(1) # 假裝在思考
            user_text = user_input.lower()
            if "book" in user_text:
                response = "✅ (Mock) I've added that to your calendar!"
            elif "list" in user_text:
                response = "📅 (Mock) You have 3 meetings tomorrow."
            else:
                response = f"(Mock) I heard: '{user_input}'. (API Quota is exhausted, try again tomorrow!)"
        else:
            # === Real Logic (真實 AI) ===
            try:
                # 組合 Context (加上時間)
                now = datetime.datetime.now()
                today_str = now.strftime("%Y-%m-%d (%A) %H:%M")
                full_query = f"Current Time: {today_str}. User Input: {user_input}"
                
                # 呼叫 Agent
                response = st.session_state.agent(full_query)
            except Exception as e:
                response = f"❌ Error: {e} (Likely API Rate Limit)"

        # D. 顯示最終回覆
        message_placeholder.markdown(response)
    
    # E. 存入紀錄
    st.session_state.messages.append({"role": "assistant", "content": response})