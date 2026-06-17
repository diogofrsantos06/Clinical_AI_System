# Summary_Prompt.py

PROMPT_ANTECEDENTES = """
Atua como um Médico Sénior de Medicina Interna. O teu objetivo é extrair o histórico de patologias do paciente.

DADOS PARA ANÁLISE:
{extracted_data}

REGRAS:
1. Extrai 100% das doenças crónicas (AP) e diagnósticos agudos de TODOS os diários.
2. Cada patologia só deve aparecer UMA vez. Se um diagnóstico aparecer como "Suspeita" no início, mas for validado como "Confirmado" mais à frente, consolida-o como "Confirmado".
3. Devolve EXCLUSIVAMENTE um objeto JSON válido, sem markdown e sem introduções.

FORMATO DE SAÍDA:
{{
  "antecedentes": [
    {{
      "diagnostico": "Nome da doença",
      "tipo": "Suspeita ou Confirmado",
      "temporalidade": "Crónico ou Agudo",
      "desde": "Data ou Sem informação"
    }}
  ]
}}
"""

PROMPT_MEDICACAO = """
Atua como um Médico Sénior. O teu objetivo é isolar a medicação habitual e alergias.

DADOS PARA ANÁLISE:
{extracted_data}

REGRAS:
1. Alergias: Compila todas. Se não houver, escreve "Sem alergias conhecidas".
2. Medicação: Lista TODOS os fármacos do TIPO HABITUAL. Descarta os restantes. Se um fármaco habitual for marcado como SUSPENSO mais recentemente, descarta-o.
3. Devolve EXCLUSIVAMENTE um objeto JSON válido, sem markdown e sem introduções.

FORMATO DE SAÍDA:
{{
  "medicacao": [
    {{
      "farmaco": "Nome",
      "dosagem": "Valor ou N/A",
      "posologia": "Informação ou N/A",
      "indicacao": "Indicação",
      "observacoes": "Observações"
    }}
  ],
  "alergias": ["Substância e reação"]
}}
"""

PROMPT_EXAMES = """
Atua como um Médico Sénior. O teu objetivo é transcrever todos os exames e resultados médicos.

DADOS PARA ANÁLISE:
{extracted_data}

REGRAS:
1. Inclui todos os exames laboratoriais (análises) e imagiológicos (Rx, Eco, TC). Proibido omitir.
2. RESULTADO: Transcreve os parâmetros/valores das análises ou o relatório de imagem na íntegra. Proibido usar "achado X/Y".
3. Devolve EXCLUSIVAMENTE um objeto JSON válido, sem markdown e sem introduções.

FORMATO DE SAÍDA:
{{
  "exames": [
    {{
      "nome": "Título do diário de origem",
      "data": "Data da consulta",
      "tipo_exame": "Tipo de Exame (ex: Análises Clínicas ou Ecografia Abdominal)",
      "resultado": "Valores das análises ou texto integral do relatório"
    }}
  ]
}}
"""

PROMPT_PLANO = """
Atua como um Médico Sénior. Limpa e formata a decisão terapêutica final do caso.

DADOS DO PLANO MAIS RECENTE:
{extracted_data}

REGRAS CRÍTICAS:
1. Transcreve de forma limpa e estruturada as decisões tomadas pelo médico neste registo.
2. Devolve EXCLUSIVAMENTE o objeto JSON válido abaixo, sem markdown (sem ```json), sem texto introdutório ou conclusões.

FORMATO DE SAÍDA OBRIGATÓRIO:
{{
  "plano": "Texto do plano terapêutico final limpo"
}}
"""