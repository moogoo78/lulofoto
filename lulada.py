#!/usr/bin/env python3
"""
Lulada - Batch Thumbnail Generator
Create thumbnails for multiple images with flexible naming options
"""

import os
import sys
import argparse
import configparser
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Error: PIL/Pillow is required for thumbnail generation.")
    print("Install with: pip install Pillow")
    sys.exit(1)


IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
CONFIG_FILE = "lulada.ini"


def load_config(config_path=None):
    """Load configuration from INI file"""
    if config_path is None:
        # Look for config in script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, CONFIG_FILE)

    config = configparser.ConfigParser()

    # Set defaults
    defaults = {
        'thumbnail_width': '800',
        'thumbnail_height': '600',
        'prefix': '',
        'postfix': '_thumb',
        'ext_case': 'lower'
    }

    if os.path.exists(config_path):
        try:
            config.read(config_path)
            print(f"Loaded configuration from: {config_path}")
        except Exception as e:
            print(f"Warning: Could not read config file: {e}")
            print("Using default settings")
    else:
        print(f"Config file not found: {config_path}")
        print("Using default settings")

    # Ensure DEFAULT section exists with fallback values
    if not config.has_section('DEFAULT'):
        config['DEFAULT'] = defaults
    else:
        for key, value in defaults.items():
            if key not in config['DEFAULT']:
                config['DEFAULT'][key] = value

    return config


def get_size_abbr(config, width):
    """Get size abbreviation for given width"""
    if config.has_section('sizes'):
        sizes = config['sizes']
        width_str = str(width)
        if width_str in sizes:
            return sizes[width_str]

    # Default abbreviations if not in config
    if width <= 200:
        return 'xs'
    elif width <= 400:
        return 'sm'
    elif width <= 800:
        return 'md'
    elif width <= 1200:
        return 'lg'
    else:
        return 'xl'


def get_preset_size(config, preset_name):
    """Get size settings from preset"""
    section_name = f"preset_{preset_name}"

    if config.has_section(section_name):
        preset = config[section_name]
        width = preset.getint('width', 800)
        height = preset.getint('height', 600)
        abbr = preset.get('abbr', preset_name)
        return width, height, abbr

    return None, None, None


def is_image_file(filename):
    """Check if file is an image based on extension"""
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


def generate_output_filename(input_filename, prefix, postfix, size_abbr, keep_same, ext_case='lower'):
    """Generate output filename based on naming options"""
    if keep_same:
        return input_filename

    # Split filename and extension
    name, ext = os.path.splitext(input_filename)

    # Replace {size} placeholder in prefix/postfix
    prefix = prefix.replace('{size}', size_abbr)
    postfix = postfix.replace('{size}', size_abbr)

    # Apply extension case transformation
    if ext_case == 'upper':
        ext = ext.upper()
    elif ext_case == 'lower':
        ext = ext.lower()
    # else: preserve original case

    # Build new filename
    new_name = f"{prefix}{name}{postfix}{ext}"

    return new_name


def create_thumbnail(input_path, output_path, width, height, quality=85):
    """Create a thumbnail from input image"""
    try:
        with Image.open(input_path) as img:
            # Calculate aspect ratio
            img_width, img_height = img.size
            img_ratio = img_width / img_height
            target_ratio = width / height

            # Resize maintaining aspect ratio (fit within bounds)
            if img_ratio > target_ratio:
                # Image is wider - fit to width
                new_width = width
                new_height = int(width / img_ratio)
            else:
                # Image is taller - fit to height
                new_height = height
                new_width = int(height * img_ratio)

            # Resize image with high-quality resampling
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convert RGBA to RGB if saving as JPEG
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                if img_resized.mode in ('RGBA', 'LA', 'P'):
                    # Create a white background
                    background = Image.new('RGB', img_resized.size, (255, 255, 255))
                    if img_resized.mode == 'P':
                        img_resized = img_resized.convert('RGBA')
                    background.paste(img_resized, mask=img_resized.split()[-1] if img_resized.mode == 'RGBA' else None)
                    img_resized = background

            # Save thumbnail
            save_kwargs = {}
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True

            img_resized.save(output_path, **save_kwargs)
            return True

    except Exception as e:
        print(f"Error creating thumbnail for {input_path}: {e}")
        return False


