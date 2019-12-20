import requests, os, io, hashlib, time
from multiprocessing import cpu_count, Manager, Pool
from google_images_download import google_images_download
from Stonks.functions.constants import DATASET_PATH
from contextlib import redirect_stdout
from PIL import Image
from PIL.ImageOps import fit

from Stonks.schema import DB, Template

num_workers = cpu_count()
num_names = 20

google_agrs = {
    "limit": 100,
    "chromedriver": "Stonks/assets/chromedriver.exe",
    "no_download": True,
    "print_urls": True,
}

def initializer():
    global google
    google = google_images_download.googleimagesdownload()

def parse_data(doc):
    try:
        lines = []
        current_name = ''
        for line in doc.split('\n'):
            if 'Item name' in line:
                current_name = line.split('=')[1].replace('\n', '')[1:]
            if 'Image URL' in line:
                url = line.split(':')[1].replace(' ', '') + ':' + line.split(':')[2].replace('\n', '')
                lines.append([url, current_name])

        return lines
    except Exception as e: return str(e)

def search_google(name):
    try:
        google_agrs['keywords'] = name
        f = io.StringIO()
        with redirect_stdout(f):
            google.download(google_agrs)
            
        return parse_data(f.getvalue())
    except Exception as e: return str(e)

def download_img(data):
    url, name = data
    
    try:
        with requests.get(url) as raw:
            raw_img = Image.open(io.BytesIO(raw.content))
    except: pass
    else:
        # img = fit(raw_img, (224, 224), Image.ANTIALIAS)
        img = raw_img.convert('RGB')
        img_hash = hashlib.md5(img.tobytes()).hexdigest()
        output_filename = os.path.join(DATASET_PATH, f"{name}", f"{img_hash}.png")

        with open(output_filename, 'wb') as out_file:
            img.save(out_file, format='png')
        
    

def engine(name):
    for meme in search_google(name):
        download_img(meme)


def build_google_imgdir():
    start = time.time()
    templates = DB.session.query(Template).all()
    names = [template.name for template in templates]#[:num_names]

    for name in names:
        try:
            os.mkdir(os.path.join(DATASET_PATH, f"{name}"))
        except: pass

    with Pool(num_workers, initializer) as pool:
        r = pool.map_async(engine, names)
        r.wait()

    return str((time.time()- start) /60)
    