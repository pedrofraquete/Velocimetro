# 💚 Sistema de Orações - Igreja Videira SJC 💜

Sistema web para acompanhar o progresso das **1000 Horas de Oração** da Igreja Videira São José dos Campos, com meta para **05 de Outubro de 2025 às 10h**.

## ✨ Características

- **🎯 Meta Clara**: Acompanhamento visual do progresso para 1000 horas
- **⏰ Contador Regressivo**: Tempo restante até a data meta
- **📊 Velocímetro Visual**: Gráfico interativo do progresso
- **📱 Responsivo**: Funciona perfeitamente em mobile e desktop
- **☁️ 100% Supabase**: Todos os dados salvos exclusivamente na nuvem
- **🚫 Sem Armazenamento Local**: Sistema falha se Supabase não estiver disponível

## 🚀 Tecnologias

### Frontend
- **React 19.0.0** - Interface moderna e responsiva
- **Tailwind CSS** - Estilização utilitária
- **Radix UI** - Componentes acessíveis
- **Canvas API** - Velocímetro customizado
- **React Router** - Navegação SPA

### Backend
- **FastAPI** - API REST moderna e rápida
- **Supabase** - Banco de dados PostgreSQL na nuvem
- **Pydantic** - Validação de dados
- **Python 3.11+** - Linguagem backend

### Deploy
- **Vercel** - Hospedagem frontend e backend
- **Supabase Cloud** - Banco de dados gerenciado

## 📦 Estrutura do Projeto

```
Velocimetro/
├── frontend/                 # Aplicação React
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   └── hooks/           # Hooks customizados
│   ├── public/              # Arquivos estáticos
│   └── package.json         # Dependências frontend
├── backend/                 # API FastAPI
│   ├── server.py           # Servidor principal
│   ├── supabase_client.py  # Cliente Supabase
│   ├── supabase_storage.py # Camada de armazenamento
│   ├── supabase_schema.sql # Schema do banco
│   └── requirements.txt    # Dependências backend
├── vercel.json             # Configuração de deploy
└── README.md               # Este arquivo
```

## 🛠️ Configuração Local

### 1. Clone o Repositório
```bash
git clone https://github.com/pedrofraquete/Velocimetro.git
cd Velocimetro
```

### 2. Configure o Supabase

1. Crie um projeto no [Supabase](https://supabase.com)
2. Execute o SQL em `backend/supabase_schema.sql` no SQL Editor
3. Copie as credenciais do projeto

### 3. Configure o Backend
```bash
cd backend
cp .env.example .env
# Edite .env com suas credenciais Supabase
pip install -r requirements.txt
python server.py
```

### 4. Configure o Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

## 🌐 Deploy no Vercel

### 1. Configurar Variáveis de Ambiente

No painel do Vercel, adicione:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### 2. Deploy Automático

O projeto está configurado para deploy automático via GitHub. Cada push na branch `main` dispara um novo deploy.

## 📊 Funcionalidades

### ✅ Implementado

- [x] **Interface Responsiva** - Design adaptável para todos os dispositivos
- [x] **Registro de Orações** - Formulário para adicionar tempo de oração
- [x] **Estatísticas em Tempo Real** - Cálculo automático do progresso
- [x] **Velocímetro Visual** - Gráfico canvas customizado
- [x] **Contador Regressivo** - Tempo restante até a meta
- [x] **Histórico de Orações** - Lista das últimas orações registradas
- [x] **API REST Completa** - CRUD completo de orações
- [x] **Validação de Dados** - Validação robusta no frontend e backend
- [x] **Deploy Automático** - CI/CD via Vercel

## 🗄️ Schema do Banco

```sql
CREATE TABLE prayers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    time_minutes INTEGER NOT NULL,
    unit VARCHAR(50) DEFAULT 'minutos',
    datetime TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔗 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/health` | Status do sistema |
| POST | `/api/prayers` | Adicionar oração |
| GET | `/api/prayers` | Listar orações |
| GET | `/api/prayers/stats` | Estatísticas |
| PUT | `/api/prayers/{id}` | Atualizar oração |
| DELETE | `/api/prayers/{id}` | Excluir oração |

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é licenciado sob a MIT License.

## 🙏 Agradecimentos

- **Igreja Videira SJC** - Pela iniciativa das 1000 Horas de Oração
- **Comunidade React** - Pelas ferramentas incríveis
- **Supabase** - Pela plataforma de banco de dados
- **Vercel** - Pela hospedagem gratuita

---

**Desenvolvido com ❤️ para a Igreja Videira São José dos Campos**

**Meta**: 1000 Horas de Oração até 05/10/2025 às 10h 🎯
