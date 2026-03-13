import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# URLs de API interna do Webmotors (filtradas pelos carros que você quer)
URLS = [
    "https://www.webmotors.com.br/api/stock/carros/fiat/argo?cidade=Campinas&precoate=62000&anode=2020&kmde=999&kmate=50000&anunciante=Concessionária|Loja&page=1",
    "https://www.webmotors.com.br/api/stock/carros/peugeot/208?cidade=Campinas&precoate=62000&anode=2022&kmde=999&kmate=50000&anunciante=Concessionária|Loja&page=1"
]

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def buscar_carros():
    encontrados = []

    for url in URLS:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            print(f"Erro ao acessar API: {r.status_code}")
            continue

        try:
            data = r.json()
        except:
            print("⚠️ API não retornou JSON")
            continue

        # cada item é um carro
        for carro in data.get("items", []):
            link = carro.get("linkWebmotors")
            if link:
                encontrados.append(link)

    return list(set(encontrados))


def main():
    carros = buscar_carros()

    if carros:
        msg = "🚗 Veículos encontrados:\n\n"
        for c in carros[:20]:
            msg += c + "\n"
        enviar(msg)
    else:
        enviar("⚠️ Nenhum veículo encontrado na API.")


if __name__ == "__main__":
    main()
