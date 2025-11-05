"""LLM Agent for natural language processing with multi-provider support (Claude, OpenAI, Gemini)"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, Optional, List, Any
from abc import ABC, abstractmethod

from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.models.event import Event

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

    @abstractmethod
    def call_llm(self, messages: List[Dict], tools: List[Dict], max_tokens: int) -> Dict:
        """Call the LLM API

        Returns:
            Dict with 'content', 'tool_calls' keys
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name"""
        pass


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider with lazy initialization"""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.api_key = config.get_api_key('anthropic')
        self.model = config.get_claude_model()
        self.client = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization - only load anthropic when actually needed"""
        if self._initialized:
            return

        self._initialized = True
        if self.api_key:
            try:
                logger.info(f"Initializing Claude provider: {self.model}")
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                logger.info(f"Claude provider initialized successfully")
            except ImportError:
                logger.error("anthropic package not installed. Run: pip install anthropic")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
                self.client = None

    def is_available(self) -> bool:
        if not self._initialized and self.api_key:
            self._ensure_initialized()
        return self.client is not None

    def get_provider_name(self) -> str:
        return "claude"

    def call_llm(self, messages: List[Dict], tools: List[Dict], max_tokens: int) -> Dict:
        """Call Claude API"""
        self._ensure_initialized()  # Lazy load on first API call

        # Convert OpenAI-style messages to Claude format
        claude_messages = []
        system_message = None

        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                claude_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

        # Convert OpenAI-style tools to Claude format
        claude_tools = []
        for tool in tools:
            func = tool['function']
            claude_tools.append({
                'name': func['name'],
                'description': func['description'],
                'input_schema': func['parameters']
            })

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_message or "You are a helpful scheduling assistant.",
            messages=claude_messages,
            tools=claude_tools if claude_tools else None
        )

        # Convert response to standard format
        result = {
            'content': None,
            'tool_calls': []
        }

        for block in response.content:
            if block.type == 'text':
                result['content'] = block.text
            elif block.type == 'tool_use':
                result['tool_calls'].append({
                    'id': block.id,
                    'type': 'function',
                    'function': {
                        'name': block.name,
                        'arguments': json.dumps(block.input)
                    }
                })

        return result


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider with lazy initialization"""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.api_key = config.get_api_key('openai')
        self.model = config.get_openai_model()
        self.client = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization - only load openai when actually needed"""
        if self._initialized:
            return

        self._initialized = True
        if self.api_key:
            try:
                logger.info(f"Initializing OpenAI provider: {self.model}")
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI provider initialized successfully")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def is_available(self) -> bool:
        if not self._initialized and self.api_key:
            self._ensure_initialized()
        return self.client is not None

    def get_provider_name(self) -> str:
        return "openai"

    def call_llm(self, messages: List[Dict], tools: List[Dict], max_tokens: int) -> Dict:
        """Call OpenAI API"""
        self._ensure_initialized()  # Lazy load on first API call

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=max_tokens,
            temperature=0.7
        )

        message = completion.choices[0].message

        return {
            'content': message.content,
            'tool_calls': message.tool_calls
        }


class LLMAgent:
    """Multi-provider LLM agent for processing natural language scheduling requests"""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize LLM Agent with configured provider

        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager or ConfigManager()
        self.conversation_history: List[Dict[str, Any]] = []

        # Determine provider
        self.provider_name = self.config.get_llm_provider()
        self.provider = self._initialize_provider()

        # Configuration
        self.max_tokens = self.config.get_max_tokens()
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _initialize_provider(self) -> Optional[BaseLLMProvider]:
        """Initialize the configured LLM provider"""
        provider_map = {
            'claude': ClaudeProvider,
            'anthropic': ClaudeProvider,
            'openai': OpenAIProvider,
            # 'gemini': GeminiProvider,  # TODO: Implement if needed
        }

        provider_class = provider_map.get(self.provider_name.lower())

        if not provider_class:
            logger.error(f"Unknown LLM provider: {self.provider_name}. Supported: {list(provider_map.keys())}")
            return None

        try:
            provider = provider_class(self.config)
            if provider.is_available():
                logger.info(f"LLM Agent initialized with provider: {self.provider_name}")
                return provider
            else:
                logger.warning(f"{self.provider_name} provider not available (check API key)")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider_name} provider: {e}", exc_info=True)
            return None

    def is_available(self) -> bool:
        """Check if LLM agent is available (provider initialized)

        Returns:
            bool: True if LLM agent can be used
        """
        return self.provider is not None and self.provider.is_available()

    def get_current_provider(self) -> str:
        """Get current provider name

        Returns:
            str: Provider name ('claude', 'openai', etc.) or 'none'
        """
        if self.provider:
            return self.provider.get_provider_name()
        return "none"

    def _get_tool_definitions(self) -> List[Dict]:
        """Get function/tool definitions (OpenAI format, compatible with Claude)

        Returns:
            List of tool definitions
        """
        return [{
            "type": "function",
            "function": {
                "name": "schedule_calendar_event",
                "description": "Create a new event in Google Calendar. Use this tool when the user wants to schedule, add, or create an event. The start and end times can be in natural language (e.g., 'tomorrow 2pm', '今天晚上8點') or standard format (YYYY-MM-DD HH:MM:SS).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Event title or summary (e.g., 'Meeting with advisor', '與導師會面')"
                        },
                        "start_time_str": {
                            "type": "string",
                            "description": "Event start time in natural language or standard format. Examples: 'tomorrow 2pm', '明天下午2點', '2025-11-05 14:00:00', 'today at 8pm', '今天晚上8點'"
                        },
                        "end_time_str": {
                            "type": "string",
                            "description": "Event end time in natural language or standard format. Can be relative to start time (e.g., '3pm', '9pm', '9點') or duration-based."
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description of the event"
                        },
                        "location": {
                            "type": "string",
                            "description": "Optional location of the event"
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of participant email addresses"
                        }
                    },
                    "required": ["summary", "start_time_str", "end_time_str"]
                }
            }
        }]

    def _create_system_message(self) -> str:
        """Create system message with current context

        Returns:
            System message string
        """
        current_time = datetime.now()
        timezone = self.config.get_timezone()

        system_message = f"""You are an intelligent scheduling assistant that helps users manage their Google Calendar.

