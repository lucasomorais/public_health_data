import time
import os
import sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from playwright.sync_api import sync_playwright
from modules.data_utils import load_dict_data, save_dict_data
from modules.status import append_status_entry

DATA_FILE = "_tabnet_info/casos_dengue.json"

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
    if not rodape:
        print("Elemento rodape_htm não encontrado")
        return {}

    rodape.scroll_into_view_if_needed()
    itens = rodape.query_selector_all("ol > li")
    dict_textos = {}

    for item in itens:
        texto = item.inner_text().strip()
        if texto.startswith("Dados de 20"):
            # Pega só a parte limpa antes de \n ou *
            texto_limpo = re.split(r'\n|\*', texto)[0].strip()
            ano_match = re.search(r'20\d{2}', texto_limpo)
            if ano_match:
                ano = ano_match.group(0)
                dict_textos[ano] = texto_limpo
    return dict_textos

def download_casos_dengue(p, filtro, changed_years, download_dir):
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def"
    page.goto(url)
    print(f"Acessando página para filtro '{filtro}': {url}")

    select_mun_loc = page.locator('select#L')
    select_mun_loc.wait_for()
    # Seleciona o filtro corretamente pelo valor esperado no select
    select_mun_loc.select_option(value=filtro)
    print(f"[INFO] Opção '{filtro}' selecionada com sucesso.")
    time.sleep(0.5)

    select_ano = page.locator('select#A')

    for ano in changed_years:
        select_ano.wait_for()
        select_ano.select_option(label=ano)
        print(f"[INFO] Selecionado ano {ano} no dropdown de períodos.")
        time.sleep(0.3)

        mostra_button = page.get_by_role("button", name="Mostra")
        mostra_button.scroll_into_view_if_needed()

        with context.expect_page() as new_page_info:
            mostra_button.click()
        new_page = new_page_info.value

        new_page.wait_for_load_state("networkidle")
        new_page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight); }")
        time.sleep(1)

        download_button = new_page.locator('td.botao_opcao a', has_text="Copia como .CSV")
        download_button.wait_for(state="visible", timeout=7000)
        download_button.scroll_into_view_if_needed()

        with new_page.expect_download() as download_info:
            download_button.click()
        download = download_info.value

        os.makedirs(download_dir, exist_ok=True)
        hoje = datetime.today()
        nome_arquivo = f"casos_dengue_{filtro}_{ano}_{hoje.year}_{hoje.month:02d}_{hoje.day:02d}.csv"
        download_path = os.path.join(download_dir, nome_arquivo)
        download.save_as(download_path)
        print(f"[INFO] Download salvo: {download_path}")

        new_page.close()
        print(f"[INFO] Aba do ano {ano} fechada.\n")
        time.sleep(0.5)

    context.close()
    browser.close()
    print(f"[INFO] Concluído filtro '{filtro}' e navegador fechado.\n")


def main():
    print(f"Rodando checagem em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    with sync_playwright() as p:
        # Carrega dados para detectar anos com mudanças
        temp_browser = p.chromium.launch(headless=False)
        temp_context = temp_browser.new_context()
        temp_page = temp_context.new_page()
        temp_page.goto("http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def")
        current_data = fetch_data(temp_page)
        temp_browser.close()

        stored_data = load_dict_data(DATA_FILE)

        changed_years = []
        for ano, texto in current_data.items():
            if ano not in stored_data or stored_data[ano] != texto:
                changed_years.append(ano)

        append_status_entry(changed_years)

        if changed_years:
            print("Novos dados detectados para os anos:", changed_years)

            filtros = [
                {"filtro": "Município_de_residência", "download_dir": "casos_dengue/municipio_downloads/"},
                {"filtro": "Faixa_Etária", "download_dir": "casos_dengue/faixa_etaria_downloads/"}
            ]

            for config in filtros:
                download_casos_dengue(
                    p,
                    filtro=config["filtro"],
                    changed_years=changed_years,
                    download_dir=config["download_dir"]
                )

            for ano in changed_years:
                stored_data[ano] = current_data[ano]
            save_dict_data(stored_data, DATA_FILE)
        else:
            print("Nenhuma alteração detectada.\n")



if __name__ == "__main__":
    main()
