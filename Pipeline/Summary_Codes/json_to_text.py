import json

def change_data_format(dados_json):

    if isinstance(dados_json, str):
        dados_json = json.loads(dados_json)

    texto_final = "RELATÓRIO CLÍNICO POR DIÁRIO\n\n"

    for nome_diario, conteudo in dados_json.items():
        texto_final += f"--- DIÁRIO: {nome_diario} ---\n"
        
        seccoes = {
            "diagnosticos": "Diagnósticos",
            "medicacao": "Medicação",
            "alergias": "Alergias",
            "exames": "Exames",
            "sintomas": "Sintomas",
            "plano": "Plano Terapêutico"
        }

        for chave, titulo in seccoes.items():
            lista_dados = conteudo.get(chave, [])
            if not lista_dados:
                continue 
            
            texto_final += f"{titulo}\n"

            for item in lista_dados:
                detalhes = [f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in item.items() if v]
                texto_final += f"- {' | '.join(detalhes)}\n"
            texto_final += "\n"

    return texto_final

