import sys
import os

try:
    import langchain
    import langchain.agents
    print(f"✅ LangChain Version: {langchain.__version__}")
    print(f"📂 Location: {os.path.dirname(langchain.__file__)}")
    
    # Check what agents are available
    agents = dir(langchain.agents)
    if "create_tool_calling_agent" in agents:
        print("✅ create_tool_calling_agent is AVAILABLE.")
    else:
        print("❌ create_tool_calling_agent is MISSING.")
        
    if "initialize_agent" in agents:
        print("✅ initialize_agent is AVAILABLE.")
    else:
        print("❌ initialize_agent is MISSING.")

except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")