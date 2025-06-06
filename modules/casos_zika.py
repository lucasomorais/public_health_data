import time
import os
from datetime import datetime
from playwright.async_api import async_playwright
from modules.data_utils import load_dict_data, save_dict_data

DATA_FILE = "_tabnet_info/tabnet_data.json"

async def download_casos_chikungunya(p, filtro, changed_years, download_dir, nome):
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()
    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/chikunbr.def"
    await page.goto(url)
    print(f"Acessando página para filtro '{filtro}': {url}")
    await page.pause()
    select_mun_loc = page.locator('select#L')
    await select_mun_loc.wait_for()
    await select_mun_loc.select_option(value=filtro)
    print(f"[INFO] Opção '{filtro}' selecionada com sucesso.")
    await page.wait_for_timeout(500)

    select_ano = page.locator('select#A')

    available_options = await select_ano.locator('option').all()
    anos_disponiveis = [(await opt.text_content()).strip() for opt in available_options]

    for ano in changed_years:
        await select_ano.wait_for()

        if ano not in anos_disponiveis:
            print(f"[AVISO] Ano {ano} não disponível no dropdown para o filtro '{nome}'. Pulando...\n")
            continue

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
        nome_arquivo = f"casos_chikungunya_{nome}_{ano}_{hoje.year}_{hoje.month:02d}_{hoje.day:02d}.csv"
        download_path = os.path.join(download_dir, nome_arquivo)
        await download.save_as(download_path)
        print(f"[INFO] Download salvo: {download_path}")

        await new_page.close()
        print(f"[INFO] Aba do ano {ano} fechada.\n")
        time.sleep(0.5)

    await context.close()
    await browser.close()
    print(f"[INFO] Concluído filtro '{nome}' e navegador fechado.\n")

async def filtros_chikungunya(changed_years, current_data):
    """Process the changed years by downloading data and updating stored data."""
    async with async_playwright() as p:
        filtros = [
            {"nome": "Casos Chikungunya", "filtro": "Município_de_residência", "download_dir": "casos_chikungunya/municipio_chikungunya_downloads/"} 
        ]
        for config in filtros:
            await download_casos_chikungunya(
                p,
                filtro=config["filtro"],
                changed_years=changed_years,
                download_dir=config["download_dir"],
                nome=config["nome"]
            )

    # Update stored data with the current data provided by main.py
    stored_data = load_dict_data(DATA_FILE)
    for ano in changed_years:
        if ano in current_data:
            stored_data[ano] = current_data[ano]
    save_dict_data(stored_data, DATA_FILE)
    print(f"[INFO] Dados armazenados atualizados para os anos: {changed_years}")