import React, { useState, useEffect } from 'react';
import { Trash2, Edit, Save, X, LogOut, Database, AlertCircle } from 'lucide-react';

const AdminPanel = ({ onLogout }) => {
  const [prayers, setPrayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [stats, setStats] = useState({ total_hours: 0, total_entries: 0 });
  const [error, setError] = useState(null);

  // API base URL - EXCLUSIVAMENTE backend Supabase
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 
    (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000/api');

  useEffect(() => {
    loadPrayers();
    loadStats();
  }, []);

  const loadPrayers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/prayers`);
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      const result = await response.json();
      if (result.success && result.data) {
        setPrayers(result.data || []);
      } else {
        throw new Error('Dados inválidos recebidos do Supabase');
      }
    } catch (error) {
      console.error('❌ Erro ao carregar orações do Supabase:', error);
      setError(`Erro ao conectar com Supabase: ${error.message}`);
      // NÃO usar localStorage - sistema deve falhar se Supabase não funcionar
      setPrayers([]);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers/stats`);
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      const result = await response.json();
      if (result.success && result.data) {
        setStats(result.data);
      } else {
        throw new Error('Estatísticas inválidas recebidas do Supabase');
      }
    } catch (error) {
      console.error('❌ Erro ao carregar estatísticas do Supabase:', error);
      setError(`Erro ao carregar estatísticas: ${error.message}`);
      setStats({ total_hours: 0, total_entries: 0 });
    }
  };

  const handleEdit = (prayer) => {
    setEditingId(prayer.id);
    setEditForm({
      name: prayer.name,
      time_minutes: prayer.time_minutes,
      description: prayer.description || ''
    });
  };

  const handleSave = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editForm),
      });

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        // Recarregar dados do Supabase
        await loadPrayers();
        await loadStats();
        setEditingId(null);
        setEditForm({});
        
        // Mostrar sucesso
        alert('✅ Oração atualizada no Supabase com sucesso!');
      } else {
        throw new Error(result.message || 'Erro ao atualizar oração');
      }
    } catch (error) {
      console.error('❌ Erro ao atualizar oração no Supabase:', error);
      alert(`❌ Erro ao atualizar: ${error.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir esta oração do Supabase?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/prayers/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        // Recarregar dados do Supabase
        await loadPrayers();
        await loadStats();
        
        // Mostrar sucesso
        alert('✅ Oração excluída do Supabase com sucesso!');
      } else {
        throw new Error(result.message || 'Erro ao excluir oração');
      }
    } catch (error) {
      console.error('❌ Erro ao excluir oração do Supabase:', error);
      alert(`❌ Erro ao excluir: ${error.message}`);
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditForm({});
  };

  const handleLogout = () => {
    // NÃO usar localStorage para autenticação
    onLogout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados do Supabase...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 flex items-center justify-center">
        <div className="text-center bg-white/70 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-red-200 max-w-md">
          <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-red-800 mb-4">Erro de Conexão</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <p className="text-sm text-gray-600 mb-4">
            O sistema funciona EXCLUSIVAMENTE com Supabase. Verifique se:
          </p>
          <ul className="text-left text-sm text-gray-600 mb-6">
            <li>• Supabase está configurado corretamente</li>
            <li>• Tabela 'prayers' existe no banco</li>
            <li>• Políticas RLS estão ativas</li>
            <li>• Conexão com internet está funcionando</li>
          </ul>
          <button
            onClick={() => window.location.reload()}
            className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Database className="w-8 h-8 text-emerald-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Painel Administrativo</h1>
                <p className="text-gray-600">Sistema EXCLUSIVAMENTE Supabase</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sair
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-emerald-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Total de Horas</h3>
            <p className="text-3xl font-bold text-emerald-600">{stats.total_hours}</p>
            <p className="text-sm text-gray-500">de 1000 horas</p>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-teal-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Orações Registradas</h3>
            <p className="text-3xl font-bold text-teal-600">{stats.total_entries}</p>
            <p className="text-sm text-gray-500">no Supabase</p>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-purple-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Progresso</h3>
            <p className="text-3xl font-bold text-purple-600">
              {((stats.total_hours / 1000) * 100).toFixed(1)}%
            </p>
            <p className="text-sm text-gray-500">da meta alcançada</p>
          </div>
        </div>

        {/* Prayers Table */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Todas as Orações ({prayers.length})
          </h2>
          
          {prayers.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">Nenhuma oração encontrada no Supabase</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Nome</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Tempo</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Data/Hora</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Descrição</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-800">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {prayers.map((prayer) => (
                    <tr key={prayer.id} className="border-b border-gray-100 hover:bg-gray-50/50">
                      <td className="py-3 px-4">
                        {editingId === prayer.id ? (
                          <input
                            type="text"
                            value={editForm.name}
                            onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                            className="w-full px-2 py-1 border border-gray-300 rounded"
                          />
                        ) : (
                          <span className="font-medium text-gray-800">{prayer.name}</span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        {editingId === prayer.id ? (
                          <input
                            type="number"
                            value={editForm.time_minutes}
                            onChange={(e) => setEditForm({...editForm, time_minutes: parseInt(e.target.value)})}
                            className="w-20 px-2 py-1 border border-gray-300 rounded"
                          />
                        ) : (
                          <span className="text-gray-600">
                            {prayer.time_minutes >= 60 
                              ? `${Math.floor(prayer.time_minutes / 60)}h ${prayer.time_minutes % 60}min`
                              : `${prayer.time_minutes}min`
                            }
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-gray-600 text-sm">
                          {new Date(prayer.datetime).toLocaleString('pt-BR')}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {editingId === prayer.id ? (
                          <input
                            type="text"
                            value={editForm.description}
                            onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                            className="w-full px-2 py-1 border border-gray-300 rounded"
                            placeholder="Descrição opcional"
                          />
                        ) : (
                          <span className="text-gray-600 text-sm">
                            {prayer.description || '-'}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        {editingId === prayer.id ? (
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleSave(prayer.id)}
                              className="text-green-600 hover:text-green-800 transition-colors"
                              title="Salvar no Supabase"
                            >
                              <Save className="w-4 h-4" />
                            </button>
                            <button
                              onClick={handleCancel}
                              className="text-gray-600 hover:text-gray-800 transition-colors"
                              title="Cancelar"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleEdit(prayer)}
                              className="text-blue-600 hover:text-blue-800 transition-colors"
                              title="Editar"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(prayer.id)}
                              className="text-red-600 hover:text-red-800 transition-colors"
                              title="Excluir do Supabase"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            🔒 Sistema EXCLUSIVAMENTE Supabase - Todos os dados na nuvem
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
