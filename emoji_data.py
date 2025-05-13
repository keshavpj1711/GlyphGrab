#  Copyright (c) 2025 Keshav Prajapati
#  Licensed under the MIT license. See LICENSE file in the project root for details.
import json
import os
from indexer import EmojiIndexer

class EmojiData:
  def __init__(self, json_path="data/emoji-en-US.json"):
    self.json_path = json_path
    self.emojis = {}
    self.emoji_keys = []
    self.indexer = None
    self.is_fully_loaded = False
    self.load_essential_data()
    
  def load_essential_data(self):
    """Load only essential emoji data at startup"""
    try:
      # Open the file but don't read all data yet
      with open(self.json_path, 'r', encoding='utf-8') as f:
        # Just get the keys (emoji characters)
        self.emojis = json.load(f)
        self.emoji_keys = list(self.emojis.keys())
      print(f"Loaded {len(self.emoji_keys)} emoji keys")
      
      # Initialize indexer but don't build index yet
      self.init_indexer()
      
    except Exception as e:
      print(f"Error loading emoji data: {e}")
      self.emojis = {}
      self.emoji_keys = []
      
  def init_indexer(self):
    """Initialize the emoji indexer"""
    self.indexer = EmojiIndexer(self.json_path)
    
    # Try to load existing index, don't build if not available
    index_path = "data/index/inverted_index.json"
    if os.path.exists(index_path):
      self.indexer.load_index(index_path)
    
  def ensure_index_loaded(self):
    """Ensure the search index is loaded when needed"""
    if not self.indexer.is_index_loaded():
      print("Building search index...")
      self.indexer.build_index()
      self.indexer.save_index()
    
  def search(self, query):
    """Search for emojis matching the query"""
    if not self.indexer:
      return []
    
    # Ensure index is loaded before searching
    self.ensure_index_loaded()
    return self.indexer.search(query)
    
  def get_all_emojis(self):
    """Return all emoji characters"""
    return self.emoji_keys
    
  def get_emoji_chunk(self, start=0, count=100):
    """Return a chunk of emojis for lazy loading"""
    end = min(start + count, len(self.emoji_keys))
    return self.emoji_keys[start:end]
    
  def get_emoji_keywords(self, emoji):
    """Get keywords for a specific emoji"""
    return self.emojis.get(emoji, [])
