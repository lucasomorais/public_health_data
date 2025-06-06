import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright
from modules.data_utils import check_update_and_download
from modules.casos_dengue import filtros_dengue
from modules.casos_chikungunya import filtros_chikungunya
from modules.casos_zika import filtros_zika


# Data files separados
DENGUE_DATA_FILE = "_tabnet_info/tabnet_dengue.json"
CHIKUNGUNYA_DATA_FILE = "_tabnet_info/tabnet_chikungunya.json"
ZIKA_DATA_FILE = "_tabnet_info/tabnet_zika.json"

# Pastas necessárias
folders = [
    "_tabnet_info/",
    "casos_dengue/",
    "casos_chikungunya/",
    "casos_zika/",
    "casos_dengue/obitos_dengue_downloads/",
    "casos_dengue/faixa_etaria_dengue_downloads/",
    "casos_dengue/municipio_dengue_downloads/",
    "casos_chikungunya/municipio_chikungunya_downloads/",
    "casos_chikungunya/municipio_zika_downloads/",
]

def ensure_dir():
    print(f"[INFO] Criando os diretórios {folders} se não existirem.")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

async def main():
    print(f"Rodando checagem em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    ensure_dir()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await check_update_and_download(
            page,
            url="http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def",
            data_file=DENGUE_DATA_FILE,
            filtro_func=filtros_dengue,
            doença_nome="dengue"
        )

        await check_update_and_download(
            page,
            url="http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/chikunbr.def",
            data_file=CHIKUNGUNYA_DATA_FILE,
            filtro_func=filtros_chikungunya,
            doença_nome="chikungunya"
        )

        await check_update_and_download(
            page,
            url="http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/chikunbr.def",
            data_file=ZIKA_DATA_FILE,
            filtro_func=filtros_zika,
            doença_nome="zika"
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
