from playwright.async_api import async_playwright
from modules.data_utils import load_dict_data, save_dict_data
from modules.config import ZIKA_CONFIGS
from modules.utils import download_disease_data

async def filtros_zika(changed_years, current_data):
    """Process the changed years by downloading data and updating stored data."""
    async with async_playwright() as p:
        config = next(iter(ZIKA_CONFIGS.values()))
        await download_disease_data(
            p,
            url=config["url"],
            filter=config["filter"],
            changed_years=changed_years,
            download_dir=config["download_dir"],
            filter_name=config["filter_name"]
        )


    # Update stored data with the current data provided by main.py
    stored_data = load_dict_data(config["DATA_FILE"])
    for ano in changed_years:
        if ano in current_data:
            stored_data[ano] = current_data[ano]
    save_dict_data(stored_data, config["DATA_FILE"])
    print(f"[INFO] Dados armazenados atualizados para os anos: {changed_years}")