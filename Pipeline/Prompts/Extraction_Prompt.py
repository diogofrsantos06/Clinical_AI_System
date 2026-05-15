def get_prompt_for_diary_extraction(diary_text: str) -> str:
    return f"""
Extrai toda a informação clínica relevante do texto abaixo e organiza-a num JSON estruturado.

OBJETIVO:
Criar uma representação clínica limpa e estruturada que permita gerar um resumo médico.

FORMATO DE SAÍDA (JSON obrigatório):

{{
  "data": "",
  "diagnosticos": [
    {{
      "doenca": "",
      "tipo": "suspeita | confirmado",
      "temporalidade": "cronico | agudo",
      "relevancia": ""
    }}
  ],
  "medicacao": [
    {{
      "farmaco": "",
      "classe": "",
      "tipo": "habitual | iniciada | ajustada | suspensa"
    }}
  ],
  "alergias": [
    {{
      "substancia": ""
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
      "tipo": "diagnostico | terapeutico | organizacional",
      "urgencia": "eletivo | urgente | emergente"
    }}
  ]
}}

REGRAS CRÍTICAS:

1. Copia o texto bruto
2. NÃO inventar informação
3. Incluir TODOS os dados clínicos relevantes
4. Separar corretamente:
   - sintomas
   - sinais
   - exames
   - diagnósticos
   - terapêutica
5. Medicação deve ser classificada corretamente (habitual vs iniciada)
6. NÃO incluir texto administrativo
7. JSON válido obrigatório (sem texto extra)

TEXTO:
{diary_text}
"""