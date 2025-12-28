from src.tools.base import AgentTool
from src.database import set_preference, get_all_preferences

class PreferenceTool(AgentTool):
    name = "manage_preferences"
    description = """
    Useful for saving user preferences (like lunch time, favorite meeting days) or reading them.
    
    Commands:
    1. SAVE: "save: [key]: [value]" 
       Example: "save: lunch_hour: 12pm to 1pm"
       
    2. READ: "read_all"
       Returns a list of all known preferences.
    """

    def execute(self, input_str: str) -> str:
        clean_input = input_str.strip()
        
        # Handle "read_all"
        if "read_all" in clean_input.lower():
            prefs = get_all_preferences()
            if not prefs:
                return "No preferences found in database."
            return f"Current User Preferences: {prefs}"
        
        # Handle "save:"
        if clean_input.lower().startswith("save:"):
            try:
                # Expected format: "save: key: value"
                # We split by ':' only for the first 2 occurrences
                parts = clean_input.split(":", 2)
                
                if len(parts) < 3:
                    return "Error: Format must be 'save: key: value'"
                
                key = parts[1].strip()
                value = parts[2].strip()
                
                set_preference(key, value)
                return f"✅ Successfully saved preference: '{key}' = '{value}'"
            except Exception as e:
                return f"Error saving preference: {str(e)}"
        
        return "Invalid input. Please use 'save: key: value' or 'read_all'."