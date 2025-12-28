from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain import hub
from src.tools.base import AgentTool
import os

class SchedulingAgent:
    """
    The Agent's core, utilizing Google Gemini 1.5 Flash with Modern Tool Calling.
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

        # 2. Initialize Gemini 1.5 Flash
        # We use the modern model which is supported by the latest libraries
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
            
        self._llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        # 3. Pull the "Tool Calling" Prompt
        # This prompt is optimized for modern agents
        prompt = hub.pull("hwchase17/openai-tools-agent")
        
        # 4. Create the Agent using 'create_tool_calling_agent'
        # This function exists in the latest langchain version
        agent_construct = create_tool_calling_agent(self._llm, self._langchain_tools, prompt)
        
        # 5. Create Executor
        self._executor = AgentExecutor(agent=agent_construct, tools=self._langchain_tools, verbose=True)

    def run(self, user_query: str):
        try:
            return self._executor.invoke({"input": user_query})["output"]
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        return self.run(user_query)