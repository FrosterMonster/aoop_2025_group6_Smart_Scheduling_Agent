from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
# This function DEFINITELY exists in langchain==0.2.16
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain import hub
from src.tools.base import AgentTool
import os

class SchedulingAgent:
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

        # 2. Initialize Gemini (1.5 Flash is supported by this version)
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
            
        self._llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        # 3. Pull Prompt
        prompt = hub.pull("hwchase17/openai-tools-agent")
        
        # 4. Create Agent
        agent_construct = create_tool_calling_agent(self._llm, self._langchain_tools, prompt)
        
        # 5. Executor
        self._executor = AgentExecutor(agent=agent_construct, tools=self._langchain_tools, verbose=True)

    def run(self, user_query: str):
        try:
            return self._executor.invoke({"input": user_query})["output"]
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        return self.run(user_query)