import json
import sys

'''
AD-GUARDIAN — Processador de Métricas de Campanha
Recebe um JSON via argumento, calcula métricas e retorna
um JSON com status e mensagem de alerta.

⚠️ PROTÓTIPO: este script não roda automaticamente. A fonte de
verdade em produção é o node "Code in JavaScript" dentro do
workflow n8n (docs/workflow.json). Este arquivo existe apenas
para testes manuais soltos via terminal.
'''

# (ajuste conforme  nicho)
ROAS_MINIMO      = 1.5   # Abaixo disso = prejuízo em muitos modelos
ROAS_META        = 3.0   # Meta saudável de retorno
GASTO_MINIMO     = 30.0  # Só alerta "Crítico"/"Escalável" se já gastou pelo menos R$30
CTR_MINIMO       = 1.0   # CTR abaixo de 1% = anúncio fraco


def parse_numero_br(valor) -> float:
    """
    Converte valores numéricos vindos da planilha para float, aceitando
    tanto formato brasileiro (30,50 ou 1.234,56) quanto padrão (30.50).
    Sem isso, "30,50" vindo da planilha vira 30 silenciosamente.
    """
    if valor is None or valor == "":
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()

    if "," in texto and "." in texto:
        # 1.234,56 -> remove separador de milhar, troca vírgula por ponto
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        # 30,50 -> troca vírgula por ponto
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return 0.0


def calcular_metricas(dados: dict) -> dict:
    """
    Recebe os dados brutos da planilha e calcula todas as métricas.
    Retorna um dicionário com os valores calculados.
    """
    investimento  = parse_numero_br(dados.get("Investimento", 0))
    cliques       = int(dados.get("Cliques", 0))
    vendas        = int(dados.get("Vendas", 0))
    valor_venda   = parse_numero_br(dados.get("Valor_Venda", 0))

    # Receita total gerada pelas vendas
    receita = vendas * valor_venda

    # ROAS = Receita / Investimento  (ex: 3.0 = R$3 gerados para cada R$1 gasto)
    roas = round(receita / investimento, 2) if investimento > 0 else 0

    # CPC = Investimento / Cliques  (custo médio por clique)
    cpc = round(investimento / cliques, 2) if cliques > 0 else 0

    # Taxa de conversão = (Vendas / Cliques) * 100 — percentual de cliques
    # que viraram venda. Não confundir com CTR (Cliques/Impressões), que
    # não é calculado aqui pois a planilha não traz o dado de Impressões.
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

    # ESCALÁVEL: ROAS acima da meta, lucro positivo E gasto relevante
    # (sem o gasto mínimo, uma única venda de sorte com pouquíssimo
    # investimento já dispararia um ROAS alto e um alerta falso de escala)
    if roas >= ROAS_META and lucro > 0 and investimento >= GASTO_MINIMO:
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
    # Uso manual via terminal (fora do n8n), para testar a lógica isoladamente:
    # python script.py '{"Campanha": "Curso Trader", ...}'
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

    # 4. Retorna o resultado como JSON para inspeção manual
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