import pandas as pd
import requests

#%% Importar dados usando a lib requests via método GET para API da nasa.

numero_de_paginas = 3

near_earth_objects = []

for numero in range(1, numero_de_paginas + 1):
    url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?page={numero}&api_key=bBmv3zSftdRt8VReZqaRbpUQFvOLBnxcHcUxhbb9"
    response = requests.get(url)
    json = response.json()
    near_earth_objects += json["near_earth_objects"]


#%% Extrair a lista de aproximações de cada asteróide.

# Criar uma lista para receber os dados de aproximação de cada asteróide.
close_approach_date_list = []

for item in near_earth_objects:
    if "close_approach_data" in item:
        # O item close_approach_data é uma lista de dicionários de dados de aproximação
        close_approach_date_list.append((item["id"], item["close_approach_data"]))
        # Deletar essa lista do dicionário near_earth_objects, pra não ficar em df
        del item["close_approach_data"]

# Gerar uma dataframe com os dados de aproximação, a função json_normalize é 
# usada para fazer um "flat" no dicionário, fazendo com que todos os subdicionarios
# sejam trazidos para o primeiro nível, o novo nome será key_keyInterna
df = pd.json_normalize(near_earth_objects, sep='_')

#%% Número de objetos perigosos a terra;

# A série is_potentially_hazardous_asteroid é booleana, True ou False
perigosos = df["is_potentially_hazardous_asteroid"]

print("PERIGOSOS!!!")
print(perigosos.value_counts())

#%% Criar dataframe de distâncias de avistamento

# Implementar um "flat" manualmente, adicionar o ID do asteróide na lista de 
# Avistamentos, porque antes isso era descoberto por hierarquia, mas agora,
# os dados de avistamento de todos os asteróides estão misturados.
# Para saber a origem, foi adicionado o campo "id" para rastrear o asteróide.
linhas = []

for id_asteroid, list_approach in close_approach_date_list:
    for item in list_approach:
        item["id"] = id_asteroid
        linhas.append(item)
        
# linhas é uma lista com dicionários que contém subdicionários, também é necessário
# achatar os dicionários para ficar todos no primeiro nível.
df_approach = pd.json_normalize(linhas, sep='_')

#%% imprimir estatisticas de avistamento sobre os asteroides perigosos

# Criar uma lista com o id dos asteróides perigosos

id_perigosos = list(df["id"][perigosos])

# Para cada avistamento no dataframe df_approach verificar se o seu id
# está na lista dos id_perigosos, isso gera uma série booleana
perigosos_approach = df_approach["id"].apply(lambda x: x in id_perigosos)

# Selecionar as linhas de asteroides perigosos

df_approach_p = df_approach[:][perigosos_approach]

# Guardar a coluna miss_distance_kilometers em uma variavel

distancias = df_approach_p["miss_distance_kilometers"]

# Transformar todos os valores da série distancias em float

distancias = distancias.apply(float)

# Imprimir a descrição estatística de distâncias dos objetos perigosos e a terra

print(distancias.describe())

#%% Transformar data de aproximacao em datetime

import datetime

def str_to_date(data):
    # Se for nan ele entra no if e retorna a própria entrada
    if data != data:
        return data
    # Transformar data de avistamento str em um objeto de datetime
    return datetime.datetime.strptime(data, '%Y-%m-%d')

# Aplicar str_to_date sobre a coluna close_approach_date do dataframe df_approach
df_approach["close_approach_date"] = df_approach["close_approach_date"].apply(str_to_date)

#%% Histograma mostrando quantos objetos perigosos tiveram aproximações com a terra por ano

# Definir intervalo

inicio = datetime.datetime.strptime('1994-01-01', '%Y-%m-%d')
fim = datetime.datetime.strptime('2012-01-01', '%Y-%m-%d')

# Gerar uma série booleana informando se a linha está ou não no intervalo de data desejado

intervalo = (inicio <= df_approach["close_approach_date"]) & (df_approach["close_approach_date"] < fim)

# Filtrar amostras dentro do intervalo

df_approach_intervalo = df_approach[:][intervalo]

# Criar uma coluna só com o numero do ano

df_approach_intervalo["year"] = df_approach["close_approach_date"].apply(lambda x: x.year)

# Imprimir histograma

grupo = df_approach_intervalo[["id", "year"]]

grupo.hist(bins=18)

#%% Histograma de tamanhos de objetos que são perigosos;

df_perigosos = df[:][perigosos]
df_nao_perigosos = df[:][~perigosos]

# Criar dataframe só com id e diametro estimado maximo

df_diametro_periogos = df_perigosos[["id", "estimated_diameter_kilometers_estimated_diameter_max"]]
df_diametro_nao_periogos = df_nao_perigosos[["id", "estimated_diameter_kilometers_estimated_diameter_max"]]

# Histograma de tamanhos de objetos que são perigosos;

df_diametro_periogos.hist()

# Histograma de tamanhos de objetos não perigosos;

df_diametro_nao_periogos.hist()
