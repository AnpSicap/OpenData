import requests
import re
import time
import random
import json
import os
from bs4 import BeautifulSoup

# Configurações
ORGAO_CODIGO = "32205"
REQUEST_DELAY = 0.5
MAX_RETRIES = 3
TIMEOUT = 30
PAGE_SIZE = 100
URL_CONTRATOS_LISTA = f"https://contratos.comprasnet.gov.br/transparencia/contratos?orgao=[{ORGAO_CODIGO}]"
URL_CONTRATOS_AJAX = "https://contratos.comprasnet.gov.br/transparencia/contratos/search"
OUTPUT_PATH = "data/IDcontratos.json"

def sleep_jitter(base=REQUEST_DELAY):
    time.sleep(base + random.uniform(0, 0.4))

def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    })
    return s

def get_csrf_token(s):
    print("🔐 Buscando CSRF token...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = s.get(URL_CONTRATOS_LISTA, timeout=TIMEOUT)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            meta = soup.find("meta", {"name": "csrf-token"})
            if not meta or not meta.get("content"):
                raise RuntimeError("Meta csrf-token não encontrado")
            token = meta["content"]
            print(f"✅ CSRF token obtido: {token[:10]}...")
            return token
        except Exception as e:
            print(f"❌ Tentativa {attempt} falhou: {e}")
            if attempt >= MAX_RETRIES:
                raise
            sleep_jitter()
    return None

def buscar_todos_ids(s, csrf_token):
    print("🔎 Iniciando busca paginada de IDs de contratos...")
    todos_ids = []
    pagina = 0

    while True:
        start = pagina * PAGE_SIZE
        print(f"\n📄 Página {pagina + 1} (start={start})...")

        headers = {
            "x-csrf-token": csrf_token,
            "x-requested-with": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://contratos.comprasnet.gov.br",
            "Referer": URL_CONTRATOS_LISTA,
            "User-Agent": s.headers.get("User-Agent", "Mozilla/5.0"),
        }

        payload = {
            "draw": 1,
            "start": start,
            "length": PAGE_SIZE,
            "numerocontrato": "",
            "orgao": f"[{ORGAO_CODIGO}]"
        }

        try:
            resp = s.post(URL_CONTRATOS_AJAX, data=payload, headers=headers, timeout=TIMEOUT)
            print("➡️ Status:", resp.status_code)
            print("➡️ Tamanho resposta:", len(resp.text))
            resp.raise_for_status()

            data = resp.json().get("data", [])
            if not data:
                print("✅ Fim da paginação. Nenhum dado retornado.")
                break

            for linha in data:
                for celula in linha:
                    m = re.search(r'/transparencia/contratos/(\d+)', str(celula))
                    if m:
                        todos_ids.append(m.group(1))

            print(f"🔢 IDs acumulados até agora: {len(todos_ids)}")
            pagina += 1
            sleep_jitter()

        except Exception as e:
            print(f"❌ Erro na página {pagina + 1}: {e}")
            break

    return todos_ids

def salvar_json(caminho, lista_ids):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(lista_ids, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("🔍 Iniciando coleta de IDs de contratos...")
    session = make_session()
    csrf_token = get_csrf_token(session)
    ids = buscar_todos_ids(session, csrf_token)
    salvar_json(OUTPUT_PATH, ids)
    print(f"\n🧾 Total final de IDs encontrados: {len(ids)}")
    print(f"📁 Arquivo salvo em: {OUTPUT_PATH}")
