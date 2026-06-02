import React, { useState, useEffect } from "react";
import api from "../services/api";
import { Prestador, Categoria, Condominio } from "../types";

export const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"prestadores" | "feedback" | "ranking">("prestadores");
  const [prestadores, setPrestadores] = useState<Prestador[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [condominios, setCondominios] = useState<Condominio[]>([]);
  const [loading, setLoading] = useState(false);

  // Form
  const [formData, setFormData] = useState({
    nome: "",
    whatsapp: "",
    categoria_id: "",
    condominio_ids: [] as number[],
    notas: "",
  });

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    setLoading(true);
    try {
      const [prestatidoresData, categoriasData, condominiosData] = await Promise.all([
        api.getPrestadores(),
        api.getCategorias(),
        api.getCondominios(),
      ]);
      setPrestadores(prestatidoresData);
      setCategorias(categoriasData);
      setCondominios(condominiosData);
    } catch (error) {
      console.error("Erro ao carregar dados:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.createPrestador({
        ...formData,
        categoria_id: parseInt(formData.categoria_id),
        status: "ativo",
      });

      // Limpar form
      setFormData({
        nome: "",
        whatsapp: "",
        categoria_id: "",
        condominio_ids: [],
        notas: "",
      });

      // Recarregar
      carregarDados();
    } catch (error: any) {
      alert("Erro ao criar prestador: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Admin ChatVGP</h1>
          <button
            onClick={() => {
              localStorage.removeItem("token");
              window.location.href = "/";
            }}
            className="px-4 py-2 text-gray-700 hover:text-gray-900"
          >
            Sair
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-6xl mx-auto px-4 py-6 border-b border-gray-200">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab("prestadores")}
            className={`px-4 py-2 font-medium ${
              activeTab === "prestadores"
                ? "text-blue-600 border-b-2 border-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Prestadores
          </button>
          <button
            onClick={() => setActiveTab("feedback")}
            className={`px-4 py-2 font-medium ${
              activeTab === "feedback"
                ? "text-blue-600 border-b-2 border-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Feedback
          </button>
          <button
            onClick={() => setActiveTab("ranking")}
            className={`px-4 py-2 font-medium ${
              activeTab === "ranking"
                ? "text-blue-600 border-b-2 border-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Ranking
          </button>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {activeTab === "prestadores" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Form */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Cadastrar Prestador</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                    <input
                      type="text"
                      value={formData.nome}
                      onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">WhatsApp</label>
                    <input
                      type="text"
                      value={formData.whatsapp}
                      onChange={(e) => setFormData({ ...formData, whatsapp: e.target.value })}
                      placeholder="11999887766"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
                    <select
                      value={formData.categoria_id}
                      onChange={(e) => setFormData({ ...formData, categoria_id: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                      required
                    >
                      <option value="">Selecione...</option>
                      {categorias.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.nome}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Condomínios</label>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {condominios.map((cond) => (
                        <label key={cond.id} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData.condominio_ids.includes(cond.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFormData({
                                  ...formData,
                                  condominio_ids: [...formData.condominio_ids, cond.id],
                                });
                              } else {
                                setFormData({
                                  ...formData,
                                  condominio_ids: formData.condominio_ids.filter((id) => id !== cond.id),
                                });
                              }
                            }}
                            className="w-4 h-4 text-blue-600"
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            {cond.nome} ({cond.cidade})
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Notas</label>
                    <textarea
                      value={formData.notas}
                      onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                      rows={3}
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 transition"
                  >
                    {loading ? "Salvando..." : "Cadastrar"}
                  </button>
                </form>
              </div>
            </div>

            {/* Lista */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Prestadores Cadastrados</h2>
                {loading ? (
                  <p className="text-gray-600">Carregando...</p>
                ) : prestadores.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-2 px-4 font-medium text-gray-900">Nome</th>
                          <th className="text-left py-2 px-4 font-medium text-gray-900">Categoria</th>
                          <th className="text-left py-2 px-4 font-medium text-gray-900">WhatsApp</th>
                          <th className="text-left py-2 px-4 font-medium text-gray-900">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {prestadores.map((prest) => (
                          <tr key={prest.id} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-3 px-4 text-gray-900">{prest.nome}</td>
                            <td className="py-3 px-4 text-gray-600">{prest.categoria.nome}</td>
                            <td className="py-3 px-4 text-gray-600">{prest.whatsapp}</td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${prest.status === 'ativo' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                {prest.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-gray-600">Nenhum prestador cadastrado ainda</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === "feedback" && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Feedback</h2>
            <p className="text-gray-600">
              Aba de feedback será implementada em breve. Aqui você poderá registrar avaliações dos prestadores.
            </p>
          </div>
        )}

        {activeTab === "ranking" && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Ranking</h2>
            <p className="text-gray-600">
              Aba de ranking será implementada em breve. Aqui você poderá visualizar o ranking de prestadores.
            </p>
          </div>
        )}
      </main>
    </div>
  );
};
