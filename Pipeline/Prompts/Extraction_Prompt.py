def get_prompt_for_diary_extraction(diary_text: str) -> str:
    return f"""
Como médico assistente e especialista em análise de documentação clínica, extrai as entidades clínicas do texto fornecido abaixo.

REGRAS FUNDAMENTAIS:
Não te limites a extrair listas. Deves realizar uma análise semântica profunda. 
- Identifica diagnósticos presentes em orações narrativas e extrai-os
Sintomas NÃO são diagnósticos.
DATA: Formato DD/MM/YYYY. PROIBIDO: "hoje", "ontem", "agora", horas. Se não houver data, usa "Sem informação".
MEDICACAO: Se o texto listar 'X+Y', cria dois objetos JSON distintos (um para X, outro para Y).
DEVES distinguir de forma ABSOLUTAMENTE CLARA o campo 'dosagem' do campo 'posologia':
- DOSAGEM (Massa/Concentração): Refere-se exclusivamente à quantidade física do princípio ativo por unidade (ex: 5mg, 160mg, 1g, 50mcg).
- POSOLOGIA (Regime de Administração): Refere-se à frequência, quantidade de unidades e duração (ex: 1id, 3 comp/dia, de 12h em 12h, 1 vez por semana).
NUNCA mistures os dois dados no mesmo campo. Se o texto disser 'Amlodipina 5mg 1x/dia', '5mg' vai para dosagem e '1x/dia' vai para posologia.

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
8. Exames podem incluir valores analíticos de anlíses ou relatórios de exames (como Raio X, Eco,...). Apresenta toda a informação sobre cada exame/analíse.

TEXTO A ANALISAR:

{diary_text}

"""