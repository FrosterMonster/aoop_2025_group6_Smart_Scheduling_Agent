# main.py
import datetime
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

load_dotenv()

def main():
    print("Initializing Smart Scheduling Agent...")
    
    # 1. Instantiate Tools
    calendar_tool = CalendarTool()
    
    # 2. Instantiate Agent
    my_agent = SchedulingAgent(tools=[calendar_tool])

    # 3. Get Current Date dynamically
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.datetime.now().strftime("%A") # e.g., "Monday"

    # 4. Construct the query with context
    # We explicitly tell the agent "Today is..." so it can calculate "tomorrow"
    user_query = "Schedule a 'Project Kickoff' meeting for tomorrow from 2pm to 3pm."
    context_query = f"Today is {today} ({current_day}). {user_query}"
    
    print(f"\nUser Query: {user_query}")
    print(f"System Context: {context_query}")
    print("-" * 50)

    # 5. Run Agent
    result = my_agent(context_query)
    
    print("-" * 50)
    print(f"Agent Response: {result}")

if __name__ == "__main__":
    main()