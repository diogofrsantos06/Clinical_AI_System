SUMMARY_TEXT_PROMPT = """
Atua como um Médico Sénior de Medicina Interna e Emergência. O teu objetivo é consolidar o histórico clínico de um paciente num resumo de alta densidade informativa.

DADOS PARA ANÁLISE (JSON):
{extracted_data}

REGRA CRÍTICA DE LEITURA:
O TEXTO acima contém múltiplos diários/registos. É OBRIGATÓRIO leres todo o texto, do início ao fim. Tens de extrair e fundir a informação de TODOS os registos presentes no Texto.

REGRAS GERAIS E DE FORMATAÇÃO:
1. Resposta em Português de Portugal.
2. O teu output TEM DE SER EXCLUSIVAMENTE UM OBJETO JSON VÁLIDO. 
3. É ABSOLUTAMENTE PROIBIDO o uso de formatação Markdown (sem asteriscos, sem negritos, sem blocos de código ```json) no output. 
4. Não escrevas texto introdutório nem conclusões fora do JSON.
5. TENS DE RESPEITAR RIGOROSAMENTE A ORDEM DAS SECÇÕES ABAIXO.

REGRAS POR SECÇÃO:

ANTECEDENTES PESSOAIS (AP) E DIAGNÓSTICOS:
- Extrai 100% das doenças crónicas (AP) e diagnósticos agudos de TODOS os diários. Não omitas nenhuma patologia.
- REFORÇO DE CONSOLIDAÇÃO (MUITO IMPORTANTE): Cada patologia só deve aparecer UMA vez. Se um diagnóstico aparecer como "Suspeita" num diário inicial, mas for validado como "Confirmado" ou surgir como Diagnóstico Principal num registo posterior (ex: Colecistite Aguda), deves consolidá-lo numa única entrada e definir o tipo obrigatoriamente como "Confirmado". Só deve ficar marcado como "Suspeita" se em nenhum momento de todos os diários tiver sido confirmado.
- Adiciona a data do diagnóstico no campo "desde", se não tiver data coloca "Sem informação".

MEDICAÇÃO HABITUAL E ALERGIAS:
- Alergias: Compila todas. Se não houver, escreve "Sem alergias conhecidas".
- Medicação: Lista TODOS os fármacos mencionados ao longo de TODOS os diários que sejam do TIPO HABITUAL. Todos os que não forem do tipo HABITUAL são descartados. Se o mesmo medicamento for do tipo HABITUAL e SUSPENSA, descarta se o tipo SUSPENSA aparecer mais recentemente.

EXAMES E RESULTADOS:
- EXTRAÇÃO COMPLETA ABSOLUTA: É obrigatório incluir todos os exames laboratoriais (análises) e exames imagiológicos (Rx, Eco, TC, etc.) do texto. É estritamente proibido ocultar, resumir, omitir exames ou inventar informações.
- TÍTULO: Usa o NOME EXATO do diário (ex: "HUC-URG CIRURGIA GERAL - 10-Ago-2023 (Registo 1)").
- ANÁLISES: Deves listar TODOS os parâmetros, valores e unidades encontrados na secção de análises (ex: "Glicose: 375 mg/dL, pH: 7.52"). É OBRIGATÓRIO incluir o valor numérico se ele existir nos dados e a unidade dele.
- IMAGIOLOGIA: Transcreve na íntegra os achados dos relatórios de exames. Não resumas o conteúdo médico; se o relatório existe, transcreve-o frase a frase.

PLANO E DECISÃO:
- Apenas as decisões clínicas mais relevantes, apenas do diário mais recente.

FORMATO DE SAÍDA (ESTRUTURA JSON OBRIGATÓRIA):
{{
  "antecedentes": [
    {{
      "diagnostico": "Nome da doença",
      "tipo": "Suspeita ou Confirmado",
      "temporalidade": "Crónico ou Agudo",
      "desde": "Data ou Sem informação"
    }}
  ],
  "medicacao": [
    {{
      "farmaco": "Nome",
      "dosagem": "Valor ou N/A",
      "posologia": "Informação ou N/A",
      "indicacao": "Indicação",
      "observacoes": "Observações"
    }}
  ],
  "alergias": ["Substância e reação"],
  "exames": [
    {{
      "nome": "Título do diário de origem",
      "data": "Data da consulta",
      "tipo_exame": "Tipo de Exame (ex: Análises Clínicas ou Ecografia Abdominal)",
      "resultado": "Conteúdo integral transcrito (valores das análises ou texto do relatório da ecografia)"
    }}
  ],
  "plano": "Plano de decisão do diário mais recente"
}}
"""