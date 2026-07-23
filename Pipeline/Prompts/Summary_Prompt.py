PROMPT_ANTECEDENTES = """
Atua como um Médico Sénior. O teu objetivo é consolidar a lista de Antecedentes Pessoais e Diagnósticos do paciente.

DADOS EXTRAÍDOS:
{extracted_data}

REGRAS CRÍTICAS:
1. DESDUPLICAÇÃO E INFERÊNCIA CLÍNICA: É estritamente proibido listar a mesma doença mais do que uma vez. Deves analisar, inferir e fundir diagnósticos sinónimos, siglas, abreviaturas ou variações de escrita na nomenclatura médica mais completa. Se houver evolução clínica, mantém APENAS o diagnóstico evoluído.
2. Campo 'data_diagnostico': para cada diagnóstico, procura entre todos os registos onde ele aparece.
   - Se algum desses registos tiver 'data_diagnostico' preenchida, usa essa data (sem asterisco).
   - Se nenhum tiver, usa a data do registo mais antigo onde esse diagnóstico aparece, e acrescenta um asterisco no fim (ex: "14-Jul-2023*") a indicar que é uma data estimada.
3. FILTRAGEM DE DOENÇAS CRÓNICAS ATIVAS: Mantém exclusivamente diagnósticos confirmados que representem **doenças crónicas ativas, sistémicas e de seguimento médico contínuo**. Uma doença crónica válida exige que o doente mantenha vigilância clínica regular ou terapêutica médica permanente para essa mesma condição.
4. REGRAS DE EXCLUSÃO ABSOLUTA (Aplica a cada diagnóstico por ordem lógica):
   a) Exclui qualquer diagnóstico classificado como agudo, intermitente, subagudo ou suspeita.
   b) Exclui qualquer evento patológico agudo, traumático, hemorrágico, infecioso ou cirúrgico que tenha ocorrido e sido resolvido, tratado ou curado no passado (mesmo que conste na história pregressa do doente, se o episódio agudo terminou, não é uma doença crónica ativa).
   c) Exclui qualquer neoplasia ou lesão oncológica localizada do passado que tenha sido completamente tratada, excisada ou resolvida cirurgicamente. Antecedentes oncológicos tratados não entram como doenças crónicas ativas de ambulatório.
   d) Exclui qualquer sintoma, sinal, queixa isolada, achado imagiológico descritivo (ex: alterações estruturais ou atrofias isoladas) ou desvio laboratorial.
   e) Exclui rigorosamente qualquer diagnóstico que seja, clinicamente, uma manifestação, consequência, sequela ou complicação secundária de outra doença de base já presente na lista. Mantém apenas a patologia primária principal.
   Em caso de dúvida fundamentada sobre a natureza estritamente crónica e ativa da doença, EXCLUI o diagnóstico.
5. Devolve EXCLUSIVAMENTE o objeto JSON válido abaixo.

FORMATO DE SAÍDA OBRIGATÓRIO:
{{
  "antecedentes": [
    {{
      "diagnostico": "Nome da Doença",
      "tipo": "Confirmado ou Suspeita",
      "temporalidade": "Crónico",
      "desde": "Data exata calculada OU Data do registo com asterisco*"
    }}
  ]
}}
"""

