import streamlit as st
import time
import datetime
from dotenv import load_dotenv

# Try to import backend
try:
    from src.tools.calendar import CalendarTool
    from src.agent.scheduling_agent import SchedulingAgent
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False

# Load environment variables
load_dotenv()

# --- 1. Page Configuration ---
st.set_page_config(page_title="Smart Scheduling Agent", page_icon="🤖", layout="wide")
st.title("🤖 Smart Scheduling Agent")

# --- 2. Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your scheduling assistant. How can I help you today?"}
    ]

# Initialize Backend Status (Default to trying Real AI)
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "online" # options: online, offline, error

# Initialize Agent
if "agent" not in st.session_state and HAS_BACKEND:
    try:
        # We initialized the class, but we haven't tested if the API Key works yet
        calendar_tool = CalendarTool()
        st.session_state.agent = SchedulingAgent(tools=[calendar_tool])
        st.session_state.backend_status = "online"
    except Exception as e:
        st.session_state.backend_status = "error"
        st.session_state.error_msg = str(e)

# --- 3. Sidebar: Status & Calendar ---
with st.sidebar:
    st.header("📅 Upcoming Events")
    # Simulated Data for UI
    events = [
        {"time": "Tomorrow 10:00 AM", "title": "Team Standup"},
        {"time": "Tomorrow 02:00 PM", "title": "Client Meeting"},
    ]
    for event in events:
        with st.expander(f"{event['time']}"):
            st.write(f"**{event['title']}**")
    
    st.divider()
    st.caption("System Status:")
    
    # Dynamic Status Indicator
    if st.session_state.backend_status == "online":
        st.success("✅ Online: Real AI Agent")
    elif st.session_state.backend_status == "error":
        st.error("🔴 Offline: API Error")
        if "error_msg" in st.session_state:
            st.caption(f"Reason: {st.session_state.error_msg[:50]}...")
        if st.button("🔄 Retry Connection"):
            del st.session_state.agent
            del st.session_state.backend_status
            st.rerun()
    else:
        st.warning("⚠️ Mode: UI Test (Mock)")

# --- 4. Chat Interface ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. Handle User Input ---
if user_input := st.chat_input("Type your request here..."):
    # Show User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process Message
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤖 Thinking...")
        
        response = ""
        
        # --- LOGIC SWITCH ---
        # If status is Error or Offline, use Mock Logic immediately
        if st.session_state.backend_status != "online":
            time.sleep(1)
            response = f"⚠️ **(Mock Reply)** System is offline. I heard: '{user_input}'"
        
        # If status is Online, try to call the Real Agent
        else:
            try:
                now = datetime.datetime.now()
                full_query = f"Current Time: {now}. User Input: {user_input}"
                
                # CALL THE AGENT
                response = st.session_state.agent(full_query)
                
                # Check if the response contains specific error keywords
                if "Agent failed" in response or "429" in response:
                    raise Exception(response)

            except Exception as e:
                # !!! CATCH THE CRASH HERE !!!
                error_str = str(e)
                response = f"❌ **System Crash**: {error_str}"
                
                # Update Status to Red immediately
                st.session_state.backend_status = "error"
                st.session_state.error_msg = error_str
                # Force rerun to update the sidebar instantly
                st.rerun()

        # Show Response
        message_placeholder.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})