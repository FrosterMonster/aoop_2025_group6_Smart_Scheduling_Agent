import datetime
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

load_dotenv()

def main():
    print("Initializing Smart Scheduling Agent...")
    calendar_tool = CalendarTool()
    my_agent = SchedulingAgent(tools=[calendar_tool])

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.datetime.now().strftime("%A")

    # TEST: Ask the agent to find and delete the duplicate
    print("\n--- TEST: Delete a Duplicate Event ---")
    user_query = "Check my upcoming meetings. If there are multiple 'Project Kickoff' meetings, delete one of them."
    
    context_query = f"Today is {today} ({current_day}). {user_query}"
    
    print(f"Query: {context_query}")
    print("-" * 50)

    result = my_agent(context_query)
    
    print("-" * 50)
    print(f"Final Result: {result}")

if __name__ == "__main__":
    main()