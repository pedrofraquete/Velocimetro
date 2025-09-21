import React from 'react';
import { History, Clock, User, MessageCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const PrayerHistory = ({ prayers }) => {
  const formatTimeAgo = (timestamp) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { 
        addSuffix: true, 
        locale: ptBR 
      });
    } catch (error) {
      return 'há alguns momentos';
    }
  };

  if (prayers.length === 0) {
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-gray-200">
        <div className="mb-6">
          <div className="inline-flex items-center gap-2 mb-2">
            <History className="w-6 h-6 text-teal-600" />
            <h2 className="text-2xl font-bold text-gray-800">Últimas Orações</h2>
          </div>
          <p className="text-gray-600">Histórico das 10 últimas orações registradas</p>
        </div>
        
        <div className="text-center py-12">
          <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">Nenhuma oração registrada ainda</p>
          <p className="text-gray-400 text-sm mt-2">Seja o primeiro a contribuir com nossa meta!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-gray-200">
      <div className="mb-6">
        <div className="inline-flex items-center gap-2 mb-2">
          <History className="w-6 h-6 text-teal-600" />
          <h2 className="text-2xl font-bold text-gray-800">Últimas Orações</h2>
        </div>
        <p className="text-gray-600">Histórico das {prayers.length} últimas orações registradas</p>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {prayers.map((prayer, index) => (
          <div 
            key={prayer.id}
            className={`p-4 rounded-lg border transition-all duration-300 hover:shadow-md ${
              index === 0 
                ? 'bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200 animate-pulse' 
                : 'bg-gray-50 border-gray-200'
            }`}
            style={{
              animation: index === 0 ? 'fadeInDown 0.5s ease-out' : 'none'
            }}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-gray-600" />
                <span className="font-semibold text-gray-800">{prayer.name}</span>
                {index === 0 && (
                  <span className="bg-emerald-100 text-emerald-800 text-xs px-2 py-1 rounded-full">
                    Nova!
                  </span>
                )}
              </div>
              
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock className="w-3 h-3" />
                <span>
                  {prayer.time} {prayer.timeUnit === 'hours' ? 'h' : 'min'}
                </span>
              </div>
            </div>

            {prayer.description && (
              <div className="mb-2">
                <div className="flex items-start gap-2">
                  <MessageCircle className="w-3 h-3 text-gray-500 mt-1 flex-shrink-0" />
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {prayer.description}
                  </p>
                </div>
              </div>
            )}

            <div className="text-xs text-gray-500">
              {formatTimeAgo(prayer.timestamp)}
            </div>
          </div>
        ))}
      </div>

      {prayers.length >= 10 && (
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Mostrando as 10 orações mais recentes
          </p>
        </div>
      )}
    </div>
  );
};

export default PrayerHistory;