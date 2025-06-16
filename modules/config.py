HEADLESS = True
DOWNLOADS_DIR = "downloads/"


DENGUE_DATA_FILE = "_tabnet_info/tabnet_dengue.json"
CHIKUNGUNYA_DATA_FILE = "_tabnet_info/tabnet_chikungunya.json"
ZIKA_DATA_FILE = "_tabnet_info/tabnet_zika.json"
AIH_DATA_FILE = "_tabnet_info/tabnet_aih.json"

DENGUE_CONFIGS = {
    "municipio_de_residencia": {
        "DATA_FILE": DENGUE_DATA_FILE,
        "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def",
        "filter": "Município_de_residência",
        "filter_name": "municipio_de_residencia",
        "download_dir": DOWNLOADS_DIR
    },
    "faixa_etaria": {
        "DATA_FILE": DENGUE_DATA_FILE,
        "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def",
        "filter": "Faixa_Etária",
        "filter_name": "faixa_etaria",
        "download_dir": DOWNLOADS_DIR
    },
    "obitos_dengue": {
        "DATA_FILE": DENGUE_DATA_FILE,
        "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def",
        "filter": "Município_de_residência",
        "filter_name": "obitos_dengue",
        "download_dir": DOWNLOADS_DIR,
            "extra_filter": { 
                    "img_id": "fig49",
                    "select_id": "S49",
                    "option_value": "3"
                }
        }
    }

CHIKUNGUNYA_CONFIGS = {
    "municipio_de_residencia": {
        "DATA_FILE": CHIKUNGUNYA_DATA_FILE,
        "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/chikunbr.def",
        "filter": "Município_de_residência",
        "filter_name": "cases_chikungunya",
        "download_dir": DOWNLOADS_DIR
    }
}

ZIKA_CONFIGS = {
    "municipio_de_residencia": {
        "DATA_FILE": ZIKA_DATA_FILE,
        "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/zikabr.def",
        "filter": "Município_de_residência",
        "filter_name": "cases_zika",
        "download_dir": DOWNLOADS_DIR
    }
}



AIH_CONFIGS = [
        {
            "filter_name": "aih_municipio_registro",
            "filtro_L": "Município",
            "filtro_C": "Ano_processamento",
            "filtros_I": "AIH_aprovadas",
            "json_file": "_tabnet_info/aih_municipio_registro.json",
            "download_dir": DOWNLOADS_DIR,
            "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
        },
        {
            "filter_name": "servicos_hospitalares",
            "filtro_L": "Município",
            "filtro_C": "Ano_processamento",
            "filtros_I": "Valor_serviços_hospitalares",
            "json_file": "_tabnet_info/servicos_hospitalares.json",
            "download_dir": DOWNLOADS_DIR,
            "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
        },
        {
            "filter_name": "servicos_profissionais",
            "filtro_L": "Município",
            "filtro_C": "Ano_processamento",
            "filtros_I": "Valor_serviços_profissionais",
            "json_file": "_tabnet_info/servicos_profissionais.json",
            "download_dir": DOWNLOADS_DIR,
            "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
        },
        {
            "filter_name": "servicos_valor_total",
            "filtro_L": "Município",
            "filtro_C": "Ano_processamento",
            "filtros_I": "Valor_total",
            "json_file": "_tabnet_info/servicos_valor_total.json",
            "download_dir": DOWNLOADS_DIR,
            "url": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def"
        }
    ]