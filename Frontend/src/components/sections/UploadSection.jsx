import React, { useState, useRef } from 'react';
import { Upload, FileText, X, Loader2, Sparkles } from 'lucide-react';
import api from '../../api';

export default function UploadSection({ patientId, onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleRemove = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleFileSelect = (event) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('patient_id', patientId);

    setIsUploading(true);
    try {
      await api.post('/api/diaries/upload_diary/', formData);
      await onUploadSuccess();
      handleRemove();
    } catch (error) {
      console.error("Erro no upload:", error);
      alert("Erro ao processar o ficheiro.");
    } finally {
      setIsUploading(false);
    }
  };

  console.log("A enviar patient_id para o upload:", patientId);
  
  return (
    <div className="w-full mb-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-[#2d6a4f] p-1.5 rounded-md text-white"><Upload size={16} /></div>
        <h3 className="text-slate-900 m-0 text-[28px] font-bold" style={{ fontFamily: 'Alice, serif' }}>Adicionar PDF</h3>
      </div>

      <div className="bg-slate-50 border-2 border-dashed border-slate-300 rounded-2xl p-10 flex flex-col items-center justify-center relative">
        
        {isUploading ? (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-6 bg-black/20 backdrop-blur-[2px]">
          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-2xl w-full max-w-lg">
            <div className="flex items-center gap-4 mb-6">
              <div className="bg-emerald-100 p-3 rounded-xl text-[#2d6a4f]">
                <Loader2 size={32} className="animate-spin" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-lg">A processar PDF...</h4>
                <p className="text-sm text-slate-500">{selectedFile?.name}</p>
              </div>
            </div>
            
            <p className="text-sm text-slate-600 mb-6 font-medium">A LLM está a extrair informação...</p>
            
            <div className="bg-emerald-50 text-emerald-800 p-4 rounded-xl text-xs flex gap-3 items-start border border-emerald-100">
              <Sparkles size={16} className="flex-shrink-0 mt-0.5" />
              <p>Este processo pode demorar algum tempo.</p>
            </div>
          </div>
        </div>
        ) : !selectedFile ? (
          /* ECRÃ DE SELEÇÃO */
          <div className="flex flex-col items-center cursor-pointer" onClick={() => fileInputRef.current.click()}>
            <div className="bg-emerald-50 p-3 rounded-xl text-[#2d6a4f] mb-4"><Upload size={24} /></div>
            <p className="font-bold text-slate-900">Arraste o PDF para aqui</p>
            <p className="text-slate-500 text-sm mb-6">ou clique para escolher um ficheiro do computador</p>
            <div className="bg-[#2d6a4f] text-white px-6 py-2 rounded-lg font-bold text-sm">Escolher ficheiro</div>
          </div>
        ) : (
          /* ECRÃ DE CONFIRMAÇÃO */
          <div className="w-full bg-white p-4 rounded-xl border border-slate-200 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-3">
              <FileText className="text-[#2d6a4f]" />
              <div>
                <p className="font-bold text-sm text-slate-900">{selectedFile.name}</p>
                <p className="text-xs text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={handleRemove} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg flex items-center gap-2 border border-slate-200">
                <X size={14} /> Remover
              </button>
              <button onClick={handleUpload} className="px-4 py-2 bg-[#2d6a4f] text-white text-sm font-bold rounded-lg flex items-center gap-2">
                <Upload size={14} /> Carregar
              </button>
            </div>
          </div>
        )}
        <input type="file" ref={fileInputRef} className="hidden" accept=".pdf" onChange={handleFileSelect} />
      </div>
    </div>
  );
}