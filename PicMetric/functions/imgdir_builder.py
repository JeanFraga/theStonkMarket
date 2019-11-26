import requests
from multiprocessing import cpu_count, Manager, Pool
from Stonks.schema import DB, Template

serpapi = 'https://serpapi.com/playground?q={}&tbm=isch&ijn={}'

def search_google():
    pass

def build_imgdir():
    imgdir_size = 1_000
    img_urls = DB.session.query(Template.url).all()
    # with Pool(cpu_count()) as pool:
    #     r = pool.map_async(search_google, range(start_page, end_page), callback=memes.append)
    #     r.wait()

    return img_urls