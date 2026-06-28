PROMPT_ANTECEDENTES = """
Atua como um Médico Sénior de Medicina Interna. O teu objetivo é extrair o histórico de patologias do paciente.

DADOS PARA ANÁLISE:
{extracted_data}

REGRAS:
1. Extrai 100% das doenças crónicas (AP) e diagnósticos agudos de TODOS os diários.
2. Cada patologia só deve aparecer UMA vez. Se um diagnóstico aparecer como "Suspeita" no início, mas for validado como "Confirmado" mais à frente, consolida-o como "Confirmado".
3. Devolve EXCLUSIVAMENTE um objeto JSON válido, sem markdown e sem introduções.
4. Para o campo 'desde' de cada diagnóstico, aplica estritamente a seguinte prioridade:
- Se o diário disser explicitamente a data do acontecimento (ex: 'diagnosticado em 2018' ou 'enfarte em 05/2021'), extrai essa data.
- Se o diário disser que foi detetado na consulta atual (ex: 'diagnosticado hoje', 'início hoje'), calcula e devolve a Data do diário clínico atual correspondente.
- Se NÃO houver qualquer menção de data no texto clínico, deves preencher com a data do primeiro diário clínico em que esse diagnóstico aparece listado, adicionando o sufixo '(Data do registo - Não confirmada)' (ex: '14-Jul-2023 (Data do registo - Não confirmada)').
- Se for impossível determinar, usa 'Sem informação'.

FORMATO DE SAÍDA:
{{
  "antecedentes": [
    {{
      "diagnostico": "Nome da doença",
      "tipo": "Suspeita ou Confirmado",
      "temporalidade": "Crónico ou Agudo",
      "desde": "Data exata / Data calculada / Data do primeiro diário (Data do registo - Não confirmada) / Sem informação"    
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
3. SEPARAÇÃO ESTRITA DOSAGEM/POSOLOGIA: O campo 'dosagem' serve APENAS para a concentração/peso (ex: "5mg", "1g") e É PROIBIDO conter frequências. O campo 'posologia' serve APENAS para a frequência ou regime de toma (ex: "1id", "1 comp/dia", "SOS") e É PROIBIDO conter a concentração ou gramagem do fármaco.
4. Devolve EXCLUSIVAMENTE um objeto JSON válido, sem markdown e sem introduções.

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
2. RESULTADO / ACHADOS (REGRA DIFERENCIADA):
- SE FOR UMA ANÁLISE CLÍNICA/LABORATORIAL: Transcreve TODOS os parâmetros e valores na ÍNTEGRA. Nunca resumas, omitas ou apagues valores analíticos (ex: Hemograma, glicémia, PCR, etc. devem vir completos com os respetivos valores).
- SE FOR UM EXAME DE IMAGEM / RELATÓRIO EXTENSO (ex: Ecografia, TAC, RM, Raio-X): Nunca transcrevas o relatório longo na íntegra. Transcreve apenas um resumo sintetizado referindo os achados clínicos patológicos ou mais relevantes para o acompanhamento do paciente.
3. Devolve EXCLUSIVAMENTE um objeto JSON válido, sem markdown e sem introduções.

FORMATO DE SAÍDA:
{{
  "exames": [
    {{
      "nome": "Título do diário de origem",
      "data": "Data da consulta",
      "tipo_exame": "Tipo de Exame (ex: Análises Clínicas ou Ecografia Abdominal)",
      "resultado": "Valores completos das análises OU texto sintetizado com os achados mais relevantes do relatório de imagem"    
      }}
  ]
}}
"""

PROMPT_PLANO = """
Atua como um Médico Sénior. O teu objetivo é interpretar, limpar e redigir a decisão terapêutica final do caso com base nos dados brutos extraídos.

DADOS DO PLANO MAIS RECENTE:
{extracted_data}

REGRAS CRÍTICAS:
1. NÃO faças uma transcrição literal. Os dados podem conter frases cortadas a meio (ex: falhas de leitura/OCR) ou erros de formatação.
2. O teu dever é unir a informação fragmentada, corrigir frases partidas e redigir um texto coeso e clinicamente estruturado.
3. Sintetiza apenas as decisões e ações clínicas relevantes tomadas pelo médico (ex: ajustes na medicação, exames solicitados, encaminhamentos ou recomendações).
4. Escreve um parágrafo clínico fluido, claro e profissional, sem numerações avulsas se não fizerem sentido.
5. Devolve EXCLUSIVAMENTE o objeto JSON válido abaixo, sem markdown (sem ```json), sem texto introdutório ou conclusões.

FORMATO DE SAÍDA OBRIGATÓRIO:
{{
  "plano": "Texto do plano terapêutico final sintetizado, coeso e corrigido"
}}
"""