import streamlit as st
import time
import pandas as pd
import datetime
from dotenv import load_dotenv

# --- Import New Modules ---
from src.logger import log_info, log_error, log_warning
from src.analytics import AnalyticsEngine

# Try to import backend
try:
    from src.tools.calendar import CalendarTool
    from src.agent.scheduling_agent import SchedulingAgent
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False

load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="Smart Scheduling Platform", page_icon="🤖", layout="wide")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your enterprise assistant."}]
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "online"

# --- Main Layout ---
st.title("🤖 Smart Scheduling Platform")
st.caption("Enterprise Edition v2.0 | Analytics & AI Integration")

# 建立兩個分頁 (Tabs)
tab1, tab2 = st.tabs(["💬 AI Chat Agent", "📊 Productivity Dashboard"])

# ==========================================
# TAB 1: 聊天介面 (原本的功能)
# ==========================================
with tab1:
    # (保留原本的側邊欄邏輯，但放在這裡)
    with st.sidebar:
        st.header("📅 Quick View")
        st.info("System Logs Active")
        if st.session_state.backend_status == "error":
            st.error("Connection Status: Offline")
        else:
            st.success("Connection Status: Online")

    # Chat UI
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Type command..."):
        log_info(f"User input received: {user_input}") # 使用新的 Logger
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤖 Thinking...")
            
            response = ""
            try:
                # 這裡嘗試呼叫 Agent
                if HAS_BACKEND and st.session_state.backend_status == "online":
                    # (需確保你有初始化 agent，這邊省略初始化代碼以節省篇幅，邏輯同前)
                    # 模擬回應以展示 UI
                    time.sleep(1)
                    response = f"I processed: '{user_input}'. (Check 'logs/system.log' for details)"
                else:
                    response = "⚠️ System Offline (Mock Mode)"
            except Exception as e:
                log_error(f"Agent Crash: {e}")
                response = f"❌ Error: {e}"

            message_placeholder.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# ==========================================
# TAB 2: 數據儀表板 (新增的大功能！)
# ==========================================
with tab2:
    st.header("📊 User Productivity Analytics")
    st.markdown("Real-time insights based on your scheduling habits.")
    
    # 初始化分析引擎
    analytics = AnalyticsEngine()
    stats = analytics.generate_mock_stats() # 取得數據

    # 1. 關鍵指標 (Metrics)
    col1, col2, col3 = st.columns(3)
    col1.metric("Productivity Score", f"{stats['productivity_score']}/100", "+5%")
    col2.metric("Total Meetings", stats['total_meetings'], "+2")
    col3.metric("Focus Hours", "12.5 hrs", "-1.2 hrs")

    st.divider()

    # 2. 圖表區域
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Weekly Meeting Load")
        # 使用 Streamlit 內建圖表
        st.bar_chart(stats['weekly_trend'].set_index("Day"))
    
    with c2:
        st.subheader("Meeting Types Distribution")
        # 簡單的 Area Chart 來模擬分佈
        st.area_chart(stats['category_dist'].set_index("Category"))

    st.divider()
    
    # 3. 系統日誌查看器 (System Health)
    with st.expander("🔍 View System Logs (Live)"):
        try:
            with open("logs/system.log" if 'log_filename' not in locals() else log_filename, "r") as f:
                logs = f.readlines()
                # 顯示最後 10 行
                for line in logs[-10:]:
                    st.text(line.strip())
        except FileNotFoundError:
            st.warning("No logs found yet.")