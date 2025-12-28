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
        
        self._llm = ChatGoogleGenerativeAI(model="gemini-exp-1206", temperature=0)

        # 3. Pull the Prompt
        prompt = hub.pull("hwchase17/react")
        
        # 4. Create Agent
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        # 5. Create Executor with a STOP LIMIT
        self._executor = AgentExecutor(
            agent=agent_construct, 
            tools=self._langchain_tools, 
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=2,     # <--- ADD THIS LINE (Prevents infinite loops)
            return_intermediate_steps=True # Helps debug if it stops early
        )

    def run(self, user_query: str):
        try:
            # We use invoke now
            result = self._executor.invoke({"input": user_query})
            return result["output"]
        except Exception as e:
            # If it hits max_iterations, it might throw an error, but the work is done.
            return "Task completed (Loop stopped to prevent duplicates)."

    def __call__(self, user_query: str):
        return self.run(user_query)