#!/usr/bin/env python3
"""
Script de monitoramento do AfiliadoHub
"""
import os
import sys
import json
import time
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import requests
import pandas as pd

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from api.utils.supabase_client import get_supabase_manager

class SystemMonitor:
    def __init__(self):
        self.supabase = get_supabase_manager()
        self.checks = []
        self.alerts = []
        
        # Configurações
        self.thresholds = {
            "database_latency": 1000,  # ms
            "api_response_time": 5000,  # ms
            "product_count_warning": 100000,
            "product_count_critical": 900000,
            "error_rate": 0.05,  # 5%
            "memory_usage": 90,  # %
            "disk_usage": 90,    # %
        }
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Verifica conexão com o banco de dados"""
        check_name = "database_connection"
        start_time = time.time()
        
        try:
            # Testa uma consulta simples
            response = self.supabase.client.table("products").select("count", count="exact").limit(1).execute()
            
            latency = (time.time() - start_time) * 1000  # ms
            
            status = "healthy" if response.count is not None else "unhealthy"
            
            result = {
                "check": check_name,
                "status": status,
                "latency_ms": round(latency, 2),
                "message": f"Conexão estabelecida ({latency:.0f}ms)",
                "details": {
                    "product_count": response.count or 0
                }
            }
            
            if latency > self.thresholds["database_latency"]:
                result["status"] = "degraded"
                result["message"] = f"Latência alta: {latency:.0f}ms"
                self.alerts.append(result)
            
            return result
            
        except Exception as e:
            return {
                "check": check_name,
                "status": "critical",
                "error": str(e),
                "message": f"Falha na conexão: {e}",
                "latency_ms": None
            }
    
    def check_api_health(self) -> Dict[str, Any]:
        """Verifica saúde da API"""
        check_name = "api_health"
        api_url = os.getenv("VERCEL_URL", "https://afiliadohub.vercel.app")
        
        if not api_url:
            return {
                "check": check_name,
                "status": "unknown",
                "message": "URL da API não configurada"
            }
        
        start_time = time.time()
        
        try:
            response = requests.get(f"{api_url}/health", timeout=10)
            latency = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                
                result = {
                    "check": check_name,
                    "status": status,
                    "latency_ms": round(latency, 2),
                    "http_status": response.status_code,
                    "message": f"API {status} ({latency:.0f}ms)",
                    "details": data
                }
                
                if latency > self.thresholds["api_response_time"]:
                    result["status"] = "degraded"
                    result["message"] = f"Resposta lenta: {latency:.0f}ms"
                    self.alerts.append(result)
                
                return result
            else:
                return {
                    "check": check_name,
                    "status": "unhealthy",
                    "latency_ms": round(latency, 2),
                    "http_status": response.status_code,
                    "message": f"API retornou {response.status_code}",
                    "details": response.text[:500]
                }
                
        except requests.exceptions.Timeout:
            return {
                "check": check_name,
                "status": "critical",
                "message": "Timeout na conexão com a API",
                "latency_ms": None
            }
        except Exception as e:
            return {
                "check": check_name,
                "status": "critical",
                "error": str(e),
                "message": f"Erro na verificação da API: {e}",
                "latency_ms": None
            }
    
    def check_telegram_bot(self) -> Dict[str, Any]:
        """Verifica status do bot Telegram"""
        check_name = "telegram_bot"
        bot_token = os.getenv("BOT_TOKEN")
        
        if not bot_token:
            return {
                "check": check_name,
                "status": "disabled",
                "message": "Bot Token não configurado"
            }
        
        start_time = time.time()
        
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{bot_token}/getMe",
                timeout=10
            )
            latency = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    
                    return {
                        "check": check_name,
                        "status": "healthy",
                        "latency_ms": round(latency, 2),
                        "message": f"Bot {bot_info.get('first_name', 'Unknown')} online",
                        "details": bot_info
                    }
                else:
                    return {
                        "check": check_name,
                        "status": "unhealthy",
                        "latency_ms": round(latency, 2),
                        "message": "Resposta inválida do Telegram",
                        "details": data
                    }
            else:
                return {
                    "check": check_name,
                    "status": "critical",
                    "latency_ms": round(latency, 2),
                    "http_status": response.status_code,
                    "message": f"Telegram API retornou {response.status_code}"
                }
                
        except Exception as e:
            return {
                "check": check_name,
                "status": "critical",
                "error": str(e),
                "message": f"Erro na verificação do bot: {e}",
                "latency_ms": None
            }
    
    def check_product_count(self) -> Dict[str, Any]:
        """Verifica contagem de produtos"""
        check_name = "product_count"
        
        try:
            response = self.supabase.client.table("products")\
                .select("count", count="exact")\
                .eq("is_active", True)\
                .execute()
            
            count = response.count or 0
            
            result = {
                "check": check_name,
                "status": "healthy",
                "message": f"{count:,} produtos ativos",
                "details": {"count": count}
            }
            
            if count > self.thresholds["product_count_critical"]:
                result["status"] = "critical"
                result["message"] = f"⚠️ ALTO: {count:,} produtos (limite: {self.thresholds['product_count_critical']:,})"
                self.alerts.append(result)
            elif count > self.thresholds["product_count_warning"]:
                result["status"] = "warning"
                result["message"] = f"⚠️ Alto: {count:,} produtos (limite: {self.thresholds['product_count_warning']:,})"
                self.alerts.append(result)
            
            return result
            
        except Exception as e:
            return {
                "check": check_name,
                "status": "critical",
                "error": str(e),
                "message": f"Erro ao contar produtos: {e}"
            }
    
    def check_recent_errors(self) -> Dict[str, Any]:
        """Verifica erros recentes no sistema"""
        check_name = "recent_errors"
        
        try:
            # Busca logs de erro das últimas 24 horas
            day_ago = (datetime.now() - timedelta(hours=24)).isoformat()
            
            response = self.supabase.client.table("product_logs")\
                .select("*")\
                .gte("created_at", day_ago)\
                .execute()
            
            error_logs = [log for log in response.data if log.get("change_type") == "error"]
            total_logs = len(response.data) if response.data else 0
            
            error_count = len(error_logs)
            error_rate = error_count / total_logs if total_logs > 0 else 0
            
            result = {
                "check": check_name,
                "status": "healthy",
                "message": f"{error_count} erros nas últimas 24h ({error_rate:.1%})",
                "details": {
                    "error_count": error_count,
                    "total_logs": total_logs,
                    "error_rate": error_rate
                }
            }
            
            if error_rate > self.thresholds["error_rate"]:
                result["status"] = "warning"
                result["message"] = f"⚠️ Alta taxa de erro: {error_rate:.1%}"
                self.alerts.append(result)
            
            return result
            
        except Exception as e:
            return {
                "check": check_name,
                "status": "critical",
                "error": str(e),
                "message": f"Erro ao verificar logs: {e}"
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Verifica uso de recursos do sistema"""
        check_name = "system_resources"
        
        try:
            # Simulação - em produção você usaria psutil ou APIs do provedor
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            result = {
                "check": check_name,
                "status": "healthy",
                "message": f"CPU: {cpu_percent}%, Mem: {memory_percent}%, Disco: {disk_percent}%",
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent,
                    "memory_used_gb": memory.used / (1024**3),
                    "memory_total_gb": memory.total / (1024**3),
                    "disk_used_gb": disk.used / (1024**3),
                    "disk_total_gb": disk.total / (1024**3)
                }
            }
            
            # Verifica thresholds
            alerts = []
            if memory_percent > self.thresholds["memory_usage"]:
                result["status"] = "warning"
                alerts.append(f"Memória alta: {memory_percent}%")
            
            if disk_percent > self.thresholds["disk_usage"]:
                result["status"] = "warning"
                alerts.append(f"Disco quase cheio: {disk_percent}%")
            
            if alerts:
                result["message"] = " | ".join(alerts)
                self.alerts.append(result)
            
            return result
            
        except ImportError:
            # psutil não disponível
            return {
                "check": check_name,
                "status": "unknown",
                "message": "psutil não instalado",
                "details": {"note": "Instale psutil para monitoramento de recursos"}
            }
        except Exception as e:
            return {
                "check": check_name,
                "status": "unknown",
                "error": str(e),
                "message": f"Erro ao verificar recursos: {e}"
            }
    
    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Executa todas as verificações"""
        checks = [
            self.check_database_connection(),
            self.check_api_health(),
            self.check_telegram_bot(),
            self.check_product_count(),
            self.check_recent_errors(),
            self.check_system_resources()
        ]
        
        self.checks = checks
        
        # Determina status geral
        statuses = [check.get("status") for check in checks]
        
        if "critical" in statuses:
            overall_status = "critical"
        elif "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "warning" in statuses:
            overall_status = "warning"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "checks": checks,
            "alerts": self.alerts,
            "summary": self._generate_summary(checks)
        }
    
    def _generate_summary(self, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera resumo das verificações"""
        total_checks = len(checks)
        healthy_checks = sum(1 for c in checks if c.get("status") == "healthy")
        unhealthy_checks = total_checks - healthy_checks
        
        # Coleta métricas
        latencies = [c.get("latency_ms") for c in checks if c.get("latency_ms")]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        return {
            "total_checks": total_checks,
            "healthy_checks": healthy_checks,
            "unhealthy_checks": unhealthy_checks,
            "avg_latency_ms": round(avg_latency, 2),
            "alert_count": len(self.alerts)
        }
    
    def generate_report(self, output_format: str = "text") -> str:
        """Gera relatório de monitoramento"""
        results = self.run_all_checks()
        
        if output_format == "json":
            return json.dumps(results, indent=2, ensure_ascii=False)
        
        # Formato texto
        report = []
        report.append("=" * 80)
        report.append("🔍 RELATÓRIO DE MONITORAMENTO - AFILIADOHUB")
        report.append("=" * 80)
        report.append(f"Data: {results['timestamp']}")
        report.append(f"Status Geral: {results['overall_status'].upper()}")
        report.append("")
        
        # Resumo
        summary = results["summary"]
        report.append("📊 RESUMO:")
        report.append(f"  • Verificações: {summary['total_checks']}")
        report.append(f"  • Saudáveis: {summary['healthy_checks']}")
        report.append(f"  • Com problemas: {summary['unhealthy_checks']}")
        report.append(f"  • Latência média: {summary['avg_latency_ms']}ms")
        report.append(f"  • Alertas: {summary['alert_count']}")
        report.append("")
        
        # Verificações detalhadas
        report.append("📋 VERIFICAÇÕES DETALHADAS:")
        for check in results["checks"]:
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "warning": "⚠️",
                "unhealthy": "❌",
                "critical": "🛑",
                "unknown": "❓",
                "disabled": "⚪"
            }.get(check.get("status"), "❓")
            
            report.append(f"  {status_emoji} {check['check']}: {check['message']}")
            
            if "latency_ms" in check and check["latency_ms"]:
                report.append(f"     Latência: {check['latency_ms']}ms")
        
        # Alertas
        if results["alerts"]:
            report.append("")
            report.append("🚨 ALERTAS:")
            for alert in results["alerts"]:
                report.append(f"  ⚠️ {alert['check']}: {alert['message']}")
        
        report.append("")
        report.append("=" * 80)
        report.append("🎯 RECOMENDAÇÕES:")
        
        # Gera recomendações baseadas nos checks
        recommendations = self._generate_recommendations(results["checks"])
        for rec in recommendations:
            report.append(f"  • {rec}")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _generate_recommendations(self, checks: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nas verificações"""
        recommendations = []
        
        for check in checks:
            status = check.get("status")
            check_name = check.get("check")
            
            if status == "critical":
                if check_name == "database_connection":
                    recommendations.append("Verifique a conexão com o Supabase e as credenciais")
                elif check_name == "api_health":
                    recommendations.append("Verifique se a API está online e acessível")
                elif check_name == "telegram_bot":
                    recommendations.append("Verifique o token do bot e a conexão com o Telegram")
            
            elif status == "warning":
                if check_name == "product_count":
                    recommendations.append("Considere arquivar produtos antigos ou migrar para plano superior")
                elif check_name == "recent_errors":
                    recommendations.append("Analise os logs de erro para identificar problemas recorrentes")
                elif check_name == "system_resources":
                    if check.get("details", {}).get("memory_percent", 0) > 80:
                        recommendations.append("Considere otimizar o uso de memória ou aumentar os recursos")
                    if check.get("details", {}).get("disk_percent", 0) > 80:
                        recommendations.append("Faça limpeza de arquivos temporários ou aumente o espaço em disco")
        
        if not recommendations:
            recommendations.append("Sistema operando normalmente. Continue monitorando.")
        
        return recommendations
    
    def send_email_alert(self, to_email: str, subject: str = None):
        """Envia alerta por email"""
        if not self.alerts:
            print("📭 Nenhum alerta para enviar")
            return
        
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT", 587)
        smtp_user = os.getenv("SMTP_USERNAME")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_server, smtp_user, smtp_pass]):
            print("⚠️ Configuração de email não encontrada")
            return
        
        if not subject:
            subject = f"🚨 Alertas AfiliadoHub - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        report = self.generate_report("text")
        
        try:
            # Cria mensagem
            from email.mime
