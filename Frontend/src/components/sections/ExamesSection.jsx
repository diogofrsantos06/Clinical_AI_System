export default function ExamesSection({ exames }) {
  return (
    <div className="card p-4 bg-white rounded-lg shadow-sm border border-slate-200 mb-4">
      <h3 className="font-bold text-slate-700 mb-2">Exames e Resultados</h3>
      {exames.map((exame, i) => (
        <div key={i} className="mb-3 pb-2 border-b border-slate-100 last:border-0">
          <p className="font-semibold text-sm text-blue-700">{exame.nome}</p>
          <p className="text-sm text-slate-600 italic">{exame.resultado}</p>
        </div>
      ))}
    </div>
  );
}