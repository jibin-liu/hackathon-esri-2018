import json
import os
import shutil
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


BASE_DIR = 'downloaded/'
# See https://www.mapillary.com/developer/api-documentation/
MAPILLARY_API_IM_SEARCH_URL = 'https://a.mapillary.com/v3/images?'
MAPILLARY_API_IM_RETRIEVE_URL = 'https://d1cuyjsrcm0gby.cloudfront.net/'
CLIENT_ID = 'QmhiQS1rdHhETEhGVHpIVEJHVUdJZzphY2E5YzhlZjYxZWI2YThm'


'''
Script to download images using the Mapillary image search API.

Downloads images inside a rect (min_lat, max_lat, min_lon, max_lon).
'''

def create_dirs(base_path):
    try:
        shutil.rmtree(base_path)
    except:
        pass
    os.makedirs(base_path)


def query_search_api(min_lat, max_lat, min_lon, max_lon, max_results):
    '''
    Send query to the search API and get dict with image data.
    '''

    # Create URL
    params = {
        'client_id': CLIENT_ID,
        'bbox': ','.join([str(min_lon), str(min_lat), str(max_lon), str(max_lat)]),
        'per_page': str(max_results)
    }

    # Get data from server, then parse JSON
    query = requests.get(MAPILLARY_API_IM_SEARCH_URL, params=params).json()
    query = query['features']

    return query


def download_images(query, path, size=1024):
    '''
    Download images in query result to path.

    Return list of downloaded images with lat,lon.
    There are four sizes available: 320, 640, 1024 (default), or 2048.
    '''
    im_size = "thumb-{0}.jpg".format(size)
    im_list = []
    downloaded = 0

    for im in query:
        # Use key to create url to download from and filename to save into
        key = im['properties']['key']
        url = MAPILLARY_API_IM_RETRIEVE_URL + key + '/' + im_size
        filename = key + ".jpg"

        try:
            # Get image and save to disk
            res = requests.get(url, stream=True)
            with open(path + filename, 'wb') as outfile:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, outfile)

            # Log filename and GPS location
            coords = ",".join(map(str, im['geometry']['coordinates']))
            im_list.append([filename, coords])

            downloaded += 1
            # print("Successfully downloaded: {0}".format(filename))
        except KeyboardInterrupt:
            break
        except:
            # print("Failed to download: {0}".format(filename))
            continue

    total = len(query)
    return im_list, (downloaded, total)


def download_worker(download_dir, min_lat, max_lat, min_lon, max_lon,
                    max_results=1000, image_size=1024):
    # query api
    query = query_search_api(min_lat, max_lat, min_lon, max_lon, max_results)
    # create directories for saving
    create_dirs(download_dir)

    # download
    downloaded_list, stats = download_images(query, path=download_dir, size=image_size)

    # save filename with lat, lon
    with open(download_dir+"downloaded.txt", "w") as f:
        for data in downloaded_list:
            f.write(",".join(data) + "\n")

    print("{}/{} images downloaded into {}".format(*stats, download_dir))


def move_download_logfile(download_dir):
    """ move downloaded.txt file out to another folder """
    # create logfolder
    logfolder = os.path.join(download_dir, 'logfile')
    if not os.path.exists(logfolder):
        os.mkdir(logfolder)

    for folder in tqdm(os.listdir(download_dir)):
        download_txt = os.path.join(download_dir, folder, 'downloaded.txt')
        dest = os.path.join(logfolder, folder + '.txt')
        if os.path.exists(download_txt):
            shutil.copyfile(download_txt, dest)
            os.remove(download_txt)


def main(polygons_json):
    with open(polygons_json, 'r') as infile:
        # load polygons
        polygons = json.load(infile)

        # download images for each polygon
        with ThreadPoolExecutor(max_workers=8) as executor:
            for polygon in polygons:
                folder = 'mapillary/{}/'.format(polygon)
                bbox = polygons[polygon]
                executor.submit(download_worker, folder, *bbox)

    print('Move download logfiles:')
    move_download_logfile('mapillary')
    print('')


if __name__ == '__main__':
    '''
    Use from command line as below, or run query_search_api and download_images
    from your own scripts.
    '''

    main('polygons.json')

    # parser = argparse.ArgumentParser()
    # parser.add_argument('min_lat', type=float)
    # parser.add_argument('max_lat', type=float)
    # parser.add_argument('min_lon', type=float)
    # parser.add_argument('max_lon', type=float)
    # parser.add_argument('--max_results', type=int, default=400)
    # parser.add_argument('--image_size', type=int, default=1024, choices=[320,640,1024,2048])
    # args = parser.parse_args()

    # download_worker(BASE_DIR, args.min_lat, args.max_lat, args.min_lon,
    #                 args.max_lon, args.max_results, args.image_size)
