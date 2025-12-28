import random
from src.tools.base import AgentTool

class WeatherTool(AgentTool):
    name = "check_weather"
    description = "Useful for checking the weather forecast for a specific date. Input should be the date (e.g., '2025-12-30')."

    def execute(self, date_str: str) -> str:
        # Mock Logic: Generate deterministic "random" weather based on the date string
        # This ensures the same date always returns the same weather for testing.
        hash_val = sum(ord(c) for c in date_str)
        conditions = ["Sunny ☀️", "Rainy 🌧️", "Cloudy ☁️", "Stormy ⛈️"]
        result = conditions[hash_val % len(conditions)]
        return f"The forecast for {date_str} is {result}."