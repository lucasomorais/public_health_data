# Projetos de Automação de Dados - Documentação

Este repositório contém três scripts de automação para extração, comparação e download de dados públicos de diferentes fontes brasileiras. Todos eles utilizam funções comuns de manipulação de dados (load/save/compare) definidas no módulo `data_utils`.

---

## Módulo `data_utils`

Este módulo contém funções genéricas para carregar, salvar, limpar e comparar dados em diferentes formatos: JSON, YAML com listas e strings. É utilizado pelos scripts para armazenar dados localmente e detectar mudanças entre execuções.

### Funções principais

- **load_dict_data(data_file)**  
  Carrega dados de um arquivo JSON e retorna um dicionário. Retorna `{}` se não existir ou ocorrer erro.

- **save_dict_data(data, data_file)**  
  Salva um dicionário em arquivo JSON formatado.

- **load_list_data(data_file)**  
  Carrega uma lista armazenada em YAML. Retorna lista vazia se não existir ou erro.

- **save_list_data(data, data_file)**  
  Salva uma lista em arquivo YAML.

- **load_string_data(data_file)**  
  Carrega uma string armazenada em YAML. Retorna `None` se não existir ou erro.

- **save_string_data(data, data_file)**  
  Salva uma string em arquivo YAML.

- **compare_data(new_data, stored_data)**  
  Compara dados novos com dados armazenados e retorna as diferenças (lista vazia se igual).

- **clear_data_file(data_file)**  
  Limpa o conteúdo do arquivo indicado.

---

## Script 1: Casos de Dengue (`casos_dengue.py`)

Automatiza a extração e download de dados anuais de casos de dengue do site do Datasus.

### Fluxo principal

1. **Acesso ao site:** navega até o formulário de casos de dengue.
2. **Extração de dados:** lê textos de rodapé que indicam os dados disponíveis por ano.
3. **Comparação:** verifica anos com dados novos ou atualizados em relação ao JSON salvo.
4. **Download:** para cada ano com dados novos, seleciona o ano no formulário, abre uma nova aba, baixa CSV, salva localmente e fecha a aba.
5. **Armazena** as informações atualizadas em JSON.

### Tecnologias

- Playwright (navegação e download)
- JSON para armazenamento de metadados
- Regex para limpeza e extração de texto

---

## Script 2: Cobertura Vacinal (`cobertura_vacinal.py`)

Automatiza a verificação e download do painel de cobertura vacinal no site do Datasus.

### Fluxo principal

1. **Acesso ao site:** abre o painel de cobertura vacinal.
2. **Espera o carregamento:** aguarda o fim da animação de carregamento (preloader).
3. **Extração da data de atualização:** captura a data exibida no painel via regex.
4. **Comparação:** verifica se a data atual difere da última salva no arquivo YAML.
5. **Download:** caso haja dados novos, acessa a aba correta e baixa o arquivo CSV, salvando com nome baseado na data atual.
6. **Armazena** a nova data no arquivo YAML.

### Tecnologias

- Playwright para interação web e download
- YAML para armazenamento da data de atualização
- Regex para captura da data no texto

---

## Script 3: Dados Meteorológicos INMET (`inmet_dados.py`)

Coleta dados históricos do portal do INMET via scraping simples e detecta atualizações.

### Fluxo principal

1. **Requisição HTTP:** busca o HTML da página de dados históricos do INMET.
2. **Parsing HTML:** usa BeautifulSoup para extrair o texto dos artigos listados.
3. **Comparação:** verifica se os dados atuais diferem dos armazenados no YAML.
4. **Atualização:** se houver novidades, limpa o arquivo e salva os novos dados.
5. **Log:** imprime no console as mudanças detectadas.

### Tecnologias

- Requests para HTTP
- BeautifulSoup para parsing HTML
- YAML para armazenamento de listas

---

## Considerações

Os scripts são independentes, mas compartilham o módulo data_utils para persistência e comparação.

O uso de arquivos JSON ou YAML depende do tipo de dado (dicionário, lista ou string).

O foco é detectar mudanças para evitar downloads ou operações desnecessárias.