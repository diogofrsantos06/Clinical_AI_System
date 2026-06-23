import React, { useState } from 'react';

export default function AntecedentesSection({ antecedentes = [] }) {
  const [filtro, setFiltro] = useState('cronico');

  // 1. Separar os dados dinamicamente com base na temporalidade
  const cronicos = antecedentes.filter(item => 
    item.temporalidade && item.temporalidade.toLowerCase().includes('crónic') || item.temporalidade?.toLowerCase().includes('cronic')
  );
  
  const agudos = antecedentes.filter(item => 
    item.temporalidade && item.temporalidade.toLowerCase().includes('agud')
  );

  // 2. Determinar qual a lista a exibir na tabela
  const dadosExibidos = filtro === 'cronico' ? cronicos : agudos;

  return (
    <div className="w-full mb-8">
      {/* Header com Titulo e Filtro (Copiado da lógica de Exames) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        
        {/* Lado Esquerdo: Título */}
        <div className="flex items-center gap-3">
          <div className="bg-[#2d6a4f] p-1 rounded-md text-white">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z" />
            </svg>
          </div>
          <div>
            <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '24px', letterSpacing: '-0.01em', fontWeight: 'bold', lineHeight: '1' }}>
              Antecedentes Pessoais e Diagnósticos
            </h3>
            <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '3px', margin: 0 }}>
              {dadosExibidos.length} registos exibidos
            </p>
          </div>
        </div>

        {/* Lado Direito: Botões de Alternância (Toggle) */}
        <div className="flex bg-gray-100 p-1 rounded-lg self-start md:self-auto">
          <button
            onClick={() => setFiltro('cronico')}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
              filtro === 'cronico' 
                ? 'bg-white text-[#2d6a4f] shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Crónicos
          </button>
          <button
            onClick={() => setFiltro('agudo')}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
              filtro === 'agudo' 
                ? 'bg-white text-[#2d6a4f] shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Agudos
          </button>
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
          {dadosExibidos.length > 0 ? (
            dadosExibidos.map((item, i) => (
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
                  <div className="font-medium text-slate-800">{item.diagnostico}</div>
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
            ))
          ) : (
            <div className="text-center py-8 text-gray-400 text-sm">
              Nenhum diagnóstico {filtro === 'cronico' ? 'crónico' : 'agudo'} encontrado.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}