"""Configuration management module"""

import os
import json
import shutil


class ConfigManager:
    """Centralized configuration management using Singleton pattern"""

    _instance = None
    _config_dir = '.config'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.config_dir = self._config_dir

        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)

        # Auto-setup config files from templates if needed
        self._auto_setup_config_files()

        # Load configuration files
        self.paths = self._load_json('paths.json')
        self.settings = self._load_json('settings.json')

        # Create necessary directories
        self._ensure_directories()

    def _auto_setup_config_files(self):
        """Auto-copy .example files to actual config files if they don't exist"""
        config_templates = {
            'paths.json': 'paths.json.example',
            'settings.json': 'settings.json.example'
        }

        setup_needed = False
        for config_file, template_file in config_templates.items():
            config_path = os.path.join(self.config_dir, config_file)
            template_path = os.path.join(self.config_dir, template_file)

            if not os.path.exists(config_path) and os.path.exists(template_path):
                try:
                    shutil.copy(template_path, config_path)
                    print(f"✓ Created {config_file} from template")
                    setup_needed = True
                except Exception as e:
                    print(f"Warning: Could not create {config_file}: {e}")

        if setup_needed:
            print("\n⚠ Configuration files created from templates.")
            print("  Please edit .config/credentials.json with your Google API credentials.")
            print("  See .config/README.md for instructions.\n")

    def _load_json(self, filename):
        """Load JSON configuration file"""
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            template_path = filepath + '.example'
            if os.path.exists(template_path):
                print(f"\n⚠ Configuration file {filepath} not found!")
                print(f"  Run: ./setup_config.sh")
                print(f"  Or manually copy: {template_path} → {filepath}\n")
            else:
                print(f"Warning: Configuration file {filepath} not found. Using defaults.")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse {filepath}: {e}")
            return {}

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        dirs_to_create = [
            self.get_path('data_directory'),
            self.get_path('logs_directory'),
            self.config_dir
        ]

        for dir_path in dirs_to_create:
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

    def get_path(self, key, default=None):
        """Get a path from paths.json"""
        return self.paths.get(key, default)

    def get_setting(self, *keys, default=None):
        """Get a setting from settings.json using dot notation
        Example: get_setting('google_calendar', 'timezone')
        """
        value = self.settings
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value if value is not None else default

    def update_setting(self, value, *keys):
        """Update a setting and save to file"""
        current = self.settings
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

        # Save to file
        filepath = os.path.join(self.config_dir, 'settings.json')
        with open(filepath, 'w') as f:
            json.dump(self.settings, f, indent=2)
