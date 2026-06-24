import json

def change_data_format(dados_json, seccao_alvo=None):

    if isinstance(dados_json, str):
        dados_json = json.loads(dados_json)

    texto_final = ""
    
    seccoes_mapeamento = {
        "diagnosticos": "Diagnósticos",
        "medicacao": "Medicação Habitual",
        "alergias": "Alergias",
        "exames": "Exames e Resultados",
        "sintomas": "Sintomas",
        "plano": "Plano Terapêutico"
    }

    if seccao_alvo:
        seccoes_a_processar = {seccao_alvo: seccoes_mapeamento[seccao_alvo]}
    else:
        seccoes_a_processar = seccoes_mapeamento

    diagnosticos_vistos = set()
    termos_vazios = {"sem informação", "n/a", "desconhecido", "não aplicável", "nenhum", "nenhuma"}

    # 3. Loop principal: Varre cada diário clínico
    for nome_diario, conteudo in dados_json.items():
        bloco_diario_texto = ""
        
        # 4. Loop secundário: Varre as secções
        for chave, titulo in seccoes_a_processar.items():
            lista_dados = conteudo.get(chave, [])
            
            if not lista_dados:
                continue 
            
            linhas_sec_texto = ""
            
            for item in lista_dados:
                detalhes = []
                
                for k, v in item.items():
                    if v:
                        valor_str = str(v).strip()
                        
                        if chave == "diagnosticos" and valor_str.lower() in termos_vazios:
                            continue
                            
                        detalhes.append(f"{k.replace('_', ' ').capitalize()}: {valor_str}")
                
                if not detalhes:
                    continue
                
                if chave == "diagnosticos":
                    assinatura_item = " | ".join(detalhes).lower()
                    if assinatura_item not in diagnosticos_vistos:
                        diagnosticos_vistos.add(assinatura_item)
                        linhas_sec_texto += f"- {' | '.join(detalhes)}\n"
                
                else:
                    linhas_sec_texto += f"- {' | '.join(detalhes)}\n"
            
            if linhas_sec_texto:
                bloco_diario_texto += f"{titulo}\n{linhas_sec_texto}\n"
                
        if bloco_diario_texto:
            texto_final += f"--- IDENTIFICAÇÃO E DATA DO REGISTO: {nome_diario} ---\n{bloco_diario_texto}\n"

    return texto_final.strip()