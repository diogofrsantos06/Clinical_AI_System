export default function PatientSearch({ onSearch, loading }) {
  return (
    <div className="flex items-center justify-center h-screen bg-slate-50">
      <form onSubmit={(e) => { e.preventDefault(); onSearch(e.target.search.value); }} className="p-8 bg-white shadow-xl rounded-2xl w-96 text-center">
        <h1 className="text-2xl font-bold mb-4">Pesquisa de Paciente</h1>
        <input 
          name="search" 
          placeholder="Introduza o número de processo..." 
          className="w-full p-3 border rounded-lg mb-4"
          required
        />
        <button 
          disabled={loading}
          className="w-full bg-blue-600 text-white p-3 rounded-lg font-bold hover:bg-blue-700"
        >
          {loading ? 'A pesquisar...' : 'Pesquisar Paciente'}
        </button>
      </form>
    </div>
  );
}