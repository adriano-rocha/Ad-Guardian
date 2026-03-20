# Ad-Guardian 🛡️

Pipeline de monitoramento automatizado de campanhas de tráfego pago (Meta/Google Ads), unindo Python, n8n e Google Sheets com alertas via Telegram.

## Tecnologias
- Python 3
- n8n (self-hosted)
- Google Sheets API
- Telegram Bot API

## Como funciona
1. **Schedule Trigger** (n8n) — dispara a cada hora
2. **Google Sheets** (n8n) — lê os dados de performance das campanhas
3. **Python** — calcula ROAS, CPC, taxa de conversão e classifica o status
4. **Telegram** — envia alerta com ação recomendada (Pausar/Escalar)

## Lógica de classificação
| Status | Condição | Ação |
|---|---|---|
| 🔴 Crítico | ROAS < 1.5 e gasto > R$30 | Pausar imediatamente |
| 🟡 Atenção | ROAS < 3.0 e gasto > R$30 | Revisar criativos |
| 🟢 Escalável | ROAS >= 3.0 e lucro > 0 | Aumentar orçamento |
| 🔵 Monitorar | Dados insuficientes | Aguardar |

## Estrutura
```
ad-guardian/
├── ad_guardian.py   # script principal de métricas
├── data/            # dados de simulação
├── docs/            # documentação do fluxo n8n
└── README.md
```

## Autor
Adriano Rocha — [GitHub](https://github.com/adriano-rocha)