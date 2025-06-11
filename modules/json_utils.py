import json
import os
import re
from datetime import datetime
from modules.data_utils import load_dict_data


STATUS_FILE = "_tabnet_info/status.json"

DEFAULT_SCRIPTS = [
    "casos_dengue.py",
    "casos_chikungunya.py",
    "casos_zika.py"
]


########## FETCH DATA ##########

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

########## CHECK IF DATA HAS CHANGED ##########

def extract_date(texto):
    """Extrai a primeira data no formato dd/mm/aaaa de um texto."""
    match = re.search(r'\d{2}/\d{2}/\d{4}', texto)
    return match.group(0) if match else None

async def check_and_update(page, url, data_file, filtro_func, doença_nome):
    print(f"\n=== Iniciando verificação de atualização para {doença_nome} ===")
    print(f"[INFO] Carregando dados da página: {url}")
    
    data = await fetch_data(page, url)
    print(f"[INFO] Dados atuais coletados: {len(data)} anos encontrados.")

    stored_data = load_dict_data(data_file)
    print(f"[INFO] Dados armazenados carregados: {len(stored_data)} anos registrados.")

    changed_years = []

    print("\n[INFO] Comparando datas de atualização por ano:")
    for ano, texto_atual in data.items():
        data_atual = extract_date(texto_atual)
        texto_anterior = stored_data.get(ano)
        data_anterior = extract_date(texto_anterior) if texto_anterior else None

        print(f"  - Ano {ano}:")
        print(f"    → Texto atual    : '{texto_atual}'")
        print(f"    → Data extraída  : {data_atual}")
        print(f"    → Texto anterior : '{texto_anterior}'")
        print(f"    → Data armazenada: {data_anterior}")

        if data_atual != data_anterior:
            print(f"    → ⚠️ Detecção de mudança na data para o ano {ano}")
            changed_years.append(ano)
        else:
            print(f"    → ✅ Sem alterações detectadas no ano {ano}")

    if changed_years:
        print(f"\n[RESULTADO] Novos dados de {doença_nome} detectados para os anos: {changed_years}")
        await filtro_func(changed_years, data)
        print(f"[SUCESSO] Dados de {doença_nome} atualizados com sucesso.\n")
    else:
        print(f"[RESULTADO] Nenhuma alteração de {doença_nome} detectada.\n")

#########################

