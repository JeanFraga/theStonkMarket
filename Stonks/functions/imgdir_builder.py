from bs4 import BeautifulSoup
from Stonks.schema import DB, Template
import requests
from multiprocessing import cpu_count, Manager, Pool

def get_meme_data(meme_containers):
    data_list = []
    for meme in meme_containers:
        data_list.append(meme['src'])
        
    return data_list

def get_page_data(page_number):
    return time.time()
    templates = DB.session.query(Template).all()
    imgflip_pages = [template.imgflip_page+'?page={}' for template in templates]
    names = [template.name for template in templates][:20]
    return names

    for imgflip_page, name in zip(imgflip_pages, names):

        with requests.get(imgflip_page.format(page_number)) as imgflip_page:
            soup = BeautifulSoup(imgflip_page.text, 'lxml')
        
        meme_containers = soup.find_all('div', class_='base-img')

        return 'test'
        return meme_containers

        if meme_containers: return {name: get_meme_data(meme_containers)}
        else: return [0]

def build_imgdir():

    start_page = 1
    step_size = 5
    memes_list = []

    early_stopping = 0
    while 0 not in memes_list:
        early_stopping+=1
        if early_stopping>2: break

        end_page = start_page+step_size

        memes = []
        with Pool(cpu_count()) as pool:
            r = pool.map_async(get_page_data, range(start_page, end_page), callback=memes.append)
            r.wait()

        # memes_list += [meme for sublist in memes[0] for meme in sublist]
        start_page=end_page
    # memes = list(filter(lambda a: a != 0, memes_list))
    
    return memes