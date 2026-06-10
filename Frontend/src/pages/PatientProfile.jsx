import { useNavigate, useParams} from 'react-router-dom';
import React, { useState, useEffect } from 'react';

import { ArrowLeft, User, FileText, Phone } from 'lucide-react';

import api from '../api';
import axios from 'axios';

export default function PatientProfile({ patient: propPatient }) {
  const { numero_processo } = useParams();
  const navigate = useNavigate();

  const [patient, setPatient] = useState(propPatient);
  const [loading, setLoading] = useState(!propPatient);

  useEffect(() => {
    if (!patient && numero_processo) {
      const fetchPatientData = async () => {
        try {
          const response = await api.get(`/api/patients/${numero_processo}/`);
          setPatient(response.data);
        } catch (err) {
          console.error("Erro ao carregar paciente no Perfil:", err);
        } finally {
          setLoading(false);
        }
      };
      
      fetchPatientData();
    } else {
      setLoading(false);
    }
  }, [numero_processo, patient]);

  const formatDate = (dateString) => {
    if (!dateString) return "--";
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
  };

  if (loading) {
    return <div className="p-10 text-center">A carregar dados do paciente...</div>;
  }

  if (!patient) {
    return <div className="p-10 text-center">Paciente não encontrado.</div>;
  }
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar Lateral Verde */}
    <aside className="w-64 bg-[#216348] text-white p-6 flex flex-col h-screen sticky top-0">
    
    <button 
      onClick={() => navigate(`/paciente/${numero_processo}`)}
      className="flex items-center gap-2 px-4 py-2 rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 transition-all text-white text-sm font-medium w-fit"
    >
      <ArrowLeft size={16} /> 
      <span>Voltar ao resumo</span>
    </button>

    {/* Informação do Paciente - Empurrado para baixo */}
    <div className="flex flex-col mt-10">
        <p className="text-[10px] uppercase tracking-widest text-[#81a396] font-bold mb-2">Paciente</p>
        <h2 className="font-bold text-lg leading-tight mb-1">{patient.nome}</h2>
        <p className="text-sm text-[#e2e8f0]">Nº {patient.numero_processo}</p>
    </div>
    </aside>

      {/* Conteúdo Principal */}
      <main className="flex-1 p-8">
        <header className="mb-8">
          <span className="text-[10px] uppercase tracking-widest text-emerald-700 font-bold bg-emerald-50 px-2 py-1 rounded">Perfil do Paciente</span>
        <h1 
            style={{ 
              fontFamily: 'Alice, serif', 
              fontSize: '36px', 
              fontWeight: 'bold', 
              lineHeight: '1', 
              color: '#0f172a',
              marginTop: '12px',
              marginBottom: '4px'
            }}
          >
            {patient.nome}
          </h1>          
          <p className="text-gray-500 text-sm mt-1">Nº {patient.numero_processo} · 21 anos · Sexo: {patient.sexo} · Nasc. {formatDate(patient.data_nascimento)}</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Card Dados Pessoais */}
          <section className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm w-full max-w-xl">
            {/* Título com linha inferior */}
            <h3 className="flex items-center gap-2 font-bold mb-4 pb-4 border-b border-gray-100 font-serif">
              <span className="text-emerald-700"><User size={18} /></span> 
              Dados Pessoais
            </h3>

            <div className="space-y-4 text-sm">
              {[
                { label: 'NOME COMPLETO', value: patient.nome },
                { label: 'DATA DE NASCIMENTO', value: formatDate(patient.data_nascimento) },
                { label: 'SEXO', value: patient.sexo },
                { label: 'NACIONALIDADE', value: patient.nacionalidade },
                { label: 'TELEFONE', value: patient.telefone },
                { label: 'EMAIL', value: patient.email },
                { label: 'MORADA', value: patient.morada }
              ].map(item => (
                <div key={item.label} className="grid grid-cols-[140px_1fr] border-b border-dashed border-gray-200 pb-3">
                  <span className="text-gray-400 font-medium text-[11px] uppercase tracking-wide">{item.label}</span>
                  <span className="text-gray-900 font-medium">{item.value}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Card Dados Administrativos */}
          <section className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm w-full max-w-xl">
            <h3 className="flex items-center gap-2 font-bold mb-4 pb-4 border-b border-gray-100 font-serif">
              <span className="text-emerald-700"><User size={18} /></span> 
              Dados Administrativos
            </h3>
            <div className="space-y-4 text-sm">
              {[
                { label: 'Nº DE PROCESSO', value: patient.numero_processo },
                { label: 'Nº SNS', value: patient.n_sns },
                { label: 'NIF', value: patient.nif },
                { label: 'SUBSISTEMA', value: patient.subsistema },
                { label: 'DATA DE ADMISSÃO', value: formatDate(patient.data_admissao) },
                { label: 'SERVIÇO / CAMA', value: patient.servico },
                { label: 'MÉDICO ASSISTENTE', value: patient.medico }
              ].map(item => (
                <div key={item.label} className="grid grid-cols-[140px_1fr] border-b border-dashed border-gray-200 pb-3">
                  <span className="text-gray-400 font-medium text-[11px] uppercase">{item.label}</span>
                  <span className="text-gray-900 font-medium">{item.value}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Card Contacto Emergência */}
          <section className="md:col-span-2 bg-white p-6 rounded-2xl border border-gray-100 shadow-sm w-full">
            <h3 className="flex items-center gap-2 font-bold mb-4 pb-4 border-b border-gray-100 font-serif">
              <span className="text-emerald-700"><Phone size={18} /></span> 
              Contacto de emergência
            </h3>
            <p className="font-bold text-gray-900 text-base">
              {patient.contacto_urg_nome} — {patient.contacto_urg_telefone}
            </p>
            <p className="text-xs text-gray-400 mt-1">Pessoa a contactar em situação de urgência.</p>
          </section>
        </div>
      </main>
    </div>
  );
}