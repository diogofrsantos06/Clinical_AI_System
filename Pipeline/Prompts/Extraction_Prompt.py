def get_prompt_for_diary_extraction(diary_text: str) -> str:
    return f"""
Como médico assistente e especialista em análise de documentação clínica, extrai as entidades clínicas do texto fornecido abaixo.

1. REGRAS DE NEGÓCIO E QUALIDADE
- Análise Semântica: Prioriza o significado clínico sobre a estrutura. Ignora verbos de estado ("é", "apresenta") e palavras de ligação.
- Datas: Formato DD/MM/YYYY. PROIBIDO: "hoje", "ontem", "agora", horas. Se não houver data, usa "Sem informação".
- Validade: O JSON deve ser perfeitamente estruturado, sem texto adicional ou explicações antes/depois do bloco[cite: 5].
- INTEGRIDADE: Extrai apenas informação explicitamente suportada pelo texto fornecido. É estritamente proibido inferir, deduzir ou completar informação clínica que não esteja escrita no texto.
- CATEGORIAS SEM INFORMAÇÃO: Inclui sempre as 6 categorias no JSON de saída. Se não houver informação para uma categoria neste diário, devolve-a como lista vazia (ex: "alergias": []) em vez de omitir a chave.

2. REGRAS FUNDAMENTAIS E EXCLUSÃO CLÍNICA
- Medicação: Mantém a distinção entre habitual e agudo conforme o contexto.
- Medicação: Se listar 'X+Y', cria dois objetos JSON distintos.
- SEPARAÇÃO POSOLOGIA/DOSAGEM: 
    - DOSAGEM: Apenas concentração (ex: "5mg", "10ml"). PROIBIDO incluir frequências.
    - POSOLOGIA: Apenas regime de toma (ex: "1cp/dia"). PROIBIDO incluir gramagens.
    - REGRA DE OURO: É estritamente proibido repetir o valor da dosagem no campo posologia. Se vires "5mg 1cp/dia", extrai "dosagem": "5mg" e "posologia": "1cp/dia".

3. DIRETRIZES DE CATEGORIZAÇÃO (EO vs MCDT)
- EXAMES OBJETIVOS (EO): Observação física in loco (ex: TA, auscultação, palpação, reflexos, temperatura). Categoria: 'exame_objetivo'.
- EXAMES COMPLEMENTARES (MCDT/ECD/Análises): Meios auxiliares externos (laboratoriais, imagiológicos, endoscópicos, eletrofisiológicos). Categoria: 'exame_complementar'.
- REGRAS DE INFERÊNCIA:
    a) Semântica: Se requer suporte externo (laboratório/máquina), é 'exame_complementar'. Se mede função biológica no consultório, é 'exame_objetivo'.
    b) Sequencial: O que segue etiquetas "EO" é tipicamente observação física; o que segue "ECD/MCDT/Análises" é complementar.
    c) PREVENÇÃO: Nunca classifiques TA/auscultação como 'exame_complementar' nem Raio-X como 'exame_objetivo'.

4. REGRAS DE EXTRAÇÃO DE DIAGNÓSTICOS:  
- Extrai apenas diagnósticos médicos explicitamente documentados. Nunca infiras diagnósticos.
- Considera como diagnóstico apenas doenças ou síndromes reconhecidas.
- Só extraias um diagnóstico se ele for apresentado como tal no texto. Não extraias uma doença apenas porque o nome aparece uma vez a descrever o contexto ou uma manifestação de outro problema (ex: "quadro de dor associada a ansiedade" não constitui um diagnóstico de ansiedade).
- NÃO extraias:
  - sintomas ou queixas clínicas;
  - sinais do exame objetivo;
  - achados imagiológicos ou anatómicos isolados;
  - resultados laboratoriais ou défices;
  - procedimentos, sequelas ou estados pós-operatórios.
- Classifica cada diagnóstico como "confirmado" ou "suspeita", e como "cronico" ou "agudo", apenas quando isso estiver explícito no texto. Se não houver informação suficiente para decidir com confiança, classifica como "suspeita" e "agudo" por omissão.
- Campo 'data_diagnostico': preenche APENAS se o texto disser explicitamente quando o diagnóstico foi feito (ex: "diagnosticado em 2015", "há 5 anos", "05/2021"). Caso contrário, deixa como string vazia ("") — não inventes nem calcules uma data.

5. FORMATO DE SAÍDA (JSON)
{{
  "data": "DD/MM/YYYY",
  "diagnosticos": [{{"doenca": "", "tipo": "suspeita | confirmado", "temporalidade": "cronico | agudo", "data_diagnostico": ""}}],
  "medicacao": [{{"farmaco": "", "indicação": "", "tipo": "habitual | administrada | suspensa", "posologia": "", "dosagem": "", "observações": ""}}],
  "alergias": [{{"substancia": "", "reação": ""}}],
  "exames": [{{"categoria": "exame_objetivo | exame_complementar", "tipo_exame": "", "parametro": "", "valor": "", "unidade": "", "relatorio": ""}}],
  "sintomas": [{{"descricao": "", "localizacao": "", "tipo": ""}}],
  "plano": [{{"acao": ""}}]
}}

TEXTO A ANALISAR:
{diary_text}
"""