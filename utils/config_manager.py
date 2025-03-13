"""
Configuration Manager for the CMYK Retro Solana Vanity Generator
Handles saving and loading application settings
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

class ConfigManager:
    """
    Configuration manager that handles saving/loading application settings
    using a local JSON file
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager
        
        Args:
            config_file: Name of the configuration file to use
        """
        # Determine config directory - use user's home directory
        home_dir = Path.home()
        self.config_dir = home_dir / ".cmyk_vanity_generator"
        self.config_path = self.config_dir / config_file
        
        # Default configuration values
        self.default_config = {
            "prefix": "",
            "suffix": "",
            "count": "1",
            "output_dir": "./keys",
            "iteration_bits": 24,
            "select_device": False,
            "theme": "cyan",
            "sound_enabled": True,
            "first_run": True
        }
        
        # Current configuration
        self.config = self.default_config.copy()
        
        # Load configuration if it exists
        self.load_config()
    
    def ensure_config_dir(self):
        """Ensure the configuration directory exists"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create config directory: {e}")
    
    def load_config(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                
                # Update config with loaded values
                for key, value in loaded_config.items():
                    self.config[key] = value
                
                return True
            else:
                # Config doesn't exist, save default
                self.save_config()
                return False
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            # Try to save default config
            self.save_config()
            return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to file
        
        Returns:
            bool: True if saving was successful, False otherwise
        """
        try:
            self.ensure_config_dir()
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save to file
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save_config()
    
    def reset(self, key: Optional[str] = None) -> None:
        """
        Reset configuration to default values
        
        Args:
            key: Specific key to reset, or None to reset all
        """
        if key is None:
            # Reset all config values
            self.config = self.default_config.copy()
        else:
            # Reset specific key if it exists in defaults
            if key in self.default_config:
                self.config[key] = self.default_config[key]
        
        self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values
        
        Returns:
            Dict: All configuration key-value pairs
        """
        return self.config.copy()
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first time the application is run
        
        Returns:
            bool: True if first run, False otherwise
        """
        return self.get('first_run', True)
    
    def mark_as_run(self) -> None:
        """Mark the application as having been run before"""
        self.set('first_run', False)
    
    def export_config(self, path: str) -> bool:
        """
        Export configuration to a specified file
        
        Args:
            path: File path to export to
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error exporting config: {e}")
            return False
    
    def import_config(self, path: str) -> bool:
        """
        Import configuration from a specified file
        
        Args:
            path: File path to import from
            
        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            with open(path, 'r') as f:
                imported_config = json.load(f)
            
            # Validate imported config
            if not isinstance(imported_config, dict):
                logging.error("Imported config is not a valid dictionary")
                return False
            
            # Update config with imported values
            for key, value in imported_config.items():
                self.config[key] = value
            
            # Save the imported config
            self.save_config()
            return True
        except Exception as e:
            logging.error(f"Error importing config: {e}")
            return False
    
    def get_theme(self) -> str:
        """
        Get the current UI theme
        
        Returns:
            str: Theme name ('cyan', 'magenta', 'yellow', or 'white')
        """
        return self.get('theme', 'cyan')
    
    def set_theme(self, theme: str) -> None:
        """
        Set the UI theme
        
        Args:
            theme: Theme name ('cyan', 'magenta', 'yellow', or 'white')
        """
        if theme in ('cyan', 'magenta', 'yellow', 'white', 'cmyk'):
            self.set('theme', theme)
    
    def toggle_sound(self) -> bool:
        """
        Toggle sound on/off
        
        Returns:
            bool: New sound state (True = enabled, False = disabled)
        """
        current_state = self.get('sound_enabled', True)
        new_state = not current_state
        self.set('sound_enabled', new_state)
        return new_state
    
    def get_output_dir(self) -> str:
        """
        Get the configured output directory
        
        Returns:
            str: Output directory path
        """
        output_dir = self.get('output_dir', './keys')
        
        # Expand user path if it starts with ~
        if output_dir.startswith('~'):
            output_dir = os.path.expanduser(output_dir)
        
        return output_dir
    
    def set_output_dir(self, directory: str) -> None:
        """
        Set the output directory
        
        Args:
            directory: Directory path
        """
        self.set('output_dir', directory)
    
    def __str__(self) -> str:
        """
        String representation of the config
        
        Returns:
            str: JSON string of the config
        """
        return json.dumps(self.config, indent=2)


# Example usage
if __name__ == "__main__":
    # Initialize config manager
    config = ConfigManager()
    
    # Print current config
    print("Current configuration:")
    print(config)
    
    # Set a value
    config.set('prefix', 'test')
    print(f"Prefix is now: {config.get('prefix')}")
    
    # Toggle sound
    sound_state = config.toggle_sound()
    print(f"Sound is now: {'enabled' if sound_state else 'disabled'}")
    
    # Reset a specific value
    config.reset('prefix')
    print(f"Prefix after reset: {config.get('prefix')}")
    
    # Check if first run
    first_run = config.is_first_run()
    print(f"Is first run: {first_run}")
    
    # Mark as run
    config.mark_as_run()
    print(f"Is first run after marking: {config.is_first_run()}")