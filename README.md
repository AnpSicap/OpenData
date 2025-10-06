# 🏢 OpenData – ANP

Automação para coleta de **dados de contratos e faturas da ANP** a partir do portal de transparência.  

Repositório: **AnpSicap/OpenData**  

📧 **Contas de e-mail utilizadas**  
- **Produção:** `sicap-sga@outlook.com`  
- **Teste:** `github_anp@outlook.com`  

---

## ⚙️ Funcionalidades

- 📋 Coleta automática de **faturas, histórico e responsáveis** via web scraping do portal de transparência  
- 📄 Coleta de **contratos** através da **API oficial de dados abertos**  
- 💾 Armazenamento em **JSON estruturado e padronizado**  
- ⏰ Execução automática via **GitHub Actions** (segunda a sexta-feira)  
- 🔄 Atualização diária dos dados  

---

## 📊 Estrutura de Dados

OpenData

│

├── .github/workflows

│ ├── IDcontratos.yml

│ ├── contratos.yml

│ ├── detalhes_contratos.yml

│ └── faturas.yml

│

├── data

│ ├── IDcontratos.json

│ ├── contratos.json

│ ├── faturas.json

│ └── historico.json

│

├── src

│ ├── IDcontratos.py

│ ├── contratos.py

│ ├── detalhes_contratos.py

│ ├── faturas.py

│ └── requirements.txt

│

├── .gitignore

└── README.md




📂 Os dados são salvos em `data/*.json` no seguinte formato:

```json
{
  "ultima_atualizacao": "2024-01-15T10:30:00",
  "total_registros": 150,
  "dados": [...]
}

````

## 🕐 Agendamento (GitHub Actions)

- 🆔 **IDcontratos**  
  `0 6 * * 1-5` → Segunda a sexta às 6h UTC (3h BRT)  

- 📄 **Contratos**  
  `0 6 * * 1-5` → Segunda a sexta às 6h UTC (3h BRT)  

- 📑 **Detalhes_contratos**  
  `0 7 * * 1-5` → Segunda a sexta às 7h UTC (4h BRT)  

- 📋 **Faturas**  
  `0 5 * * 1-5` → Segunda a sexta às 5h UTC (2h BRT)  

---

## 📦 Dados Disponíveis

- 📌 ID de todos os contratos da ANP: https://raw.githubusercontent.com/AnpSicap/OpenData/main/data/IDcontratos.json
- 📌 Faturas de todos os contratos da ANP: https://raw.githubusercontent.com/AnpSicap/OpenData/main/data/faturas.json
- 📌 Informações principais dos Contratos da ANP: https://raw.githubusercontent.com/AnpSicap/OpenData/main/data/contratos.json
- 📌 Histórico dos contratos da ANP: https://raw.githubusercontent.com/AnpSicap/OpenData/main/data/historico.json
- 📌 Responsáveis pelos contratos da ANP: https://raw.githubusercontent.com/AnpSicap/OpenData/main/data/responsaveis.json


---

## 🚀 Como Usar

- Acesse os JSONs diretamente pelos links acima  
- Consuma no **Power Apps, Excel** ou qualquer aplicação  
- Dados atualizados **automaticamente todos os dias**  

---

## 🔐 Transparência e Segurança

✅ Repositório público e aberto  
✅ Apenas dados públicos oficiais  
✅ Nenhuma credencial ou dado sensível  
✅ Código aberto para auditoria  

---

## 🔗 Fontes Oficiais

- Portal de Transparência: [https://contratos.comprasnet.gov.br](https://contratos.comprasnet.gov.br)  
- Faturas da ANP: [https://contratos.comprasnet.gov.br/transparencia/faturas?orgao=[32205]](https://contratos.comprasnet.gov.br/transparencia/faturas?orgao=[32205])  
- API de Contratos: [https://dadosabertos.compras.gov.br/modulo-contratos](https://dadosabertos.compras.gov.br/modulo-contratos)  

---

## 📈 Estatísticas de Execução

- ⏱️ Tempo médio: **1-2 minutos (API)** | **5-10 minutos (scraper)**  
- 📊 Consumo: ~8% do limite gratuito mensal  
- 💰 Custo: **$0.00** (plano gratuito)  

---

## 💡 Informações Técnicas

- Desenvolvido em **Python 3.10**  
- Agendamento via **GitHub Actions**  
- JSON otimizado para **Power Apps**  

---

## 🎯 Benefícios do Projeto

- 🔄 Automação completa: coleta sem intervenção manual  
- 📅 Dados sempre atualizados: execução diária  
- 📐 Padronização: schema único em JSON  
- 🌐 Transparência: apenas dados públicos e auditáveis  
- 🔒 Segurança: sem credenciais sensíveis  
- 💸 Custo zero: uso do GitHub Actions gratuito  
- ♻️ Independência tecnológica: pode rodar em GitHub, GitLab ou servidores próprios  
- 📂 E-mail curinga: sem dependência de contas pessoais  
- 👥 Continuidade: não depende de equipe específica  
- 🔗 Escalabilidade: estrutura modular em Python  
- 📦 Backup automático: histórico versionado no SharePoint  
- ⚡ Baixo consumo de recursos: execução rápida e leve  

---

## 🔄 Integração com Power Apps (Cache Update)

### 🔄 Fluxo 1 – Agendado (Cache Update)

- **Disparo:** todo dia às 05:00 (E. South America Standard Time)  
- **Ações:**  
  - HTTP GET em `contratos.json` e `faturas.json`  
  - Validação do retorno (status 200 e body válido)  
  - Atualização das listas no SharePoint  
  - Registro de erros em caso de falha  

### 🔎 Fluxo 2 – Consulta (OnDemand)

- **Disparo:** pelo Power Apps (abertura do app ou botão "Atualizar")  
- **Ações:**  
  - Busca dados direto do SharePoint  
  - Retorna JSON estável para o app  

✅ **Vantagens**  
- O app consulta apenas o SharePoint (mais estável que GitHub)  
- Cache atualizado em horários controlados  
- Usuários continuam com acesso ao último dado válido mesmo em falhas  
- OnStart do app mais rápido  

---

✍️ **Autor:** Equipe **SICAP/SGA/ANP**  
📌 Projeto público, livre e reutilizável.



