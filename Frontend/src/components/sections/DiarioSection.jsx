import React, { useState } from 'react';
import { Clock, ChevronDown, ChevronUp } from 'lucide-react';
export default function DiarioSection({ diarios }) {
  const [expandedIds, setExpandedIds] = useState([]);
  const toggleExpand = (id) => {
    setExpandedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const parseTitleDate = (title) => {
    const months = { 'Jan': 0, 'Fev': 1, 'Mar': 2, 'Abr': 3, 'Mai': 4, 'Jun': 5, 
                     'Jul': 6, 'Ago': 7, 'Set': 8, 'Out': 9, 'Nov': 10, 'Dez': 11 };
    const match = title.match(/(\d{2})-(\w{3})-(\d{4})/);
    if (!match) return new Date(0);
    const [_, day, monthStr, year] = match;
    return new Date(year, months[monthStr] || 0, day);
  };

  const sortedDiaries = [...diarios]
    .map(d => ({ ...d, date: parseTitleDate(d.title) }))
    .sort((a, b) => b.date - a.date);

  const diariosComLabel = sortedDiaries.map((d) => {
    const tituloBase = d.title.split(' - ')[0];
    
    const grupoMesmoNome = sortedDiaries
      .filter(item => item.title.split(' - ')[0] === tituloBase)
      .sort((a, b) => a.date - b.date);
    
    const indexNoGrupo = grupoMesmoNome.findIndex(item => item === d);
    
    return { ...d, diaLabel: `D${indexNoGrupo + 1}` };
  });

  let currentYear = null;

  return (
    <div className="w-full">
      {/* Cabeçalho */}
      <div className="flex items-center gap-3 mb-2">
        <div className="bg-[#2d6a4f] p-1 rounded-md text-white"><Clock size={18}/></div>
        <div>
          <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', fontWeight: 'bold', lineHeight: '1' }}>
            Diários Clínicos
          </h3>
          <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '2px' }}>
            {diarios.length} registos · ordenados do mais recente para o mais antigo
          </p>
        </div>
      </div>

      <div className="space-y-2">
        {diariosComLabel.map((d, i) => {
          const year = d.date.getFullYear();
          const showYear = year !== currentYear;
          if (showYear) currentYear = year;

          const isExpanded = expandedIds.includes(i);
          const tituloLimpo = d.title.split(' - ')[0];
          console.log("Diário completo:", d);
          return (
            <React.Fragment key={i}>
              {showYear && <div className="font-bold text-[#2d6a4f] text-sm py-2">{year}</div>}
              
              <div className="grid grid-cols-[90px_30px_1fr] items-start gap-0">
                
                <div className="flex flex-col items-end pt-1 pr-0.5">
                  <span className="text-[21px] font-bold text-slate-900 leading-none">{d.date.getDate()}</span>
                  <span className="text-[10px] font-bold text-slate-400 tracking-wider mt-1 uppercase">
                    {d.date.toLocaleDateString('pt-PT', { month: 'short' })}
                  </span>
                </div>

                <div className="flex justify-center pt-2">
                  <div className="w-3 h-3 rounded-full bg-[#2d6a4f]"></div>
                </div>

                <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                  <div className="flex justify-between items-start">
                    <h4 className="font-bold text-slate-900 text-[15px] mb-1">
                      {tituloLimpo} ({d.diaLabel})
                    </h4>
                    <button onClick={() => toggleExpand(i)} className="text-slate-400 hover:text-[#2d6a4f]">
                      {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                    </button>
                  </div>
                  <p className={`text-slate-600 text-sm leading-relaxed whitespace-pre-wrap ${!isExpanded ? 'line-clamp-2' : ''}`}>
                    {d.original_text || "Sem resumo disponível."}
                  </p>
                </div>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}