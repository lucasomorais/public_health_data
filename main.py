import asyncio
import re
import os
from datetime import datetime
from playwright.async_api import async_playwright
from modules.data_utils import load_dict_data
from modules.status import append_status_entry
from modules.casos_dengue import filtros_dengue
from modules.casos_chikungunya import filtros_chikungunya


DATA_FILE = "_tabnet_info/tabnet_data.json"

folders = [
    "_tabnet_info/",
    "casos_dengue/",
    "casos_chikungunya/",
    "casos_dengue/obitos_dengue_downloads/",
    "casos_dengue/faixa_etaria_dengue_downloads/",
    "casos_dengue/municipio_dengue_downloads/"
    "casos_chikungunya/municipio_chikungunya_downloads/",
]

def ensure_dir():
    print(f"[INFO] Criando os diretórios {folders} se não existirem.")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    


async def fetch_data(page):
    rodape = await page.query_selector("div.rodape_htm")
    if not rodape:
        print("Elemento rodape_htm não encontrado")
        return {}

    await rodape.scroll_into_view_if_needed()
    itens = await rodape.query_selector_all("ol > li")
    dict_textos = {}

    for item in itens:
        texto = await item.inner_text()
        texto = texto.strip()
        if texto.startswith("Dados de 20"):
            texto_limpo = re.split(r'\n|\*', texto)[0].strip()
            ano_match = re.search(r'20\d{2}', texto_limpo)
            if ano_match:
                ano = ano_match.group(0)
                dict_textos[ano] = texto_limpo
    return dict_textos

async def main():
    print(f"Rodando checagem em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    ensure_dir()
    async with async_playwright() as p:
        temp_browser = await p.chromium.launch(headless=True)
        temp_context = await temp_browser.new_context()
        temp_page = await temp_context.new_page()
        await temp_page.goto("http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def")
        current_data = await fetch_data(temp_page)
        await temp_browser.close()

        stored_data = load_dict_data(DATA_FILE)

        changed_years = []
        for ano, texto in current_data.items():
            if ano not in stored_data or stored_data[ano] != texto:
                changed_years.append(ano)

        append_status_entry(changed_years)

        if changed_years:
            print("Novos dados detectados para os anos:", changed_years)
            await filtros_dengue(changed_years, current_data)
            print("Dados de dengue atualizados com sucesso.\n")
            await filtros_chikungunya(changed_years, current_data)
            print("Dados de chikungunya atualizados com sucesso.\n")
        else:
            print("Nenhuma alteração detectada.\n")

if __name__ == "__main__":
    asyncio.run(main())