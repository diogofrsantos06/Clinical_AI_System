import React from 'react';
import { useNavigate } from 'react-router-dom'; // 1. Importa o useNavigate
import { Home, Search, User } from 'lucide-react';

export default function PatientHeader({ patient, onBack, searchTerm, onSearch }) {
  const navigate = useNavigate(); // 2. Inicializa o hook

  if (!patient) return null;

  const calculateAge = (dobString) => {
    if (!dobString) return "--";
    const birthDate = new Date(dobString);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) age--;
    return `${age} anos`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return "--";
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
  };

  const nomeExibido = patient.nome || "Sem Nome";
  
  return (
    <header className="w-full flex items-center justify-between px-8 py-4 bg-white border-b border-gray-200">
      
      {/* 1. Breadcrumbs */}
      <div className="flex items-center gap-2 text-sm text-gray-500 whitespace-nowrap">
        <button onClick={onBack} className="flex items-center gap-1 hover:text-emerald-700">
          <Home size={16} /> Pacientes
        </button>
        <span>›</span>
        <span className="font-semibold text-gray-900">Dashboard</span>
      </div>

      {/* 2. Cartão Central (Agora navega para o perfil) */}
      <div className="flex-1 flex justify-center px-6">
        <button 
          // 3. Alteração aqui: Navega para a rota de perfil
          onClick={() => navigate(`/paciente/${patient.numero_processo}/perfil`)}
          className="flex items-center gap-3 bg-white border border-gray-200 rounded-full px-8 py-2 shadow-sm hover:border-emerald-300 transition-all text-left"
        >
          <div className="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-700 shrink-0">
            <User size={18} /> 
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-gray-900 text-sm whitespace-nowrap">{nomeExibido}</span>
            <span className="text-[11px] text-gray-500 whitespace-nowrap">
              Nº {patient.numero_processo || "---"} · {calculateAge(patient.data_nascimento)} · {patient.sexo || "---"} · Nasc. {formatDate(patient.data_nascimento)}
            </span>
          </div>
        </button>
      </div>

      {/* 3. Pesquisa */}
      <div className="flex justify-end">
        <div className="relative w-48">
           <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
           <input 
              className="pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-full text-sm w-full"
              placeholder="Pesquisar..."
              value={searchTerm}
              onChange={(e) => onSearch(e.target.value)} // Atualiza o estado no Dashboard
            />
        </div>
      </div>
    </header>
  );
}