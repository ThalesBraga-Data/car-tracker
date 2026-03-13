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
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True})

async def buscar_carros():
    todos_carros = set()
    
    async with async_playwright() as p:
        # Lançando com argumentos para evitar detecção
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        
        # Criando um contexto com Viewport e User Agent de gente de verdade
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()

        for url in URLS:
            try:
                print(f"Acessando: {url[:50]}...")
                # Mudamos de 'networkidle' para 'commit' (mais rápido) e depois esperamos o seletor
                await page.goto(url, wait_until="commit", timeout=60000)
                
                # Espera o container principal ou um tempo fixo se o seletor falhar
                try:
                    await page.wait_for_selector("div.ContainerCardVehicle", timeout=20000)
                except:
                    print("Seletor não apareceu, tentando prosseguir assim mesmo...")

                # Simula um scroll humano lento
                await page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(3)

                # Busca links. O seletor da Webmotors muitas vezes usa h2 ou div para o link
                elementos = await page.query_selector_all('a[href*="/comprar/"]')
                
                for e in elementos:
                    link = await e.get_attribute("href")
                    if link:
                        if "/comprar/carros/" in link:
                            full_link = link if link.startswith("http") else f"https://www.webmotors.com.br{link}"
                            clean_link = full_link.split('?')[0]
                            todos_carros.add(clean_link)
                
                print(f"Encontrados {len(todos_carros)} links até agora.")

            except Exception as e:
                print(f"Erro ao acessar: {e}")
                continue

        await browser.close()
    return list(todos_carros)

async def main():
    carros = await buscar_carros()
    if carros:
        # Envia de 20 em 20 para não estourar o limite do Telegram
        for i in range(0, len(carros), 20):
            bloco = carros[i:i+20]
            msg = f"🚗 Carros Encontrados ({i+1}/{len(carros)}):\n\n" + "\n\n".join(bloco)
            enviar(msg)
    else:
        print("Realmente não encontrou nada. Pode ser bloqueio de IP do GitHub.")

if __name__ == "__main__":
    asyncio.run(main())
