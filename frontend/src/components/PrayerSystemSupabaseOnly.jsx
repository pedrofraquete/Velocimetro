import React, { useState, useEffect } from 'react';
import { Clock, Heart, Users, Settings } from 'lucide-react';
import CountdownTimer from './CountdownTimer';
import SpeedometerChart from './SpeedometerChart';
import PrayerForm from './PrayerForm';
import PrayerHistory from './PrayerHistory';
import ConfigButton from './ConfigButton';
import { useToast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/toaster';

const PrayerSystem = () => {
  const [totalHours, setTotalHours] = useState(0);
  const [prayers, setPrayers] = useState([]);
  const [totalEntries, setTotalEntries] = useState(0);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  // API base URL - EXCLUSIVAMENTE backend
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 
    (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000/api');

  // Load data from API on component mount
  useEffect(() => {
    loadPrayerStats();
    loadPrayerHistory();
  }, []);

  const loadPrayerStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers/stats`);
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      const result = await response.json();
      if (result.success && result.data) {
        setTotalHours(result.data.total_hours || 0);
        setTotalEntries(result.data.total_entries || 0);
        
        toast({
          title: "✅ Dados carregados do Supabase",
          description: `${result.data.total_entries} orações, ${result.data.total_hours}h totais`,
        });
      } else {
        throw new Error('Dados inválidos recebidos do servidor');
      }
    } catch (error) {
      console.error('❌ Erro ao carregar estatísticas:', error);
      toast({
        title: "❌ Erro ao carregar dados",
        description: "Não foi possível conectar ao Supabase. Verifique sua conexão.",
        variant: "destructive",
      });
      
      // NÃO usar localStorage - sistema deve falhar se Supabase não funcionar
      setTotalHours(0);
      setTotalEntries(0);
    } finally {
      setLoading(false);
    }
  };

  const loadPrayerHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers`);
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      const result = await response.json();
      if (result.success && result.data) {
        setPrayers(result.data || []);
      } else {
        throw new Error('Dados inválidos recebidos do servidor');
      }
    } catch (error) {
      console.error('❌ Erro ao carregar histórico:', error);
      // NÃO usar localStorage - sistema deve falhar se Supabase não funcionar
      setPrayers([]);
    }
  };

  const addPrayer = async (name, timeValue, unit, description = '') => {
    try {
      // Converter para minutos
      const timeInMinutes = unit === 'horas' ? timeValue * 60 : timeValue;
      
      const response = await fetch(`${API_BASE_URL}/prayers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: name,
          time_minutes: timeInMinutes,
          description: description,
          unit: unit
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        // Recarregar dados do Supabase
        await loadPrayerStats();
        await loadPrayerHistory();
        
        toast({
          title: "✅ Oração registrada no Supabase!",
          description: `${name} - ${timeValue} ${unit}`,
        });
        
        return true;
      } else {
        throw new Error(result.message || 'Erro ao salvar oração');
      }
    } catch (error) {
      console.error('❌ Erro ao adicionar oração:', error);
      toast({
        title: "❌ Erro ao registrar oração",
        description: "Não foi possível salvar no Supabase. Tente novamente.",
        variant: "destructive",
      });
      return false;
    }
  };

  // Calcular progresso
  const progressPercentage = totalHours > 0 ? (totalHours / 1000) * 100 : 0;
  const remainingHours = Math.max(0, 1000 - totalHours);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      <div className="container mx-auto px-4 py-8 relative">
        {/* Config Button */}
        <ConfigButton />
        
        {/* Header com Logo */}
        <div className="text-center mb-8">
          <div className="mb-6">
            <img 
              src="/logo-igreja-videira.png" 
              alt="Logo Igreja Videira" 
              className="w-24 h-24 mx-auto rounded-full shadow-lg hover:scale-105 transition-transform duration-300"
            />
          </div>
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-emerald-600 to-purple-600 bg-clip-text text-transparent mb-2">
            💚 1000 Horas de Oração 💜
          </h1>
          <p className="text-xl text-gray-600 mb-2">Igreja Videira SJC</p>
          <p className="text-lg text-gray-500">Meta: 05 de Outubro de 2025 às 10h</p>
          <p className="text-sm text-emerald-600 font-semibold mt-2">
            📊 Dados salvos EXCLUSIVAMENTE no Supabase
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-emerald-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Total de Horas</p>
                <p className="text-3xl font-bold text-emerald-600">{totalHours}</p>
                <p className="text-xs text-gray-500">de 1000 horas</p>
              </div>
              <Clock className="w-8 h-8 text-emerald-600" />
            </div>
          </div>

          <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-teal-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Orações Registradas</p>
                <p className="text-3xl font-bold text-teal-600">{totalEntries}</p>
                <p className="text-xs text-gray-500">orações registradas</p>
              </div>
              <Users className="w-8 h-8 text-teal-600" />
            </div>
          </div>

          <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Progresso</p>
                <p className="text-3xl font-bold text-purple-600">{progressPercentage.toFixed(1)}%</p>
                <p className="text-xs text-gray-500">da meta alcançada</p>
              </div>
              <Heart className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Countdown Timer */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200 mb-8">
          <div className="flex items-center justify-center mb-4">
            <Clock className="w-6 h-6 text-emerald-600 mr-2" />
            <h2 className="text-2xl font-bold text-gray-800">⏰ Tempo Restante</h2>
          </div>
          <p className="text-center text-gray-600 mb-4">Para nossa meta de 1000 horas</p>
          <CountdownTimer targetDate="2025-10-05T10:00:00" />
        </div>

        {/* Speedometer */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200 mb-8">
          <div className="flex items-center justify-center mb-4">
            <Heart className="w-6 h-6 text-purple-600 mr-2" />
            <h2 className="text-2xl font-bold text-gray-800">📊 Progresso das Orações</h2>
          </div>
          <SpeedometerChart currentHours={totalHours} maxHours={1000} />
        </div>

        {/* Prayer Form */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200 mb-8">
          <div className="flex items-center justify-center mb-4">
            <Heart className="w-6 h-6 text-emerald-600 mr-2" />
            <h2 className="text-2xl font-bold text-gray-800">🙏 Registrar Oração</h2>
          </div>
          <PrayerForm onAddPrayer={addPrayer} />
        </div>

        {/* Prayer History */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200">
          <div className="flex items-center justify-center mb-4">
            <Users className="w-6 h-6 text-teal-600 mr-2" />
            <h2 className="text-2xl font-bold text-gray-800">📋 Últimas Orações</h2>
          </div>
          <p className="text-center text-gray-600 mb-4">
            Histórico das {Math.min(prayers.length, 10)} últimas orações registradas
          </p>
          <PrayerHistory prayers={prayers.slice(0, 10)} />
        </div>
      </div>
      
      <Toaster />
    </div>
  );
};

export default PrayerSystem;
