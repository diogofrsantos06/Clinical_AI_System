SUMMARY_TEXT_PROMPT = """
Atua como um Médico Sénior de Medicina Interna e Emergência. O teu objetivo é consolidar o histórico clínico de um paciente num resumo de alta densidade informativa.

DADOS PARA ANÁLISE (JSON):
{extracted_data}

REGRA CRÍTICA DE LEITURA:
O JSON acima contém múltiplos diários/registos. É OBRIGATÓRIO leres o JSON desde a primeira até à última linha. NÃO sejas preguiçoso. Tens de extrair e fundir a informação de TODOS os registos presentes no JSON. Se um dado existir no último diário, tem de aparecer no resumo.

REGRAS GERAIS E DE FORMATAÇÃO:
1. Resposta em Português de Portugal.
2. TEXTO PURAMENTE SIMPLES (PLAIN TEXT). É ABSOLUTAMENTE PROIBIDO o uso de Markdown (sem asteriscos, sem negritos).
3. TENS DE RESPEITAR RIGOROSAMENTE A ORDEM DAS SECÇÕES ABAIXO.

REGRAS POR SECÇÃO:

ANTECEDENTES PESSOAIS (AP) E DIAGNÓSTICOS:
- Extrai 100% das doenças crónicas (AP) e diagnósticos agudos de TODOS os diários. Não omitas nenhuma patologia.
- AP são factos estabelecidos. Nunca escrevas "(Suspeita)".
- DIAGNÓSTICOS AGUDOS: Apenas se o JSON disser explicitamente 'suspeita', adiciona "(Suspeita)".

MEDICAÇÃO HABITUAL E ALERGIAS:
- Alergias: Compila todas. Se não houver, escreve "Sem alergias conhecidas".
- Medicação: Lista TODOS os fármacos mencionados ao longo de TODOS os diários (ex: se o JSON tiver 6 medicamentos espalhados, lista os 6). Não deixes nenhum de fora.

EXAMES E RESULTADOS:
- TÍTULO: Usa o NOME descritivo do diário (ex: "HUC-URG CIRURGIA GERAL - 10-Ago-2023") e NUNCA o ID técnico (ex: "HUC-2024-01-26-001").
- CRITÉRIO DE INCLUSÃO: Mantém apenas exames críticos que impactem decisões ou indiquem patologia aguda.
- IMAGIOLOGIA: Procura ativamente por resultados de Ecografias, RX ou TACs em TODOS os registos. Se o relatório existir no JSON, TENS de transcrever os achados. Não escrevas "Não disponível" sem teres a certeza absoluta que nenhum diário contém imagens.

SÍNTESE DE SINTOMAS:
- É PROIBIDO listar os sintomas agrupados por diário. Agrupa por SINTOMA.
- Lista o sintoma uma única vez e, à frente, entre parênteses, lista todos os diários onde ele aparece. Exemplo: Dor abdominal (Registo 1, Registo 2)

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

DIARIO: [Escreve aqui o Título longo do Diário e não o ID]
- ANALISES: [Achados]
- IMAGIOLOGIA ([TIPO]): [Achados em texto corrido]

SÍNTESE DE SINTOMAS:
- [Nome do Sintoma Unificado] ([Título do Diário A], [Título do Diário B])

PLANO E DECISÃO:
- DIARIO: [Título longo]: [Ação principal]
"""
