import React, { useState, useEffect } from 'react';
import { Clock, Heart, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import CountdownTimer from './CountdownTimer';
import SpeedometerChart from './SpeedometerChart';
import PrayerForm from './PrayerForm';
import PrayerHistory from './PrayerHistory';
import { useToast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/toaster';

const PrayerSystem = () => {
  const [totalHours, setTotalHours] = useState(0);
  const [prayers, setPrayers] = useState([]);
  const [totalEntries, setTotalEntries] = useState(0);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const navigate = useNavigate();

  // API base URL
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 
    (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8001/api');

  // Load data from API on component mount
  useEffect(() => {
    loadPrayerStats();
    loadPrayerHistory();
  }, []);

  const loadPrayerStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers/stats`);
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data) {
          setTotalHours(result.data.total_hours || 0);
          setTotalEntries(result.data.total_entries || 0);
        } else {
          // Fallback se não houver dados
          loadFromLocalStorage();
        }
      } else {
        // Fallback para localStorage se API não estiver disponível
        loadFromLocalStorage();
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
      loadFromLocalStorage();
    } finally {
      setLoading(false);
    }
  };

  const loadPrayerHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/prayers`);
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data) {
          // Converter formato da API para formato do frontend
          const formattedPrayers = result.data.map((prayer, index) => ({
            id: `api-${index}`,
            name: prayer.name,
            time: prayer.time,
            timeUnit: prayer.unit === 'horas' ? 'hours' : 'minutes',
            timestamp: prayer.datetime || prayer.created_at || new Date().toISOString()
          }));
          setPrayers(formattedPrayers.slice(0, 10)); // Mostrar apenas os últimos 10
        }
      }
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    }
  };

  const loadFromLocalStorage = () => {
    const savedPrayers = localStorage.getItem('prayers');
    if (savedPrayers) {
      const parsedPrayers = JSON.parse(savedPrayers);
      setPrayers(parsedPrayers);
      
      // Calculate total hours from saved prayers
      const total = parsedPrayers.reduce((acc, prayer) => {
        const hours = prayer.timeUnit === 'hours' ? prayer.time : prayer.time / 60;
        return acc + hours;
      }, 0);
      setTotalHours(total);
      setTotalEntries(parsedPrayers.length);
    }
  };

  const addPrayer = async (prayer) => {
    try {
      // Preparar dados para API
      const prayerData = {
        name: prayer.name,
        time: prayer.time,
        unit: prayer.timeUnit === 'hours' ? 'horas' : 'minutos',
        description: prayer.description || ''
      };

      // Enviar para API
      const response = await fetch(`${API_BASE_URL}/prayers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(prayerData),
      });

      if (response.ok) {
        const result = await response.json();
        
        // Recarregar dados da API
        await loadPrayerStats();
        await loadPrayerHistory();

        // Show success toast
        toast({
          title: "Oração registrada!",
          description: `${prayer.time} ${prayer.timeUnit === 'hours' ? 'horas' : 'minutos'} adicionadas ao total.`,
          duration: 3000,
        });
      } else {
        throw new Error('Erro ao registrar oração na API');
      }
    } catch (error) {
      console.error('Erro ao adicionar oração:', error);
      
      // Fallback para localStorage
      const newPrayer = {
        ...prayer,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      };

      // Calculate hours to add
      const hoursToAdd = prayer.timeUnit === 'hours' ? prayer.time : prayer.time / 60;
      setTotalHours(prev => prev + hoursToAdd);
      setTotalEntries(prev => prev + 1);

      // Add prayer to the beginning of the array and keep only last 10
      setPrayers(prev => [newPrayer, ...prev.slice(0, 9)]);

      // Save to localStorage as backup
      const updatedPrayers = [newPrayer, ...prayers.slice(0, 9)];
      localStorage.setItem('prayers', JSON.stringify(updatedPrayers));

      // Show warning toast
      toast({
        title: "Oração registrada localmente",
        description: `${prayer.time} ${prayer.timeUnit === 'hours' ? 'horas' : 'minutos'} adicionadas. Dados salvos localmente.`,
        duration: 3000,
        variant: "destructive"
      });
    }
  };

  const progressPercentage = Math.min((totalHours / 1000) * 100, 100);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50">
      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-6 sm:mb-12 relative">
          {/* Ícone de Configuração */}
          <div className="absolute top-0 right-0 sm:right-4 z-10">
            <button
              onClick={() => navigate('/admin')}
              className="p-2 sm:p-3 bg-white/70 backdrop-blur-sm rounded-full shadow-lg border border-gray-200 hover:bg-white/90 hover:scale-110 transition-all duration-300 group"
              title="Configurações"
              aria-label="Abrir painel administrativo"
            >
              <svg
                className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600 group-hover:text-gray-800 group-hover:rotate-90 transition-all duration-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </button>
          </div>
          
          {/* Logo da Igreja Videira */}
          <div className="flex justify-center mb-4 sm:mb-6">
            <img 
              src="/logo-igreja-videira.png" 
              alt="Logo Igreja Videira" 
              className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 rounded-full shadow-lg border-2 border-white/50 hover:scale-105 transition-transform duration-300"
            />
          </div>
          
          <div className="flex items-center justify-center gap-2 sm:gap-3 mb-3 sm:mb-4 flex-wrap">
            <Heart className="w-6 h-6 sm:w-8 sm:h-8 text-emerald-600" />
            <h1 className="text-2xl sm:text-4xl md:text-5xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-purple-600 bg-clip-text text-transparent text-center leading-tight">
              1000 Horas de Oração
            </h1>
            <Heart className="w-6 h-6 sm:w-8 sm:h-8 text-purple-600" />
          </div>
          <p className="text-base sm:text-lg text-gray-700 mb-1 sm:mb-2">Igreja Videira SJC</p>
          <p className="text-xs sm:text-sm text-gray-600">Meta: 05 de Outubro de 2025 às 10h</p>
        </div>

        {/* Progress Summary */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-6 mb-6 sm:mb-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 sm:p-6 shadow-lg border border-emerald-100">
            <div className="flex items-center gap-2 sm:gap-3 mb-2">
              <Clock className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-600" />
              <h3 className="font-semibold text-gray-800 text-sm sm:text-base">Total de Horas</h3>
            </div>
            <p className="text-2xl sm:text-3xl font-bold text-emerald-700">{totalHours.toFixed(1)}</p>
            <p className="text-xs sm:text-sm text-gray-600">de 1000 horas</p>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 sm:p-6 shadow-lg border border-teal-100">
            <div className="flex items-center gap-2 sm:gap-3 mb-2">
              <Users className="w-4 h-4 sm:w-5 sm:h-5 text-teal-600" />
              <h3 className="font-semibold text-gray-800 text-sm sm:text-base">Orações Registradas</h3>
            </div>
            <p className="text-2xl sm:text-3xl font-bold text-teal-700">{totalEntries}</p>
            <p className="text-xs sm:text-sm text-gray-600">orações registradas</p>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 sm:p-6 shadow-lg border border-purple-100">
            <div className="flex items-center gap-2 sm:gap-3 mb-2">
              <Heart className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
              <h3 className="font-semibold text-gray-800 text-sm sm:text-base">Progresso</h3>
            </div>
            <p className="text-2xl sm:text-3xl font-bold text-purple-700">{progressPercentage.toFixed(1)}%</p>
            <p className="text-xs sm:text-sm text-gray-600">da meta alcançada</p>
          </div>
        </div>

        {/* Countdown Timer */}
        <div className="mb-6 sm:mb-8">
          <CountdownTimer />
        </div>

        {/* Speedometer */}
        <div className="mb-6 sm:mb-8">
          <SpeedometerChart totalHours={totalHours} />
        </div>

        {/* Prayer Form and History */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 sm:gap-8">
          <PrayerForm onAddPrayer={addPrayer} />
          <PrayerHistory prayers={prayers} />
        </div>
      </div>
      <Toaster />
    </div>
  );
};

export default PrayerSystem;