import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import shutil


def query_photos_by_page(page):
    """ query photos by bbox """
    sf = ['-122.519311', '37.707870', '-122.358216', '37.818383']
    url = 'https://api.flickr.com/services/rest/'
    params = {
        'method': 'flickr.photos.search',
        'api_key': '165300b58a365ba2c650d0182ca6f5d9',
        'bbox': ','.join(sf),
        'format': 'json',
        'nojsoncallback': '1',
        'extras': 'url_o,original_format,geo',
        'page': page,
        'per_page': '250'
    }
    r = requests.get(url, params)
    print(r.url)
    res = r.json()

    download_photo_by_page(res['photos'])


def photo_info_to_url(photo_info):
    """ convert photo dict into url for download """
    if 'url_o' in photo_info:
        return photo_info['url_o']
    else:
        return 'https://farm{farm}.staticflickr.com/{server}/{id}_{secret}.jpg'.format(**photo_info)


def download_photo(photo_info, folder):
    """ dowload photo provided as url """
    url = photo_info_to_url(photo_info)
    photo_filename = url.split('/')[-1]

    # skip exist file 1/21
    exist_file = os.path.join(os.getcwd(), 'photos', photo_filename)
    if not os.path.exists(exist_file):

        photo_path = os.path.join(folder, photo_filename)

        res = requests.get(url, stream=True)
        if res.status_code == 200:
            with open(photo_path, 'wb') as outfile:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, outfile)

    # save the photo lat long
    # save_photo_lat_long(d, photo_filename, photo_info['latitude'], photo_info['longitude'])

    # return 'Finished downloading {}'.format(photo_filename)


def save_photo_lat_long(d, photo_filename, lat, lon):
    d[photo_filename] = (lat, lon)


def download_photo_by_page(photo_json):
    # yield each photo
    page = photo_json['page']
    folder = os.path.join(os.getcwd(), 'photos2', str(page))
    if not os.path.exists(folder):
        os.mkdir(folder)

    for photo in photo_json['photo']:
        download_photo(photo, folder)

    msg = 'Finished downloading page: {}'.format(page)
    print(msg)


if __name__ == '__main__':

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(query_photos_by_page, page) for page in range(101, 696)]
        for future in as_completed(futures):
            print(future.result())