def batch_thumbnails(source_dir, output_dir, width, height, prefix, postfix, size_abbr, keep_same, quality, ext_case='lower'):
    """Generate thumbnails for all images in source directory"""

    source_dir = os.path.abspath(source_dir)
    output_dir = os.path.abspath(output_dir)

    # Validate source directory
    if not os.path.exists(source_dir):
        print(f"Error: Source directory does not exist: {source_dir}")
        return False

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Statistics
    stats = {
        'total_found': 0,
        'processed': 0,
        'skipped': 0,
        'errors': 0
    }

    # Process all images in source directory
    print(f"\nProcessing images from: {source_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Thumbnail size: {width}x{height}")
    print("-" * 50)

    for filename in os.listdir(source_dir):
        if not is_image_file(filename):
            continue

        stats['total_found'] += 1
        input_path = os.path.join(source_dir, filename)

        # Generate output filename
        output_filename = generate_output_filename(filename, prefix, postfix, size_abbr, keep_same, ext_case)
        output_path = os.path.join(output_dir, output_filename)

        # Skip if output already exists
        if os.path.exists(output_path):
            print(f"Skipped (exists): {filename} -> {output_filename}")
            stats['skipped'] += 1
            continue

        # Create thumbnail
        if create_thumbnail(input_path, output_path, width, height, quality):
            print(f"Created: {filename} -> {output_filename}")
            stats['processed'] += 1
        else:
            stats['errors'] += 1

    # Print summary
    print("\n" + "="*50)
    print("Summary:")
    print(f"  Total images found: {stats['total_found']}")
    print(f"  Thumbnails created: {stats['processed']}")
    print(f"  Skipped (already exist): {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")
    print("="*50)

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Batch thumbnail generator with flexible naming options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default settings from lulada.ini
  %(prog)s /path/to/source /path/to/output

  # Use preset size from config
  %(prog)s /path/to/source /path/to/output --preset md

  # Custom size
  %(prog)s /path/to/source /path/to/output --width 1024 --height 768

  # Add prefix
  %(prog)s /path/to/source /path/to/output --prefix thumb_

  # Add postfix with size
  %(prog)s /path/to/source /path/to/output --postfix _{size}

  # Keep same filename
  %(prog)s /path/to/source /path/to/output --keep-name

  # Custom config file
  %(prog)s /path/to/source /path/to/output --config myconfig.ini
        """
    )

    parser.add_argument('source', help='Source directory containing images')
    parser.add_argument('output', help='Output directory for thumbnails')

    # Size options
    size_group = parser.add_mutually_exclusive_group()
    size_group.add_argument('--preset', '-p', type=str,
                           help='Use size preset from config (xs, sm, md, lg, xl)')
    size_group.add_argument('--width', '-w', type=int,
                           help='Custom thumbnail width')

    parser.add_argument('--height', '-H', type=int,
                       help='Custom thumbnail height (required with --width)')

    # Naming options
    naming_group = parser.add_mutually_exclusive_group()
    naming_group.add_argument('--prefix', type=str,
                             help='Prefix for output filenames (use {size} for size abbr)')
    naming_group.add_argument('--postfix', type=str,
                             help='Postfix for output filenames (use {size} for size abbr)')
    naming_group.add_argument('--keep-name', action='store_true',
                             help='Keep original filename (ignore prefix/postfix)')

    # Other options
    parser.add_argument('--quality', '-q', type=int, default=85,
                       help='JPEG quality (1-100, default: 85)')
    parser.add_argument('--ext-case', type=str, choices=['lower', 'upper', 'preserve'],
                       help='Extension case: lower, upper, or preserve (default: from config or lower)')
    parser.add_argument('--config', '-c', type=str,
                       help='Path to config file (default: lulada.ini in script dir)')

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Determine size
    width = None
    height = None
    size_abbr = 'thumb'

    if args.preset:
        # Use preset from config
        width, height, size_abbr = get_preset_size(config, args.preset)
        if width is None:
            print(f"Error: Preset '{args.preset}' not found in config")
            sys.exit(1)
        print(f"Using preset: {args.preset} ({width}x{height})")
    elif args.width:
        # Custom size
        width = args.width
        if not args.height:
            print("Error: --height is required when using --width")
            sys.exit(1)
        height = args.height
        size_abbr = get_size_abbr(config, width)
    else:
        # Use defaults from config
        width = config['DEFAULT'].getint('thumbnail_width', 800)
        height = config['DEFAULT'].getint('thumbnail_height', 600)
        size_abbr = get_size_abbr(config, width)

    # Determine naming
    prefix = ''
    postfix = ''
    keep_same = args.keep_name

    if args.prefix is not None:
        prefix = args.prefix
    elif args.postfix is not None:
        postfix = args.postfix
    elif not keep_same:
        # Use defaults from config
        prefix = config['DEFAULT'].get('prefix', '')
        postfix = config['DEFAULT'].get('postfix', '_thumb')

    # Validate quality
    if args.quality < 1 or args.quality > 100:
        print("Error: Quality must be between 1 and 100")
        sys.exit(1)

    # Determine extension case
    ext_case = args.ext_case if args.ext_case else config['DEFAULT'].get('ext_case', 'lower')

    # Run batch processing
    success = batch_thumbnails(
        args.source,
        args.output,
        width,
        height,
        prefix,
        postfix,
        size_abbr,
        keep_same,
        args.quality,
        ext_case
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
