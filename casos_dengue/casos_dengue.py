import time
import os, sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.data_utils import load_list_data, save_list_data, compare_data, clear_data_file
from playwright.sync_api import sync_playwright
from datetime import datetime

DATA_FILE = "casos_dengue/casos_dengue.yaml"  # ajuste o caminho conforme desejar

def access_website(p):
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def"
    page.goto(url)
    print(f"Acessando página: {url}")

    return page, browser

def fetch_data(page):
    rodape = page.query_selector("div.rodape_htm")
    if rodape:
        rodape.scroll_into_view_if_needed()
        
        itens = rodape.query_selector_all("ol > li")
        
        lista_textos = []
        for item in itens:
            texto = item.inner_text().strip()
            if texto.startswith("Dados de 20"):
                # Mantém só até a primeira quebra de linha ou asterisco
                texto_limpo = re.split(r'\n|\*', texto)[0].strip()
                lista_textos.append(texto_limpo)
        
        return lista_textos
    else:
        print("Elemento rodape_htm não encontrado")
        return []


def download_casos_dengue(page):
    




def main():

    print(f"Running check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with sync_playwright() as p:
        page, browser = access_website(p)
        current_data = fetch_data(page)
        browser.close()

        stored_data = load_list_data(DATA_FILE)

        differences = compare_data(current_data, stored_data)

        if differences:
            print("New data detected! Proceeding with download.")
            print(f"Differences found: {differences}")
            save_list_data(current_data, DATA_FILE)
        else:
            print("No changes detected.")

        browser.close()

if __name__ == "__main__":
    main()
