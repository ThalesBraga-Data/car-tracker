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

payload = {
    "Page": 1,
    "PageSize": 20,
    "Sort": "Relevance",
    "Filter": {
        "Make": "FIAT",
        "Model": "ARGO",
        "City": "Campinas"
    }
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

r = requests.post(url, json=payload, headers=headers)

print("Status:", r.status_code)
print(r.text[:500])

try:
    data = r.json()
except:
    enviar("❌ API não retornou JSON")
    exit()

carros = data.get("SearchResults", [])

links = []

for c in carros:
    id_carro = c.get("ID")
    if id_carro:
        links.append(f"https://www.webmotors.com.br/comprar/{id_carro}")

if links:
    msg = "🚗 Segue a lista de veículos encontrados:\n\n"
    for l in links[:10]:
        msg += l + "\n"
    enviar(msg)
else:
    enviar("⚠️ API retornou 0 carros.")
