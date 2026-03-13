import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

VEICULOS = [
    {
        "marca": "fiat",
        "modelo": "argo",
        "cidade": "Campinas",
        "ano_min": 2020,
        "ano_max": 2026,
        "km_max": 50000,
        "preco_max": 62000
    },
    {
        "marca": "peugeot",
        "modelo": "208",
        "cidade": "Campinas",
        "ano_min": 2022,
        "ano_max": 2026,
        "km_max": 50000,
        "preco_max": 62000
    }
]

async def buscar_carros():
    links_encontrados = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for v in VEICULOS:
            url = f"https://www.webmotors.com.br/carros/estoque/{v['marca']}/{v['modelo']}?cidade={v['cidade']}"
            await page.goto(url)
            await page.wait_for_selector("a[href*='/comprar/']", timeout=10000)

            # Pegar links
            elementos = await page.query_selector_all("a[href*='/comprar/']")
            for el in elementos:
                link = await el.get_attribute("href")
                if link and link.startswith("/comprar/"):
                    links_encontrados.append("https://www.webmotors.com.br" + link)

        await browser.close()
    return list(set(links_encontrados))

async def main():
    links = await buscar_carros()
    if links:
        msg = "🚗 Segue a lista de veículos encontrados:\n\n"
        for l in links[:20]:
            msg += l + "\n"
        enviar(msg)
    else:
        enviar("⚠️ Nenhum veículo encontrado.")

if __name__ == "__main__":
    asyncio.run(main())
