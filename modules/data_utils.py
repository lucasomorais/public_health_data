import yaml
import os
import yaml
import os
import json

####################################

# GLOBAL

def compare_data(new_data, stored_data):
    """Compare new data with stored data and return differences."""
    if stored_data is None:
        return [new_data]  # Se não há nada armazenado, considerar tudo novo
    return [] if (new_data) == (stored_data) else [new_data]

def clear_data_file(data_file):
    """Clear the YAML data file."""
    try:
        with open(data_file, "w", encoding="utf-8") as f:
            f.write("")  # limpa o conteúdo
    except Exception as e:
        print(f"Error clearing data file: {e}")

####################################
# JSON DATA HANDLING FUNCTIONS
####################################

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
    """Save dict data to the JSON file."""
    try:
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
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

def clear_data_file(data_file):
    """Clear the JSON data file."""
    try:
        with open(data_file, "w", encoding="utf-8") as f:
            f.write("")  # limpa o conteúdo
    except Exception as e:
        print(f"Error clearing data file: {e}")



#  STRING DATA HANDLING FUNCTIONS

def load_string_data(data_file):
    """Load stored data from the YAML file."""
    try:
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                # Garantir que é uma string, se não, converter ou retornar None
                if isinstance(data, str):
                    return data
                else:
                    # Se for None ou outro tipo, retornar None para forçar nova captura
                    return None
        return None
    except yaml.YAMLError as e:
        print(f"Error loading YAML file: {e}")
        return None

def save_string_data(data, data_file):
    """Save data to the YAML file."""
    try:
        # Salvar direto a string (data), não lista
        with open(data_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True)
    except yaml.YAMLError as e:
        print(f"Error saving YAML file: {e}")



####################################

#  LIST DATA HANDLING FUNCTIONS

def load_list_data(data_file):
    """Load stored list data from the YAML file."""
    try:
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                # Se carregou como lista de listas, pega só a última.
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





