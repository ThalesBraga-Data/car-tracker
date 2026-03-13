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

url = "https://www.webmotors.com.br/carros/estoque/fiat/argo?tipoveiculo=carros&cidade=Campinas"

headers = {"User-Agent": "Mozilla/5.0"}

r = requests.get(url, headers=headers)

soup = BeautifulSoup(r.text, "html.parser")

carros = soup.find_all("a")

links = []

for c in carros:
    link = c.get("href")
    if link and "/comprar/" in link:
        links.append("https://www.webmotors.com.br" + link)

links = list(set(links))

if links:
    enviar("🚗 Carros encontrados:")
    for l in links[:5]:
        enviar(l)
else:
    enviar("Nenhum carro encontrado agora.")
