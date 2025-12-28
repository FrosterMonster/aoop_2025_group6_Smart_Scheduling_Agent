from abc import ABC, abstractmethod

class AgentTool(ABC):
    """
    Abstract Base Class for all external tools.
    Demonstrates Inheritance and Polymorphism.
    """
    def __init__(self, name: str, description: str):
        self._name = name  # Encapsulation: protected attribute
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @abstractmethod
    def execute(self, **kwargs):
        """
        Abstract method that all tools must implement.
        """
        pass

    def __str__(self):
        # Magic method for clear printing [cite: 56]
        return f"Tool: {self._name} | {self._description}"

    def __repr__(self):
        # Magic method for debugging [cite: 57]
        return f"<AgentTool(name='{self._name}')>"