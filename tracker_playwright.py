import os
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Onde vamos salvar os carros já enviados
ARQUIVO_ANTIGOS = Path("carros_enviados.json")

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
    novos_carros = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for url in URLS:
            await page.goto(url)
            # scroll até carregar todos os carros
            previous_height = None
            while True:
                height = await page.evaluate("document.body.scrollHeight")
                if previous_height == height:
                    break
                previous_height = height
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)  # espera carregar novos anúncios

            # pegar todos links de carros
            elementos = await page.query_selector_all("a[href*='/comprar/']")
            for e in elementos:
                link = await e.get_attribute("href")
                if link:
                    novos_carros.append("https://www.webmotors.com.br" + link)
        await browser.close()
    return list(set(novos_carros))

def carregar_anteriores():
    if ARQUIVO_ANTIGOS.exists():
        with ARQUIVO_ANTIGOS.open("r") as f:
            return set(json.load(f))
    return set()

def salvar_carros(carros):
    with ARQUIVO_ANTIGOS.open("w") as f:
        json.dump(list(carros), f)

async def main():
    todos_carros = await buscar_carros()
    enviados = carregar_anteriores()

    novos = [c for c in todos_carros if c not in enviados]

    if novos:
        msg = "🚗 Novos veículos encontrados:\n\n" + "\n".join(novos[:20])
        enviar(msg)
        # atualiza arquivo com todos carros já enviados
        salvar_carros(enviados.union(novos))
    else:
        enviar("⚠️ Nenhum veículo novo encontrado.")

if __name__ == "__main__":
    asyncio.run(main())
