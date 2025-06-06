import time
import os
import sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from playwright.sync_api import sync_playwright
from modules.data_utils import load_dict_data, save_dict_data

DATA_FILE = "casos_dengue/casos_dengue.json"

def access_website(p):
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def"
    page.goto(url)
    print(f"Acessando página: {url}")

    return page, browser



