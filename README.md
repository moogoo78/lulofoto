# Photo Organizer

A Python script to automatically organize photos by creation date with support for incremental copying and date-based filtering.

By Claude Code v2.0.22 Sonnet 4.5

## Features

- 📁 **Automatic Organization**: Organizes photos into date-based folders (YYMMDD format)
- 📅 **EXIF Data Support**: Extracts creation date from photo EXIF metadata when available
- 🔄 **Incremental Sync**: Tracks previously copied files to avoid duplicates
- 📆 **Date Filtering**: Copy only photos from a specific date onwards
- 🔍 **Smart Detection**: Supports multiple image formats (JPG, PNG, HEIC, RAW, etc.)
- 🚫 **Duplicate Handling**: Automatically renames files if duplicates exist

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository

2. (Optional) Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install Pillow
```

> **Note**: The script can run without Pillow, but it will fall back to using file modification time instead of EXIF data.

## Usage

### Basic Syntax

```bash
./bak-foto.py <source_directory> <destination_directory> [options]
```

### Examples

#### First Time Copy
Copy all photos from source to destination:
```bash
./bak-foto.py /path/to/photos /path/to/backup
```

#### Incremental Copy
Run again to copy only new or modified files:
```bash
./bak-foto.py /path/to/photos /path/to/backup
```

#### Copy from Specific Date
Copy only photos from January 18, 2025 onwards:
```bash
./bak-foto.py /path/to/photos /path/to/backup --start-date 250118
```

#### Force Copy All Files
Ignore previous sync state and copy everything:
```bash
./bak-foto.py /path/to/photos /path/to/backup --force-all
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--start-date YYMMDD` | `-s` | Only copy photos from this date onwards (e.g., 250118 for Jan 18, 2025) |
| `--force-all` | `-f` | Copy all files, ignoring last sync time |
| `--help` | `-h` | Show help message and exit |

## How It Works

1. **Date Extraction**: The script attempts to read the photo's creation date from:
   - EXIF metadata (DateTimeOriginal, DateTime, or DateTimeDigitized)
   - File modification time (fallback if EXIF is unavailable)

2. **Organization**: Photos are copied to folders named in YYMMDD format:
   ```
   destination/
   ├── 250115/
   │   ├── photo1.jpg
   │   └── photo2.jpg
   ├── 250116/
   │   └── photo3.jpg
   └── 250118/
       └── photo4.jpg
   ```

3. **State Tracking**: A hidden file `.photo_organizer_state.json` is created in the destination directory to track:
   - Last sync timestamp
   - Previously copied files
   - Photo dates for each file

4. **Incremental Sync**: On subsequent runs (without `--force-all` or `--start-date`), only new or modified files are copied.

## Supported File Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- HEIC/HEIF (.heic, .heif)
- RAW formats (.raw, .cr2, .nef, .arw, .dng)

## Output Example

```
Photo Organizer
Source: /home/user/Photos
Destination: /home/user/Backup
--------------------------------------------------
Starting from: 2025-01-18
Only copying photos from this date onwards...
Copied: IMG_001.jpg -> 250118/
Copied: IMG_002.jpg -> 250119/
Copied: IMG_003.jpg -> 250120/

==================================================
Summary:
  Total photos found: 150
  Copied: 45
  Skipped: 105
  Errors: 0
==================================================
```

## State File

The script creates a `.photo_organizer_state.json` file in the destination directory:

```json
{
  "last_sync": "2025-01-18T14:30:45.123456",
  "copied_files": {
    "folder1/photo.jpg": "2025-01-18T10:23:15",
    "folder2/image.png": "2025-01-19T15:42:30"
  }
}
```

You can delete this file to reset the sync state.

## Troubleshooting

### "PIL/Pillow not installed" Warning
Install Pillow to enable EXIF data extraction:
```bash
pip install Pillow
```

### Duplicate Filenames
If a file with the same name already exists in the destination folder, the script automatically appends a counter (e.g., `photo_1.jpg`, `photo_2.jpg`).

### Permission Errors
Ensure you have read permissions for the source directory and write permissions for the destination directory.

## License

This project is open source and available for personal and commercial use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
