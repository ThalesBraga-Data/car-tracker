import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# URLs simplificadas (removendo filtros pesados que disparam o bot detector)
URLS = [
    "https://www.webmotors.com.br/carros/sp-campinas/fiat/argo/de.2020?kmate=50000&precoate=62000",
    "https://www.webmotors.com.br/carros/sp/peugeot/208/de.2022?kmate=50000&precoate=62000"
]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True})

async def buscar_carros():
    todos_carros = set()
    
    async with async_playwright() as p:
        # Lançando o browser SEM ser headless para tentar enganar o detector
        # (No GitHub Actions ele roda em um framebuffer virtual)
        browser = await p.chromium.launch(headless=True)
        
        # Vamos usar um perfil de navegação mais "sujo"
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "pt-BR,pt;q=0.9",
                "Referer": "https://www.google.com/"
            }
        )
        
        page = await context.new_page()

        # Bloqueia imagens e CSS para economizar tempo e evitar detecção de rastreadores
        await page.route("**/*.{png,jpg,jpeg,svg,css}", lambda route: route.abort())

        for url in URLS:
            try:
                print(f"Tentando burlar bloqueio: {url[:50]}")
                
                # Vai para a página e espera apenas o essencial
                response = await page.goto(url, wait_until="commit")
                
                # Se o status for 403, fomos bloqueados por IP
                if response.status == 403:
                    print("Status 403: O IP do GitHub foi totalmente banido pela Webmotors.")
                    continue

                # Espera o JS rodar um pouco
                await asyncio.sleep(10)

                # Tática Ninja: Pegar todos os links que seguem o padrão de anúncio
                # O comando abaixo extrai direto do HTML bruto se o seletor falhar
                links = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a'))
                        .map(a => a.href)
                        .filter(href => href.includes('/comprar/carros/'))
                }''')

                for link in links:
                    clean_link = link.split('?')[0]
                    if "/estoque" not in clean_link:
                        todos_carros.add(clean_link)

                print(f"Encontrados nesta URL: {len(links)}")

            except Exception as e:
                print(f"Erro: {e}")

        await browser.close()
    return list(todos_carros)

async def main():
    carros = await buscar_carros()
    if carros:
        msg = f"✅ Sucesso! Encontrei {len(carros)} carros:\n\n" + "\n\n".join(carros[:10])
        enviar(msg)
    else:
        # Se falhar aqui, a Webmotors bloqueou a Amazon/Microsoft de vez
        enviar("❌ A Webmotors bloqueou o servidor do GitHub. Preciso mudar de estratégia.")

if __name__ == "__main__":
    asyncio.run(main())
