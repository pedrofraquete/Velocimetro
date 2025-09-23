# Backend - Sistema de Orações Igreja Videira

## Configuração EXCLUSIVAMENTE Supabase

Este backend foi configurado para funcionar **EXCLUSIVAMENTE** com o Supabase. Não há armazenamento local, Google Sheets ou qualquer outro sistema de persistência.

### ✅ Características

- **100% Supabase**: Todos os dados são salvos e lidos apenas do Supabase
- **Sem fallback local**: Sistema falha se Supabase não estiver disponível
- **API REST completa**: Endpoints para CRUD de orações
- **Estatísticas em tempo real**: Cálculo automático de progresso
- **Validação robusta**: Pydantic para validação de dados

### 🚀 Configuração Rápida

1. **Configure o Supabase**:
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env
   
   # Edite .env com suas credenciais Supabase
   nano .env
   ```

2. **Execute o schema SQL**:
   - Acesse o painel do Supabase
   - Vá para SQL Editor
   - Execute o conteúdo de `supabase_schema.sql`

3. **Instale dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o servidor**:
   ```bash
   python server.py
   ```

### 📋 Variáveis de Ambiente Obrigatórias

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### 🔗 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Status do servidor |
| GET | `/api/health` | Verificação de saúde |
| POST | `/api/prayers` | Adicionar oração |
| GET | `/api/prayers` | Listar todas as orações |
| GET | `/api/prayers/stats` | Estatísticas das orações |
| PUT | `/api/prayers/{id}` | Atualizar oração |
| DELETE | `/api/prayers/{id}` | Excluir oração |
| GET | `/api/storage/info` | Informações do armazenamento |

### 📊 Exemplo de Uso

```python
import requests

# Adicionar oração
response = requests.post("http://localhost:8000/api/prayers", json={
    "name": "João Silva",
    "time_minutes": 30,
    "description": "Oração matinal",
    "unit": "minutos"
})

# Obter estatísticas
stats = requests.get("http://localhost:8000/api/prayers/stats")
print(stats.json())
```

### 🗄️ Schema do Banco

A tabela `prayers` contém:
- `id`: Identificador único
- `name`: Nome da pessoa
- `time_minutes`: Tempo em minutos
- `unit`: Unidade (minutos/horas)
- `datetime`: Data e hora da oração
- `description`: Descrição opcional
- `created_at`: Data de criação
- `updated_at`: Data de atualização

### 🚫 Removido do Sistema

- ❌ Armazenamento local (JSON, CSV)
- ❌ Google Sheets integration
- ❌ MongoDB/PyMongo
- ❌ Sistema híbrido
- ❌ Fallback para arquivos locais
- ❌ Backup automático local

### 🔧 Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements.txt

# Executar testes
pytest

# Formatar código
black .
isort .

# Linting
flake8 .
mypy .
```

### 📝 Logs

O sistema exibe logs detalhados:
- ✅ Operações bem-sucedidas
- ❌ Erros e falhas
- 📊 Estatísticas de uso
- 🔄 Status de conexão

### 🆘 Solução de Problemas

**Erro: "Não foi possível inicializar Supabase"**
- Verifique se SUPABASE_URL e SUPABASE_KEY estão configurados
- Confirme se o projeto Supabase está ativo
- Execute o schema SQL no Supabase

**Erro: "Tabela 'prayers' não encontrada"**
- Execute o arquivo `supabase_schema.sql` no SQL Editor do Supabase
- Verifique se as políticas RLS estão ativadas

**Erro de CORS**
- O servidor está configurado para aceitar todas as origens
- Verifique se o frontend está fazendo requisições para a URL correta

### 📞 Suporte

Para problemas específicos do Supabase, consulte:
- [Documentação Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python)

---
**Versão**: 2.0 - Exclusivamente Supabase  
**Última atualização**: Setembro 2025
