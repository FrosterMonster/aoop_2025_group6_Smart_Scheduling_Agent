import datetime
import time
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

load_dotenv()

def main():
    print("Initializing Smart Scheduling Agent (Week 4: Conflict Detection)...")
    calendar_tool = CalendarTool()
    my_agent = SchedulingAgent(tools=[calendar_tool])

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    print("\n--- Phase 1: Create an obstacle (The 'Client Meeting') ---")
    # 我們先佔住明天下午 2 點到 3 點的時段
    setup_query = (
        f"Today is {today}. "
        "Schedule an 'Important Client Meeting' for tomorrow from 2 PM to 3 PM."
    )
    print(f"User: {setup_query}")
    my_agent(setup_query)
    
    print("\n" + "="*50 + "\n")
    print("Waiting for sync...")
    time.sleep(3)

    print("\n--- Phase 2: The Conflict Test ---")
    # 嘗試在「同一時間」塞入另一個會議
    # 聰明的 Agent 應該要先 List -> 發現衝突 -> 拒絕並回報
    conflict_query = (
        f"Today is {today}. "
        "Schedule a 'Team Sync' for tomorrow from 2 PM to 3 PM."
    )
    
    print(f"User: {conflict_query}")
    print("-" * 30)
    
    result = my_agent(conflict_query)
    
    print("-" * 50)
    print(f"Final Result: {result}")

if __name__ == "__main__":
    main()