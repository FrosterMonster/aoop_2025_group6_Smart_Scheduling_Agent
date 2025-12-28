from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from src.tools.base import AgentTool
import os

class SchedulingAgent:
    """
    The Agent's core, utilizing Google Gemini for decision making.
    """
    def __init__(self, tools: list[AgentTool]):
        self._tools = tools
        self._memory = []
        
        # 1. Convert Custom Tools to LangChain Tools
        self._langchain_tools = [
            Tool(
                name=tool.name,
                func=tool.execute,
                description=tool.description
            )
            for tool in tools
        ]

        # 2. Initialize Gemini (Using 1.5 Flash)
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
            
        # Initialize the LLM
        self._llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        # 3. Create the Agent using 'initialize_agent'
        # This method is compatible with virtually all LangChain versions.
        # It automatically handles the prompt engineering for "Reason + Act".
        self._executor = initialize_agent(
            tools=self._langchain_tools,
            llm=self._llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True # vital for preventing crashes if the LLM output is slightly off
        )

    def run(self, user_query: str):
        """
        Executes the agent workflow on a user query.
        """
        try:
            # Note: initialize_agent uses .run() (or .invoke() in newer versions)
            # We use .run() for maximum compatibility
            return self._executor.run(user_query)
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        """
        Magic method: Allows the object to be called like a function.
        """
        return self.run(user_query)

    def __repr__(self):
        return f"<SchedulingAgent(tools={len(self._tools)})>"