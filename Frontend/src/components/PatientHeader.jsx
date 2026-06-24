import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Search, User, Bell, AlertTriangle } from 'lucide-react';

export default function PatientHeader({ patient, onBack, searchTerm, onSearch, notifications = [], onMarkAsRead }) {
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);

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
  
  // Agora usamos is_read que vem do teu serializer do Django
  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <header className="w-full flex items-center justify-between px-8 py-4 bg-white border-b border-gray-200">
      
      <div className="flex items-center gap-2 text-sm text-gray-500 whitespace-nowrap">
        <button onClick={onBack} className="flex items-center gap-1 hover:text-emerald-700">
          <Home size={16} /> Pacientes
        </button>
        <span>›</span>
        <span className="font-semibold text-gray-900">Dashboard</span>
      </div>

      <div className="flex-1 flex justify-center px-6">
        <button 
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

      <div className="flex items-center justify-end gap-4">
        
        <div className="relative w-48">
           <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
           <input 
              className="pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-full text-sm w-full"
              placeholder="Pesquisar..."
              value={searchTerm}
              onChange={(e) => onSearch(e.target.value)}
            />
        </div>

        {/* Ícone de Notificações */}
        <div className="relative">
          <button 
            onClick={() => {
              setShowNotifications(!showNotifications);
              // Quando o popover abre, avisa o backend que as mensagens foram lidas!
              if (!showNotifications && onMarkAsRead) {
                onMarkAsRead();
              }
            }}
            className={`p-2 rounded-full transition-colors relative ${
              unreadCount > 0 ? 'bg-amber-50 text-amber-500 hover:bg-amber-100' : 'bg-gray-50 text-gray-400 hover:bg-gray-100'
            }`}
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className="absolute top-0 right-0 -mt-1 -mr-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white shadow-sm">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Popover / Menu Dropdown de Notificações */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-100 z-50 overflow-hidden">
              <div className="bg-slate-50 px-4 py-3 border-b border-gray-100 flex justify-between items-center">
                <span className="font-bold text-slate-800 text-sm">Notificações do Sistema</span>
                <span className="text-xs text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full">{unreadCount} novas</span>
              </div>
              
              <div className="max-h-80 overflow-y-auto">
                {notifications.length > 0 ? (
                  notifications.map((notif, index) => (
                    <div key={index} className={`p-4 border-b border-gray-50 flex gap-3 ${notif.is_read ? 'bg-white opacity-60' : 'bg-amber-50/30'}`}>
                      <div className="text-amber-500 mt-0.5">
                        <AlertTriangle size={16} />
                      </div>
                      <div>
                        {/* Usamos message que vem do serializer */}
                        <p className="text-xs text-slate-700 leading-snug">{notif.message}</p>
                        <span className="text-[10px] text-slate-400 mt-1 block">{notif.data}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center text-sm text-gray-400">
                    Não existem notificações pendentes.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}