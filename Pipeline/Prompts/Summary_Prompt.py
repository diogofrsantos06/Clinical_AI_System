PROMPT_ANTECEDENTES = """
Atua como um Médico Sénior. O teu objetivo é consolidar a lista de Antecedentes Pessoais e Diagnósticos do paciente.

DADOS EXTRAÍDOS:
{extracted_data}

REGRAS CRÍTICAS:
1. FOCO CRÓNICO: Extrai APENAS diagnósticos crónicos e patologias ativas relevantes. IGNORA completamente diagnósticos agudos ou resolvidos.
2. DESDUPLICAÇÃO E INFERÊNCIA CLÍNICA: É estritamente proibido listar a mesma doença mais do que uma vez. Deves analisar, inferir e fundir diagnósticos sinónimos, siglas, abreviaturas ou variações de escrita. Escolhe sempre fundi-los na nomenclatura médica mais completa e atualizada. Se houver evolução clínica (ex: "Nódulo" -> "Carcinoma"), mantém APENAS o diagnóstico evoluído.
3. REGRA DA DATA ('desde'):
   - Se o texto indicar claramente quando a doença foi diagnosticada (ex: "diagnosticado em 2015", "há 5 anos" ou "hoje"), calcula e escreve essa data exata/ano.
   - Se a data exata do diagnóstico não for mencionada, mas a patologia constar no histórico, usa a data do cabeçalho mais antigo onde ela aparece e ADICIONA OBRIGATORIAMENTE um asterisco no final (ex: "14-Jul-2023*").
4. Devolve EXCLUSIVAMENTE o objeto JSON válido abaixo.

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
9. PROIBIÇÃO DE SOBREPOSIÇÃO: É estritamente proibido incluir qualquer valor de dosagem (mg, g, ml, mcg) no campo 'posologia'. .
   - DOSAGEM: Deve conter APENAS valores de concentração/quantidade seguidos de unidade de medida (ex: "5mg", "500mg", "10ml"). 
   - POSOLOGIA: Deve conter APENAS regime de toma/frequência (ex: "1 comp/dia", "ao deitar", "3 comp/dia").
10. AVALIAÇÃO DE ERRO: 
  - Se o campo 'dosagem' contiver palavras como "comp", "dia", "toma", "jejum" ou "vezes", o conteúdo desse campo é, na verdade, POSOLOGIA.
  - Deves mover automaticamente esse conteúdo para o campo 'posologia' e deixar o campo 'dosagem' vazio (ou "N/A") se não existir uma concentração real.
11.  É terminantemente proibido manter instruções de toma (ex: "3 comp/dia" ou "3 gotas/dia") no campo 'dosagem'.


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

REGRAS DE OURO:
REGRAS:
1. FILTRAGEM: A tua entrada contém exames classificados como 'exame_objetivo' e 'exame_complementar'. Deves ignorar COMPLETAMENTE qualquer exame cuja categoria seja 'exame_objetivo'. Mantém apenas os classificados como 'exame_complementar'.
2. VAZIO: Se o diário não contiver exames complementares (apenas objetivos ou nada), deves responder estritamente "SEM_DADOS" e não gerar nenhum objeto JSON.
3. VALORES (Análises/Numéricos): Devem ser copiados na íntegra, sem omissões. Mantém a precisão dos números, unidades e referência (se houver).
4. RELATÓRIOS (Texto/Imagem): Deves ler o texto completo, INFERIR o que é clinicamente relevante (achados patológicos, alterações, conclusões do radiologista/especialista) e escrever um resumo sucinto. 
   - Objetivo: Extrair a conclusão clínica (o que importa para o tratamento).
   - Proibido: Transcrever relatórios inteiros com descrições anatómicas normais que não contribuem para a decisão clínica.
5. INTEGRIDADE: Se um exame for 'exame_complementar', ele DEVE aparecer no JSON final.

FORMATO DE SAÍDA:
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