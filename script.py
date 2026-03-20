import json
import sys

'''
AD-GUARDIAN — Processador de Métricas de Campanha
Recebe um JSON via argumento, calcula métricas e retorna
um JSON com status e mensagem de alerta.
'''

# (ajuste conforme  nicho)
ROAS_MINIMO      = 1.5   # Abaixo disso = prejuízo em muitos modelos
ROAS_META        = 3.0   # Meta saudável de retorno
GASTO_MINIMO     = 30.0  # Só alerta "Crítico" se já gastou pelo menos R$30
CTR_MINIMO       = 1.0   # CTR abaixo de 1% = anúncio fraco

def calcular_metricas(dados: dict) -> dict:
    """
    Recebe os dados brutos da planilha e calcula todas as métricas.
    Retorna um dicionário com os valores calculados.
    """
    investimento  = float(dados.get("Investimento", 0))
    cliques       = int(dados.get("Cliques", 0))
    vendas        = int(dados.get("Vendas", 0))
    valor_venda   = float(dados.get("Valor_Venda", 0))

    # Receita total gerada pelas vendas
    receita = vendas * valor_venda

    # ROAS = Receita / Investimento  (ex: 3.0 = R$3 gerados para cada R$1 gasto)
    roas = round(receita / investimento, 2) if investimento > 0 else 0

    # CPC = Investimento / Cliques  (custo médio por clique)
    cpc = round(investimento / cliques, 2) if cliques > 0 else 0

    # CTR = (Cliques / Impressões) * 100  — como não temos impressões na planilha,
    # usamos Cliques/Vendas como proxy de qualidade do funil (taxa de conversão)
    taxa_conversao = round((vendas / cliques) * 100, 2) if cliques > 0 else 0

    # Lucro Líquido = Receita - Investimento
    lucro_liquido = round(receita - investimento, 2)

    return {
        "campanha"       : dados.get("Campanha", "N/A"),
        "data"           : dados.get("Data", "N/A"),
        "investimento"   : investimento,
        "cliques"        : cliques,
        "vendas"         : vendas,
        "valor_venda"    : valor_venda,
        "receita"        : round(receita, 2),
        "roas"           : roas,
        "cpc"            : cpc,
        "taxa_conversao" : taxa_conversao,
        "lucro_liquido"  : lucro_liquido,
    }


def classificar_status(metricas: dict) -> tuple[str, str, str]:
    """
    Aplica a lógica de gestão e retorna:
    - status   : "Crítico" | "Atenção" | "Escalável" | "Monitorar"
    - emoji    : para deixar o alerta visual no Telegram
    - acao     : o que fazer com a campanha
    """
    roas        = metricas["roas"]
    investimento = metricas["investimento"]
    lucro       = metricas["lucro_liquido"]

    # CRÍTICO: ROAS ruim E já gastou o suficiente para ser relevante
    if roas < ROAS_MINIMO and investimento >= GASTO_MINIMO:
        return "Crítico", "🔴", "PAUSAR imediatamente"

    # ATENÇÃO: ROAS abaixo da meta, mas ainda não crítico
    if roas < ROAS_META and investimento >= GASTO_MINIMO:
        return "Atenção", "🟡", "Revisar criativos e segmentação"

    # ESCALÁVEL: ROAS acima da meta e lucro positivo
    if roas >= ROAS_META and lucro > 0:
        return "Escalável", "🟢", "ESCALAR — aumentar orçamento"

    # MONITORAR: ainda sem dados suficientes ou em fase inicial
    return "Monitorar", "🔵", "Aguardar mais dados"


def formatar_mensagem(metricas: dict, status: str, emoji: str, acao: str) -> str:
    """
    Monta a mensagem formatada que será enviada pelo Telegram.
    """
    msg = f"""
{emoji} *AD-GUARDIAN ALERTA*
━━━━━━━━━━━━━━━━━━━━
📋 *Campanha:* {metricas['campanha']}
📅 *Data:* {metricas['data']}
━━━━━━━━━━━━━━━━━━━━
💸 *Investimento:* R$ {metricas['investimento']:.2f}
🖱️ *Cliques:* {metricas['cliques']}
🛒 *Vendas:* {metricas['vendas']}
💰 *Receita:* R$ {metricas['receita']:.2f}
━━━━━━━━━━━━━━━━━━━━
📊 *ROAS:* {metricas['roas']}x
💲 *CPC:* R$ {metricas['cpc']:.2f}
🎯 *Conv. Rate:* {metricas['taxa_conversao']}%
✅ *Lucro Líquido:* R$ {metricas['lucro_liquido']:.2f}
━━━━━━━━━━━━━━━━━━━━
{emoji} *STATUS: {status}*
⚡ *AÇÃO: {acao}*
""".strip()
    return msg


def main():
    # O n8n vai passar o JSON como argumento na linha de comando
    # Exemplo: python ad_guardian.py '{"Campanha": "Curso Trader", ...}'
    if len(sys.argv) < 2:
        print(json.dumps({"erro": "Nenhum dado recebido. Passe o JSON como argumento."}))
        sys.exit(1)

    try:
        dados_brutos = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(json.dumps({"erro": "JSON inválido recebido."}))
        sys.exit(1)

    # 1. Calcula todas as métricas
    metricas = calcular_metricas(dados_brutos)

    # 2. Classifica o status da campanha
    status, emoji, acao = classificar_status(metricas)

    # 3. Monta a mensagem de alerta
    mensagem = formatar_mensagem(metricas, status, emoji, acao)

    # 4. Retorna o resultado como JSON para o n8n processar
    resultado = {
        "status"   : status,
        "emoji"    : emoji,
        "acao"     : acao,
        "mensagem" : mensagem,
        "metricas" : metricas,
    }

    print(json.dumps(resultado, ensure_ascii=False))


if __name__ == "__main__":
    main()