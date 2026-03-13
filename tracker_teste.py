import requests
import os

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

url = "https://www.webmotors.com.br/api/search/car"

params = {
    "url": "https://www.webmotors.com.br/carros/estoque/fiat/argo?cidade=Campinas"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(url, params=params, headers=headers)

data = r.json()

carros = data.get("SearchResults", [])

links = []

for c in carros:
    if "Specification" in c:
        id_carro = c["ID"]
        link = f"https://www.webmotors.com.br/comprar/{id_carro}"
        links.append(link)

if links:
    msg = "🚗 Segue a lista de veículos encontrados:\n\n"
    for l in links[:10]:
        msg += l + "\n"
    enviar(msg)
else:
    enviar("⚠️ API retornou zero carros.")
