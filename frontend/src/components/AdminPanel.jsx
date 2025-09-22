import React, { useState, useEffect } from 'react';
import { ArrowLeft, Edit2, Trash2, Save, X, Eye, EyeOff } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/toaster';

const AdminPanel = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [prayers, setPrayers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingPrayer, setEditingPrayer] = useState(null);
  const [editForm, setEditForm] = useState({});
  const { toast } = useToast();

  // API base URL
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 
    (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8001/api');

  // Verificar autenticação
  const handleLogin = () => {
    if (password === 'PRCARLAO') {
      setIsAuthenticated(true);
      loadPrayers();
      toast({
        title: "Acesso autorizado!",
        description: "Bem-vindo ao painel administrativo.",
        duration: 3000,
      });
    } else {
      toast({
        title: "Senha incorreta",
        description: "Verifique a senha e tente novamente.",
        variant: "destructive",
        duration: 3000,
      });
    }
  };

  // Carregar todas as orações
  const loadPrayers = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/prayers`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setPrayers(data.data || []);
        } else {
          throw new Error('Erro ao carregar orações');
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Erro ao carregar orações:', error);
      toast({
        title: "Erro ao carregar orações",
        description: "Não foi possível carregar a lista de orações.",
        variant: "destructive",
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  // Iniciar edição
  const startEdit = (prayer) => {
    setEditingPrayer(prayer.id);
    setEditForm({
      name: prayer.name,
      time: prayer.time,
      unit: prayer.unit || 'minutos',
      description: prayer.description || ''
    });
  };

  // Cancelar edição
  const cancelEdit = () => {
    setEditingPrayer(null);
    setEditForm({});
  };

  // Salvar edição
  const saveEdit = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers/${editingPrayer}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editForm)
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          toast({
            title: "Oração atualizada!",
            description: `Oração de ${editForm.name} foi atualizada com sucesso.`,
            duration: 3000,
          });
          setEditingPrayer(null);
          setEditForm({});
          loadPrayers(); // Recarregar lista
        } else {
          throw new Error(data.message || 'Erro ao atualizar');
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Erro ao atualizar oração:', error);
      toast({
        title: "Erro ao atualizar",
        description: "Não foi possível atualizar a oração. Tente novamente.",
        variant: "destructive",
        duration: 5000,
      });
    }
  };

  // Excluir oração
  const deletePrayer = async (prayer) => {
    if (!confirm(`Tem certeza que deseja excluir a oração de ${prayer.name}?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/prayers/${prayer.id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          toast({
            title: "Oração excluída!",
            description: `Oração de ${prayer.name} foi excluída com sucesso.`,
            duration: 3000,
          });
          loadPrayers(); // Recarregar lista
        } else {
          throw new Error(data.message || 'Erro ao excluir');
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Erro ao excluir oração:', error);
      toast({
        title: "Erro ao excluir",
        description: "Não foi possível excluir a oração. Tente novamente.",
        variant: "destructive",
        duration: 5000,
      });
    }
  };

  // Formatação de data
  const formatDate = (dateString) => {
    if (!dateString) return 'Data não disponível';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Data inválida';
    }
  };

  // Tela de login
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-emerald-100 p-8">
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold text-gray-800 mb-2">Painel Administrativo</h1>
              <p className="text-gray-600">Digite a senha para acessar</p>
            </div>

            <div className="space-y-6">
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                  placeholder="Senha de acesso"
                  className="w-full px-4 py-3 pr-12 rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              <button
                onClick={handleLogin}
                className="w-full bg-emerald-600 text-white py-3 px-6 rounded-lg hover:bg-emerald-700 transition-colors font-medium"
              >
                Entrar
              </button>

              <button
                onClick={() => window.location.href = '/'}
                className="w-full flex items-center justify-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Voltar ao início
              </button>
            </div>
          </div>
        </div>
        <Toaster />
      </div>
    );
  }

  // Painel administrativo
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Painel Administrativo</h1>
            <p className="text-gray-600">Gerencie todas as orações do sistema</p>
          </div>
          <button
            onClick={() => window.location.href = '/'}
            className="flex items-center gap-2 px-4 py-2 bg-white/70 backdrop-blur-sm rounded-lg shadow border border-gray-200 hover:bg-white/90 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-emerald-100">
            <h3 className="font-semibold text-emerald-700 mb-2">Total de Orações</h3>
            <p className="text-2xl font-bold text-emerald-800">{prayers.length}</p>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-teal-100">
            <h3 className="font-semibold text-teal-700 mb-2">Total de Horas</h3>
            <p className="text-2xl font-bold text-teal-800">
              {prayers.reduce((total, prayer) => total + (prayer.time || 0), 0) / 60} h
            </p>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-purple-100">
            <h3 className="font-semibold text-purple-700 mb-2">Progresso</h3>
            <p className="text-2xl font-bold text-purple-800">
              {((prayers.reduce((total, prayer) => total + (prayer.time || 0), 0) / 60) / 1000 * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Tabela de Orações */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-800">Lista de Orações</h2>
              <button
                onClick={loadPrayers}
                disabled={loading}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Carregando...' : 'Atualizar'}
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tempo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {prayers.map((prayer) => (
                  <tr key={prayer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {prayer.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {editingPrayer === prayer.id ? (
                        <input
                          type="text"
                          value={editForm.name}
                          onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                          className="w-full px-2 py-1 border rounded focus:ring-2 focus:ring-emerald-500"
                        />
                      ) : (
                        prayer.name
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {editingPrayer === prayer.id ? (
                        <div className="flex gap-2">
                          <input
                            type="number"
                            value={editForm.time}
                            onChange={(e) => setEditForm({...editForm, time: parseInt(e.target.value)})}
                            className="w-16 px-2 py-1 border rounded focus:ring-2 focus:ring-emerald-500"
                          />
                          <select
                            value={editForm.unit}
                            onChange={(e) => setEditForm({...editForm, unit: e.target.value})}
                            className="px-2 py-1 border rounded focus:ring-2 focus:ring-emerald-500"
                          >
                            <option value="minutos">min</option>
                            <option value="horas">h</option>
                          </select>
                        </div>
                      ) : (
                        `${prayer.time} ${prayer.unit === 'horas' ? 'h' : 'min'}`
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                      {editingPrayer === prayer.id ? (
                        <input
                          type="text"
                          value={editForm.description}
                          onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                          className="w-full px-2 py-1 border rounded focus:ring-2 focus:ring-emerald-500"
                          placeholder="Descrição..."
                        />
                      ) : (
                        prayer.description || '-'
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(prayer.datetime || prayer.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {editingPrayer === prayer.id ? (
                        <div className="flex gap-2">
                          <button
                            onClick={saveEdit}
                            className="text-emerald-600 hover:text-emerald-900 p-1"
                            title="Salvar"
                          >
                            <Save className="w-4 h-4" />
                          </button>
                          <button
                            onClick={cancelEdit}
                            className="text-gray-600 hover:text-gray-900 p-1"
                            title="Cancelar"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex gap-2">
                          <button
                            onClick={() => startEdit(prayer)}
                            className="text-blue-600 hover:text-blue-900 p-1"
                            title="Editar"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deletePrayer(prayer)}
                            className="text-red-600 hover:text-red-900 p-1"
                            title="Excluir"
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

          {prayers.length === 0 && !loading && (
            <div className="text-center py-12">
              <p className="text-gray-500">Nenhuma oração encontrada.</p>
            </div>
          )}
        </div>
      </div>
      <Toaster />
    </div>
  );
};

export default AdminPanel;