import React, { useState } from 'react';
import { FounderBadge } from '../components/FounderBadge';
import logoChatVGP from '../assets/logo-chatvgp.svg';
import { API_BASE_URL } from '../config';

export const ChatPage = () => {
  const [pergunta, setPergunta] = useState('');
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleBuscar = async () => {
    if (!pergunta.trim()) {
      setError('Digite uma pergunta');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/buscar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta }),
      });

      const data = await response.json();
      setResultado(data);
    } catch (err) {
      setError('Erro ao buscar prestadores');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f0f9ff', padding: '40px 20px' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <img src={logoChatVGP} alt="ChatVGP" style={{ height: '60px', marginBottom: '8px' }} />
          <p style={{ fontSize: '16px', color: '#374151', margin: 0 }}>
            Encontre prestadores de serviços em Vargem Grande Paulista-SP
          </p>
          <a
            href="https://www.instagram.com/chatvgp/"
            target="_blank"
            rel="noreferrer"
            title="Siga o ChatVGP no Instagram"
            style={{ display: 'inline-flex', marginTop: '10px' }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style={{ color: '#E1306C' }}>
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.266.069 1.646.069 4.85 0 3.204-.012 3.584-.07 4.85-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.85-.07-3.251-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zM5.838 12a6.162 6.162 0 1 1 12.324 0 6.162 6.162 0 0 1-12.324 0zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm4.965-10.322a1.44 1.44 0 1 1 2.881.001 1.44 1.44 0 0 1-2.881-.001z"/>
            </svg>
          </a>
        </div>

        <input
          type="text"
          placeholder="Ex: preciso de um eletricista"
          value={pergunta}
          onChange={(e) => setPergunta(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleBuscar()}
          style={{ width: '100%', padding: '12px', marginBottom: '12px', borderRadius: '8px', border: '2px solid #e5e7eb', boxSizing: 'border-box' }}
        />
        
        <button
          onClick={handleBuscar}
          disabled={loading}
          style={{ width: '100%', padding: '12px', backgroundColor: loading ? '#9ca3af' : '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
        >
          {loading ? '🔄 Buscando...' : '🔍 Buscar'}
        </button>

        {error && <div style={{ color: 'red', marginTop: '20px' }}>❌ {error}</div>}

        {resultado && (
          <div style={{ marginTop: '20px', backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
            {resultado.prestadores && resultado.prestadores.length > 0 ? (
              <>
                <h2>✅ Encontrados {resultado.prestadores.length} prestadores</h2>
                {resultado.prestadores.map((p) => (
                  <div key={p.id} style={{ padding: '15px', borderBottom: '1px solid #e5e7eb' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                      <h3 style={{ margin: 0 }}>{p.nome}</h3>
                      <FounderBadge iverificado={p.verificado_hurbem} size="sm" showLabel />
                      {p.premium && (
                        <span title="Prestador Premium" style={{ backgroundColor: '#dbeafe', color: '#0c4a6e', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>
                          👑 Premium
                        </span>
                      )}
                    </div>

                    <p>📱 {p.whatsapp}</p>
                    {p.email && <p>📧 {p.email}</p>}

                    {p.descricao && (
                      <p style={{ fontSize: '14px', color: '#444', marginBottom: '10px', padding: '10px', backgroundColor: '#f9fafb', borderRadius: '4px', borderLeft: '3px solid #3b82f6' }}>
                        {p.descricao}
                      </p>
                    )}

                    {p.notas && (
                      <p style={{ fontSize: '14px', color: '#666', fontStyle: 'italic', marginBottom: '10px', padding: '8px', backgroundColor: '#f3f4f6', borderRadius: '4px' }}>
                        📝 {p.notas}
                      </p>
                    )}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                      {p.instagram && (
                        <a href={p.instagram} target="_blank" rel="noreferrer" title="Instagram" style={{ textDecoration: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={{ color: '#E1306C' }}>
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.266.069 1.646.069 4.85 0 3.204-.012 3.584-.07 4.85-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.85-.07-3.251-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zM5.838 12a6.162 6.162 0 1 1 12.324 0 6.162 6.162 0 0 1-12.324 0zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm4.965-10.322a1.44 1.44 0 1 1 2.881.001 1.44 1.44 0 0 1-2.881-.001z"/>
                          </svg>
                        </a>
                      )}
                      {p.site && (
                        <a href={p.site} target="_blank" rel="noreferrer" title="Website" style={{ fontSize: '20px', textDecoration: 'none', cursor: 'pointer' }}>
                          🌐
                        </a>
                      )}
                    </div>
                    <a
                      href={p.link_whatsapp}
                      target="_blank"
                      rel="noreferrer"
                      onClick={() => {
                        fetch(`${API_BASE_URL}/api/prestadores/${p.id}/clique-whatsapp`, { method: 'POST' }).catch(() => {});
                      }}
                      style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginTop: '10px', padding: '8px 16px', backgroundColor: '#16a34a', color: 'white', textDecoration: 'none', borderRadius: '6px' }}
                    >
                      💬 WhatsApp
                    </a>
                  </div>
                ))}
              </>
            ) : (
              <p>ℹ️ {resultado.mensagem || 'Nenhum prestador encontrado'}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
