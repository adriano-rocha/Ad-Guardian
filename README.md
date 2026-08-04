# Ad-Guardian 🛡️

Pipeline de monitoramento automatizado de campanhas de tráfego pago (Meta/Google Ads), unindo JavaScript, n8n e Google Sheets com alertas em tempo real via Telegram.

## Como funciona

O sistema roda de forma totalmente automatizada, sem intervenção manual:

1. **Schedule Trigger** (n8n) — dispara a cada hora automaticamente
2. **Google Sheets** (n8n) — lê os dados de performance de todas as campanhas
3. **Code in JavaScript** (n8n) — calcula ROAS, CPC, taxa de conversão, classifica cada campanha e verifica se o status mudou desde a última execução
4. **IF** (n8n) — filtra campanhas com status diferente de "Monitorar" **e** que tiveram mudança de status (evita alerta repetido toda hora pra mesma situação)
5. **Telegram Bot** — envia alerta formatado com status e ação recomendada

## Lógica de classificação

| Status | Condição | Ação recomendada |
|---|---|---|
| 🔴 Crítico | ROAS < 1.5 e gasto ≥ R$30 | Pausar imediatamente |
| 🟡 Atenção | ROAS < 3.0 e gasto ≥ R$30 | Revisar criativos e segmentação |
| 🟢 Escalável | ROAS ≥ 3.0, lucro > 0 e gasto ≥ R$30 | Aumentar orçamento |
| 🔵 Monitorar | Dados insuficientes (gasto < R$30) | Aguardar mais dados |

> O gasto mínimo de R$30 é exigido em **todos** os status de ação (inclusive Escalável) para evitar decisões baseadas em amostra pequena — ex: 1 venda de sorte com R$5 investidos não deve disparar "escalar orçamento".

## Métricas calculadas

- **ROAS** — Retorno sobre investimento em anúncios (Receita / Investimento)
- **CPC** — Custo por clique (Investimento / Cliques)
- **Taxa de conversão** — Percentual de cliques que viraram vendas
- **Lucro líquido** — Receita menos investimento

## ⚠️ Fonte de verdade do código

A lógica de negócio (cálculo de métricas + classificação) existe em dois lugares do repositório, mas **apenas um roda em produção**:

- `docs/workflow.json` → node **"Code in JavaScript"** — **é o que roda de verdade**, disparado pelo Schedule Trigger dentro do n8n.
- `script.py` → **protótipo/estudo**, não é executado automaticamente. Serve só para testar a lógica isoladamente via terminal (`python script.py '{"Campanha": ...}'`). Se alterar a lógica de negócio, replique a mudança no node JS do n8n — o Python não é lido pelo workflow.

## Anti-spam de alertas

O node "Code in JavaScript" usa a memória persistente do n8n (`$getWorkflowStaticData`) para lembrar o último status de cada campanha e só libera o alerta quando o status **muda** de uma execução para a outra. Isso só funciona se o workflow estiver **salvo e ativo** no n8n — em execução manual solta (sem salvar), essa memória não persiste entre execuções.

## Estrutura do projeto
```
ad-guardian/
├── script.py        # protótipo em Python (não roda automaticamente, ver seção acima)
├── docs/
│   └── workflow.json  # export do fluxo n8n — fonte de verdade da lógica em produção
├── data/            # dados de simulação para testes
├── .env             # credenciais (não versionado)
├── .gitignore
└── README.md
```

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

Importar o workflow em `docs/workflow.json`, configurar as credenciais do Google Sheets e Telegram Bot, **salvar o workflow** e ativar o toggle "Active" para ele rodar sozinho a cada hora.

### Rodar 24/7 sem custo

Rodar local (`n8n start` no seu PC) só funciona enquanto o PC estiver ligado. Para operação contínua com gasto zero, a opção recomendada é hospedar o n8n numa VM gratuita da **Oracle Cloud Free Tier** (camada gratuita permanente, não é trial).

## Autor

Adriano Rocha — [GitHub](https://github.com/adriano-rocha)