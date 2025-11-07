# Lulada - Batch Thumbnail Generator

A flexible command-line tool for generating thumbnails from images in batch, with configurable sizing and naming options.

(Created by Claude Code)

## Features

- **Batch Processing**: Process all images in a directory at once
- **Flexible Sizing**: Use presets or custom dimensions
- **Smart Naming**: Add prefix, postfix, or keep original names
- **Quality Control**: Adjustable JPEG quality
- **Aspect Ratio Preservation**: Maintains original image proportions
- **High-Quality Resampling**: Uses Lanczos algorithm for best results
- **Skip Existing**: Automatically skips already-generated thumbnails
- **Configuration File**: Save default settings in `lulada.ini`

## Requirements

- Python 3.6+
- Pillow (PIL)

```bash
pip install Pillow
```

## Installation

1. Make the script executable:
```bash
chmod +x lulada.py
```

2. Optionally, copy to a directory in your PATH:
```bash
sudo cp lulada.py /usr/local/bin/lulada
```

## Configuration

The script uses `lulada.ini` for default settings. The config file should be in the same directory as the script.

### Configuration Options

```ini
[DEFAULT]
# Default thumbnail size
thumbnail_width = 800
thumbnail_height = 600

# Naming options
prefix =
postfix = _thumb

# Size abbreviations
[sizes]
200 = xs
400 = sm
800 = md
1200 = lg
1920 = xl

# Size presets
[preset_md]
width = 800
height = 600
abbr = md
```

### Size Presets

The default config includes these presets:
- **xs**: 200x150
- **sm**: 400x300
- **md**: 800x600 (default)
- **lg**: 1200x900
- **xl**: 1920x1440

## Usage

### Basic Usage

```bash
# Use default settings from lulada.ini
./lulada.py /path/to/source /path/to/output
```

### Using Presets

```bash
# Small thumbnails (400x300)
./lulada.py /path/to/source /path/to/output --preset sm

# Medium thumbnails (800x600)
./lulada.py /path/to/source /path/to/output --preset md

# Large thumbnails (1200x900)
./lulada.py /path/to/source /path/to/output --preset lg
```

### Custom Sizes

```bash
# Custom dimensions
./lulada.py /path/to/source /path/to/output --width 1024 --height 768
```

### Naming Options

```bash
# Add prefix: thumb_photo.jpg
./lulada.py /path/to/source /path/to/output --prefix thumb_

# Add postfix: photo_thumb.jpg
./lulada.py /path/to/source /path/to/output --postfix _thumb

# Add postfix with size: photo_md.jpg
./lulada.py /path/to/source /path/to/output --postfix _{size}

# Keep original filename (different folder)
./lulada.py /path/to/source /path/to/output --keep-name
```

### Quality Control

```bash
# High quality (larger file size)
./lulada.py /path/to/source /path/to/output --quality 95

# Lower quality (smaller file size)
./lulada.py /path/to/source /path/to/output --quality 70
```

### Custom Config File

```bash
# Use a different config file
./lulada.py /path/to/source /path/to/output --config myconfig.ini
```

## Command-Line Options

```
positional arguments:
  source                Source directory containing images
  output                Output directory for thumbnails

size options:
  --preset, -p PRESET   Use size preset (xs, sm, md, lg, xl)
  --width, -w WIDTH     Custom thumbnail width
  --height, -H HEIGHT   Custom thumbnail height (required with --width)

naming options:
  --prefix PREFIX       Prefix for output filenames (use {size} for size abbr)
  --postfix POSTFIX     Postfix for output filenames (use {size} for size abbr)
  --keep-name           Keep original filename (ignore prefix/postfix)

other options:
  --quality, -q QUALITY JPEG quality (1-100, default: 85)
  --config, -c CONFIG   Path to config file
  --help, -h            Show help message
```

## Examples

### Example 1: Quick thumbnails with default settings

```bash
./lulada.py ~/Photos/vacation ~/Photos/vacation_thumbs
```

Output:
```
photo1.jpg → photo1_thumb.jpg
photo2.jpg → photo2_thumb.jpg
```

### Example 2: Social media thumbnails

```bash
./lulada.py ~/Photos ~/Photos/social --preset sm --postfix _{size}
```

Output:
```
photo1.jpg → photo1_sm.jpg (400x300)
photo2.jpg → photo2_sm.jpg (400x300)
```

### Example 3: Web gallery

```bash
./lulada.py ~/originals ~/web_gallery --width 1200 --height 900 --prefix web_ --quality 90
```

Output:
```
DSC001.jpg → web_DSC001.jpg (1200x900, high quality)
DSC002.jpg → web_DSC002.jpg (1200x900, high quality)
```

### Example 4: Mirror directory structure

```bash
./lulada.py ~/Photos/originals ~/Photos/thumbs --keep-name --preset sm
```

Output (same names, different folder):
```
photo1.jpg → photo1.jpg (400x300)
photo2.jpg → photo2.jpg (400x300)
```

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- WebP (.webp)

## How It Works

1. **Reads Configuration**: Loads settings from `lulada.ini`
2. **Scans Source Directory**: Finds all image files
3. **Generates Thumbnails**: Resizes each image maintaining aspect ratio
4. **Saves with New Name**: Applies prefix/postfix/preset naming
5. **Skips Existing**: Won't overwrite existing thumbnails
6. **Reports Results**: Shows summary of processed files

## Tips

- Use `--preset` for consistent sizing across projects
- Use `{size}` placeholder in prefix/postfix for automatic size labels
- Adjust `--quality` to balance file size and image quality (85 is a good default)
- The script skips existing files, so it's safe to run multiple times
- Images maintain aspect ratio - thumbnails fit within specified dimensions

## Troubleshooting

**Error: PIL/Pillow is required**
```bash
pip install Pillow
```

**Config file not found**
- Make sure `lulada.ini` is in the same directory as `lulada.py`
- Or specify a custom config with `--config`

**Permission denied**
```bash
chmod +x lulada.py
```

**Images look pixelated**
- Increase the size with `--width` and `--height`
- Increase quality with `--quality 95`

## Related Tools

- **lulofoto.py**: Photo organizer that sorts images by date

## License

MIT License - feel free to use and modify as needed.
