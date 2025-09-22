import React, { useState } from 'react';
import { Shield, ArrowLeft, Database } from 'lucide-react';

const AdminLogin = ({ onLogin, onBack }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Verificar senha
    if (password === 'PRCARLAO') {
      // NÃO salvar no localStorage - autenticação apenas na sessão
      onLogin();
    } else {
      setError('Palavra-chave incorreta');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center">
      <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-gray-200 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="bg-emerald-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <Shield className="w-8 h-8 text-emerald-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Acesso Administrativo</h1>
          <p className="text-gray-600 mb-2">Sistema EXCLUSIVAMENTE Supabase</p>
          <div className="flex items-center justify-center text-sm text-emerald-600">
            <Database className="w-4 h-4 mr-1" />
            <span>Dados 100% na nuvem</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Palavra-chave de Acesso
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
              placeholder="Digite a palavra-chave"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-600 text-white py-3 px-4 rounded-lg hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Verificando...
              </div>
            ) : (
              'Acessar Configurações'
            )}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <button
            onClick={onBack}
            className="w-full flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar ao sistema principal
          </button>
        </div>

        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            🔒 Acesso restrito apenas para administradores
          </p>
          <p className="text-xs text-gray-500 mt-1">
            📊 Todos os dados são gerenciados no Supabase
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;
