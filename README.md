# File Renamer

A simple utility to rename files in a folder by adding text before or after the filename.

## Features

- Add text before or after filenames
- Select target folder
- View files in the selected folder
- Undo renaming operations

## Requirements

- Python 3.6+
- PySide6
- auto-py-to-exe if you want to complie it to an exe. 

## Installation

1. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

1. Run the application:

```
python file_renamer.py
```

2. Enter the text you want to add to filenames in the text box
3. Check "Before filename" to add text at the beginning of filenames
4. Check "After filename" to add text at the end of filenames
5. Use "Select Folder" to choose the target directory (defaults to current directory)
6. Click "Start Renaming" to begin the renaming process
7. If needed, click "Undo" to revert the most recent renaming operation 
