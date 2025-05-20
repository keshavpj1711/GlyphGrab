#  Copyright (c) 2025 Keshav Prajapati
#  Licensed under the MIT license. See LICENSE file in the project root for details.
import json
import os
from collections import defaultdict
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
emoji_json_path = os.path.join(BASE_DIR, "data", "emoji-en-US.json")
index_dir_path = os.path.join(BASE_DIR, "data", "index")
index_json_path = os.path.join(BASE_DIR, "data", "index", "inverted_index.json")

class EmojiIndexer:
  def __init__(self, emoji_json_path=emoji_json_path):
    self.emoji_json_path = emoji_json_path
    self.emoji_data = {}
    self.inverted_index = defaultdict(list)
    self.load_emoji_data()
    
    if os.path.exists(index_json_path):
      print("Using the existing index")
      self.load_index()
    else:      
      self.build_index()
      
  def ensure_index_exists(self):
    """Ensure the index exists, build and save if it doesn't"""
    if not os.path.exists(index_json_path):
        self.build_index()
        self.save_index()

  def is_index_loaded(self):
    """Check if the index is loaded"""
    return len(self.inverted_index) > 0

    
  def load_emoji_data(self):
    """Load emoji data from JSON file"""
    try:
      with open(self.emoji_json_path, 'r', encoding='utf-8') as f:
        self.emoji_data = json.load(f)
      print(f"Loaded {len(self.emoji_data)} emojis from {self.emoji_json_path}")
    except Exception as e:
      print(f"Error loading emoji data: {e}")
      self.emoji_data = {}
    
  def build_index(self):
    """Build inverted index from emoji data"""
    for emoji_char, keywords in self.emoji_data.items():
      # Add each keyword to the inverted index
      for keyword in keywords:
        self.inverted_index[keyword].append(emoji_char)
        
        # Also add parts of compound keywords (e.g., "grinning_face" -> "grinning", "face")
        if "_" in keyword:
          parts = keyword.split("_")
          for part in parts:
            if len(part) > 1:  # Skip single-character parts
              self.inverted_index[part].append(emoji_char)
    
    # Convert defaultdict to regular dict
    self.inverted_index = dict(self.inverted_index)
    print(f"Built inverted index with {len(self.inverted_index)} keywords")
    
  def save_index(self, index_dir=index_dir_path):
    """Save the inverted index to a file"""
    os.makedirs(index_dir, exist_ok=True)
    index_path = os.path.join(index_dir, "inverted_index.json")
    
    try:
      with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(self.inverted_index, f, ensure_ascii=False)
      print(f"Saved inverted index to {index_path}")
    except Exception as e:
      print(f"Error saving inverted index: {e}")
    
  def load_index(self, index_path="data/index/inverted_index.json"):
    """Load the inverted index from a file"""
    try:
      with open(index_path, 'r', encoding='utf-8') as f:
        self.inverted_index = json.load(f)
      print(f"Loaded inverted index with {len(self.inverted_index)} keywords")
      return True
    except Exception as e:
      print(f"Error loading inverted index: {e}")
      return False
    
  def search(self, query):
    """Search for emojis matching the query"""
    if not query:
      return []
      
    query = query.lower()
    
    # Split the query into words
    words = re.findall(r'\w+', query)
    
    # Start with empty result set
    results = set()
    
    for word in words:
      # Look for exact matches
      if word in self.inverted_index:
        if not results:
          # For first word, initialize results
          results = set(self.inverted_index[word])
        else:
          # For subsequent words, find intersection (AND search)
          results &= set(self.inverted_index[word])
    
    # If no exact matches found or results is empty, try partial matches
    if not results:
      for word in words:
        for indexed_word in self.inverted_index:
          if word in indexed_word:
            # For partial matches, use union (OR search)
            results.update(self.inverted_index[indexed_word])
    
    return list(results)

# Example usage
if __name__ == "__main__":
  indexer = EmojiIndexer()
  # indexer.save_index()
  
  # Example search
  query = input("Enter the keyword to search for emoji: ")
  results = indexer.search(query)
  print(f"Search for '{query}' found {len(results)} emojis:")
  print(results[:24])  # Print first 10 results
