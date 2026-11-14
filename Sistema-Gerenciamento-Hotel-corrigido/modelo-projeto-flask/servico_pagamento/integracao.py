import os
import requests
from erros import ErroIntegracao

URLS = {
    "hospedes": os.getenv("HOSPEDES_URL", "http://127.0.0.1:5001").rstrip("/"),
    "quartos": os.getenv("QUARTOS_URL", "http://127.0.0.1:5002").rstrip("/"),
    "reservas": os.getenv("RESERVAS_URL", "http://127.0.0.1:5003").rstrip("/"),
    "pagamentos": os.getenv("PAGAMENTOS_URL", "http://127.0.0.1:5004").rstrip("/"),
}
TIMEOUT = 5
ORIGEM = "pagamentos"


def chamar(destino, metodo, caminho, **kwargs):
    if destino not in URLS:
        raise ErroIntegracao(f"Destino de integração desconhecido: {destino}.", 500)
    url = URLS[destino] + caminho
    print(f"[{ORIGEM}] chamando {metodo} {url}", flush=True)
    try:
        resposta = requests.request(metodo, url, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.Timeout as erro:
        raise ErroIntegracao(f"O serviço {destino} não respondeu dentro de {TIMEOUT} segundos.", 503) from erro
    except requests.exceptions.ConnectionError as erro:
        raise ErroIntegracao(f"O serviço {destino} está indisponível. Verifique se está iniciado.", 503) from erro
    except requests.exceptions.RequestException as erro:
        raise ErroIntegracao(f"Falha ao comunicar com o serviço {destino}: {erro}", 502) from erro
    print(f"[{ORIGEM}] resposta de {destino}: HTTP {resposta.status_code}", flush=True)
    return resposta
