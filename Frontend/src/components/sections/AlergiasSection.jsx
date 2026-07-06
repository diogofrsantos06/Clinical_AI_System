import Highlight from '../Highlight';

export default function AlergiasSection({ alergias, searchTerm = ''  }) {
  const valoresNulos = ["Sem alergias conhecidas", "N/A", "Nenhum", ""];
  const primeiraAlergiaStr = alergias && alergias.length > 0 ? (alergias[0].substancia || alergias[0]) : "";
  const temAlergias = alergias && alergias.length > 0 && !valoresNulos.includes(primeiraAlergiaStr);
  
  return (
    <div className="w-full mb-8">
      <div className="flex items-center gap-3 mb-6">
          <div className={`p-1 rounded-md text-white flex items-center justify-center ${temAlergias ? 'bg-amber-600' : 'bg-[#2d6a4f]'}`}>           <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
             <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
             <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
           </svg>
        </div>
        <div>
          <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', fontWeight: 'bold', lineHeight: '1' }}>Alergias</h3>
          <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '1px' }}>
            {temAlergias ? `${alergias.length} alergias identificadas` : "Sem alergias conhecidas"}
          </p>
        </div>
      </div>

      {/* CONTEÚDO */}
      {temAlergias ? (
        // Caixa de Alerta (quando há alergias)
        <div className="bg-[#fffbeb] p-6 rounded-2xl border border-amber-200 shadow-sm">
          <div className="mb-4 p-3 bg-amber-50 border border-amber-100 rounded-lg text-amber-800 text-sm flex items-center gap-2">
            <span className="font-bold">⚠️ Atenção:</span> verifique antes de prescrever.
          </div>
          <div className="space-y-3">
            {alergias.map((item, i) => (
              <div key={i} className="bg-white p-4 rounded-xl border border-slate-200 flex justify-between items-center shadow-sm">
                <div>
                  <div className="font-bold text-slate-900"><Highlight text={item.substancia || item} term={searchTerm} /></div>
                  <div className="text-sm text-slate-600"><Highlight text={item.reacao || 'Sem descrição da reação'} term={searchTerm} /></div>

                  {item.registo_origem && item.registo_origem !== "N/A" && (
                    <div className="text-xs text-slate-400 mt-2 italic font-medium">
                      Identificado pela 1ª vez em: {item.registo_origem}
                    </div>
                  )}
                  
                </div>
                <span className="bg-rose-50 text-rose-700 text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">Grave</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        // Caixa Branca Neutra (quando não há alergias)
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-center gap-3">          <div className="bg-slate-200 p-1 rounded-full text-slate-600 mt-0.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <div>
            <p className="font-bold text-slate-900 m-0">Sem alergias conhecidas</p>
            <p className="text-sm text-slate-500 m-0">Confirme com o paciente sempre que prescrever.</p>
          </div>
        </div>
      )}
    </div>
  );
}