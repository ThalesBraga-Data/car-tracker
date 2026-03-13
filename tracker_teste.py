import requests
import os
from bs4 import BeautifulSoup

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

url = "https://www.webmotors.com.br/carros/estoque/fiat/argo?cidade=Campinas"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Connection": "keep-alive"
}

r = requests.get(url, headers=headers)

soup = BeautifulSoup(r.text, "html.parser")

links = []

for a in soup.find_all("a", href=True):
    if "/comprar/" in a["href"]:
        links.append("https://www.webmotors.com.br" + a["href"])

links = list(set(links))

if links:
    msg = "🚗 Segue a lista de veículos encontrados:\n\n"
    for l in links[:10]:
        msg += l + "\n"
    enviar(msg)
else:
    enviar("⚠️ Nenhum veículo encontrado no scraping.")
