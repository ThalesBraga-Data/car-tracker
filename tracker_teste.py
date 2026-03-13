import requests
import os
from bs4 import BeautifulSoup

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL_BASE = "https://www.webmotors.com.br"

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

headers = {"User-Agent": "Mozilla/5.0"}

urls = [
    "https://www.webmotors.com.br/carros/estoque/fiat/argo?cidade=Campinas",
    "https://www.webmotors.com.br/carros/estoque/peugeot/208?cidade=Campinas"
]

links = []

for url in urls:
    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    carros = soup.find_all("a")

    for c in carros:
        link = c.get("href")
        if link and "/comprar/" in link:
            full_link = URL_BASE + link
            links.append(full_link)

links = list(set(links))

if links:
    mensagem = "🚗 Segue a lista de veículos encontrados:\n\n"

    for l in links[:20]:
        mensagem += l + "\n"

    enviar(mensagem)

else:
    enviar("⚠️ Nenhum veículo encontrado no scraping.")
