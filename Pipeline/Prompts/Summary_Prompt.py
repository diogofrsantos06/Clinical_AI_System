PROMPT_ANTECEDENTES = """
Atua como um Médico Sénior. O teu objetivo é consolidar a lista de Antecedentes Pessoais e Diagnósticos do paciente.

DADOS EXTRAÍDOS:
{extracted_data}

REGRAS CRÍTICAS:
1. DESDUPLICAÇÃO E INFERÊNCIA CLÍNICA: É estritamente proibido listar a mesma doença mais do que uma vez. Deves analisar, inferir e fundir diagnósticos sinónimos, siglas, abreviaturas ou variações de escrita na nomenclatura médica mais completa. Se houver evolução clínica, mantém APENAS o diagnóstico evoluído.
2. Campo 'data_diagnostico': para cada diagnóstico, procura entre todos os registos onde ele aparece.
   - Se algum desses registos tiver 'data_diagnostico' preenchida, usa essa data (sem asterisco).
   - Se nenhum tiver, usa a data do registo mais antigo onde esse diagnóstico aparece, e acrescenta um asterisco no fim (ex: "14-Jul-2023*") a indicar que é uma data estimada.
3. FILTRAGEM DE DOENÇAS CRÓNICAS ATIVAS: Mantém exclusivamente diagnósticos que, com base no teu conhecimento clínico geral sobre a doença nomeada, representem **doenças crónicas ativas e sistémicas, do tipo que por natureza exige seguimento médico contínuo** (ex.: doenças metabólicas, cardiovasculares, neurológicas degenerativas, autoimunes). Não confies cegamente no campo 'temporalidade' fornecido — usa o teu próprio julgamento clínico sobre o nome da doença como verificação adicional. Se o nome da doença corresponder claramente a um sintoma, achado ou evento transitório, mesmo que 'temporalidade' venha marcado como "cronico", trata-o de acordo com as regras de exclusão abaixo.
4. REGRAS DE EXCLUSÃO ABSOLUTA (Aplica a cada diagnóstico por ordem lógica):
   a) Exclui qualquer diagnóstico classificado com 'tipo' = 'agudo' ou 'suspeita'.
   b) Exclui qualquer diagnóstico que, pelo nome, corresponda a um evento agudo, traumático, hemorrágico, infecioso ou cirúrgico tipicamente autolimitado ou resolúvel (mesmo que 'temporalidade' venha marcado como "cronico" por erro de extração).
   c) NEOPLASIAS E LESÕES ONCOLÓGICAS: mantém sempre qualquer diagnóstico de natureza oncológica ou neoplásica, independentemente de estar tratado, excisado ou resolvido, e independentemente de ser um único registo ou vários. O historial oncológico mantém relevância clínica a longo prazo mesmo após tratamento curativo, pelo que nunca deve ser excluído apenas por já não estar ativo.
   d) ACHADOS DESCRITIVOS E IMAGIOLÓGICOS: exclui qualquer diagnóstico cujo nome descreva um achado de exame de imagem ou um sinal isolado, em vez de uma doença clínica ativa e tratável. Isto inclui explicitamente nomes que referem alterações estruturais, atrofias, leucoencefalopatias, leucoaraiose, alterações isquémicas inespecíficas, ou qualquer outra formulação que descreva o que um exame mostra, em vez de um diagnóstico. Este tipo de achado NUNCA deve ser listado, mesmo que o nome esteja formulado como se fosse um diagnóstico.
   e) CONDIÇÕES PSICOSSOCIAIS, COMPORTAMENTAIS E DE CONSUMO DE SUBSTÂNCIAS: aplica um critério mais rigoroso a este tipo de diagnóstico. Só o mantém se, pelo teu conhecimento clínico, a condição nomeada implicar tipicamente acompanhamento médico ou psiquiátrico estruturado e permanente por si só (ex.: uma perturbação psiquiátrica major com necessidade de terapêutica continuada). Não assumas cronicidade apenas porque a categoria geral (comportamental, psicossocial, uso de substâncias) é frequentemente associada a cronicidade — analisa a condição específica nomeada.
   f) Exclui rigorosamente qualquer diagnóstico que seja, clinicamente, uma manifestação, consequência, sequela ou complicação secundária de outra doença de base já presente na lista. Mantém apenas a patologia primária principal.
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

IMPORTANTE: A tua resposta deve conter APENAS o objeto JSON pedido, começando em "{{" e terminando em "}}". Não escrevas nenhum texto, explicação ou título antes ou depois do JSON.
"""

