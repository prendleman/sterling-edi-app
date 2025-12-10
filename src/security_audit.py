"""
Security and Audit Logging
Provides security features, audit logging, and compliance reporting.
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import csv

logger = logging.getLogger(__name__)


class SecurityAudit:
    """Security and audit logging functionality."""
    
    def __init__(self, audit_log_path: str = "logs/audit.log"):
        """
        Initialize security audit.
        
        Args:
            audit_log_path: Path to audit log file
        """
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.audit_entries = []
    
    def log_access(self, user: str, resource: str, action: str, 
                  success: bool, details: Dict[str, Any] = None):
        """
        Log access attempt.
        
        Args:
            user: User/system identifier
            resource: Resource accessed
            action: Action performed
            success: Whether action was successful
            details: Additional details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "access",
            "user": user,
            "resource": resource,
            "action": action,
            "success": success,
            "details": details or {}
        }
        self._write_audit_entry(entry)
    
    def log_data_access(self, user: str, data_type: str, record_count: int,
                       filters: Dict[str, Any] = None):
        """
        Log data access for compliance.
        
        Args:
            user: User/system identifier
            data_type: Type of data accessed
            record_count: Number of records accessed
            filters: Filters applied
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "data_access",
            "user": user,
            "data_type": data_type,
            "record_count": record_count,
            "filters": filters or {}
        }
        self._write_audit_entry(entry)
    
    def log_config_change(self, user: str, config_file: str, 
                         changes: Dict[str, Any]):
        """
        Log configuration changes.
        
        Args:
            user: User/system identifier
            config_file: Configuration file changed
            changes: Dictionary of changes made
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "config_change",
            "user": user,
            "config_file": config_file,
            "changes": changes
        }
        self._write_audit_entry(entry)
    
    def log_security_event(self, event_type: str, severity: str,
                          description: str, details: Dict[str, Any] = None):
        """
        Log security event.
        
        Args:
            event_type: Type of security event
            severity: Severity level (low, medium, high, critical)
            description: Event description
            details: Additional details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "security_event",
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "details": details or {}
        }
        self._write_audit_entry(entry)
    
    def _write_audit_entry(self, entry: Dict[str, Any]):
        """Write audit entry to log file."""
        try:
            with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
            self.audit_entries.append(entry)
            
            # Log high-severity events immediately
            if entry.get("severity") in ["high", "critical"]:
                logger.warning(f"Security event: {entry.get('description')}")
        except Exception as e:
            logger.error(f"Failed to write audit entry: {e}")
    
    def get_audit_report(self, start_date: str = None, 
                        end_date: str = None,
                        event_type: str = None) -> List[Dict[str, Any]]:
        """
        Get audit report.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            event_type: Event type filter
            
        Returns:
            List of audit entries
        """
        entries = self.audit_entries.copy()
        
        # Filter by date
        if start_date:
            entries = [e for e in entries if e["timestamp"] >= start_date]
        if end_date:
            entries = [e for e in entries if e["timestamp"] <= end_date]
        
        # Filter by type
        if event_type:
            entries = [e for e in entries if e.get("type") == event_type]
        
        return entries
    
    def export_compliance_report(self, output_path: str, 
                                start_date: str = None,
                                end_date: str = None):
        """
        Export compliance report to CSV.
        
        Args:
            output_path: Output file path
            start_date: Start date filter
            end_date: End date filter
        """
        entries = self.get_audit_report(start_date, end_date)
        
        if not entries:
            return
        
        # Get all unique keys
        all_keys = set()
        for entry in entries:
            all_keys.update(entry.keys())
        
        fieldnames = sorted(all_keys)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entries)
        
        logger.info(f"Compliance report exported to {output_path}")


class DataEncryption:
    """Data encryption utilities."""
    
    @staticmethod
    def hash_sensitive_data(data: str, salt: str = None) -> str:
        """
        Hash sensitive data.
        
        Args:
            data: Data to hash
            salt: Optional salt
            
        Returns:
            Hashed value
        """
        if salt:
            data = data + salt
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def mask_pii(data: str, mask_char: str = "*") -> str:
        """
        Mask PII data.
        
        Args:
            data: Data to mask
            mask_char: Character to use for masking
            
        Returns:
            Masked data
        """
        if len(data) <= 4:
            return mask_char * len(data)
        return data[:2] + mask_char * (len(data) - 4) + data[-2:]
    
    @staticmethod
    def sanitize_log_entry(entry: Dict[str, Any], 
                          sensitive_fields: List[str] = None) -> Dict[str, Any]:
        """
        Sanitize log entry by masking sensitive fields.
        
        Args:
            entry: Log entry dictionary
            sensitive_fields: List of sensitive field names
            
        Returns:
            Sanitized entry
        """
        if sensitive_fields is None:
            sensitive_fields = ["password", "api_key", "token", "secret", 
                              "ssn", "credit_card", "account_number"]
        
        sanitized = entry.copy()
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = DataEncryption.mask_pii(str(sanitized[field]))
        
        return sanitized


class ComplianceReporter:
    """Compliance reporting functionality."""
    
    def __init__(self, audit: SecurityAudit):
        """
        Initialize compliance reporter.
        
        Args:
            audit: SecurityAudit instance
        """
        self.audit = audit
    
    def generate_access_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate access report for compliance.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Access report dictionary
        """
        entries = self.audit.get_audit_report(start_date, end_date, "access")
        
        report = {
            "period": {"start": start_date, "end": end_date},
            "total_access_attempts": len(entries),
            "successful": len([e for e in entries if e.get("success")]),
            "failed": len([e for e in entries if not e.get("success")]),
            "by_user": {},
            "by_resource": {}
        }
        
        for entry in entries:
            user = entry.get("user", "unknown")
            resource = entry.get("resource", "unknown")
            
            report["by_user"][user] = report["by_user"].get(user, 0) + 1
            report["by_resource"][resource] = report["by_resource"].get(resource, 0) + 1
        
        return report
    
    def generate_data_access_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate data access report for compliance.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Data access report dictionary
        """
        entries = self.audit.get_audit_report(start_date, end_date, "data_access")
        
        report = {
            "period": {"start": start_date, "end": end_date},
            "total_data_access_events": len(entries),
            "total_records_accessed": sum([e.get("record_count", 0) for e in entries]),
            "by_user": {},
            "by_data_type": {}
        }
        
        for entry in entries:
            user = entry.get("user", "unknown")
            data_type = entry.get("data_type", "unknown")
            
            report["by_user"][user] = report["by_user"].get(user, 0) + 1
            report["by_data_type"][data_type] = report["by_data_type"].get(data_type, 0) + 1
        
        return report
    
    def generate_security_incident_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate security incident report.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Security incident report dictionary
        """
        entries = self.audit.get_audit_report(start_date, end_date, "security_event")
        
        report = {
            "period": {"start": start_date, "end": end_date},
            "total_incidents": len(entries),
            "by_severity": {},
            "by_type": {}
        }
        
        for entry in entries:
            severity = entry.get("severity", "unknown")
            event_type = entry.get("event_type", "unknown")
            
            report["by_severity"][severity] = report["by_severity"].get(severity, 0) + 1
            report["by_type"][event_type] = report["by_type"].get(event_type, 0) + 1
        
        return report

