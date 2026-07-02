def get_prompt_for_diary_extraction(diary_text: str) -> str:
    return f"""
Como médico assistente e especialista em análise de documentação clínica, extrai as entidades clínicas do texto fornecido abaixo.

REGRAS FUNDAMENTAIS:
Não te limites a extrair listas. Deves realizar uma análise semântica profunda. 
- Identifica diagnósticos presentes em orações narrativas e extrai-os
Sintomas NÃO são diagnósticos.
DATA: Formato DD/MM/YYYY. PROIBIDO: "hoje", "ontem", "agora", horas. Se não houver data, usa "Sem informação".
MEDICACAO: Se o texto listar 'X+Y', cria dois objetos JSON distintos (um para X, outro para Y).

REGRAS CRÍTICAS DE SEPARAÇÃO:
- DOSAGEM: Apenas a concentração ou quantidade da substância (ex: 5mg, 500mg, 10ml).
- POSOLOGIA: Apenas o esquema de toma (ex: 1cp/dia, 2x ao dia, em jejum).
- PROIBIDO: É estritamente proibido repetir o valor da dosagem no campo posologia. 
  Se vires "5mg 1cp/dia", extrai "dosagem": "5mg" e "posologia": "1cp/dia". 
  Se escreveres "5mg" no campo posologia, o teu JSON será considerado inválido.
  
FORMATO DE SAÍDA (JSON obrigatório):

{{
  "data": "",
  "diagnosticos": [
    {{
      "doenca": "",
      "tipo": "suspeita | confirmado",
      "temporalidade": "cronico | agudo",
      "desde": ""
    }}
  ],
  "medicacao": [
    {{
      "farmaco": "",
      "indicação": "",
      "tipo": "habitual | administrada | suspensa",
      "posologia": "", 
      "dosagem": "", 
      "observações": ""
    }}
  ],
  "alergias": [
    {{
      "substancia": "",
      "reação": ""
    }}
  ],
  "exames": [
    {{
      "categoria": "exame_objetivo | exame_complementar",
      "tipo_exame": "",
      "parametro": "",
      "valor": "",
      "unidade": "",
      "relatorio": "",
    }}
  ],
  "sintomas": [
    {{
      "descricao": "",
      "localizacao": "",
      "tipo": ""
    }}
  ],
  "plano": [
    {{
      "acao": "",
    }}
  ]
}}

DIRETRIZES DE EXTRAÇÃO:
1. Extração Semântica: Prioriza o significado clínico sobre a estrutura da frase. Se o texto diz "Doente com [Diagnóstico]", extrai apenas "[Diagnóstico]".
2. Limpeza de Entidades: Remove palavras de ligação, determinantes e verbos de estado ("é", "apresenta", "tem", "trata-se de").
3. Exaustividade: Extrai toda a informação presente, independentemente de estar numa lista, tabela ou parágrafo descritivo.
4. Validade: O JSON deve ser perfeitamente estruturado, sem texto adicional ou explicações antes/depois do bloco JSON.
5. Medicacao: Mantém a distinção entre habitual e agudo conforme o contexto do texto.
6. Exclusão Clínica: Sintomas ou queixas isoladas NÃO são diagnósticos. Um diagnóstico deve ser uma patologia médica estabelecida, um síndrome ou uma condição crónica/aguda diagnosticada ou que seja suspeita.
7. A data que aparece nos diagnosticos deve ser do tipo DD/MM/YYYY ou apenas YYYY. Não deve aparecer horas, nem referências temporais como 'hoje'.
8. DISTINÇÃO CLÍNICA: 
   - EXAMES OBJETIVOS (EO): Dados da observação física direta (ex: TA, auscultação, palpação, reflexos, temperatura, etc). Classifica a categoria como 'exame_objetivo'.
   - EXAMES COMPLEMENTARES (MCDT/ECD): Ferramentas de diagnóstico solicitadas (laboratoriais, imagiológicas, endoscópicas, elétricas, etc). Classifica a categoria como 'exame_complementar'.
   - ESTRATÉGIA DE EXTRAÇÃO:
     a) PRIORIDADE SEMÂNTICA: Se o exame requer suporte externo (ex: laboratório, máquina de imagem), é 'exame_complementar'. Se mede uma função biológica in loco, é 'exame_objetivo'.
     b) PISTA SEQUENCIAL: Considera a organização do diário. Textos que seguem imediatamente a etiqueta "EO" ou "Exame Objetivo" são tipicamente dados de observação física. Textos que seguem etiquetas como "ECD", "MCDT", "Exames Complementares" ou "Análises" pertencem à categoria 'exame_complementar'.
     c) PREVENÇÃO DE ERROS: Nunca classifiques valores de tensão arterial ou auscultação como 'exame_complementar', mesmo que surjam por engano perto de uma lista de exames. Da mesma forma, nunca classifiques um Raio-X ou uma análise sanguínea como 'exame_objetivo'.
   - REGRA DE OURO: O médico não precisa de escrever explicitamente "EO" ou "MCDT"/"ECD". Tu deves inferir a categoria com base no tipo de exame: se mede uma função biológica em tempo real no consultório, é 'exame_objetivo'. Se requer um suporte externo (análise/imagem), é 'exame_complementar'.

   
   


TEXTO A ANALISAR:

{diary_text}

"""