import Highlight from '../Highlight';

export default function PlanoSection({ plano, searchTerm = '' }) {
  // 1. Verificação de segurança: garantimos que 'itensPlano' é sempre um array.
  // Se o backend enviar uma string (dados antigos) ou algo inválido, devolvemos array vazio.
  const itensPlano = Array.isArray(plano) ? plano : [];

  return (
    <div className="w-full mb-8">
      {/* Header da Secção */}
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-[#2d6a4f] p-1.5 rounded-md text-white flex items-center justify-center">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </div>
        <div>
          <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', fontWeight: 'bold', lineHeight: '1' }}>
            Plano da Última Consulta
          </h3>
          <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '1px', lineHeight: '1.2' }}>
            Plano de estudo e seguimento por especialidade
          </p>
        </div>
      </div>

      {/* Conteúdo do Plano */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {itensPlano.length > 0 ? (
          itensPlano.map((item, index) => (
            <div 
              key={index} 
              className="flex items-start gap-4 p-5 border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors"
            >
              {/* Contador */}
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-50 text-emerald-700 font-bold flex items-center justify-center text-sm border border-emerald-100">
                {index + 1}
              </div>
              
              {/* Informação do Plano */}
              <div className="flex flex-col w-full">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-slate-800 text-sm">
                    <Highlight text={item.especialidade || "Especialidade"} term={searchTerm} />
                  </span>
                  <span className="text-[10px] bg-slate-100 px-2 py-0.5 rounded text-slate-500 uppercase tracking-wider">
                    {item.data || "Sem data"}
                  </span>
                </div>
                <p className="text-slate-700 m-0 text-base leading-relaxed">
                  <Highlight text={item.conteudo} term={searchTerm} />
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="p-5 text-slate-400 italic text-sm text-center">
            Nenhum plano terapêutico estruturado disponível.
          </div>
        )}
      </div>
    </div>
  );
}