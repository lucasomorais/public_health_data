import time
import os
from datetime import datetime
from playwright.async_api import async_playwright
from modules.data_utils import load_dict_data, save_dict_data
from modules.config import HEADLESS, DOWNLOADS_DIR

DATA_FILE = "_tabnet_info/tabnet_dengue.json"

async def download_casos_dengue(p, filtro, changed_years, download_dir, extra_filter, nome):
    browser = await p.chromium.launch(headless=HEADLESS)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()
    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def"
    await page.goto(url)
    print(f"Acessando página para filtro '{filtro}': {url}")

    select_mun_loc = page.locator('select#L')
    await select_mun_loc.wait_for()
    await select_mun_loc.select_option(value=filtro)
    print(f"[INFO] Opção '{filtro}' selecionada com sucesso.")
    await page.wait_for_timeout(500)

    if extra_filter:
        await page.click(f"img#{extra_filter['img_id']}")
        await page.wait_for_timeout(300)
        select_extra = page.locator(f"select#{extra_filter['select_id']}")
        await select_extra.select_option(value=extra_filter["option_value"])
        print(f"[INFO] Filtro extra aplicado: {extra_filter['option_value']}")
        await page.wait_for_timeout(500)


    select_ano = page.locator('select#A')

    for ano in changed_years:
        await select_ano.wait_for()
        await select_ano.select_option(label=ano)
        print(f"[INFO] Selecionado ano {ano} no dropdown de períodos.")
        time.sleep(0.3)

        mostra_button = page.get_by_role("button", name="Mostra")
        await mostra_button.scroll_into_view_if_needed()

        async with context.expect_page() as new_page_info:
            await mostra_button.click()
        new_page = await new_page_info.value

        await new_page.wait_for_load_state("networkidle")
        await new_page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight); }")
        time.sleep(1)

        download_button = new_page.locator('td.botao_opcao a', has_text="Copia como .CSV")
        await download_button.wait_for(state="visible", timeout=7000)
        await download_button.scroll_into_view_if_needed()

        async with new_page.expect_download() as download_info:
            await download_button.click()
        download = await download_info.value

        os.makedirs(download_dir, exist_ok=True)
        hoje = datetime.today()
        nome_arquivo = f"{nome}_{ano}_{hoje.year}_{hoje.month:02d}_{hoje.day:02d}.csv"
        download_path = os.path.join(download_dir, nome_arquivo)
        await download.save_as(download_path)
        print(f"[INFO] Download salvo: {download_path}")

        await new_page.close()
        print(f"[INFO] Aba do ano {ano} fechada.\n")
        time.sleep(0.5)

    await context.close()
    await browser.close()
    print(f"[INFO] Concluído filtro '{nome}' e navegador fechado.\n")

async def filtros_dengue(changed_years, current_data):
    """Process the changed years by downloading data and updating stored data."""
    async with async_playwright() as p:
        filtros = [
            {"nome": "municipio_de_residencia", "filtro": "Município_de_residência", "download_dir": DOWNLOADS_DIR} ,    #MUNICIPIO DE RESIDENCIA
            {"nome": "faixa_etaria", "filtro": "Faixa_Etária", "download_dir": DOWNLOADS_DIR},             #FAIXA ETARIA
            {"nome": "obitos_dengue", "filtro": "Município_de_residência", "download_dir": DOWNLOADS_DIR,   #ÓBITO PELO AGRAVO NOTIFICADO
                "extra_filter": { 
                    "img_id": "fig49",
                    "select_id": "S49",
                    "option_value": "3"
                }
            }
        ]

        for config in filtros:
            await download_casos_dengue(
                p,
                filtro=config["filtro"],
                changed_years=changed_years,
                download_dir=DOWNLOADS_DIR,
                extra_filter=config.get("extra_filter"),
                nome=config["nome"]
            )

    # Update stored data with the current data provided by main.py
    stored_data = load_dict_data(DATA_FILE)
    for ano in changed_years:
        if ano in current_data:
            stored_data[ano] = current_data[ano]
    save_dict_data(stored_data, DATA_FILE)
    print(f"[INFO] Dados armazenados atualizados para os anos: {changed_years}")