PROMPT_MEDICACAO = """
Atua como um Médico Sénior. O teu objetivo é consolidar a Medicação Habitual e as Alergias do paciente.

DADOS EXTRAÍDOS:
{extracted_data}

REGRAS CRÍTICAS PARA MEDICAÇÃO:
1. FUSÃO INTELIGENTE: Cria uma única entrada por fármaco. Cada fármaco entra só uma vez na lista final.
2. O QUE VAIS RECEBER: para consultas externas, os 2 registos mais recentes de cada especialidade; para a urgência, TODOS os registos dentro do último ano (um único internamento é muitas vezes dividido em vários registos, por vezes até com nomes de especialidade diferentes — ex: HUC-URG_NEUROLOGIA, HUC-URG_CIRURGIA_CARDIOTORÁCICA — trata-os como parte do mesmo episódio de urgência). Cada fármaco tem 'tipo': "habitual", "administrada" ou "suspensa" — mas um fármaco com tipo "administrada" pode ainda assim representar uma alteração duradoura (ex: uma substituição ou início de tratamento continuado, descrito no campo 'observações'), não apenas uma dose pontual. Lê sempre 'observações' antes de decidires excluir só por causa do tipo.
3. Base: o registo mais recente com pelo menos um fármaco "habitual" (ou "administrada" que na prática representa uma mudança duradoura). Salta registos sem isso, seja qual for a especialidade.
4. Se a medicação da base cobrir só doenças da própria especialidade (ex: só antiepiléticos num registo de Neurologia) é PARCIAL: guarda-a e completa com o registo mais recente a seguir — primeiro procura outro registo da MESMA especialidade (se tiveres mais do que um), depois de outra especialidade — até encontrares uma lista completa ou esgotares 1 ano. Se cobrir a medicação geral do doente, é COMPLETA: pára aqui.
5. Antes de acrescentar um fármaco vindo de um registo mais antigo, confirma que não aparece como "suspensa" nalgum registo mais recente (até à base). Se aparecer, não incluas. Da mesma forma, se um fármaco for substituído por outro com a mesma indicação (ex: "passa a fazer X em vez de Y", "Y é descontinuado e inicia X"), considera Y suspenso e não o incluas, mesmo que nenhum registo o marque explicitamente como "suspensa".
6. EXCLUSÃO DE TRATAMENTOS TÓPICOS E DE CURTA DURAÇÃO: Medicação habitual implica toma continuada, regular e sem data de fim prevista (tipicamente diária). Exclui da lista final:
   - tratamentos tópicos/locais (cremes, pomadas, aplicações sobre a pele ou lesões, ex: para queratoses, feridas);
   - tratamentos com fim definido ou previsto (ex: "até à consulta", um ciclo curto, um tratamento pontual para resolver um problema específico e não recorrente).
   Em caso de dúvida sobre se um fármaco é de toma continuada ou só um tratamento pontual, exclui-o.
7. INFERÊNCIA DE INDICAÇÃO: Se 'indicacao' estiver vazia, infere o motivo com base no contexto clínico. Não deixes vazio.
8. Regra de Rastreabilidade: O campo 'diario_origem' deve conter estritamente o formato: "NOME DA ESPECIALIDADE - DATA".
9. DOSAGEM vs. POSOLOGIA — DEFINIÇÃO, PRIORIDADE E CORREÇÃO:
   - DOSAGEM: apenas concentração/quantidade (ex: "5mg", "10ml"). NUNCA um regime de toma.
   - POSOLOGIA: apenas regime de toma/frequência (ex: "1cp/dia", "2id", "ao deitar"). NUNCA uma concentração.
   - Se um destes campos vier com o valor do outro misturado (ex: "dosagem" a conter "3 comp/dia", ou qualquer um dos dois a incluir palavras como "comp", "toma", "jejum", "vezes"), corrige automaticamente: move o conteúdo para o campo certo, e deixa "N/A" no campo onde não houver informação real.
   - Se o mesmo fármaco aparecer em mais do que um registo, usa sempre a dosagem/posologia do registo mais recente.
10. TRADUÇÃO DE ABREVIATURAS DE POSOLOGIA: "id" sozinho = "1 vez ao dia". "2id" = "2 vezes ao dia", "3id" = "3 vezes ao dia", "4id" = "4 vezes ao dia" — o número antes do "id" multiplica a frequência; nunca o ignores nem o confundas com "id" sozinho.
11. PROIBIÇÃO DE VALORES POR OMISSÃO: nunca assumas, infiras ou "adivinhes" uma dosagem ou posologia que não esteja explicitamente presente nos dados fornecidos para aquele fármaco — mesmo que "1 vez ao dia" seja a frequência mais comum na prática clínica em geral. Sem informação real em nenhum dos registos disponíveis, usa "N/A" nesse campo, independentemente de outros campos desse fármaco (indicação, nome) estarem preenchidos.

REGRAS CRÍTICAS PARA ALERGIAS (RASTREABILIDADE):
1. Lista todas as alergias ou reações adversas medicamentosas.
2. DESDUPLICAÇÃO CLÍNICA: Se a mesma alergia (ou alergia à mesma substância) for referida em vários registos, deves fundi-la numa única entrada na lista final (NÃO repitas alergias).
3. REGISTO DE ORIGEM: Identifica o cabeçalho ("--- IDENTIFICAÇÃO E DATA DO REGISTO ---") onde a alergia aparece. Se a mesma alergia aparecer em vários registos de datas diferentes, guarda OBRIGATORIAMENTE o registo com a data mais ANTIGA no campo 'registo_origem', pois esse é o diagnóstico original.

FORMATO DE SAÍDA OBRIGATÓRIO (JSON VÁLIDO):
{{
  "medicacao": [
    {{
      "farmaco": "Nome",
      "dosagem": "Dosagem",
      "posologia": "Posologia",
      "indicacao": "Motivo",
      "diario_origem": "Nome do diário de origem"
    }}
  ],
  "alergias": [
    {{
      "substancia": "Nome da substância ou alergia",
      "reacao": "Descrição da reação",
      "registo_origem": "Nome do diário com a data mais antiga onde foi referida"
    }}
  ]
}}
"""

