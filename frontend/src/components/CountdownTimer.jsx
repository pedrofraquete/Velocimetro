import React, { useState, useEffect } from 'react';
import { Calendar, Clock } from 'lucide-react';

const CountdownTimer = () => {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  });

  useEffect(() => {
    // Target date: October 5, 2025 at 10:00 AM (Brazil timezone)
    const targetDate = new Date('2025-10-05T10:00:00-03:00');

    const updateTimer = () => {
      const now = new Date();
      const difference = targetDate.getTime() - now.getTime();

      if (difference > 0) {
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);

        setTimeLeft({ days, hours, minutes, seconds });
      } else {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
      }
    };

    // Update immediately
    updateTimer();

    // Update every second
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-gray-200">
      <div className="text-center mb-6">
        <div className="inline-flex items-center gap-2 mb-2">
          <Calendar className="w-6 h-6 text-emerald-600" />
          <h2 className="text-2xl font-bold text-gray-800">Tempo Restante</h2>
        </div>
        <p className="text-gray-600">Para nossa meta de 1000 horas</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white rounded-xl p-4 shadow-lg">
            <div className="text-3xl md:text-4xl font-bold mb-1">{timeLeft.days}</div>
            <div className="text-sm opacity-90">Dias</div>
          </div>
        </div>
        
        <div className="text-center">
          <div className="bg-gradient-to-br from-teal-500 to-cyan-600 text-white rounded-xl p-4 shadow-lg">
            <div className="text-3xl md:text-4xl font-bold mb-1">{timeLeft.hours}</div>
            <div className="text-sm opacity-90">Horas</div>
          </div>
        </div>
        
        <div className="text-center">
          <div className="bg-gradient-to-br from-cyan-500 to-blue-600 text-white rounded-xl p-4 shadow-lg">
            <div className="text-3xl md:text-4xl font-bold mb-1">{timeLeft.minutes}</div>
            <div className="text-sm opacity-90">Minutos</div>
          </div>
        </div>
        
        <div className="text-center">
          <div className="bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-xl p-4 shadow-lg">
            <div className="text-3xl md:text-4xl font-bold mb-1">{timeLeft.seconds}</div>
            <div className="text-sm opacity-90">Segundos</div>
          </div>
        </div>
      </div>

      <div className="mt-6 text-center">
        <div className="inline-flex items-center gap-2 text-gray-600">
          <Clock className="w-4 h-4" />
          <span className="text-sm">Atualizado em tempo real</span>
        </div>
      </div>
    </div>
  );
};

export default CountdownTimer;