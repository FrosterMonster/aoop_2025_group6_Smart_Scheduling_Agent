from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from src.tools.base import AgentTool
import os

# --- IMPORT TOOLS ---
# We import the new tools we created for the "Expansion Pack"
from src.tools.preferences import PreferenceTool
from src.tools.weather import WeatherTool

# --- SYSTEM PROMPT ---
# This prompt tells the AI how to behave and when to use specific tools.
CUSTOM_SYSTEM_PROMPT = """
You are a Smart Scheduling Assistant. Your goal is to manage the user's schedule efficiently while considering their personal preferences and external factors like weather.

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes Action: the action to take, should be one of [{tool_names}] Action Input: the input to the action Observation: the result of the action


When you have a response for the human, or if you do not need to use a tool, you MUST use the format:

Thought: Do I need to use a tool? No Final Answer: [your response here]


IMPORTANT RULES:
1. **CHECK PREFERENCES FIRST**: If the user asks to book a meeting, ALWAYS check 'manage_preferences' (read_all) first to see if they have constraints (e.g., "No meetings on Fridays", "Lunch is at 12 PM").
2. **CHECK WEATHER**: If the user asks for an outdoor activity (e.g., Camping, Tennis, Hiking), use 'check_weather' to ensure conditions are good. Warn them if it's raining.
3. **SAFETY**: Before executing 'delete_event', you MUST ask the user for confirmation.
4. **CONFLICTS**: Always run 'list_events' before creating or moving a meeting.
5. **DATE**: Today's date is provided in the input. Use it to resolve "tomorrow" or "next week".

Previous conversation history:
{chat_history}

Begin!

User Input: {input}
Thought:{agent_scratchpad}
"""

class SchedulingAgent:
    def __init__(self, tools: list[AgentTool]):
        self._tools = tools
        
        # 1. Initialize the Base Tool (Calendar) provided from outside
        self._langchain_tools = [
            Tool(
                name=tool.name,
                func=tool.execute,
                description=tool.description
            )
            for tool in tools
        ]

        # 2. Add "Memory" Tool (Preferences)
        # This allows the agent to read/write from user_data.db
        pref_tool = PreferenceTool()
        self._langchain_tools.append(
            Tool(
                name=pref_tool.name,
                func=pref_tool.execute,
                description=pref_tool.description
            )
        )

        # 3. Add "Context" Tool (Weather)
        # This allows the agent to check simulated weather conditions
        weather_tool = WeatherTool()
        self._langchain_tools.append(
            Tool(
                name=weather_tool.name,
                func=weather_tool.execute,
                description=weather_tool.description
            )
        )

        # 4. Check API Key
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")
        
        # 5. Initialize the Brain (LLM)
        # We use 'gemini-1.5-flash' for the best balance of speed and free quota (1500 req/day).
        # If this model is unavailable in your region, try 'gemini-pro'.
        self._llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0
        )

        # 6. Setup the Prompt Template
        prompt = PromptTemplate(
            template=CUSTOM_SYSTEM_PROMPT,
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", "chat_history"]
        )
        
        # 7. Setup Conversation Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 8. Construct the Agent
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        # 9. Create the Executor
        self._executor = AgentExecutor(
            agent=agent_construct, 
            tools=self._langchain_tools, 
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            memory=self.memory
        )

    def run(self, user_query: str):
        """
        Main entry point for the agent to process a query.
        """
        try:
            # invoke() runs the ReAct loop (Thought -> Action -> Observation)
            result = self._executor.invoke({"input": user_query})
            return result["output"]
        except Exception as e:
            # Return the error as a string so the UI can display it gracefully
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        return self.run(user_query)