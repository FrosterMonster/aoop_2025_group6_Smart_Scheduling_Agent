from langchain_openai import ChatOpenAI 
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from src.tools.base import AgentTool

class SchedulingAgent:
    """
    The Agent's core, responsible for decision-making and tool orchestration.
    """
    def __init__(self, tools: list[AgentTool]):
        self._tools = tools  # Encapsulation: Stores your custom Tool objects
        self._memory = []    # Placeholder for Week 3
        
        # 1. Convert your custom AgentTools into LangChain-compatible Tools
        self._langchain_tools = [
            Tool(
                name=tool.name,
                func=tool.execute,
                description=tool.description
            )
            for tool in tools
        ]

        # 2. Initialize the LLM (The "Brain")
        # Ensure OPENAI_API_KEY is in your .env file
        self._llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # 3. Create the Agent using a standard ReAct prompt (Reasoning + Acting)
        # This prompt tells the LLM: "Think about what to do, use a tool, observe output."
        prompt = hub.pull("hwchase17/react") 
        
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        # AgentExecutor handles the loop: LLM -> Tool -> LLM
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
        Example: agent("schedule a meeting")
        """
        return self.run(user_query)

    def __repr__(self):
        return f"<SchedulingAgent(tools={len(self._tools)})>"