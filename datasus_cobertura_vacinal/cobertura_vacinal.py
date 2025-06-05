import time
import os, sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.data_utils import load_string_data, save_string_data, compare_data, clear_data_file
from playwright.sync_api import sync_playwright
from datetime import datetime

DATA_FILE = "datasus_cobertura_vacinal/datasus_cobertura_vacinal.yaml"

def access_website(p):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    url = "https://infoms.saude.gov.br/extensions/SEIDIGI_DEMAS_VACINACAO_CALENDARIO_NACIONAL_COBERTURA_RESIDENCIA/SEIDIGI_DEMAS_VACINACAO_CALENDARIO_NACIONAL_COBERTURA_RESIDENCIA.html"
    page.goto(url)
    print(f"Acessando página: {url}")
    preloader_selector = ".preloader"

    try:
        page.wait_for_selector(preloader_selector, timeout=5000)
    except:
        pass

    while True:
        try:
            if not page.is_visible(preloader_selector):
                break
        except:
            break
        page.wait_for_timeout(500)

    return page, browser

def fetch_data(page):
    container_selector = "#kpi-container"
    try:
        page.wait_for_selector(container_selector, timeout=5000)
        container_text = page.query_selector(container_selector).inner_text()

        # Regex para capturar a data no formato dd/mm/yyyy
        match = re.search(r"Atualização do painel em (\d{2}/\d{2}/\d{4})", container_text)
        if match:
            data_atualizacao = match.group(1)
            print(f"Data de atualização extraída: {data_atualizacao}")
            return data_atualizacao
        else:
            print("Data de atualização não encontrada no texto.")
            return None
    except Exception as e:
        print(f"Erro ao extrair data de atualização: {e}")
        return None

def download_cobertura_vacinal(page):
    tab_de_dados_selector = "#aba2-tab"
    page.wait_for_selector(tab_de_dados_selector, timeout=10000)

    tab_de_dados = page.query_selector(tab_de_dados_selector)
    if tab_de_dados:
        tab_de_dados.scroll_into_view_if_needed()
        tab_de_dados.click()
        print("Aba de dados acessada com sucesso!")
    else:
        print("Aba de dados não encontrada!")
        return

    page.wait_for_load_state("networkidle")
    time.sleep(2)

    download_button_selector = "#exportar-dados-QV1-10"
    page.wait_for_selector(download_button_selector, timeout=10000)

    download_button = page.query_selector(download_button_selector)
    if download_button:
        download_button.scroll_into_view_if_needed()

        with page.expect_download() as download_info:
            time.sleep(2.5)
            download_button.click()

        download = download_info.value

        # Nome dinâmico baseado na data
        today = datetime.today()
        filename = f"cobertura_vacinal_{today.year}_{today.month:02d}_{today.day:02d}.csv"
        download_dir = "datasus_cobertura_vacinal"
        os.makedirs(download_dir, exist_ok=True)
        download_path = os.path.join(download_dir, filename)

        download.save_as(download_path)
        print(f"Download salvo em: {download_path}")

    else:
        print("Botão de download não encontrado!")

    page.wait_for_timeout(2000)

def main():
    print(f"Running check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with sync_playwright() as p:
        page, browser = access_website(p)
        current_data = fetch_data(page)

        if not current_data:
            print("No data fetched. Exiting.")
            browser.close()
            return

        stored_data = load_string_data(DATA_FILE)  or []

        differences = compare_data(current_data, stored_data)

        if differences:
            print("New data detected! Proceeding with download.")
            download_cobertura_vacinal(page)
            save_string_data(current_data, DATA_FILE)
        else:
            print("No new data detected.")

        browser.close()

if __name__ == "__main__":
    main()
