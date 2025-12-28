import hashlib
from src.tools.base import AgentTool
import datetime

class WeatherTool(AgentTool):
    name = "check_weather"
    description = """
    Useful for checking the weather forecast. 
    Input should be a date string (e.g., '2025-12-30') or 'today'/'tomorrow'.
    """

    def execute(self, date_str: str) -> str:
        # 1. Handle "today" / "tomorrow" relative dates
        today = datetime.date.today()
        target_date = today

        clean_input = date_str.lower().strip()
        
        if "tomorrow" in clean_input:
            target_date = today + datetime.timedelta(days=1)
        elif "today" in clean_input:
            target_date = today
        else:
            # Try to parse simple YYYY-MM-DD
            try:
                target_date = datetime.datetime.strptime(clean_input, "%Y-%m-%d").date()
            except ValueError:
                # Fallback: Just use the input string to generate hash
                pass

        # 2. Simulation Logic (Deterministic)
        # We use a hash of the date string so the "random" weather 
        # is consistent (e.g., Dec 30th is always Rainy).
        date_key = str(target_date)
        hash_val = int(hashlib.sha256(date_key.encode('utf-8')).hexdigest(), 16)
        
        conditions = [
            "Sunny ☀️ - Temperature: 25°C", 
            "Rainy 🌧️ - Temperature: 18°C", 
            "Cloudy ☁️ - Temperature: 20°C", 
            "Thunderstorms ⛈️ - Temperature: 16°C",
            "Windy 💨 - Temperature: 22°C"
        ]
        
        # Pick a condition based on the hash
        weather = conditions[hash_val % len(conditions)]
        
        return f"Forecast for {date_key}: {weather}"