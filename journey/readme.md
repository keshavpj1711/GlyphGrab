# Walkthough 

This is where I will document my process of building GlyphGrab

## Setting Up 

### Packages installed

- PyQt5>=5.15.11 
  - Python binding for Qt5, used to create GUI. Provides with all the widgets, layouts, and event handling functionality
- PyQt5-Qt5>=5.15.16
  - Subset of Qt5 lib needed by PyQt5, it's essential for PyQt5 to function properly.
- pyperclip>=1.9.0
  - cross-platform module which handles clipboard operations

### Directory Structure

```bash
../GlyphGrab/
├── assets/                     # For icons, images
├── config.py                   # For config and settings
├── data                        
│   ├── emoji-en-US.json        # json file used for emojis
│   └── index/                  # For storing the inverted index generated
├── emoji_data.py               # Emoji data handling and search
├── indexer.py                  # For building the inverted index
├── __init__.py                 # Making the directory a package
├── journey
│   └── readme.md
├── LICENSE
├── main.py                     # Entry point and ui initialization
├── README.md
├── requirements.txt
```

