from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
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

        # 2. Initialize Gemini (The "Brain")
        # Ensure GOOGLE_API_KEY is in your .env file
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        # FIX: We use 'gemini-pro' because it is the standard model supported 
        # by the stable version of the library we installed.
        self._llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        # 3. Pull the Prompt
        # This downloads a standard "Reason+Act" prompt template
        prompt = hub.pull("hwchase17/react")
        
        # 4. Create Agent
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        # 5. Create Executor
        self._executor = AgentExecutor(agent=agent_construct, tools=self._langchain_tools, verbose=True)

    def run(self, user_query: str):
        """
        Executes the agent workflow on a user query.
        """
        try:
            # The executor runs the "Thought -> Action -> Observation" loop
            response = self._executor.invoke({"input": user_query})
            return response["output"]
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        """
        Magic method: Allows the object to be called like a function.
        """
        return self.run(user_query)

    def __repr__(self):
        return f"<SchedulingAgent(tools={len(self._tools)})>"