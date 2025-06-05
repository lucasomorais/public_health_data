import time
import os
import sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.data_utils import (
    load_dict_data,
    save_dict_data,
    compare_and_update,
    clear_data_file
)
from playwright.sync_api import sync_playwright
from datetime import datetime

DATA_FILE = "casos_dengue/casos_dengue.json"  # agora JSON
DOWNLOAD_DIR = "casos_dengue/downloads/"

def access_website(p):
    browser = p.chromium.launch(headless=True)
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
        
        dict_textos = {}
        for item in itens:
            texto = item.inner_text().strip()
            if texto.startswith("Dados de 20"):
                texto_limpo = re.split(r'\n|\*', texto)[0].strip()
                ano_match = re.search(r'20\d{2}', texto_limpo)
                if ano_match:
                    ano = ano_match.group(0)
                    dict_textos[ano] = texto_limpo
        
        return dict_textos
    else:
        print("Elemento rodape_htm não encontrado")
        return {}

def download_casos_dengue(page):
    context = page.context

    select_locator = page.locator('select#L')
    option_value = "Município_de_residência"
    select_locator.wait_for()  # espera até o <select> existir
    select_locator.select_option(value=option_value)
    print("[INFO] Opção 'Município de residência' selecionada com sucesso.")
    time.sleep(0.5)

    mostra_button = page.get_by_role("button", name="Mostra")
    mostra_button.scroll_into_view_if_needed()

    with context.expect_page() as new_page_info:
        mostra_button.click()
    new_page = new_page_info.value
    print("[INFO] Botão 'Mostra' clicado e nova aba aberta.")

    new_page.wait_for_load_state("networkidle")
    print("[INFO] Nova aba carregada.")

    new_page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight); }")
    time.sleep(1)

    download_button = new_page.locator('td.botao_opcao a', has_text="Copia como .CSV")
    download_button.wait_for(state="attached", timeout=10000)
    download_button.scroll_into_view_if_needed()
    download_button.wait_for(state="visible", timeout=7000)
    print("[INFO] Botão de download 'Copia como .CSV' localizado com sucesso.")

    with new_page.expect_download() as download_info:
        download_button.click()
    download = download_info.value

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    hoje = datetime.today()
    nome_arquivo = f"cobertura_vacinal_{hoje.year}_{hoje.month:02d}_{hoje.day:02d}.csv"
    download_path = os.path.join(DOWNLOAD_DIR, nome_arquivo)
    download.save_as(download_path)
    print(f"[INFO] Download salvo em: {download_path}")

def main():
    print(f"Running check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with sync_playwright() as p:
        page, browser = access_website(p)

        current_data = fetch_data(page)
        stored_data = load_dict_data(DATA_FILE)

        updated, new_data = compare_and_update(current_data, stored_data)

        if updated:
            print("Novos dados detectados! Baixando CSV e atualizando arquivo.")
            save_dict_data(new_data, DATA_FILE)
            download_casos_dengue(page)
        else:
            print("Nenhuma alteração detectada.")

        browser.close()

if __name__ == "__main__":
    main()
