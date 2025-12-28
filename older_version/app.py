import streamlit as st
import time

# --- 1. 設定頁面 ---
st.set_page_config(page_title="Smart Scheduling Agent", page_icon="🤖")

st.title("🤖 Smart Scheduling Agent")
st.caption("Week 5: Interactive UI Demo (Mock Backend)")

# --- 2. 初始化聊天紀錄 (Session State) ---
# Streamlit 每次互動都會重跑程式，所以要把紀錄存在 session_state 裡
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your scheduling assistant. (UI Test Mode)"}
    ]

# --- 3. 顯示歷史訊息 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. 處理使用者輸入 ---
if user_input := st.chat_input("Type your request here..."):
    # A. 顯示使用者的話
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # B. 模擬 Agent 思考 (Mock Logic)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤖 Thinking...")
        
        # 模擬延遲 (假裝在呼叫 API)
        time.sleep(1.5)

        # C. 假的後端邏輯 (之後會換成真的 Agent)
        user_text = user_input.lower()
        if "book" in user_text or "schedule" in user_text:
            response = "✅ (UI Demo) I have successfully scheduled that meeting for you!"
        elif "delete" in user_text or "cancel" in user_text:
            response = "⚠️ (UI Demo) Are you sure you want to delete this event?"
        else:
            response = f"I received your message: '{user_input}'. But I am currently in UI Mode."

        # D. 顯示回覆
        message_placeholder.markdown(response)
    
    # E. 存入紀錄
    st.session_state.messages.append({"role": "assistant", "content": response})