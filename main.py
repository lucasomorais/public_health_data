from datetime import datetime
from playwright.sync_api import sync_playwright
from modules.data_utils import load_dict_data, save_dict_data
from modules.status import append_status_entry
import re

DATA_FILE = "_tabnet_info/casos_dengue.json"

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
        else:
            print("Nenhuma alteração detectada.\n")

if __name__ == "__main__":
    main()
