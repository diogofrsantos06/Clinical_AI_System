import json

def change_data_format(dados_json):
    # 1. Se for string, converte para dicionário
    if isinstance(dados_json, str):
        dados_json = json.loads(dados_json)

    texto_final = "RELATÓRIO CLÍNICO POR DIÁRIO\n\n"

    # 2. Iteramos sobre cada Diário (cada chave no JSON pai)
    for nome_diario, conteudo in dados_json.items():
        texto_final += f"--- DIÁRIO: {nome_diario} ---\n"
        
        # 3. Dicionário de mapeamento para as secções internas
        seccoes = {
            "diagnosticos": "Diagnósticos",
            "medicacao": "Medicação",
            "alergias": "Alergias",
            "exames": "Exames",
            "sintomas": "Sintomas",
            "plano": "Plano Terapêutico"
        }

        # 4. Iteramos sobre as secções dentro de cada diário
        for chave, titulo in seccoes.items():
            lista_dados = conteudo.get(chave, [])
            if not lista_dados:
                continue # Pula secções vazias para não poluir o texto
            
            texto_final += f"{titulo}\n"
            # 5. Formatação dos itens internos
            for item in lista_dados:
                detalhes = [f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in item.items() if v]
                texto_final += f"- {' | '.join(detalhes)}\n"
            texto_final += "\n"

    return texto_final

