import React from 'react';
import Highlight from '../Highlight';

export default function AntecedentesSection({ antecedentes = [], searchTerm = '' }) {
  // Como a LLM agora só devolve crónicos/ativos, usamos a lista diretamente
  const diagnosticos = antecedentes || [];
  
  // Verifica se alguma das datas contém o asterisco para acionar a legenda no fundo
  const temAsterisco = diagnosticos.some(item => item.desde && item.desde.includes('*'));

  return (
    <div className="w-full mb-8">
      {/* Header com Titulo */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        
        {/* Lado Esquerdo: Título */}
        <div className="flex items-center gap-3">
          <div className="bg-[#2d6a4f] p-1 rounded-md text-white">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z" />
            </svg>
          </div>
          <div>
            <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', letterSpacing: '-0.01em', fontWeight: 'bold', lineHeight: '1' }}>
              Antecedentes Pessoais e Diagnósticos
            </h3>
            <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '1px', margin: 0 }}>
              {diagnosticos.length} registos exibidos
            </p>
          </div>
        </div>
      </div>

      {/* Tabela Estruturada Mais Compacta */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Largura de colunas ligeiramente mais compacta no grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr 0.8fr', gap: '16px', padding: '10px 18px', borderBottom: '1px solid var(--ink-50)', fontSize: '11px', color: 'var(--ink-500)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          <div>Diagnóstico</div>
          <div>Evolução</div>
          <div className="text-right">Desde</div>
        </div>

        <div className="text-slate-800">
          {diagnosticos.length > 0 ? (
            diagnosticos.map((item, i) => (
              <div 
                key={i} 
                style={{ 
                  display: 'grid', 
                  gridTemplateColumns: '1.8fr 1fr 0.8fr', 
                  gap: '16px', 
                  padding: '8px 18px',  /* Reduzido de 14px para 8px para ficar mais fina */
                  borderBottom: '1px solid var(--ink-50)', 
                  fontSize: '13.5px', 
                  alignItems: 'center' 
                }}
                className="hover:bg-slate-50 transition-colors last:border-0"
              >
                <div>
                  <div className="font-medium text-slate-800"><Highlight text={item.diagnostico} term={searchTerm} /></div>
                  <div className="text-xs text-slate-500 font-normal mt-0.5">
                    <Highlight text={item.tipo || 'N/A'} term={searchTerm} />
                  </div>
                </div>

                <div className="text-slate-600">
                  <Highlight text={item.temporalidade || 'N/A'} term={searchTerm} />
                </div>

                <div className="text-right text-slate-600">
                  <Highlight text={item.desde || 'Sem informação'} term={searchTerm} />
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-400 text-sm">
              Nenhum diagnóstico crónico ou ativo encontrado.
            </div>
          )}
        </div>
        
        {/* LEGENDA DO ASTERISCO */}
        {temAsterisco && (
          <div className="p-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 italic">
            * Data referente ao registo clínico mais antigo documentado no sistema, não correspondendo obrigatoriamente à data do diagnóstico inicial.
          </div>
        )}
      </div>
    </div>
  );
}