import datetime
import time
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

load_dotenv()

def main():
    print("Initializing Smart Scheduling Agent (Week 3 Test)...")
    calendar_tool = CalendarTool()
    
    # 增加迭代次數，讓 Agent 有足夠的步驟思考 (列表 -> 思考 -> 更新)
    my_agent = SchedulingAgent(tools=[calendar_tool])
    my_agent._executor.max_iterations = 8 

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- 階段一：建立活動 (Setup) ---
    print("\n[Phase 1] Setting up the environment: Creating the meeting first...")
    setup_query = (
        f"Today is {today}. "
        "Please schedule a 'Project Kickoff' meeting for tomorrow at 2 PM to 3 PM."
    )
    print(f"User: {setup_query}")
    print("-" * 30)
    my_agent(setup_query) # 執行建立
    
    print("\n" + "="*50 + "\n")
    
    # 等待幾秒鐘確保 Google 後台資料同步
    print("Waiting for Google Calendar to sync...")
    time.sleep(3)

    # --- 階段二：改期測試 (The Real Test) ---
    print("\n[Phase 2] Testing Week 3 Logic: Rescheduling...")
    
    # 這裡我們故意不給 ID，強迫 Agent 自己去 List 查詢
    reschedule_query = (
        f"Today is {today}. "
        "I need to change the 'Project Kickoff' meeting I just scheduled. "
        "Please check my upcoming meetings to find its ID, "
        "and then move it to 4 PM (16:00) on the same day."
    )
    
    print(f"User: {reschedule_query}")
    print("-" * 30)
    
    result = my_agent(reschedule_query)
    
    print("-" * 50)
    print(f"Final Result: {result}")

if __name__ == "__main__":
    main()