from modules.data_utils import load_dict_data, save_dict_data
from modules.config import AIH_CONFIGS
from modules.utils import extract_years_months, baixar_dados_tabnet, start_playwright


async def check_and_update_aih_por_filtro(config):
    """Verifica e atualiza dados de AIH para um filter específico."""
    stored_data = load_dict_data(config["json_file"])
    async for p in start_playwright():
        current_data = await extract_years_months(p, config["url"], config["filtro_L"], config["filtro_C"], config["filtros_I"])
        for ano, meses in current_data.items():
            if ano not in stored_data:
                stored_data[ano] = {}
            for mes in meses:
                if mes not in stored_data[ano]:
                    stored_data[ano][mes] = {"baixado": False}

        stored_data = await baixar_dados_tabnet(p, config["url"], config, current_data, stored_data)
        save_dict_data(stored_data, config["json_file"])

async def check_all_filtros_aih():
    """Coordena a execução de todos os filters de AIH."""
    configs = AIH_CONFIGS
    for config in configs:
        await check_and_update_aih_por_filtro(config)