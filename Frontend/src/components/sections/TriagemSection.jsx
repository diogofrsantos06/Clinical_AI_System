import React, { useState, useEffect } from 'react';
import { FileText, X, Check } from 'lucide-react';

export default function TriagemSection({ triagemData, onSave }) {
  const [texto, setTexto] = useState(triagemData || "");
  const [alterado, setAlterado] = useState(false);

  // Detecta alterações para mostrar os botões
  useEffect(() => {
    setAlterado(texto !== (triagemData || ""));
  }, [texto, triagemData]);

  const handleGuardar = () => {
    onSave(texto);
    setAlterado(false);
  };

  const handleDescartar = () => {
    setTexto(triagemData || "");
    setAlterado(false);
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
          // Fundo branco (bg-white) e borda mais fina (border-[0.5px])
          className="w-full h-32 p-4 bg-white border border-slate-200 rounded-xl focus:ring-1 focus:ring-[#2d6a4f] focus:border-[#2d6a4f] outline-none resize-none text-slate-700 transition-all"
        />

        <div className="flex justify-between items-center mt-4">
          <span className="text-xs text-slate-400">
            {texto.length} caracteres {alterado ? "· alterações por guardar" : "· guardado"}
          </span>
          
          {alterado && (
            <div className="flex gap-3">
              <button 
                onClick={handleDescartar}
                className="px-4 py-2 text-sm font-bold text-slate-600 hover:bg-slate-100 rounded-lg flex items-center gap-2"
              >
                <X size={16} /> Descartar
              </button>
              <button 
                onClick={handleGuardar}
                // Borda verde fina e botão sólido
                className="px-4 py-2 bg-[#2d6a4f] text-white text-sm font-bold rounded-lg flex items-center gap-2 hover:bg-[#235841] transition-colors"
              >
                <Check size={16} /> Guardar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}