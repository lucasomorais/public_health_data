from playwright.sync_api import sync_playwright
import time
import os
from datetime import datetime

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()      # Cria um contexto (aba) para controlar abas
        page = context.new_page()

        url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def"
        page.goto(url)

        # Selecionar a opção "Município de residência"
        select_locator = page.locator('select#L')
        option_value = "Município_de_residência"
        select_locator.wait_for()
        select_locator.select_option(value=option_value)
        print("Opção 'Município de residência' selecionada com sucesso.")
        time.sleep(1)
        page.pause()
        # Preparar para captura da nova aba aberta após clicar em "Mostra"
        mostra_button = page.get_by_role("button", name="Mostra")
        mostra_button.scroll_into_view_if_needed()

        with context.expect_page() as new_page_info:
            mostra_button.click()  # Clica uma vez aqui, aguarda nova aba abrir

        new_page = new_page_info.value
        print("Botão 'Mostra' clicado e nova aba aberta.")

        new_page.wait_for_load_state("networkidle")
        print("Nova aba carregada.")

        # Localizar o botão de download "Copia como .CSV" na nova aba
        download_button = new_page.locator('td.botao_opcao a', has_text="Copia como .CSV")
        download_button.wait_for(state="visible", timeout=10000)
        download_button.scroll_into_view_if_needed()
        print("Botão de download 'Copia como .CSV' localizado com sucesso.")

        # Preparar para capturar o download
        with new_page.expect_download() as download_info:
            download_button.click()

        download = download_info.value

        # Criar pasta para salvar o arquivo
        download_dir = "casos_dengue/downloads/"
        os.makedirs(download_dir, exist_ok=True)

        today = datetime.today()
        filename = f"cobertura_vacinal_{today.year}_{today.month:02d}_{today.day:02d}.csv"
        download_path = os.path.join(download_dir, filename)

        download.save_as(download_path)
        print(f"Download salvo em: {download_path}")

        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    run()
