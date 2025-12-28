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

        # 2. Initialize Gemini
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
            
        # FIX: Use 'gemini-pro' which is fully supported by this library version
        self._llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

        # 3. Create the Agent using 'initialize_agent'
        # This function exists in langchain==0.2.16
        self._executor = initialize_agent(
            tools=self._langchain_tools,
            llm=self._llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )

    def run(self, user_query: str):
        try:
            return self._executor.run(user_query)
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        return self.run(user_query)