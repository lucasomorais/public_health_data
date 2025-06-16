import json, os , yaml
from datetime import datetime


def load_dict_data(data_file):
    """Load stored dict data from the JSON file."""
    try:
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return {}

def save_dict_data(data, data_file):
    """Save dict data to the JSON file with newer years and months first."""
    try:
        # Ordena os anos do mais recente para o mais antigo
        sorted_data = dict(sorted(data.items(), key=lambda x: int(x[0]), reverse=True))

        # Para cada ano, ordena os meses também do mais recente para o mais antigo
        for ano in sorted_data:
            if isinstance(sorted_data[ano], dict):
                sorted_data[ano] = dict(sorted(
                    sorted_data[ano].items(),
                    key=lambda x: int(x[0]),
                    reverse=True
                ))

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error saving JSON file: {e}")


def compare_and_update(current_data, stored_data):
    """
    Compare current and stored dicts.
    Update stored_data with any new or changed entries.
    Returns: (updated: bool, updated_data: dict)
    """
    updated = False

    for ano, texto in current_data.items():
        if ano not in stored_data or stored_data[ano] != texto:
            print(f"[INFO] Ano {ano} atualizado: '{stored_data.get(ano)}' → '{texto}'")
            stored_data[ano] = texto
            updated = True

    return updated, stored_data

def load_string_data(data_file):
    """Load stored data from the JSON file."""
    try:
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
        return None
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def save_string_data(data, data_file):
    """Save data and timestamp to a JSON file."""
    try:
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y - %H:%M")
        obj = {
            "data": data,
            "saved_at": timestamp
        }
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving JSON file: {e}")

def load_list_data(data_file):
    """Load stored list data from the YAML file."""
    try:
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if isinstance(data, list):
                    if all(isinstance(x, list) for x in data):
                        return data[-1]
                    return data
                return []
        return []
    except yaml.YAMLError as e:
        print(f"Error loading YAML file: {e}")
        return []

def save_list_data(data, data_file):
    """Save list data to the YAML file (overwrite, no nesting)."""
    try:
        with open(data_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True)
    except yaml.YAMLError as e:
        print(f"Error saving YAML file: {e}")