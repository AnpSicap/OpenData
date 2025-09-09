# src/detalhes_contratos.py
# -*- coding: utf-8 -*-
import os
import re
import json
import time
import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# =============================
# Configurações
# =============================
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

URL_IDS_CONTRATOS = "data/IDcontratos.json"
URL_CONTRATO_DETALHE = "https://contratos.comprasnet.gov.br/transparencia/contratos/{}"

OUTPUT_FILES = {
    "historico": "data/historico.json",
    "responsaveis": "data/responsaveis.json",
}

# =============================
# Utilidades
# =============================
def norm(txt: str) -> str:
    if txt is None:
        return ""
    return re.sub(r"\s+", " ", str(txt)).strip().lower()

def sleep_jitter(base=REQUEST_DELAY):
    time.sleep(base + random.uniform(0, 0.4))

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    })
    return s

def carregar_ids():
    if not os.path.exists(URL_IDS_CONTRATOS):
        raise FileNotFoundError(f"Arquivo não encontrado: {URL_IDS_CONTRATOS}")
    with open(URL_IDS_CONTRATOS, "r", encoding="utf-8") as f:
        base = json.load(f)
    if isinstance(base, list):
        return base
    return base.get("dados", [])

def salvar_json(caminho, dados_array):
    os.makedirs("data", exist_ok=True)
    saida = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "total_registros": len(dados_array),
        "dados": dados_array
    }
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

# =============================
# Extração (apenas Histórico e Responsáveis)
# =============================
TABELAS_HEADERS = {
    "historico": ["Data Assinatura", "Número", "Tipo", "Observação",
                  "Data Início", "Data Fim", "Vlr. Global", "Parcelas", "Vlr. Parcela"],
    "responsaveis": ["CPF", "Nome", "Tipo"],
}

def match_headers(actual_headers, expected_headers):
    a = [norm(h) for h in actual_headers]
    e = [norm(h) for h in expected_headers]
    return a == e

def extrair_tabelas(soup: BeautifulSoup, contrato_id: str):
    tabelas = {k: [] for k in TABELAS_HEADERS.keys()}
    for tabela in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in tabela.find_all("th")]
        for chave, esperado in TABELAS_HEADERS.items():
            if match_headers(headers, esperado):
                for tr in tabela.find_all("tr")[1:]:
                    tds = tr.find_all("td")
                    if not tds:
                        continue
                    linha = {headers[i]: tds[i].get_text(strip=True) for i in range(len(headers))}
                    tabelas[chave].append({
                        "contrato_id": contrato_id,
                        "dados": linha
                    })
    return tabelas

# =============================
# Main
# =============================
def main():
    print("🚀 Extraindo Histórico e Responsáveis dos contratos (ComprasNet)...")
    ids = carregar_ids()
    print(f"🧾 Total de contratos a processar: {len(ids)}")

    s = make_session()
    acumulado = {k: [] for k in TABELAS_HEADERS.keys()}

    for i, contrato_id in enumerate(ids, start=1):
        print(f"[{i}/{len(ids)}] 🔎 Baixando contrato {contrato_id}...")
        url = URL_CONTRATO_DETALHE.format(contrato_id)
        detalhe_html = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = s.get(url, timeout=TIMEOUT)
                r.raise_for_status()
                detalhe_html = r.text
                break
            except Exception as e:
                print(f"   ❌ Falha ao carregar {contrato_id} (tentativa {attempt}/{MAX_RETRIES}): {e}")
                if attempt >= MAX_RETRIES:
                    detalhe_html = None
                else:
                    sleep_jitter(REQUEST_DELAY + 0.5)

        if not detalhe_html:
            print(f"⚠️ Ignorando contrato {contrato_id} (sem HTML).")
            continue

        soup = BeautifulSoup(detalhe_html, "html.parser")
        tabelas = extrair_tabelas(soup, contrato_id)

        for chave, valores in tabelas.items():
            acumulado[chave].extend(valores)

        sleep_jitter()

    for chave, caminho in OUTPUT_FILES.items():
        salvar_json(caminho, acumulado[chave])
        print(f"✅ Arquivo gerado: {caminho} ({len(acumulado[chave])} registros)")

    return True

if __name__ == "__main__":
    ok = main()
    raise SystemExit(0 if ok else 1)
