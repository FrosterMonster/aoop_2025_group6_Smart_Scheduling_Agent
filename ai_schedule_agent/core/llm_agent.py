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


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider with lazy initialization"""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.api_key = config.get_api_key('gemini')
        self.model = config.get_gemini_model()
        self.client = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization - only load google-generativeai when actually needed"""
        if self._initialized:
            return

        self._initialized = True
        if self.api_key:
            try:
                logger.info(f"Initializing Gemini provider: {self.model}")
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
                logger.info(f"Gemini provider initialized successfully")
            except ImportError:
                logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None

    def is_available(self) -> bool:
        if not self._initialized and self.api_key:
            self._ensure_initialized()
        return self.client is not None

    def get_provider_name(self) -> str:
        return "gemini"

    def call_llm(self, messages: List[Dict], tools: List[Dict], max_tokens: int) -> Dict:
        """Call Gemini API with structured output or simple text response"""
        self._ensure_initialized()  # Lazy load on first API call
        import google.generativeai as genai

        # Build the full prompt with system message and user input
        system_message = None
        user_message = None

        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            elif msg['role'] == 'user':
                user_message = msg['content']

        # Check if this is a simple text prompt (no tools)
        if not tools or len(tools) == 0:
            # Simple text generation without structured output
            full_prompt = ""
            if system_message:
                full_prompt += f"{system_message}\n\n"
            full_prompt += user_message

            try:
                generation_config = genai.GenerationConfig(
                    max_output_tokens=max_tokens
                )
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )

                return {
                    'content': response.text if hasattr(response, 'text') else '',
                    'tool_calls': [],
                    'action': 'chat'
                }
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Try to get partial response
                try:
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and candidate.content.parts:
                            partial_text = ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                            if partial_text:
                                return {'content': partial_text, 'tool_calls': [], 'action': 'chat'}
                except:
                    pass
                return {'content': '', 'tool_calls': [], 'action': 'chat', 'error': str(e)}

        # Combine system message with user input and tool instructions
        full_prompt = ""
        if system_message:
            full_prompt += f"{system_message}\n\n"

        if tools:
            # Add structured output instructions
            full_prompt += """Analyze the user's request and respond with structured JSON.

=== QUERY ACTIONS ===
When user wants to VIEW/CHECK their schedule:
{
  "action": "query",
  "query": {
    "query_type": "show_schedule" | "find_event" | "check_availability" | "list_events",
    "time_range": "tomorrow" | "next week" | "Friday afternoon" | "this month",
    "search_term": "Alex" | "team meeting" | "dentist" (for find_event)
  },
  "response": "I'll show you your schedule for [timeframe]."
}

Examples:
- "What's on my calendar tomorrow?" -> query (show_schedule, time_range: "tomorrow")
- "When is my meeting with Alex?" -> query (find_event, search_term: "Alex")
- "Am I free Friday afternoon?" -> query (check_availability, time_range: "Friday afternoon")
- "Show me next week" -> query (show_schedule, time_range: "next week")

=== EDIT ACTIONS ===
When user wants to MODIFY an existing event:
{
  "action": "edit_event",
  "edit": {
    "event_identifier": "3pm meeting" | "meeting with Alex" | "tomorrow's standup",
    "changes": {
      "new_time": "4pm" (if changing time),
      "new_duration": "2 hours" (if extending),
      "new_location": "Zoom" (if changing location),
      "add_participants": ["alex@email.com"] (if adding people),
      "remove_participants": ["john@email.com"] (if removing people)
    }
  },
  "response": "I'll update your [event] with the new details."
}

Examples:
- "Move my 3pm meeting to 4pm" -> edit_event (event: "3pm meeting", new_time: "4pm")
- "Change tomorrow's location to Zoom" -> edit_event (event: "tomorrow's meeting", new_location: "Zoom")
- "Add Sarah to my 2pm meeting" -> edit_event (event: "2pm meeting", add_participants: ["Sarah"])
- "Make my lunch meeting 30 minutes longer" -> edit_event (event: "lunch meeting", new_duration: "+30 minutes")

=== MOVE ACTIONS ===
When user wants to RESCHEDULE (simpler than edit):
{
  "action": "move_event",
  "move": {
    "event_identifier": "3pm meeting",
    "new_time": "tomorrow at 2pm" | "next week same time" | "Friday afternoon"
  },
  "response": "I'll move your [event] to [new time]."
}

Examples:
- "Reschedule my morning meeting to afternoon" -> move_event
- "Move everything after 3pm to tomorrow" -> move_event (can be multiple)

=== DELETE ACTIONS ===
When user wants to CANCEL/REMOVE events:
{
  "action": "delete_event",
  "delete": {
    "event_identifier": "3pm meeting" | "team standup",
    "time_range": "Friday afternoon" | "all meetings with John" (for bulk delete)
  },
  "response": "I'll cancel your [event]."
}

Examples:
- "Cancel my 3pm meeting" -> delete_event (event: "3pm meeting")
- "Delete tomorrow's team standup" -> delete_event (event: "tomorrow's team standup")
- "Clear my schedule for Friday afternoon" -> delete_event (time_range: "Friday afternoon")
- "Remove all meetings with John" -> delete_event (time_range: "all meetings with John")

=== MULTI-SCHEDULE ACTIONS ===
When user wants to schedule MULTIPLE events at once:
{
  "action": "multi_schedule",
  "multi_events": [
    {"summary": "Interview 1", "start_time_str": "tomorrow 10am", "end_time_str": "1 hour"},
    {"summary": "Interview 2", "start_time_str": "tomorrow 2pm", "end_time_str": "1 hour"},
    {"summary": "Interview 3", "start_time_str": "tomorrow 4pm", "end_time_str": "1 hour"}
  ],
  "response": "I'll schedule 3 interviews for you tomorrow."
}

Examples:
- "Schedule 3 interviews tomorrow at 10am, 2pm, and 4pm" -> multi_schedule
- "Block Monday through Wednesday for focus time" -> multi_schedule (3 events)

=== CHECK SCHEDULE THEN BOOK ===
When user wants to schedule WITHOUT specific time:
{
  "action": "check_schedule",
  "date": "11/7" | "tomorrow" | "next week",
  "duration": "3 hours" | "4 hrs" | "90 minutes",
  "event_details": {
    "summary": "event title",
    "description": "optional",
    "location": "optional"
  },
  "response": "Let me check your schedule for [date] to find a good time."
}

Examples:
- "Schedule 4hr study session on 11/7" -> check_schedule (no specific time)
- "Need to meet with team sometime" -> check_schedule (vague request)
- "Block time for project work" -> check_schedule (no specific time)

=== DIRECT SCHEDULING ===
When scheduling WITH specific time:
{
  "action": "schedule_event",
  "event": {
    "summary": "clear event title",
    "start_time_str": "MUST include both date AND time. Examples: 'tomorrow 3pm', 'today 9am', 'Friday 10:00', '2025-11-27 21:00'",
    "end_time_str": "PREFER duration format: '1 hour', '90 minutes', '3 hours'. Alternative: end time like 'tomorrow 4pm'",
    "description": "optional details",
    "location": "optional location or 'Online'",
    "participants": ["optional@email.com"]
  },
  "response": "I've scheduled [event] for [time]."
}

IMPORTANT RULES:
1. start_time_str MUST have BOTH date AND time (not just "9pm" - say "today 9pm" or "tomorrow 9pm")
2. end_time_str should be DURATION when possible ("1 hour", "2 hours", "30 minutes")
3. If user doesn't specify duration, use "1 hour" for meetings, "30 minutes" for calls
4. summary must be descriptive (good: "Team Meeting", bad: "Meeting")

Examples:
✓ "Meeting tomorrow at 2pm" -> start_time_str: "tomorrow 2pm", end_time_str: "1 hour"
✓ "Call today 9am for 30 minutes" -> start_time_str: "today 9am", end_time_str: "30 minutes"
✓ "Team lunch Friday noon" -> start_time_str: "Friday 12pm", end_time_str: "1 hour"
✗ "Meeting at 2pm" -> BAD (missing date - should be "today 2pm" or "tomorrow 2pm")

=== CHAT (NON-SCHEDULING) ===
{
  "action": "chat",
  "response": "Your helpful response"
}

"""

        full_prompt += f"User request: {user_message}"

        # Define response schema for structured output
        response_schema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to take",
                    "enum": ["check_schedule", "schedule_event", "query", "edit_event", "delete_event", "move_event", "multi_schedule", "chat"]
                },
                "date": {
                    "type": "string",
                    "description": "Date to check schedule (for check_schedule action)"
                },
                "duration": {
                    "type": "string",
                    "description": "Required duration (for check_schedule action)"
                },
                "event_details": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Event title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description"
                        },
                        "location": {
                            "type": "string",
                            "description": "Optional location"
                        }
                    }
                },
                "event": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Event title or summary"
                        },
                        "start_time_str": {
                            "type": "string",
                            "description": "Event start time"
                        },
                        "end_time_str": {
                            "type": "string",
                            "description": "Event end time or duration"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional event description"
                        },
                        "location": {
                            "type": "string",
                            "description": "Optional event location"
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional participant emails"
                        }
                    }
                },
                "response": {
                    "type": "string",
                    "description": "Your response message to the user"
                },
                "query": {
                    "type": "object",
                    "description": "Query details (for query action)",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["show_schedule", "find_event", "check_availability", "list_events"],
                            "description": "Type of query"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "Time range to query (e.g., 'tomorrow', 'next week', 'Friday afternoon')"
                        },
                        "search_term": {
                            "type": "string",
                            "description": "Search term for finding specific events (e.g., person name, meeting title)"
                        }
                    }
                },
                "edit": {
                    "type": "object",
                    "description": "Edit details (for edit_event action)",
                    "properties": {
                        "event_identifier": {
                            "type": "string",
                            "description": "How to identify the event (e.g., '3pm meeting', 'meeting with Alex', 'tomorrow morning meeting')"
                        },
                        "changes": {
                            "type": "object",
                            "properties": {
                                "new_time": {"type": "string", "description": "New time if changing time"},
                                "new_duration": {"type": "string", "description": "New duration if extending/shortening"},
                                "new_location": {"type": "string", "description": "New location if changing location"},
                                "add_participants": {"type": "array", "items": {"type": "string"}, "description": "Participants to add"},
                                "remove_participants": {"type": "array", "items": {"type": "string"}, "description": "Participants to remove"}
                            }
                        }
                    }
                },
                "delete": {
                    "type": "object",
                    "description": "Delete details (for delete_event action)",
                    "properties": {
                        "event_identifier": {
                            "type": "string",
                            "description": "How to identify the event to delete"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "Time range for bulk delete (e.g., 'Friday afternoon', 'all meetings with John')"
                        }
                    }
                },
                "move": {
                    "type": "object",
                    "description": "Move details (for move_event action)",
                    "properties": {
                        "event_identifier": {
                            "type": "string",
                            "description": "Event to move"
                        },
                        "new_time": {
                            "type": "string",
                            "description": "New time (e.g., '4pm', 'tomorrow', 'next week same time')"
                        }
                    }
                },
                "multi_events": {
                    "type": "array",
                    "description": "Multiple events (for multi_schedule action)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"},
                            "start_time_str": {"type": "string"},
                            "end_time_str": {"type": "string"},
                            "description": {"type": "string"},
                            "location": {"type": "string"}
                        }
                    }
                },
                "check_schedule": {
                    "type": "object",
                    "description": "Check schedule details (for check_schedule action)",
                    "properties": {
                        "event_details": {
                            "type": "object",
                            "properties": {
                                "summary": {"type": "string"},
                                "description": {"type": "string"},
                                "location": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "required": ["action", "response"]
        }

        # Convert schema to Gemini format
        gemini_schema = self._build_gemini_schema(response_schema)

        # Call Gemini API with structured output
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=gemini_schema,
            max_output_tokens=max_tokens
        )

        response = self.client.generate_content(
            full_prompt,
            generation_config=generation_config
        )

        # Parse the structured JSON response
        try:
            structured_data = json.loads(response.text)

            result = {
                'content': structured_data.get('response', ''),
                'tool_calls': [],
                'action': structured_data.get('action', 'chat')  # Include action in result
            }

            # Handle check_schedule action
            if structured_data.get('action') == 'check_schedule':
                result['check_schedule'] = {
                    'date': structured_data.get('date'),
                    'duration': structured_data.get('duration'),
                    'event_details': structured_data.get('event_details', {})
                }

            # Convert to tool call format if action is schedule_event
            elif structured_data.get('action') == 'schedule_event' and 'event' in structured_data:
                result['tool_calls'].append({
                    'id': 'gemini_structured_call',
                    'type': 'function',
                    'function': {
                        'name': 'schedule_calendar_event',
                        'arguments': json.dumps(structured_data['event'])
                    }
                })

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini structured output: {e}")
            return {
                'content': response.text,
                'tool_calls': [],
                'action': 'chat'
            }

    def _build_gemini_schema(self, schema_dict: Dict) -> Dict:
        """Build Gemini schema from a dict-based schema definition

        Args:
            schema_dict: Schema definition as a dictionary

        Returns:
            Schema dict compatible with Gemini's response_schema parameter
        """
        result = {}

        # Copy basic properties
        if 'type' in schema_dict:
            result['type'] = schema_dict['type'].upper()

        if 'description' in schema_dict:
            result['description'] = schema_dict['description']

        if 'enum' in schema_dict:
            result['enum'] = schema_dict['enum']

        # Handle object properties
        if 'properties' in schema_dict:
            result['properties'] = {}
            for key, prop in schema_dict['properties'].items():
                result['properties'][key] = self._build_gemini_schema(prop)

        # Handle required fields
        if 'required' in schema_dict:
            result['required'] = schema_dict['required']

        # Handle array items
        if 'items' in schema_dict:
            result['items'] = self._build_gemini_schema(schema_dict['items'])

        return result

    def _convert_property_schema(self, prop: Dict) -> 'genai.protos.Schema':
        """Convert OpenAI property schema to Gemini Schema (deprecated, kept for compatibility)"""
        import google.generativeai as genai

        prop_type = prop.get('type', 'string')
        schema_kwargs = {
            'type': self._convert_type(prop_type),
            'description': prop.get('description', '')
        }

        # Handle array type - must include items
        if prop_type == 'array' and 'items' in prop:
            items_type = prop['items'].get('type', 'string')
            schema_kwargs['items'] = genai.protos.Schema(
                type=self._convert_type(items_type)
            )

        return genai.protos.Schema(**schema_kwargs)

    def _convert_type(self, openai_type: str) -> int:
        """Convert OpenAI type to Gemini type enum (deprecated, kept for compatibility)"""
        import google.generativeai as genai
        type_map = {
            'string': genai.protos.Type.STRING,
            'integer': genai.protos.Type.INTEGER,
            'number': genai.protos.Type.NUMBER,
            'boolean': genai.protos.Type.BOOLEAN,
            'array': genai.protos.Type.ARRAY,
            'object': genai.protos.Type.OBJECT,
        }
        return type_map.get(openai_type, genai.protos.Type.STRING)


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
            'gemini': GeminiProvider,  # Gemini support added
            'google': GeminiProvider,  # Alias for gemini
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
                            "description": "Event title or summary (e.g., 'Meeting with advisor', '與導師會面'). Must be clear and descriptive."
                        },
                        "start_time_str": {
                            "type": "string",
                            "description": "Event start time with BOTH date and time. IMPORTANT: Always include the DATE (not just time). Good examples: 'tomorrow 2pm', 'today 8pm', '2025-11-15 14:00', 'next Monday 3pm'. BAD examples: '2pm' (missing date), '14:00' (missing date)."
                        },
                        "end_time_str": {
                            "type": "string",
                            "description": "Event duration or end time. Prefer DURATION format for clarity. Good examples: '1 hour', '90 minutes', '2 hours', '30 mins'. Alternative: actual end time like 'tomorrow 3pm', 'today 9pm'. If user doesn't specify, use reasonable default (1 hour for meetings, 30 mins for calls)."
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description or notes about the event"
                        },
                        "location": {
                            "type": "string",
                            "description": "Optional location of the event (room, address, or 'Online' for virtual meetings)"
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of participant email addresses or names"
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

CRITICAL: When calling schedule_calendar_event function:

1. **summary**: Clear, descriptive title (required)
   - Good: "Team Meeting with John", "Lunch with Sarah"
   - Bad: "Meeting" (too vague)

2. **start_time_str**: MUST include BOTH date AND time (required)
   - Good: "tomorrow 2pm", "today 8pm", "next Monday 3pm", "2025-11-15 14:00"
   - Bad: "2pm" (missing date), "14:00" (missing date), "tomorrow" (missing time)
   - If user only says "2pm", infer the date based on context (usually today or tomorrow)

3. **end_time_str**: Prefer DURATION format (required)
   - Best: "1 hour", "90 minutes", "2 hours", "30 mins"
   - Alternative: Full end time like "tomorrow 3pm", "today 9pm"
   - Default if not specified: "1 hour" for meetings, "30 minutes" for calls/quick meetings

4. **description**: Additional details or notes (optional)
5. **location**: Where the event takes place (optional)
6. **participants**: List of email addresses or names (optional)

Examples of CORRECT function calls:

User: "Schedule meeting with John tomorrow at 2pm"
→ summary: "Meeting with John"
→ start_time_str: "tomorrow 2pm"
→ end_time_str: "1 hour"

User: "Team standup today at 9am for 30 minutes"
→ summary: "Team standup"
→ start_time_str: "today 9am"
→ end_time_str: "30 minutes"

User: "Coffee chat next Monday 3pm"
→ summary: "Coffee chat"
→ start_time_str: "next Monday 3pm"
→ end_time_str: "1 hour"

Always confirm the extracted details with the user in your response. Be conversational and friendly."""

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

            # Check for check_schedule action (Gemini specific)
            if response_data.get('action') == 'check_schedule' and 'check_schedule' in response_data:
                check_data = response_data['check_schedule']
                logger.info(f"LLM requested to check schedule for: {check_data.get('date')} (duration: {check_data.get('duration')})")

                return {
                    'success': True,
                    'response': response_data['content'],
                    'action': 'check_schedule',
                    'data': check_data,
                    'provider': self.provider_name
                }

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
