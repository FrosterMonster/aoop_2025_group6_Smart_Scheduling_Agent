"""State Manager - Comprehensive state persistence for all app data"""

import os
import json
import pickle
from datetime import datetime
from typing import Dict, List, Any
from ai_schedule_agent.utils.logging import logger


class StateManager:
    """Manages persistence of all application state across sessions"""

    def __init__(self, state_dir='.state'):
        """Initialize state manager

        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = os.path.abspath(state_dir)
        os.makedirs(self.state_dir, exist_ok=True)

        # State file paths
        self.events_cache_file = os.path.join(self.state_dir, 'events_cache.json')
        self.app_state_file = os.path.join(self.state_dir, 'app_state.json')
        self.learned_patterns_file = os.path.join(self.state_dir, 'learned_patterns.pkl')
        self.conversation_history_file = os.path.join(self.state_dir, 'conversation_history.json')

        logger.info(f"State Manager initialized: {self.state_dir}")

    def save_events_cache(self, events: List[Dict[str, Any]]):
        """Save calendar events to cache

        Args:
            events: List of event dictionaries
        """
        try:
            # Convert datetime objects to strings
            serializable_events = []
            for event in events:
                event_copy = event.copy()
                for key in ['start', 'end', 'created', 'updated']:
                    if key in event_copy and isinstance(event_copy[key], dict):
                        if 'dateTime' in event_copy[key]:
                            # Already a string
                            pass
                serializable_events.append(event_copy)

            with open(self.events_cache_file, 'w') as f:
                json.dump({
                    'events': serializable_events,
                    'cached_at': datetime.now().isoformat(),
                    'count': len(serializable_events)
                }, f, indent=2, default=str)

            logger.info(f"✓ Saved {len(events)} events to cache")

        except Exception as e:
            logger.error(f"✗ Failed to save events cache: {e}")

    def load_events_cache(self) -> List[Dict[str, Any]]:
        """Load cached calendar events

        Returns:
            List of event dictionaries
        """
        try:
            if os.path.exists(self.events_cache_file):
                with open(self.events_cache_file, 'r') as f:
                    data = json.load(f)

                events = data.get('events', [])
                cached_at = data.get('cached_at', 'unknown')
                logger.info(f"✓ Loaded {len(events)} events from cache (cached at: {cached_at})")
                return events
            else:
                logger.info("No events cache found, starting fresh")
                return []

        except Exception as e:
            logger.error(f"✗ Failed to load events cache: {e}")
            return []

    def save_app_state(self, state: Dict[str, Any]):
        """Save general application state

        Args:
            state: Dictionary containing app state
                - last_view: Last viewed calendar view (day/week/month)
                - current_date: Last viewed date
                - selected_filters: Active event filters
                - window_geometry: Window size and position
                - last_opened: Timestamp of last app open
        """
        try:
            state['saved_at'] = datetime.now().isoformat()

            with open(self.app_state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)

            logger.info(f"✓ Saved app state")

        except Exception as e:
            logger.error(f"✗ Failed to save app state: {e}")

    def load_app_state(self) -> Dict[str, Any]:
        """Load application state

        Returns:
            Dictionary containing app state
        """
        try:
            if os.path.exists(self.app_state_file):
                with open(self.app_state_file, 'r') as f:
                    state = json.load(f)

                saved_at = state.get('saved_at', 'unknown')
                logger.info(f"✓ Loaded app state (saved at: {saved_at})")
                return state
            else:
                logger.info("No app state found, using defaults")
                return {}

        except Exception as e:
            logger.error(f"✗ Failed to load app state: {e}")
            return {}

    def save_learned_patterns(self, patterns: Dict[str, Any]):
        """Save learned user patterns (using pickle for complex objects)

        Args:
            patterns: Dictionary of learned patterns
        """
        try:
            with open(self.learned_patterns_file, 'wb') as f:
                pickle.dump({
                    'patterns': patterns,
                    'saved_at': datetime.now()
                }, f)

            logger.info(f"✓ Saved learned patterns")

        except Exception as e:
            logger.error(f"✗ Failed to save learned patterns: {e}")

    def load_learned_patterns(self) -> Dict[str, Any]:
        """Load learned user patterns

        Returns:
            Dictionary of learned patterns
        """
        try:
            if os.path.exists(self.learned_patterns_file):
                with open(self.learned_patterns_file, 'rb') as f:
                    data = pickle.load(f)

                patterns = data.get('patterns', {})
                saved_at = data.get('saved_at', 'unknown')
                logger.info(f"✓ Loaded learned patterns (saved at: {saved_at})")
                return patterns
            else:
                logger.info("No learned patterns found, starting fresh")
                return {}

        except Exception as e:
            logger.error(f"✗ Failed to load learned patterns: {e}")
            return {}

    def save_conversation_history(self, history: List[Dict[str, Any]]):
        """Save conversation history with NLP/LLM

        Args:
            history: List of conversation messages
        """
        try:
            # Keep only last 100 messages
            history = history[-100:] if len(history) > 100 else history

            with open(self.conversation_history_file, 'w') as f:
                json.dump({
                    'history': history,
                    'saved_at': datetime.now().isoformat(),
                    'count': len(history)
                }, f, indent=2, default=str)

            logger.info(f"✓ Saved {len(history)} conversation messages")

        except Exception as e:
            logger.error(f"✗ Failed to save conversation history: {e}")

    def load_conversation_history(self) -> List[Dict[str, Any]]:
        """Load conversation history

        Returns:
            List of conversation messages
        """
        try:
            if os.path.exists(self.conversation_history_file):
                with open(self.conversation_history_file, 'r') as f:
                    data = json.load(f)

                history = data.get('history', [])
                logger.info(f"✓ Loaded {len(history)} conversation messages")
                return history
            else:
                logger.info("No conversation history found, starting fresh")
                return []

        except Exception as e:
            logger.error(f"✗ Failed to load conversation history: {e}")
            return []

    def clear_all_state(self):
        """Clear all cached state (for reset/debugging)"""
        try:
            files_to_remove = [
                self.events_cache_file,
                self.app_state_file,
                self.learned_patterns_file,
                self.conversation_history_file
            ]

            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"✓ Removed {os.path.basename(file_path)}")

            logger.info("✓ All state cleared")

        except Exception as e:
            logger.error(f"✗ Failed to clear state: {e}")

    def get_state_info(self) -> Dict[str, Any]:
        """Get information about cached state

        Returns:
            Dictionary with state file info
        """
        info = {}

        files = {
            'events_cache': self.events_cache_file,
            'app_state': self.app_state_file,
            'learned_patterns': self.learned_patterns_file,
            'conversation_history': self.conversation_history_file
        }

        for name, path in files.items():
            if os.path.exists(path):
                stat = os.stat(path)
                info[name] = {
                    'exists': True,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                info[name] = {'exists': False}

        return info
