import React, { useState, useEffect } from 'react';
import './IndicarProfissional.css';

interface Condominio {
  id: number;
  nome: string;
  cidade: string;
}

interface Categoria {
  id: number;
  nome: string;
}

interface FormData {
  condominio_id: string;
  nome_morador: string;
  whatsapp_morador: string;
  categoria_id: string;
  nome_prestador: string;
  whatsapp_prestador: string;
  instagram: string;
  site: string;
  notas: string;
}

export default function IndicarProfissional() {
  const [condominios, setCondominios] = useState<Condominio[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('');

  const [formData, setFormData] = useState<FormData>({
    condominio_id: '',
    nome_morador: '',
    whatsapp_morador: '',
    categoria_id: '',
    nome_prestador: '',
    whatsapp_prestador: '',
    instagram: '',
    site: '',
    notas: '',
  });

  useEffect(() => {
    const carregarDados = async () => {
      try {
        const [condRes, catRes] = await Promise.all([
          fetch('https://api.chatvgp.com/api/condominios'),
          fetch('https://api.chatvgp.com/api/categorias'),
        ]);

        if (condRes.ok) {
          const condData = await condRes.json();
          setCondominios(condData);
        }

        if (catRes.ok) {
          const catData = await catRes.json();
          setCategorias(catData);
        }
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
        setMessage('Erro ao carregar dados. Tente novamente.');
        setMessageType('error');
      } finally {
        setLoading(false);
      }
    };

    carregarDados();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validarFormulario = (): boolean => {
    if (!formData.condominio_id) {
      setMessage('Selecione um condomínio');
      setMessageType('error');
      return false;
    }
    if (!formData.nome_morador.trim()) {
      setMessage('Informe seu nome');
      setMessageType('error');
      return false;
    }
    if (!formData.whatsapp_morador.trim()) {
      setMessage('Informe seu WhatsApp');
      setMessageType('error');
      return false;
    }
    if (!formData.categoria_id) {
      setMessage('Selecione uma categoria');
      setMessageType('error');
      return false;
    }
    if (!formData.nome_prestador.trim()) {
      setMessage('Informe o nome do prestador');
      setMessageType('error');
      return false;
    }
    if (!formData.whatsapp_prestador.trim()) {
      setMessage('Informe o WhatsApp do prestador');
      setMessageType('error');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');

    if (!validarFormulario()) {
      return;
    }

    setSubmitLoading(true);

    try {
      const prestadorData = {
        nome: formData.nome_prestador,
        whatsapp: formData.whatsapp_prestador,
        instagram: formData.instagram || null,
        site: formData.site || null,
        categoria_id: parseInt(formData.categoria_id),
        status: 'ativo',
        notas: formData.notas || null,
      };

      const response = await fetch('https://api.chatvgp.com/api/prestadores', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(prestadorData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao criar prestador');
      }

      const novoPresador = await response.json();

      await fetch('https://api.chatvgp.com/api/feedback/indicacoes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          condominio_id: parseInt(formData.condominio_id),
          nome_morador: formData.nome_morador,
          whatsapp_morador: formData.whatsapp_morador,
          prestador_id: novoPresador.id,
          prestador_nome: novoPresador.nome,
        }),
      }).catch(err => {
        console.warn('Erro ao registrar indicação:', err);
      });

      setMessage('✅ Prestador indicado com sucesso! Obrigado pela indicação.');
      setMessageType('success');

      setFormData({
        condominio_id: '',
        nome_morador: '',
        whatsapp_morador: '',
        categoria_id: '',
        nome_prestador: '',
        whatsapp_prestador: '',
        instagram: '',
        site: '',
        notas: '',
      });
    } catch (error: any) {
      console.error('Erro:', error);
      setMessage(`❌ ${error.message}`);
      setMessageType('error');
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="indicar-container">
        <div className="loading">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="indicar-container">
      <div className="indicar-card">
        <h1>Indique um Profissional</h1>
        <p className="subtitle">Conhece alguém bom? Indique para sua comunidade!</p>

        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <fieldset className="form-section">
            <legend>📝 Dados de quem indica</legend>

            <div className="form-group">
              <label htmlFor="condominio_id">
                Condomínio <span className="required">*</span>
              </label>
              <select
                id="condominio_id"
                name="condominio_id"
                value={formData.condominio_id}
                onChange={handleInputChange}
                required
              >
                <option value="">Selecione um condomínio</option>
                {condominios.map(cond => (
                  <option key={cond.id} value={cond.id}>
                    {cond.nome} - {cond.cidade}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="nome_morador">
                Seu Nome <span className="required">*</span>
              </label>
              <input
                id="nome_morador"
                type="text"
                name="nome_morador"
                placeholder="João Silva"
                value={formData.nome_morador}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="whatsapp_morador">
                Seu WhatsApp <span className="required">*</span>
              </label>
              <input
                id="whatsapp_morador"
                type="tel"
                name="whatsapp_morador"
                placeholder="(11) 99999-9999"
                value={formData.whatsapp_morador}
                onChange={handleInputChange}
                required
              />
            </div>
          </fieldset>

          <fieldset className="form-section">
            <legend>🔧 Dados do prestador</legend>

            <div className="form-group">
              <label htmlFor="categoria_id">
                Categoria <span className="required">*</span>
              </label>
              <select
                id="categoria_id"
                name="categoria_id"
                value={formData.categoria_id}
                onChange={handleInputChange}
                required
              >
                <option value="">Selecione uma categoria</option>
                {categorias.map(cat => (
                  <option key={cat.id} value={cat.id}>
                    {cat.nome}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="nome_prestador">
                Nome <span className="required">*</span>
              </label>
              <input
                id="nome_prestador"
                type="text"
                name="nome_prestador"
                placeholder="Nome do profissional"
                value={formData.nome_prestador}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="whatsapp_prestador">
                WhatsApp <span className="required">*</span>
              </label>
              <input
                id="whatsapp_prestador"
                type="tel"
                name="whatsapp_prestador"
                placeholder="(11) 99999-9999"
                value={formData.whatsapp_prestador}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="instagram">Instagram</label>
              <input
                id="instagram"
                type="url"
                name="instagram"
                placeholder="https://instagram.com/usuario"
                value={formData.instagram}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="site">Site</label>
              <input
                id="site"
                type="url"
                name="site"
                placeholder="https://exemplo.com"
                value={formData.site}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="notas">Notas adicionais</label>
              <textarea
                id="notas"
                name="notas"
                placeholder="Algo especial sobre este profissional?"
                value={formData.notas}
                onChange={handleInputChange}
                rows={4}
              />
            </div>
          </fieldset>

          <button
            type="submit"
            className="submit-btn"
            disabled={submitLoading}
          >
            {submitLoading ? 'Enviando...' : 'Enviar Indicação'}
          </button>
        </form>
      </div>
    </div>
  );
}
