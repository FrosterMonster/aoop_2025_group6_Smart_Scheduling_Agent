"""Pattern learning from user scheduling behavior"""

import datetime
from collections import defaultdict, Counter
from typing import List, Optional, Tuple
import numpy as np
from sklearn.cluster import KMeans

from ai_schedule_agent.models.event import Event
from ai_schedule_agent.models.enums import EventType


class PatternLearner:
    """Learn from user scheduling patterns using machine learning"""

    def __init__(self):
        self.event_history = []
        self.scheduling_patterns = defaultdict(list)
        self.time_preferences = defaultdict(Counter)

    def add_event(self, event: Event):
        """Add event to learning history"""
        self.event_history.append(event)

        # Learn time preferences
        hour = event.start_time.hour
        self.time_preferences[event.event_type][hour] += 1

        # Learn scheduling patterns
        day_of_week = event.start_time.weekday()
        self.scheduling_patterns[day_of_week].append({
            'type': event.event_type,
            'hour': hour,
            'duration': (event.end_time - event.start_time).seconds // 60
        })

    def get_optimal_time(self, event_type: EventType, date: datetime.date) -> Optional[int]:
        """Get optimal hour for event type based on learned patterns"""
        if event_type in self.time_preferences:
            preferences = self.time_preferences[event_type]
            if preferences:
                return max(preferences, key=preferences.get)
        return None

    def suggest_batch_events(self) -> List[Tuple[EventType, List[int]]]:
        """Suggest events that could be batched together using K-Means clustering"""
        suggestions = []

        for event_type in EventType:
            hours = [e.start_time.hour for e in self.event_history
                    if e.event_type == event_type]

            if len(hours) > 3:
                # Use clustering to find common time slots
                hours_array = np.array(hours).reshape(-1, 1)
                if len(set(hours)) > 1:
                    kmeans = KMeans(n_clusters=min(3, len(set(hours))), random_state=42)
                    kmeans.fit(hours_array)

                    clusters = defaultdict(list)
                    for hour, label in zip(hours, kmeans.labels_):
                        clusters[label].append(hour)

                    for cluster_hours in clusters.values():
                        if len(cluster_hours) > 2:
                            suggestions.append((event_type, cluster_hours))

        return suggestions
