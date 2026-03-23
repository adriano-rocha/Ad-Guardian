const itens = $input.all();
const ROAS_MINIMO = 1.5;
const ROAS_META   = 3.0;
const GASTO_MIN   = 30.0;

const resultados = [];

for (let i = 0; i < itens.length; i++) {
  const dados = itens[i].json;
  const investimento  = parseFloat(dados.Investimento) || 0;
  const cliques       = parseInt(dados.Cliques)        || 0;
  const vendas        = parseInt(dados.Vendas)         || 0;
  const valorVenda    = parseFloat(dados.Valor_Venda)  || 0;
  const receita       = vendas * valorVenda;
  const roas          = investimento > 0 ? receita / investimento : 0;
  const cpc           = cliques > 0 ? investimento / cliques : 0;
  const taxaConversao = cliques > 0 ? (vendas / cliques) * 100 : 0;
  const lucroLiquido  = receita - investimento;

  let status, emoji, acao;
  if (roas < ROAS_MINIMO && investimento >= GASTO_MIN) {
    status = "Critico";  emoji = "🔴";  acao = "PAUSAR imediatamente";
  } else if (roas < ROAS_META && investimento >= GASTO_MIN) {
    status = "Atencao";  emoji = "🟡";  acao = "Revisar criativos";
  } else if (roas >= ROAS_META && lucroLiquido > 0) {
    status = "Escalavel"; emoji = "🟢"; acao = "ESCALAR - aumentar orcamento";
  } else {
    status = "Monitorar"; emoji = "🔵"; acao = "Aguardar mais dados";
  }

  const mensagem = `${emoji} AD-GUARDIAN ALERTA
Campanha: ${dados.Campanha}
Data: ${dados.Data}
Investimento: R$ ${investimento.toFixed(2)}
Cliques: ${cliques}
Vendas: ${vendas}
Receita: R$ ${receita.toFixed(2)}
ROAS: ${roas.toFixed(2)}x
CPC: R$ ${cpc.toFixed(2)}
Conv. Rate: ${taxaConversao.toFixed(2)}%
Lucro Liquido: R$ ${lucroLiquido.toFixed(2)}
STATUS: ${status}
ACAO: ${acao}`;

  resultados.push({
    json: {
      status, emoji, acao, mensagem,
      metricas: {
        campanha: dados.Campanha,
        data: dados.Data,
        investimento, cliques, vendas, valorVenda,
        receita: parseFloat(receita.toFixed(2)),
        roas: parseFloat(roas.toFixed(2)),
        cpc: parseFloat(cpc.toFixed(2)),
        taxaConversao: parseFloat(taxaConversao.toFixed(2)),
        lucroLiquido: parseFloat(lucroLiquido.toFixed(2))
      }
    }
  });
}

return resultados;