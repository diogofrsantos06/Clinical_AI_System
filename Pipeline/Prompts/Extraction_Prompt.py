def get_prompt_for_section(section_name: str, section_text: str) -> str:

    structures = {
        "historia_clinica": "Lista de objetos com 'evento', 'inicio', 'caracteristicas' e 'antecedentes_relevantes'.",
        "exames_e_resultados": "Lista de objetos com 'exame', 'parametro', 'valor', 'unidade' e 'interpretacao'.",
        "avaliacao_e_sintomas": "Lista de objetos com 'sinal_sintoma', 'localizacao', 'intensidade' e 'exame_objetivo_detalhe'.",
        "terapeutica_e_medicao": "Lista de objetos com 'fármaco', 'dosagem', 'via', 'frequência' e 'tipo' (habitual ou nova).",
        "plano_e_decisao": "Lista de objetos com 'acao_proposta', 'urgencia' e 'destino_doente'.",
        "diagnosticos": "Lista de objetos com 'doenca', 'tipo' (suspeita ou confirmado) e 'estado' (novo ou conhecido).",
        "outras_informacoes": "Lista de objetos com 'observacao' e 'detalhe'."
    }

    structure = structures.get(section_name, "Lista de factos relevantes.")

    return f"""
Extrai TODA a informação clinicamente relevante da secção "{section_name}" seguindo rigorosamente esta estrutura:
{structure}

REGRAS OBRIGATÓRIAS:

1. EXTRAÇÃO LITERAL
- Copia exatamente o texto original.
- NÃO traduzas, reformules ou expandas abreviaturas.
- NÃO alteres unidades, números ou termos.

2. EXAUSTIVIDADE
- Inclui toda a informação clinicamente relevante.
- NÃO omitas informação presente no texto.

3. SEPARAÇÃO SEMÂNTICA
- Coloca cada informação apenas na secção correta.
- NÃO mistures exames, eventos, diagnósticos ou terapêutica entre si.

4. NÃO REDUNDÂNCIA
- NÃO repitas a mesma informação em vários campos.
- Cada campo deve conter apenas o tipo de informação correspondente.

5. ESTRUTURAÇÃO
- Divide a informação em múltiplas entradas quando necessário.
- NÃO agregues múltiplos factos diferentes no mesmo campo.

6. GESTÃO DE DADOS
- Usa null apenas quando a informação não existir.
- NÃO inventes dados.

7. FORMATO DE SAÍDA (CRÍTICO)
- A resposta deve começar diretamente com "{" e terminar com "}"
- NÃO incluir texto antes ou depois do JSON
- NÃO usar blocos de código (```json)
- NÃO usar aspas simples

8. EXTRAÇÃO DE EXAMES
- Extrai apenas a informação objetiva e relevante do exame.
- NÃO copiar relatórios completos.
- Cada resultado deve ser separado em entradas distintas.
- Preencher sempre que possível:
  - parametro
  - valor
  - unidade
- "interpretacao" deve ser curta e conter apenas a conclusão clínica essencial.
- NÃO repetir o mesmo conteúdo em múltiplos exames.

9. NÃO DUPLICAÇÃO GLOBAL
- NÃO repetir a mesma informação em múltiplas entradas.
- Cada facto deve aparecer apenas uma vez em toda a secção.

TEXTO:
{section_text}
"""