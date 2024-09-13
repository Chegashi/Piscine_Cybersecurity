#!/usr/bin/env python3

import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS

EXIF_SUPPORTED_FORMATS = ['JPEG', 'TIFF']

def get_exif_data(img):
    """Extract EXIF data from an image file if supported."""
    try:
        if img.format not in EXIF_SUPPORTED_FORMATS:
            return None
        exif_data = img._getexif()
        if exif_data:
            exif = {}
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                exif[tag_name] = value
            return exif
        return None
    except AttributeError:
        return None
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")
        return None

def display_basic_info(img):
    """Display basic image attributes such as size, width, and height."""
    width, height = img.size
    print(f"Width: {width} px")
    print(f"Height: {height} px")

def display_metadata(file):
    """Display metadata including EXIF data and basic info for a given image file."""
    try:
        file_stats = os.stat(file)
        print(f"\nFile: {file}")
        print(f"Size: {file_stats.st_size} bytes")
        print(f"Created: {os.path.getctime(file)}")
        print(f"Last Modified: {os.path.getmtime(file)}")
        img = Image.open(file)
        print(f"Image Format: {img.format}")
        exif = get_exif_data(img)
        if exif:
            print("EXIF Data:")
            for key, value in exif.items():
                print(f"{key}: {value}")
        else:
            print(f"No EXIF data found or EXIF not supported for {img.format} files.")
        display_basic_info(img)
    except Exception as e:
        print(f"Error displaying metadata: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: ./scorpion.py FILE1 [FILE2 ...]")
        sys.exit(1)

    for file in sys.argv[1:]:
        if os.path.isfile(file):
            display_metadata(file)
        else:
            print(f"File not found: {file}")

if __name__ == '__main__':
    main()
