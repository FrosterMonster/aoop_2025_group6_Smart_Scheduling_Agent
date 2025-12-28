from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from src.tools.base import AgentTool
import os

# --- 定義專屬的「排程大腦」 ---
CUSTOM_SYSTEM_PROMPT = """
You are a Smart Scheduling Assistant. Your job is to manage the user's Google Calendar.

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:

Thought: Do I need to use a tool? Yes Action: the action to take, should be one of [{tool_names}] Action Input: the input to the action Observation: the result of the action


When you have a response for the human, or if you do not need to use a tool, you MUST use the format:

Thought: Do I need to use a tool? No Final Answer: [your response here]


IMPORTANT RULES:
1. BEFORE creating any event, you MUST run 'list_events' for that specific day to check for conflicts.
2. If there is a conflict (another event at the same time), DO NOT create the event. Instead, tell the user about the conflict and suggest the next available time slot.
3. If the time slot is clear, proceed to create the event.
4. Always double-check the date. Today is available in the context.

Begin!

User Input: {input}
Thought:{agent_scratchpad}
"""

class SchedulingAgent:
    """
    Week 4 Agent: Equipped with Conflict Detection logic.
    """
    def __init__(self, tools: list[AgentTool]):
        self._tools = tools
        
        self._langchain_tools = [
            Tool(
                name=tool.name,
                func=tool.execute,
                description=tool.description
            )
            for tool in tools
        ]

        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
        
        # ▼▼▼ 修改這裡：改回 gemini-1.5-flash ▼▼▼
        self._llm = ChatGoogleGenerativeAI(model="gemini-exp-1206", temperature=0)
        # --- 使用自定義 Prompt ---
        prompt = PromptTemplate.from_template(CUSTOM_SYSTEM_PROMPT)
        
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        self._executor = AgentExecutor(
            agent=agent_construct, 
            tools=self._langchain_tools, 
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10, 
            return_intermediate_steps=True
        )

    def run(self, user_query: str):
        try:
            result = self._executor.invoke({"input": user_query})
            return result["output"]
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        return self.run(user_query)