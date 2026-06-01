import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PatientSearch from './components/PatientSearch';
import Dashboard from './pages/Dashboard';
import api from './api'; // Mantendo o seu import original

function AppRoutes() {
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState('');

  const handleFetchPatient = async (processNumber) => {
    setLoading(true);
    setSearchError('');
    try {
      // Usando a sua instância api (axios) diretamente
      const response = await api.get(`/api/patients/${processNumber}/`); 
      setPatient(response.data);
    } catch (error) {
      console.error("Erro ao carregar paciente:", error);
      setSearchError("Paciente não encontrado. Verifique o número de processo.");
    } finally {
      setLoading(false);
    }
  };

  if (!patient) {
    return (
      <div className="min-h-screen bg-slate-50">
        <PatientSearch onSearch={handleFetchPatient} loading={loading} />
        {searchError && (
          <p className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-red-50 border border-red-300 text-red-700 px-5 py-2.5 rounded-lg text-sm font-medium shadow-md z-50 m-0">
            {searchError}
          </p>
        )}
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/"
        element={<Dashboard patient={patient} onNewSearch={() => setPatient(null)} />}
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