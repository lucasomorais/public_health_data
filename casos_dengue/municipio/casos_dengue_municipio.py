import time
import os
import sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.data_utils import load_dict_data, save_dict_data
from playwright.sync_api import sync_playwright
from datetime import datetime

# Agora usamos JSON para armazenar { ano: texto }
DATA_FILE = "casos_dengue/municipio/casos_dengue_municipio.json"
DOWNLOAD_DIR = "casos_dengue/municipio/downloads/"

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
                # Mantém só até a primeira quebra de linha ou asterisco
                texto_limpo = re.split(r'\n|\*', texto)[0].strip()
                # Extrai o ano
                ano_match = re.search(r'20\d{2}', texto_limpo)
                if ano_match:
                    ano = ano_match.group(0)
                    dict_textos[ano] = texto_limpo
        return dict_textos

    print("Elemento rodape_htm não encontrado")
    return {}

def download_casos_dengue(page, changed_years):

    context = page.context

    # 1) Selecionar "Município de residência" (já era feito)
    select_mun_loc = page.locator('select#L')
    select_mun_loc.wait_for()
    select_mun_loc.select_option(value="Município_de_residência")
    print("[INFO] Opção 'Município de residência' selecionada com sucesso.")
    time.sleep(0.5)

    # Localizador do <select> de anos
    select_ano = page.locator('select#A')

    for ano in changed_years:
        # 2) Selecionar somente o ano desejado (pelo label, ex.: "2024")
        select_ano.wait_for()
        select_ano.select_option(label=ano)
        print(f"[INFO] Selecionado ano {ano} no dropdown de períodos.")
        time.sleep(0.3)

        # 3) Clicar em "Mostra" para abrir nova aba
        mostra_button = page.get_by_role("button", name="Mostra")
        mostra_button.scroll_into_view_if_needed()
        with context.expect_page() as new_page_info:
            mostra_button.click()
        new_page = new_page_info.value
        print(f"[INFO] Botão 'Mostra' clicado para o ano {ano}. Nova aba aberta.")

        # 4) Aguarda carregar e rola até o fim para achar o link CSV
        new_page.wait_for_load_state("networkidle")
        print(f"[INFO] Nova aba carregada para o ano {ano}.")
        new_page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight); }")
        time.sleep(1)

        download_button = new_page.locator('td.botao_opcao a', has_text="Copia como .CSV")
        download_button.wait_for(state="attached", timeout=10000)
        download_button.scroll_into_view_if_needed()
        download_button.wait_for(state="visible", timeout=7000)
        print(f"[INFO] Botão 'Copia como .CSV' localizado para o ano {ano}.")

        # 5) Executa o download
        with new_page.expect_download() as download_info:
            download_button.click()
        download = download_info.value

        # 6) Salva o arquivo corretamente nomeado
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        hoje = datetime.today()
        nome_arquivo = f"casos_dengue_{ano}_{hoje.year}_{hoje.month:02d}_{hoje.day:02d}.csv"
        download_path = os.path.join(DOWNLOAD_DIR, nome_arquivo)
        download.save_as(download_path)
        print(f"[INFO] Download do ano {ano} salvo em: {download_path}")

        # 7) Depois de baixar, fechamos a aba para voltar ao formulário
        new_page.close()
        print(f"[INFO] Aba do ano {ano} fechada. Voltando para a página de seleção.\n")
        time.sleep(0.5)

def main():
    print(f"Running check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    with sync_playwright() as p:
        page, browser = access_website(p)

        # 1) Busca os textos atuais
        current_data = fetch_data(page)
        # 2) Carrega o JSON salvo anteriormente (pode vir {} se não existir)
        stored_data = load_dict_data(DATA_FILE)

        # 3) Monta a lista de anos que mudaram
        changed_years = []
        for ano, texto in current_data.items():
            if ano not in stored_data or stored_data[ano] != texto:
                changed_years.append(ano)

        if changed_years:
            print("Novos dados detectados para os anos:", changed_years)
            # Atualiza apenas as chaves/valores que mudaram
            for ano in changed_years:
                stored_data[ano] = current_data[ano]
            # Salva o JSON atualizado
            save_dict_data(stored_data, DATA_FILE)

            # Chama o download apenas para os anos que mudaram
            download_casos_dengue(page, changed_years)
        else:
            print("Nenhuma alteração detectada.\n")

        browser.close()

if __name__ == "__main__":
    main()
