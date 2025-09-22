#!/usr/bin/env python3
"""
Testes focados na integração com Supabase
Verifica se as orações estão sendo salvas corretamente no Supabase
"""

import requests
import json
import time
from datetime import datetime

class SupabaseFocusedTester:
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
            print(f"   Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
    
    def test_supabase_status(self):
        """1. Verificar status atual do Supabase"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                storage_info = data.get("storage", {})
                
                # Verificar se Supabase está como primary_storage
                primary_storage = storage_info.get("primary_storage")
                supabase_available = storage_info.get("supabase_available", False)
                
                if primary_storage == "supabase" and supabase_available:
                    self.log_test("Supabase Status", True, 
                                f"Supabase configurado como armazenamento primário", 
                                {
                                    "primary_storage": primary_storage,
                                    "supabase_available": supabase_available,
                                    "storage_info": storage_info
                                })
                else:
                    self.log_test("Supabase Status", False, 
                                f"Supabase não está como primário: {primary_storage}", 
                                storage_info)
            else:
                self.log_test("Supabase Status", False, 
                            f"Erro no health check: {response.status_code}")
                
        except Exception as e:
            self.log_test("Supabase Status", False, f"Erro de conexão: {str(e)}")
    
    def test_prayer_saving_supabase(self):
        """2. Testar salvamento de orações no Supabase"""
        test_prayers = [
            {
                "name": "João Santos",
                "time": 60,
                "unit": "minutos",
                "description": "Oração pela igreja local"
            },
            {
                "name": "Ana Costa",
                "time": 30,
                "unit": "minutos", 
                "description": "Intercessão pelos missionários"
            },
            {
                "name": "Carlos Oliveira",
                "time": 90,
                "unit": "minutos",
                "description": "Oração de gratidão e louvor"
            }
        ]
        
        added_prayers = []
        
        for i, prayer in enumerate(test_prayers):
            try:
                response = requests.post(f"{self.base_url}/api/prayers", 
                                       json=prayer, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        prayer_data = data.get("data", {})
                        
                        # Verificar se tem ID do Supabase (sequencial)
                        prayer_id = prayer_data.get("id")
                        if prayer_id and isinstance(prayer_id, int):
                            added_prayers.append({
                                "id": prayer_id,
                                "name": prayer["name"],
                                "response_data": prayer_data
                            })
                            
                            self.log_test(f"Add Prayer {i+1}", True, 
                                        f"Oração '{prayer['name']}' salva com ID {prayer_id}", 
                                        {
                                            "prayer_id": prayer_id,
                                            "name": prayer["name"],
                                            "time": prayer["time"],
                                            "has_supabase_id": True
                                        })
                        else:
                            self.log_test(f"Add Prayer {i+1}", False, 
                                        f"Oração salva mas sem ID do Supabase", 
                                        prayer_data)
                    else:
                        self.log_test(f"Add Prayer {i+1}", False, 
                                    f"Falha ao salvar: {data.get('message', 'erro desconhecido')}")
                else:
                    self.log_test(f"Add Prayer {i+1}", False, 
                                f"Status code {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Add Prayer {i+1}", False, f"Erro: {str(e)}")
        
        return added_prayers
    
    def test_prayer_retrieval_supabase(self):
        """3. Verificar recuperação de dados do Supabase"""
        try:
            # GET /api/prayers
            response = requests.get(f"{self.base_url}/api/prayers", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    prayers = data.get("data", [])
                    storage_info = data.get("storage_info", {})
                    
                    # Verificar se todas as orações vêm do Supabase
                    supabase_prayers = [p for p in prayers if p.get("source") == "supabase"]
                    total_prayers = len(prayers)
                    supabase_count = len(supabase_prayers)
                    
                    if supabase_count == total_prayers and total_prayers > 0:
                        self.log_test("Prayer Retrieval", True, 
                                    f"Todas as {total_prayers} orações vêm do Supabase", 
                                    {
                                        "total_prayers": total_prayers,
                                        "supabase_prayers": supabase_count,
                                        "storage_type": storage_info.get("primary_storage"),
                                        "sample_ids": [p.get("id") for p in prayers[:3]]
                                    })
                    else:
                        self.log_test("Prayer Retrieval", False, 
                                    f"Nem todas as orações vêm do Supabase: {supabase_count}/{total_prayers}", 
                                    {
                                        "total": total_prayers,
                                        "from_supabase": supabase_count,
                                        "sources": list(set(p.get("source", "unknown") for p in prayers))
                                    })
                else:
                    self.log_test("Prayer Retrieval", False, "Falha na busca de orações")
            else:
                self.log_test("Prayer Retrieval", False, f"Status code {response.status_code}")
                
        except Exception as e:
            self.log_test("Prayer Retrieval", False, f"Erro: {str(e)}")
    
    def test_prayer_stats_supabase(self):
        """Verificar estatísticas atualizadas"""
        try:
            response = requests.get(f"{self.base_url}/api/prayers/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    stats = data.get("data", {})
                    
                    total_entries = stats.get("total_entries", 0)
                    total_hours = stats.get("total_hours", 0)
                    progress = stats.get("progress_percentage", 0)
                    
                    # Verificar se as estatísticas fazem sentido
                    if total_entries >= 16 and total_hours >= 10:
                        self.log_test("Prayer Stats", True, 
                                    f"Estatísticas atualizadas: {total_entries} orações, {total_hours}h ({progress}%)", 
                                    {
                                        "total_entries": total_entries,
                                        "total_hours": total_hours,
                                        "progress_percentage": progress,
                                        "expected_minimum": {"entries": 16, "hours": 10}
                                    })
                    else:
                        self.log_test("Prayer Stats", False, 
                                    f"Estatísticas abaixo do esperado: {total_entries} orações, {total_hours}h")
                else:
                    self.log_test("Prayer Stats", False, "Falha ao obter estatísticas")
            else:
                self.log_test("Prayer Stats", False, f"Status code {response.status_code}")
                
        except Exception as e:
            self.log_test("Prayer Stats", False, f"Erro: {str(e)}")
    
    def test_recent_prayers_supabase(self):
        """Verificar orações recentes do Supabase"""
        try:
            response = requests.get(f"{self.base_url}/api/prayers/recent", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    recent = data.get("data", [])
                    
                    if recent:
                        # Verificar se as orações recentes têm IDs do Supabase
                        has_supabase_ids = all(p.get("id") and isinstance(p.get("id"), int) for p in recent)
                        has_supabase_source = all(p.get("source") == "supabase" for p in recent)
                        
                        if has_supabase_ids and has_supabase_source:
                            self.log_test("Recent Prayers", True, 
                                        f"{len(recent)} orações recentes do Supabase", 
                                        {
                                            "count": len(recent),
                                            "all_from_supabase": True,
                                            "latest_id": recent[0].get("id"),
                                            "latest_name": recent[0].get("name")
                                        })
                        else:
                            self.log_test("Recent Prayers", False, 
                                        f"Orações recentes não são todas do Supabase", 
                                        {
                                            "has_supabase_ids": has_supabase_ids,
                                            "has_supabase_source": has_supabase_source
                                        })
                    else:
                        self.log_test("Recent Prayers", False, "Nenhuma oração recente encontrada")
                else:
                    self.log_test("Recent Prayers", False, "Falha ao buscar orações recentes")
            else:
                self.log_test("Recent Prayers", False, f"Status code {response.status_code}")
                
        except Exception as e:
            self.log_test("Recent Prayers", False, f"Erro: {str(e)}")
    
    def test_data_persistence(self):
        """4. Testar persistência dos dados"""
        try:
            # Adicionar uma oração de teste
            test_prayer = {
                "name": "Teste Persistência",
                "time": 25,
                "unit": "minutos",
                "description": "Teste de persistência no Supabase"
            }
            
            # Adicionar oração
            add_response = requests.post(f"{self.base_url}/api/prayers", 
                                       json=test_prayer, timeout=10)
            
            if add_response.status_code == 200:
                add_data = add_response.json()
                
                if add_data.get("success"):
                    prayer_data = add_data.get("data", {})
                    prayer_id = prayer_data.get("id")
                    
                    # Aguardar um momento
                    time.sleep(1)
                    
                    # Verificar se aparece na consulta
                    get_response = requests.get(f"{self.base_url}/api/prayers", timeout=10)
                    
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        
                        if get_data.get("success"):
                            prayers = get_data.get("data", [])
                            
                            # Procurar a oração adicionada
                            found_prayer = None
                            for prayer in prayers:
                                if prayer.get("id") == prayer_id:
                                    found_prayer = prayer
                                    break
                            
                            if found_prayer:
                                self.log_test("Data Persistence", True, 
                                            f"Oração persistida com ID {prayer_id}", 
                                            {
                                                "added_id": prayer_id,
                                                "found_prayer": {
                                                    "id": found_prayer.get("id"),
                                                    "name": found_prayer.get("name"),
                                                    "source": found_prayer.get("source")
                                                }
                                            })
                            else:
                                self.log_test("Data Persistence", False, 
                                            f"Oração com ID {prayer_id} não encontrada após adição")
                        else:
                            self.log_test("Data Persistence", False, "Falha ao buscar orações para verificar persistência")
                    else:
                        self.log_test("Data Persistence", False, f"Erro na consulta: {get_response.status_code}")
                else:
                    self.log_test("Data Persistence", False, "Falha ao adicionar oração de teste")
            else:
                self.log_test("Data Persistence", False, f"Erro ao adicionar: {add_response.status_code}")
                
        except Exception as e:
            self.log_test("Data Persistence", False, f"Erro: {str(e)}")
    
    def test_hybrid_system_verification(self):
        """5. Verificar sistema híbrido"""
        try:
            # Verificar endpoint de sync
            sync_response = requests.post(f"{self.base_url}/api/sync", timeout=15)
            
            if sync_response.status_code == 200:
                sync_data = sync_response.json()
                
                if sync_data.get("success"):
                    # Sistema híbrido funcionando com Supabase
                    self.log_test("Hybrid System", True, 
                                "Sistema híbrido funcionando com Supabase como primário", 
                                {
                                    "sync_successful": True,
                                    "message": sync_data.get("message"),
                                    "data": sync_data.get("data", {})
                                })
                else:
                    # Verificar se é erro esperado ou problema real
                    error_msg = sync_data.get("message", "")
                    if "já sincronizado" in error_msg.lower() or "nenhum dado" in error_msg.lower():
                        self.log_test("Hybrid System", True, 
                                    "Sistema já sincronizado (comportamento esperado)", 
                                    {"message": error_msg})
                    else:
                        self.log_test("Hybrid System", False, 
                                    f"Erro na sincronização: {error_msg}")
            else:
                self.log_test("Hybrid System", False, f"Erro no sync: {sync_response.status_code}")
                
        except Exception as e:
            self.log_test("Hybrid System", False, f"Erro: {str(e)}")
    
    def run_focused_tests(self):
        """Executar todos os testes focados no Supabase"""
        print("🔄 Iniciando testes focados na integração com Supabase...")
        print(f"🎯 Base URL: {self.base_url}")
        print("=" * 70)
        
        # 1. Verificar status do Supabase
        self.test_supabase_status()
        
        # 2. Testar salvamento de orações
        added_prayers = self.test_prayer_saving_supabase()
        
        # 3. Verificar recuperação de dados
        self.test_prayer_retrieval_supabase()
        
        # 4. Verificar estatísticas
        self.test_prayer_stats_supabase()
        
        # 5. Verificar orações recentes
        self.test_recent_prayers_supabase()
        
        # 6. Testar persistência
        self.test_data_persistence()
        
        # 7. Verificar sistema híbrido
        self.test_hybrid_system_verification()
        
        # Resumo final
        print("=" * 70)
        print(f"📊 RESUMO DOS TESTES SUPABASE:")
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
        else:
            print(f"\n✅ TODOS OS TESTES PASSARAM! Supabase funcionando perfeitamente.")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "success_rate": (self.passed_tests/self.total_tests)*100,
            "results": self.test_results,
            "failures": failures
        }

if __name__ == "__main__":
    # Executar testes focados
    tester = SupabaseFocusedTester()
    results = tester.run_focused_tests()
    
    # Salvar resultados
    with open("/app/supabase_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/supabase_test_results.json")