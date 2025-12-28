from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from src.tools.base import AgentTool
from src.tools.preferences import PreferenceTool
import os

# --- Week 5 最終版 Prompt ---
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
1. **MEMORY**: Use the chat history to understand context (e.g., "it", "that meeting").
2. **SAFETY**: Before executing 'delete_event', you MUST ask the user for confirmation (e.g., "Are you sure you want to delete...?").
   - If the user says "Yes", proceed to delete.
   - If the user says "No", stop.
3. **CONFLICTS**: Always run 'list_events' before creating/rescheduling to check for conflicts.
4. **DATE**: Today is available in the input context.

Previous conversation history:
{chat_history}

Begin!

User Input: {input}
Thought:{agent_scratchpad}
"""

class SchedulingAgent:
    def __init__(self, tools: list[AgentTool]):
        self._tools = tools
        
        self._langchain_tools = [
            
            
            Tool(
                name=tool.name,
                func=tool.execute,
                description=tool.description
            )
            
            Tool(
                name=PreferenceTool.name,
                func=PreferenceTool().execute,
                description=PreferenceTool.description
            )
            
            for tool in tools
        ]

        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
        
        # 使用 Google 最穩定的免費模型
        self._llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
        # 設定 Prompt
        prompt = PromptTemplate(
            template=CUSTOM_SYSTEM_PROMPT,
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", "chat_history"]
        )
        
        # 初始化記憶體
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 建立 Agent
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        # 建立執行器 (掛載記憶體)
        self._executor = AgentExecutor(
            agent=agent_construct, 
            tools=self._langchain_tools, 
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            memory=self.memory
        )

    def run(self, user_query: str):
        try:
            result = self._executor.invoke({"input": user_query})
            return result["output"]
        except Exception as e:
            return f"Agent failed: {e}"

    def __call__(self, user_query: str):
        return self.run(user_query)