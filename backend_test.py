#!/usr/bin/env python3
"""
Testes para o sistema de orações - Backend API
Testa todos os endpoints e funcionalidades do sistema híbrido
"""

import requests
import json
import time
from datetime import datetime

class PrayerSystemTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, message, details=None):
        """Registrar resultado do teste"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_health_endpoint(self):
        """Testar endpoint de saúde do sistema"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar estrutura da resposta
                required_fields = ["status", "storage", "data_summary"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Health Endpoint", False, 
                                f"Campos obrigatórios ausentes: {missing_fields}", data)
                else:
                    storage_info = data.get("storage", {})
                    data_summary = data.get("data_summary", {})
                    
                    self.log_test("Health Endpoint", True, 
                                f"Sistema {data['status']} - Storage: {storage_info.get('primary_storage', 'unknown')}", 
                                {
                                    "total_prayers": data_summary.get("total_prayers", 0),
                                    "total_hours": data_summary.get("total_hours", 0),
                                    "progress": data_summary.get("progress", "0%"),
                                    "supabase_available": storage_info.get("supabase_available", False)
                                })
            else:
                self.log_test("Health Endpoint", False, 
                            f"Status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Erro de conexão: {str(e)}")
    
    def test_get_prayers(self):
        """Testar busca de todas as orações"""
        try:
            response = requests.get(f"{self.base_url}/api/prayers", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    prayers = data.get("data", [])
                    count = data.get("count", 0)
                    storage_info = data.get("storage_info", {})
                    
                    self.log_test("Get Prayers", True, 
                                f"Encontradas {count} orações - Storage: {storage_info.get('primary_storage', 'unknown')}", 
                                {
                                    "count": count,
                                    "sample_prayer": prayers[0] if prayers else None,
                                    "storage_type": storage_info.get("primary_storage")
                                })
                else:
                    self.log_test("Get Prayers", False, "Resposta indica falha", data)
            else:
                self.log_test("Get Prayers", False, 
                            f"Status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Get Prayers", False, f"Erro de conexão: {str(e)}")
    
    def test_get_stats(self):
        """Testar endpoint de estatísticas"""
        try:
            response = requests.get(f"{self.base_url}/api/prayers/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    stats = data.get("data", {})
                    required_stats = ["total_hours", "total_entries", "progress_percentage", "remaining_hours"]
                    missing_stats = [stat for stat in required_stats if stat not in stats]
                    
                    if missing_stats:
                        self.log_test("Prayer Stats", False, 
                                    f"Estatísticas ausentes: {missing_stats}", data)
                    else:
                        self.log_test("Prayer Stats", True, 
                                    f"Stats: {stats['total_entries']} orações, {stats['total_hours']}h ({stats['progress_percentage']}%)", 
                                    stats)
                else:
                    self.log_test("Prayer Stats", False, "Resposta indica falha", data)
            else:
                self.log_test("Prayer Stats", False, 
                            f"Status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Prayer Stats", False, f"Erro de conexão: {str(e)}")
    
    def test_add_prayer(self):
        """Testar adição de nova oração"""
        try:
            # Dados de teste realistas
            test_prayer = {
                "name": "Maria Silva",
                "time": 45,
                "unit": "minutos",
                "description": "Oração de intercessão pela família"
            }
            
            response = requests.post(f"{self.base_url}/api/prayers", 
                                   json=test_prayer, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    prayer_data = data.get("data", {})
                    self.log_test("Add Prayer", True, 
                                f"Oração adicionada: {test_prayer['name']} - {test_prayer['time']} {test_prayer['unit']}", 
                                {
                                    "added_prayer": prayer_data,
                                    "storage": prayer_data.get("storage", "unknown")
                                })
                else:
                    self.log_test("Add Prayer", False, "Resposta indica falha", data)
            else:
                self.log_test("Add Prayer", False, 
                            f"Status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Add Prayer", False, f"Erro de conexão: {str(e)}")
    
    def test_recent_prayers(self):
        """Testar endpoint de orações recentes"""
        try:
            response = requests.get(f"{self.base_url}/api/prayers/recent?limit=5", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    recent = data.get("data", [])
                    count = data.get("count", 0)
                    total = data.get("total", 0)
                    
                    self.log_test("Recent Prayers", True, 
                                f"Últimas {count} de {total} orações", 
                                {
                                    "recent_count": count,
                                    "total_prayers": total,
                                    "latest_prayer": recent[0] if recent else None
                                })
                else:
                    self.log_test("Recent Prayers", False, "Resposta indica falha", data)
            else:
                self.log_test("Recent Prayers", False, 
                            f"Status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Recent Prayers", False, f"Erro de conexão: {str(e)}")
    
    def test_supabase_sync(self):
        """Testar sincronização com Supabase"""
        try:
            response = requests.post(f"{self.base_url}/api/sync", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Esperamos que falhe porque Supabase não está configurado
                if not data.get("success"):
                    error_msg = data.get("message", "")
                    if "Supabase não disponível" in error_msg or "não configurado" in error_msg:
                        self.log_test("Supabase Sync", True, 
                                    "Corretamente detectou ausência do Supabase", 
                                    {"expected_behavior": "Supabase não configurado"})
                    else:
                        self.log_test("Supabase Sync", False, 
                                    f"Erro inesperado: {error_msg}", data)
                else:
                    # Se sucesso, Supabase está configurado
                    self.log_test("Supabase Sync", True, 
                                "Sincronização com Supabase funcionando", data)
            else:
                self.log_test("Supabase Sync", False, 
                            f"Status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Supabase Sync", False, f"Erro de conexão: {str(e)}")
    
    def test_backup_creation(self):
        """Testar criação de backup"""
        try:
            response = requests.post(f"{self.base_url}/api/backup", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    backup_info = data.get("data", {})
                    self.log_test("Backup Creation", True, 
                                f"Backup criado com {data.get('message', 'dados')}", 
                                backup_info)
                else:
                    self.log_test("Backup Creation", False, 
                                f"Falha no backup: {data.get('message', 'erro desconhecido')}", data)
            else:
                self.log_test("Backup Creation", False, 
                            f"Status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Backup Creation", False, f"Erro de conexão: {str(e)}")
    
    def test_root_endpoint(self):
        """Testar endpoint raiz"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["message", "version", "features", "storage_info"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Root Endpoint", False, 
                                f"Campos ausentes: {missing_fields}", data)
                else:
                    storage_info = data.get("storage_info", {})
                    self.log_test("Root Endpoint", True, 
                                f"API {data['version']} - Storage: {storage_info.get('primary_storage', 'unknown')}", 
                                {
                                    "version": data["version"],
                                    "features": data["features"],
                                    "storage_type": storage_info.get("primary_storage")
                                })
            else:
                self.log_test("Root Endpoint", False, 
                            f"Status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Erro de conexão: {str(e)}")
    
    def verify_local_data_file(self):
        """Verificar se o arquivo de dados locais existe e tem conteúdo"""
        try:
            import os
            local_file = "/app/backend/prayers_data.json"
            
            if os.path.exists(local_file):
                with open(local_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                prayers = data.get("prayers", [])
                self.log_test("Local Data File", True, 
                            f"Arquivo local encontrado com {len(prayers)} orações", 
                            {
                                "file_path": local_file,
                                "prayer_count": len(prayers),
                                "sample_names": [p.get("name") for p in prayers[:3]]
                            })
            else:
                self.log_test("Local Data File", False, 
                            f"Arquivo local não encontrado: {local_file}")
                
        except Exception as e:
            self.log_test("Local Data File", False, f"Erro ao verificar arquivo: {str(e)}")
    
    def run_all_tests(self):
        """Executar todos os testes"""
        print("🔄 Iniciando testes do sistema de orações...")
        print(f"🎯 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Testes de conectividade básica
        self.test_root_endpoint()
        self.test_health_endpoint()
        
        # Testes de dados
        self.verify_local_data_file()
        self.test_get_prayers()
        self.test_get_stats()
        self.test_recent_prayers()
        
        # Testes de funcionalidade
        self.test_add_prayer()
        
        # Testes de integração
        self.test_supabase_sync()
        self.test_backup_creation()
        
        # Resumo final
        print("=" * 60)
        print(f"📊 RESUMO DOS TESTES:")
        print(f"   Total: {self.total_tests}")
        print(f"   Passou: {self.passed_tests}")
        print(f"   Falhou: {self.total_tests - self.passed_tests}")
        print(f"   Taxa de sucesso: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        # Mostrar falhas
        failures = [r for r in self.test_results if "❌" in r["status"]]
        if failures:
            print(f"\n❌ TESTES QUE FALHARAM ({len(failures)}):")
            for failure in failures:
                print(f"   • {failure['test']}: {failure['message']}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "success_rate": (self.passed_tests/self.total_tests)*100,
            "results": self.test_results,
            "failures": failures
        }

if __name__ == "__main__":
    # Executar testes
    tester = PrayerSystemTester()
    results = tester.run_all_tests()
    
    # Salvar resultados
    with open("/app/test_results_backend.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/test_results_backend.json")