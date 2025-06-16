import asyncio
from datetime import datetime
from modules.json_utils import check_and_update
from modules.config import HEADLESS, DENGUE_CONFIGS, CHIKUNGUNYA_CONFIGS, ZIKA_CONFIGS
from scripts.casos_dengue import filtros_dengue
from scripts.casos_chikungunya import filtros_chikungunya
from scripts.casos_zika import filtros_zika
from scripts.aih_approved import check_all_filtros_aih
from scripts.ftmedicSpecialty import check_all_filtros_medicos
from scripts.ftmedicalAgent import check_all_filtros_medical_agent
from scripts.sidra_status import check_and_update_sidra
from modules.utils import start_playwright, ensure_dir

dengue_cfgs = DENGUE_CONFIGS 
chikun_cfgs = CHIKUNGUNYA_CONFIGS
zika_cfgs = ZIKA_CONFIGS



async def main():
    print(f"Rodando checagem em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    ensure_dir()

    async for p in start_playwright():
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        page = await context.new_page()
        
        
        ### DENGUE ###
        for cfgs in dengue_cfgs.values():
            await check_and_update(
                page=page,
                url=cfgs["url"],
                data_file=cfgs["DATA_FILE"],
                filtro_func=filtros_dengue,
                filter_name=cfgs["filter_name"]
            )

        ### CHIKUN ###
        for cfgs in chikun_cfgs.values():
            await check_and_update(
                page=page,
                url=cfgs["url"],
                data_file=cfgs["DATA_FILE"],
                filtro_func=filtros_chikungunya,
                filter_name=cfgs["filter_name"]
            )

        ### ZIKA ###
        for cfgs in zika_cfgs.values():
            await check_and_update(
                page=page,
                url=cfgs["url"],
                data_file=cfgs["DATA_FILE"],
                filtro_func=filtros_zika,
                filter_name=cfgs["filter_name"]
            )

        await check_all_filtros_aih()

        #await check_all_filtros_medicos()

        #await check_all_filtros_medical_agent()

        #await check_and_update_sidra()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())