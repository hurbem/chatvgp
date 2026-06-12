import React, { useState, useEffect } from 'react';

// Valida CPF (11 dígitos) ou CNPJ (14 dígitos), incluindo dígitos verificadores.
function validarCpfCnpj(valor) {
  const digitos = (valor || '').replace(/\D/g, '');

  if (digitos.length === 11) {
    if (/^(\d)\1{10}$/.test(digitos)) return false;
    for (let i = 9; i <= 10; i++) {
      let soma = 0;
      for (let num = 0; num < i; num++) {
        soma += parseInt(digitos[num], 10) * ((i + 1) - num);
      }
      const digito = ((soma * 10) % 11) % 10;
      if (digito !== parseInt(digitos[i], 10)) return false;
    }
    return true;
  }

  if (digitos.length === 14) {
    if (/^(\d)\1{13}$/.test(digitos)) return false;
    const pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    const pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    for (const [i, pesos] of [[12, pesos1], [13, pesos2]]) {
      let soma = 0;
      for (let num = 0; num < i; num++) {
        soma += parseInt(digitos[num], 10) * pesos[num];
      }
      const resto = soma % 11;
      const digito = resto < 2 ? 0 : 11 - resto;
      if (digito !== parseInt(digitos[i], 10)) return false;
    }
    return true;
  }

  return false;
}

