import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Search, PlusSquare, MinusSquare, X, Upload, Send, 
  FileText, Loader2, Database, Eye 
} from 'lucide-react';
import ulsLogo from '../assets/ULS_logo.png';

const Dashboard = () => {
  // --- ESTADOS PRINCIPAIS ---
  const [patients, setPatients] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [showUploadModal, setShowUploadModal] = useState(null);
  
  // --- ESTADOS DE UI (RESUMO E DIÁRIOS) ---
  const [selectedSummary, setSelectedSummary] = useState({ id: null, text: "", loading: false });
  const [openDiariesList, setOpenDiariesList] = useState(null);
  
  // --- ESTADO DO MODAL DE VISUALIZAÇÃO DE DIÁRIO ---
  const [viewingDiary, setViewingDiary] = useState(null); 
  const [viewMode, setViewMode] = useState('text'); // 'text' ou 'data'
  
  const fileInputRef = useRef(null);

  // --- FUNÇÕES DE API ---
  const fetchPatients = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/patients/');
      setPatients(response.data);
    } catch (error) { console.error("Erro ao carregar pacientes:", error); }
  };

  useEffect(() => { fetchPatients(); }, []);

  const handleSeeSummary = async (patientId) => {
    if (selectedSummary.id === patientId) {
      setSelectedSummary({ id: null, text: "", loading: false });
      return;
    }
    setSelectedSummary({ id: patientId, text: "A gerar resumo clínico com IA...", loading: true });
    try {
      // URL ajustada para a tua rota: api/summaries/patient-summary/generate/
      const response = await axios.post('http://127.0.0.1:8000/api/summaries/patient-summary/generate/', {
        patient_id: patientId
      });
      setSelectedSummary({ id: patientId, text: response.data.summary_text, loading: false });
    } catch (error) {
      setSelectedSummary({ id: patientId, text: "Erro ao gerar resumo. Verifique os diários.", loading: false });
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !showUploadModal) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_id', showUploadModal);

    try {
      await axios.post('http://127.0.0.1:8000/api/diaries/upload_diary/', formData);
      alert("PDF processado e segmentado com sucesso!");
      setShowUploadModal(null);
      fetchPatients();
    } catch (error) { alert("Erro no processamento do ficheiro."); }
  };

  // --- FILTRO DE PESQUISA ---
  const filteredPatients = patients.filter(p => 
    p.id.toString().includes(searchTerm)
  );

  return (
    <div className="min-h-screen bg-[#F2F2F2] p-4 font-sans text-gray-800">
      {/* HEADER */}
      <header className="flex justify-between items-center mb-8 px-6">
        <img src={ulsLogo} alt="ULS" className="h-14" />
        <div className="relative">
          <input 
            type="text" 
            className="pl-3 pr-10 py-2 border border-gray-400 rounded-md w-80 shadow-sm focus:ring-1 focus:ring-black outline-none" 
            placeholder="Pesquisar ID Paciente..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        </div>
      </header>

      {/* CONTEÚDO PRINCIPAL */}
      <div className="w-full px-6">
        <div className="flex justify-between items-end mb-2">
          <h2 className="text-xl font-bold uppercase tracking-tight">Informação Pacientes</h2>
        </div>
        <div className="w-full h-[2px] bg-gray-400 mb-8"></div>

        <div className="bg-white border border-gray-400 shadow-lg overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-400">
                <th className="p-4 border-r border-gray-400 text-center w-[15%] font-bold uppercase text-xs">ID Paciente</th>
                <th className="p-4 border-r border-gray-400 text-center font-bold uppercase text-xs">Resumo Clínico</th>
                <th className="p-4 text-center w-[25%] font-bold uppercase text-xs">Diários Clínicos</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.map(patient => (
                <tr key={patient.id} className="border-b border-gray-300 hover:bg-gray-50 transition-colors">
                  <td className="p-4 text-center border-r border-gray-400 font-bold text-lg">{patient.id}</td>
                  
                  {/* COLUNA RESUMO */}
                  <td className="p-4 border-r border-gray-400 align-top">
                    {selectedSummary.id === patient.id ? (
                      <div className="p-4 border border-gray-200 rounded bg-gray-50 relative animate-in fade-in duration-300">
                        <div className="flex justify-between items-center mb-2 border-b pb-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Resumo Clínico</span>
                          <div className="flex items-center gap-2">
                            {selectedSummary.loading && <Loader2 size={12} className="animate-spin" />}
                            <button onClick={() => setSelectedSummary({id:null, text:""})} className="text-[10px] text-red-600 font-bold hover:underline">FECHAR</button>
                          </div>
                        </div>
                        <p className="text-sm italic text-gray-700 whitespace-pre-wrap leading-relaxed">
                          {selectedSummary.text}
                        </p>
                      </div>
                    ) : (
                      <button 
                        onClick={() => handleSeeSummary(patient.id)} 
                        className="w-full py-2 text-blue-600 font-medium hover:underline decoration-2 underline-offset-4"
                      >
                        Ver Resumo Clínico
                      </button>
                    )}
                  </td>

                  {/* COLUNA DIÁRIOS */}
                  <td className="p-4 align-top">
                    <div className="flex flex-col gap-3 items-start ml-4">
                      <button onClick={() => setShowUploadModal(patient.id)} className="flex items-center gap-2 text-xs font-bold text-gray-600 hover:text-black transition-colors">
                        <PlusSquare size={16} /> ADICIONAR DIÁRIO
                      </button>
                      
                      <button 
                        onClick={() => setOpenDiariesList(openDiariesList === patient.id ? null : patient.id)}
                        className="flex items-center gap-2 text-xs font-bold text-gray-600 hover:text-black transition-colors"
                      >
                        {openDiariesList === patient.id ? <MinusSquare size={16}/> : <PlusSquare size={16}/>}
                        VER DIÁRIOS ({patient.diaries?.length || 0})
                      </button>

                      {openDiariesList === patient.id && (
                        <div className="ml-6 mt-1 flex flex-col gap-2 border-l-2 border-gray-200 pl-4 py-1">
                          {patient.diaries?.length > 0 ? (
                            patient.diaries.map(d => (
                              <button 
                                key={d.id} 
                                onClick={() => { setViewingDiary(d); setViewMode('text'); }}
                                className="text-[11px] text-blue-500 hover:text-blue-800 hover:underline flex items-center gap-2 font-medium"
                              >
                                <FileText size={12} /> Diário nº {d.diary_number}
                              </button>
                            ))
                          ) : (
                            <span className="text-[10px] text-gray-400 italic">Nenhum diário processado.</span>
                          )}
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* --- MODAL DE VISUALIZAÇÃO DE DIÁRIO (APENAS TEXTO) --- */}
      {viewingDiary && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-6">
          <div className="bg-white w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl border-2 border-black">
            
            {/* Cabeçalho Modal */}
            <div className="p-4 border-b-2 border-black bg-gray-100 flex justify-between items-center">
              <div>
                <h3 className="font-black uppercase text-sm tracking-tight">Diário Original</h3>
                <p className="text-[10px] font-mono text-gray-500">
                  PACIENTE: {viewingDiary.patient} | DIÁRIO Nº {viewingDiary.diary_number}
                </p>
              </div>
              <button 
                onClick={() => setViewingDiary(null)} 
                className="hover:bg-black hover:text-white p-1 transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            {/* Conteúdo do Texto Original */}
            <div className="p-8 overflow-y-auto flex-1 bg-[#FCFCFA]">
              <div className="max-w-prose mx-auto">
                {/* whitespace-pre-wrap é essencial para manter as quebras de linha do .txt */}
                <p className="text-gray-800 leading-relaxed font-serif text-base whitespace-pre-wrap">
                  {viewingDiary.original_text || "O conteúdo deste diário não está disponível."}
                </p>
              </div>
            </div>

            {/* Footer Modal */}
            <div className="p-4 border-t border-gray-300 bg-gray-50 flex justify-end">
              <button 
                onClick={() => setViewingDiary(null)}
                className="px-6 py-2 bg-white border-2 border-black text-xs font-black uppercase hover:bg-black hover:text-white transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-1 active:translate-y-1"
              >
                Fechar Diário
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE UPLOAD (Existente) */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white p-10 border-2 border-black w-[450px] relative shadow-[10px_10px_0px_0px_rgba(0,0,0,0.2)]">
             <h3 className="text-center font-black mb-6 uppercase tracking-tighter text-xl">Upload Diário Médico</h3>
             <p className="text-[10px] text-center mb-4 font-bold text-gray-400 uppercase">Paciente ID: {showUploadModal}</p>
             <div 
                onClick={() => fileInputRef.current.click()}
                className="border-2 border-dashed border-gray-300 p-10 flex flex-col items-center cursor-pointer hover:border-black hover:bg-gray-50 transition-all group"
             >
                <Upload size={40} className="text-gray-300 group-hover:text-black mb-4 transition-colors" />
                <span className="text-[10px] font-black tracking-widest text-gray-400 group-hover:text-black">SELECIONAR FICHEIRO PDF</span>
             </div>
             <input type="file" ref={fileInputRef} className="hidden" accept=".pdf" onChange={handleFileUpload} />
             <button onClick={() => setShowUploadModal(null)} className="absolute top-4 right-4 hover:rotate-90 transition-transform"><X /></button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;