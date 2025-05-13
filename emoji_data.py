import json
import os
from indexer import EmojiIndexer

class EmojiData:
  def __init__(self, json_path="data/emoji-en-US.json"):
    self.json_path = json_path
    self.emoji_dict = {}
    self.load_emoji_data()
    # Create indexer but don't rebuild the index (it handles loading existing index)
    self.indexer = EmojiIndexer(self.json_path)
    
  def load_emoji_data(self):
    """Load emoji data from JSON file"""
    try:
      with open(self.json_path, 'r', encoding='utf-8') as f:
        self.emoji_dict = json.load(f)
      print(f"Loaded {len(self.emoji_dict)} emojis from {self.json_path}")
    except Exception as e:
      print(f"Error loading emoji data: {e}")
      self.emoji_dict = {}
  
  def get_all_emojis(self):
    """Return all emoji characters"""
    return list(self.emoji_dict.keys())
  
  def get_emoji_keywords(self, emoji):
    """Get keywords for a specific emoji"""
    return self.emoji_dict.get(emoji, [])
  
  def search(self, query):
    """Search for emojis matching the query using the indexer"""
    return self.indexer.search(query)
  
  def get_emoji_categories(self):
    """Group emojis by category (first keyword is usually the category)"""
    categories = {}
    for emoji, keywords in self.emoji_dict.items():
      if keywords:
        category = keywords[0].split('_')[0]  # Use first part of first keyword as category
        if category not in categories:
          categories[category] = []
        categories[category].append(emoji)
    return categories
  
  def get_emoji_chunk(self, start=0, count=100):
    """Return a chunk of emojis for lazy loading"""
    all_emojis = self.get_all_emojis()
    end = min(start + count, len(all_emojis))
    return all_emojis[start:end]

# Example usage
if __name__ == "__main__":
  emoji_data = EmojiData()
  
  # Example: get all emojis
  all_emojis = emoji_data.get_all_emojis()
  print(f"Total emojis: {len(all_emojis)}")
  
  # Example: search
  query = input("Enter search term: ")
  results = emoji_data.search(query)
  print(f"Found {len(results)} results for '{query}':")
  print(results[:10])
  
  # Example: get emoji keywords
  if results:
    first_emoji = results[0]
    keywords = emoji_data.get_emoji_keywords(first_emoji)
    print(f"Keywords for {first_emoji}: {keywords}")
