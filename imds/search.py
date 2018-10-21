import os
import logging
from io import BytesIO
from pathlib import Path
from typing import Collection
from multiprocessing import Pool, cpu_count

import requests
from PIL import Image


class BingImageSearch:
    """Simple wrapper on top of Microsoft Cognitive Search API.

    The wrapper focused on a specific API functionality, namely, image search.
    So it was intentionally narrowed to simplify usage.
    """
    url = 'https://api.cognitive.microsoft.com/bing/v7.0/images/search'
    env_var = 'BING_SEARCH_API_KEY'

    def __init__(self, api_key=None, log=None, parallel: bool=True):
        if api_key is None:
            if self.env_var not in os.environ:
                raise ValueError(
                    'Neither API key, nor env variable was provided.')
            api_key = os.environ[self.env_var]

        self.log = log or default_logger()
        self.parallel = parallel
        self.headers = {'Ocp-Apim-Subscription-Key': api_key}

    def download(self, queries: Collection[str], folder: str=None):

        def get_urls(r):
            values = r.get('value')
            if values is None:
                return None
            return [img['thumbnailUrl'] for img in values]


        offset, count = 0, 20
        folder = Path(folder or os.getcwd())
        os.makedirs(folder, exist_ok=True)
        downloaded = []
        log = self.log

        for query in queries:
            log.info('[.] Running query: %s', query)
            index = 0
            while True:
                result = self.request_images_json(query, offset, count)
                if result is None:
                    return
                thumbnail_urls = get_urls(result)
                if thumbnail_urls is None:
                    log.warning('[!] No more results for query')
                    break
                images = self.download_images(thumbnail_urls)
                paths = self.save_images(images, folder, index)
                index += len(paths)
                offset = result['nextOffset']
                downloaded.extend(paths)

        return downloaded

    def download_images(self, urls: Collection[str]) -> Collection:
        if self.parallel:
            with Pool(cpu_count()) as pool:
                images = pool.map(download_image, urls)
        else:
            images = [download_image(url) for url in urls]
        return [img for img in images if img is not None]

    def request_images_json(
            self, search_term: str, offset: int=0, count: int=10,
            save_search=True, public_domain=True, image_type='photo'):

        params = {'q': search_term,
                  'offset': offset,
                  'count': count,
                  'safeSearch': 'Strict' if save_search else 'Off',
                  'imageType': image_type}

        if public_domain:
            params['license'] = 'public'

        response = requests.get(self.url, headers=self.headers, params=params)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            error = response.json()
            self.log.error('[-] Cannot make query')
            for info in error['errors']:
                self.log.error(f"[-] {info['code']}. {info['moreDetails']}")
            return None
        else:
            return response.json()

    def save_images(self, images: Collection, folder: Path, start: int=0):
        """Saves downloaded images into folder.

        Each image is named after its order in collection, starting from
        `offset`. For example, if `images` array contains 5 images, and
        offset is equal to 10, then `folder` will have the following content:

            folder/
                - 10.jpeg
                - 11.jpeg
                - 12.jpeg
                - 13.jpeg
                - 14.jpeg

        Args:
            images: Collection of PIL images.
            folder: Destination folder.
            start: Starting number to enumerate images.

        """
        paths = []
        for index, img in enumerate(images, start):
            path = folder/f'{index}.{img.format.lower()}'
            img.save(path)
            paths.append(path)
        self.log.info(f'Number of images saved: {len(paths)}')
        return paths


def default_logger():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    return logging.getLogger()


def download_image(url: str) -> Image:
    image_data = requests.get(url)
    try:
        image_data.raise_for_status()
    except requests.HTTPError:
        return None
    else:
        return Image.open(BytesIO(image_data.content))
