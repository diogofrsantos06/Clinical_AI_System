import json

def change_data_format(dados_json, seccao_alvo=None):
    # 1. Garante que os dados são um dicionário Python
    if isinstance(dados_json, str):
        dados_json = json.loads(dados_json)

    texto_final = ""
    
    # 2. Dicionário de tradução/mapeamento de secções
    seccoes_mapeamento = {
        "diagnosticos": "Diagnósticos",
        "medicacao": "Medicação Habitual",
        "alergias": "Alergias",
        "exames": "Exames e Resultados",
        "sintomas": "Sintomas",
        "plano": "Plano Terapêutico"
    }

    # 3. LINHA SIMPLIFICADA: Decisão de qual secção filtrar
    if seccao_alvo:
        # Se escolheste uma secção, criamos um mini-mapeamento apenas com ela
        seccoes_a_processar = {seccao_alvo: seccoes_mapeamento[seccao_alvo]}
    else:
        # Se não escolheste nenhuma, processamos todas as secções por defeito
        seccoes_a_processar = seccoes_mapeamento

    # 4. Loop principal: Varre cada diário clínico (a chave 'nome_diario' contém a Data)
    for nome_diario, conteudo in dados_json.items():
        bloco_diario_texto = ""
        
        # 5. Loop secundário: Varre as secções que decidimos processar
        for chave, titulo in seccoes_a_processar.items():
            lista_dados = conteudo.get(chave, [])
            
            # Se esta secção estiver vazia neste diário, passa à frente
            if not lista_dados:
                continue 
            
            # Adiciona o título da secção (ex: "Medicação Habitual")
            bloco_diario_texto += f"{titulo}\n"
            
            # 6. Loop terciário: Transforma a lista de objetos JSON em linhas de texto
            for item in lista_dados:
                detalhes = [f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in item.items() if v]
                bloco_diario_texto += f"- {' | '.join(detalhes)}\n"
            bloco_diario_texto += "\n"
            
        # 7. Junção final: Se o diário tinha dados, cola tudo e destaca a DATA no topo
        if bloco_diario_texto:
            texto_final += f"--- IDENTIFICAÇÃO E DATA DO REGISTO: {nome_diario} ---\n{bloco_diario_texto}\n"

    return texto_final.strip()