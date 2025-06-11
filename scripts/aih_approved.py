import os
from datetime import datetime
from playwright.async_api import async_playwright
from modules.data_utils import load_dict_data, save_dict_data
from modules.config import HEADLESS, DOWNLOADS_DIR

month_map = {
    "Jan": "01", "Fev": "02", "Mar": "03", "Abr": "04", "Mai": "05", "Jun": "06",
    "Jul": "07", "Ago": "08", "Set": "09", "Out": "10", "Nov": "11", "Dez": "12"
}

async def extrair_anos_meses(p, filtro):
    browser = await p.chromium.launch(headless=HEADLESS)
    context = await browser.new_context()
    page = await context.new_page()
    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
    await page.goto(url)
    print(f"[INFO] Acessando página para extrair anos/meses: {url}")

    await page.locator('select#L').select_option(value=filtro)
    await page.wait_for_timeout(500)

    select_ano = page.locator('select#A')
    await select_ano.wait_for()

    options = await select_ano.locator('option').all()
    ano_mes_dict = {}

    for option in options:
        text = (await option.text_content()).strip()
        if "/" not in text:
            continue
        mes_abrev, ano = text.split("/")
        mes_abrev = mes_abrev.strip()
        ano = ano.strip()

        if mes_abrev in month_map:
            mes_num = month_map[mes_abrev]
            if ano not in ano_mes_dict:
                ano_mes_dict[ano] = []
            if mes_num not in ano_mes_dict[ano]:
                ano_mes_dict[ano].append(mes_num)

    await browser.close()
    print(f"[INFO] Extração concluída: anos encontrados: {list(ano_mes_dict.keys())}")
    return ano_mes_dict

async def download_casos_aih(p, filtro_L, filtro_C, filtros_I, current_data, stored_data, download_dir, nome):
    browser = await p.chromium.launch(headless=HEADLESS)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()
    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
    await page.goto(url)
    print(f"[INFO] Acessando página: {url}")

    await page.locator('select#L').select_option(value=filtro_L)
    await page.locator('select#C').select_option(value=filtro_C)
    await page.wait_for_timeout(500)

    await page.locator('select#I').select_option(value=filtros_I)

    select_ano = page.locator('select#A')
    await select_ano.wait_for()
    opcoes_site = [(await opt.text_content()).strip() for opt in await select_ano.locator('option').all()]

    for ano, meses in current_data.items():
        if ano not in stored_data:
            stored_data[ano] = {}

        for mes in meses:
            if stored_data.get(ano, {}).get(mes, {}).get("baixado") == True:
                continue

            mes_abrev = {v: k for k, v in month_map.items()}[mes]
            opcao_esperada = f"{mes_abrev}/{ano}"

            if opcao_esperada not in opcoes_site:
                print(f"[AVISO] Opção {opcao_esperada} não disponível no site, pulando.")
                continue

            await select_ano.select_option(label=opcao_esperada)
            print(f"[INFO] Selecionado {opcao_esperada} para download.")

            mostra_button = page.get_by_role("button", name="Mostra")
            await mostra_button.scroll_into_view_if_needed()

            async with context.expect_page() as new_page_info:
                await mostra_button.click()
            new_page = await new_page_info.value

            await new_page.wait_for_load_state("networkidle")
            await new_page.evaluate("() => { window.scrollTo(0, document.body.scrollHeight); }")
            await new_page.wait_for_timeout(1000)

            download_button = new_page.locator('td.botao_opcao a', has_text="Copia como .CSV")
            await download_button.wait_for(state="visible", timeout=7000)
            await download_button.scroll_into_view_if_needed()

            async with new_page.expect_download() as download_info:
                await download_button.click()
            download = await download_info.value

            os.makedirs(download_dir, exist_ok=True)
            hoje = datetime.today()
            nome_arquivo = f"{nome}_{ano}_{mes}_{hoje.year}_{hoje.month:02d}_{hoje.day:02d}.csv"
            download_path = os.path.join(download_dir, nome_arquivo)
            await download.save_as(download_path)
            print(f"[INFO] Download salvo: {download_path}")

            await new_page.close()
            print(f"[INFO] Aba do mês {mes}/{ano} fechada.\n")

            stored_data[ano][mes] = {"baixado": True}
            await page.wait_for_timeout(500)

    await context.close()
    await browser.close()
    print(f"[INFO] Concluído filtro '{nome}' e navegador fechado.\n")

async def check_and_update_aih_por_filtro(config):
    stored_data = load_dict_data(config["json_file"])
    async with async_playwright() as p:
        current_data = await extrair_anos_meses(p, filtro=config["filtro_L"])

        for ano, meses in current_data.items():
            if ano not in stored_data:
                stored_data[ano] = {}
            for mes in meses:
                if mes not in stored_data[ano]:
                    stored_data[ano][mes] = {"baixado": False}

        await download_casos_aih(
            p,
            filtro_L=config["filtro_L"],
            filtro_C=config["filtro_C"],
            filtros_I=config["filtros_I"],
            current_data=current_data,
            stored_data=stored_data,
            download_dir=config["download_dir"],
            nome=config["nome"]
        )

    save_dict_data(stored_data, config["json_file"])

async def check_all_filtros_aih():
    filtros = [
        {
            "nome": "aih_municipio_registro",
            "filtro_L": "Município",
            "filtro_C": "Ano_processamento",
            "filtros_I": "AIH_aprovadas",
            "json_file": "_tabnet_info/aih_municipio_registro.json",
            "download_dir": DOWNLOADS_DIR
        },
        {
            "nome": "servicos_hospitalares",
            "filtro_L": "Município",
            "filtro_C": "Ano_processamento",
            "filtros_I": "Valor_serviços_hospitalares",
            "json_file": "_tabnet_info/servicos_hospitalares.json",
            "download_dir": DOWNLOADS_DIR
        },
        {
            "nome": "servicos_profissionais",
            "filtro_L": "Município",
            "filtro_C": "Ano_processamento",
            "filtros_I": "Valor_serviços_profissionais",
            "json_file": "_tabnet_info/servicos_profissionais.json",
            "download_dir": DOWNLOADS_DIR
        },
        {
            "nome": "servicos_valor_total",
            "filtro_L": "Município",
            "filtro_C": "Ano_processamento",
            "filtros_I": "Valor_total",
            "json_file": "_tabnet_info/servicos_valor_total.json",
            "download_dir": DOWNLOADS_DIR
        }
    ]

    for config in filtros:
        await check_and_update_aih_por_filtro(config)



