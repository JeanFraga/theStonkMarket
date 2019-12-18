from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from bs4 import BeautifulSoup
from schema import DB, Template
import requests
from multiprocessing import cpu_count, Manager, Pool

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
    memes_list = []

    while 0 not in memes_list:
        end_page = start_page+step_size

        memes = []
        with Pool(cpu_count()) as pool:
            r = pool.map_async(get_page_data, range(start_page, end_page), callback=memes.append)
            r.wait()

        memes_list += [meme for sublist in memes[0] for meme in sublist]
        start_page=end_page
    memes = list(filter(lambda a: a != 0, memes_list))

    templates = [Template(**meme) for meme in memes]
    DB.session.add_all(templates)
    DB.session.commit()

if __name__=="__main__":
    build_template_db()