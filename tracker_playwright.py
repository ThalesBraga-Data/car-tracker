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
        # Simulando um iPhone 13 para mudar a rota de filtragem do servidor
        device = p.devices['iPhone 13']
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(
            **device,
            locale="pt-BR",
            timezone_id="America/Sao_Paulo"
        )
        
        page = await context.new_page()

        for url in URLS:
            try:
                print(f"Tentando acesso mobile em: {url[:40]}...")
                
                # Vamos direto ao ponto, sem esperar idle
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Espera extra para renderização do JS
                await asyncio.sleep(8) 
                
                # Scroll para garantir que os cards carreguem
                await page.mouse.wheel(0, 2000)
                await asyncio.sleep(2)

                # Seletor mobile costuma ser diferente, vamos buscar por links de compra de forma genérica
                links = await page.eval_on_selector_all(
                    "a", 
                    "elements => elements.map(el => el.href).filter(href => href.includes('/comprar/'))"
                )
                
                for link in links:
                    clean_link = link.split('?')[0]
                    # Evita links de parcelamento ou institucionais
                    if "/carros/estoque" not in clean_link:
                        todos_carros.add(clean_link)
                
                print(f"Sucesso! Links encontrados: {len(todos_carros)}")

            except Exception as e:
                print(f"Erro na tentativa: {e}")
                continue

        await browser.close()
    return list(todos_carros)

async def main():
    carros = await buscar_carros()
    if carros:
        msg = f"🚗 {len(carros)} carros encontrados!\n\n" + "\n\n".join(carros[:15])
        enviar(msg)
    else:
        print("Bloqueio persistente. O IP do GitHub Actions está na blacklist.")

if __name__ == "__main__":
    asyncio.run(main())
