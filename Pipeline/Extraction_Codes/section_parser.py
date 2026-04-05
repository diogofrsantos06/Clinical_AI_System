import json
import sys
import re

from typing import Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from groq_client import chat, get_client

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SYSTEM_PROMPT_PATH = BASE_DIR / "Pipeline" / "System_Prompts" / "Section_Parser.txt"

@dataclass
class DiarySection:
    """Representa as secções de um diário clínico."""
    data: Optional[str] = None
    historia_clinica: Optional[str] = None  
    exames_e_resultados: Optional[str] = None  
    avaliacao_e_sintomas: Optional[str] = None  
    terapeutica_e_medicao: Optional[str] = None  
    plano_e_decisao: Optional[str] = None  
    diagnosticos: Optional[str] = None  
    outras_informacoes: Optional[str] = None 
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        """Converte para dicionário."""
        return asdict(self)

SECTION_SPLITTING_PROMPT = """
Analisa o diário clínico abaixo e extrai o texto INTEGRAL para as seguintes chaves JSON. 

REGRAS DE OURO:
1. NÃO cries sub-chaves ou novos campos JSON. Todo o conteúdo deve ser apenas uma string dentro da chave correspondente.
2. MANTÉM o texto original exatamente como aparece, incluindo listas, valores e quebras de linha.
3. Se houver vários resultados para uma secção (ex: vários exames), coloca-os todos como texto corrido ou lista textual dentro da chave correspondente.
4. As palavras-chave são apenas guias para ajudar a identificar as secções, mas estas podem não estar presentes em todos os diários.

CHAVES OBRIGATÓRIAS:
1. "data": Data do diário.
    * Palavras-chave para identificar: "Data:"
2. "historia_clinica": Deve conter a história clínica completa, incluindo AP, Diagnósticos prévios e evolução do episódio atual. Não deve conter medicação.
    * Palavras-chave para identificar: "AP:", "Diagnósticos anteriores:", "Evolução do episódio atual:"
3. "exames_e_resultados": Texto completo de análises, MCDTs, GSA, Imagem, etc.
    * Palavras-chave para identificar: "MCDTs:", "Exames realizados:", "Resultados de exames:"
4. "avaliacao_e_sintomas": Exame objetivo, queixas, sintomas e observações físicas.
    * Palavras-chave para identificar: "S/:", "C/:", "EO:", "Queixas:", "Sintomas:"
5. "terapeutica_e_medicao": Medicação habitual e prescrições atuais. Se aparecer infomação sobre alergias, deve ser incluída aqui.
    * Palavras-chave para identificar: "MH:", "Medicação habitual:", "Prescrição atual:", "Alergias:"
6. "diagnosticos": Lista de diagnósticos confirmados, hipóteses diagnósticas ou suspeitas clínicas.
    * Palavras-chave para identificar: "Possível diagnóstico", "Hipótese", "Suspeita"
7. "plano_e_decisao": Próximos passos, propostas e destino do doente.
    * Palavras-chave para identificar: "Plano:", "Proposta:", "Destino do doente:", "Decisão:"
8. "outras_informacoes": Notas administrativas ou que não se enquadrem acima.
    * Palavras-chave para identificar: "Observações administrativas:", "Notas adicionais:"

TEXTO PARA ANALISAR:
{diary_text}

RESPOSTA (APENAS JSON PURO):
"""

class LLMSectionParser:
    def __init__(self, system_prompt_path: Optional[Path] = None):
        self.client = get_client()
        
        path = system_prompt_path or DEFAULT_SYSTEM_PROMPT_PATH 
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read().strip()
        except Exception as e:
            self.system_prompt = "És um assistente médico especialista em organizar notas clínicas."
            print(f"Aviso: Usando fallback porque o ficheiro não foi lido: {e}")
    
    def parse(self, diary_text: str) -> DiarySection:
        user_prompt = SECTION_SPLITTING_PROMPT.format(diary_text=diary_text)
        response = chat(self.client, user_prompt, self.system_prompt)
        
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = re.sub(r'```json\s*|```', '', response_clean)

        try:
            data = json.loads(response_clean)
        except json.JSONDecodeError:
            
            json_match = re.search(r'(\{.*\})', response_clean, re.DOTALL)
            if json_match:
                try:
                    raw_json = json_match.group(1)
                    sanitized_json = raw_json.replace('\n', '\\n').replace('\r', '')
                    sanitized_json = sanitized_json.replace('{\\n', '{').replace('\\n}', '}').replace('\\n"', '"').replace('",\\n', '",')
                    
                    data = json.loads(sanitized_json)
                except Exception as e:
                    print(f"Erro persistente ao decodificar JSON: {e}")
                    return DiarySection(outras_informacoes=diary_text)
            else:
                return DiarySection(outras_informacoes=diary_text)

        return DiarySection(
            data=data.get('data'),
            historia_clinica=data.get('historia_clinica'),
            exames_e_resultados=data.get('exames_e_resultados'),
            avaliacao_e_sintomas=data.get('avaliacao_e_sintomas'),
            terapeutica_e_medicao=data.get('terapeutica_e_medicao'),
            diagnosticos=data.get('diagnosticos'),
            plano_e_decisao=data.get('plano_e_decisao'),
            outras_informacoes=data.get('outras_informacoes')
        )


'''
# -------------------------- Teste -------------------------- 
def split_diary_sections(patient_id: str, system_prompt_path: Path, patients_base_dir: Path):
    """
    Divide os diários de um paciente em secções usando LLM.
    """
    patient_dir = patients_base_dir / patient_id
    diaries_dir = patient_dir / "cleaned"
    output_dir = patient_dir / "sections"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not diaries_dir.exists():
        print(f"Diretório não encontrado: {diaries_dir}")
        return {}
    
    diary_files = sorted(diaries_dir.glob("cleaned_diary_*.txt"))
    
    if not diary_files:
        print(f"Nenhum diário encontrado em: {diaries_dir}")
        return {}
    
    print(f"Dividindo {len(diary_files)} diários em secções")
    print(f"Paciente: {patient_id}")
    
    parser = LLMSectionParser(system_prompt_path)
    cleaner = DiaryCleaner() 

    all_sections = {}
    
    for i, diary_file in enumerate(diary_files, 1):
        print(f"[{i}/{len(diary_files)}] {diary_file.name}")
        
        with open(diary_file, 'r', encoding='utf-8') as f:
            diary_text = f.read()
        
        clean_text = cleaner.clean_diary(diary_text)
        
        sections = parser.parse(clean_text)
        
        output_file = output_dir / f"{diary_file.stem}_sections.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sections.to_dict(), f, ensure_ascii=False, indent=2)
        
        all_sections[diary_file.name] = sections.to_dict()
    
    consolidated_path = output_dir / "all_sections.json"
    
    with open(consolidated_path, 'w', encoding='utf-8') as f:
        json.dump(all_sections, f, ensure_ascii=False, indent=2)
    
    print(f"Divisão completa!")
    print(f"Secções guardadas em: {output_dir}")
    print(f"Consolidado: {consolidated_path.name}")
    
    return all_sections


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    PATIENTS_DIR = BASE_DIR / "Patients"
    
    SYSTEM_PROMPT_PATH = BASE_DIR / "System_Prompts" / "Section_Parser.txt"
    
    patient_test_id = "Patient_test2" 
    
    print(f"Iniciando Pipeline de Segmentação para: {patient_test_id}")
    
    sections = split_diary_sections(
        patient_id=patient_test_id,
        system_prompt_path=SYSTEM_PROMPT_PATH,
        patients_base_dir=PATIENTS_DIR
    )
    '''
