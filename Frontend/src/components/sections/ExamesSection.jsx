import React, { useState } from 'react';
import { FlaskConical, ChevronLeft, ChevronRight } from 'lucide-react';
import Highlight from '../Highlight';

export default function ExamesSection({ exames = [], examesTriagem = [], searchTerm = ''  }) {
  const [filtro, setFiltro] = useState('todos');
  const [paginaAtual, setPaginaAtual] = useState(1);
  const itensPorPagina = 4; 

  const examesAtuais = filtro === 'todos' ? exames : examesTriagem;

  // Agrupamento por diário
  const agrupados = examesAtuais.reduce((acc, examen) => {
    if (!acc[examen.nome]) {
      acc[examen.nome] = { nome: examen.nome, data: examen.data || '', items: [] };
    }
    acc[examen.nome].items.push({ tipo: examen.tipo_exame, resultado: examen.resultado });
    return acc;
  }, {});

  // Conversor de datas para ordenação precisa
  const converterParaData = (textoData) => {
    if (!textoData) return new Date(0);
    const mesesPt = { jan: 0, fev: 1, mar: 2, abr: 3, mai: 4, jun: 5, jul: 6, ago: 7, set: 8, out: 9, nov: 10, dez: 11 };
    const partes = textoData.toLowerCase().replace(/_/g, '-').split(/[-/]/);
    if (partes.length === 3) {
      const dia = parseInt(partes[0], 10);
      const ano = parseInt(partes[2], 10);
      const mesTexto = partes[1];
      const mes = mesesPt[mesTexto] !== undefined ? mesesPt[mesTexto] : parseInt(mesTexto, 10) - 1;
      return new Date(ano, mes, dia);
    }
    return isNaN(Date.parse(textoData)) ? new Date(0) : new Date(Date.parse(textoData));
  };

  const sortedExames = Object.values(agrupados).sort((a, b) => converterParaData(b.data) - converterParaData(a.data));

  // Lógica de paginação
  const totalItens = sortedExames.length;
  const totalPaginas = Math.ceil(totalItens / itensPorPagina);
  const examesExibidos = filtro === 'todos' ? sortedExames.slice((paginaAtual - 1) * itensPorPagina, paginaAtual * itensPorPagina) : sortedExames;

  const alterarFiltro = (novoFiltro) => {
    setFiltro(novoFiltro);
    setPaginaAtual(1);
  };

  // Geração da numeração inteligente das páginas
  const gerarNumeracaoPaginas = () => {
    const paginas = [];
    if (totalPaginas <= 4) {
      for (let i = 1; i <= totalPaginas; i++) paginas.push(i);
    } else {
      if (paginaAtual <= 2) {
        paginas.push(1, 2, '...', totalPaginas);
      } else if (paginaAtual >= totalPaginas - 1) {
        paginas.push(1, '...', totalPaginas - 1, totalPaginas);
      } else {
        paginas.push(1, '...', paginaAtual, '...', totalPaginas);
      }
    }
    return paginas;
  };

  return (
    <div className="w-full mb-8">
      {/* Header com os botões originais no canto superior direito */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 w-full">
        <div className="flex items-center gap-3">
          <div className="bg-[#216348] p-1 rounded-lg text-white">
            <FlaskConical size={18} />
          </div>
          <div>
            <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', letterSpacing: '-0.01em', fontWeight: 'bold', lineHeight: '1' }}>
              Exames e Análises
            </h3>
            <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '1px', margin: 0 }}>
              Exames realizados no último ano
            </p>
          </div>
        </div>
        
        {/* Filtros mantidos no lado direito */}
        <div className="flex bg-gray-100 p-1 rounded-lg self-end md:self-auto">
          <button 
            onClick={() => alterarFiltro('todos')} 
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${filtro === 'todos' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Todos
          </button>
          <button 
            onClick={() => alterarFiltro('triagem')} 
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${filtro === 'triagem' ? 'bg-white text-[#216348] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Relacionados
          </button>
        </div>
      </div>

      {/* Lista de Cards - Ocupa agora a largura TOTAL da página */}
      <div className="space-y-4 w-full">
        {examesExibidos.length > 0 ? (
          examesExibidos.map((diario, i) => (
            <div key={i} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-start gap-4 w-full">
              <div className="bg-slate-100 p-2.5 rounded-lg text-slate-600 mt-0.5">
                <FlaskConical size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start mb-3">
                  <h4 className="font-bold text-gray-900 text-base truncate"><Highlight text={diario.nome} term={searchTerm} /></h4>
                  <span className="text-xs text-gray-400 font-medium whitespace-nowrap ml-2">{diario.data}</span>
                </div>
                <div className="space-y-2">
                  {diario.items.map((item, index) => {
                    // Evita mostrar o tipo se for redundante com o resultado (ex: Tipo: Bioquímica, Resultado: Bioquímica Normal)
                    const isRedundante = !item.tipo || !item.resultado || item.resultado.toLowerCase().includes(item.tipo.toLowerCase());
                    
                    return (
                      <div key={index} className="text-sm bg-gray-50 p-2 rounded border-l-4 border-[#216348]">
                        {!isRedundante && (
                          <span className="font-semibold text-gray-800"><Highlight text={item.tipo} term={searchTerm} />: </span>
                        )}
                        <span className="text-gray-600"><Highlight text={item.resultado} term={searchTerm} /></span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-10 border border-dashed border-gray-200 rounded-xl text-gray-400 text-sm w-full">
            {filtro === 'triagem' ? "Sem exames relacionados encontrados na triagem." : "Sem registos disponíveis."}
          </div>
        )}
      </div>

      {filtro === 'todos' && totalPaginas > 1 && (
        <div className="w-full flex justify-end mt-5">
          <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-lg text-xs shadow-sm">
            <button
              onClick={() => setPaginaAtual(prev => Math.max(prev - 1, 1))}
              disabled={paginaAtual === 1}
              className="p-1.5 text-gray-500 hover:bg-white hover:text-gray-900 rounded transition-all disabled:opacity-30 disabled:hover:bg-transparent"
            >
              <ChevronLeft size={14} />
            </button>
            
            <div className="flex items-center gap-1 px-1">
              {gerarNumeracaoPaginas().map((p, idx) => (
                <button
                  key={idx}
                  disabled={p === '...'}
                  onClick={() => setPaginaAtual(p)}
                  className={`px-2.5 py-1 text-xs font-semibold rounded transition-all ${
                    paginaAtual === p 
                      ? 'bg-white text-[#216348] shadow-sm' 
                      : p === '...' ? 'text-gray-400 cursor-default' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>

            <button
              onClick={() => setPaginaAtual(prev => Math.min(prev + 1, totalPaginas))}
              disabled={paginaAtual === totalPaginas}
              className="p-1.5 text-gray-500 hover:bg-white hover:text-gray-900 rounded transition-all disabled:opacity-30 disabled:hover:bg-transparent"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}