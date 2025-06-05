import yaml
import os
import yaml
import os

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





