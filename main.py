import pandas as pd
import requests

numero_de_paginas = 3

near_earth_objects = []

for numero in range(1, numero_de_paginas + 1):
    url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?page={numero}&api_key=bBmv3zSftdRt8VReZqaRbpUQFvOLBnxcHcUxhbb9"
    response = requests.get(url)
    json = response.json()
    near_earth_objects += json["near_earth_objects"]


#%% 

close_approach_date_list = []

for item in near_earth_objects:
    if "close_approach_data" in item:
        close_approach_date_list.append((item["id"], item["close_approach_data"]))
        del item["close_approach_data"]

df = pd.json_normalize(near_earth_objects, sep='_')

#%%

perigosos = df["is_potentially_hazardous_asteroid"]

print("PERIGOSOS!!!")
print(perigosos.value_counts())

#%% Criar dataframe de distâncias de avistamento

linhas = []

for id_asteroid, list_approach in close_approach_date_list:
    for item in list_approach:
        item["id"] = id_asteroid
        linhas.append(item)
        
df_approach = pd.json_normalize(linhas, sep='_')

#%% imprimir estatisticas de avistamento sobre os asteroides perigosos

# Identificar as linhas de asteroides perigosos

id_perigosos = list(df["id"][perigosos])
perigosos_approach = df_approach["id"].apply(lambda x: x in id_perigosos)

# Selecionar as linhas de asteroides perigosos

df_approach_p = df_approach[:][perigosos_approach]

# Calcular media e desvio padrao da distancia do avistamento em km

distancias = df_approach_p["miss_distance_kilometers"]

# Deixar valores em float

distancias = distancias.apply(float)

print(distancias.describe())

#%% Transformar data de aproximacao em datetime

import datetime

def str_to_date(data):
    if data != data:
        return data
    return datetime.datetime.strptime(data, '%Y-%m-%d')

df_approach["close_approach_date"] = df_approach["close_approach_date"].apply(str_to_date)

#%%

# Definir intervalo

inicio = datetime.datetime.strptime('1994-01-01', '%Y-%m-%d')
fim = datetime.datetime.strptime('2012-01-01', '%Y-%m-%d')

intervalo = (inicio <= df_approach["close_approach_date"]) & (df_approach["close_approach_date"] < fim)

# Filtrar amostras para o intervalo

df_approach_intervalo = df_approach[:][intervalo]

# Criar uma coluna só com o numero do ano

df_approach_intervalo["year"] = df_approach["close_approach_date"].apply(lambda x: x.year)

# agrupar

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
