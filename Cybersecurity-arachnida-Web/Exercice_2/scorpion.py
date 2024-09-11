#!/usr/bin/env python3

from PIL import Image, ExifTags
from sys import argv, exit

def extract_exif(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return "No EXIF metadata found in the image."
        exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items() if k in ExifTags.TAGS}
        return exif
    except Exception as e:
        return f"Error processing the image: {e}"

def print_exif(exif_data):
    if isinstance(exif_data, dict):
        for tag, value in exif_data.items():
            print(f"{tag}: {value}")
    else:
        print(exif_data)

def main():
    if len(argv) != 2:
        print("Usage: python3 scorpion.py <image_path>")
        exit(1)
    
    image_path = argv[1]
    exif_data = extract_exif(image_path)
    print_exif(exif_data)

if __name__ == "__main__":
    main()
