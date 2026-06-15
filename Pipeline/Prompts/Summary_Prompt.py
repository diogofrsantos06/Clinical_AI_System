SUMMARY_TEXT_PROMPT = """
Atua como um Médico Sénior de Medicina Interna e Emergência. O teu objetivo é consolidar o histórico clínico de um paciente num resumo de alta densidade informativa.

DADOS PARA ANÁLISE (JSON):
{extracted_data}

REGRA CRÍTICA DE LEITURA:
O TEXTO acima contém múltiplos diários/registos. É OBRIGATÓRIO leres todo o texto, do inicio ao fim. Tens de extrair e fundir a informação de TODOS os registos presentes no Texto.

REGRAS GERAIS E DE FORMATAÇÃO:
1. Resposta em Português de Portugal.
2. O teu output TEM DE SER EXCLUSIVAMENTE UM OBJETO JSON VÁLIDO. 
3. É ABSOLUTAMENTE PROIBIDO o uso de formatação Markdown (sem asteriscos, sem negritos, sem blocos de código ```json) no output. 
4. Não escrevas texto introdutório nem conclusões fora do JSON.
. TENS DE RESPEITAR RIGOROSAMENTE A ORDEM DAS SECÇÕES ABAIXO.

REGRAS POR SECÇÃO:

ANTECEDENTES PESSOAIS (AP) E DIAGNÓSTICOS:
- Extrai 100% das doenças crónicas (AP) e diagnósticos agudos de TODOS os diários. Não omitas nenhuma patologia. Consolida patologias identicas, fica a que estiver mais especifica.
- Apenas se no TEXTO disser explicitamente 'suspeita', adiciona "(Suspeita)".
- Adiciona a data do diagnóstico, se não tiver data coloca sem informação nesse campo.

MEDICAÇÃO HABITUAL E ALERGIAS:
- Alergias: Compila todas. Se não houver, escreve "Sem alergias conhecidas".
- Medicação: Lista TODOS os fármacos mencionados ao longo de TODOS os diários que sejam do TIPO HABITUAL. Todos os que não forem do tipo HABITUAL são descartados. Se o mesmo medicamento for do tipo HABITUAL e SUSPENSA, descarta se o tipo SUSPENSA aparecer mais recentemente.

EXAMES E RESULTADOS:
- TÍTULO: Usa o NOME EXATO do diário (ex: "HUC-URG CIRURGIA GERAL - 10-Ago-2023 (Registo 1)").
- ANÁLISES: Deves listar TODOS os parâmetros, valores e unidades encontrados na secção de análises (ex: "Glicose: 375 mg/dL, pH: 7.52"). É OBRIGATÓRIO incluir o valor numérico se ele existir nos dados e a unidade dele.
- IMAGIOLOGIA: Transcreve na íntegra os achados dos relatórios de exames. Não resumas o conteúdo médico; se o relatório existe, transcreve-o frase a frase.
- IMAGIOLOGIA: Agrupa obrigatoriamente os achados por tipo de exame dentro de cada diário para evitar repetições. Se existirem vários órgãos/achados para o mesmo exame (ex: "ECOGRAFIA ABDOMINAL"), escreve o nome do exame apenas uma vez seguido de dois pontos, e depois lista os achados individuais separados por ponto e vírgula.
  * Exemplo de formato: "ECOGRAFIA ABDOMINAL: (Vesícula Biliar): achado X; (Fígado): achado Y; (Rins): achado Z."
  * Não repitas o nome do exame em cada linha ou frase.

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
      "nome": "Título do diário",
      "data": "retirada do titulo",
      "tipo_exame": "tipo de exame",
      "resultado": "Análises (parâmetros: valores); Imagiologia: relatório integral"
    }}
  ],
  "plano": "Plano de decisão do diário mais recente"
}}
"""


#SÍNTESE DE SINTOMAS:
#- É PROIBIDO listar os sintomas agrupados por diário. Agrupa por SINTOMA.
#- Lista o sintoma uma única vez e, à frente, entre parênteses, lista todos os diários onde ele aparece. Exemplo: Dor abdominal (Diário X, Diario Y)

#SÍNTESE DE SINTOMAS:
#- [Nome do Sintoma Unificado] ([Título do Diário A], [Título do Diário B])
