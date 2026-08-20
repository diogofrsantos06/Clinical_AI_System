PROMPT_DIARY_CONSULTA = """
Atua como um Médico Sénior a escrever uma nota clínica de consulta externa, para um caso sintético de teste. O teu objetivo é produzir um diário clínico REALISTA, no estilo telegráfico e denso que os médicos realmente usam — não é prosa fluida nem um resumo bonito, é uma nota escrita a correr, entre doentes.

DADOS DO PACIENTE (para manteres coerência clínica com o resto do histórico — usa isto só para saberes o que escrever, NUNCA escrevas o nome do paciente no texto, ver regra abaixo):
{seed_json}

DADOS DESTA VISITA:
- Especialidade: {especialidade}
- Data: {data}
- Contexto detalhado (usa isto como guião do que a nota deve cobrir — não te limites a resumir isto, desenvolve cada achado mencionado com o detalhe clínico que um médico realmente registaria):
{contexto}

--- DENSIDADE (CRÍTICO — LÊ COM ATENÇÃO) ---
Diários clínicos reais são tipicamente LONGOS e DETALHADOS, não umas poucas frases. A maioria das notas reais desta base de dados tem uma dimensão considerável (na ordem de várias centenas a milhares de caracteres). Isto vem sobretudo da secção de exames — os exames objetivos e complementares raramente faltam, e quando estão presentes são detalhados, não resumidos numa linha. Trata os exames como o "corpo" da nota, não como um extra opcional.

--- REGRA CRÍTICA: NUNCA MENCIONES O NOME DO PACIENTE NO CORPO DO TEXTO ---
Os diários reais não repetem o nome do doente no corpo da nota (o nome já consta noutro sítio do processo). No corpo do texto, refere-te ao paciente de uma destas formas, escolhendo livremente:
- Um descritor breve: "homem, 55 anos", "mulher de 48 anos", "doente de 32 anos".
- Ou nem sequer refires o sujeito explicitamente — vai direto à informação clínica: "Refere melhoria das queixas.", "Sem sinais de alarme.".
Nunca escrevas "Paciente: [Nome]" nem qualquer nome próprio do doente.

--- ESTILO DE ESCRITA (CRÍTICO) ---
- Frases curtas, telegráficas, muitas vezes sem verbo ou sujeito explícito.
- Cada nota tem "a caligrafia" de um médico diferente — decide, para ESTA nota, um estilo pessoal (mais telegráfico vs. mais descritivo; mais ou menos uso de abreviaturas; frases mais curtas vs. mais longas) e mantém-no consistente dentro da nota, mas varia de nota para nota.
- Não escrevas como um relatório formal para um leigo — escreve como um médico a documentar para outro médico.

--- PROIBIDO USAR TÍTULOS FORMAIS POR EXTENSO ---
Nunca escrevas títulos de secção completos e formais como "Medicação Habitual:", "Exames Objetivos:", "Antecedentes Pessoais:". Estes NUNCA aparecem em notas reais. As únicas formas aceitáveis de introduzir um tópico são: a abreviatura (MH, EO, AP, ECD/MCDTs), OU nenhuma etiqueta (nenhuma informação integrada diretamente na frase). Um título por extenso com maiúscula inicial e dois pontos é sempre um erro.

--- VARIABILIDADE DE FORMATO POR TÓPICO (CRÍTICO — não sigas sempre o mesmo padrão) ---
Para CADA tópico abaixo, decide de forma independente e aleatória qual das opções de formato usar nesta nota — não uses sempre a mesma opção em todas as notas, e não sigas sempre a mesma ordem entre tópicos:

- ANTECEDENTES: escolhe UMA destas abordagens nesta nota — não misturas sempre a mesma forma:
  a) BLOCO AGRUPADO: a maioria dos antecedentes relevantes reunidos numa frase/bloco compacto logo no início ("AP:" / "AP -" / "Antecedentes:" seguido da lista, ex: "AP: AR, HTA, hipotiroidismo, DLP."). Esta é uma opção comum e válida — usa-a com frequência, não só ocasionalmente.
  b) Sem etiqueta nenhuma, misturados em frases ao longo do texto (ex: "Doente com antecedentes de EM, refere...").
  c) Nem sequer mencionados nesta nota.
  Podes também combinar (a) com um antecedente extra a aparecer depois, de passagem — mas o grupo principal deve normalmente sair concentrado, não disperso frase a frase por todo o texto.
- MEDICAÇÃO HABITUAL/AGUDA: escolhe, para esta nota especificamente, UMA destas abordagens:
  a) BLOCO AGRUPADO: "MH:" seguido da lista de fármacos relevantes num só bloco (ex: "MH: MTX 15mg/semana, ácido fólico, prednisolona 5mg id, perindopril 5mg id."). Usa esta opção com frequência.
  b) Não mencionar medicação nenhuma (se não for relevante ao contexto desta visita).
  c) Mencionar só 1-2 fármacos especificamente relevantes ao contexto, sem listar o resto.
  d) Mencionar vários fármacos espalhados pelo texto, alguns com dosagem completa e outros só pelo nome.
  Nunca repitas sempre a lista completa e idêntica da semente, palavra por palavra, nota após nota — varia entre estas abordagens.
- ALERGIAS: quando mencionadas (raro — só se for clinicamente relevante para esta visita), tipicamente é uma menção curta tipo "alergia a X" — só por vezes com a reação descrita a seguir, muitas vezes sem.
- EXAMES OBJETIVOS: presentes na maioria das notas, mas MANTÉM CONTIDOS — não é a secção principal da nota. A seguir a "EO:" / "EO -", OU sem etiqueta nenhuma. Inclui os sinais vitais (TA, FC, saturação, temperatura) e, no máximo, 1 a 2 sistemas mais relevantes ao contexto desta visita (não percorras sistematicamente todos os sistemas do corpo). Uma frase ou duas por sistema chega — não é preciso desenvolver cada achado ao mesmo nível de detalhe exigido para os MCDTs.
- EXAMES COMPLEMENTARES (MCDTs) — TEXTO CORRIDO, NUNCA TÓPICOS:
  PROIBIDO usar bullet points, travessões, ou títulos como "Técnica:", "Achados:", "Conclusão:" como itens de lista separados. Tudo em frases corridas, encadeadas, no mesmo estilo telegráfico do resto da nota.

  ANÁLISES (sangue, urina, etc.): só o nome do parâmetro e o valor, em frases corridas — podem estar todos numa linha ou espalhados por várias, consoante o tipo. Ex: "Hemograma: Hb 12,5 g/dL, Leucócitos 8500/uL, Plaquetas 250000/uL. Bioquímica: Creatinina 1,2 mg/dL, Ureia 40 mg/dL, Glicemia 90 mg/dL. VS 25 mm/h, PCR 12 mg/L." Nada de sub-tópicos, nada de organizar por categorias com títulos — é só a lista de parâmetros e valores, em frases.

  EXAMES DE IMAGEM/FUNCIONAIS (Rx, TAC, RMN, Ecografia, ECG, EEG, etc.): escreve como um parágrafo narrativo corrido, sem separar em partes rotuladas. Dentro desse parágrafo, menciona naturalmente: o que foi examinado, os achados relevantes estrutura a estrutura (sem cabeçalho nenhum a anunciar isso, só encadeia as frases), comparação com exame anterior se fizer sentido, e a impressão final — tudo fundido num texto só, como um relatório real está escrito.
  MÍNIMO 4-6 frases fundidas num parágrafo, não uma lista de 4-6 pontos.

  EXEMPLO DO FORMATO CERTO (prosa, sem tópicos):
  "Radiografia das mãos com incidências AP e perfil: articulações metacarpofalângicas com erosões ósseas ligeiras bilateralmente, sinovite associada, sem outras alterações ósseas relevantes. Comparativamente ao estudo prévio, denota discreta progressão das erosões. Achados compatíveis com artrite reumatoide em atividade moderada."

  EXEMPLO DO QUE NÃO FAZER (nunca uses este formato de tópicos):
  "- Técnica: incidências AP e perfil
  - Achados: erosões ósseas ligeiras
  - Conclusão: compatível com artrite reumatoide"
- DIAGNÓSTICOS: podem aparecer isolados, OU integrados numa frase junto de outra informação (ex: "Refere agravamento da rigidez articular; nódulos subcutâneos notados em doente com diabetes de longa data." — o diagnóstico de diabetes surge de passagem, sem ser destacado).
- PLANO: a palavra "Plano:" pode aparecer, ou a decisão terapêutica pode só estar integrada na última frase da nota, sem etiqueta nenhuma.

- Se o campo de contexto desta visita especificar exames concretos realizados (ex: "foi feito ECG e ecocardiograma"), tens de os incluir TODOS, com o mesmo nível de detalhe indicado acima — não ignores nenhum exame mencionado no contexto.

--- DENSIDADE POR ESPECIALIDADE (CRÍTICO — ALVOS DE DIMENSÃO) ---
- NÍVEL EXAUSTIVO — Medicina Interna, Reumatologia, Cardiologia: estas notas devem ser MUITO extensas — alvo de 3000 a 4500 caracteres. Aborda LITERALMENTE TUDO: todos os antecedentes crónicos, qualquer "ruído clínico" relevante da semente, exame objetivo contido (ver regra acima — sinais vitais + 1-2 sistemas), e vários exames complementares (analíticos E de imagem/funcionais) com descrição detalhada de cada um. Os MCDTs devem ser a secção mais extensa da nota, claramente maior do que o exame objetivo — se a nota ficar longa sobretudo à custa do exame objetivo, isso é um erro; desenvolve antes mais um exame complementar. Se, depois de escreveres, a nota te parecer "completa" mas curta, força-te a desenvolver mais um MCDT ou mais um antecedente antes de terminar, não mais um sistema do exame objetivo.
- NÍVEL INTERMÉDIO — Neurologia, Endocrinologia, Dermatologia e especialidades não listadas noutro nível: alvo de 1200 a 2000 caracteres.
- NÍVEL CURTO — Oftalmologia: notas curtas e diretas, 2-4 linhas, sem elaborar antecedentes ou exames extensos.

PROIBIDO RESUMIR EXAMES: nunca condenses um exame numa frase curta tipo "análises normais" ou "sem alterações relevantes". Descreve cada exame como um médico real descreveria — parâmetro a parâmetro, com números concretos, e para relatórios de imagem, frase a frase o que foi observado (localização, dimensões, características, comparação com exames anteriores se aplicável). Um único exame complementar bem descrito pode ocupar, por si só, várias linhas.

OUTROS ANTECEDENTES/ACHADOS (integra sem os assinalar como categoria à parte): a semente do paciente pode conter, no campo "ruido_clinico", elementos como episódios agudos passados, sintomas sem diagnóstico definido, achados prévios em exames, ou manifestações associadas a outras doenças. Se o contexto desta visita mencionar um destes elementos, escreve-o exatamente como escreverias qualquer outro dado clínico — misturado na frase, sem anunciares que é um "achado incidental" ou "ruído" ou nada que soe a categoria/relatório. Não escrevas frases como "achado incidental, sem necessidade de vigilância ativa" — em vez disso, menciona-o tal como um médico o mencionaria de passagem (ex: "mantém-se conhecido quisto renal simples, sem intercorrências." ou apenas "refere cefaleias ocasionais atribuídas a stress.").

--- PROIBIDO ABSOLUTAMENTE (nunca escrevas nenhuma destas palavras/frases como título ou introdução) ---
"Ruído clínico:", "Observações adicionais:", "Achados incidentais:", "Outros antecedentes:", ou qualquer frase que anuncie uma categoria antes de a desenvolver. A informação entra diretamente no fluxo do texto, sem anúncio prévio nenhum.

--- NÃO INCLUAS TUDO SEMPRE ---
Nem todos os tópicos acima têm de aparecer em toda a nota. Decide, de forma realista, quais fazem sentido para ESTA visita específica.

--- FORMATO DE CABEÇALHO OBRIGATÓRIO (uma única linha, sem exceções) ---
A PRIMEIRA linha do texto tem de seguir exatamente esta ordem, tudo na mesma linha, sem quebra de linha no meio:
[Data no formato DD-Mon-AAAA] Dr(a). [Nome fictício de médico, diferente a cada chamada] ({especialidade})

Exemplo real: "10-Set-2025 Dr(a). Maria João Silva (HUC-REUMATOLOGIA)"

NUNCA separes a data do nome do médico por uma quebra de linha. NUNCA omitas a data desta primeira linha. O corpo do diário começa só a partir da segunda linha.

Depois do cabeçalho, escreve o corpo do diário livremente. NÃO uses JSON, NÃO uses markdown.
"""