PROMPT_MEDICACAO = """
Atua como um Médico Sénior. O teu objetivo é consolidar a Medicação Habitual e as Alergias do paciente.

DADOS EXTRAÍDOS:
{extracted_data}

REGRAS CRÍTICAS PARA MEDICAÇÃO:
1. FUSÃO INTELIGENTE: cria uma única entrada por fármaco. Cada fármaco entra só uma vez na lista final.
2. O QUE VAIS RECEBER: todos os diários com medicação de cada especialidade (incluindo urgência), dentro do último ano — não é uma lista já filtrada, tens o histórico completo à disposição.
3. ENCONTRA A BASE: percorre os diários do mais recente para o mais antigo. O primeiro que tiver pelo menos um fármaco "habitual" é a tua base — ignora diários sem nenhuma medicação "habitual", seja qual for a especialidade.
4. LISTA JÁ COMPLETA POR ESPECIALIDADE: para cada especialidade, olha primeiro para o seu diário mais recente. Se esse diário já listar mais do que 1-2 fármacos (indício de que é uma lista completa da medicação relevante para essa especialidade), usa-a diretamente e não precisas de recuar a diários mais antigos DA MESMA especialidade à procura de mais fármacos. Só recuas a um diário mais antigo dessa especialidade se o mais recente não tiver nenhuma lista de medicação, ou só tiver 1-2 fármacos isolados (sinal de lista incompleta).
5. FUSÃO ENTRE ESPECIALIDADES: depois de determinares a lista de cada especialidade (regra 4), junta tudo, especialidade a especialidade — cada uma pode contribuir com fármacos que as outras não mencionam.
6. ASTERISCO: um fármaco só fica SEM asterisco se estiver escrito no "registo mais recente" (ponto 3). Todos os outros fármacos (vindos de qualquer outro registo, de qualquer especialidade) levam um asterisco no fim do nome (ex: "Levotiroxina*"). Não escrevas nada sobre isto no campo 'indicacao'. Aplica sempre da mesma forma a fármacos com o mesmo 'diario_origem' — nunca uns com asterisco e outros sem, vindos do mesmo registo.
7. EXCLUSÃO DE SUSPENSÕES E TRATAMENTOS TEMPORÁRIOS: exclui por completo (não incluas de forma nenhuma, nem com asterisco) qualquer fármaco que:
   - esteja explicitamente identificado como suspenso, descontinuado, ou substituído por outro, em qualquer um dos diários recebidos (mesmo que essa informação só apareça no plano, não na lista de medicação);
   - tenha uma duração de tratamento definida ou prevista (ex.: "até à consulta", "durante um mês", um ciclo curto) — só entra na lista final medicação verdadeiramente continuada, sem data de fim prevista;
   - seja um tratamento tópico/local (cremes, pomadas, aplicações sobre a pele ou lesões).
   Em caso de dúvida sobre se é suspensão/temporário, exclui o fármaco.
8. PRIORIDADE DE DOSAGEM/POSOLOGIA: quando o mesmo fármaco aparece em mais do que um diário, a dosagem e a posologia devem vir sempre do diário mais recente onde esse fármaco aparece — nunca de um diário mais antigo, mesmo que o mais antigo tenha mais detalhe. Apenas se o diario mais recente não tiver indicações sobre os campos é que deves retirar do diario anterior mais recente que tiver.
9. INFERÊNCIA DE INDICAÇÃO: se 'indicacao' estiver vazia (e não se aplicar a regra 6), infere o motivo pelo contexto clínico. Não deixes vazio.
10. RASTREABILIDADE: o campo 'diario_origem' deve conter estritamente o formato "NOME DA ESPECIALIDADE - DATA", referente ao diário de onde veio a dosagem/posologia usada (regra 8).
11. DOSAGEM vs. POSOLOGIA: DOSAGEM = só concentração (ex.: "5mg"). POSOLOGIA = só regime de toma (ex.: "1cp/dia", "2id"). Nunca misturar; corrige automaticamente se vierem trocadas ou com o valor do outro campo incluído.
12. TRADUÇÃO DE ABREVIATURAS: "id" sozinho = "1 vez ao dia". "2id" = "2 vezes ao dia", "3id" = "3 vezes ao dia" — o número antes do "id" multiplica a frequência, nunca o ignores.
13. PROIBIÇÃO DE VALORES POR OMISSÃO: nunca assumas uma dosagem ou posologia que não esteja explicitamente presente nos dados para aquele fármaco. Sem informação real, usa "N/A".

REGRAS CRÍTICAS PARA ALERGIAS (RASTREABILIDADE):
1. Lista todas as alergias ou reações adversas medicamentosas.
2. DESDUPLICAÇÃO CLÍNICA: se a mesma alergia for referida em vários registos, funde-a numa única entrada.
3. REGISTO DE ORIGEM: identifica o cabeçalho ("--- IDENTIFICAÇÃO E DATA DO REGISTO ---") onde a alergia aparece. Se aparecer em vários registos, guarda no campo 'registo_origem' o registo com a data mais ANTIGA.

FORMATO DE SAÍDA OBRIGATÓRIO (JSON VÁLIDO):
{{
  "medicacao": [
    {{
      "farmaco": "Nome (com asterisco no fim se aplicável, ex: Levotiroxina*)",
      "dosagem": "Dosagem",
      "posologia": "Posologia",
      "indicacao": "Motivo (inclui a nota de incerteza da regra 6, se aplicável)",
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

IMPORTANTE: A tua resposta deve conter APENAS o objeto JSON pedido, começando em "{{" e terminando em "}}". Não escrevas nenhum texto, explicação ou título antes ou depois do JSON.
"""

