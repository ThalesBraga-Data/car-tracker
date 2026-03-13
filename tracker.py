import requests
import os
from bs4 import BeautifulSoup
import json

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
URL_BASE = "https://www.webmotors.com.br"

# Filtros configuráveis
filtros = [
    {
        "marca": "fiat",
        "modelo": "argo",
        "ano_min": 2020,
        "ano_max": 2026
    },
    {
        "marca": "peugeot",
        "modelo": "208",
        "ano_min": 2022,
        "ano_max": 2026
    }
]

CIDADE = "Campinas"
RAIO = 100
KM_MIN = 1000
KM_MAX = 50000
PRECO_MAX = 62000
VENDEDORES = ["concessionária", "loja"]

ARQUIVO_CACHE = "veiculos_encontrados.json"

# Função de envio Telegram
def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# Carregar cache de anúncios já enviados
try:
    with open(ARQUIVO_CACHE, "r") as f:
        enviados = json.load(f)
except FileNotFoundError:
    enviados = []

novos_enviados = []

# Função que busca carros
def buscar_carros(marca, modelo):
    url = f"{URL_BASE}/carros/estoque/{marca}/{modelo}?tipoveiculo=carros&cidade={CIDADE}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        enviar(f"Erro ao acessar Webmotors: {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    carros = soup.find_all("a")
    resultados = []

    for c in carros:
        link = c.get("href")
        if link and "/comprar/" in link:
            full_link = URL_BASE + link
            # Evitar duplicidade
            if full_link not in enviados:
                resultados.append(full_link)
    return resultados

# Rodar para cada filtro
for f in filtros:
    encontrados = buscar_carros(f["marca"], f["modelo"])
    if encontrados:
        enviar(f"🚗 Novos anúncios de {f['marca'].capitalize()} {f['modelo'].capitalize()}:")
        for link in encontrados[:5]:
            enviar(link)
            novos_enviados.append(link)

# Atualizar cache
if novos_enviados:
    enviados.extend(novos_enviados)
    with open(ARQUIVO_CACHE, "w") as f:
        json.dump(enviados, f)
