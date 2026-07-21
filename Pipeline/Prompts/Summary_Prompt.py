PROMPT_ANTECEDENTES = """
Atua como um Médico Sénior. O teu objetivo é consolidar a lista de Antecedentes Pessoais e Diagnósticos do paciente.

DADOS EXTRAÍDOS:
{extracted_data}

REGRAS CRÍTICAS:
1. DESDUPLICAÇÃO E INFERÊNCIA CLÍNICA: É estritamente proibido listar a mesma doença mais do que uma vez. Deves analisar, inferir e fundir diagnósticos sinónimos, siglas, abreviaturas ou variações de escrita. Escolhe sempre fundi-los na nomenclatura médica mais completa e atualizada. Se houver evolução clínica (ex: "Nódulo" -> "Carcinoma"), mantém APENAS o diagnóstico evoluído.
2. Campo 'data_diagnostico': para cada diagnóstico, procura entre todos os registos onde ele aparece.
   - Se algum desses registos tiver 'data_diagnostico' preenchida, usa essa data (sem asterisco) — é a informação mais fiável que existe.
   - Se nenhum tiver, usa a data do registo mais antigo (indicada no cabeçalho "--- IDENTIFICAÇÃO E DATA DO REGISTO ---") onde esse diagnóstico aparece, e acrescenta um asterisco no fim (ex: "14-Jul-2023*") a indicar que é uma data estimada.
3. Mantém apenas diagnósticos confirmados que correspondam a doenças crónicas ativas e independentes.
4. REGRAS DE EXCLUSÃO OBRIGATÓRIAS: Antes de incluíres qualquer diagnóstico na lista final, aplica OBRIGATORIAMENTE cada uma das regras seguintes a esse diagnóstico. Estas regras definem CATEGORIAS gerais, não uma lista fechada de doenças — aplica sempre o critério pela natureza da informação, independentemente do nome exato da doença ou da palavra usada no texto original.
   a) Exclui qualquer diagnóstico agudo, e qualquer diagnóstico classificado como suspeita (não confirmado).
   b) Exclui qualquer sintoma, sinal ou queixa clínica que não seja, em si, o nome formal de uma entidade clínica. Só é exceção quando o próprio texto nomeia essa queixa como uma entidade crónica independente e a trata como diagnóstico, não como sintoma.
   c) Exclui qualquer valor, resultado ou achado de exame (imagem ou laboratorial) que seja descrito apenas como uma medida, alteração ou desvio do normal (incluindo explicitamente déficits nutricionais ou laboratoriais isolados, como deficiências de vitaminas ex: Vitamina E, ou anemias leves sem doença de base associada), sem que o texto o trate como uma patologia crónica major.
   d) Exclui qualquer lesão traumática, ortopédica ou reumatológica regional/isolada (incluindo tendinopatias, bursites e trocanterites).
   e) Exclui qualquer infeção já tratada ou resolvida, sequela, estado pós-operatório, ou lesões benignas passadas que já foram totalmente resolvidas/excisadas (incluindo pólipos uterinos, intestinais ou cutâneos removidos no passado).
   f) Exclui qualquer diagnóstico que seja, clinicamente, uma manifestação ou complicação reconhecida de outro diagnóstico já presente nesta mesma lista, para este mesmo doente. Nestes casos, mantém apenas o diagnóstico principal (a doença de base), nunca as suas manifestações.
   Em caso de dúvida sobre qualquer uma destas regras, exclui o diagnóstico.
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
2. Cada registo é a visita mais recente de uma especialidade (a urgência pode juntar várias notas do mesmo episódio). Cada fármaco tem 'tipo': "habitual" ou "suspensa".
3. Base: o registo mais recente com pelo menos um fármaco "habitual" (salta os que não têm, seja qual for a especialidade).
4. Se a medicação da base cobrir só doenças da própria especialidade (ex: só antiepiléticos num registo de Neurologia) é PARCIAL: guarda-a e repete esta análise no registo seguinte mais recente de OUTRA especialidade, até encontrares uma lista completa ou esgotares 1 ano. Se cobrir a medicação geral do doente, é COMPLETA: pára aqui.
5. Antes de acrescentar um fármaco vindo de um registo mais antigo, confirma que não aparece como "suspensa" nalgum registo mais recente (até à base). Se aparecer, não incluas.
6. INFERÊNCIA DE INDICAÇÃO: Se 'indicacao' estiver vazia, infere o motivo com base no contexto clínico. Não deixes vazio.
7. Regra de Rastreabilidade: O campo 'diario_origem' deve conter estritamente o formato: "NOME DA ESPECIALIDADE - DATA".
8. PRIORIDADE: A Dosagem e Posologia devem vir do registo mais recente.
9. PROIBIÇÃO DE SOBREPOSIÇÃO: É estritamente proibido incluir qualquer valor de dosagem (mg, g, ml, mcg) no campo 'posologia'. 
   - DOSAGEM: Deve conter APENAS valores de concentração/quantidade seguidos de unidade de medida (ex: "5mg", "500mg", "10ml"). 
   - POSOLOGIA: Deve conter APENAS regime de toma/frequência (ex: "1 comp/dia", "ao deitar", "3 comp/dia").
10. AVALIAÇÃO DE ERRO: 
  - Se o campo 'dosagem' contiver palavras como "comp", "dia", "toma", "jejum" ou "vezes", o conteúdo desse campo é, na verdade, POSOLOGIA.
  - Deves mover automaticamente esse conteúdo para o campo 'posologia' e deixar o campo 'dosagem' vazio (ou "N/A") se não existir uma concentração real.
11. É terminantemente proibido manter instruções de toma (ex: "3 comp/dia" ou "3 gotas/dia") no campo 'dosagem'.
12. TRADUÇÃO DE ABREVIATURAS DE POSOLOGIA: Interpreta corretamente as abreviaturas médicas latinas comuns: "id" significa "1 vez ao dia" (diário) e NUNCA "3 vezes/dia". Respeita rigorosamente a posologia unitária original sem extrapolar frequências falsas.

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