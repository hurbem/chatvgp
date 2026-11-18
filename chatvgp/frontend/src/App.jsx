import React, { useState } from 'react';
import { ChatPage } from './pages/ChatPage';
import IndicarProfissional from './pages/IndicarProfissional';

// Data do build, gravada no momento do `npm run build` (ver script "build" no package.json).
// Se não existir (ex.: em `npm start`), o selo não é exibido.
const BUILD_DATE = process.env.REACT_APP_BUILD_DATE;

export default function App() {
  const [currentPage, setCurrentPage] = useState('chat');

  return (
    <>
      {currentPage === 'chat' && <ChatPage />}
      {currentPage === 'indicar' && <IndicarProfissional />}

      {/* Navigation Buttons */}
      <div style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        zIndex: 9999
      }}>
        {currentPage !== 'chat' && (
          <button
            onClick={() => setCurrentPage('chat')}
            style={{
              padding: '10px 16px',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '24px',
              fontWeight: '500',
              cursor: 'pointer',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
            }}
          >
            💬 Chat
          </button>
        )}
        {currentPage !== 'indicar' && (
          <button
            onClick={() => setCurrentPage('indicar')}
            style={{
              padding: '10px 16px',
              backgroundColor: '#16a34a',
              color: 'white',
              border: 'none',
              borderRadius: '24px',
              fontWeight: '500',
              cursor: 'pointer',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
            }}
          >
            ⭐ Cadastrar
          </button>
        )}

        {/* Version Display */}
        {BUILD_DATE && <div
          style={{
            padding: '6px 12px',
            backgroundColor: '#6b7280',
            color: 'white',
            borderRadius: '24px',
            fontSize: '11px',
            fontWeight: '500',
            textAlign: 'center',
            userSelect: 'none',
            marginTop: '8px'
          }}
          title="Data do último build"
        >
          {BUILD_DATE}
        </div>}
      </div>
    </>
  );
}
