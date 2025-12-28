from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from src.tools.base import AgentTool

class SchedulingAgent:
    """
    The Agent's core, responsible for decision-making and tool orchestration.
    """
    def __init__(self, tools: list[AgentTool]):
        self._tools = tools
        self._memory = []
        
        # 1. Convert your custom AgentTools into LangChain-compatible Tools
        self._langchain_tools = [
            Tool(
                name=tool.name,
                func=tool.execute,
                description=tool.description
            )
            for tool in tools
        ]

        # 2. Initialize the LLM
        # Ensure OPENAI_API_KEY is in your .env file
        self._llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # 3. Create the Agent using 'initialize_agent' (Compatible with older versions)
        # We use ZERO_SHOT_REACT_DESCRIPTION which lets the AI pick the tool based on description
        self._executor = initialize_agent(
            tools=self._langchain_tools,
            llm=self._llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True  # Keeps the agent from crashing if output is imperfect
        )

    def run(self, user_query: str):
        """
        Executes the agent workflow on a user query.
        """
        try:
            # Note: initialize_agent uses .run() instead of .invoke()
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