PROMPT_EXAMES = """
Atua como um Médico Sénior. O teu objetivo é consolidar os Meios Complementares de Diagnóstico (MCDT).

DADOS RECEBIDOS:
{extracted_data}

REGRAS CRÍTICAS:
1. FILTRAGEM: A tua entrada contém exames classificados como 'exame_objetivo' e 'exame_complementar'. Deves ignorar COMPLETAMENTE qualquer exame cuja categoria seja 'exame_objetivo'. Mantém apenas os classificados como 'exame_complementar'.
2. VAZIO: Se o diário não contiver exames complementares (apenas objetivos, nada, ou só exames excluídos pela regra 5), deves responder estritamente "SEM_DADOS" e não gerar nenhum objeto JSON.
3. TRATAMENTO DOS EXAMES (RIGOR ABSOLUTO DE REGISTO): 
   - A) VALORES ANALÍTICOS (Numéricos): Devem ser transcrevidos na ÍNTEGRA, valor a valor, parâmetro a parâmetro. É terminantemente proibido omitir ou resumir valores analíticos.
   - B) RESULTADOS QUALITATIVOS OU RESUMIDOS (Ex: "BQ: N", "Urina tipo: N", "Normal", "Negativo"): NUNCA os ignores ou elimines por não terem números. Se o resultado vier descrito como "N" (Normal) ou com uma menção qualitativa global, deves mantê-lo obrigatoriamente no JSON final indicando explicitamente esse estado (ex: "Normal / Sem alterações").
   - C) RELATÓRIOS (Imagiologia, Endoscopias, etc.): Extrair APENAS os achados patológicos mais importantes e a conclusão clínica principal.
4. INTEGRIDADE: Se um exame for 'exame_complementar', ele DEVE aparecer obrigatoriamente no JSON final. Não podes descartar nenhum painel analítico sob nenhuma circunstância.
5. EXCLUSÃO DE EXAMES SEM RESULTADO: Exclui por completo (não incluas no JSON final) qualquer exame cujo "resultado" não seja, de facto, um achado clínico — ou seja, exclui sempre que o texto disponível só indicar que o exame:
   - ainda não foi realizado (ex: "Pendente", "A realizar dentro de um mês", "Não disponível durante a noite");
   - foi apenas pedido/requisitado, sem resultado (ex: "Pedido", "Marcado para 15 de junho", "Tem RMN marcada");
   - descreve só o motivo/contexto de ter sido pedido, sem apresentar o achado em si (ex: "Realizado na sequência de episódios de mal estar geral, hipersudorese e sensação de desmaio" — isto é a justificação clínica do pedido, não o resultado).
   Um exame só entra no JSON final se o texto contiver o resultado/achado real (mesmo que seja "Normal" ou "Sem alterações", como já previsto na regra 3-B). Em caso de dúvida sobre se é resultado ou não, exclui.

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
1. PROCESSAMENTO TOTAL: Deves ler CADA bloco identificado por ###ESPECIALIDADE, sem exceção.
2. RELEVÂNCIA CLÍNICA (FILTRO OBRIGATÓRIO): Só inclui uma especialidade na lista final se o seu plano contiver pelo menos uma decisão terapêutica ativa e concreta — início, alteração, suspensão ou manutenção explícita de um tratamento/medicação, ou uma indicação clínica concreta a seguir (ex: "inicia levetiracetam 500mg 2id"). 
   Exclui, e não incluas de forma nenhuma, especialidades cujo conteúdo seja apenas:
   - agendamento de consultas ou datas de seguimento (ex: "Consulta agendada dia 06/07/2026", "Alta para o domicílio");
   - encaminhamentos/referenciações sem outra decisão terapêutica associada (ex: "Encaminhamento para consulta de ortopedia");
   - informação prestada a familiares, explicações de sinais de alarme, ou instruções administrativas de alta (ex: "Explicação de sinais de alarme para retorno à urgência");
   - afirmações de ausência de indicação para tratamento (ex: "Sem indicação atual para tratamento com Botox");
   - vigilância genérica sem outra ação associada (ex: "Sem lesões novas suspeitas. Continuação de vigilância").
   Se, depois deste filtro, uma especialidade não tiver nenhum conteúdo clinicamente relevante, OMITE essa especialidade por completo da lista

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

IMPORTANTE: A tua resposta deve conter APENAS o objeto JSON pedido, começando em "{{" e terminando em "}}". Não escrevas nenhum texto, explicação ou título antes ou depois do JSON.
"""