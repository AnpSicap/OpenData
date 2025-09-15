import os
import json
import time
import requests
from collections import defaultdict

BASE_URL = "https://contratos-api.ans.gov.br/contratos"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

ARQUIVO_SAIDA = os.path.join(DATA_DIR, "contratos.json")
ARQUIVO_DESCARTADOS = os.path.join(DATA_DIR, "contratos_descartados.json")


def coletar_contratos():
    contratos = []
    for ano in range(2000, 2026):
        print(f"\n🔍 Processando ano {ano}...")
        pagina = 1
        while True:
            print(f"   📄 Página {pagina}...")
            url = f"{BASE_URL}?ano={ano}&pagina={pagina}&tamanhoPagina=200"
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                dados = resp.json()
            except Exception as e:
                print(f"   ⚠️ Erro ao coletar ano {ano} página {pagina}: {e}")
                break

            itens = dados.get("content", [])
            if not itens:
                print(f"   ✅ 0 contratos encontrados (Total: {len(contratos)})")
                break

            contratos.extend(itens)
            print(f"   ✅ {len(itens)} contratos encontrados (Total: {len(contratos)})")

            if dados.get("last", True):
                break
            pagina += 1
            time.sleep(0.5)
    return contratos


def remover_duplicados_com_diagnostico(contratos):
    """Remove duplicados usando apenas numeroContrato como chave."""
    contratos_unicos = {}
    contratos_descartados = []
    ocorrencias_por_numero = {}

    for idx, contrato in enumerate(contratos):
        numero = contrato.get("numeroContrato")
        if not numero:
            # Se não houver numeroContrato, guarda como descartado com motivo
            contrato_copy = contrato.copy()
            contrato_copy.update({"motivo_descarte": "sem_numeroContrato"})
            contratos_descartados.append(contrato_copy)
            continue

        # Contar campos missing
        null_count = sum(
            1
            for v in contrato.values()
            if v is None or (isinstance(v, str) and v.strip() == "")
        )

        ocorrencias_por_numero.setdefault(numero, {"count": 0, "samples": []})
        ocorrencias_por_numero[numero]["count"] += 1
        if len(ocorrencias_por_numero[numero]["samples"]) < 3:
            ocorrencias_por_numero[numero]["samples"].append(
                {
                    "idx": idx,
                    "null_count": null_count,
                    "idCompra": contrato.get("idCompra"),
                    "codigoUnidadeGestora": contrato.get("codigoUnidadeGestora"),
                }
            )

        if numero not in contratos_unicos:
            contratos_unicos[numero] = (contrato, null_count)
        else:
            existente, existente_nulls = contratos_unicos[numero]
            if null_count < existente_nulls:
                # novo é mais completo -> descarta o antigo
                existente_copy = existente.copy()
                existente_copy.update(
                    {"motivo_descarte": "mais_incompleto", "null_count": existente_nulls}
                )
                contratos_descartados.append(existente_copy)
                contratos_unicos[numero] = (contrato, null_count)
            elif null_count == existente_nulls:
                # empate -> mantém o primeiro
                contrato_copy = contrato.copy()
                contrato_copy.update(
                    {"motivo_descarte": "empate_mesmo_numero", "null_count": null_count}
                )
                contratos_descartados.append(contrato_copy)
            else:
                # novo é mais incompleto
                contrato_copy = contrato.copy()
                contrato_copy.update(
                    {"motivo_descarte": "mais_incompleto", "null_count": null_count}
                )
                contratos_descartados.append(contrato_copy)

    unicos = [c for c, _ in contratos_unicos.values()]
    return unicos, contratos_descartados, ocorrencias_por_numero


def salvar_json(dados, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"💾 Dados salvos em: {caminho}")


def main():
    print("🚀 Iniciando coleta de contratos ANP via API...")
    contratos = coletar_contratos()

    unicos, descartados, ocorrencias = remover_duplicados_com_diagnostico(contratos)

    salvar_json(unicos, ARQUIVO_SAIDA)
    salvar_json(descartados, ARQUIVO_DESCARTADOS)

    print(
        f"\n🎉 Concluído! Total coletados: {len(contratos)} | Únicos: {len(unicos)} | Descartados: {len(descartados)}"
    )

    # Diagnóstico rápido
    repetidos = {k: v for k, v in ocorrencias.items() if v["count"] > 1}
    print(f"\n📊 Diagnóstico: {len(repetidos)} numerosContrato com mais de 1 ocorrência")
    for numero, info in list(repetidos.items())[:5]:
        print(f"   - {numero}: {info['count']} ocorrências (amostras: {info['samples']})")


if __name__ == "__main__":
    main()
