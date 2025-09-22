import React, { useState, useEffect } from 'react';
import AdminLogin from './AdminLogin';
import AdminPanel from './AdminPanel';

const AdminApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verificar se há autenticação válida no localStorage
    const checkAuth = () => {
      const authStatus = localStorage.getItem('adminAuth');
      const authTime = localStorage.getItem('adminAuthTime');
      
      if (authStatus === 'true' && authTime) {
        const timeElapsed = Date.now() - parseInt(authTime);
        const maxSessionTime = 24 * 60 * 60 * 1000; // 24 horas
        
        if (timeElapsed < maxSessionTime) {
          setIsAuthenticated(true);
        } else {
          // Sessão expirada
          localStorage.removeItem('adminAuth');
          localStorage.removeItem('adminAuthTime');
          setIsAuthenticated(false);
        }
      }
      
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const handleLogin = (success) => {
    setIsAuthenticated(success);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {isAuthenticated ? (
        <AdminPanel onLogout={handleLogout} />
      ) : (
        <AdminLogin onLogin={handleLogin} />
      )}
    </>
  );
};

export default AdminApp;
