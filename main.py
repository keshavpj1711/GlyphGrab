# sys for cmd args
import sys
import pyperclip  # For clipboard operations

# required components for building our app
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                           QVBoxLayout, QWidget, QGridLayout, QPushButton,
                           QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

# Import our custom modules
from emoji_data import EmojiData
from config import Config

class GlyphGrabMainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    
    # Initialize emoji data and config
    self.config = Config()
    self.emoji_data = EmojiData()
    
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
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet("""
      QScrollArea {
        border-radius: 20px;
        background-color: #f5f5f5;
        border: 1px solid #e0e0e0;
      }
    """)
    
    # Create widget to hold the grid inside the scroll area
    scroll_content = QWidget()
    all_layout = QVBoxLayout(scroll_content)
    all_layout.setContentsMargins(10, 10, 10, 10)
    
    # Grid for all emojis
    self.all_grid = QGridLayout()
    self.all_grid.setSpacing(5)
    
    # Load all emojis
    all_emojis = self.emoji_data.get_all_emojis()
    self.display_emojis(self.all_grid, all_emojis)
    
    all_layout.addLayout(self.all_grid)
    scroll_area.setWidget(scroll_content)
    main_layout.addWidget(scroll_area)
    
    # Set up the central widget
    container = QWidget()
    container.setLayout(main_layout)
    self.setCentralWidget(container)
    
    # Connect search bar to filter function
    self.search_bar.textChanged.connect(self.filter_emojis)
    
    # Set focus to search bar
    self.search_bar.setFocus()
  
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
      btn.setFont(QFont("Noto Color Emoji", 14))  # Set emoji font directly on button
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
      if col >= 8:  # 8 emojis per row
        col = 0
        row += 1
  
  def filter_emojis(self):
    search_text = self.search_bar.text()
    
    # Show/hide recent section based on search
    if not search_text:
      # If search is empty, show recent section and all emojis
      self.recent_section.show()
      all_emojis = self.emoji_data.get_all_emojis()
      self.display_emojis(self.all_grid, all_emojis)
      return
    else:
      self.recent_section.hide()
    
    # Search for emojis"
    results = self.emoji_data.search(search_text)
    
    # Display results
    self.display_emojis(self.all_grid, results)
    
  def copy_emoji(self, emoji):
    # Copy to clipboard
    pyperclip.copy(emoji)
    
    # Add to recent emojis
    self.config.add_recent_emoji(emoji)
    
    print(f"Copied emoji: {emoji}")
    
    # Close the window
    self.close()


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
