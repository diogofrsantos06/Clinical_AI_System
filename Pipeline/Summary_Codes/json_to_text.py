import json

def change_data_format(dados_json):

    if isinstance(dados_json, str):
        try:
            dados_json = json.loads(dados_json)
        except json.JSONDecodeError:
            return "ERRO: O formato dos dados fornecidos não é um JSON válido."

    texto_final = "DADOS CLÍNICOS EXTRAÍDOS (LÊ TODOS OS REGISTOS COM ATENÇÃO):\n\n"

    for titulo_diario, info in dados_json.items():
        texto_final += f"--- DIÁRIO: {titulo_diario} ---\n"

        # 1. DIAGNÓSTICOS
        cronicos = []
        agudos = []
        for d in info.get("diagnosticos", []):
            doenca = d.get("doenca", "")
            if not doenca: continue
            tipo = d.get("tipo", "")
            relevancia = d.get("relevancia", "")
            
            detalhes = []
            if tipo: detalhes.append(tipo.capitalize())
            if relevancia: detalhes.append(relevancia.capitalize())
            
            info_extra = f" [{', '.join(detalhes)}]" if detalhes else ""
            doenca_formatada = f"{doenca}{info_extra}"
            
            if d.get("temporalidade") == "cronico":
                cronicos.append(doenca_formatada)
            else:
                agudos.append(doenca_formatada)
                
        texto_final += f"Antecedentes Crónicos: {', '.join(cronicos) if cronicos else 'Nenhum'}\n"
        texto_final += f"Diagnósticos Agudos: {', '.join(agudos) if agudos else 'Nenhum'}\n"

        # 2. MEDICAÇÃO
        meds_habitual = []
        meds_outra = []
        for m in info.get("medicacao", []):
            farmaco = m.get("farmaco", "")
            if not farmaco: continue
            classe = m.get("classe", "")
            tipo_med = m.get("tipo", "") 
            desc_med = f"{farmaco} ({classe})" if classe else farmaco
            
            if tipo_med == "habitual":
                meds_habitual.append(desc_med)
            else:
                meds_outra.append(f"{desc_med} [{tipo_med.upper()}]" if tipo_med else desc_med)

        texto_final += f"Medicação Habitual: {', '.join(meds_habitual) if meds_habitual else 'Nenhuma'}\n"
        texto_final += f"Medicação na Urgência/Outra: {', '.join(meds_outra) if meds_outra else 'Nenhuma'}\n"

        # 3. ALERGIAS
        alergias = [a.get("substancia") for a in info.get("alergias", []) if a.get("substancia")]
        texto_final += f"Alergias: {', '.join(alergias) if alergias else 'Sem alergias conhecidas'}\n"

        # --- 4. EXAMES (A PROVA DE BALA) ---
        analises = []
        imagens = []
        for e in info.get("exames", []):
            parametro = e.get("parametro") or "Exame"
            valor = e.get("valor")
            unidade = e.get("unidade")
            relatorio = e.get("relatorio")
            tipo_exame = e.get("tipo_exame") or "Exame"
            
            # Se a chave "valor" tiver conteúdo, é garantidamente uma análise numérica
            if valor:
                str_unidade = f" {unidade}" if unidade else ""
                analises.append(f"{parametro}: {valor}{str_unidade}".strip())
            
            # Se a chave "relatorio" tiver conteúdo, é um texto descritivo
            elif relatorio:
                imagens.append(f"{tipo_exame.upper()} ({parametro}): {relatorio}")

        # Junta as análises separadas por ponto e vírgula, exatamente como pediste!
        texto_final += f"Análises: {'; '.join(analises) if analises else 'Nenhuma'}\n"
        if imagens:
            texto_final += f"Imagiologia e Outros: {'; '.join(imagens)}\n"

        # 5. SINTOMAS
        sintomas = []
        for s in info.get("sintomas", []):
            desc = s.get("descricao", "")
            loc = s.get("localizacao", "")
            tipo_sint = s.get("tipo", "")
            
            loc_tag = f" ({loc})" if loc and loc.lower() not in desc.lower() else ""
            tipo_tag = f" [{tipo_sint.capitalize()}]" if tipo_sint else ""
            sintomas.append(f"{desc}{loc_tag}{tipo_tag}")
            
        texto_final += f"Sintomas e Sinais: {', '.join(sintomas) if sintomas else 'Nenhum'}\n"

        # 6. PLANO
        planos = []
        for p in info.get("plano", []):
            acao = p.get("acao", "")
            tipo_plano = p.get("tipo", "")
            urgencia = p.get("urgencia", "")
            
            if acao:
                tags = []
                if tipo_plano: tags.append(tipo_plano.capitalize())
                if urgencia: tags.append(urgencia.upper())
                planos.append(f"{acao} [{', '.join(tags)}]" if tags else acao)
                
        texto_final += f"Plano: {', '.join(planos) if planos else 'Nenhum'}\n\n"

    print(texto_final)
    
    return texto_final