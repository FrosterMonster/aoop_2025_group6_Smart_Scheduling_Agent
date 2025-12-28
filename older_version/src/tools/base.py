from abc import ABC, abstractmethod

class AgentTool(ABC):
    # These are placeholders that subclasses can override
    name: str = ""
    description: str = ""

    def __init__(self, name: str = None, description: str = None):
        # If arguments are passed, use them. 
        # Otherwise, keep the class-level default.
        if name:
            self.name = name
        if description:
            self.description = description

    @abstractmethod
    def execute(self, input_str: str) -> str:
        """
        Execute the tool with the given input string.
        """
        pass