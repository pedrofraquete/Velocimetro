import React, { useState } from 'react';
import AdminLogin from './AdminLoginSupabaseOnly';
import AdminPanel from './AdminPanelSupabaseOnly';

const AdminApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    // NÃO usar localStorage - autenticação apenas na sessão atual
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    // NÃO usar localStorage - apenas limpar estado da sessão
    setIsAuthenticated(false);
  };

  const handleBack = () => {
    // Voltar para a página principal
    window.location.href = '/';
  };

  if (isAuthenticated) {
    return <AdminPanel onLogout={handleLogout} />;
  }

  return (
    <AdminLogin 
      onLogin={handleLogin} 
      onBack={handleBack}
    />
  );
};

export default AdminApp;
