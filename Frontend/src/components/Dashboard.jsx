import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, PlusSquare, MinusSquare, X, Upload, Send, 
  FileText, Loader2, Database, Eye 
} from 'lucide-react';
import ulsLogo from '../assets/ULS_Logo.png';
import api from '../api';

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

  // Adiciona estas duas linhas abaixo:
  const [showAddPatientModal, setShowAddPatientModal] = useState(false);
  const [newPatientId, setNewPatientId] = useState("");

  const [feedback, setFeedback] = useState(null);

  const [isUploading, setIsUploading] = useState(false);

  // Efeito para limpar a mensagem após 4 segundos
  useEffect(() => {
    if (feedback) {
      const timer = setTimeout(() => setFeedback(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [feedback]);

  // --- FUNÇÕES DE API ---
  const fetchPatients = async () => {
    try {
      const response = await api.get('/api/patients/');
      setPatients(response.data);
    } catch (error) { console.error("Erro ao carregar pacientes:", error); }
  };

  useEffect(() => { fetchPatients(); }, []);

  const handleSeeSummary = async (patientId) => {
  if (selectedSummary.id === patientId) {
    setSelectedSummary({ id: null, text: "", loading: false });
    return;
  }

  const patient = patients.find(p => p.id === patientId);
  
  // Verifica se já existe um resumo e se não houve novos diários desde então
  // Nota: Assume que o teu backend envia 'last_summary' e 'last_diary_date' no objeto patient
  if (patient.last_summary && (!patient.new_diaries_added)) {
    setSelectedSummary({ id: patientId, text: patient.last_summary, loading: false });
    return;
  }

  setSelectedSummary({ id: patientId, text: "A gerar novo resumo clínico...", loading: true });
  
  try {
    const response = await api.post('/api/summaries/patient-summary/generate/', {
      patient_id: patientId
    });
    setSelectedSummary({ id: patientId, text: response.data.summary_text, loading: false });
    fetchPatients(); // Atualiza a lista para marcar que o resumo está em dia
  } catch (error) {
    setSelectedSummary({ id: patientId, text: "Erro ao comunicar com a IA.", loading: false });
  }
  };

  const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file || !showUploadModal) return;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_id', showUploadModal);

  // Ativa o estado de carregamento
  setIsUploading(true);

  try {
    // O await espera que a LLM no Django responda
    await api.post('/api/diaries/upload_diary/', formData);
    
    // Feedback de sucesso
    setFeedback({ type: 'success', message: "Processamento concluído com sucesso!" });
    
    // Fecha o modal e limpa o estado
    setShowUploadModal(null);
    fetchPatients(); 
  } catch (error) {
    setFeedback({ type: 'error', message: "Erro ao processar o ficheiro." });
  } finally {
    // Desativa o loading independentemente do resultado
    setIsUploading(false);
  }
  };
  // --- FILTRO DE PESQUISA ---
  const filteredPatients = patients.filter(p => 
    p.id.toString().includes(searchTerm)
  );

  const handleAddPatient = async (e) => {
  e.preventDefault();
  if (!newPatientId) return;
  try {
    await api.post('/api/patients/', { id: newPatientId });
    setFeedback({ type: 'success', message: `Paciente ${newPatientId} adicionado!` });
    setNewPatientId("");
    setShowAddPatientModal(false);
    fetchPatients();
  } catch (error) {
    setFeedback({ type: 'error', message: "ID já existente ou erro de rede." });
  }
  };

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
      
      {feedback && (
        <div className={`mb-4 p-3 rounded border text-xs font-bold uppercase tracking-widest animate-in slide-in-from-top duration-300 ${
          feedback.type === 'success' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'
        }`}>
          {feedback.message}
        </div>
      )}
      {/* CONTEÚDO PRINCIPAL */}
      <div className="w-full px-6">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-bold uppercase tracking-tight">Informação Pacientes</h2>
          <button 
            onClick={() => setShowAddPatientModal(true)}
            className="flex items-center gap-2 bg-white border border-gray-300 px-4 py-2 rounded-full text-xs font-bold hover:bg-gray-50 transition-all shadow-sm"
          >
            <PlusSquare size={14} /> ADICIONAR PACIENTE
          </button>
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
                          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Resumo Estruturado</span>
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
                        <PlusSquare size={16} /> ADICIONAR NOVO PDF
                      </button>
                      
                      <button 
                        onClick={() => setOpenDiariesList(openDiariesList === patient.id ? null : patient.id)}
                        className="flex items-center gap-2 text-xs font-bold text-gray-600 hover:text-black transition-colors"
                      >
                        {openDiariesList === patient.id ? <MinusSquare size={16}/> : <PlusSquare size={16}/>}
                        LISTAR DIÁRIOS ({patient.diaries?.length || 0})
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
                                <FileText size={12} /> {d.title || `Diário nº ${d.diary_number}`}
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

      {/* --- MODAL DE VISUALIZAÇÃO DE DIÁRIO (APENAS TEXTO ORIGINAL) --- */}
      {viewingDiary && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-[110] p-6">
          <div className="bg-white w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl border border-gray-300 relative animate-in fade-in zoom-in duration-200">
            
            {/* Botão Fechar Ícone (Superior Direito) */}
            <button 
              onClick={() => setViewingDiary(null)} 
              className="absolute top-4 right-4 text-gray-400 hover:text-black hover:rotate-90 transition-all"
            >
              <X size={20} />
            </button>

            {/* Cabeçalho Minimalista */}
            <div className="p-6 border-b border-gray-100 bg-gray-50/50">
              <h3 className="font-bold uppercase text-sm tracking-tight text-gray-900">
                Nota Clínica Original
              </h3>
            </div>

            {/* Conteúdo de Texto */}
            <div className="p-8 overflow-y-auto flex-1 bg-white">
              <div className="max-w-prose mx-auto">
                {/* Estilo tipográfico para leitura longa */}
                <p className="text-gray-700 leading-relaxed font-serif text-base whitespace-pre-wrap selection:bg-blue-100">
                  {viewingDiary.original_text || "O texto original não está disponível para esta nota clínica."}
                </p>
              </div>
            </div>

            {/* Footer Simples */}
            <div className="p-4 border-t border-gray-100 bg-gray-50/30 flex justify-end">
              <button 
                onClick={() => setViewingDiary(null)}
                className="px-6 py-2 bg-gray-900 text-white text-[10px] font-bold uppercase tracking-widest hover:bg-black transition-all rounded shadow-sm"
              >
                Fechar 
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE UPLOAD */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white p-10 border-2 border-black w-[450px] relative shadow-[10px_10px_0px_0px_rgba(0,0,0,0.2)]">
            
            {isUploading ? (
              /* --- ESTADO DE PROCESSAMENTO --- */
              <div className="flex flex-col items-center py-6 animate-in fade-in duration-500">
                <Loader2 size={48} className="animate-spin text-blue-600 mb-6" />
                <h3 className="font-black uppercase text-center text-lg tracking-tighter">
                  Processando Diários...
                </h3>
                <div className="mt-4 flex flex-col gap-2 items-center">
                  <p className="text-[11px] font-bold text-gray-500 uppercase tracking-widest text-center">
                    O PDF está a ser analisado pela LLM
                  </p>
                </div>
                {/* Bloqueia o fecho acidental durante o processamento crítico */}
                <p className="mt-8 text-[9px] text-blue-500 font-bold uppercase italic">
                  Não feche esta janela
                </p>
              </div>
            ) : (
              /* --- ESTADO INICIAL (SELEÇÃO) --- */
              <>
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
                
                {/* Botão de fechar só disponível antes do upload começar */}
                <button onClick={() => setShowUploadModal(null)} className="absolute top-4 right-4 hover:rotate-90 transition-transform">
                  <X />
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* --- MODAL DE ADICIONAR PACIENTE (ESTILO SIMPLIFICADO) --- */}
      {showAddPatientModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-[110]">
          {/* Layout clean: borda fina, sombra suave, sem neo-brutalismo */}
          <div className="bg-white p-8 border border-gray-300 w-[400px] relative shadow-2xl animate-in fade-in duration-300">
            
            <button onClick={() => setShowAddPatientModal(false)} className="absolute top-4 right-4 hover:rotate-90 transition-transform"><X /></button>
            
            <h3 className="text-center font-bold mb-6 uppercase tracking-tight text-lg text-gray-900">Novo Registo de Paciente</h3>
            
            <form onSubmit={handleAddPatient} className="flex flex-col gap-5">
              <div>
                <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest block mb-1">ID do Paciente</label>
                <input 
                  type="number" 
                  className="w-full border border-gray-300 p-3 rounded focus:ring-1 focus:ring-black outline-none font-medium"
                  placeholder="Ex: 20261708"
                  value={newPatientId}
                  onChange={(e) => setNewPatientId(e.target.value)}
                  required
                />
              </div>
              
              <button 
                type="submit"
                className="w-full bg-gray-900 text-white py-3 rounded font-bold uppercase text-xs tracking-widest hover:bg-black transition-colors shadow"
              >
                Confirmar Registo
              </button>
            </form>
          </div>
        </div>
      )}
    </div> // Fecho da div principal do componente
  );
};

export default Dashboard;