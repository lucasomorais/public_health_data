# Sistema de Download de Dados de Saúde do TabNet

Este projeto automatiza o download de dados de saúde do site TabNet do DATASUS usando Playwright. Ele verifica dados já baixados, baixa apenas os novos ou atualizados em formato CSV e organiza os arquivos em um diretório específico. Suporta múltiplos tipos de dados, como casos de dengue, chikungunya, zika, AIH aprovadas, médicos por especialidade e agentes médicos.

## Funcionalidades Principais

- Verifica dados disponíveis no site contra os armazenados localmente.
- Baixa apenas dados novos ou atualizados, evitando duplicatas.
- Organiza os arquivos CSV em um diretório dedicado.
- Usa JSONs para controle de versões e períodos baixados.

## Requisitos

- Python 3.7 ou superior
- Playwright
- PyYAML

## Instalação

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```bash
   python main.py
   ```

## Estrutura do Projeto

- **`main.py`**: Ponto de entrada que coordena a execução.
- **`scripts/`**: Scripts específicos para cada tipo de dado (ex.: `casos_dengue.py`).
- **`modules/`**: Módulos utilitários (ex.: `json_utils.py`, `config.py`).
- **`utils.py`**: Funções reutilizáveis para navegação e download.
- **`_tabnet_info/`**: Diretório para JSONs de controle.
- **`downloads/`**: Diretório para os arquivos CSV baixados.

## Detalhes dos Módulos e Funções

### `main.py`
- **Localização**: Raiz do projeto
- **Descrição**: Script principal que inicia o Playwright e gerencia a execução dos processos de download.
- **Funções**:
  - `ensure_dir()`: Cria os diretórios `_tabnet_info/` e `downloads/` se não existirem.
  - `main()`: Função assíncrona que inicia o Playwright, cria um contexto de navegador e chama funções de processamento de dados (ex.: `check_all_filtros_medical_agent()`).

### `scripts/casos_dengue.py`
- **Localização**: Pasta `scripts/`
- **Descrição**: Processa dados de casos de dengue.
- **Funções**:
  - `processar_filtros_dengue(changed_years, current_data)`: Extrai e baixa dados de dengue para os anos/meses especificados, atualizando o JSON de controle.

### `scripts/casos_chikungunya.py`
- **Localização**: Pasta `scripts/`
- **Descrição**: Processa dados de casos de chikungunya.
- **Funções**:
  - `processar_filtros_chikungunya(changed_years, current_data)`: Similar ao script de dengue, mas para chikungunya.

### `scripts/casos_zika.py`
- **Localização**: Pasta `scripts/`
- **Descrição**: Processa dados de casos de zika.
- **Funções**:
  - `processar_filtros_zika(changed_years, current_data)`: Similar ao script de dengue, mas para zika.

### `scripts/aih_approved.py`
- **Localização**: Pasta `scripts/`
- **Descrição**: Gerencia dados de AIH aprovadas.
- **Funções**:
  - `check_and_update_aih_por_filtro(config)`: Verifica e baixa dados de AIH para um filter específico.
  - `check_all_filtros_aih()`: Coordena a execução para todos os filters de AIH.

### `scripts/ftmedicSpecialty.py`
- **Localização**: Pasta `scripts/`
- **Descrição**: Gerencia dados de médicos por especialidade.
- **Funções**:
  - `check_and_update_medicos_por_filtro(config)`: Verifica e baixa dados para um filter de médicos.
  - `check_all_filtros_medicos()`: Coordena a execução para todos os filters de médicos.

### `scripts/ftmedicalAgent.py`
- **Localização**: Pasta `scripts/`
- **Descrição**: Gerencia dados de agentes médicos (ativo por padrão).
- **Funções**:
  - `check_and_update_medical_agent(config)`: Verifica e baixa dados para um filter de agentes médicos.
  - `check_all_filtros_medical_agent()`: Coordena a execução para todos os filters de agentes médicos.

### `modules/json_utils.py`
- **Localização**: Pasta `modules/`
- **Descrição**: Funções para buscar e gerenciar dados do site.
- **Funções**:
  - `fetch_data(page, url)`: Extrai informações do rodapé do TabNet.
  - `extract_date(texto)`: Extrai datas de textos do site.
  - `check_and_update(page, url, data_file, filtro_func, disease_name)`: Compara dados locais com o site e atualiza se necessário, chamando a função de filter correspondente.

### `modules/config.py`
- **Localização**: Pasta `modules/`
- **Descrição**: Define configurações globais.
- **Variáveis**:
  - `HEADLESS`: Define se o navegador roda sem interface gráfica (True/False).
  - `DOWNLOADS_DIR`: Caminho para o diretório de downloads.

### `modules/data_utils.py`
- **Localização**: Pasta `modules/`
- **Descrição**: Funções utilitárias para manipulação de dados.
- **Funções**:
  - Carrega e salva dados em JSON e YAML.
  - Compara e atualiza informações entre dados locais e do site.

### `utils.py`
- **Localização**: Raiz do projeto
- **Descrição**: Centraliza funções reutilizáveis.
- **Funções**:
  - `start_playwright()`: Inicia o Playwright e retorna um contexto de navegador.
  - `extract_years_months(p, url, filtro_L, filtro_C=None, filtros_I=None)`: Extrai anos e meses disponíveis no TabNet para um filter.
  - `download_disease_data(p, url, config, current_data, stored_data=None, extra_filter=None)`: Navega no site, aplica filters e baixa os dados em CSV.

## Como Funciona

1. O `main.py` cria diretórios e inicia o Playwright.
2. Chama funções como `check_all_filtros_medical_agent()` para processar cada tipo de dado.
3. Essas funções verificam os períodos disponíveis no site, comparam com os JSONs locais e baixam os dados pendentes via `download_disease_data()`.
4. Os CSVs são salvos em `downloads/` e os JSONs em `_tabnet_info/` são atualizados.

