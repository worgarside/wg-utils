from os import system, name, getenv, path
from dotenv import load_dotenv

from bs4 import BeautifulSoup
from requests import get, post
from pickle import load, dump

GROUPS = [
    'https://groups.freecycle.org/group/ChesterCityWest/posts/offer',
    'https://groups.freecycle.org/group/ChesterCityEastUK/posts/offer',
    'https://groups.freecycle.org/group/creweUK/posts/offer',
    'https://groups.freecycle.org/group/FlintshireUK/posts/offer',
    'https://groups.freecycle.org/group/MarketDraytonUK/posts/offer',
    'https://groups.freecycle.org/group/ShrewsburyUK/posts/offer',
    'https://groups.freecycle.org/group/WrexhamUK/posts/offer'
]

KEYWORDS = {'desktop', 'laptop', 'computer', 'dell', 'acer', 'parts', 'electronic', 'tv', 'television', 'spare parts',
            'asus', 'monitor', 'pi', 'hp', 'printer', 'microwave', 'phone', 'lenovo', 'arduino', 'thinkpad', 'xiaomi',
            'macbook', 'apple', 'mac', 'electronics'}

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'

PKL_FILE = '{}scripts/cron/freecycle_links.pkl'.format(WGUTILS_DIR)
ENV_FILE = '{}secret_files/.env'.format(WGUTILS_DIR)

load_dotenv(ENV_FILE)

PB_API_KEY = getenv('PB_API_KEY')


def notify(t='Freecycle Alert', m=''):
    post(
        'https://api.pushbullet.com/v2/pushes',
        headers={
            'Access-Token': PB_API_KEY,
            'Content-Type': 'application/json'
        },
        json={
            'body': m,
            'title': t,
            'type': 'note'
        }
    )


def main():
    with open(PKL_FILE, 'rb') as f:
        scraped_links = load(f)

    for group in GROUPS:
        table = BeautifulSoup(get(group).content, 'html.parser').findAll('table')

        if not len(table) == 1:
            notify(m='Number of tables on page != 1: {}'.format(len(table)))
        else:
            table = table[0]

        rows = table.findAll('tr')

        for item in rows:
            item_link_set = set([a['href'] for a in item.findAll('a', href=True)])

            if not len(item_link_set) == 1:
                notify(m='Number of links in row {} != 1: {}'.format(item, len(item_link_set)))

            item_link = item_link_set.pop()

            if item_link in scraped_links:
                continue
            else:
                scraped_links.add(item_link)

            item_details = BeautifulSoup(get(item_link).content, 'html.parser').find('div', {'id': 'group_post'})

            item_title = ''
            for h2 in item_details.findAll('h2'):
                if 'offer' in h2.text.lower():
                    item_title = h2.text.lower().replace('offer:', '')
                    break

            item_desc = [p.text for p in item_details.findAll('p')]

            item_lookup = set(' '.join(item_desc).split()) | set(item_title.split())

            if KEYWORDS & item_lookup:
                notify(m='{}\n\n{}\n\n{}'.format(item_title.title().strip(), item_desc[0].strip(), item_link))

    with open(PKL_FILE, 'wb') as f:
        dump(scraped_links, f)


if __name__ == '__main__':
    main()
