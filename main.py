# sys for cmd args
import sys
import pyperclip # For clipboard operations

# required components for building our app
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                           QVBoxLayout, QWidget, QGridLayout, QPushButton,
                           QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QSize, QTimer, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# Import our custom modules
from emoji_data import EmojiData
from config import Config

# Worker class for threaded search
class SearchWorker(QObject):
  finished = pyqtSignal(list)
  
  def __init__(self, emoji_data):
    super().__init__()
    self.emoji_data = emoji_data
    self.query = ""
  
  def set_query(self, query):
    self.query = query
  
  def search(self):
    # Perform the search in a separate thread
    results = self.emoji_data.search(self.query)
    self.finished.emit(results)

# Worker for loading emoji chunks
class LoadEmojiWorker(QObject):
  finished = pyqtSignal(list, int)
  
  def __init__(self, emoji_data):
    super().__init__()
    self.emoji_data = emoji_data
    self.offset = 0
    self.chunk_size = 100
  
  def set_params(self, offset, chunk_size):
    self.offset = offset
    self.chunk_size = chunk_size
  
  def load(self):
    # Load emoji chunk in a separate thread
    emojis = self.emoji_data.get_emoji_chunk(self.offset, self.chunk_size)
    self.finished.emit(emojis, self.offset)

class GlyphGrabMainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    
    # Initialize emoji data and config
    self.config = Config()
    self.emoji_data = EmojiData()
    
    # For lazy loading
    self.emoji_chunk_size = 100
    self.current_emoji_offset = 0
    self.is_loading_more = False
    
    # For caching
    self.cached_emoji_grid = None
    self.cached_emoji_widget = None
    self.is_search_active = False
    
    # Set up the search thread
    self.search_thread = QThread()
    self.search_worker = SearchWorker(self.emoji_data)
    self.search_worker.moveToThread(self.search_thread)
    self.search_worker.finished.connect(self.update_search_results)
    self.search_thread.start()
    
    # Set up the emoji loading thread
    self.load_thread = QThread()
    self.load_worker = LoadEmojiWorker(self.emoji_data)
    self.load_worker.moveToThread(self.load_thread)
    self.load_worker.finished.connect(self.append_loaded_emojis)
    self.load_thread.start()
    
    # Set window properties
    self.setWindowTitle("GlyphGrab")
    self.setFixedSize(500, 500)
    
    # Main layout
    main_layout = QVBoxLayout()
    main_layout.setSpacing(10)
    main_layout.setContentsMargins(20, 20, 20, 20)
    
    # Search bar with rounded corners
    self.search_bar = QLineEdit()
    self.search_bar.setPlaceholderText("Search Here")
    self.search_bar.setMinimumHeight(40)
    self.search_bar.setStyleSheet("""
      QLineEdit {
        border-radius: 20px;
        padding: 0 15px;
        background-color: #f5f5f5;
        border: 1px solid #e0e0e0;
        font-size: 16px;
      }
    """)
    main_layout.addWidget(self.search_bar)
    
    # Recent Emojis section
    self.recent_section = QWidget()
    recent_layout = QVBoxLayout(self.recent_section)
    recent_layout.setContentsMargins(0, 0, 0, 0)
    
    recent_label = QLabel("Recent Emojis")
    recent_label.setFont(QFont("Arial", 12, QFont.Bold))
    recent_layout.addWidget(recent_label)
    
    # Frame for recent emojis with rounded corners
    recent_frame = QFrame()
    recent_frame.setFrameShape(QFrame.StyledPanel)
    recent_frame.setStyleSheet("""
      QFrame {
        border-radius: 20px;
        background-color: #f5f5f5;
        border: 1px solid #e0e0e0;
      }
    """)
    
    self.recent_container = QVBoxLayout(recent_frame)
    
    # Load recent emojis from config
    self.recent_emojis = self.config.get_recent_emojis()
    
    if not self.recent_emojis:
      # Show message when no recent emojis
      no_recent_label = QLabel("Use some emojis")
      no_recent_label.setAlignment(Qt.AlignCenter)
      no_recent_label.setStyleSheet("color: #888888; padding: 20px;")
      self.recent_container.addWidget(no_recent_label)
    else:
      # Grid for recent emojis
      self.recent_grid = QGridLayout()
      self.recent_grid.setSpacing(5)
      self.display_emojis(self.recent_grid, self.recent_emojis)
      self.recent_container.addLayout(self.recent_grid)
    
    recent_layout.addWidget(recent_frame)
    main_layout.addWidget(self.recent_section)
    
    # All Emojis section
    all_label = QLabel("All")
    all_label.setFont(QFont("Arial", 12, QFont.Bold))
    main_layout.addWidget(all_label)
    
    # Create scroll area for all emojis
    self.scroll_area = QScrollArea()
    self.scroll_area.setWidgetResizable(True)
    self.scroll_area.setStyleSheet("""
      QScrollArea {
        border-radius: 20px;
        background-color: #f5f5f5;
        border: 1px solid #e0e0e0;
      }
    """)
    
    # Connect scroll area to lazy loading
    self.scroll_area.verticalScrollBar().valueChanged.connect(self.check_scroll_position)
    
    # Create widget to hold the grid inside the scroll area
    self.scroll_content = QWidget()
    self.all_layout = QVBoxLayout(self.scroll_content)
    self.all_layout.setContentsMargins(10, 10, 10, 10)
    
    # Grid for all emojis
    self.all_grid = QGridLayout()
    self.all_grid.setSpacing(5)
    
    # Load initial emojis (just first chunk)
    self.load_initial_emojis()
    
    self.all_layout.addLayout(self.all_grid)
    self.scroll_area.setWidget(self.scroll_content)
    main_layout.addWidget(self.scroll_area)
    
    # Set up the central widget
    container = QWidget()
    container.setLayout(main_layout)
    self.setCentralWidget(container)
    
    # Set up debouncing for search
    self.search_timer = QTimer()
    self.search_timer.setSingleShot(True)
    self.search_timer.timeout.connect(self.perform_search)
    
    # Connect search bar to debounce function
    self.search_bar.textChanged.connect(self.debounce_search)
    
    # Set focus to search bar
    self.search_bar.setFocus()
  
  def load_initial_emojis(self):
    """Load just the first chunk of emojis"""
    initial_emojis = self.emoji_data.get_emoji_chunk(0, self.emoji_chunk_size)
    self.current_emoji_offset = len(initial_emojis)
    self.display_emojis(self.all_grid, initial_emojis)
  
  def check_scroll_position(self, value):
    """Check if we need to load more emojis when scrolling"""
    # Only check scroll position if we're not in search mode
    if self.is_search_active:
      return
      
    scrollbar = self.sender()
    if not self.is_loading_more and value > scrollbar.maximum() * 0.7:
      self.is_loading_more = True
      self.load_more_emojis()
  
  def load_more_emojis(self):
    """Load the next chunk of emojis in a separate thread"""
    self.load_worker.set_params(self.current_emoji_offset, self.emoji_chunk_size)
    self.load_worker.load()
  
  def append_loaded_emojis(self, emojis, offset):
    """Handle emojis loaded from worker thread"""
    if emojis:
      self.current_emoji_offset += len(emojis)
      self.append_emojis(self.all_grid, emojis)
      
      # Update cache if we're not in search mode
      if not self.is_search_active:
        self.cache_current_emoji_grid()
    
    self.is_loading_more = False
  
  def cache_current_emoji_grid(self):
    """Cache the current emoji grid to avoid rebuilding it"""
    # Create a new widget to hold the cached grid
    if self.cached_emoji_widget is None:
      self.cached_emoji_widget = QWidget()
      self.cached_emoji_grid = QGridLayout(self.cached_emoji_widget)
      self.cached_emoji_grid.setSpacing(5)
    
    # Copy all buttons from the current grid to the cache
    for i in range(self.all_grid.count()):
      item = self.all_grid.itemAt(i)
      if item and item.widget():
        btn = item.widget()
        row, col, _, _ = self.all_grid.getItemPosition(i)
        
        # Create a copy of the button
        new_btn = QPushButton(btn.text())
        new_btn.setFixedSize(QSize(40, 40))
        new_btn.setFont(QFont("Noto Color Emoji", 14))
        new_btn.setStyleSheet(btn.styleSheet())
        new_btn.clicked.connect(lambda _, e=btn.text(): self.copy_emoji(e))
        
        # Add to cached grid
        self.cached_emoji_grid.addWidget(new_btn, row, col)
  
  def restore_cached_emoji_grid(self):
    """Restore the emoji grid from cache"""
    if self.cached_emoji_widget:
      # Clear the current grid
      for i in reversed(range(self.all_grid.count())):
        widget = self.all_grid.itemAt(i).widget()
        if widget:
          widget.setParent(None)
      
      # Copy all buttons from cache to the current grid
      for i in range(self.cached_emoji_grid.count()):
        item = self.cached_emoji_grid.itemAt(i)
        if item and item.widget():
          btn = item.widget()
          row, col, _, _ = self.cached_emoji_grid.getItemPosition(i)
          
          # Create a copy of the button
          new_btn = QPushButton(btn.text())
          new_btn.setFixedSize(QSize(40, 40))
          new_btn.setFont(QFont("Noto Color Emoji", 14))
          new_btn.setStyleSheet(btn.styleSheet())
          new_btn.clicked.connect(lambda _, e=btn.text(): self.copy_emoji(e))
          
          # Add to current grid
          self.all_grid.addWidget(new_btn, row, col)
      
      return True
    return False
  
  def display_emojis(self, grid_layout, emoji_list):
    # Clear existing widgets in the grid
    for i in reversed(range(grid_layout.count())):
      widget = grid_layout.itemAt(i).widget()
      if widget:
        widget.deleteLater()
    
    # Add emojis to grid (8 per row)
    row, col = 0, 0
    for emoji in emoji_list:
      btn = QPushButton(emoji)
      btn.setFixedSize(QSize(40, 40))
      btn.setFont(QFont("Noto Color Emoji", 14)) # Set emoji font directly on button
      btn.setStyleSheet("""
        QPushButton {
          border: none;
          background-color: transparent;
          font-size: 24px;
        }
        QPushButton:hover {
          background-color: #e0e0e0;
          border-radius: 5px;
        }
      """)
      # Connect button click to copy emoji
      btn.clicked.connect(lambda _, e=emoji: self.copy_emoji(e))
      grid_layout.addWidget(btn, row, col)
      
      col += 1
      if col >= 8: # 8 emojis per row
        col = 0
        row += 1
  
  def append_emojis(self, grid_layout, emoji_list):
    """Append emojis to existing grid without clearing"""
    # Find the last position
    row_count = 0
    col_count = 0
    for i in range(grid_layout.count()):
      item = grid_layout.itemAt(i)
      if item and item.widget():
        row, col, _, _ = grid_layout.getItemPosition(i)
        row_count = max(row_count, row + 1)
        col_count = max(col_count, col + 1)
    
    # Start from the last row
    row = row_count - 1 if row_count > 0 else 0
    col = col_count if row_count > 0 else 0
    
    # If we finished a row, move to next row
    if col >= 8:
      row += 1
      col = 0
    
    # Add new emojis
    for emoji in emoji_list:
      btn = QPushButton(emoji)
      btn.setFixedSize(QSize(40, 40))
      btn.setFont(QFont("Noto Color Emoji", 14))
      btn.setStyleSheet("""
        QPushButton {
          border: none;
          background-color: transparent;
          font-size: 24px;
        }
        QPushButton:hover {
          background-color: #e0e0e0;
          border-radius: 5px;
        }
      """)
      btn.clicked.connect(lambda _, e=emoji: self.copy_emoji(e))
      grid_layout.addWidget(btn, row, col)
      
      col += 1
      if col >= 8:
        col = 0
        row += 1
  
  def debounce_search(self):
    # Reset the timer on each keystroke
    self.search_timer.stop()
    self.search_timer.start(200) # 200ms delay before searching
    
    # Immediately handle empty search box case for better responsiveness
    if not self.search_bar.text():
      self.recent_section.show()
  
  def perform_search(self):
    search_text = self.search_bar.text()
    
    # Show/hide recent section based on search
    if not search_text:
      # If search is empty, show recent section and restore cached grid
      self.recent_section.show()
      self.is_search_active = False
      
      # Try to restore from cache first
      if not self.restore_cached_emoji_grid():
        # If no cache, reset lazy loading and load first chunk
        self.current_emoji_offset = 0
        self.load_initial_emojis()
      return
    else:
      self.recent_section.hide()
      self.is_search_active = True
    
    # Set the query and perform search in the worker thread
    self.search_worker.set_query(search_text)
    QThread.msleep(10) # Small delay to ensure the UI updates
    self.search_worker.search()
  
  def update_search_results(self, results):
    # This function is called when the search is complete
    self.display_emojis(self.all_grid, results)
  
  def copy_emoji(self, emoji):
    # Copy to clipboard
    pyperclip.copy(emoji)
    
    # Add to recent emojis
    self.config.add_recent_emoji(emoji)
    
    print(f"Copied emoji: {emoji}")
    
    # Close the window
    self.close()
  
  def closeEvent(self, event):
    # Clean up the threads when the window is closed
    self.search_thread.quit()
    self.search_thread.wait()
    self.load_thread.quit()
    self.load_thread.wait()
    super().closeEvent(event)

def main():
  app = QApplication(sys.argv)
  
  # Set a font that supports color emojis
  emoji_font = QFont("Noto Color Emoji", 12)
  app.setFont(emoji_font)
  
  window = GlyphGrabMainWindow()
  window.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
