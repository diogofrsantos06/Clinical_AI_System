import React, { useState } from 'react';
import { FlaskConical } from 'lucide-react';

export default function ExamesSection({ exames }) {
  const [filtro, setFiltro] = useState('todos');

  // 1. Agrupar os exames por 'nome'
  const agrupados = exames.reduce((acc, exame) => {
    if (!acc[exame.nome]) {
      acc[exame.nome] = {
        nome: exame.nome,
        data: exame.data,
        items: []
      };
    }
    acc[exame.nome].items.push({
      tipo: exame.tipo_exame,
      resultado: exame.resultado
    });
    return acc;
  }, {});

  // 2. Converter o objeto de volta para array e ordenar pela data
  const sortedExames = Object.values(agrupados).sort((a, b) => new Date(b.data) - new Date(a.data));

  return (
    <div className="mb-8">
      {/* Header com Filtro */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-[#216348] p-2 rounded-lg text-white">
            <FlaskConical size={20} />
          </div>
          <h3 className="font-bold text-gray-900 text-lg">Exames e Análises</h3>
        </div>
      </div>

      {/* Lista de Cards Agrupados */}
      <div className="space-y-4">
        {sortedExames.length > 0 ? (
          sortedExames.map((diario, i) => (
            <div key={i} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-start gap-4">
              <div className="bg-slate-100 p-2.5 rounded-lg text-slate-600 mt-0.5">
                <FlaskConical size={18} />
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start mb-3">
                  <h4 className="font-bold text-gray-900">{diario.nome}</h4>
                  <span className="text-xs text-gray-400 font-medium">{diario.data}</span>
                </div>
                
                {/* Lista de exames internos do diário */}
                <div className="space-y-2">
                  {diario.items.map((item, index) => (
                    <div key={index} className="text-sm bg-gray-50 p-2 rounded border-l-4 border-[#216348]">
                      <span className="font-semibold text-gray-800">{item.tipo}: </span>
                      <span className="text-gray-600">{item.resultado}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-10 border-2 border-dashed border-gray-100 rounded-xl text-gray-400 text-sm">
            Sem registos disponíveis.
          </div>
        )}
      </div>
    </div>
  );
}