PROMPT_DIARY_URGENCIA = """
Atua como um Médico de Urgência a escrever o registo completo de um episódio de urgência, para um caso sintético de teste. O teu objetivo é produzir UM ÚNICO diário REALISTA, cobrindo o episódio do princípio ao fim (admissão, avaliação, decisão), seguindo a estrutura administrativa+clínica típica destes registos.

DADOS DO PACIENTE (para manteres coerência clínica — NUNCA escrevas o nome do paciente no texto, ver regra abaixo):
{seed_json}

DADOS DESTE EPISÓDIO:
- Especialidade/serviço: {especialidade}
- Data: {data}
- Contexto detalhado (usa isto como guião do que a nota deve cobrir — desenvolve cada achado mencionado com o detalhe clínico real, não te limites a resumir):
{contexto}

--- DENSIDADE (CRÍTICO) ---
Episódios de urgência reais geram notas longas e detalhadas — exame objetivo com vários parâmetros, e frequentemente exames complementares (análises, imagiologia) com achados descritos em detalhe. Trata os exames como parte central da nota, não como um extra.

--- REGRA CRÍTICA: NUNCA MENCIONES O NOME DO PACIENTE NO CORPO DO TEXTO ---
Refere-te ao paciente por um descritor breve ("mulher de 32 anos") ou sem sujeito explícito ("Refere dor abdominal..."). Nunca escrevas "Paciente: [Nome]" nem qualquer nome próprio do doente.

--- ESTILO DE ESCRITA (CRÍTICO) ---
- Telegráfico, denso, abreviado: "Refere dor abdominal c/ 2 dias evolução.", "Sem febre.", "TA 130/80, FC 78, apirético."
- Decide, para ESTA nota, um estilo pessoal do médico (mais ou menos verboso, mais ou menos uso de abreviaturas) e mantém-no consistente dentro da nota.
--- PROIBIDO USAR TÍTULOS FORMAIS POR EXTENSO ---
Nunca escrevas títulos de secção completos e formais como "Medicação Habitual:", "Exames Objetivos:", "Antecedentes Pessoais:". Estes NUNCA aparecem em notas reais. As únicas formas aceitáveis de introduzir um tópico são: a abreviatura (MH, EO, AP, ECD/MCDTs), OU nenhuma etiqueta nenhuma (informação integrada diretamente na frase). Um título por extenso com maiúscula inicial e dois pontos é sempre um erro.

OUTROS ANTECEDENTES/ACHADOS (integra sem os assinalar como categoria à parte): a semente do paciente pode conter, no campo "ruido_clinico", elementos como episódios agudos passados, sintomas sem diagnóstico definido, achados prévios em exames, ou manifestações associadas a outras doenças. Se o contexto desta visita mencionar um destes elementos, escreve-o exatamente como escreverias qualquer outro dado clínico — misturado na frase, sem anunciares que é um "achado incidental" ou "ruído" ou nada que soe a categoria/relatório. Não escrevas frases como "achado incidental, sem necessidade de vigilância ativa" — em vez disso, menciona-o tal como um médico o mencionaria de passagem (ex: "mantém-se conhecido quisto renal simples, sem intercorrências." ou apenas "refere cefaleias ocasionais atribuídas a stress.").

--- PROIBIDO ABSOLUTAMENTE (nunca escrevas nenhuma destas palavras/frases como título ou introdução) ---
"Ruído clínico:", "Observações adicionais:", "Achados incidentais:", "Outros antecedentes:", ou qualquer frase que anuncie uma categoria antes de a desenvolver. A informação entra diretamente no fluxo do texto, sem anúncio prévio nenhum.

--- VARIABILIDADE DE FORMATO POR TÓPICO (CRÍTICO — igual à lógica de consulta externa) ---
- ANTECEDENTES: a seguir a "AP:", ou sem etiqueta, integrados na frase, ou omitidos.
- MEDICAÇÃO HABITUAL: a seguir a "MH:", ou sem etiqueta, ou omitida.
- ALERGIAS: quando mencionadas, tipicamente curtas ("alergia a X"), reação nem sempre descrita.
- EXAME OBJETIVO: quase sempre presente, com vários parâmetros — TA, FC, saturação, temperatura, e achados relevantes ao motivo de vinda, descritos com detalhe (não só valores soltos).
- EXAMES COMPLEMENTARES: quando pedidos/realizados, apresenta valores analíticos específicos (vários parâmetros) e/ou descrições longas e detalhadas de imagiologia, tal como indicado para a consulta externa.
- DIAGNÓSTICOS: podem surgir integrados na narrativa, não só na secção formal.
- Podem surgir combinados numa frase só (ex: "dor lombar em doente hipertenso e diabético, sem sinais de alarme").

--- ESTRUTURA (inclui só as secções administrativas que fizerem sentido — nem todo episódio gera todas) ---
1. Cabeçalho (uma única linha, tudo junto, sem quebra de linha no meio): [Data e hora no formato DD-Mon-AAAA HH:MM:SS] Dr(a). [Nome fictício, diferente a cada chamada] ({especialidade})

Exemplo real: "03-Dez-2025 09:14:00 Dr(a). Ana Rita Ferreira (HUC-URG_MEDICA)"

NUNCA coloques a data depois do nome do médico. NUNCA separes por quebra de linha.
2. Narrativa clínica livre (motivo de vinda, antecedentes relevantes, achados, avaliação, decisão final) — segue a variabilidade de formato acima.
3. Se fizer sentido: "Notas de Enfermagem" (sinais vitais, observações).
4. Se houver diagnóstico atribuído: "Diagnósticos", com código genérico entre parêntesis (ex: "(M999) - Lesão biomecânica NE").
5. Se houver medicação administrada: "Medicação", tabela "Data Início | Data Fim | Data da última toma | Designação do Fármaco".
6. Se houver exames pedidos/realizados: "MCDT Requisitados / Procedimentos Efectuados", código alfanumérico + descrição (ex: "M10830 1 JOELHO 2 INCIDENCIAS"). Se o resultado já estiver disponível, descreve-o com o mesmo nível de detalhe indicado acima para MCDTs (pode ser uma descrição longa, especialmente para imagiologia).
7. Secção final "Destino do Doente" (inclui sempre, é o registo completo do episódio): "Data:", "Destino:", "Médico:".

NÃO uses JSON nem markdown — texto corrido, tal como um documento SClínico real.
"""
