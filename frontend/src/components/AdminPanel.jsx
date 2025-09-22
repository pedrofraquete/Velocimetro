import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Users, 
  Clock, 
  Edit, 
  Trash2, 
  Plus, 
  LogOut, 
  Save,
  X,
  Calendar,
  User,
  Timer,
  MessageSquare
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/toaster';

const AdminPanel = ({ onLogout }) => {
  const [prayers, setPrayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingPrayer, setEditingPrayer] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [stats, setStats] = useState({ total_hours: 0, total_entries: 0 });
  const { toast } = useToast();

  // API base URL
  const API_BASE_URL = process.env.NODE_ENV === 'production' 
    ? '/api' 
    : 'http://localhost:8000/api';

  useEffect(() => {
    loadPrayers();
    loadStats();
  }, []);

  const loadPrayers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers`);
      if (response.ok) {
        const data = await response.json();
        setPrayers(data.data || data || []);
      } else {
        // Fallback para localStorage
        const localPrayers = JSON.parse(localStorage.getItem('prayers') || '[]');
        setPrayers(localPrayers);
      }
    } catch (error) {
      console.error('Erro ao carregar orações:', error);
      const localPrayers = JSON.parse(localStorage.getItem('prayers') || '[]');
      setPrayers(localPrayers);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleEdit = (prayer) => {
    setEditingPrayer({
      ...prayer,
      time: prayer.time_minutes ? prayer.time_minutes : prayer.time,
      unit: prayer.time_minutes ? 'minutos' : 'horas'
    });
  };

  const handleSaveEdit = async () => {
    try {
      const updatedPrayer = {
        name: editingPrayer.name,
        time: editingPrayer.time,
        unit: editingPrayer.unit,
        description: editingPrayer.description || ''
      };

      const response = await fetch(`${API_BASE_URL}/prayers/${editingPrayer.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedPrayer),
      });

      if (response.ok) {
        await loadPrayers();
        await loadStats();
        setEditingPrayer(null);
        toast({
          title: "Oração atualizada!",
          description: "As alterações foram salvas com sucesso.",
          duration: 3000,
        });
      } else {
        throw new Error('Erro ao atualizar oração');
      }
    } catch (error) {
      console.error('Erro ao salvar edição:', error);
      toast({
        title: "Erro ao atualizar",
        description: "Não foi possível salvar as alterações.",
        duration: 3000,
        variant: "destructive"
      });
    }
  };

  const handleDelete = async (prayerId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta oração?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/prayers/${prayerId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadPrayers();
        await loadStats();
        toast({
          title: "Oração excluída!",
          description: "A oração foi removida com sucesso.",
          duration: 3000,
        });
      } else {
        throw new Error('Erro ao excluir oração');
      }
    } catch (error) {
      console.error('Erro ao excluir oração:', error);
      toast({
        title: "Erro ao excluir",
        description: "Não foi possível excluir a oração.",
        duration: 3000,
        variant: "destructive"
      });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminAuth');
    localStorage.removeItem('adminAuthTime');
    onLogout();
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR');
    } catch {
      return 'Data inválida';
    }
  };

  const formatTime = (prayer) => {
    if (prayer.time_minutes) {
      return prayer.time_minutes >= 60 
        ? `${(prayer.time_minutes / 60).toFixed(1)}h`
        : `${prayer.time_minutes}min`;
    }
    return `${prayer.time}${prayer.unit === 'horas' ? 'h' : 'min'}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-100 rounded-lg">
              <Settings className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Painel Administrativo</h1>
              <p className="text-gray-600">Gerencie as orações do sistema</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => window.location.href = '/'}
              className="px-4 py-2 text-gray-600 hover:text-emerald-600 transition-colors duration-200"
            >
              ← Voltar ao sistema
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors duration-200"
            >
              <LogOut className="w-4 h-4" />
              Sair
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-emerald-100">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-emerald-600" />
              <h3 className="font-semibold text-gray-800">Total de Horas</h3>
            </div>
            <p className="text-3xl font-bold text-emerald-700">{stats.total_hours?.toFixed(1) || '0.0'}</p>
            <p className="text-sm text-gray-600">de 1000 horas</p>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-teal-100">
            <div className="flex items-center gap-3 mb-2">
              <Users className="w-5 h-5 text-teal-600" />
              <h3 className="font-semibold text-gray-800">Orações Registradas</h3>
            </div>
            <p className="text-3xl font-bold text-teal-700">{stats.total_entries || 0}</p>
            <p className="text-sm text-gray-600">orações registradas</p>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg border border-purple-100">
            <div className="flex items-center gap-3 mb-2">
              <Settings className="w-5 h-5 text-purple-600" />
              <h3 className="font-semibold text-gray-800">Progresso</h3>
            </div>
            <p className="text-3xl font-bold text-purple-700">
              {((stats.total_hours || 0) / 1000 * 100).toFixed(1)}%
            </p>
            <p className="text-sm text-gray-600">da meta alcançada</p>
          </div>
        </div>

        {/* Prayers Table */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Todas as Orações</h2>
              <button
                onClick={() => setShowAddForm(true)}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors duration-200"
              >
                <Plus className="w-4 h-4" />
                Nova Oração
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Nome
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div className="flex items-center gap-2">
                      <Timer className="w-4 h-4" />
                      Tempo
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Data/Hora
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4" />
                      Descrição
                    </div>
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {prayers.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                      Nenhuma oração registrada ainda.
                    </td>
                  </tr>
                ) : (
                  prayers.map((prayer) => (
                    <tr key={prayer.id} className="hover:bg-gray-50/50 transition-colors duration-150">
                      <td className="px-6 py-4 whitespace-nowrap">
                        {editingPrayer?.id === prayer.id ? (
                          <input
                            type="text"
                            value={editingPrayer.name}
                            onChange={(e) => setEditingPrayer({...editingPrayer, name: e.target.value})}
                            className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                          />
                        ) : (
                          <div className="text-sm font-medium text-gray-900">{prayer.name}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {editingPrayer?.id === prayer.id ? (
                          <div className="flex gap-2">
                            <input
                              type="number"
                              value={editingPrayer.time}
                              onChange={(e) => setEditingPrayer({...editingPrayer, time: parseInt(e.target.value)})}
                              className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            />
                            <select
                              value={editingPrayer.unit}
                              onChange={(e) => setEditingPrayer({...editingPrayer, unit: e.target.value})}
                              className="px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            >
                              <option value="minutos">min</option>
                              <option value="horas">h</option>
                            </select>
                          </div>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                            {formatTime(prayer)}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(prayer.datetime || prayer.timestamp)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                        {editingPrayer?.id === prayer.id ? (
                          <input
                            type="text"
                            value={editingPrayer.description || ''}
                            onChange={(e) => setEditingPrayer({...editingPrayer, description: e.target.value})}
                            className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                            placeholder="Descrição opcional"
                          />
                        ) : (
                          prayer.description || '-'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {editingPrayer?.id === prayer.id ? (
                          <div className="flex justify-end gap-2">
                            <button
                              onClick={handleSaveEdit}
                              className="text-emerald-600 hover:text-emerald-900 transition-colors duration-200"
                              title="Salvar"
                            >
                              <Save className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => setEditingPrayer(null)}
                              className="text-gray-600 hover:text-gray-900 transition-colors duration-200"
                              title="Cancelar"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <div className="flex justify-end gap-2">
                            <button
                              onClick={() => handleEdit(prayer)}
                              className="text-blue-600 hover:text-blue-900 transition-colors duration-200"
                              title="Editar"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(prayer.id)}
                              className="text-red-600 hover:text-red-900 transition-colors duration-200"
                              title="Excluir"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <Toaster />
    </div>
  );
};

export default AdminPanel;
