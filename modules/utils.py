import os, time, asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from modules.config import HEADLESS, DOWNLOADS_DIR


folders = [
    "_tabnet_info/",
    DOWNLOADS_DIR
]

def ensure_dir():
    print(f"[INFO] Criando os diretórios {folders} se não existirem.")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        
month_map = {
    "Jan": "01", "Fev": "02", "Mar": "03", "Abr": "04", "Mai": "05", "Jun": "06",
    "Jul": "07", "Ago": "08", "Set": "09", "Out": "10", "Nov": "11", "Dez": "12"
}

async def start_playwright():
    """Inicia o contexto Playwright e retorna o objeto Playwright."""
    async with async_playwright() as p:
        yield p

async def extract_years_months(p, url, filtro_L, filtro_C=None, filtros_I=None, filter_name=None):
    """Extrai anos e meses disponíveis no TabNet para um filter."""
    browser = await p.chromium.launch(headless=HEADLESS)
    context = await browser.new_context()
    filter_name = filter_name
    page = await context.new_page()
    await page.goto(url)

    await page.locator('select#L').select_option(value=filtro_L)
    await page.wait_for_timeout(300)
    if filtro_C:
        await page.locator('select#C').select_option(value=filtro_C)
        await page.wait_for_timeout(300)
    if filtros_I:
        await page.locator('select#I').select_option(value=filtros_I)
        await page.wait_for_timeout(300)

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

####################

async def download_disease_data(p, url, filter, changed_years, download_dir, filter_name, extra_filter=None):
    browser = await p.chromium.launch(headless=HEADLESS)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()
    await page.goto(url)
    print(f"Acessando página para filter '{filter}': {url}")
    
    select_mun_loc = page.locator('select#L')
    await select_mun_loc.wait_for()
    await select_mun_loc.select_option(value=filter)
    print(f"[INFO] Opção '{filter}' selecionada com sucesso.")
    await page.wait_for_timeout(500)

    select_ano = page.locator('select#A')
    available_options = await select_ano.locator('option').all()
    anos_disponiveis = [(await opt.text_content()).strip() for opt in available_options]

    for ano in changed_years:
        await select_ano.wait_for()
        if ano not in anos_disponiveis:
            print(f"[AVISO] Ano {ano} não disponível no dropdown para o filter '{filter_name}'. Pulando...\n")
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
        nome_arquivo = f"{filter_name}_{ano}_{hoje.year}_{hoje.month:02d}_{hoje.day:02d}.csv"
        download_path = os.path.join(download_dir, nome_arquivo)
        await download.save_as(download_path)
        print(f"[INFO] Download salvo: {download_path}")

        await new_page.close()
        print(f"[INFO] Aba do ano {ano} fechada.\n")
        time.sleep(0.5)

    await context.close()
    await browser.close()
    print(f"[INFO] Concluído filter '{filter_name}' e navegador fechado.\n")


####################

async def baixar_dados_tabnet(p, url, config, current_data, stored_data=None, extra_filter=None):
    """Baixa dados do TabNet em CSV para os períodos especificados."""
    browser = await p.chromium.launch(headless=HEADLESS)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()
    await page.goto(url)
    print(f"[INFO] Acessando página: {url}")

    await page.locator('select#L').select_option(value=config["filtro_L"])
    await page.wait_for_timeout(300)
    if config.get("filtro_C"):
        await page.locator('select#C').select_option(value=config["filtro_C"])
        await page.wait_for_timeout(300)
    if config.get("filtros_I"):
        await page.locator('select#I').select_option(value=config["filtros_I"])
        await page.wait_for_timeout(300)

    if extra_filter:
        print(f"[INFO] Aplicando filtro extra: {extra_filter}")
        if "img_id" in extra_filter:
            await page.locator(f'img#{extra_filter["img_id"]}').click()
            await page.wait_for_timeout(300)
        if "select_id" in extra_filter and "option_value" in extra_filter:
            await page.locator(f'select#{extra_filter["select_id"]}').select_option(value=extra_filter["option_value"])
            await page.wait_for_timeout(300)

    select_ano = page.locator('select#A')
    await select_ano.wait_for()
    opcoes_site = [(await opt.text_content()).strip() for opt in await select_ano.locator('option').all()]

    if stored_data is None:
        stored_data = {}

    for ano in current_data:
        if isinstance(current_data, dict):
            meses = current_data.get(ano, [])
            if ano not in stored_data:
                stored_data[ano] = {}
        else:
            meses = [None]
            if ano not in stored_data:
                stored_data[ano] = None

        for mes in meses if meses else [None]:
            if mes and stored_data.get(ano, {}).get(mes, {}).get("baixado") == True:
                continue

            opcao_esperada = f"{[k for k, v in month_map.items() if v == mes][0]}/{ano}" if mes else ano
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

            MAX_RETRIES = 3
            for attempt in range(MAX_RETRIES):
                try:
                    download_button = new_page.locator('td.botao_opcao a', has_text="Copia como .CSV")
                    await download_button.wait_for(state="visible", timeout=10000)
                    await download_button.scroll_into_view_if_needed()

                    async with new_page.expect_download() as download_info:
                        await download_button.click()
                    download = await download_info.value

                    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
                    hoje = datetime.today()
                    nome_arquivo = f"{config['filter_name']}_{ano}_{mes or ''}_{hoje.year}_{hoje.month:02d}_{hoje.day:02d}.csv"
                    download_path = os.path.join(DOWNLOADS_DIR, nome_arquivo)
                    await download.save_as(download_path)
                    print(f"[INFO] Download salvo: {download_path}")

                    await new_page.close()
                    print(f"[INFO] Aba do {'mês ' + mes + '/' if mes else ''}{ano} fechada.\n")

                    if mes:
                        stored_data[ano][mes] = {"baixado": True}
                    else:
                        stored_data[ano] = {"baixado": True}
                    await page.wait_for_timeout(500)
                    break

                except Exception as e:
                    print(f"[ERRO] Tentativa {attempt + 1} falhou para {'mês ' + mes + '/' if mes else ''}{ano}: {e}")
                    if attempt == MAX_RETRIES - 1:
                        print(f"[FALHA] Todas as tentativas falharam para {'mês ' + mes + '/' if mes else ''}{ano}. Pulando.")
                    else:
                        await asyncio.sleep(2)
                        
    await context.close()
    await browser.close()
    print(f"[INFO] Concluído filter '{config['filter_name']}' e navegador fechado.\n")
    return stored_data