PROMPT_EXAMES = """
Atua como um Médico Sénior. O teu objetivo é consolidar os Meios Complementares de Diagnóstico (MCDT).

DADOS RECEBIDOS:
{extracted_data}

REGRAS CRÍTICAS:
1. FILTRAGEM: A tua entrada contém exames classificados como 'exame_objetivo' e 'exame_complementar'. Deves ignorar COMPLETAMENTE qualquer exame cuja categoria seja 'exame_objetivo'. Mantém apenas os classificados como 'exame_complementar'.
2. VAZIO: Se o diário não contiver exames complementares (apenas objetivos ou nada), deves responder estritamente "SEM_DADOS" e não gerar nenhum objeto JSON.
3. TRATAMENTO DOS EXAMES (RIGOR ABSOLUTO DE REGISTO): 
   - A) VALORES ANALÍTICOS (Numéricos): Devem ser transcrevidos na ÍNTEGRA, valor a valor, parâmetro a parâmetro. É terminantemente proibido omitir ou resumir valores analíticos.
   - B) RESULTADOS QUALITATIVOS OU RESUMIDOS (Ex: "BQ: N", "Urina tipo: N", "Normal", "Negativo"): NUNCA os ignores ou elimines por não terem números. Se o resultado vier descrito como "N" (Normal) ou com uma menção qualitativa global, deves mantê-lo obrigatoriamente no JSON final indicando explicitamente esse estado (ex: "Normal / Sem alterações").
   - C) RELATÓRIOS (Imagiologia, Endoscopias, etc.): Extrair APENAS os achados patológicos mais importantes e a conclusão clínica principal.
4. INTEGRIDADE: Se um exame for 'exame_complementar', ele DEVE aparecer obrigatoriamente no JSON final. Não podes descartar nenhum painel analítico sob nenhuma circunstância.

- TIPO DE EXAME: Indica apenas a categoria limpa (ex: "Bioquímica", "Urina Tipo II", "Hemograma"). Nunca repitas o nome do exame dentro do campo de resultado se isso gerar redundância.
FORMATO DE SAÍDA OBRIGATÓRIO (JSON VÁLIDO):
{{
  "exames": [
    {{
      "nome": "Data e Especialidade original",
      "data": "DD/MM/YYYY",
      "tipo_exame": "Ex: Hemograma ou Ecografia Abdominal",
      "resultado": "VALORES COMPLETOS OU SÍNTESE CLÍNICA DO RELATÓRIO"
    }}
  ]
}}

IMPORTANTE: A tua resposta deve conter APENAS o objeto JSON pedido, começando em "{{" e terminando em "}}". Não escrevas nenhum texto, explicação ou título antes ou depois do JSON.
"""

PROMPT_PLANO = """
Atua como um Médico Sénior. O teu objetivo é interpretar e redigir o plano terapêutico ativo do paciente com base na última consulta de CADA especialidade no último ano.

DADOS EXTRAÍDOS (Agrupados por Especialidade):
{extracted_data}

REGRAS CRÍTICAS:
1. PROCESSAMENTO TOTAL: Deves ler CADA bloco identificado por ###ESPECIALIDADE.
2. Não podes ignorar nenhuma especialidade presente nos dados.
3. Para cada especialidade, extrai a data e sintetiza o plano.
4. Devolve EXCLUSIVAMENTE um JSON com uma lista de planos (um objeto por especialidade).

FORMATO DE SAÍDA OBRIGATÓRIO:
{{
  "plano": [
    {{
      "especialidade": "Nome da Especialidade",
      "data": "DD/MM/YYYY",
      "conteudo": "Síntese do plano."
    }}
  ]
}}
"""