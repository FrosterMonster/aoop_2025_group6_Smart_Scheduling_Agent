"""User profile data model"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple


@dataclass
class UserProfile:
    """User preferences and patterns"""
    working_hours: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # day: (start, end)
    locations: List[str] = field(default_factory=list)
    energy_patterns: Dict[int, float] = field(default_factory=dict)  # hour: energy_level (0-1)
    preferred_meeting_length: int = 60  # minutes
    focus_time_length: int = 120  # minutes
    email: str = ""
    behavioral_rules: List[str] = field(default_factory=list)
    learned_patterns: Dict = field(default_factory=dict)

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        # Convert energy_patterns keys from strings to integers
        # (JSON serialization converts int keys to strings)
        if 'energy_patterns' in data:
            data['energy_patterns'] = {
                int(k): v for k, v in data['energy_patterns'].items()
            }
        return cls(**data)
