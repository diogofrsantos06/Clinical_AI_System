# prompts/Summary_Prompt.py

SUMMARY_TEXT_PROMPT = """
Transforma o seguinte JSON clínico num relatório estruturado.

JSON:
{extracted_data}

========================
INSTRUÇÕES DE MAPEAMENTO (OBRIGATÓRIO)
========================

1. DIAGNÓSTICOS
- Listar TODOS os itens de "diagnosticos"
- Formato: nome da doença (sem interpretação)

2. MEDICAÇÃO
- Listar TODOS os itens de "medicacao"
- Um fármaco por linha
- NÃO excluir nenhum

3. EXAMES

3.1 Análises laboratoriais
- Para cada entrada com "parametro" e "valor":
  → escrever: parametro: valor unidade (se existir)
- NÃO agrupar
- NÃO eliminar duplicados

3.2 Exames de imagem
- Se existir campo "relatorio":
  → copiar texto integral ou quase integral
- NÃO resumir

4. SINTOMAS
- Listar todos os "descricao"
- NÃO agrupar
- NÃO interpretar

5. PLANO
- Listar todas as ações

========================
FORMATO FIXO (OBRIGATÓRIO)
========================

ANTECEDENTES PESSOAIS / DIAGNÓSTICOS
- item
- item

MEDICAÇÃO HABITUAL
- item
- item

EXAMES (VALORES E RELATÓRIOS)

### Análises laboratoriais
- parametro: valor
- parametro: valor

### Imagiologia
- relatório
- relatório

SINTOMAS E ACHADOS CLÍNICOS
- item
- item

PLANO / DECISÃO / ORIENTAÇÃO FUTURA
- item
- item

========================
REGRAS FINAIS
========================

- NÃO resumir
- NÃO omitir
- NÃO interpretar
- NÃO inventar
- NÃO reorganizar informação

Se existirem 10 itens no JSON, devem existir 10 itens no output.

Responde apenas com o relatório final.
"""

