# -*- coding: utf-8 -*-
import os
import json
import time
import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# =============================
# Configurações
# =============================
REQUEST_DELAY = 0.8
MAX_RETRIES = 3
TIMEOUT = 30

URL_CONTRATO_DETALHE = "https://contratos.comprasnet.gov.br/transparencia/contratos/{}"
URL_CONTRATOS_IDS = "data/IDcontratos.json"

TABELAS_MAPA = {
    1: "detalhes.json",
    2: "historico.json",
    3: "despesasAcessorias.json",
    4: "empenhos.json",
    5: "faturas.json",
    6: "garantias.json",
    7: "itens.json",
    8: "prepostos.json",
    9: "responsaveis.json",
    10: "arquivos.json"
}

# =============================
# Utilidades
# =============================
def sleep_jitter(base=REQUEST_DELAY):
    time.sleep(base + random.uniform(0, 0.4))

def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    })
    return s

def carregar_ids(caminho=URL_CONTRATOS_IDS):
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo {caminho} não encontrado.")
    with open(caminho, "r", encoding="utf-8") as f:
        base = json.load(f)
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

def extrair_tabelas(soup: BeautifulSoup, contrato_id: str):
    tabelas_extraidas = {}
    tabelas = soup.find_all("table")
    print(f"📊 {len(tabelas)} tabelas encontradas para contrato {contrato_id}")

    for i, tabela in enumerate(tabelas, start=1):
        linhas = []
        headers = [th.get_text(strip=True) for th in tabela.find_all("th")]

        for tr in tabela.find_all("tr")[1:]:
            tds = tr.find_all("td")
            if not tds:
                continue
            linha = {headers[j]: tds[j].get_text(strip=True) for j in range(min(len(headers), len(tds)))}
            linhas.append(linha)

        nome_arquivo = TABELAS_MAPA.get(i)
        if nome_arquivo:
            if nome_arquivo not in tabelas_extraidas:
                tabelas_extraidas[nome_arquivo] = []
            tabelas_extraidas[nome_arquivo].append({
                "contrato_id": contrato_id,
                "registros": linhas
            })

    return tabelas_extraidas

# =============================
# Main
# =============================
def main():
    print("🚀 Extraindo tabelas dos contratos (ComprasNet)...")
    ids = carregar_ids()
    print(f"🔢 Total de contratos: {len(ids)}")

    session = make_session()

    # buffers separados por tipo de tabela
    buffers = {fname: [] for fname in TABELAS_MAPA.values()}

    for i, contrato_id in enumerate(ids, start=1):
        print(f"[{i}/{len(ids)}] Baixando contrato {contrato_id}...")
        url = URL_CONTRATO_DETALHE.format(contrato_id)

        detalhe_html = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = session.get(url, timeout=TIMEOUT)
                r.raise_for_status()
                detalhe_html = r.text
                break
            except Exception as e:
                print(f"   ❌ Falha tentativa {attempt}/{MAX_RETRIES}: {e}")
                if attempt >= MAX_RETRIES:
                    detalhe_html = None
                else:
                    sleep_jitter(REQUEST_DELAY + 0.5)

        if not detalhe_html:
            print(f"⚠️ Ignorando contrato {contrato_id} (sem HTML).")
            continue

        soup = BeautifulSoup(detalhe_html, "html.parser")
        tabelas = extrair_tabelas(soup, contrato_id)

        # acumula nos buffers
        for fname, dados in tabelas.items():
            buffers[fname].extend(dados)

        sleep_jitter()

    # salvar cada arquivo
    for fname, dados in buffers.items():
        salvar_json(f"data/{fname}", dados)
        print(f"✅ Gerado data/{fname} ({len(dados)} contratos)")

    print("🎉 Finalizado com sucesso!")

if __name__ == "__main__":
    ok = main()
    raise SystemExit(0 if ok else 1)