Current Context:
- Current date and time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ({current_time.strftime('%A')})
- Timezone: {timezone}
- Day of week: {current_time.strftime('%A')}

Your capabilities:
1. Create calendar events from natural language requests
2. Understand both English and Chinese (繁體中文)
3. Parse relative time expressions (e.g., "tomorrow", "明天", "next Monday", "下週一")
4. Parse specific time expressions (e.g., "2pm", "下午2點", "晚上8點")

When the user wants to schedule an event:
1. Extract the event title/summary
2. Identify the start time (can be natural language)
3. Identify the end time (can be natural language or relative to start)
4. Extract any additional details (description, location, participants)
5. Call the schedule_calendar_event function with the extracted information

Important notes:
- For Chinese time expressions like "下午2點" or "晚上8點", pass them as-is to the function
- For relative dates like "tomorrow" or "明天", pass them as-is
- If the user doesn't specify an end time, make a reasonable assumption (e.g., 1 hour for meetings)
- If the user doesn't specify a date, assume they mean today or the nearest logical date
- Always be helpful and confirm what you understood before creating the event

Be conversational and friendly. Confirm the details before scheduling."""

        return system_message

    def process_request(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a natural language scheduling request

        Args:
            user_input: User's natural language request
            context: Optional context dictionary (e.g., user profile, existing events)

        Returns:
            Dictionary with processing results:
            {
                'success': bool,
                'response': str,  # Assistant's response
                'action': str,  # Action taken (e.g., 'schedule_event')
                'data': dict,  # Any structured data (e.g., event details)
                'provider': str,  # Which LLM provider was used
                'error': str  # Error message if failed
            }
        """
        if not self.is_available():
            return {
                'success': False,
                'response': f"LLM agent is not available. Please configure {self.provider_name.upper()}_API_KEY in .env file.",
                'error': "Provider not available"
            }

        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })

            # Prepare messages for API call
            messages = [
                {"role": "system", "content": self._create_system_message()}
            ] + self.conversation_history

            # Call LLM API with retry logic
            response_data = None
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Calling {self.provider_name} API (attempt {attempt + 1}/{self.max_retries})")
                    response_data = self.provider.call_llm(
                        messages=messages,
                        tools=self._get_tool_definitions(),
                        max_tokens=self.max_tokens
                    )
                    break
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"API call failed (attempt {attempt + 1}): {e}. Retrying in {self.retry_delay}s...")
                        time.sleep(self.retry_delay)
                        self.retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        raise

            if not response_data:
                raise Exception(f"Failed to get response from {self.provider_name} API")

            # Add assistant's response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_data['content'],
                "tool_calls": response_data.get('tool_calls')
            })

            # Check if tool was called
            tool_calls = response_data.get('tool_calls', [])
            if tool_calls:
                tool_call = tool_calls[0]

                # Handle different tool call formats (OpenAI vs Claude)
                if hasattr(tool_call, 'function'):
                    # OpenAI format
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                else:
                    # Claude/dict format
                    function_name = tool_call.get('function', {}).get('name')
                    function_args = json.loads(tool_call.get('function', {}).get('arguments', '{}'))

                if function_name == "schedule_calendar_event":
                    logger.info(f"LLM requested to schedule event: {function_args.get('summary')}")

                    return {
                        'success': True,
                        'response': response_data['content'] or f"I'll schedule '{function_args.get('summary')}' for you.",
                        'action': 'schedule_event',
                        'data': function_args,
                        'provider': self.provider_name
                    }

            # No tool call - just conversation
            return {
                'success': True,
                'response': response_data['content'] or "I'm here to help you schedule events. What would you like to add to your calendar?",
                'action': 'conversation',
                'data': {},
                'provider': self.provider_name
            }

        except Exception as e:
            logger.error(f"Error processing request with {self.provider_name}: {e}", exc_info=True)
            return {
                'success': False,
                'response': f"Sorry, I encountered an error processing your request: {str(e)}",
                'error': str(e),
                'provider': self.provider_name
            }

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.retry_delay = 1  # Reset retry delay
        logger.info("Conversation history reset")

    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history

        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
