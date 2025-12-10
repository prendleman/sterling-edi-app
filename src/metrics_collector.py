"""
Metrics Collector
Collects and stores EDI processing metrics for Power BI dashboard.
"""

import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ProcessingMetric:
    """Represents a single processing metric."""
    timestamp: str
    filepath: str
    edi_type: str  # X12 or EDIFACT
    transaction_type: str  # 850, 855, 810, ORDERS, etc.
    trading_partner: str
    status: str  # success or failed
    processing_time_ms: int
    error_count: int
    warning_count: int
    validation_passed: bool
    delivered_to_sterling: bool


class MetricsCollector:
    """Collects and stores EDI processing metrics."""
    
    def __init__(self, storage_path: str = "metrics", use_database: bool = True):
        """
        Initialize metrics collector.
        
        Args:
            storage_path: Path to store metrics data
            use_database: Use SQLite database (True) or JSON files (False)
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.use_database = use_database
        
        if use_database:
            self.db_path = self.storage_path / "metrics.db"
            self._init_database()
        else:
            self.json_path = self.storage_path / "metrics.json"
            self._load_json_metrics()
    
    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filepath TEXT,
                edi_type TEXT,
                transaction_type TEXT,
                trading_partner TEXT,
                status TEXT,
                processing_time_ms INTEGER,
                error_count INTEGER,
                warning_count INTEGER,
                validation_passed INTEGER,
                delivered_to_sterling INTEGER
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON processing_metrics(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON processing_metrics(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transaction_type ON processing_metrics(transaction_type)
        """)
        
        conn.commit()
        conn.close()
    
    def _load_json_metrics(self):
        """Load metrics from JSON file."""
        if self.json_path.exists():
            try:
                with open(self.json_path, 'r') as f:
                    self.metrics = json.load(f)
            except:
                self.metrics = []
        else:
            self.metrics = []
    
    def _save_json_metrics(self):
        """Save metrics to JSON file."""
        with open(self.json_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def record_processing(self, result: Dict[str, Any]) -> None:
        """
        Record a processing result.
        
        Args:
            result: Processing result dictionary from EDIProcessor
        """
        try:
            # Extract data from result
            filepath = result.get("filepath", "")
            edi_type = result.get("edi_type", "UNKNOWN")
            status = "success" if result.get("success", False) else "failed"
            
            # Extract transaction type
            transaction_type = "UNKNOWN"
            if result.get("data"):
                transaction_type = (
                    result["data"].get("transaction_type") or 
                    result["data"].get("message_type") or 
                    "UNKNOWN"
                )
            
            # Extract trading partner from data or filepath
            trading_partner = "UNKNOWN"
            if result.get("data") and result["data"].get("data"):
                # Try to get from parties or other fields
                parties = result["data"]["data"].get("parties", [])
                if parties:
                    trading_partner = parties[0].get("name", "UNKNOWN")
            
            # Calculate processing time (if available)
            processing_time_ms = result.get("processing_time_ms", 0)
            
            # Get validation info
            validation = result.get("validation", {})
            error_count = validation.get("error_count", 0) if validation else len(result.get("errors", []))
            warning_count = validation.get("warning_count", 0) if validation else 0
            validation_passed = validation.get("is_valid", False) if validation else False
            
            # Delivery status
            delivered_to_sterling = result.get("delivered", False) or result.get("api_delivered", False)
            
            metric = ProcessingMetric(
                timestamp=datetime.now().isoformat(),
                filepath=filepath,
                edi_type=edi_type,
                transaction_type=transaction_type,
                trading_partner=trading_partner,
                status=status,
                processing_time_ms=processing_time_ms,
                error_count=error_count,
                warning_count=warning_count,
                validation_passed=validation_passed,
                delivered_to_sterling=delivered_to_sterling
            )
            
            if self.use_database:
                self._save_to_database(metric)
            else:
                self.metrics.append(asdict(metric))
                self._save_json_metrics()
            
            logger.debug(f"Recorded metric: {status} - {transaction_type}")
            
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
    
    def _save_to_database(self, metric: ProcessingMetric):
        """Save metric to database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO processing_metrics 
            (timestamp, filepath, edi_type, transaction_type, trading_partner, status,
             processing_time_ms, error_count, warning_count, validation_passed, delivered_to_sterling)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric.timestamp,
            metric.filepath,
            metric.edi_type,
            metric.transaction_type,
            metric.trading_partner,
            metric.status,
            metric.processing_time_ms,
            metric.error_count,
            metric.warning_count,
            1 if metric.validation_passed else 0,
            1 if metric.delivered_to_sterling else 0
        ))
        
        conn.commit()
        conn.close()
    
    def get_metrics(self, 
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   status: Optional[str] = None,
                   transaction_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get metrics with optional filters.
        
        Args:
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            status: Status filter (success/failed)
            transaction_type: Transaction type filter
            
        Returns:
            List of metric dictionaries
        """
        if self.use_database:
            return self._get_from_database(start_date, end_date, status, transaction_type)
        else:
            return self._get_from_json(start_date, end_date, status, transaction_type)
    
    def _get_from_database(self, start_date, end_date, status, transaction_type) -> List[Dict[str, Any]]:
        """Get metrics from database."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM processing_metrics WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        if status:
            query += " AND status = ?"
            params.append(status)
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        metrics = []
        for row in rows:
            metrics.append({
                "timestamp": row["timestamp"],
                "filepath": row["filepath"],
                "edi_type": row["edi_type"],
                "transaction_type": row["transaction_type"],
                "trading_partner": row["trading_partner"],
                "status": row["status"],
                "processing_time_ms": row["processing_time_ms"],
                "error_count": row["error_count"],
                "warning_count": row["warning_count"],
                "validation_passed": bool(row["validation_passed"]),
                "delivered_to_sterling": bool(row["delivered_to_sterling"])
            })
        
        conn.close()
        return metrics
    
    def _get_from_json(self, start_date, end_date, status, transaction_type) -> List[Dict[str, Any]]:
        """Get metrics from JSON."""
        metrics = self.metrics.copy()
        
        # Apply filters
        if start_date:
            metrics = [m for m in metrics if m["timestamp"] >= start_date]
        if end_date:
            metrics = [m for m in metrics if m["timestamp"] <= end_date]
        if status:
            metrics = [m for m in metrics if m["status"] == status]
        if transaction_type:
            metrics = [m for m in metrics if m["transaction_type"] == transaction_type]
        
        return metrics
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for dashboard.
        
        Returns:
            Dictionary with aggregated statistics
        """
        all_metrics = self.get_metrics()
        
        if not all_metrics:
            return {
                "total_files": 0,
                "success_count": 0,
                "failed_count": 0,
                "success_rate": 0.0,
                "avg_processing_time_ms": 0,
                "total_errors": 0,
                "total_warnings": 0
            }
        
        total_files = len(all_metrics)
        success_count = sum(1 for m in all_metrics if m["status"] == "success")
        failed_count = total_files - success_count
        success_rate = (success_count / total_files * 100) if total_files > 0 else 0
        
        processing_times = [m["processing_time_ms"] for m in all_metrics if m["processing_time_ms"] > 0]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        total_errors = sum(m["error_count"] for m in all_metrics)
        total_warnings = sum(m["warning_count"] for m in all_metrics)
        
        # Transaction type breakdown
        transaction_counts = defaultdict(int)
        for m in all_metrics:
            transaction_counts[m["transaction_type"]] += 1
        
        # Status by transaction type
        status_by_type = defaultdict(lambda: {"success": 0, "failed": 0})
        for m in all_metrics:
            status_by_type[m["transaction_type"]][m["status"]] += 1
        
        return {
            "total_files": total_files,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": round(success_rate, 2),
            "avg_processing_time_ms": round(avg_processing_time, 2),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "transaction_counts": dict(transaction_counts),
            "status_by_type": {k: dict(v) for k, v in status_by_type.items()}
        }
    
    def export_for_powerbi(self, output_path: str = "metrics/powerbi_data.json") -> str:
        """
        Export metrics in format suitable for Power BI import.
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        metrics = self.get_metrics()
        
        # Convert to Power BI friendly format
        powerbi_data = []
        for m in metrics:
            powerbi_data.append({
                "Date": m["timestamp"][:10],  # YYYY-MM-DD
                "Time": m["timestamp"][11:19],  # HH:MM:SS
                "DateTime": m["timestamp"],
                "Filepath": m["filepath"],
                "EDIType": m["edi_type"],
                "TransactionType": m["transaction_type"],
                "TradingPartner": m["trading_partner"],
                "Status": m["status"],
                "ProcessingTimeMs": m["processing_time_ms"],
                "ErrorCount": m["error_count"],
                "WarningCount": m["warning_count"],
                "ValidationPassed": m["validation_passed"],
                "DeliveredToSterling": m["delivered_to_sterling"],
                "IsSuccess": 1 if m["status"] == "success" else 0,
                "IsFailed": 1 if m["status"] == "failed" else 0
            })
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(powerbi_data, f, indent=2)
        
        logger.info(f"Exported {len(powerbi_data)} metrics to {output_file}")
        return str(output_file)

