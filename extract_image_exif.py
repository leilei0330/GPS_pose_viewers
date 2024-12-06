import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd
from tqdm import tqdm

def get_decimal_coordinates(info):
    """Convert GPS coordinates from degrees/minutes/seconds to decimal degrees"""
    if not info:
        return None
    
    for key in ['Latitude', 'Longitude']:
        if f'GPS{key}' not in info or f'GPS{key}Ref' not in info:
            return None

    lat = info['GPSLatitude']
    lat_ref = info['GPSLatitudeRef']
    lon = info['GPSLongitude']
    lon_ref = info['GPSLongitudeRef']

    lat = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600
    lon = float(lon[0]) + float(lon[1])/60 + float(lon[2])/3600

    if lat_ref != 'N':
        lat = -lat
    if lon_ref != 'E':
        lon = -lon

    return lat, lon

def get_altitude(info):
    """Get altitude from GPS info"""
    if not info or 'GPSAltitude' not in info:
        return None
    
    altitude = info['GPSAltitude']
    if isinstance(altitude, tuple):
        altitude = float(altitude[0]) / float(altitude[1])
    return altitude

def get_gps_info(image_path):
    """Extract GPS information from image EXIF data"""
    try:
        image = Image.open(image_path)
        exif = image._getexif()
        
        if not exif:
            return None, None, None

        gps_info = {}
        for tag, value in exif.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                for gps_tag in value:
                    sub_tag = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[sub_tag] = value[gps_tag]

        lat_lon = get_decimal_coordinates(gps_info)
        altitude = get_altitude(gps_info)

        if lat_lon:
            return lat_lon[0], lat_lon[1], altitude
        return None, None, None

    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None, None, None

def process_images_folder(folder_path):
    """Process all images in a folder and save GPS data to CSV"""
    # Get all image files using a set to avoid duplicates
    image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
    image_files = set()
    
    # Walk through the directory
    for filename in os.listdir(folder_path):
        ext = os.path.splitext(filename.lower())[1]  # 转换为小写进行比较
        if ext in image_extensions:
            image_files.add(os.path.join(folder_path, filename))
    
    # Convert set to sorted list
    image_files = sorted(list(image_files))
    print(f"Found {len(image_files)} image files")

    # Prepare data for DataFrame
    data = []
    for image_path in tqdm(image_files, desc="Processing images", unit="image"):
        image_name = os.path.basename(image_path)
        lat, lon, altitude = get_gps_info(image_path)
        data.append({
            'image_name': image_name,
            'longitude': lon,  # X-axis
            'latitude': lat,   # Y-axis
            'altitude': altitude  # Z-axis
        })

    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    
    # Save CSV in parent directory
    parent_dir = os.path.dirname(folder_path)
    folder_name = os.path.basename(folder_path)
    csv_path = os.path.join(parent_dir, f'{folder_name}_exif_data.csv')
    
    df.to_csv(csv_path, index=False, header=False)  # header=False 表示不保存列名
    print(f"\nCSV file saved to: {csv_path}")

if __name__ == "__main__":
    # Get folder path from user input
    # folder_path = input("Please enter the folder path containing images: ")
    folder_path = input("请输入包含图像的文件夹路径: ")
    folder_path = folder_path.strip('"')  # Remove quotes if present
    
    if os.path.isdir(folder_path):
        process_images_folder(folder_path)
    else:
        print("Invalid folder path. Please provide a valid directory path.")
