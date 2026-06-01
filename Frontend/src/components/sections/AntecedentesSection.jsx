export default function AntecedentesSection({ antecedentes }) {
    console.log("Dados de antecedentes recebidos:", antecedentes);
  return (
    <div className="w-full mb-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-[#2d6a4f] p-1 rounded-md text-white">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z" />
          </svg>
        </div>
        <div>
          <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', letterSpacing: '-0.01em', fontWeight: 'bold', lineHeight: '1' }}>
            Antecedentes Pessoais e Diagnósticos
          </h3>
          <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '1px' }}>
            {antecedentes.length} registos
          </p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 0.8fr', gap: '16px', padding: '14px 18px', borderBottom: '1px solid var(--ink-50)', fontSize: '12px', color: 'var(--ink-500)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          <div>Diagnóstico</div>
          <div>Evolução</div>
          <div className="text-right">Desde</div>
        </div>

        <div className="text-slate-800">
          {antecedentes.map((item, i) => (
            <div 
              key={i} 
              style={{ 
                display: 'grid', 
                gridTemplateColumns: '2fr 1fr 0.8fr', 
                gap: '16px', 
                padding: 'var(--row-pad-y, 14px) 18px', 
                borderBottom: '1px solid var(--ink-50)', 
                fontSize: '14px', 
                alignItems: 'center' 
              }}
              className="hover:bg-slate-50 transition-colors last:border-0"
            >
              <div>
                <div className="font-medium text-slate-800">{item.diagnostico}</div>
                  {/* Alterado de text-emerald-600 para text-slate-500 e removida a cor manual */}
                <div className="text-xs text-slate-500 font-normal mt-0.5">
                  {item.tipo || 'N/A'}
                </div>
              </div>

              <div className="text-slate-600">
                {item.temporalidade || 'N/A'}
              </div>

              <div className="text-right text-slate-600">
                {item.desde || 'Sem informação'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}