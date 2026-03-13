import requests
from bs4 import BeautifulSoup

URL_BASE = "https://www.webmotors.com.br"

filtros = [
    {"marca": "fiat", "modelo": "argo"},
    {"marca": "peugeot", "modelo": "208"}
]

CIDADE = "Campinas"

def buscar_carros(marca, modelo):
    url = f"{URL_BASE}/carros/estoque/{marca}/{modelo}?tipoveiculo=carros&cidade={CIDADE}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Erro {r.status_code} ao acessar {marca} {modelo}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    carros = soup.find_all("a")
    resultados = []

    for c in carros:
        link = c.get("href")
        if link and "/comprar/" in link:
            full_link = URL_BASE + link
            resultados.append(full_link)
    return resultados

# Rodar teste
for f in filtros:
    encontrados = buscar_carros(f["marca"], f["modelo"])
    print(f"\n--- {f['marca'].capitalize()} {f['modelo'].capitalize()} ---")
    if encontrados:
        for link in encontrados[:20]:  # mostra até 20 links
            print(link)
    else:
        print("Nenhum carro encontrado")
