from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from src.tools.base import AgentTool
import os

# --- IMPORT NEW TOOL ---
from src.tools.preferences import PreferenceTool  # <--- NEW

# --- SYSTEM PROMPT ---
# We update the prompt to tell the Agent to check preferences!
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
1. **CHECK PREFERENCES**: If the user asks to book a meeting, consider checking 'manage_preferences' (read_all) first to see if they have specific rules (e.g., no meetings on Friday).
2. **MEMORY**: Use the chat history to understand context.
3. **SAFETY**: Before executing 'delete_event', you MUST ask the user for confirmation.
4. **CONFLICTS**: Always run 'list_events' before creating/rescheduling.
5. **DATE**: Today's date is provided in context.

Previous conversation history:
{chat_history}

Begin!

User Input: {input}
Thought:{agent_scratchpad}
"""

class SchedulingAgent:
    def __init__(self, tools: list[AgentTool]):
        self._tools = tools
        
        # 1. Initialize Tools
        self._langchain_tools = [
            Tool(
                name=tool.name,
                func=tool.execute,
                description=tool.description
            )
            for tool in tools
        ]
        
        # 2. ADD PREFERENCE TOOL
        pref_tool = PreferenceTool()
        self._langchain_tools.append(
            Tool(
                name=pref_tool.name,
                func=pref_tool.execute,
                description=pref_tool.description
            )
        )

        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
        
        # 3. Initialize LLM
        # Trying 'gemini-pro' (1.0 Pro) as a fallback since 1.5 failed for you
        # This usually has better availability than Flash-Latest
        self._llm = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            temperature=0
        )

        # 4. Setup Prompt
        prompt = PromptTemplate(
            template=CUSTOM_SYSTEM_PROMPT,
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", "chat_history"]
        )
        
        # 5. Setup Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 6. Create Agent
        agent_construct = create_react_agent(self._llm, self._langchain_tools, prompt)
        
        # 7. Create Executor
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