"""
Ponto de entrada da geração de dados sintéticos.

A semente e o percurso clínico do paciente 1 são escritos à mão (ver
output/paciente_1_seed.json e output/paciente_1_percurso.json). Este script
lê os dois, e gera o texto completo de cada diário do percurso, guardando cada
um num ficheiro .txt separado — para poderes depois testar o teu pipeline real
de extração/segmentação com eles, tal como farias com PDFs verdadeiros.

USO:
    export GROQ_API_KEY="a-tua-chave"
    python -m Synthetic_Data.run_synthetic_pipeline
"""
import json
import re
from pathlib import Path

#from Synthetic_Data.groq_client import get_client
from Synthetic_Data.openai_client import get_client
from Synthetic_Data.diary_content_generator import DiaryContentGenerator

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
SEED_PATH = OUTPUT_DIR / "paciente_5_seed.json"
PATHWAY_PATH = OUTPUT_DIR / "paciente_5_percurso.json"
DIARIES_DIR = OUTPUT_DIR / "diarios_paciente_5"


def load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_pathway():
    with open(PATHWAY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def nome_ficheiro(indice: int, visita: dict) -> str:
    especialidade_limpa = re.sub(r'[^A-Za-z0-9_]', '_', visita["especialidade"])
    data_limpa = visita["data"].replace("/", "-")
    return f"{indice:02d}_{especialidade_limpa}_{data_limpa}.txt"


def run():
    if not SEED_PATH.exists():
        raise FileNotFoundError(f"Não encontrei {SEED_PATH}. Preenche este ficheiro à mão primeiro.")
    if not PATHWAY_PATH.exists():
        raise FileNotFoundError(f"Não encontrei {PATHWAY_PATH}. Preenche este ficheiro à mão primeiro.")

    seed = load_seed()
    pathway = load_pathway()
    visitas = pathway.get("percurso", [])

    print(f"Semente carregada: {seed['paciente']['nome']}, "
          f"{len(seed.get('patologias_cronicas', []))} patologias crónicas.", flush=True)
    print(f"Percurso carregado: {len(visitas)} visitas "
          f"({sum(1 for v in visitas if v['tipo'] == 'ruido')} de ruído, "
          f"{sum(1 for v in visitas if v['tipo'] == 'urgencia')} de urgência).\n", flush=True)

    api_key = get_client()
    generator = DiaryContentGenerator(api_key)

    DIARIES_DIR.mkdir(parents=True, exist_ok=True)

    seed_atual = seed  # começa como a semente original

    for i, visita in enumerate(visitas, start=1):
        print(f"[{i}/{len(visitas)}] A gerar diário: {visita['especialidade']} "
              f"({visita['tipo']}, {visita['data']})...", flush=True)

        try:
            diary_text = generator.generate(seed_atual, visita)
        except Exception as e:
            print(f"  [ERRO] Falhou a gerar este diário: {e}", flush=True)
            continue
        
        out_path = DIARIES_DIR / nome_ficheiro(i, visita)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(diary_text)

        print(f"  -> guardado em {out_path} ({len(diary_text)} caracteres)", flush=True)

        seed_atual = aplicar_alteracoes(seed_atual, visita.get("alteracoes_seed"))

    print(f"\nConcluído. Diários guardados em: {DIARIES_DIR}", flush=True)

def aplicar_alteracoes(seed, alteracoes):
    """Aplica as alterações declaradas no percurso diretamente à semente, sem LLM."""
    if not alteracoes:
        return seed

    for novo_dx in alteracoes.get("novos_diagnosticos_cronicos", []):
        seed["patologias_cronicas"].append(novo_dx)

    for novo_farmaco in alteracoes.get("nova_medicacao", []):
        seed["medicacao_base"].append(novo_farmaco)

    removidos = alteracoes.get("medicacao_removida", [])
    if removidos:
        seed["medicacao_base"] = [
            f for f in seed["medicacao_base"] if f["farmaco"] not in removidos
        ]

    return seed


if __name__ == "__main__":
    run()
