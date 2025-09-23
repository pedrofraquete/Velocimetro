-- Schema para o Sistema de Orações - Igreja Videira
-- EXCLUSIVAMENTE Supabase - Sem armazenamento local

-- Criar tabela de orações
CREATE TABLE IF NOT EXISTS prayers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    time_minutes INTEGER NOT NULL CHECK (time_minutes > 0),
    unit VARCHAR(50) DEFAULT 'minutos' CHECK (unit IN ('minutos', 'horas')),
    datetime TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    description TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_prayers_datetime ON prayers(datetime DESC);
CREATE INDEX IF NOT EXISTS idx_prayers_name ON prayers(name);
CREATE INDEX IF NOT EXISTS idx_prayers_created_at ON prayers(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prayers_time_minutes ON prayers(time_minutes);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_prayers_updated_at 
    BEFORE UPDATE ON prayers 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) - Permitir acesso público para o sistema de orações
ALTER TABLE prayers ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura pública
CREATE POLICY IF NOT EXISTS "Allow public read access" ON prayers
    FOR SELECT USING (true);

-- Política para permitir inserção pública
CREATE POLICY IF NOT EXISTS "Allow public insert access" ON prayers
    FOR INSERT WITH CHECK (true);

-- Política para permitir atualização pública
CREATE POLICY IF NOT EXISTS "Allow public update access" ON prayers
    FOR UPDATE USING (true);

-- Política para permitir exclusão pública
CREATE POLICY IF NOT EXISTS "Allow public delete access" ON prayers
    FOR DELETE USING (true);

-- Função para calcular estatísticas das orações
CREATE OR REPLACE FUNCTION get_prayer_statistics()
RETURNS JSON AS $$
DECLARE
    total_prayers INTEGER;
    total_minutes INTEGER;
    total_hours NUMERIC;
    progress_percentage NUMERIC;
    remaining_hours NUMERIC;
    result JSON;
BEGIN
    -- Calcular estatísticas
    SELECT 
        COUNT(*),
        COALESCE(SUM(time_minutes), 0)
    INTO total_prayers, total_minutes
    FROM prayers;
    
    total_hours := total_minutes::NUMERIC / 60;
    progress_percentage := (total_hours / 1000) * 100;
    remaining_hours := GREATEST(0, 1000 - total_hours);
    
    -- Construir resultado JSON
    result := json_build_object(
        'total_prayers', total_prayers,
        'total_minutes', total_minutes,
        'total_hours', ROUND(total_hours, 2),
        'progress_percentage', ROUND(progress_percentage, 2),
        'remaining_hours', ROUND(remaining_hours, 2),
        'goal_hours', 1000,
        'last_updated', NOW()
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Função para obter orações recentes
CREATE OR REPLACE FUNCTION get_recent_prayers(limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    id INTEGER,
    name VARCHAR(255),
    time_minutes INTEGER,
    unit VARCHAR(50),
    datetime TIMESTAMP WITH TIME ZONE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.time_minutes,
        p.unit,
        p.datetime,
        p.description,
        p.created_at
    FROM prayers p
    ORDER BY p.datetime DESC, p.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- View para estatísticas em tempo real
CREATE OR REPLACE VIEW prayer_stats AS
SELECT 
    COUNT(*) as total_prayers,
    COALESCE(SUM(time_minutes), 0) as total_minutes,
    ROUND(COALESCE(SUM(time_minutes), 0)::NUMERIC / 60, 2) as total_hours,
    ROUND((COALESCE(SUM(time_minutes), 0)::NUMERIC / 60 / 1000) * 100, 2) as progress_percentage,
    ROUND(GREATEST(0, 1000 - (COALESCE(SUM(time_minutes), 0)::NUMERIC / 60)), 2) as remaining_hours,
    1000 as goal_hours
FROM prayers;

-- Inserir dados de exemplo (opcional - remover em produção)
-- INSERT INTO prayers (name, time_minutes, unit, description) VALUES
-- ('João Silva', 30, 'minutos', 'Oração matinal'),
-- ('Maria Santos', 60, 'minutos', 'Oração de intercessão'),
-- ('Pedro Costa', 45, 'minutos', 'Oração de gratidão');

-- Comentários para documentação
COMMENT ON TABLE prayers IS 'Tabela principal para armazenar registros de orações do sistema Igreja Videira';
COMMENT ON COLUMN prayers.id IS 'Identificador único da oração';
COMMENT ON COLUMN prayers.name IS 'Nome da pessoa que orou';
COMMENT ON COLUMN prayers.time_minutes IS 'Tempo de oração em minutos';
COMMENT ON COLUMN prayers.unit IS 'Unidade de tempo (minutos ou horas)';
COMMENT ON COLUMN prayers.datetime IS 'Data e hora da oração';
COMMENT ON COLUMN prayers.description IS 'Descrição ou motivo da oração';
COMMENT ON COLUMN prayers.created_at IS 'Data de criação do registro';
COMMENT ON COLUMN prayers.updated_at IS 'Data da última atualização do registro';

COMMENT ON FUNCTION get_prayer_statistics() IS 'Função para calcular estatísticas completas das orações';
COMMENT ON FUNCTION get_recent_prayers(INTEGER) IS 'Função para obter orações mais recentes';
COMMENT ON VIEW prayer_stats IS 'View com estatísticas em tempo real das orações';

-- Verificação final
SELECT 'Schema criado com sucesso!' as status,
       'Tabela prayers configurada' as table_status,
       'Políticas RLS ativadas' as security_status,
       'Funções e views criadas' as functions_status;
