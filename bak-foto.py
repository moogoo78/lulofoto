#!/usr/bin/env python3
"""
Photo Organizer - Automatically organize photos by creation date
Supports incremental copying by tracking last sync time
"""

import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path
import argparse

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL/Pillow not installed. Will use file modification time instead of EXIF data.")
    print("Install with: pip install Pillow")


STATE_FILE = ".photo_organizer_state.json"
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw', '.dng'}


def get_photo_date(file_path):
    """Extract photo creation date from EXIF or file metadata"""

    # Try EXIF first if PIL is available
    if HAS_PIL:
        try:
            image = Image.open(file_path)
            exif_data = image._getexif()

            if exif_data:
                # Look for DateTime tags
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']:
                        try:
                            # EXIF date format: "2025:01:18 14:30:45"
                            return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                        except:
                            pass
        except Exception as e:
            pass

    # Fallback to file modification time
    timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp)


def load_state(dest_dir):
    """Load last sync state"""
    state_path = os.path.join(dest_dir, STATE_FILE)

    if os.path.exists(state_path):
        try:
            with open(state_path, 'r') as f:
                state = json.load(f)
                if 'last_sync' in state:
                    state['last_sync'] = datetime.fromisoformat(state['last_sync'])
                return state
        except Exception as e:
            print(f"Warning: Could not load state file: {e}")

    return {'last_sync': None, 'copied_files': {}}


def save_state(dest_dir, state):
    """Save sync state"""
    state_path = os.path.join(dest_dir, STATE_FILE)

    # Convert datetime to ISO format for JSON
    state_copy = state.copy()
    if state_copy['last_sync']:
        state_copy['last_sync'] = state_copy['last_sync'].isoformat()

    try:
        with open(state_path, 'w') as f:
            json.dump(state_copy, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save state file: {e}")


def is_image_file(filename):
    """Check if file is an image based on extension"""
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


def organize_photos(source_dir, dest_dir, force_all=False):
    """
    Copy and organize photos from source to destination by date

    Args:
        source_dir: Source directory containing photos
        dest_dir: Destination directory for organized photos
        force_all: If True, copy all files ignoring last sync time
    """

    source_dir = os.path.abspath(source_dir)
    dest_dir = os.path.abspath(dest_dir)

    # Validate directories
    if not os.path.exists(source_dir):
        print(f"Error: Source directory does not exist: {source_dir}")
        return False

    # Create destination if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Load state
    state = load_state(dest_dir)
    last_sync = state['last_sync']
    copied_files = state['copied_files']

    if last_sync and not force_all:
        print(f"Last sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Only copying new/modified files...")
    else:
        print("Copying all files...")

    # Statistics
    stats = {
        'total_found': 0,
        'copied': 0,
        'skipped': 0,
        'errors': 0
    }

    # Walk through source directory
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if not is_image_file(filename):
                continue

            stats['total_found'] += 1
            source_path = os.path.join(root, filename)

            try:
                # Get file modification time for incremental check
                file_mtime = datetime.fromtimestamp(os.path.getmtime(source_path))

                # Check if file needs to be copied
                file_key = os.path.relpath(source_path, source_dir)

                if not force_all and last_sync and file_mtime <= last_sync:
                    # File hasn't changed since last sync
                    if file_key in copied_files:
                        stats['skipped'] += 1
                        continue

                # Get photo date
                photo_date = get_photo_date(source_path)

                # Create date-based folder (format: YYMMDD)
                date_folder = photo_date.strftime("%y%m%d")
                dest_folder = os.path.join(dest_dir, date_folder)
                os.makedirs(dest_folder, exist_ok=True)

                # Destination path
                dest_path = os.path.join(dest_folder, filename)

                # Handle duplicate filenames
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(dest_folder, new_filename)
                        counter += 1

                # Copy file
                shutil.copy2(source_path, dest_path)
                copied_files[file_key] = photo_date.isoformat()
                stats['copied'] += 1

                print(f"Copied: {filename} -> {date_folder}/")

            except Exception as e:
                stats['errors'] += 1
                print(f"Error processing {filename}: {e}")

    # Update and save state
    state['last_sync'] = datetime.now()
    state['copied_files'] = copied_files
    save_state(dest_dir, state)

    # Print summary
    print("\n" + "="*50)
    print("Summary:")
    print(f"  Total photos found: {stats['total_found']}")
    print(f"  Copied: {stats['copied']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")
    print("="*50)

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Organize photos by creation date with incremental copy support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First time copy
  %(prog)s /path/to/source /path/to/destination

  # Subsequent copies (only new files)
  %(prog)s /path/to/source /path/to/destination

  # Force copy all files
  %(prog)s /path/to/source /path/to/destination --force-all
        """
    )

    parser.add_argument('source', help='Source directory containing photos')
    parser.add_argument('destination', help='Destination directory for organized photos')
    parser.add_argument('--force-all', '-f', action='store_true',
                       help='Copy all files, ignoring last sync time')

    args = parser.parse_args()

    print("Photo Organizer")
    print(f"Source: {args.source}")
    print(f"Destination: {args.destination}")
    print("-" * 50)

    success = organize_photos(args.source, args.destination, args.force_all)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
