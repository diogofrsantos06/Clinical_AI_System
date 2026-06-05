import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import PatientHeader from '../components/PatientHeader';
import TriagemSection from '../components/sections/TriagemSection';
import AntecedentesSection from '../components/sections/AntecedentesSection';
import MedicacaoSection from '../components/sections/MedicacaoSection';
import AlergiasSection from '../components/sections/AlergiasSection';
import ExamesSection from '../components/sections/ExamesSection';
import PlanoSection from '../components/sections/PlanoSection';
import UploadSection from '../components/sections/UploadSection';
import DiarioSection from '../components/sections/DiarioSection';
import api from '../api';


// 1. O Loader (Componente auxiliar)
function DashboardLoader({ patient, fetchPatient }) {
  const { numero_processo } = useParams();

  useEffect(() => {
    // Só carrega se não tivermos o paciente ou se o ID for diferente do URL
    if (!patient || patient.numero_processo !== numero_processo) {
      fetchPatient(numero_processo);
    }
  }, [numero_processo, patient, fetchPatient]);

  if (!patient) return <div className="p-8">Carregando dados do paciente...</div>;

  return <DashboardContent patient={patient} />;
}

// 2. O conteúdo real do teu Dashboard (renomeia o teu Dashboard atual para isto)
function DashboardContent({ patient }) {
  return (
    <div>
      {/* Todo o teu JSX original do Dashboard */}
      <h1>{patient.nome}</h1>
    </div>
  );
}


export default function Dashboard({ patient, onNewSearch }) {
  const [summary, setSummary] = useState(patient?.summary?.dados_estruturados || patient?.summary || {});
  const [diaries, setDiaries] = useState(patient?.diaries || []);
  const [summaryInvalidated, setSummaryInvalidated] = useState(patient?.new_diaries_added || false);
  const [activeSection, setActiveSection] = useState('triagem');
  const [showUploadModal, setShowUploadModal] = useState(null); 
  
  const sectionStyle = { scrollMarginTop: '100px' };
  const patientId = patient?.id;

  const refreshData = async () => {
    if (!patientId) return;
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

  // Lógica de ScrollSpy
  useEffect(() => {
    const handleScroll = () => {
      const sections = ['triagem', 'antecedentes', 'medicacao', 'alergias', 'exames', 'plano', 'upload', 'diarios'];
      const mainElement = document.getElementById('main-scroll-area');
      
      if (!mainElement) return;

      // Percorre as secções de baixo para cima para encontrar a que está no topo
      for (const id of sections) {
        const element = document.getElementById(id);
        if (element) {
          const rect = element.getBoundingClientRect();
          
          if (rect.top >= 0 && rect.top <= 300) {
            setActiveSection(id);
            return; // Encontrou a secção visível, para a execução
          }
        }
      }
    };
    
    const mainElement = document.getElementById('main-scroll-area');
    mainElement?.addEventListener('scroll', handleScroll);

    return () => mainElement?.removeEventListener('scroll', handleScroll);
  }, []);

  
  const temAlergiasReais = patient?.alergias && 
                           patient.alergias.length > 0 && 
                           !["Sem alergias conhecidas", "N/A", "Nenhum"].includes(patient.alergias[0]);

  if (!patient) {
    return <div className="p-10 text-center">A carregar dados do paciente...</div>;
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      
      {/* Sidebar Fixa à esquerda */}
      <Sidebar
        activeSection={activeSection}
        onNavigate={(id) => {
          setActiveSection(id);
          document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        }}
        hasAllergies={temAlergiasReais} // Agora recebe o valor filtrado
        patient={patient}
        onNewSearch={onNewSearch}
      />

      {/* Main Container - Ocupa o resto à direita */}
      <main id="main-scroll-area" className="flex-1 h-screen overflow-y-auto flex flex-col">
        
        {/* Header fixo no topo da zona de conteúdo */}
        <div className="sticky top-0 z-20 bg-gray-50">
          <PatientHeader 
            patient={patient} 
            onBack={onNewSearch} 
            onSearch={(term) => console.log("Pesquisar:", term)} 
          />
        </div>
        

        {/* Conteúdo scrollável */}
        <div className="p-8 flex-1">
          <div className="max-w-5xl mx-auto w-full flex flex-col gap-8">
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
        </div>
      </main>


      {/* Modal Upload */}
      {showUploadModal && (
        <UploadSection 
          patientId={showUploadModal} 
          onUploadSuccess={() => { refreshData(); setShowUploadModal(null); }} 
          onClose={() => setShowUploadModal(null)}
        />
      )}
    </div>
  );
}