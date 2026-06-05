import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import PatientSearch from './components/PatientSearch';
import Dashboard from './pages/Dashboard';
import PatientProfile from './pages/PatientProfile';
import api from './api';

function AppRoutes() {
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState('');
  const navigate = useNavigate();

  const handleFetchPatient = async (processNumber) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/patients/${processNumber}/`);
      setPatient(response.data);
      navigate(`/paciente/${processNumber}`); 
    } catch (error) {
      setSearchError("Paciente não encontrado.");
      setLoading(false);
    }
  };

  return (
    <Routes>
      {/* Rota Única da Pesquisa */}
      <Route 
        path="/" 
        element={
          <div className="min-h-screen bg-slate-50">
            <PatientSearch 
              onSearch={handleFetchPatient} 
              loading={loading} 
              onMount={() => { setLoading(false); setSearchError(''); }} 
            />
            {searchError && (
              <p className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-red-50 border border-red-300 text-red-700 px-5 py-2.5 rounded-lg text-sm font-medium shadow-md z-50">
                {searchError}
              </p>
            )}
          </div>
        } 
      />

      {/* Rota do Dashboard (Faltava esta!) */}
      <Route
        path="/paciente/:numero_processo"
        element={<Dashboard patient={patient} onNewSearch={() => { setPatient(null); navigate('/'); }} />}
      />

      {/* Rota do Perfil */}
      <Route
        path="/paciente/:numero_processo/perfil"
        element={<PatientProfile patient={patient} />}
      />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}