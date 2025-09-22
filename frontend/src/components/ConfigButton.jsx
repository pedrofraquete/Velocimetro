import React from 'react';
import { useNavigate } from 'react-router-dom';

const ConfigButton = () => {
  const navigate = useNavigate();

  const handleClick = () => {
    try {
      navigate('/admin');
    } catch (error) {
      // Fallback para navegação direta
      window.location.href = '/admin';
    }
  };

  return (
    <div className="absolute top-0 right-0 sm:right-4 z-10">
      <button
        onClick={handleClick}
        className="p-2 sm:p-3 bg-white/70 backdrop-blur-sm rounded-full shadow-lg border border-gray-200 hover:bg-white/90 hover:scale-110 transition-all duration-300 group"
        title="Configurações"
        aria-label="Abrir painel administrativo"
        type="button"
      >
        <svg
          className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600 group-hover:text-gray-800 group-hover:rotate-90 transition-all duration-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
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
  );
};

export default ConfigButton;