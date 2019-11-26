import requests
from multiprocessing import cpu_count, Manager, Pool
from google_images_download import google_images_download

from Stonks.schema import DB, Template

imgdir_size = 1

def initializer():
    global google
    google = google_images_download.googleimagesdownload()

def search_google(name):
    arguments = {
        "keywords": name,
        "limit": 110,
        "output_directory": "Stonks/assets/imgdir",
        "chromedriver": "Stonks/assets/chromedriver.exe",
        "no_download": True,
        "save_source": "testing.txt"}
    try:
        absolute_image_paths = google.download(arguments)
    except: pass

def build_imgdir():
    
    templates = DB.session.query(Template).all()
    names = [template.name for template in templates]

    with Pool(cpu_count(), initializer) as pool:
        r = pool.map_async(search_google, names[:1])
        r.wait()

    return 'done'