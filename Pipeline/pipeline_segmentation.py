import re, sys
from pathlib import Path

from Pipeline.llm import chat

BASE_DIR = Path(__file__).resolve().parent  
PROJ_ROOT = BASE_DIR.parent                 

if str(PROJ_ROOT) not in sys.path:
    sys.path.append(str(PROJ_ROOT))
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


def gerar_titulo_diario(texto_diario, index):
    """Extrai a data e a especialidade do cabeçalho estruturado encontrado no diário."""

    if not texto_diario or not texto_diario.strip():
        return f"Nota Clínica {index}"
        
    date_part = r'\d{1,2}[-/](?:[A-Za-z]{3}|\d{1,2})[-/]\d{2,4}'
    time_part = r'(?:\s+\d{2}:\d{2}(?::\d{2})?)?'
    doctor_part = r'.*?(?:Dr\(?a?\)?\.?\s|Drª\s|Médico:)' 
    
    padrao_cabecalho = fr'{date_part}{time_part}{doctor_part}[^\n]*'
    match_linha = re.search(padrao_cabecalho, texto_diario, re.IGNORECASE)
    
    # Se encontrar, usa essa linha como a "primeira_linha" do teu código original.
    # Se não encontrar (fallback), usa a primeira linha com texto que encontrar.
    if match_linha:
        primeira_linha = match_linha.group(0).strip()
    else:
        linhas = [l.strip() for l in texto_diario.split('\n') if l.strip()]
        if not linhas:
            return f"Nota Clínica {index}"
        primeira_linha = linhas[0]

    # Extrair a Data
    match_data = re.search(r'\d{1,2}[-/](?:[A-Za-z]{3}|\d{1,2})[-/]\d{2,4}', primeira_linha)
    data = match_data.group(0) if match_data else "Data Desconhecida"
    
    if re.match(r'\d{2}-\d{2}-\d{4}', data):
        meses = {
            '01':'Jan', '02':'Fev', '03':'Mar', '04':'Abr', '05':'Mai', '06':'Jun', 
            '07':'Jul', '08':'Ago', '09':'Set', '10':'Out', '11':'Nov', '12':'Dez'
        }
        partes = data.split('-')
        if len(partes) == 3:
            dia, mes, ano = partes
            data = f"{dia}-{meses.get(mes, mes)}-{ano}"
    
    if '/' in primeira_linha:
        especialidade = primeira_linha.split('/')[-1].strip()
    elif '(' in primeira_linha and ')' in primeira_linha:
        match_especialidade = re.search(r'\(([^)]+)\)[^()]*$', primeira_linha)
        especialidade = match_especialidade.group(1).strip() if match_especialidade else f"Nota Clínica {index}"
    else:
        especialidade = f"Nota Clínica {index}" 
        
    especialidade = re.sub(r'[\\/*?:"<>|.,;]', '', especialidade).strip()
    especialidade = re.sub(r'\s+', '_', especialidade)

    return f"{especialidade} - {data}"

def get_diary_start_indices(text):
    """Mapeia os índices de início reais de cada registo clínico por expressão regular."""
    date_part = r'\d{1,2}[-/](?:[A-Za-z]{3}|\d{1,2})[-/]\d{2,4}'
    time_part = r'(?:\s+\d{2}:\d{2}(?::\d{2})?)?'
    doctor_part = r'.*?(?:Dr\(?a?\)?\.?\s|Drª\s|Médico:)' 
    
    full_pattern = f'{date_part}{time_part}{doctor_part}'
    return [m.start() for m in re.finditer(full_pattern, text, re.IGNORECASE)]


def run_smart_segmentation(full_text, client):
    """
    Segmenta o texto purificado mapeando os limites via Regex estrutural.
    Aplica a limpeza residual do cabeçalho de consulta externa e executa a LLM restritiva no último diário.
    """

    indices = get_diary_start_indices(full_text)
    
    print(f"[DEBUG SEGMENTATION] Regex localizou {len(indices)} inícios de diários clínicos.", flush=True)
    
    if not indices:
        print("[AVISO] Falha ao segmentar: Nenhum padrão detetado. Devolvendo bloco inteiro.", flush=True)
        return [{"titulo": "Documento Clínico Unificado", "texto": full_text}]
        
    indices.append(len(full_text))
    todos_diarios = []
    total_esperado = len(indices) - 1

    for i in range(total_esperado):
        inicio = indices[i]
        fim = indices[i+1]
        segmento_bruto = full_text[inicio:fim].strip()
        
        if len(segmento_bruto) < 20: 
            continue

        e_ultimo = (i == total_esperado - 1)

        segmento_limpo = re.sub(r'Diário\s+Clínico\s*\n*\s*Consulta\s+Externa', '', segmento_bruto, flags=re.IGNORECASE)
        segmento_limpo = segmento_limpo.replace("Diário Clínico", "").replace("Consulta Externa", "")
        segmento_limpo = re.sub(r'Pag\.\s*\d+\s*/\s*\d+', '', segmento_limpo, flags=re.IGNORECASE)
        segmento_limpo = re.sub(r'\n\s*\n+', '\n\n', segmento_limpo).strip()

        if e_ultimo:
            print(f"[{i+1}/{total_esperado}] Processando Bloco Final. Invocando LLM para isolar Diagnósticos...", flush=True)
            
            sys_prompt = """És um assistente médico especialista em curadoria de registos hospitalares.
Este é o último bloco do documento e pode conter secções administrativas e finais.
Se aparecerem:
1. DEVES REMOVER completamente as secções: "Notas de Enfermagem", "Medicação", "MCDT Requisitados" e "Destino do Doente".
2. DEVES MANTER a secção "Diagnósticos" (ou "Diagnosticos") e o seu respetivo conteúdo clínico.
3. Adiciona essa secção de Diagnósticos no final da narrativa clínica do médico.
4. Devolve exclusivamente o texto resultante limpo, sem comentários ou markdown."""
            
            try:
                resposta, _, _ = chat(client, user_prompt=segmento_limpo, system_prompt=sys_prompt)
                texto_final = resposta.strip()
            except Exception as e:
                print(f"⚠️ Falha ao processar o fecho administrativo via LLM: {e}")
                texto_final = segmento_limpo
        else:
            texto_final = segmento_limpo

        if len(texto_final) > 10:
            titulo_gerado = gerar_titulo_diario(segmento_bruto, i+1)
            
            todos_diarios.append({
                "id": i + 1,
                "titulo": titulo_gerado,
                "texto": texto_final
            })
            print(f"Diário {i+1}/{total_esperado} Estruturado com Sucesso: {titulo_gerado}", flush=True)

    return todos_diarios