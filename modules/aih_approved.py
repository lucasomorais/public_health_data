import os
from datetime import datetime
from playwright.async_api import async_playwright
from modules.data_utils import load_dict_data, save_dict_data
from modules.config import HEADLESS, DOWNLOADS_DIR

DATA_FILE = "_tabnet_info/tabnet_aih.json"


month_map = {
    "Jan": "01", "Fev": "02", "Mar": "03", "Abr": "04", "Mai": "05", "Jun": "06",
    "Jul": "07", "Ago": "08", "Set": "09", "Out": "10", "Nov": "11", "Dez": "12"
}

# Extrai anos e meses disponíveis no site (ex: {"2025": ["01","02","03"], "2024": ["12"]})
async def extrair_anos_meses(p, filtro):
    browser = await p.chromium.launch(headless=HEADLESS)
    context = await browser.new_context()
    page = await context.new_page()
    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
    await page.goto(url)
    print(f"[INFO] Acessando página para extrair anos/meses: {url}")

    select_mun_loc = page.locator('select#L')
    await select_mun_loc.wait_for()
    await select_mun_loc.select_option(value=filtro)
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

# Ajuste a função de download para iterar ano e mês, e só baixar os que ainda não foram baixados
async def download_casos_aih(p, filtro, current_data, stored_data, download_dir, nome):
    browser = await p.chromium.launch(headless=HEADLESS)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()
    url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
    await page.goto(url)
    print(f"[INFO] Acessando página para filtro '{filtro}': {url}")

    select_mun_loc = page.locator('select#L')
    await select_mun_loc.wait_for()
    await select_mun_loc.select_option(value=filtro)
    await page.wait_for_timeout(500)

    select_ano = page.locator('select#A')
    await select_ano.wait_for()

    options = await select_ano.locator('option').all()
    opcoes_site = [(await opt.text_content()).strip() for opt in options]

    # Iterar por ano e mês
    for ano, meses in current_data.items():
        if ano not in stored_data:
            stored_data[ano] = {}

        for mes in meses:
            # Verifica se já baixou
            if stored_data[ano].get(mes, {}).get("baixado"):
                print(f"[INFO] Já baixado {ano}/{mes}, pulando.")
                continue

            # Monta string do dropdown "MesAbrev/Ano" (ex: "Jan/2025")
            mes_abrev = {v: k for k, v in month_map.items()}[mes]
            opcao_esperada = f"{mes_abrev}/{ano}"

            if opcao_esperada not in opcoes_site:
                print(f"[AVISO] Opção {opcao_esperada} não disponível no site, pulando.")
                continue

            # Seleciona a opção no dropdown
            await select_ano.select_option(label=opcao_esperada)
            print(f"[INFO] Selecionado {opcao_esperada} para download.")

            # Clica no botão mostra, abre nova página etc (mesmo que antes)
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

            # Marca como baixado no dict em memória
            stored_data[ano][mes] = {"baixado": True}

            await page.wait_for_timeout(500)

    await context.close()
    await browser.close()
    print(f"[INFO] Concluído filtro '{nome}' e navegador fechado.\n")

# Função para checar o que precisa baixar e atualizar os dados persistidos
async def check_and_update_aih():
    current_data = None
    stored_data = load_dict_data(DATA_FILE)

    async with async_playwright() as p:
        current_data = await extrair_anos_meses(p, filtro="Município")

        # Se stored_data vazio, inicializa estrutura para meses
        for ano, meses in current_data.items():
            if ano not in stored_data:
                stored_data[ano] = {}
            for mes in meses:
                if mes not in stored_data[ano]:
                    stored_data[ano][mes] = {"baixado": False}

        await download_casos_aih(
            p,
            filtro="Município",
            current_data=current_data,
            stored_data=stored_data,
            download_dir=DOWNLOADS_DIR,
            nome="aih_approved"
        )

    # Salva os dados atualizados (com marcação de downloads feitos)
    save_dict_data(stored_data, DATA_FILE)
    print(f"[INFO] Dados armazenados atualizados.")

