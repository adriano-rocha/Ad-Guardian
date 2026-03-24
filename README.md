# Ad-Guardian 🛡️

Pipeline de monitoramento automatizado de campanhas de tráfego pago (Meta/Google Ads), unindo JavaScript, n8n e Google Sheets com alertas em tempo real via Telegram.

## Como funciona

O sistema roda de forma totalmente automatizada, sem intervenção manual:

1. **Schedule Trigger** (n8n) — dispara a cada hora automaticamente
2. **Google Sheets** (n8n) — lê os dados de performance de todas as campanhas
3. **Code in JavaScript** (n8n) — calcula ROAS, CPC, taxa de conversão e classifica cada campanha
4. **IF** (n8n) — filtra campanhas que precisam de atenção imediata
5. **Telegram Bot** — envia alerta formatado com status e ação recomendada

## Lógica de classificação

| Status | Condição | Ação recomendada |
|---|---|---|
| 🔴 Crítico | ROAS < 1.5 e gasto > R$30 | Pausar imediatamente |
| 🟡 Atenção | ROAS < 3.0 e gasto > R$30 | Revisar criativos e segmentação |
| 🟢 Escalável | ROAS >= 3.0 e lucro > 0 | Aumentar orçamento |
| 🔵 Monitorar | Dados insuficientes | Aguardar mais dados |

## Métricas calculadas

- **ROAS** — Retorno sobre investimento em anúncios (Receita / Investimento)
- **CPC** — Custo por clique (Investimento / Cliques)
- **Taxa de conversão** — Percentual de cliques que viraram vendas
- **Lucro líquido** — Receita menos investimento

## Estrutura do projeto
```
ad-guardian/
├── script.py        # lógica original prototipada em Python
├── codeJs.js        # código JavaScript que roda no n8n
├── data/            # dados de simulação para testes
├── docs/            # documentação e export do fluxo n8n
└── README.md
```

## Decisão técnica

A lógica de classificação foi prototipada em Python puro (`script.py`) e depois portada para JavaScript (`codeJs.js`) para rodar nativamente dentro do n8n, eliminando a necessidade de um servidor externo e mantendo o projeto 100% gratuito.

## Tecnologias

- JavaScript (n8n Code node)
- Python 3 (prototipagem da lógica)
- n8n self-hosted
- Google Sheets API
- Telegram Bot API

## Como rodar localmente
```bash
# Instalar o n8n
npm install -g n8n

# Iniciar o n8n
n8n start

# Acessar no navegador
http://localhost:5678
```

Importar o workflow em `docs/workflow.json` e configurar as credenciais do Google Sheets e Telegram Bot.

## Autor

Adriano Rocha — [GitHub](https://github.com/adriano-rocha)