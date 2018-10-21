from io import BytesIO
from pprint import pprint as pp

import requests
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


AUTH_KEY = '0f699f06f94f4629ad0de64ab4243f30'
SEARCH_URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"


def image_request(search_term,
                  offset=0,
                  count=10,
                  url=SEARCH_URL,
                  key=AUTH_KEY):

    headers = {"Ocp-Apim-Subscription-Key": key}
    params = {"q": search_term,
              "offset": offset,
              "count": count,
              "safesearch": "on",
              "license": "public",
              "imageType": "photo"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    results = response.json()
    return results


def get_urls(result):
    values = result.get('value')
    if values is None:
        return None
    thumbnail_urls = [img['thumbnailUrl'] for img in values]
    return thumbnail_urls


def download_images(urls):
    for url in urls:
        print('[.] Getting image:', url)
        image_data = requests.get(url)
        try:
            image_data.raise_for_status()
        except requests.HTTPError:
            print('[-] Cannot retrieve image. Skipping...')
        else:
            image = Image.open(BytesIO(image_data.content))
            yield image


def save_images_grid(images, filename):
    f, axes = plt.subplots(4, 4)
    for ax, image in zip(axes.flatten(), images):
        ax.axis('off')
        ax.imshow(image)
    f.savefig(filename)
    print('[+] Images saved into file:', filename)


def main():
    offset, count = 0, 16
    for query in ('white male face',):
        print(f'[.] Running query: \'{query}\'')
        while True:
            result = image_request(query, offset=offset, count=count)
            thumbnail_urls = get_urls(result)
            if thumbnail_urls is None:
                print('[!] No more results for query')
                break
            images = list(download_images(thumbnail_urls))
            filename = f'grid_{offset}_{count}.png'
            save_images_grid(images, filename)
            offset += count
    print('[.] Ended')


if __name__ == '__main__':
    main()
