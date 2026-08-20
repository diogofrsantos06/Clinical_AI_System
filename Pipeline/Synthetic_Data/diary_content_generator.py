import json
import time
#from Synthetic_Data.groq_client import chat
from Synthetic_Data.openai_client import chat
from Synthetic_Data.Prompts.Diary_Content_Prompt import PROMPT_DIARY_CONSULTA, PROMPT_DIARY_URGENCIA


class DiaryContentGenerator:
    """Gera o texto completo de um diário clínico, a partir de uma entrada do
    percurso e da semente do paciente. Escolhe o prompt certo consoante o tipo
    de visita (urgência tem uma estrutura diferente de consulta/ruído)."""

    def __init__(self, api_key):
        self.api_key = api_key

    def generate(self, seed: dict, visita: dict) -> str:
        seed_json = json.dumps(seed, indent=2, ensure_ascii=False)

        contexto = visita.get("contexto") or visita.get("contexto_breve", "")

        if visita["tipo"] == "urgencia":
            user_prompt = PROMPT_DIARY_URGENCIA.format(
                seed_json=seed_json,
                especialidade=visita["especialidade"],
                data=visita["data"],
                contexto=contexto,
            )
        else:
            user_prompt = PROMPT_DIARY_CONSULTA.format(
                seed_json=seed_json,
                especialidade=visita["especialidade"],
                data=visita["data"],
                contexto=contexto,
            )

        system_prompt = "Escreves sempre em português de Portugal, no estilo telegráfico real de notas clínicas hospitalares."

        diary_text = chat(self.api_key, user_prompt=user_prompt, system_prompt=system_prompt)


        return diary_text.strip()
