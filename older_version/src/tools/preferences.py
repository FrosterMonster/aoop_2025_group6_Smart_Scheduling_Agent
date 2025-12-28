from src.tools.base import AgentTool
from src.database import set_preference, get_all_preferences

class PreferenceTool(AgentTool):
    name = "manage_preferences"
    description = """
    Useful for saving or reading user preferences.
    Input should be a string describing the action:
    - To SAVE: "save: [key]: [value]" (e.g., "save: lunch_time: 12PM-1PM")
    - To READ: "read_all"
    """

    def execute(self, input_str: str) -> str:
        if input_str.strip() == "read_all":
            prefs = get_all_preferences()
            if not prefs:
                return "No preferences found."
            return f"Current User Preferences: {prefs}"
        
        if input_str.startswith("save:"):
            try:
                # Parse "save: key: value"
                parts = input_str.replace("save:", "").split(":", 1)
                key = parts[0].strip()
                value = parts[1].strip()
                set_preference(key, value)
                return f"Successfully saved preference: {key} = {value}"
            except Exception:
                return "Error parsing save command. Use format 'save: key: value'"
        
        return "Invalid command. Use 'read_all' or 'save: key: value'."