export default function IndicarProfissional() {
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [formData, setFormData] = useState({
    categoria_ids: [],
    nome_prestador: '',
    email_prestador: '',
    whatsapp_prestador: '',
    cpf_cnpj: '',
    descricao: '',
    instagram: '',
    site: '',
  });

  useEffect(() => {
    const carregarDados = async () => {
      try {
        const catRes = await fetch('http://localhost:8000/api/categorias');
        if (catRes.ok) setCategorias(await catRes.json());
      } catch (error) {
        setMessage('Erro ao carregar dados');
      } finally {
        setLoading(false);
      }
    };

    carregarDados();
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (name === 'categoria_ids') {
      const catId = parseInt(value);
      setFormData(prev => {
        const cats = prev.categoria_ids || [];
        if (checked && cats.length < 3) {
          return { ...prev, categoria_ids: [...cats, catId] };
        } else if (!checked) {
          return { ...prev, categoria_ids: cats.filter(id => id !== catId) };
        }
        return prev;
      });
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');

    if (!formData.nome_prestador || !formData.whatsapp_prestador) {
      setMessage('❌ Preencha todos os campos obrigatórios');
      return;
    }

    const whatsappDigits = formData.whatsapp_prestador.replace(/\D/g, '');
    if (whatsappDigits.length !== 11) {
      setMessage('❌ WhatsApp deve ter 11 dígitos (DDD + número)');
      return;
    }

    if (!formData.categoria_ids || formData.categoria_ids.length === 0) {
      setMessage('❌ Selecione pelo menos 1 categoria');
      return;
    }

    if (formData.categoria_ids.length > 3) {
      setMessage('❌ Máximo 3 categorias');
      return;
    }

    if (formData.cpf_cnpj && formData.cpf_cnpj.trim() !== '' && !validarCpfCnpj(formData.cpf_cnpj)) {
      setMessage('❌ CPF/CNPJ inválido');
      return;
    }

    setSubmitLoading(true);

    try {
      // Criar prestador
      const prestadorData = {
        nome: formData.nome_prestador,
        email: formData.email_prestador || null,
        whatsapp: whatsappDigits,
        cpf_cnpj: formData.cpf_cnpj || null,
        categoria_ids: formData.categoria_ids,
        descricao: formData.descricao || null,
        instagram: formData.instagram || null,
        site: formData.site || null,
      };

      const prestadorResponse = await fetch('http://localhost:8000/api/prestadores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(prestadorData),
      });

      if (!prestadorResponse.ok) throw new Error('Erro ao criar prestador');

      setMessage('✅ Prestador cadastrado com sucesso!');
      setFormData({
        categoria_ids: [],
        nome_prestador: '',
        email_prestador: '',
        whatsapp_prestador: '',
        cpf_cnpj: '',
        descricao: '',
        instagram: '',
        site: '',
      });
    } catch (error) {
      setMessage('❌ Erro ao indicar prestador');
      console.error('Erro:', error);
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) return <div style={{ padding: '40px', textAlign: 'center' }}>Carregando...</div>;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f0f9ff', padding: '40px 20px' }}>
      <div style={{ maxWidth: '600px', margin: '0 auto', backgroundColor: 'white', padding: '40px', borderRadius: '12px' }}>
        <h1>🔧 Cadastre seu Serviço</h1>
        <p style={{ color: '#666', marginBottom: '30px' }}>Preencha seus dados e ofereça seus serviços</p>

        {message && (
          <div style={{ padding: '12px', backgroundColor: message.startsWith('✅') ? '#d4edda' : '#f8d7da', color: message.startsWith('✅') ? '#155724' : '#721c24', borderRadius: '8px', marginBottom: '20px' }}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <fieldset style={{ border: '2px solid #e0e0e0', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
            <legend style={{ fontWeight: '600' }}>🔧 Cadastro do Prestador</legend>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontWeight: '500', marginBottom: '10px' }}>Categorias (máx. 3) *</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', maxHeight: '300px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px', borderRadius: '6px' }}>
                {categorias.map(cat => (
                  <div key={cat.id} style={{ display: 'flex', alignItems: 'center' }}>
                    <input
                      type="checkbox"
                      name="categoria_ids"
                      value={cat.id}
                      checked={formData.categoria_ids.includes(cat.id)}
                      onChange={handleInputChange}
                      disabled={!formData.categoria_ids.includes(cat.id) && formData.categoria_ids.length >= 3}
                      style={{ marginRight: '8px', cursor: 'pointer' }}
                    />
                    <label style={{ cursor: 'pointer', fontSize: '14px' }}>{cat.nome}</label>
                  </div>
                ))}
              </div>
              <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
                Selecionadas: {formData.categoria_ids.length}/3
              </small>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontWeight: '500', marginBottom: '5px' }}>Nome *</label>
              <input name="nome_prestador" value={formData.nome_prestador} onChange={handleInputChange} required style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }} />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontWeight: '500', marginBottom: '5px' }}>Email</label>
              <input type="email" name="email_prestador" value={formData.email_prestador} onChange={handleInputChange} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }} />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontWeight: '500', marginBottom: '5px' }}>WhatsApp (DDD + número, 11 dígitos) *</label>
              <input name="whatsapp_prestador" value={formData.whatsapp_prestador} onChange={handleInputChange} required maxLength={11} placeholder="11999999999" style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }} />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontWeight: '500', marginBottom: '5px' }}>CPF/CNPJ</label>
              <input name="cpf_cnpj" value={formData.cpf_cnpj} onChange={handleInputChange} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }} />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontWeight: '500', marginBottom: '5px' }}>Descrição (resumo/bio)</label>
              <textarea name="descricao" value={formData.descricao} onChange={handleInputChange} rows="3" style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }} />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontWeight: '500', marginBottom: '5px' }}>Instagram</label>
              <input name="instagram" value={formData.instagram} onChange={handleInputChange} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }} />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontWeight: '500', marginBottom: '5px' }}>Site</label>
              <input name="site" value={formData.site} onChange={handleInputChange} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }} />
            </div>
          </fieldset>

          <button type="submit" disabled={submitLoading} style={{ width: '100%', padding: '12px', backgroundColor: submitLoading ? '#9ca3af' : '#16a34a', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '500', cursor: 'pointer' }}>
            {submitLoading ? 'Cadastrando...' : 'Cadastrar Prestador'}
          </button>
        </form>
      </div>
    </div>
  );
}
