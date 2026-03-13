import os
import requests
import json

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Configurações de Busca (Convertidas para o formato da API)
BUSCAS = [
    {"marca": "FIAT", "modelo": "ARGO", "ano_de": 2020, "preco_ate": 62000, "cidade": "Campinas"},
    {"marca": "PEUGEOT", "modelo": "208", "ano_de": 2022, "preco_ate": 62000, "cidade": "SÃO PAULO"}
]

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True})

def buscar_webmotors():
    todos_links = []
    
    # Headers que simulam um navegador real para evitar bloqueio de API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.webmotors.com.br",
        "Referer": "https://www.webmotors.com.br/carros/estoque"
    }

    for busca in BUSCAS:
        print(f"Buscando {busca['marca']} {busca['modelo']}...")
        
        # URL da API de busca da Webmotors
        api_url = f"https://www.webmotors.com.br/api/search/car?p=1&qt=36&o=5&anode={busca['ano_de']}&precoate={busca['preco_ate']}"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                veiculos = data.get("SearchResults", [])
                
                for carro in veiculos:
                    # Monta o link base do anúncio
                    marca = carro['Specification']['Make']['Value'].lower()
                    modelo = carro['Specification']['Model']['Value'].lower().replace(" ", "-")
                    id_anuncio = carro['UniqueId']
                    
                    link = f"https://www.webmotors.com.br/comprar/{marca}/{modelo}/4-portas/{busca['ano_de']}/{id_anuncio}"
                    todos_links.append(link)
            else:
                print(f"Erro na API: Status {response.status_code}")
        except Exception as e:
            print(f"Falha na requisição: {e}")

    return list(set(todos_links))

def main():
    links = buscar_webmotors()
    
    if links:
        # Enviando apenas os 15 primeiros para teste
        msg = f"🚀 Encontrei {len(links)} carros via API!\n\n" + "\n\n".join(links[:15])
        enviar_telegram(msg)
        print(f"Sucesso! {len(links)} enviados.")
    else:
        print("A API também bloqueou ou não há resultados.")

if __name__ == "__main__":
    main()
