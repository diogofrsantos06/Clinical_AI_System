SUMMARY_TEXT_PROMPT = """
Atua como um Médico Sénior de Medicina Interna e Emergência. O teu objetivo é consolidar o histórico clínico de um paciente num resumo de alta densidade informativa.

DADOS PARA ANÁLISE (JSON):
{extracted_data}

REGRA CRÍTICA DE LEITURA:
O TEXTO acima contém múltiplos diários/registos. É OBRIGATÓRIO leres todo o texto, do inicio ao fim. Tens de extrair e fundir a informação de TODOS os registos presentes no Texto.

REGRAS GERAIS E DE FORMATAÇÃO:
1. Resposta em Português de Portugal.
2. TEXTO PURAMENTE SIMPLES (PLAIN TEXT). É ABSOLUTAMENTE PROIBIDO o uso de Markdown (sem asteriscos, sem negritos).
3. TENS DE RESPEITAR RIGOROSAMENTE A ORDEM DAS SECÇÕES ABAIXO.

REGRAS POR SECÇÃO:

ANTECEDENTES PESSOAIS (AP) E DIAGNÓSTICOS:
- Extrai 100% das doenças crónicas (AP) e diagnósticos agudos de TODOS os diários. Não omitas nenhuma patologia.
- DIAGNÓSTICOS AGUDOS: Apenas se no TEXT disser explicitamente 'suspeita', adiciona "(Suspeita)".

MEDICAÇÃO HABITUAL E ALERGIAS:
- Alergias: Compila todas. Se não houver, escreve "Sem alergias conhecidas".
- Medicação: Lista TODOS os fármacos mencionados ao longo de TODOS os diários. Não deixes nenhum de medicmento de fora a menos que esteja explicíto que vai deixar de ser tomado. 

EXAMES E RESULTADOS:
- TÍTULO: Usa o NOME EXATO do diário (ex: "HUC-URG CIRURGIA GERAL - 10-Ago-2023 (Registo 1)").
- ANÁLISES E GASIMETRIAS: Deves listar TODOS os parâmetros, valores e unidades encontrados na secção de análises (ex: "Glicose: 375 mg/dL, pH: 7.52"). É OBRIGATÓRIO incluir o valor numérico se ele existir nos dados.
- IMAGIOLOGIA: Transcreve na íntegra os achados dos relatórios de exames. Não resumas o conteúdo médico; se o relatório existe, transcreve-o frase a frase.
- IMAGIOLOGIA: Agrupa obrigatoriamente os achados por tipo de exame dentro de cada diário para evitar repetições. Se existirem vários órgãos/achados para o mesmo exame (ex: "ECOGRAFIA ABDOMINAL"), escreve o nome do exame apenas uma vez seguido de dois pontos, e depois lista os achados individuais separados por ponto e vírgula.
  * Exemplo de formato: "ECOGRAFIA ABDOMINAL: (Vesícula Biliar): achado X; (Fígado): achado Y; (Rins): achado Z."
  * Não repitas o nome do exame em cada linha ou frase.

SÍNTESE DE SINTOMAS:
- É PROIBIDO listar os sintomas agrupados por diário. Agrupa por SINTOMA.
- Lista o sintoma uma única vez e, à frente, entre parênteses, lista todos os diários onde ele aparece. Exemplo: Dor abdominal (Diário X, Diario Y)

PLANO E DECISÃO:
- Apenas as decisões clínicas mais relevantes (do mais recente para o mais antigo).

=== TEMPLATE DE RESPOSTA OBRIGATÓRIO ===
Preenche a estrutura abaixo exatamente nesta ordem, sem usar markdown:

ANTECEDENTES PESSOAIS (AP) E DIAGNÓSTICOS:
- [Doença 1]
- [Doença 2]

MEDICAÇÃO HABITUAL E ALERGIAS:
- Alergias: [Lista ou Sem alergias conhecidas]
- Medicação Habitual:
  - [Fármaco 1]
  - [Fármaco 2]

EXAMES E RESULTADOS:

DIARIO: [NOME EXATO DO DIÁRIO]
- ANÁLISES: [Lista OBRIGATORIAMENTE todos os parâmetros e valores numa única linha, separados apenas por ponto e vírgula. Ex: "pH: 7.528; pCO2: 28.1; pO2: 86.4". NÃO repitas a categoria ou tipo de exame]
- IMAGIOLOGIA: [Transcreve o relatório na íntegra. Se não houver, escreve Nenhuma]

SÍNTESE DE SINTOMAS:
- [Nome do Sintoma Unificado] ([Título do Diário A], [Título do Diário B])

PLANO E DECISÃO:
- DIARIO: [Título longo]: [Ação principal]
"""
