import requests
import os
import io
import hashlib
from multiprocessing import cpu_count, Manager, Pool
from google_images_download import google_images_download
from contextlib import redirect_stdout
from PIL import Image
from PIL.ImageOps import fit

from Stonks.schema import DB, Template

num_workers = cpu_count()
imgdir_size = 1
IMGDIR_PATH = 'Stonks/databases/imgdir'
google_doc = 'Stonks/assets/google_data.txt'
google_agrs = {
    "limit": 10,
    "chromedriver": "Stonks/assets/chromedriver.exe",
    "no_download": True,
    "print_urls": True,
}

def initializer():
    global google
    google = google_images_download.googleimagesdownload()

def search_google(name):
    google_agrs['keywords'] = name
    with open(google_doc, 'a+') as f:
        with redirect_stdout(f):
            google.download(google_agrs)

def parse_out_data(doc):
    lines = []
    current_name = ''
    with open(doc, 'r+') as f:
        for line in f.readlines():
            if 'Item name' in line:
                name = line.split('=')[1].replace('\n', '')[1:]
                current_name = name
            if 'Image URL' in line:
                url = line.split(':')[1].replace(' ', '') + ':' + line.split(':')[2].replace('\n', '')
                lines.append([url, current_name])

    return lines

def download_img(data):
    url, name = data
    
    try:
        with requests.get(url) as raw:
            raw_img = Image.open(io.BytesIO(raw.content))

        # img = fit(raw_img, (224, 224), Image.ANTIALIAS)
        img = raw_img.convert("L")

        img_hash = hashlib.md5(img.tobytes()).hexdigest()
        
        # output_filename = os.path.join(IMGDIR_PATH, f"{name}/{img_hash}.png")
        output_filename = os.path.join(IMGDIR_PATH, f"{img_hash}.png")

        with open(output_filename, 'wb') as out_file:
            img.save(out_file, format='png')

        return img_hash
        
    except Exception as e: return str(e)
def build_imgdir():
    
    templates = DB.session.query(Template).all()
    names = [template.name for template in templates]

    # for name in names:
    #     try:
    #         os.mkdir(os.path.join(IMGDIR_PATH, f"{name}"))
    #     except: pass

    with Pool(num_workers, initializer) as pool:
        r = pool.map_async(search_google, names[:10])
        r.wait()

    data = parse_out_data(google_doc)
    os.remove(google_doc)

    hashs = []
    with Pool(num_workers) as pool:
        r = pool.map_async(download_img, data[:10], callback=hashs.append)
        r.wait()

    return hashs
    