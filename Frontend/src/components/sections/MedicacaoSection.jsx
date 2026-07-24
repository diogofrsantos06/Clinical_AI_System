import Highlight from '../Highlight';

export default function MedicacaoSection({ medicacao = [], searchTerm = ''  }) {
  const temAsterisco = medicacao.some(med => med.farmaco && med.farmaco.includes('*'));

  return (
    <div className="w-full mb-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-[#2d6a4f] p-1 rounded-md text-white">
          <div className="bg-[#2d6a4f] p-0.3 rounded-md text-white flex items-center justify-center">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="7" y="3" width="10" height="18" rx="5" ry="5" />
              <line x1="7" y1="12" x2="17" y2="12" />
            </svg>
          </div>
        </div>
        <div>
          <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', letterSpacing: '-0.01em', fontWeight: 'bold', lineHeight: '1' }}>
            Medicação Habitual
          </h3>
          <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '1px' }}>
            {medicacao.length} registos
          </p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Header original */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '1.5fr 0.8fr 1fr 1fr 1fr', 
          gap: '16px', 
          padding: '14px 18px', 
          borderBottom: '1px solid var(--ink-50)', 
          fontSize: '12px', 
          color: 'var(--ink-500)', 
          textTransform: 'uppercase', 
          letterSpacing: '0.08em' 
        }}>
          <div>Fármaco</div>
          <div>Dosagem</div>
          <div>Posologia</div>
          <div>Indicação</div>
          <div>Origem</div>
        </div>

        <div className="text-slate-800">
          {medicacao.map((med, i) => (
            <div 
              key={i} 
              style={{ 
                display: 'grid', 
                gridTemplateColumns: '1.5fr 0.8fr 1fr 1fr 1fr', 
                gap: '16px', 
                padding: '14px 18px', 
                borderBottom: '1px solid var(--ink-50)', 
                fontSize: '14px', 
                alignItems: 'center' 
              }}
              className="hover:bg-slate-50 transition-colors last:border-0"
            >
              <div className="font-medium text-slate-800"><Highlight text={med.farmaco || 'N/A'} term={searchTerm} /></div>
              <div className="text-slate-600"><Highlight text={med.dosagem || 'N/A'} term={searchTerm} /></div>
              <div className="text-slate-600"><Highlight text={med.posologia || 'N/A'} term={searchTerm} /></div>
              <div className="text-slate-600"><Highlight text={med.indicacao || 'N/A'} term={searchTerm} /></div>
              <div className="text-slate-500 leading-tight">
                <div className="font-semibold text-[11px] text-slate-700">
                  {/* Pega no texto até ao primeiro ' - ' (o nome da especialidade) */}
                  <Highlight text={med.diario_origem ? med.diario_origem.split(' - ')[0] : 'N/A'} term={searchTerm} />
                </div>
                <div className="text-[10px]">
                  {/* Pega na parte central que contém a data, removendo o Registo no final */}
                  <Highlight text={med.diario_origem ? med.diario_origem.split(' - ')[1].split('(')[0].trim() : ''} term={searchTerm} />
                </div>
              </div>
            </div>
          ))}
        </div>
        {temAsterisco && (
          <div className="p-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 italic">
            * Fármaco não confirmado no registo mais recente disponível — pode ter sido suspenso ou alterado desde então.
          </div>
        )}
      </div>
    </div> 
  );
}