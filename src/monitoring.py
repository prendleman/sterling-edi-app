"""
System Monitoring and Alerting
Provides health monitoring, performance tracking, and alerting capabilities.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque
import threading

logger = logging.getLogger(__name__)


class HealthMonitor:
    """System health monitoring."""
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize health monitor.
        
        Args:
            check_interval: Health check interval in seconds
        """
        self.check_interval = check_interval
        self.health_status = {
            "status": "healthy",
            "last_check": None,
            "checks": {}
        }
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start background health monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                self.check_health()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Health status dictionary
        """
        checks = {}
        
        # Check disk space
        try:
            import shutil
            disk = shutil.disk_usage(".")
            disk_free_percent = (disk.free / disk.total) * 100
            checks["disk_space"] = {
                "status": "healthy" if disk_free_percent > 10 else "warning",
                "free_percent": round(disk_free_percent, 2)
            }
        except Exception as e:
            checks["disk_space"] = {"status": "error", "error": str(e)}
        
        # Check memory (if psutil available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            checks["memory"] = {
                "status": "healthy" if memory.percent < 90 else "warning",
                "usage_percent": memory.percent
            }
        except ImportError:
            checks["memory"] = {"status": "not_available"}
        except Exception as e:
            checks["memory"] = {"status": "error", "error": str(e)}
        
        # Determine overall status
        overall_status = "healthy"
        for check_name, check_result in checks.items():
            if check_result.get("status") == "error":
                overall_status = "unhealthy"
                break
            elif check_result.get("status") == "warning":
                overall_status = "degraded"
        
        self.health_status = {
            "status": overall_status,
            "last_check": datetime.now().isoformat(),
            "checks": checks
        }
        
        return self.health_status
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return self.health_status


class PerformanceMonitor:
    """Performance monitoring and tracking."""
    
    def __init__(self, window_size: int = 100):
        """
        Initialize performance monitor.
        
        Args:
            window_size: Number of recent measurements to keep
        """
        self.window_size = window_size
        self.processing_times = deque(maxlen=window_size)
        self.error_rates = deque(maxlen=window_size)
        self.throughput = deque(maxlen=window_size)
    
    def record_processing(self, processing_time: float, success: bool):
        """
        Record processing metrics.
        
        Args:
            processing_time: Processing time in seconds
            success: Whether processing was successful
        """
        self.processing_times.append(processing_time)
        self.error_rates.append(0 if success else 1)
        
        # Calculate throughput (files per minute)
        if len(self.processing_times) >= 2:
            time_window = sum(list(self.processing_times)[-10:])
            throughput = (10 / time_window) * 60 if time_window > 0 else 0
            self.throughput.append(throughput)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Performance metrics dictionary
        """
        if not self.processing_times:
            return {
                "average_processing_time": 0,
                "p95_processing_time": 0,
                "error_rate": 0,
                "throughput": 0
            }
        
        times = list(self.processing_times)
        errors = list(self.error_rates)
        throughputs = list(self.throughput)
        
        # Calculate percentiles
        sorted_times = sorted(times)
        p95_index = int(len(sorted_times) * 0.95)
        p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        
        return {
            "average_processing_time": sum(times) / len(times),
            "p95_processing_time": p95_time,
            "max_processing_time": max(times),
            "error_rate": sum(errors) / len(errors) if errors else 0,
            "throughput": sum(throughputs) / len(throughputs) if throughputs else 0,
            "sample_size": len(times)
        }


class AlertManager:
    """Alert management system."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.alerts = []
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "processing_time": 10.0,  # 10 seconds
            "disk_space": 10,  # 10% free
            "memory": 90  # 90% usage
        }
    
    def check_thresholds(self, health_status: Dict[str, Any], 
                        performance_metrics: Dict[str, Any]):
        """
        Check if any thresholds are exceeded.
        
        Args:
            health_status: Health status from HealthMonitor
            performance_metrics: Performance metrics from PerformanceMonitor
        """
        alerts = []
        
        # Check error rate
        if performance_metrics.get("error_rate", 0) > self.alert_thresholds["error_rate"]:
            alerts.append({
                "type": "error_rate",
                "severity": "high",
                "message": f"Error rate {performance_metrics['error_rate']*100:.1f}% exceeds threshold",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check processing time
        if performance_metrics.get("average_processing_time", 0) > self.alert_thresholds["processing_time"]:
            alerts.append({
                "type": "processing_time",
                "severity": "medium",
                "message": f"Average processing time {performance_metrics['average_processing_time']:.2f}s exceeds threshold",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check disk space
        disk_check = health_status.get("checks", {}).get("disk_space", {})
        if disk_check.get("free_percent", 100) < self.alert_thresholds["disk_space"]:
            alerts.append({
                "type": "disk_space",
                "severity": "high",
                "message": f"Disk space {disk_check.get('free_percent', 0):.1f}% below threshold",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check memory
        memory_check = health_status.get("checks", {}).get("memory", {})
        if memory_check.get("usage_percent", 0) > self.alert_thresholds["memory"]:
            alerts.append({
                "type": "memory",
                "severity": "medium",
                "message": f"Memory usage {memory_check.get('usage_percent', 0):.1f}% above threshold",
                "timestamp": datetime.now().isoformat()
            })
        
        self.alerts.extend(alerts)
        
        # Log alerts
        for alert in alerts:
            if alert["severity"] == "high":
                logger.error(f"ALERT: {alert['message']}")
            else:
                logger.warning(f"ALERT: {alert['message']}")
        
        return alerts
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alerts[-limit:]
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []


class SystemMonitor:
    """Combined system monitoring."""
    
    def __init__(self):
        """Initialize system monitor."""
        self.health_monitor = HealthMonitor()
        self.performance_monitor = PerformanceMonitor()
        self.alert_manager = AlertManager()
    
    def start(self):
        """Start all monitoring."""
        self.health_monitor.start_monitoring()
        logger.info("System monitoring started")
    
    def stop(self):
        """Stop all monitoring."""
        self.health_monitor.stop_monitoring()
        logger.info("System monitoring stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete system status.
        
        Returns:
            Complete status dictionary
        """
        health = self.health_monitor.get_health_status()
        performance = self.performance_monitor.get_performance_metrics()
        
        # Check for alerts
        alerts = self.alert_manager.check_thresholds(health, performance)
        
        return {
            "health": health,
            "performance": performance,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }

