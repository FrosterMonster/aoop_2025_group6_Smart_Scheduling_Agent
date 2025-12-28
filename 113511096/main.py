from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

# Load API keys
load_dotenv()

def main():
    print("Initializing Smart Scheduling Agent...")

    # 1. Instantiate Tools (Polymorphism: Agent treats CalendarTool as an AgentTool)
    calendar_tool = CalendarTool()
    
    # 2. Instantiate Agent with the tools
    my_agent = SchedulingAgent(tools=[calendar_tool])

    # 3. User Query (Natural Language)
    user_input = "Please schedule a 'Project Kickoff' meeting for tomorrow from 2pm to 3pm."
    
    print(f"\nUser Query: {user_input}")
    print("-" * 50)

    # 4. Run Agent (using __call__ magic method)
    # The Agent should:
    #   1. Understand "tomorrow from 2pm to 3pm" -> Calculate the date
    #   2. Formulate a JSON action -> {"action": "create_event", ...}
    #   3. Call CalendarTool.execute()
    result = my_agent(user_input)
    
    print("-" * 50)
    print(f"Agent Response: {result}")

if __name__ == "__main__":
    main()