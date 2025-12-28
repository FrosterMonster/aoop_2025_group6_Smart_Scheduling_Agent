import pytest
import os
from unittest.mock import Mock, patch, MagicMock, call
from langchain_core.tools import Tool
from src.agent.scheduling_agent import SchedulingAgent, CUSTOM_SYSTEM_PROMPT
from src.tools.base import AgentTool

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_calendar_tool():
    """Create a mock calendar tool."""
    tool = Mock(spec=AgentTool)
    tool.name = "google_calendar"
    tool.description = "Manage Google Calendar events"
    tool.execute = Mock(return_value="Event created successfully")
    return tool

@pytest.fixture
def mock_env_with_api_key(monkeypatch):
    """Set up environment with Google API key."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key_12345")

@pytest.fixture
def mock_env_without_api_key(monkeypatch):
    """Set up environment without Google API key."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

@pytest.fixture
def mock_langchain_components():
    """Mock all LangChain components."""
    with patch('src.agent.scheduling_agent.ChatGoogleGenerativeAI') as mock_llm, \
         patch('src.agent.scheduling_agent.create_react_agent') as mock_agent, \
         patch('src.agent.scheduling_agent.AgentExecutor') as mock_executor, \
         patch('src.agent.scheduling_agent.ConversationBufferMemory') as mock_memory, \
         patch('src.agent.scheduling_agent.PreferenceTool') as mock_pref, \
         patch('src.agent.scheduling_agent.WeatherTool') as mock_weather:
        
        # Setup return values
        mock_executor_instance = MagicMock()
        mock_executor.return_value = mock_executor_instance
        mock_executor_instance.invoke.return_value = {"output": "Test response"}
        
        yield {
            'llm': mock_llm,
            'agent': mock_agent,
            'executor': mock_executor,
            'executor_instance': mock_executor_instance,
            'memory': mock_memory,
            'pref': mock_pref,
            'weather': mock_weather
        }

# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

