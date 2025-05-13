#  Copyright (c) 2025 Keshav Prajapati
#  Licensed under the MIT license. See LICENSE file in the project root for details.
import os
import json
from pathlib import Path

class Config:
  def __init__(self):
    # Application paths
    self.app_name = "GlyphGrab"
    self.app_version = "0.1.0"
    
    # Get user config directory
    self.config_dir = Path.home() / ".config" / "glyphgrab"
    self.data_dir = self.config_dir / "data"
    self.recent_emojis_file = self.data_dir / "recent.json"
    
    # Create directories if they don't exist
    self.config_dir.mkdir(parents=True, exist_ok=True)
    self.data_dir.mkdir(parents=True, exist_ok=True)
    
    # Default settings
    self.default_config = {
      "max_recent_emojis": 24,
      "emoji_size": 40,
      "window_width": 500,
      "window_height": 500,
      "theme": "system",  # system, light, dark
    }
    
    # Load or create config file
    self.config_file = self.config_dir / "config.json"
    self.settings = self.load_config()
    
  def load_config(self):
    """Load config from file or create default"""
    if self.config_file.exists():
      try:
        with open(self.config_file, 'r') as f:
          return json.load(f)
      except Exception as e:
        print(f"Error loading config: {e}")
        return self.default_config
    else:
      self.save_config(self.default_config)
      return self.default_config
      
  def save_config(self, config):
    """Save config to file"""
    try:
      with open(self.config_file, 'w') as f:
        json.dump(config, f, indent=2)
    except Exception as e:
      print(f"Error saving config: {e}")
  
  def get_recent_emojis(self):
    """Load recent emojis from file"""
    if self.recent_emojis_file.exists():
      try:
        with open(self.recent_emojis_file, 'r', encoding='utf-8') as f:
          return json.load(f)
      except Exception as e:
        print(f"Error loading recent emojis: {e}")
        return []
    return []
    
  def add_recent_emoji(self, emoji):
    """Add emoji to recent list"""
    recent_emojis = self.get_recent_emojis()
    
    # Remove if already exists
    if emoji in recent_emojis:
      recent_emojis.remove(emoji)
      
    # Add to beginning
    recent_emojis.insert(0, emoji)
    
    # Limit to max_recent_emojis
    max_recent = self.settings.get("max_recent_emojis", 24)
    recent_emojis = recent_emojis[:max_recent]
    
    # Save to file
    try:
      with open(self.recent_emojis_file, 'w', encoding='utf-8') as f:
        json.dump(recent_emojis, f, ensure_ascii=False)
    except Exception as e:
      print(f"Error saving recent emojis: {e}")
