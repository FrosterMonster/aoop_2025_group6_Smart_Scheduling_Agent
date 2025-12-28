from langchain_openai import ChatOpenAI 
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from src.tools.base import AgentTool

class SchedulingAgent:
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

        # 2. Initialize LLM
        self._llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # 3. Pull the Prompt (Requires langchainhub)
        prompt = hub.pull("hwchase17/react") 
        
        # 4. Create Agent
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        # 5. Create Executor
        self._executor = AgentExecutor(agent=agent_construct, tools=self._langchain_tools, verbose=True)

    def run(self, user_query: str):
        try:
            # Invoke the agent
            response = self._executor.invoke({"input": user_query})
            return response["output"]
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        return self.run(user_query)