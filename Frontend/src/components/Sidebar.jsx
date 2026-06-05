import {
  UserRound,
  ChevronLeft,
  Stethoscope,
  FlaskConical
} from 'lucide-react';


import { Link } from 'react-router-dom'; 

const NAV_ITEMS = [
  { id: 'triagem', label: 'Relatório de Triagem', icon: (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><line x1="10" y1="9" x2="8" y2="9" /></svg>)},
  { id: 'antecedentes', label: 'Antecedentes Pessoais e Diagnósticos', icon: (<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></svg>) },
  { id: 'medicacao', label: 'Medicação Habitual', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="7" y="3" width="10" height="18" rx="5" ry="5" /><line x1="7" y1="12" x2="17" y2="12" /></svg>},
  { id: 'alergias', label: 'Alergias', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>, allergyKey: true },
  { id: 'exames', label: 'Exames e Análises', icon: <FlaskConical size={18} strokeWidth={2} /> },
  { id: 'plano', label: 'Plano da Última Consulta', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> },
  { id: 'upload', label: 'Adicionar PDF', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg> },
  { id: 'diarios', label: 'Diários Clínicos', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> },
];

export default function Sidebar({ activeSection, onNavigate, hasAllergies, patient, onNewSearch }) {
  console.log("hasAllergies está a receber:", hasAllergies); // Vê o que aparece na consola F12
  function scrollTo(id) {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      onNavigate(id);
    }
  }

  return (
    <aside style={{ width: 240, minWidth: 240, background: '#216348', height: '100vh', position: 'sticky', top: 0, display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '1.25rem 1rem', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ width: 40, height: 40, borderRadius: 10, background: '#3d7a62', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Stethoscope size={20} color="white" />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontWeight: 700, fontSize: '1.1rem', color: 'white', fontFamily: 'Georgia, serif' }}>Resumo Clínico</span>
            <span style={{ fontSize: '0.85rem', color: '#e2e8f0', fontFamily: 'Georgia, serif' }}>Dr. Paulo Ferreira</span>
        </div>
        </div>

      <nav style={{ flex: 1, overflowY: 'auto', padding: '0.5rem 0.625rem' }}>
        <p style={{ fontSize: '0.625rem', fontWeight: 700, color: '#81a396', textTransform: 'uppercase', letterSpacing: '0.125em', padding: '0.5rem', fontFamily: 'Georgia, serif' }}>Secções do Resumo</p>

        {NAV_ITEMS.map(({ id, label, icon: Icon, allergyKey }) => {
            const isAllergyAlert = allergyKey && hasAllergies;
            const isActive = activeSection === id;
            
            return (
              <button key={id} onClick={() => scrollTo(id)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.6rem 0.75rem',
                  borderRadius: '0.6rem', width: '100%', border: 'none', cursor: 'pointer',
                  background: isActive ? 'rgba(255, 255, 255, 0.15)' : (isAllergyAlert ? '#fbbf24' : 'transparent'),
                  transition: 'all 0.2s', textAlign: 'left', fontFamily: 'Alice, serif'
                }}
              >
            <div style={{ background: '#2d6a4f', padding: '4px', borderRadius: '6px', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {Icon}
            </div>
            <span style={{ 
              flex: 1, 
              fontSize: '0.95rem', 
              color: isAllergyAlert ? '#000' : '#e2e8f0', 
              fontWeight: isActive ? 600 : 500 
            }}>
              {label}
            </span>
          </button>
        );
      })}

        <div style={{ margin: '0.75rem 0', borderTop: '1px solid rgba(255,255,255,0.1)' }} />

        <Link 
          to={patient ? `/paciente/${patient.numero_processo}/perfil` : '#'}
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.75rem', 
            padding: '0.6rem 0.75rem', 
            color: '#e2e8f0', 
            textDecoration: 'none', 
            fontSize: '0.85rem', 
            transition: '0.2s', 
            fontFamily: 'Georgia, serif' 
          }}
        >
          <UserRound size={18} />
          <span>Perfil do Paciente</span>
          <span style={{ marginLeft: 'auto', opacity: 0.6 }}>↗</span>
        </Link>
      </nav>

      <div style={{ 
      padding: '0.75rem', 
      borderTop: '0.5px solid rgba(255, 255, 255, 0.2)' 
    }}>
      <button 
        onClick={onNewSearch} 
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          gap: '0.5rem', 
          background: 'rgba(255, 255, 255, 0.08)', // Fundo ligeiramente mais claro que o sidebar
          border: '1px solid rgba(255, 255, 255, 0.1)', // Borda subtil
          borderRadius: '0.75rem', // Cantos arredondados iguais à imagem
          padding: '0.75rem', // Espaçamento interno
          color: 'white', 
          fontSize: '0.9rem', 
          fontWeight: '500',
          cursor: 'pointer', 
          width: '100%', 
          fontFamily: 'Alice, serif',
          transition: 'all 0.2s'
        }}
      >
        <ChevronLeft size={18} /> Nova pesquisa
      </button>
    </div>
    </aside>
  );
}