"""
Integration Tests
End-to-end integration tests for the EDI application.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

from src.edi_processor import EDIProcessor
from src.acumatica_connector import AcumaticaConnector
from src.ecommerce_connector import ECommerceConnector
from src.sql_server_integration import SQLServerIntegration
from src.ai_automation import AIValidator, AutomatedErrorHandler
from src.security_audit import SecurityAudit


class TestEDIProcessorIntegration:
    """Integration tests for EDI processor."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def processor(self, temp_dir):
        """Create EDI processor instance."""
        config = {
            "sterling": {
                "pickup_directories": [os.path.join(temp_dir, "pickup")],
                "delivery_directories": [os.path.join(temp_dir, "delivery")]
            },
            "metrics": {
                "storage_path": os.path.join(temp_dir, "metrics"),
                "use_database": False
            }
        }
        return EDIProcessor(config)
    
    def test_process_x12_file(self, processor):
        """Test processing X12 file."""
        sample_file = "tests/sample_data/sample_850.x12"
        if os.path.exists(sample_file):
            result = processor.process_file(sample_file, deliver=False)
            assert result["success"] is True
            assert result["edi_type"] == "X12"
    
    def test_process_edifact_file(self, processor):
        """Test processing EDIFACT file."""
        sample_file = "tests/sample_data/sample_855.edifact"
        if os.path.exists(sample_file):
            result = processor.process_file(sample_file, deliver=False)
            assert result["success"] is True
            assert result["edi_type"] == "EDIFACT"


class TestAIValidation:
    """Tests for AI validation."""
    
    def test_ai_validator_learning(self):
        """Test AI validator pattern learning."""
        validator = AIValidator()
        
        # Learn pattern
        validator.learn_pattern("po_number", ["PO001", "PO002", "PO003"], r"^PO\d+$")
        
        # Validate
        result = validator.validate_with_ai({"po_number": "PO004"}, "850")
        assert result["valid"] is True
    
    def test_anomaly_detection(self):
        """Test anomaly detection."""
        validator = AIValidator()
        
        # Add historical data
        for i in range(10):
            validator.update_historical_data("850", {"amount": 1000.0 + i * 10})
        
        # Test anomaly
        result = validator.validate_with_ai({"amount": 5000.0}, "850")
        assert len(result.get("anomalies", [])) > 0


class TestErrorHandling:
    """Tests for automated error handling."""
    
    def test_error_classification(self):
        """Test error classification."""
        handler = AutomatedErrorHandler()
        
        # Test connection error
        error = Exception("Connection timeout")
        error_type = handler.classify_error(error)
        assert error_type == "connection"
        
        # Test authentication error
        error = Exception("Unauthorized access")
        error_type = handler.classify_error(error)
        assert error_type == "authentication"
    
    def test_retry_logic(self):
        """Test retry logic."""
        handler = AutomatedErrorHandler(max_retries=3)
        
        # Connection error should be retryable
        error = Exception("Connection timeout")
        assert handler.should_retry(error, 1) is True
        
        # Authentication error should not be retryable
        error = Exception("Unauthorized")
        assert handler.should_retry(error, 1) is False


class TestSecurityAudit:
    """Tests for security audit."""
    
    def test_audit_logging(self, tmp_path):
        """Test audit logging."""
        audit = SecurityAudit(audit_log_path=str(tmp_path / "audit.log"))
        
        # Log access
        audit.log_access("user1", "resource1", "read", True)
        
        # Get report
        entries = audit.get_audit_report()
        assert len(entries) == 1
        assert entries[0]["user"] == "user1"
    
    def test_compliance_report(self, tmp_path):
        """Test compliance reporting."""
        audit = SecurityAudit(audit_log_path=str(tmp_path / "audit.log"))
        
        # Log multiple events
        audit.log_access("user1", "resource1", "read", True)
        audit.log_data_access("user1", "EDI_Data", 100)
        
        # Generate report
        from src.security_audit import ComplianceReporter
        reporter = ComplianceReporter(audit)
        report = reporter.generate_access_report("2025-01-01", "2025-12-31")
        
        assert report["total_access_attempts"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

