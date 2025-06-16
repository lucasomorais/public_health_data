import re
from modules.data_utils import load_dict_data, save_dict_data

DATA_FILE = "_tabnet_info/sidra_status.json"
URL_SIDRA = "https://sidra.ibge.gov.br/tabela/7167"  # substitua se necessário

async def fetch_data_sidra(page, url):
    await page.goto(url)
    await page.wait_for_selector(".lv-block", timeout=10000)

    itens = await page.query_selector_all(".item-lista")
    dict_textos = {}

    for item in itens:
        ano_el = await item.query_selector(".name")
        sufixo_el = await item.query_selector(".sufixo-periodo")

        if not ano_el or not sufixo_el:
            continue

        ano = (await ano_el.inner_text()).strip()
        sufixo = (await sufixo_el.inner_text()).strip()
        data = re.search(r"\d{2}/\d{2}/\d{4}", sufixo)
        data_str = data.group(0) if data else "data desconhecida"

        texto = f"Dados de {ano} atualizados em {data_str}."
        dict_textos[ano] = texto

    return dict_textos

def extract_date(texto):
    """Extrai a primeira data no formato dd/mm/aaaa de um texto."""
    match = re.search(r'\d{2}/\d{2}/\d{4}', texto)
    return match.group(0) if match else None

async def check_and_update_sidra():
    from modules.utils import start_playwright

    print("\n=== Iniciando verificação de atualização para SIDRA ===")
    url = "https://sidra.ibge.gov.br/tabela/7167"

    async for p in start_playwright():
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        data = await fetch_data_sidra(page, url)
        print(f"[INFO] Dados atuais coletados: {len(data)} anos encontrados.")

        stored_data = load_dict_data(DATA_FILE)
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
            print(f"\n[RESULTADO] Novos dados do SIDRA detectados para os anos: {changed_years}")
        else:
            print(f"[RESULTADO] Nenhuma alteração de SIDRA detectada.")

        for ano in changed_years:
            stored_data[ano] = data[ano]

        if changed_years:
            save_dict_data(stored_data, DATA_FILE)
            print(f"[SUCESSO] Dados do SIDRA armazenados atualizados.")

        await browser.close()