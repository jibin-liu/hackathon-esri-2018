"""
ref: http://web.archive.org/web/20120919234615/http://mkelsey.com/2011/07/03/Flickr-oAuth-Python-Example.html
"""

import time
import requests
import shutil
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


class FlickrAPI(object):
    OAUTH_URL = r'https://www.flickr.com/services/oauth/'

    def __init__(self, consumer_key, secret):
        """ initializer """
        self._consumer_key = consumer_key
        self._secret = secret

        # initialize properties
        self._oauth_token = None
        self._oauth_token_secret = None
        self._token = None
        self._access_token = None
        self._access_token_secret = None

    def _parse_response_content(self, res):
        contents = dict()
        for content in res.text.split('&'):
            k, v = content.split('=')
            contents[k] = v

        return contents

    def _request_token(self):
        if self._oauth_token and self._oauth_token_secret:
            return

        url = self.OAUTH_URL + 'request_token'
        params = {
            'oauth_timestamp': str(int(time.time())),
            'oauth_signature_method':"HMAC-SHA1",
            'oauth_version': "1.0",
            'oauth_callback': "http://www.flickr.com",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_consumer_key': self._consumer_key
        }

        # create consumer
        self._consumer = oauth.Consumer(key=self._consumer_key, secret=self._secret)

        # construct request
        req = oauth.Request(method='GET', url=url, parameters=params)

        # create signature
        signature = oauth.SignatureMethod_HMAC_SHA1().sign(req, self._consumer, None)
        req['oauth_signature'] = signature

        # making request
        res = requests.get(req.to_url())
        if res.ok:
            contents = self._parse_response_content(res)

            self._oauth_token = contents['oauth_token']
            self._oauth_token_secret = contents['oauth_token_secret']

        else:
            res.raise_for_status()

    def _authorize(self):
        if not self._oauth_token and not self._oauth_token_secret:
            self._request_token()

        url = self.OAUTH_URL + 'authorize'
        self._token = oauth.Token(self._oauth_token, self._oauth_token_secret)

        # request for ahuthorize
        print('Go to the following link in your browser:')
        print('{}?oauth_token={}&perms=read'.format(url, self._oauth_token))
        print()

        # input verifier
        self._oauth_verifier = input('Type the verifier: ')
        self._token.set_verifier(self._oauth_verifier)

    def get_access_token(self):
        if not self._token:
            self._authorize()

        url = self.OAUTH_URL + 'access_token'
        params = {
            'oauth_consumer_key': self._consumer_key,
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_signature_method':"HMAC-SHA1",
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': self._oauth_token,
            'oauth_verifier' : self._oauth_verifier
        }

        # create request
        req = oauth.Request(method='GET', url=url, parameters=params)

        # create signature
        signature = oauth.SignatureMethod_HMAC_SHA1(). sign(req,
                                                            self._consumer,
                                                            self._token)
        req['oauth_signature'] = signature

        # make request
        res = requests.get(req.to_url())
        if res.ok:
            contents = self._parse_response_content(res)

            self._access_token = contents['oauth_token']
            self._access_token_secret = contents['oauth_token_secret']
            import pdb; pdb.set_trace()
            self.save_access_token_to_file(filename=contents['username'])

        else:
            res.raise_for_status()

    def save_access_token_to_file(self, filename):
        """
        save access token and access token secret, using username as filename
        """

        if not self._access_token and not self._access_token_secret:
            self.get_access_token()

        with open(r'./{}.txt'.format(filename), 'w') as outfile:
            outfile.write('access_token={}\n'.format(self._access_token))
            outfile.write('access_token_secret={}'.format(self._access_token_secret))


def query_photos_by_bbox(min_long, min_lat, max_long, max_lat):
    """ query photos by bbox """
    url = 'https://api.flickr.com/services/rest/'
    params = {
        'method': 'flickr.photos.search',
        'api_key': 'c4fe8cd9de5d67c6b06e12c46ff87568',
        'bbox': ','.join([min_long, min_lat, max_long, max_lat]),
        'format': 'json',
        'nojsoncallback': '1',
        'extras': 'url_o,original_format,geo',
        'per_page': '250'
    }
    res = requests.get(url, params).json()
    
    # get number of pages
    pages = int(res['photos']['pages'])
    page = 1

    # yield photo in each page
    while page <= pages:
        params['page'] = str(page)
        r = requests.get(url, params)
        res = r.json()

        if res['stat'] != 'ok':
            raise ValueError(r.url)

        # yield each photo
        for photo in res['photos']['photo']:
            yield photo

        page += 1


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
    photo_path = os.path.join(folder, photo_filename)

    # check existing file
    if not os.path.exists(photo_path):
        res = requests.get(url, stream=True)
        if res.status_code == 200:
            with open(photo_path, 'wb') as outfile:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, outfile)

    # save the photo lat long
    # save_photo_lat_long(d, photo_filename, photo_info['latitude'], photo_info['longitude'])

    return 'Finished downloading {}'.format(photo_filename)


def save_photo_lat_long(d, photo_filename, lat, lon):
    d[photo_filename] = (lat, lon)


def download_photo_by_page(photo_json, page):
    folder = os.path.join(os.getcwd(), 'photos', str(page))
    if not os.path.exists(folder):
        os.mkdir(folder)

    for photo in photo_json['photo']:
        download_photo(photo, folder, d)



if __name__ == '__main__':
    # key = '165300b58a365ba2c650d0182ca6f5d9'
    # secret = '050836c8d87616de'
    # flickr = FlickrAPI(key, secret)
    # flickr.get_access_token()
    # sf = ['-122.519311', '37.707870', '-122.358216', '37.818383']
    bbox = open(r'.\sf.csv').readlines()
    for box in bbox:
        photos = query_photos_by_bbox(*box.split(','))
        folder = os.path.join(os.getcwd(), 'photos')
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(download_photo, photo, folder) for photo in photos]
            for future in as_completed(futures):
                print(future.result())