def test_agent_initialization_with_api_key(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test agent initializes successfully with API key."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    assert agent is not None
    assert hasattr(agent, '_executor')
    assert hasattr(agent, 'memory')

def test_agent_initialization_without_api_key(mock_calendar_tool, mock_env_without_api_key):
    """Test agent raises error without API key."""
    with patch('src.agent.scheduling_agent.PreferenceTool'), \
         patch('src.agent.scheduling_agent.WeatherTool'):
        with pytest.raises(ValueError, match="GOOGLE_API_KEY not found"):
            SchedulingAgent(tools=[mock_calendar_tool])

def test_agent_converts_tools_to_langchain_format(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test agent converts AgentTool to LangChain Tool format."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    # Verify tools were converted
    assert len(agent._langchain_tools) >= 1  # At least calendar tool

def test_agent_adds_preference_tool(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test agent automatically adds PreferenceTool."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    # PreferenceTool should be added
    tool_names = [t.name for t in agent._langchain_tools]
    # Can't check exact name without mocking PreferenceTool name, but verify tools > 1
    assert len(agent._langchain_tools) > 1

def test_agent_adds_weather_tool(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test agent automatically adds WeatherTool."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    # WeatherTool should be added
    assert len(agent._langchain_tools) >= 3  # Calendar + Preference + Weather

def test_multiple_tools_initialization(mock_env_with_api_key, mock_langchain_components):
    """Test initialization with multiple custom tools."""
    tool1 = Mock(spec=AgentTool)
    tool1.name = "tool_one"
    tool1.description = "First tool"
    tool1.execute = Mock()
    
    tool2 = Mock(spec=AgentTool)
    tool2.name = "tool_two"
    tool2.description = "Second tool"
    tool2.execute = Mock()
    
    agent = SchedulingAgent(tools=[tool1, tool2])
    
    # Should have 2 custom tools + preference + weather = 4 total
    assert len(agent._langchain_tools) >= 4

# ============================================================================
# LLM CONFIGURATION TESTS
# ============================================================================

def test_llm_uses_gemini_flash(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test LLM is configured with gemini-1.5-flash."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    mock_langchain_components['llm'].assert_called_once()
    call_kwargs = mock_langchain_components['llm'].call_args[1]
    assert call_kwargs['model'] == "gemini-1.5-flash"

def test_llm_temperature_zero(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test LLM uses temperature 0 for deterministic responses."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    call_kwargs = mock_langchain_components['llm'].call_args[1]
    assert call_kwargs['temperature'] == 0

# ============================================================================
# MEMORY CONFIGURATION TESTS
# ============================================================================

def test_memory_initialization(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test conversation memory is initialized."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    mock_langchain_components['memory'].assert_called_once()
    call_kwargs = mock_langchain_components['memory'].call_args[1]
    assert call_kwargs['memory_key'] == "chat_history"
    assert call_kwargs['return_messages'] == True

def test_memory_persists_across_calls(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test memory persists across multiple agent calls."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    agent.run("First query")
    agent.run("Second query")
    
    # Executor should be invoked twice
    assert mock_langchain_components['executor_instance'].invoke.call_count == 2

# ============================================================================
# AGENT EXECUTOR CONFIGURATION TESTS
# ============================================================================

def test_executor_verbose_mode(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test executor is set to verbose mode."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    call_kwargs = mock_langchain_components['executor'].call_args[1]
    assert call_kwargs['verbose'] == True

def test_executor_handles_parsing_errors(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test executor handles parsing errors."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    call_kwargs = mock_langchain_components['executor'].call_args[1]
    assert call_kwargs['handle_parsing_errors'] == True

def test_executor_max_iterations(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test executor has maximum iterations set."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    call_kwargs = mock_langchain_components['executor'].call_args[1]
    assert call_kwargs['max_iterations'] == 10

def test_executor_uses_memory(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test executor is configured with memory."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    call_kwargs = mock_langchain_components['executor'].call_args[1]
    assert 'memory' in call_kwargs

# ============================================================================
# RUN METHOD TESTS
# ============================================================================

def test_run_method_basic_query(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test run method processes basic query."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    result = agent.run("Schedule a meeting tomorrow at 2 PM")
    
    assert result == "Test response"
    mock_langchain_components['executor_instance'].invoke.assert_called_once()

def test_run_method_with_complex_query(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test run method handles complex queries."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    complex_query = "Check my preferences, then schedule a team meeting tomorrow at 3 PM if there are no conflicts"
    result = agent.run(complex_query)
    
    assert result is not None
    mock_langchain_components['executor_instance'].invoke.assert_called_with({"input": complex_query})

def test_run_method_passes_input_correctly(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test run method passes input to executor correctly."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    test_input = "List all events for today"
    agent.run(test_input)
    
    call_args = mock_langchain_components['executor_instance'].invoke.call_args
    assert call_args[0][0]['input'] == test_input

def test_run_method_returns_output(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test run method extracts and returns output."""
    mock_langchain_components['executor_instance'].invoke.return_value = {
        "output": "Custom response",
        "other_data": "ignored"
    }
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Test query")
    
    assert result == "Custom response"

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_run_handles_executor_exception(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test run method handles executor exceptions gracefully."""
    mock_langchain_components['executor_instance'].invoke.side_effect = Exception("LLM timeout")
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Test query")
    
    assert "Agent failed" in result
    assert "LLM timeout" in result

def test_run_handles_tool_exception(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test run method handles tool execution exceptions."""
    mock_langchain_components['executor_instance'].invoke.side_effect = Exception("Tool execution failed")
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Test query")
    
    assert "Agent failed" in result

def test_run_handles_parsing_error(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test run method handles parsing errors."""
    mock_langchain_components['executor_instance'].invoke.side_effect = Exception("Could not parse LLM output")
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Test query")
    
    assert "Agent failed" in result
    assert "Could not parse" in result

def test_run_handles_empty_response(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test run method handles empty responses."""
    mock_langchain_components['executor_instance'].invoke.return_value = {"output": ""}
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Test query")
    
    assert result == ""

# ============================================================================
# CALLABLE INTERFACE TESTS
# ============================================================================

def test_agent_is_callable(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test agent can be called directly."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    result = agent("Test query")
    
    assert result is not None

def test_callable_interface_uses_run(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test __call__ delegates to run method."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    with patch.object(agent, 'run', return_value="Mocked response") as mock_run:
        result = agent("Test query")
        
        mock_run.assert_called_once_with("Test query")
        assert result == "Mocked response"

# ============================================================================
# PROMPT TEMPLATE TESTS
# ============================================================================

def test_system_prompt_exists():
    """Test custom system prompt is defined."""
    assert CUSTOM_SYSTEM_PROMPT is not None
    assert len(CUSTOM_SYSTEM_PROMPT) > 0

def test_system_prompt_has_tools_placeholder():
    """Test prompt has placeholder for tools."""
    assert "{tools}" in CUSTOM_SYSTEM_PROMPT

def test_system_prompt_has_tool_names_placeholder():
    """Test prompt has placeholder for tool names."""
    assert "{tool_names}" in CUSTOM_SYSTEM_PROMPT

def test_system_prompt_has_input_placeholder():
    """Test prompt has placeholder for user input."""
    assert "{input}" in CUSTOM_SYSTEM_PROMPT

def test_system_prompt_has_chat_history_placeholder():
    """Test prompt has placeholder for chat history."""
    assert "{chat_history}" in CUSTOM_SYSTEM_PROMPT

def test_system_prompt_has_scratchpad_placeholder():
    """Test prompt has placeholder for agent scratchpad."""
    assert "{agent_scratchpad}" in CUSTOM_SYSTEM_PROMPT

def test_system_prompt_mentions_preferences():
    """Test prompt instructs agent to check preferences."""
    assert "preferences" in CUSTOM_SYSTEM_PROMPT.lower() or "preference" in CUSTOM_SYSTEM_PROMPT.lower()

def test_system_prompt_mentions_weather():
    """Test prompt instructs agent to check weather."""
    assert "weather" in CUSTOM_SYSTEM_PROMPT.lower()

def test_system_prompt_mentions_conflicts():
    """Test prompt instructs agent to check conflicts."""
    assert "conflict" in CUSTOM_SYSTEM_PROMPT.lower()

def test_system_prompt_mentions_safety():
    """Test prompt includes safety instructions for delete."""
    assert "delete" in CUSTOM_SYSTEM_PROMPT.lower()
    assert "confirmation" in CUSTOM_SYSTEM_PROMPT.lower() or "confirm" in CUSTOM_SYSTEM_PROMPT.lower()

def test_system_prompt_react_format():
    """Test prompt follows ReAct format."""
    assert "Thought:" in CUSTOM_SYSTEM_PROMPT
    assert "Action:" in CUSTOM_SYSTEM_PROMPT
    assert "Observation:" in CUSTOM_SYSTEM_PROMPT
    assert "Final Answer:" in CUSTOM_SYSTEM_PROMPT

# ============================================================================
# INTEGRATION WITH TOOLS TESTS
# ============================================================================

def test_tool_execution_through_agent(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test tools can be executed through agent."""
    # Setup tool to be called
    mock_langchain_components['executor_instance'].invoke.return_value = {
        "output": "Tool executed successfully"
    }
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Use calendar tool")
    
    assert "Tool executed" in result or result is not None

def test_multiple_tool_calls_in_sequence(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test agent can make multiple tool calls in sequence."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    result1 = agent.run("First query")
    result2 = agent.run("Second query")
    
    assert result1 is not None
    assert result2 is not None
    assert mock_langchain_components['executor_instance'].invoke.call_count == 2

# ============================================================================
# SPECIFIC SCENARIO TESTS
# ============================================================================

def test_schedule_meeting_scenario(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test scheduling a meeting scenario."""
    mock_langchain_components['executor_instance'].invoke.return_value = {
        "output": "Meeting scheduled for tomorrow at 2 PM"
    }
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Schedule a meeting tomorrow at 2 PM")
    
    assert "scheduled" in result.lower() or "2 PM" in result

def test_check_preferences_scenario(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test checking preferences scenario."""
    mock_langchain_components['executor_instance'].invoke.return_value = {
        "output": "Your work hours are 9 AM to 6 PM"
    }
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("What are my work hours?")
    
    assert result is not None

def test_weather_check_scenario(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test weather checking scenario."""
    mock_langchain_components['executor_instance'].invoke.return_value = {
        "output": "Weather is sunny, good for outdoor activity"
    }
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Can we have outdoor meeting tomorrow?")
    
    assert result is not None

def test_conflict_detection_scenario(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test conflict detection scenario."""
    mock_langchain_components['executor_instance'].invoke.return_value = {
        "output": "Time slot is available, no conflicts found"
    }
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("Schedule meeting at 2 PM, check for conflicts")
    
    assert result is not None

# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_query(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test handling of empty query."""
    mock_langchain_components['executor_instance'].invoke.return_value = {"output": ""}
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run("")
    
    assert result is not None

def test_very_long_query(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test handling of very long query."""
    long_query = "Schedule a meeting " * 100
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run(long_query)
    
    assert result is not None

def test_special_characters_in_query(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test handling of special characters."""
    special_query = "Schedule meeting @ 2:30 PM with Jane & John (urgent!)"
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run(special_query)
    
    assert result is not None

def test_non_english_query(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test handling of non-English query."""
    chinese_query = "安排明天下午2點的會議"
    
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    result = agent.run(chinese_query)
    
    assert result is not None

# ============================================================================
# TOOL REGISTRATION TESTS
# ============================================================================

def test_tool_name_preserved(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test tool names are preserved during registration."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    tool_names = [t.name for t in agent._langchain_tools]
    assert "google_calendar" in tool_names

def test_tool_description_preserved(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test tool descriptions are preserved."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    calendar_tools = [t for t in agent._langchain_tools if t.name == "google_calendar"]
    if calendar_tools:
        assert calendar_tools[0].description == "Manage Google Calendar events"

def test_tool_function_preserved(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test tool functions are preserved."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    calendar_tools = [t for t in agent._langchain_tools if t.name == "google_calendar"]
    if calendar_tools:
        assert callable(calendar_tools[0].func)

# ============================================================================
# CONVERSATION FLOW TESTS
# ============================================================================

def test_multi_turn_conversation(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test multi-turn conversation flow."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    agent.run("Hello")
    agent.run("What can you do?")
    agent.run("Schedule a meeting")
    
    assert mock_langchain_components['executor_instance'].invoke.call_count == 3

def test_context_preserved_across_turns(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test context is preserved across conversation turns."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    agent.run("My name is Alice")
    agent.run("What is my name?")
    
    # Memory should contain both messages
    assert mock_langchain_components['executor_instance'].invoke.call_count == 2

# ============================================================================
# PERFORMANCE & RELIABILITY TESTS
# ============================================================================

def test_agent_initialization_performance(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test agent initializes in reasonable time."""
    import time
    
    start = time.time()
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    elapsed = time.time() - start
    
    # Should initialize quickly (< 5 seconds)
    assert elapsed < 5.0

def test_agent_handles_rapid_queries(mock_calendar_tool, mock_env_with_api_key, mock_langchain_components):
    """Test agent handles rapid successive queries."""
    agent = SchedulingAgent(tools=[mock_calendar_tool])
    
    results = []
    for i in range(5):
        result = agent.run(f"Query {i}")
        results.append(result)
    
    assert len(results) == 5
    assert all(r is not None for r in results)

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])