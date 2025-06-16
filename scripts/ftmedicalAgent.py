from modules.data_utils import load_dict_data, save_dict_data
from modules.config import DOWNLOADS_DIR
from modules.utils import extract_years_months, download_disease_data, start_playwright


async def check_and_update_medical_agent(config):
    """Verifica e atualiza dados de agentes médicos para um filter específico."""
    stored_data = load_dict_data(config["json_file"])
    async for p in start_playwright():
        current_data = await extract_years_months(p, config["url"], config["filtro_L"], config["filtro_C"], config["filtros_I"])
        for ano, meses in current_data.items():
            if ano not in stored_data:
                stored_data[ano] = {}
            for mes in meses:
                if mes not in stored_data[ano]:
                    stored_data[ano][mes] = {"baixado": False}

        stored_data = await download_disease_data(p, config["url"], config, current_data, stored_data, config.get("extra_filter"))
        save_dict_data(stored_data, config["json_file"])

async def check_all_filtros_medical_agent():
    """Coordena a execução de todos os filters de agentes médicos."""
    configs = [
        {
            "name": "profissionais_de_saude",
            "filtro_L": "Município",
            "filtro_C": "Profissionais_selecionados",
            "filtros_I": "Total",
            "json_file": "_tabnet_info/profissionais_de_saude.json",
            "download_dir": DOWNLOADS_DIR,
            "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?cnes/cnv/proc02br.def"
        },
        {
            "name": "agente_comunitario_de_saude",
            "filtro_L": "Município",
            "filtro_C": "--Não-Ativa--",
            "filtros_I": "Total",
            "json_file": "_tabnet_info/agente_comunitario_de_saude.json",
            "download_dir": DOWNLOADS_DIR,
            "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?cnes/cnv/proc02br.def",
            "extra_filter": {
                "img_id": "fig27",
                "select_id": "S27",
                "option_value": "2"
            }
        }  
    ]

    for config in configs:
        await check_and_update_medical_agent(config)