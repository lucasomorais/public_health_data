from modules.data_utils import load_dict_data, save_dict_data
from modules.config import DOWNLOADS_DIR
from modules.utils import extract_years_months, download_disease_data, start_playwright


async def check_and_update_medicos_por_filtro(config):
    """Verifica e atualiza dados de médicos para um filter específico."""
    stored_data = load_dict_data(config["json_file"])
    async for p in start_playwright():
        current_data = await extract_years_months(p, config["url"], config["filtro_L"], config["filtro_C"], config["filtros_I"])
        for ano, meses in current_data.items():
            if ano not in stored_data:
                stored_data[ano] = {}
            for mes in meses:
                if mes not in stored_data[ano]:
                    stored_data[ano][mes] = {"baixado": False}

        stored_data = await download_disease_data(p, config["url"], config, current_data, stored_data, name=config["name"] )
        save_dict_data(stored_data, config["json_file"])

async def check_all_filtros_medicos():
    """Coordena a execução de todos os filters de médicos."""
    configs = [
        {
            "name": "medicos_municipio",
            "filtro_L": "Município",
            "filtro_C": "Médicos",
            "filtros_I": "Quantidade",
            "json_file": "_tabnet_info/medicos_municipio.json",
            "download_dir": DOWNLOADS_DIR,
            "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?cnes/cnv/prid02br.def"
        },
        {
            "name": "medicos_sus_municipio",
            "filtro_L": "Município",
            "filtro_C": "Atende_no_SUS",
            "filtros_I": "Quantidade",
            "json_file": "_tabnet_info/medicos_sus_municipio.json",
            "download_dir": DOWNLOADS_DIR,
            "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?cnes/cnv/prid02br.def"
        }
    ]

    for config in configs:
        await check_and_update_medicos_por_filtro(config)