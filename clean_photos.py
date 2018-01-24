"""
remove photos without geotags
"""


import exifread
import os
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def copy_photos_with_geotags(from_folder, to_folder):
    for file in tqdm(os.listdir(from_folder)):
        existing_file = os.path.join(to_folder, file)
        if os.path.exists(existing_file):
            continue

        filepath = os.path.join(from_folder, file)
        f = open(filepath, 'rb')
        try:
            tags = exifread.process_file(f)
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                shutil.copy(filepath, to_folder)
        except Exception as e:
            continue


def list_photos(in_folder):
    return (os.path.join(from_folder, file) for file in os.listdir(in_folder))


def copy_photo_with_geotags(filepath, out_folder):
    f = open(filepath, 'rb')
    tags = exifread.process_file(f)
    if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
        shutil.copy(filepath, to_folder)
    return 'Successsfully copied {}'.format(os.path.basename(filepath))


if __name__ == '__main__':
    from_folder = r'.\photos'
    to_folder = r'.\photos_geo'
    # photos = list_photos(from_folder)
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     futures = [executor.submit(copy_photo_with_geotags, photo, to_folder) for photo in tqdm(photos)]
    #     for future in as_completed(futures):
    #         print(future.result())
    copy_photos_with_geotags(from_folder, to_folder)
