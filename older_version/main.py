import datetime
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

load_dotenv()

def main():
    print("Initializing Smart Scheduling Agent...")
    calendar_tool = CalendarTool()
    
    # Increase iterations to 5 so it has enough steps to Create -> Create -> List -> Delete
    my_agent = SchedulingAgent(tools=[calendar_tool])
    # Manually adjust the limit for this complex test
    my_agent._executor.max_iterations = 8 

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.datetime.now().strftime("%A")

    print("\n--- TEST SUITE: Create Duplicates & Delete One ---")
    
    # We give a complex instruction that forces the full workflow
    user_query = (
        "I want to test my calendar. "
        "1. Schedule a 'Strategy Meeting' for tomorrow at 9 AM to 10 AM. "
        "2. Schedule ANOTHER 'Strategy Meeting' for the same time (create a duplicate). "
        "3. Check my upcoming meetings to see the IDs. "
        "4. Delete one of the 'Strategy Meetings' using its ID."
    )
    
    context_query = f"Today is {today} ({current_day}). {user_query}"
    
    print(f"Query: {context_query}")
    print("-" * 50)

    result = my_agent(context_query)
    
    print("-" * 50)
    print(f"Final Result: {result}")

if __name__ == "__main__":
    main()