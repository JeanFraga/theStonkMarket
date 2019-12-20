from bs4 import BeautifulSoup
from Stonks.schema import DB, Template
import requests
from multiprocessing import cpu_count, Pool
import itertools

IMG_FLIP_URI = 'https://imgflip.com/memetemplates?page={}'

def get_meme_data(memes):
    data_list = []
    for meme in memes:
        data = {
            'name': meme.div.a['title'],
            'imgflip_page': 'imgflip.com' + meme.div.a['href'],
            'url': meme.div.a.img['src']
        }
        data_list.append(data)
        
    return data_list

def get_page_data(page_number):
    with requests.get(IMG_FLIP_URI.format(page_number)) as imgflip_page:
        soup = BeautifulSoup(imgflip_page.text, 'lxml')
    
    meme_containers = soup.find_all('div', class_='mt-box')

    if meme_containers: return get_meme_data(meme_containers)
    else: return [0]

def build_template_db():
    start_page = 1
    step_size = 32
    meme_data = []

    while [0] not in meme_data:
        end_page = start_page+step_size

        with Pool(cpu_count()) as pool:
            r = pool.map_async(get_page_data, range(start_page, end_page), callback=meme_data.extend)
            r.wait()

        start_page=end_page

    meme_gen = filter(lambda a: a != 0, itertools.chain.from_iterable(meme_data))
    templates = [Template(**meme) for meme in meme_gen]
    DB.session.add_all(templates)
    DB.session.commit()

    return list(filter(lambda a: a != 0, itertools.chain.from_iterable(meme_data)))