import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URLS = [
    # Argo 2020
    "https://www.webmotors.com.br/carros/sp-campinas/fiat/argo/de.2020?tipoveiculo=carros&localizacao=-22.9099384%2C-47.0626332x100km&estadocidade=S%C3%A3o%20Paulo-Campinas&marca1=FIAT&modelo1=ARGO&kmde=999&kmate=50000&anunciante=Concession%C3%A1ria%7CLoja&o=5&page=1&anode=2020&precoate=62000",
    # Peugeot 208 2022
    "https://www.webmotors.com.br/carros/sp/peugeot/208/de.2022?tipoveiculo=carros&estadocidade=S%C3%A3o%20Paulo&marca1=Peugeot&modelo1=208&kmde=999&kmate=50000&anunciante=Concession%C3%A1ria%7CLoja&page=1&anode=2022&precoate=62000"
]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

async def buscar_carros():
    todos_carros = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for url in URLS:
            await page.goto(url)
            # Scroll até carregar todos os carros
            previous_height = None
            while True:
                height = await page.evaluate("document.body.scrollHeight")
                if previous_height == height:
                    break
                previous_height = height
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)  # espera carregar novos anúncios

            # Pega todos os links
            elementos = await page.query_selector_all("a[href*='/comprar/']")
            for e in elementos:
                link = await e.get_attribute("href")
                if link:
                    todos_carros.append("https://www.webmotors.com.br" + link)
        await browser.close()
    return list(set(todos_carros))

async def main():
    carros = await buscar_carros()
    if carros:
        msg = "🚗 Lista completa de veículos encontrados:\n\n" + "\n".join(carros[:50])
        enviar(msg)
    else:
        enviar("⚠️ Nenhum veículo encontrado na lista.")

if __name__ == "__main__":
    asyncio.run(main())
