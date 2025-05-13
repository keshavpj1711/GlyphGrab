Yet to be updated with advanced user guide 

# Installation guide 

## Prerequisites

- Python 3.8 or higher
- Internet Connection for download required packages

## Basic Installation 

### Step 1: Clone this repository

Download this github repo by cloning it or downloading the zip file.
```bash
git clone https://github.com/keshavpj1711/GlyphGrab.git
```

### Step 2: Install required packages 

```bash
cd GlyphGrab
pip install -r requirements.txt
```

### Step 3: Install Required Fonts

- **For Linux:** you might have to install proper fonts to displaying emojis in the app
  ```bash
  sudo pacman -S noto-fonts-emoji  # Arch Based Linux
  # OR
  sudo apt install fonts-noto-color-emoji  # Ubuntu/Debian
  # OR
  sudo dnf install google-noto-emoji-color-fonts  # Fedora
  ```
- **For Windows and macOS**: The required emoji fonts are already included in your operating system.

### Step 4: Run the Application 

```bash
python main.py
```





