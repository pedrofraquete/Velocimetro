import React, { useState, useEffect } from 'react';
import { Clock, Heart, Users } from 'lucide-react';
import CountdownTimer from './CountdownTimer';
import SpeedometerChart from './SpeedometerChart';
import PrayerForm from './PrayerForm';
import PrayerHistory from './PrayerHistory';
import { useToast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/toaster';

const PrayerSystem = () => {
  const [totalHours, setTotalHours] = useState(0);
  const [prayers, setPrayers] = useState([]);
  const { toast } = useToast();

  // Load data from localStorage on component mount
  useEffect(() => {
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
    }
  }, []);

  // Save prayers to localStorage whenever prayers state changes
  useEffect(() => {
    if (prayers.length > 0) {
      localStorage.setItem('prayers', JSON.stringify(prayers));
    }
  }, [prayers]);

  const addPrayer = (prayer) => {
    const newPrayer = {
      ...prayer,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    };

    // Calculate hours to add
    const hoursToAdd = prayer.timeUnit === 'hours' ? prayer.time : prayer.time / 60;
    setTotalHours(prev => prev + hoursToAdd);

    // Add prayer to the beginning of the array and keep only last 10
    setPrayers(prev => [newPrayer, ...prev.slice(0, 9)]);

    // Show success toast
    toast({
      title: "Oração registrada!",
      description: `${prayer.time} ${prayer.timeUnit === 'hours' ? 'horas' : 'minutos'} adicionadas ao total.`,
      duration: 3000,
    });
  };

  const progressPercentage = Math.min((totalHours / 1000) * 100, 100);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50">
      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-6 sm:mb-12">
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
            <p className="text-2xl sm:text-3xl font-bold text-teal-700">{prayers.length}</p>
            <p className="text-xs sm:text-sm text-gray-600">pessoas oraram</p>
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