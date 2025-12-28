from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from src.tools.base import AgentTool
import os

class SchedulingAgent:
    """
    The Agent's core, utilizing the stable 'gemini-flash-latest' model.
    """
    def __init__(self, tools: list[AgentTool]):
        self._tools = tools
        self._memory = []
        
        # 1. Convert Custom Tools
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
        
        # FIX: Use 'gemini-flash-latest'. 
        # This points to the currently active stable Flash model (1.5 or newer)
        # and has the most reliable free tier quota.
        self._llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

        # 3. Pull the Prompt
        prompt = hub.pull("hwchase17/react")
        
        # 4. Create Agent
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        # 5. Create Executor
        self._executor = AgentExecutor(
            agent=agent_construct, 
            tools=self._langchain_tools, 
            verbose=True,
            handle_parsing_errors=True # vital for stability
        )

    def run(self, user_query: str):
        try:
            return self._executor.invoke({"input": user_query})["output"]
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        return self.run(user_query)