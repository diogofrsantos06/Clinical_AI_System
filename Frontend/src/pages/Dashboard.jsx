import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
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
import axios from 'axios';

function DashboardLoader({ patient, fetchPatient }) {
  
  const { numero_processo } = useParams();

  console.log("Estado atual:", { 
    url_param: numero_processo, 
    patient_exists: !!patient,
    patient_number: patient?.numero_processo 
  });

  useEffect(() => {
    console.log("URL param:", numero_processo);
    console.log("Paciente atual:", patient);
    
    if (!patient || String(patient.numero_processo) !== String(numero_processo)) {
      console.log("A disparar fetchPatient...");
      fetchPatient(numero_processo);
    }
  }, [numero_processo, patient, fetchPatient]);

  if (!patient) return <div className="p-8">A carregar os dados do paciente...</div>;

  return <Dashboard patient={patient} />;
}

function DashboardContent({ patient }) {
  return (
    <div>
      <h1>{patient.nome}</h1>
    </div>
  );
}


export default function Dashboard({ patient: propPatient, onNewSearch }) {

  const { numero_processo } = useParams();
  
  const [patient, setPatient] = useState(propPatient);
  const [loading, setLoading] = useState(!propPatient);
  const [summary, setSummary] = useState(patient?.summary?.dados_estruturados || patient?.summary || {});
  const [diaries, setDiaries] = useState(patient?.diaries || []);
  const [summaryInvalidated, setSummaryInvalidated] = useState(patient?.new_diaries_added || false);
  const [activeSection, setActiveSection] = useState('triagem');
  const [showUploadModal, setShowUploadModal] = useState(null);

  const [resultadoTriagem, setResultadoTriagem] = useState(null);
  
  const patientId = patient?.id;

  const sectionStyle = { scrollMarginTop: '100px' };

  const refreshData = async () => {
      const proc = patient?.numero_processo || numero_processo;
      if (!proc) return;

      try {
        const response = await api.get(`/api/patients/${proc}/`);
        console.log("DADOS RECEBIDOS DA API:", response.data);
        
        setSummary(response.data?.summary?.dados_estruturados || response.data?.summary || {});
        setDiaries(response.data?.diaries || []);
        setSummaryInvalidated(response.data?.new_diaries_added || false);
      } catch (err) {
        console.error("Erro ao atualizar dados:", err);
      }
  };

  async function handleSaveTriagem(text) {
    try {
      const response = await axios.post('/api/summaries/patient-summary/analyze_triage/', {
        patient_id: patientId, 
        triage_text: text
      });
      
      setResultadoTriagem(response.data);
      
      console.log("Chegou ao frontend!", response.data);

    } catch (err) {
      console.error("Erro ao enviar triagem:", err);
    }
  }

  useEffect(() => {
    if (!patient && numero_processo) {
      const fetchPatientData = async () => {
        try {
          const response = await api.get(`/api/patients/${numero_processo}/`);
          setPatient(response.data);
        } catch (err) {
          console.error("Erro ao buscar paciente:", err);
        } finally {
          setLoading(false);
        }
      };
      fetchPatientData();
    }
  }, [numero_processo, patient]);


  useEffect(() => {

    const handleScroll = () => {
      const sections = ['triagem', 'antecedentes', 'medicacao', 'alergias', 'exames', 'plano', 'upload', 'diarios'];
      const mainElement = document.getElementById('main-scroll-area');
      if (!mainElement) return;

      for (const id of sections) {
        const element = document.getElementById(id);
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top >= 0 && rect.top <= 300) {
            setActiveSection(id);
            return;
          }
        }
      }
    };

    const mainElement = document.getElementById('main-scroll-area');
    mainElement?.addEventListener('scroll', handleScroll);

    return () => mainElement?.removeEventListener('scroll', handleScroll);
  }, [loading]);

  const temAlergiasReais = patient?.alergias && patient.alergias.length > 0 && !["Sem alergias conhecidas", "N/A", "Nenhum"].includes(patient.alergias[0]);

  useEffect(() => {
    if (patient) {
      setSummary(patient?.summary?.dados_estruturados || patient?.summary || {});
      setDiaries(patient?.diaries || []);
      setSummaryInvalidated(patient?.new_diaries_added || false);
    }
  }, [patient]);

  if (loading) {
    return <div className="p-10 text-center">A carregar dados do paciente...</div>;
  }

  if (!patient) {
    return <div className="p-10 text-center">Paciente não encontrado.</div>;
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
            <div id="exames" style={sectionStyle}><ExamesSection exames={summary?.exames || []} examesTriagem={resultadoTriagem?.dados_estruturados?.exames || []} /></div>
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