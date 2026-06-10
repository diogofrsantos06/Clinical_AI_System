import React, { useState, useEffect } from 'react';
import { Search, Stethoscope, User, ChevronRight, ChevronDown } from 'lucide-react';
import { useNavigate} from 'react-router-dom';

export default function PatientSearch({ onSearch, loading, recentPatients = [], onMount }) {
  const [input, setInput] = useState('');
  const navigate = useNavigate();


  useEffect(() => {
    if (onMount) onMount();
  }, [onMount]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      onSearch(input);
    }
  };

  const handleSearch = async (processNumber) => {
    const success = await onSearch(processNumber); 
    
    if (success) {
      navigate(`/paciente/${processNumber}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Cabeçalho da App */}
      <header className="bg-white border-none shadow-sm px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-[#216348] p-2 rounded-lg text-white">
            <Stethoscope size={20} />
          </div>
          <div>
            <h1 className="font-bold text-gray-900 m-0 leading-tight">Resumo Clínico</h1>
            <p className="text-xs text-gray-500">Dashboard de apoio à decisão</p>
          </div>
        </div>

        {/* Área do Médico com seletor */}
        <button 
          onClick={() => console.log("Abrir menu de troca de conta")} 
          className="flex items-center gap-3 text-sm text-gray-600 font-medium hover:bg-gray-50 px-3 py-2 rounded-lg transition-all"
        >
          <div className="flex flex-col items-end">
            <span className="text-[10px] uppercase text-gray-400 tracking-wider font-bold">Bem-vindo</span>
            <span className="text-gray-900 font-bold">Dr. Paulo Ferreira</span>
          </div>
          
          <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-[#216348] relative">
            <User size={16} />
            <div className="absolute -bottom-1 -right-1 bg-white rounded-full border border-gray-200 p-[1px]">
              <ChevronDown size={10} className="text-gray-500" />
            </div>
          </div>
        </button>
      </header>

      {/* Conteúdo Principal */}
      <main className="max-w-5xl mx-auto px-8 py-16">
      {/* Saudação */}
      <div className="mb-12">
        <span className="text-[#2d6a4f] font-bold text-sm bg-emerald-50 px-3 py-1 rounded-full">INÍCIO</span>
        <h2 className="text-5xl font-bold text-[#1a3c30] mt-4 mb-2" style={{ fontFamily: 'Alice, serif' }}>
          Bem-Vindo, Dr. Paulo.
        </h2>
        <p className="text-gray-500 text-lg">Escolha um paciente pelo número de processo para abrir o respetivo resumo clínico.</p>
      </div>

      {/* Barra de Pesquisa */}
      <div className="flex flex-col gap-2 mb-16">
        <label className="text-sm font-semibold text-gray-700">Número de processo</label>
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-4 text-gray-400" size={20} />
            <input 
              className="w-full pl-12 pr-4 py-4 rounded-xl border border-gray-200 shadow-sm outline-none focus:border-[#216348] transition-all"
              placeholder="ex. 202617"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </div>
          <button 
            onClick={() => onSearch(input)}
            disabled={loading}
            className="bg-[#216348] text-white px-8 py-4 rounded-xl font-bold hover:bg-[#1a4f3a] transition-all flex items-center gap-2"
          >
            {loading ? "A abrir..." : "Abrir paciente →"}
          </button>
        </div>
        <p className="text-sm text-gray-500">
          Dica: experimente <button onClick={() => onSearch("20261708")} className="text-[#216348] underline font-medium">202617</button>
        </p>
      </div>
    </main>
    </div>
  );
} 