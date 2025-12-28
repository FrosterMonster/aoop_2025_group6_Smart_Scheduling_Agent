import datetime
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

load_dotenv()

def main():
    print("Initializing Smart Scheduling Agent (Week 3 Mode)...")
    calendar_tool = CalendarTool()
    
    # We need enough steps for: List -> Think -> Update
    my_agent = SchedulingAgent(tools=[calendar_tool])
    my_agent._executor.max_iterations = 5 

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    print("\n--- TEST: Reschedule an Event ---")
    
    user_query = (
        "Check my upcoming 'Project Kickoff' meeting. "
        "It's currently scheduled for 2 PM, but I need to move it to 4 PM on the same day. "
        "Please reschedule it."
    )
    
    context_query = f"Today is {today}. {user_query}"
    
    print(f"Query: {context_query}")
    print("-" * 50)

    result = my_agent(context_query)
    
    print("-" * 50)
    print(f"Final Result: {result}")

if __name__ == "__main__":
    main()