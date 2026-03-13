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
    # Adicionado disable_web_page_preview para a mensagem não ficar gigante com fotos
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True})

async def buscar_carros():
    todos_carros = set() # Usar set evita duplicados automaticamente
    
    async with async_playwright() as p:
        # User-agent para evitar bloqueio básico
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        for url in URLS:
            try:
                # Timeout de 60s para garantir que a página carregue no GitHub Actions
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Espera o container dos cards aparecer (seletor comum na Webmotors)
                await page.wait_for_selector("div.ContainerCardVehicle", timeout=15000)
                
                # Um pequeno scroll ajuda a disparar o carregamento lazy-load
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)

                # Busca links que contenham '/comprar/' no href
                links = await page.locator('a[href*="/comprar/"]').all_human_ids() # ou use o seletor abaixo
                elementos = await page.query_selector_all('a[href*="/comprar/"]')
                
                for e in elementos:
                    link = await e.get_attribute("href")
                    if link:
                        # Garante que o link seja completo e limpo
                        full_link = link if link.startswith("http") else f"https://www.webmotors.com.br{link}"
                        # Limpa parâmetros de busca do link individual para ficar menor
                        clean_link = full_link.split('?')[0]
                        todos_carros.add(clean_link)
            
            except Exception as e:
                print(f"Erro ao acessar {url}: {e}")
                continue

        await browser.close()
    return list(todos_carros)

async def main():
    carros = await buscar_carros()
    if carros:
        # Enviar em blocos se houver muitos, o Telegram tem limite de caracteres
        total = len(carros)
        msg = f"🚗 Encontrei {total} veículos novos!\n\n" + "\n\n".join(carros[:25])
        enviar(msg)
    else:
        # Não enviar nada se não encontrar, para não spammar erro
        print("Nenhum carro encontrado nesta rodada.")

if __name__ == "__main__":
    asyncio.run(main())
