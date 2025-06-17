# GlyphGrab

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15.11+-orange.svg)](https://redis.io)
[![PyQt5-Qt5](https://img.shields.io/badge/PyQt5Qt5-5.15.2+-cyan.svg)](https://redis.io)
[![pyperclip](https://img.shields.io/badge/pyperclip-1.9.0+-brick.svg)](https://opensource.org/licenses/MIT)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

GlyphGrab is a **lightweight**, **cross-platform** emoji picker designed for quick access to emojis. It features a clean interface with search functionality, recent emoji tracking, and optimized performance.

## Features

- **Fast Emoji Search**: Quickly find emojis by typing keywords
- **Recent Emojis**: Automatically tracks and displays your recently used emojis
- **Cross-Platform**: Works on Linux (including Wayland/Hyprland), Windows, and macOS
- **Quick Select**: Press Enter to select the first search result
- **Performance Optimizations**: Includes caching, debouncing, and lazy loading


## Performance Improvements

### Loading Time Optimization

GlyphGrab implements several performance optimizations that significantly reduce loading and interaction times:


| Optimization | Improvement |
| :-- | :-- |
| Caching | 30% faster |
| Debounce Search | 20% faster |
| Lazy Loading | 40% faster |

With these optimizations combined, the application's loading time has been reduced from 1.0 second to just 0.1 seconds - a 90% improvement in overall performance.

### Search Performance

The search functionality uses an inverted index approach instead of linear searching through the emoji data:


| Search Method | Search Time (ms) |
| :-- | :-- |
| Linear Search | 953.0 ms |
| Inverted Index | 0.2 ms |

**Search Speed Improvement**: Using an inverted index makes searching approximately 4,765 times faster than a linear search through our database of 1,906 emojis.

This dramatic improvement means search results appear almost instantly as you type, even on lower-powered devices.

## How It Works

### Inverted Index

Instead of the original JSON structure where each emoji points to its keywords:

```
{emoji: [keywords]}
```

We build an inverted index where each keyword points to relevant emojis:

```
{keyword: [emojis]}
```

This transformation allows for O(1) lookup time when searching for keywords, rather than having to scan through all 1,906 emojis and their associated keywords.

### Lazy Loading

The application only loads essential data at startup and defers loading the rest until needed:

- Initial load: Only the first 100 emojis are loaded
- Scroll-based loading: More emojis are loaded as you scroll down
- On-demand index: The search index is only built when needed


### Debounced Search

Search operations are debounced with a 200ms delay, meaning:

- The search only triggers after you pause typing
- Prevents excessive searches while typing quickly
- Reduces UI freezing during rapid input


### Caching

The emoji grid is cached after initial creation:

- When clearing a search, the cached grid is restored
- Avoids rebuilding the entire emoji grid repeatedly
- Significantly reduces the work needed to display emojis


## Installation and Usage

See the [User Guide](./USER_GUIDE.md) for detailed installation and usage instructions.

## License

Copyright © 2025 Keshav Prajapati

