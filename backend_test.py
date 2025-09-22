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
    
    def test_update_prayer_endpoint(self):
        """Testar endpoint PUT /api/prayers/{id} para atualizar oração"""
        try:
            # Primeiro, buscar uma oração existente para atualizar
            response = requests.get(f"{self.base_url}/api/prayers", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Update Prayer - Get Existing", False, 
                            f"Falha ao buscar orações existentes: {response.status_code}")
                return
            
            data = response.json()
            prayers = data.get("data", [])
            
            if not prayers:
                self.log_test("Update Prayer", False, "Nenhuma oração encontrada para atualizar")
                return
            
            # Pegar a primeira oração para atualizar
            prayer_to_update = prayers[0]
            prayer_id = prayer_to_update.get("id")
            
            if not prayer_id:
                self.log_test("Update Prayer", False, "Oração sem ID encontrada")
                return
            
            # Dados atualizados
            updated_prayer = {
                "name": "João Santos (Atualizado)",
                "time": 60,
                "unit": "minutos",
                "description": "Oração de gratidão atualizada via teste"
            }
            
            # Fazer a atualização
            update_response = requests.put(f"{self.base_url}/api/prayers/{prayer_id}", 
                                         json=updated_prayer, timeout=10)
            
            if update_response.status_code == 200:
                update_data = update_response.json()
                
                if update_data.get("success"):
                    updated_data = update_data.get("data", {})
                    self.log_test("Update Prayer", True, 
                                f"Oração ID {prayer_id} atualizada: {updated_prayer['name']} - {updated_prayer['time']} {updated_prayer['unit']}", 
                                {
                                    "prayer_id": prayer_id,
                                    "updated_name": updated_data.get("name"),
                                    "updated_time": updated_data.get("time_minutes"),
                                    "original_name": prayer_to_update.get("name")
                                })
                else:
                    self.log_test("Update Prayer", False, 
                                f"Falha na atualização: {update_data.get('message', 'erro desconhecido')}", update_data)
            else:
                self.log_test("Update Prayer", False, 
                            f"Status code {update_response.status_code}", update_response.text)
                
        except Exception as e:
            self.log_test("Update Prayer", False, f"Erro de conexão: {str(e)}")
    
    def test_delete_prayer_endpoint(self):
        """Testar endpoint DELETE /api/prayers/{id} para excluir oração"""
        try:
            # Primeiro, criar uma oração de teste para excluir
            test_prayer = {
                "name": "Teste Para Exclusão",
                "time": 30,
                "unit": "minutos",
                "description": "Oração criada apenas para teste de exclusão"
            }
            
            # Criar a oração
            create_response = requests.post(f"{self.base_url}/api/prayers", 
                                          json=test_prayer, timeout=10)
            
            if create_response.status_code != 200:
                self.log_test("Delete Prayer - Create Test", False, 
                            f"Falha ao criar oração de teste: {create_response.status_code}")
                return
            
            create_data = create_response.json()
            if not create_data.get("success"):
                self.log_test("Delete Prayer - Create Test", False, 
                            "Falha ao criar oração de teste", create_data)
                return
            
            # Buscar a oração criada para obter o ID
            prayers_response = requests.get(f"{self.base_url}/api/prayers", timeout=10)
            if prayers_response.status_code != 200:
                self.log_test("Delete Prayer - Find Test", False, 
                            f"Falha ao buscar orações: {prayers_response.status_code}")
                return
            
            prayers_data = prayers_response.json()
            prayers = prayers_data.get("data", [])
            
            # Encontrar a oração de teste
            test_prayer_id = None
            for prayer in prayers:
                if prayer.get("name") == test_prayer["name"]:
                    test_prayer_id = prayer.get("id")
                    break
            
            if not test_prayer_id:
                self.log_test("Delete Prayer", False, "Oração de teste não encontrada após criação")
                return
            
            # Excluir a oração
            delete_response = requests.delete(f"{self.base_url}/api/prayers/{test_prayer_id}", timeout=10)
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                
                if delete_data.get("success"):
                    deleted_data = delete_data.get("data", {})
                    self.log_test("Delete Prayer", True, 
                                f"Oração ID {test_prayer_id} excluída com sucesso: {deleted_data.get('name', 'N/A')}", 
                                {
                                    "deleted_prayer_id": test_prayer_id,
                                    "deleted_name": deleted_data.get("name"),
                                    "deleted_time": deleted_data.get("time_minutes")
                                })
                    
                    # Verificar se a oração foi realmente excluída
                    verify_response = requests.get(f"{self.base_url}/api/prayers", timeout=10)
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        remaining_prayers = verify_data.get("data", [])
                        
                        # Verificar se a oração não está mais na lista
                        prayer_still_exists = any(p.get("id") == test_prayer_id for p in remaining_prayers)
                        
                        if not prayer_still_exists:
                            self.log_test("Delete Prayer - Verification", True, 
                                        f"Confirmado: Oração ID {test_prayer_id} não aparece mais na listagem")
                        else:
                            self.log_test("Delete Prayer - Verification", False, 
                                        f"ERRO: Oração ID {test_prayer_id} ainda aparece na listagem após exclusão")
                else:
                    self.log_test("Delete Prayer", False, 
                                f"Falha na exclusão: {delete_data.get('message', 'erro desconhecido')}", delete_data)
            else:
                self.log_test("Delete Prayer", False, 
                            f"Status code {delete_response.status_code}", delete_response.text)
                
        except Exception as e:
            self.log_test("Delete Prayer", False, f"Erro de conexão: {str(e)}")
    
    def test_update_nonexistent_prayer(self):
        """Testar atualização de oração que não existe (deve retornar 404)"""
        try:
            nonexistent_id = 99999
            updated_prayer = {
                "name": "Oração Inexistente",
                "time": 45,
                "unit": "minutos",
                "description": "Esta oração não deveria ser atualizada"
            }
            
            response = requests.put(f"{self.base_url}/api/prayers/{nonexistent_id}", 
                                  json=updated_prayer, timeout=10)
            
            if response.status_code == 404:
                self.log_test("Update Nonexistent Prayer", True, 
                            f"Corretamente retornou 404 para oração inexistente ID {nonexistent_id}")
            elif response.status_code == 500:
                # Verificar se a mensagem de erro é apropriada
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                    if "não encontrada" in error_detail.lower() or "not found" in error_detail.lower():
                        self.log_test("Update Nonexistent Prayer", True, 
                                    f"Corretamente detectou oração inexistente: {error_detail}")
                    else:
                        self.log_test("Update Nonexistent Prayer", False, 
                                    f"Erro inesperado: {error_detail}")
                except:
                    self.log_test("Update Nonexistent Prayer", False, 
                                f"Status 500 sem detalhes do erro: {response.text}")
            else:
                self.log_test("Update Nonexistent Prayer", False, 
                            f"Status code inesperado {response.status_code} (esperado 404 ou 500)", response.text)
                
        except Exception as e:
            self.log_test("Update Nonexistent Prayer", False, f"Erro de conexão: {str(e)}")
    
    def test_delete_nonexistent_prayer(self):
        """Testar exclusão de oração que não existe (deve retornar 404)"""
        try:
            nonexistent_id = 99999
            
            response = requests.delete(f"{self.base_url}/api/prayers/{nonexistent_id}", timeout=10)
            
            if response.status_code == 404:
                self.log_test("Delete Nonexistent Prayer", True, 
                            f"Corretamente retornou 404 para oração inexistente ID {nonexistent_id}")
            elif response.status_code == 500:
                # Verificar se a mensagem de erro é apropriada
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                    if "não encontrada" in error_detail.lower() or "not found" in error_detail.lower():
                        self.log_test("Delete Nonexistent Prayer", True, 
                                    f"Corretamente detectou oração inexistente: {error_detail}")
                    else:
                        self.log_test("Delete Nonexistent Prayer", False, 
                                    f"Erro inesperado: {error_detail}")
                except:
                    self.log_test("Delete Nonexistent Prayer", False, 
                                f"Status 500 sem detalhes do erro: {response.text}")
            else:
                self.log_test("Delete Nonexistent Prayer", False, 
                            f"Status code inesperado {response.status_code} (esperado 404)", response.text)
                
        except Exception as e:
            self.log_test("Delete Nonexistent Prayer", False, f"Erro de conexão: {str(e)}")
    
    def test_full_crud_workflow(self):
        """Testar workflow completo CRUD (Create, Read, Update, Delete)"""
        try:
            # 1. CREATE - Criar nova oração
            test_prayer = {
                "name": "Ana Costa - CRUD Test",
                "time": 45,
                "unit": "minutos",
                "description": "Oração para teste completo CRUD"
            }
            
            create_response = requests.post(f"{self.base_url}/api/prayers", 
                                          json=test_prayer, timeout=10)
            
            if create_response.status_code != 200 or not create_response.json().get("success"):
                self.log_test("CRUD Workflow - CREATE", False, 
                            "Falha na criação da oração de teste")
                return
            
            # 2. READ - Buscar a oração criada
            read_response = requests.get(f"{self.base_url}/api/prayers", timeout=10)
            
            if read_response.status_code != 200:
                self.log_test("CRUD Workflow - READ", False, 
                            f"Falha ao buscar orações: {read_response.status_code}")
                return
            
            prayers_data = read_response.json()
            prayers = prayers_data.get("data", [])
            
            # Encontrar a oração criada
            created_prayer = None
            for prayer in prayers:
                if prayer.get("name") == test_prayer["name"]:
                    created_prayer = prayer
                    break
            
            if not created_prayer:
                self.log_test("CRUD Workflow - READ", False, 
                            "Oração criada não encontrada na listagem")
                return
            
            prayer_id = created_prayer.get("id")
            
            # 3. UPDATE - Atualizar a oração
            updated_data = {
                "name": "Ana Costa - CRUD Test (Atualizada)",
                "time": 60,
                "unit": "minutos",
                "description": "Oração atualizada no teste CRUD"
            }
            
            update_response = requests.put(f"{self.base_url}/api/prayers/{prayer_id}", 
                                         json=updated_data, timeout=10)
            
            if update_response.status_code != 200 or not update_response.json().get("success"):
                self.log_test("CRUD Workflow - UPDATE", False, 
                            "Falha na atualização da oração")
                return
            
            # 4. DELETE - Excluir a oração
            delete_response = requests.delete(f"{self.base_url}/api/prayers/{prayer_id}", timeout=10)
            
            if delete_response.status_code != 200 or not delete_response.json().get("success"):
                self.log_test("CRUD Workflow - DELETE", False, 
                            "Falha na exclusão da oração")
                return
            
            # 5. VERIFY - Verificar que foi excluída
            verify_response = requests.get(f"{self.base_url}/api/prayers", timeout=10)
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                remaining_prayers = verify_data.get("data", [])
                
                prayer_still_exists = any(p.get("id") == prayer_id for p in remaining_prayers)
                
                if not prayer_still_exists:
                    self.log_test("CRUD Workflow Complete", True, 
                                f"Workflow CRUD completo executado com sucesso: CREATE → READ → UPDATE → DELETE → VERIFY", 
                                {
                                    "prayer_id": prayer_id,
                                    "original_name": test_prayer["name"],
                                    "updated_name": updated_data["name"],
                                    "final_status": "excluída com sucesso"
                                })
                else:
                    self.log_test("CRUD Workflow - VERIFY", False, 
                                "Oração ainda existe após exclusão")
            else:
                self.log_test("CRUD Workflow - VERIFY", False, 
                            "Falha na verificação final")
                
        except Exception as e:
            self.log_test("CRUD Workflow", False, f"Erro no workflow CRUD: {str(e)}")
    
    def test_stats_after_operations(self):
        """Testar se as estatísticas são atualizadas após operações CRUD"""
        try:
            # Obter estatísticas iniciais
            initial_stats_response = requests.get(f"{self.base_url}/api/prayers/stats", timeout=10)
            
            if initial_stats_response.status_code != 200:
                self.log_test("Stats After Operations", False, 
                            "Falha ao obter estatísticas iniciais")
                return
            
            initial_stats = initial_stats_response.json().get("data", {})
            initial_count = initial_stats.get("total_entries", 0)
            initial_hours = initial_stats.get("total_hours", 0)
            
            # Criar uma oração de teste
            test_prayer = {
                "name": "Teste Estatísticas",
                "time": 120,  # 2 horas
                "unit": "minutos",
                "description": "Oração para testar atualização de estatísticas"
            }
            
            create_response = requests.post(f"{self.base_url}/api/prayers", 
                                          json=test_prayer, timeout=10)
            
            if create_response.status_code != 200:
                self.log_test("Stats After Operations - CREATE", False, 
                            "Falha ao criar oração de teste")
                return
            
            # Obter estatísticas após criação
            after_create_response = requests.get(f"{self.base_url}/api/prayers/stats", timeout=10)
            
            if after_create_response.status_code == 200:
                after_create_stats = after_create_response.json().get("data", {})
                new_count = after_create_stats.get("total_entries", 0)
                new_hours = after_create_stats.get("total_hours", 0)
                
                count_increased = new_count > initial_count
                hours_increased = new_hours > initial_hours
                
                if count_increased and hours_increased:
                    self.log_test("Stats After Operations", True, 
                                f"Estatísticas atualizadas corretamente: {initial_count}→{new_count} orações, {initial_hours:.2f}→{new_hours:.2f}h", 
                                {
                                    "initial_count": initial_count,
                                    "new_count": new_count,
                                    "initial_hours": initial_hours,
                                    "new_hours": new_hours,
                                    "hours_added": new_hours - initial_hours
                                })
                else:
                    self.log_test("Stats After Operations", False, 
                                f"Estatísticas não atualizaram: count {initial_count}→{new_count}, hours {initial_hours:.2f}→{new_hours:.2f}")
            else:
                self.log_test("Stats After Operations", False, 
                            "Falha ao obter estatísticas após criação")
                
        except Exception as e:
            self.log_test("Stats After Operations", False, f"Erro no teste de estatísticas: {str(e)}")
    
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
        
        # Testes de funcionalidade básica
        self.test_add_prayer()
        
        # 🆕 TESTES DE ADMINISTRAÇÃO - NOVOS ENDPOINTS
        print("\n🔧 TESTANDO FUNCIONALIDADES ADMINISTRATIVAS...")
        self.test_update_prayer_endpoint()
        self.test_delete_prayer_endpoint()
        
        # Testes de edge cases
        print("\n⚠️  TESTANDO CASOS EXTREMOS...")
        self.test_update_nonexistent_prayer()
        self.test_delete_nonexistent_prayer()
        
        # Teste de workflow completo
        print("\n🔄 TESTANDO WORKFLOW CRUD COMPLETO...")
        self.test_full_crud_workflow()
        
        # Teste de integridade de dados
        print("\n📊 TESTANDO INTEGRIDADE DE ESTATÍSTICAS...")
        self.test_stats_after_operations()
        
        # Testes de integração
        print("\n🔗 TESTANDO INTEGRAÇÕES...")
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
        
        # Mostrar sucessos administrativos
        admin_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in ["Update", "Delete", "CRUD"])]
        admin_successes = [r for r in admin_tests if "✅" in r["status"]]
        
        if admin_successes:
            print(f"\n✅ FUNCIONALIDADES ADMINISTRATIVAS FUNCIONANDO ({len(admin_successes)}):")
            for success in admin_successes:
                print(f"   • {success['test']}: {success['message']}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "success_rate": (self.passed_tests/self.total_tests)*100,
            "results": self.test_results,
            "failures": failures,
            "admin_tests": admin_tests,
            "admin_successes": admin_successes
        }

if __name__ == "__main__":
    # Executar testes
    tester = PrayerSystemTester()
    results = tester.run_all_tests()
    
    # Salvar resultados
    with open("/app/test_results_backend.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/test_results_backend.json")