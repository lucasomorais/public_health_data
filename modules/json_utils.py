import json
import os
import re
from datetime import datetime
from data_utils import load_dict_data

STATUS_FILE = "_tabnet_info/status.json"

DEFAULT_SCRIPTS = [
    "casos_dengue_municipio",
]

def load_status_log():
    if not os.path.exists(STATUS_FILE):
        return []
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_status_log(log_data):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

def append_status_entry(changed_years):
    timestamp = datetime.now().isoformat()
    changed = bool(changed_years)

    entry = {
        "timestamp": timestamp,
        "changed": changed,
        "changed_years": changed_years,
        "scripts": {key: changed for key in DEFAULT_SCRIPTS}
    }

    log = load_status_log()
    log.append(entry)
    save_status_log(log)

def get_latest_status():
    log = load_status_log()
    if log:
        return log[-1]
    return None


# FETCH DATA FUNCTION

async def fetch_data(page, url):
    await page.goto(url)
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

    #CHECK IF THE DATA HAS CHANGED

async def check_update_and_download(page, url, data_file, filtro_func, doença_nome):
    data = await fetch_data(page, url)
    stored_data = load_dict_data(data_file)
    changed_years = [ano for ano, texto in data.items() if ano not in stored_data or stored_data[ano] != texto]
    append_status_entry(changed_years)

    if changed_years:
        print(f"Novos dados de {doença_nome} detectados para os anos:", changed_years)
        await filtro_func(changed_years, data)
        print(f"Dados de {doença_nome} atualizados com sucesso.\n")
    else:
        print(f"Nenhuma alteração de {doença_nome} detectada.\n")
