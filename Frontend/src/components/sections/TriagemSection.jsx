import React, { useState, useEffect } from 'react';
import { FileText, X, Sparkles } from 'lucide-react';

export default function TriagemSection({ processNumber, triagemData, onSave }) {
  const [texto, setTexto] = useState(triagemData || "");
  const [alterado, setAlterado] = useState(false);
  const [analiseClinica, setAnaliseClinica] = useState(null);
  const [carregando, setCarregando] = useState(false);

  // Detecta alterações para gerir o estado 'alterado'
  useEffect(() => {
    setAlterado(texto !== (triagemData || ""));
  }, [texto, triagemData]);

  const handleDescartar = () => {
    setTexto(triagemData || "");
    setAlterado(false);
  };

  const enviarTriagemParaAnalise = async () => {
    setCarregando(true);
    
    // (Opcional) Se quiseres que o Dashboard também "saiba" qual é o texto atual,
    // podes chamar o onSave aqui. Se não precisares de guardar na Base de Dados, podes remover esta linha.
    if (alterado) {
       onSave(texto);
       setAlterado(false);
    }

    try {
      const response = await fetch('/api/summaries/patient-summary/analyze_triage/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: processNumber, 
          triage_text: texto
        })
      });
      
      const data = await response.json();
      setAnaliseClinica(data);
    } catch (error) {
      console.error("Erro na triagem:", error);
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="w-full mb-8">
      {/* Cabeçalho */}
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-[#2d6a4f] p-1 rounded-md text-white">
          <FileText size={16} />
        </div>
        <div>
          <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', fontWeight: 'bold', lineHeight: '1' }}>
            Relatório de Triagem
          </h3>
          <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '1px' }}>
            Campo livre · opcional
          </p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Escreva aqui o relatório da triagem (opcional)..."
          className="w-full h-32 p-4 bg-white border border-slate-200 rounded-xl focus:ring-1 focus:ring-[#2d6a4f] focus:border-[#2d6a4f] outline-none resize-none text-slate-700 transition-all"
        />

        <div className="flex justify-between items-center mt-4">
          {/* Esquerda: Status do texto */}
          <span className="text-xs text-slate-400">
            {texto.length} caracteres {alterado ? "· não analisado" : "· guardado"}
          </span>
          
          <div className="flex gap-3">
            
            {/* O botão Descartar só aparece se houver alterações não guardadas */}
            {alterado && (
              <button 
                onClick={handleDescartar} 
                className="px-4 py-2 text-sm font-bold text-slate-600 hover:bg-slate-100 rounded-lg flex items-center gap-2"
                disabled={carregando}
              >
                <X size={16} /> Descartar
              </button>
            )}

            {/* O botão Analisar aparece sempre que há texto, independentemente de estar alterado ou não */}
            {texto.length > 0 && (
              <button 
                onClick={enviarTriagemParaAnalise}
                disabled={carregando}
                className="px-4 py-2 bg-[#2d6a4f] text-white text-sm font-bold rounded-lg flex items-center gap-2 hover:bg-[#235841] transition-colors"
              >
                <Sparkles size={16} /> {carregando ? "A analisar..." : "Analisar Triagem"}
              </button>
            )}
            
          </div>
        </div>
      </div>

      {analiseClinica && (
        <div className="w-full mt-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-[#2d6a4f] p-1 rounded-md text-white">
              <FileText size={16} />
            </div>
            <div>
              <h3 className="text-slate-900 m-0" style={{ fontFamily: 'Alice, serif', fontSize: '28px', fontWeight: 'bold', lineHeight: '1' }}>
                Sugestão da IA
              </h3>
              <p style={{ color: 'var(--ink-500)', fontSize: '13px', marginTop: '1px' }}>
                Análise de dados clínicos e priorização baseada na triagem atual.
              </p>
            </div>
          </div>

          <div className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl">
            <div className="w-full p-4 bg-white border border-slate-200 rounded-xl text-slate-700 leading-relaxed text-sm min-h-[120px] whitespace-pre-wrap">
              {analiseClinica.analise_texto}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}