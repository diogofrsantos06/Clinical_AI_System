import json

def achatar_dados_clinicos(dados_json):
    if isinstance(dados_json, str):
        try:
            dados_json = json.loads(dados_json)
        except json.JSONDecodeError:
            return "ERRO: O formato JSON é inválido."

    texto_final = "DADOS CLÍNICOS (LÊ TODOS OS REGISTOS E REPRODUZ OS NOMES EXATOS):\n\n"

    for titulo_original, info in dados_json.items():
        texto_final += f"--- DIÁRIO: {titulo_original} ---\n"

        # --- 1. ALERGIAS (O Workaround) ---
        # Tenta procurar uma chave 'alergias' caso adiciones no teu prompt de extração futuro
        alergias = info.get("alergias", [])
        if not alergias:
            # Procura a palavra "alergia" escondida dentro dos diagnósticos
            alergias = [d.get("doenca") for d in info.get("diagnosticos", []) if "alergia" in str(d.get("doenca")).lower()]
        
        texto_final += f"Alergias: {', '.join(alergias) if alergias else 'Sem alergias conhecidas'}\n"

        # --- 2. ANTECEDENTES E DIAGNÓSTICOS ---
        aps = []
        agudos = []
        for d in info.get("diagnosticos", []):
            doenca = d.get("doenca", "")
            # Ignora as alergias aqui para não repetir
            if "alergia" in doenca.lower():
                continue
                
            if d.get("temporalidade") == "cronico":
                aps.append(doenca)
            else:
                prefixo = " (Suspeita)" if d.get("tipo") == "suspeita" else ""
                agudos.append(f"{doenca}{prefixo}")
                
        texto_final += f"Antecedentes Crónicos: {', '.join(aps) if aps else 'Nenhum'}\n"
        texto_final += f"Diagnósticos Agudos: {', '.join(agudos) if agudos else 'Nenhum'}\n"

        # --- 3. MEDICAÇÃO HABITUAL ---
        meds_habitual = []
        for m in info.get("medicacao", []):
            if m.get("tipo") == "habitual":
                farmaco = m.get("farmaco", "")
                classe = m.get("classe", "")
                meds_habitual.append(f"{farmaco} ({classe})" if classe else farmaco)
                
        texto_final += f"Medicação Habitual: {', '.join(meds_habitual) if meds_habitual else 'Nenhuma'}\n"

        # --- 4. SINTOMAS (com Localização) ---
        sintomas = []
        for s in info.get("sintomas", []):
            desc = s.get("descricao", "")
            loc = s.get("localizacao", "")
            if loc and loc.lower() not in desc.lower():
                sintomas.append(f"{desc} ({loc})")
            else:
                sintomas.append(desc)
        texto_final += f"Sintomas: {', '.join(sintomas) if sintomas else 'Nenhum'}\n"

        # --- 5. EXAMES ---
        analises = []
        imagens = []
        for e in info.get("exames", []):
            tipo = (e.get("tipo_exame") or "").lower()
            param = e.get("parametro") or "Exame"
            
            if tipo in ["analise", "gasimetria"]:
                val = e.get("valor") or ""
                uni = e.get("unidade") or ""
                analises.append(f"{param}: {val} {uni}".strip())
            else:
                # Para ecografia, rx, tac, outro
                interp = e.get("interpretacao") or "Sem descrição"
                imagens.append(f"{tipo.upper()} ({param}): {interp}")

        texto_final += f"Análises: {', '.join(analises) if analises else 'Nenhuma'}\n"
        if imagens:
            texto_final += f"Imagiologia: {'; '.join(imagens)}\n"

        # --- 6. PLANO (com Urgência) ---
        planos = []
        for p in info.get("plano", []):
            acao = p.get("acao", "")
            urgencia = p.get("urgencia", "")
            planos.append(f"{acao} [{urgencia.upper()}]" if urgencia else acao)
            
        texto_final += f"Plano: {', '.join(planos) if planos else 'Nenhum'}\n\n"

    return texto_final