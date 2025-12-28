import datetime
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

load_dotenv()

def main():
    print("Initializing Smart Scheduling Agent (Quota Saving Mode)...")
    calendar_tool = CalendarTool()
    my_agent = SchedulingAgent(tools=[calendar_tool])
    my_agent._executor.max_iterations = 5 

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    print("\n[Phase 2 Only] Testing Rescheduling...")
    print("(Please ensure you have MANUALLY created a 'Project Kickoff' meeting for tomorrow 2PM)")
    
    # 直接要求改期
    reschedule_query = (
        f"Today is {today}. "
        "I need to change the 'Project Kickoff' meeting scheduled for tomorrow 2 PM. "
        "Please find its ID and move it to 4 PM (16:00) on the same day."
    )
    
    print(f"User: {reschedule_query}")
    print("-" * 30)
    
    result = my_agent(reschedule_query)
    
    print("-" * 50)
    print(f"Final Result: {result}")

if __name__ == "__main__":
    main()