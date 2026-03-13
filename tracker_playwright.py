import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URLS = [
    "https://www.webmotors.com.br/carros/sp-campinas/fiat/argo/de.2020?tipoveiculo=carros&localizacao=-22.9099384%2C-47.0626332x100km&estadocidade=S%C3%A3o%20Paulo-Campinas&marca1=FIAT&modelo1=ARGO&kmde=999&kmate=50000&anunciante=Concession%C3%A1ria%7CLoja&o=5&page=1&anode=2020&precoate=62000",
    "https://www.webmotors.com.br/carros/sp/peugeot/208/de.2022?tipoveiculo=carros&estadocidade=S%C3%A3o%20Paulo&marca1=Peugeot&modelo1=208&kmde=999&kmate=50000&anunciante=Concession%C3%A1ria%7CLoja&page=1&anode=2022&precoate=62000"
]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

async def buscar_links():
    encontrados = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for url in URLS:

            await page.goto(url)

            # espera página carregar
            await page.wait_for_timeout(5000)

            # scroll para carregar anúncios
            await page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight)
            """)

            await page.wait_for_timeout(3000)

            links = await page.eval_on_selector_all(
                "a[href*='/comprar/']",
                "elements => elements.map(e => e.href)"
            )

            encontrados.extend(links)

        await browser.close()

    return list(set(encontrados))


async def main():

    links = await buscar_links()

    if links:

        msg = "🚗 Veículos encontrados:\n\n"

        for l in links[:20]:
            msg += l + "\n"

        enviar(msg)

    else:
        enviar("⚠️ Nenhum veículo encontrado.")


if __name__ == "__main__":
    asyncio.run(main())
