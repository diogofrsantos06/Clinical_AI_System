def get_prompt_for_diary_extraction(diary_text: str) -> str:
    return f"""
Como médico assistente e especialista em análise de documentação clínica, extrai as entidades clínicas do texto fornecido abaixo.

1. REGRAS DE NEGÓCIO E QUALIDADE
- Análise Semântica: Prioriza o significado clínico sobre a estrutura. Ignora verbos de estado ("é", "apresenta") e palavras de ligação.
- Datas: Formato DD/MM/YYYY. PROIBIDO: "hoje", "ontem", "agora", horas. Se não houver data, usa "Sem informação".
- Validade: O JSON deve ser perfeitamente estruturado, sem texto adicional ou explicações antes/depois do bloco.
- INTEGRIDADE: Extrai apenas informação explicitamente suportada pelo texto fornecido. É estritamente proibido inferir, deduzir ou completar informação clínica que não esteja escrita no texto.
- CATEGORIAS SEM INFORMAÇÃO: Inclui sempre as 6 categorias no JSON de saída. Se não houver informação para uma categoria neste diário, devolve-a como lista vazia (ex: "alergias": []) em vez de omitir a chave.

2. REGRAS FUNDAMENTAIS E EXCLUSÃO CLÍNICA
- Medicação: Mantém a distinção entre habitual e agudo conforme o contexto.
- Medicação: Se listar 'X+Y', cria dois objetos JSON distintos.
- COBERTURA TOTAL: Extrai TODA a menção a medicação, mesmo que não esteja numa lista formal de "Medicação Habitual" — incluindo início, alteração de dose ou substituição de fármacos mencionados dentro do plano terapêutico ou notas de alta (ex: "passa a fazer X 10mg", "inicia Y até à consulta"). Cria sempre uma entrada em 'medicacao' para cada uma destas menções, mesmo que a frase esteja escrita como uma decisão/plano e não como uma lista de medicamentos.
- SEPARAÇÃO POSOLOGIA/DOSAGEM: 
    - DOSAGEM: Apenas concentração (ex: "5mg", "10ml"). PROIBIDO incluir frequências.
    - POSOLOGIA: Apenas regime de toma (ex: "1cp/dia"). PROIBIDO incluir gramagens.
    - REGRA DE OURO: É estritamente proibido repetir o valor da dosagem no campo posologia. Se vires "5mg 1cp/dia", extrai "dosagem": "5mg" e "posologia": "1cp/dia".
    - SEM INFORMAÇÃO REAL: Se o texto não indicar uma dosagem e/ou posologia reais para um fármaco, usa "N/A" nesse(s) campo(s). É estritamente proibido preencher 'dosagem' ou 'posologia' com a indicação clínica, a descrição de uma lesão, ou qualquer outro texto que não seja, de facto, uma concentração ou um regime de toma.

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
- Só extraias um diagnóstico se ele for apresentado como tal no texto. Não extraias uma doença apenas porque o nome aparece uma vez a descrever o contexto ou uma manifestação de outro problema.
- NÃO extraias:
  - sintomas ou queixas clínicas;
  - sinais do exame objetivo;
  - achados imagiológicos ou anatómicos isolados;
  - resultados laboratoriais ou défices;
  - procedimentos, cirurgias, eventos agudos passados, sequelas ou estados pós-operatórios.
- CRITÉRIO RIGOROSO DE TEMPORALIDADE:
  - 'cronico': Aplica-se exclusivamente a patologias sistémicas, de longa duração ou permanentes, que exigem monitorização e seguimento médico contínuo e regular no ambulatório (ex: patologias metabólicas, cardiovasculares crónicas, endocrinopatias, doenças neurodegenerativas).
  - 'agudo': Aplica-se a qualquer episódio de aparecimento súbito, intercorrência clínica, traumatismo, hemorragia, lesão aguda, ou qualquer condição que tenha tido tratamento cirúrgico/resolução e já não constitua uma doença sistémica ativa em curso.
- Classifica cada diagnóstico como "confirmado" ou "suspeita". Se houver qualquer dúvida quanto à cronicidade, classifica obrigatoriamente como "agudo".
- Campo 'data_diagnostico': preenche APENAS se o texto disser explicitamente quando o diagnóstico foi feito. Caso contrário, deixa como string vazia ("").

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