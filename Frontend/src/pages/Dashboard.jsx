import React, { useState } from 'react';
import { Upload } from 'lucide-react';
import { useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import TriagemSection from '../components/sections/TriagemSection';
import AntecedentesSection from '../components/sections/AntecedentesSection';
import MedicacaoSection from '../components/sections/MedicacaoSection';
import AlergiasSection from '../components/sections/AlergiasSection';
import ExamesSection from '../components/sections/ExamesSection';
import PlanoSection from '../components/sections/PlanoSection';
import UploadSection from '../components/sections/UploadSection';
import DiarioSection from '../components/sections/DiarioSection';
import api from '../api';

export default function Dashboard({ patient, onNewSearch }) {
  const [summary, setSummary] = useState(patient?.summary?.dados_estruturados || patient?.summary || {});
  const [diaries, setDiaries] = useState(patient?.diaries || []);
  const [summaryInvalidated, setSummaryInvalidated] = useState(patient?.new_diaries_added || false);
  const [activeSection, setActiveSection] = useState('triagem');
  const [showUploadModal, setShowUploadModal] = useState(null); 
  const sectionStyle = { scrollMarginTop: '100px' };

  
  const patientId = patient.numero_processo || patient.id;

  const refreshData = async () => {
    try {
      const response = await api.get(`/api/patients/${patientId}/`);
      setSummary(response.data?.summary?.dados_estruturados || response.data?.summary || {});
      setDiaries(response.data?.diaries || []);
      setSummaryInvalidated(response.data?.new_diaries_added || false);
    } catch (err) {
      console.error("Erro ao atualizar dados:", err);
    }
  };

  async function handleSaveTriagem(text) {
    try { await api.post(`/api/patients/${patientId}/triagem/`, { texto: text }); } catch (err) { console.error(err); }
  }

  async function handleRequestNewSummary() {
    try {
      await api.post(`/api/patients/${patientId}/generate_summary/`); 
      setSummaryInvalidated(false);
      refreshData();
    } catch (err) { alert("Erro ao gerar sumário."); }
  }

  useEffect(() => {
    const handleScroll = () => {
      // Lista de todos os IDs das tuas secções
      const sections = ['triagem', 'antecedentes', 'medicacao', 'alergias', 'exames', 'plano', 'upload', 'diarios'];
      
      for (const id of sections) {
        const element = document.getElementById(id);
        if (element) {
          const rect = element.getBoundingClientRect();
          // Se o elemento estiver perto do topo (margem de 150px para ativar)
          if (rect.top >= 0 && rect.top <= 200) {
            setActiveSection(id);
            break; // Para no primeiro que encontrar
          }
        }
      }
    };

    // Seleciona o elemento que tem o scroll (geralmente a <main> ou window)
    const mainElement = document.querySelector('main');
    mainElement.addEventListener('scroll', handleScroll);
    
    return () => mainElement.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar
        activeSection={activeSection}
        onNavigate={setActiveSection}
        hasAllergies={(summary?.alergias?.length || 0) > 0}
        patient={patient}
        onNewSearch={onNewSearch}
      />

      <main className="flex-1 overflow-y-auto h-screen">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between sticky top-0 z-10">
          <div>
            <h2 className="text-lg font-bold text-slate-800 m-0">{patient.nome}</h2>
            <p className="text-sm text-slate-500 m-0">Processo #{patientId}</p>
          </div>
          {summaryInvalidated && (
            <span className="text-xs text-amber-700 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-300">
              ⚠ Sumário desatualizado
            </span>
          )}
        </div>

        <div className="p-6 md:p-8 flex flex-col gap-5 max-w-5xl mx-auto w-full">
          <div id="triagem" style={sectionStyle}><TriagemSection processNumber={patientId} onSave={handleSaveTriagem} /></div>
          <div id="antecedentes" style={sectionStyle}><AntecedentesSection antecedentes={summary?.antecedentes || []} /></div>
          <div id="medicacao" style={sectionStyle}><MedicacaoSection medicacao={summary?.medicacao || []} /></div>
          <div id="alergias" style={sectionStyle}><AlergiasSection alergias={summary?.alergias || []} /></div>
          <div id="exames" style={sectionStyle}><ExamesSection exames={summary?.exames || []} /></div>
          <div id="plano" style={sectionStyle}><PlanoSection plano={summary?.plano_ultima_consulta || summary?.plano || ""} /></div>
          
          <div id="upload" style={sectionStyle}>
            <UploadSection patientId={patientId} onUploadSuccess={refreshData} />
          </div>

          <div id="diarios" style={sectionStyle}>
            <DiarioSection diarios={diaries || []} />
          </div>
        </div>
      </main>

      {/* Modal de Upload (só aparece quando showUploadModal tem valor) */}
      {showUploadModal && (
        <UploadSection 
          patientId={showUploadModal} 
          onUploadSuccess={() => {
            refreshData();
            setShowUploadModal(null);
          }} 
          onClose={() => setShowUploadModal(null)}
        />
      )}
    </div>
  );
}