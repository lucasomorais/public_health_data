import os, sys
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.data_utils import load_list_data, save_list_data, compare_data, clear_data_file
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = "inmet_dados/inmet_dados.yaml"

def fetch_data():
    """Fetch data from the website and return as a list."""
    try:
        response = requests.get("https://portal.inmet.gov.br/dadoshistoricos", timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        data = []
        for article in soup.find_all("article", class_="post-preview"):
            article_data = article.text.strip()
            data.append(article_data)
        return data
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []
    

def main():
    """Main function to fetch, compare, and notify about changes."""
    print(f"Running check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Fetch current data
    current_data = fetch_data()
    if not current_data:
        print("No data fetched. Exiting.")
        return

    # Load stored data
    stored_data = load_list_data(DATA_FILE)

    # Compare and detect changes
    changes = compare_data(current_data, stored_data)

    # Print changes
    if changes:
        print(f"Changes detected: {len(changes)} new items.")
        for change in changes:
            print(change)
        # Atualiza: junta e salva só itens únicos e normalizados
        stored_data = clear_data_file(DATA_FILE)
        updated_data = changes
        save_list_data(updated_data, DATA_FILE)
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
