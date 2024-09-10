from PIL import Image, ExifTags

img = Image.open('/Users/mohamedchegri/Desktop/2024-09-10 16.44.11.jpg')

exif_data = img._getexif()

if exif_data:
    exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items() if k in ExifTags.TAGS}
    for tag, value in exif.items():
        print(f"{tag}: {value}")
else:
    print("No EXIF metadata found in the image.")
