"""
EDI Processor
Main orchestrator for EDI file processing pipeline.
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .x12_parser import X12Parser
from .edifact_parser import EdifactParser
from .edi_validator import EDIValidator
from .edi_transformer import EDITransformer
from .sterling_integration import SterlingIntegration
from .acumatica_connector import AcumaticaConnector
from .acumatica_crm_integration import AcumaticaCRMIntegration
from .ecommerce_connector import ECommerceConnector
from .ai_automation import AIValidator, AutomatedErrorHandler, PredictiveAnalytics
from .sql_server_integration import SQLServerIntegration
from .metrics_collector import MetricsCollector
from .utils.logger import setup_logger
import time

logger = setup_logger(__name__)


class EDIProcessor:
    """Main EDI processing engine."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize EDI processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize components
        self.x12_parser = X12Parser()
        self.edifact_parser = EdifactParser()
        self.validator = EDIValidator()
        self.transformer = EDITransformer()
        
        # Initialize Sterling integration
        sterling_config = self.config.get("sterling", {})
        self.sterling = SterlingIntegration(
            pickup_directories=sterling_config.get("pickup_directories", []),
            delivery_directories=sterling_config.get("delivery_directories", []),
            api_base_url=sterling_config.get("api_base_url"),
            api_username=sterling_config.get("api_username"),
            api_password=sterling_config.get("api_password")
        )
        
        # Initialize metrics collector
        metrics_config = self.config.get("metrics", {})
        self.metrics_collector = MetricsCollector(
            storage_path=metrics_config.get("storage_path", "metrics"),
            use_database=metrics_config.get("use_database", True)
        )
        
        # Initialize Acumatica connector (if configured)
        acumatica_config = self.config.get("acumatica", {})
        if acumatica_config.get("enabled", False):
            self.acumatica = AcumaticaConnector(
                base_url=acumatica_config.get("base_url"),
                username=acumatica_config.get("username"),
                password=acumatica_config.get("password"),
                tenant=acumatica_config.get("tenant"),
                branch=acumatica_config.get("branch")
            )
            # Initialize CRM integration
            self.acumatica_crm = AcumaticaCRMIntegration(self.acumatica)
        else:
            self.acumatica = None
            self.acumatica_crm = None
        
        # Initialize eCommerce connector (if configured)
        ecommerce_config = self.config.get("ecommerce", {})
        if ecommerce_config.get("enabled", False):
            self.ecommerce = ECommerceConnector(
                platform=ecommerce_config.get("platform"),
                base_url=ecommerce_config.get("base_url"),
                api_key=ecommerce_config.get("api_key"),
                api_secret=ecommerce_config.get("api_secret"),
                access_token=ecommerce_config.get("access_token")
            )
        else:
            self.ecommerce = None
        
        # Initialize AI/automation features
        self.ai_validator = AIValidator()
        self.error_handler = AutomatedErrorHandler()
        self.predictive_analytics = PredictiveAnalytics()
        
        # Initialize SQL Server integration (if configured)
        sql_config = self.config.get("sql_server", {})
        if sql_config.get("enabled", False):
            self.sql_server = SQLServerIntegration(
                server=sql_config.get("server"),
                database=sql_config.get("database"),
                username=sql_config.get("username"),
                password=sql_config.get("password"),
                use_windows_auth=sql_config.get("use_windows_auth", True),
                driver=sql_config.get("driver", "ODBC Driver 17 for SQL Server")
            )
            # Create metrics table if needed
            if sql_config.get("auto_create_tables", True):
                self.sql_server.create_metrics_table()
        else:
            self.sql_server = None
        
        # Initialize security audit (always enabled)
        security_config = self.config.get("security", {})
        audit_log_path = security_config.get("audit_log_path", "logs/audit.log")
        self.security_audit = SecurityAudit(audit_log_path=audit_log_path)
    
    def detect_edi_type(self, content: str) -> str:
        """
        Detect EDI type from content.
        
        Args:
            content: EDI file content
            
        Returns:
            'X12' or 'EDIFACT'
        """
        content_stripped = content.strip()
        if content_stripped.startswith("ISA"):
            return "X12"
        elif content_stripped.startswith("UNB") or content_stripped.startswith("UNA"):
            return "EDIFACT"
        else:
            # Try to parse and see which works
            try:
                self.x12_parser.parse(content[:500])
                return "X12"
            except:
                try:
                    self.edifact_parser.parse(content[:500])
                    return "EDIFACT"
                except:
                    return "UNKNOWN"
    
    def process_file(self, filepath: str, 
                    validate: bool = True,
                    transform: bool = False,
                    deliver: bool = True) -> Dict[str, Any]:
        """
        Process an EDI file through the complete pipeline.
        
        Args:
            filepath: Path to EDI file
            validate: Whether to validate the file
            transform: Whether to apply transformations
            deliver: Whether to deliver to Sterling
            
        Returns:
            Processing result dictionary
        """
        result = {
            "filepath": filepath,
            "success": False,
            "edi_type": None,
            "validation": None,
            "data": None,
            "errors": []
        }
        
        start_time = time.time()
        
        try:
            # Read file
            logger.info(f"Processing file: {filepath}")
            
            # Log access
            self.security_audit.log_access(
                user="system",
                resource=filepath,
                action="process_file",
                success=True
            )
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Detect EDI type
            edi_type = self.detect_edi_type(content)
            result["edi_type"] = edi_type
            
            if edi_type == "UNKNOWN":
                raise ValueError("Unable to detect EDI type")
            
            # Parse
            if edi_type == "X12":
                envelope = self.x12_parser.parse(content)
                if envelope.transactions:
                    transaction = envelope.transactions[0]
                    result["data"] = self.x12_parser.extract_transaction_data(transaction)
            elif edi_type == "EDIFACT":
                envelope = self.edifact_parser.parse(content)
                if envelope.messages:
                    message = envelope.messages[0]
                    result["data"] = self.edifact_parser.extract_message_data(message)
            
            # Validate
            if validate:
                validation_result = self.validator.validate(content, edi_type)
                result["validation"] = validation_result.get_summary()
                
                # AI-powered validation
                if result.get("data"):
                    ai_validation = self.ai_validator.validate_with_ai(result["data"], transaction_type)
                    result["ai_validation"] = ai_validation
                    
                    # Check AI validation warnings
                    if ai_validation.get("anomalies"):
                        result["warnings"] = result.get("warnings", [])
                        result["warnings"].extend(ai_validation.get("anomalies", []))
                        logger.info(f"AI detected anomalies in {filepath}: {ai_validation.get('anomalies')}")
                
                if not validation_result.is_valid:
                    result["errors"].extend([
                        f"Validation error: {e.message}" 
                        for e in validation_result.errors
                    ])
                    logger.warning(f"Validation failed for {filepath}: {len(validation_result.errors)} error(s)")
            
            # Transform (if requested)
            if transform and result["data"]:
                # Apply any configured transformations
                transform_config = self.config.get("transformations", {})
                if transform_config:
                    result["data"] = self.transformer.apply_mapping(
                        result["data"],
                        transform_config
                    )
            
            # Deliver to Sterling
            if deliver:
                # Extract trading partner from envelope
                trading_partner = None
                if edi_type == "X12":
                    trading_partner = envelope.get_receiver_id()
                elif edi_type == "EDIFACT":
                    trading_partner = envelope.get_receiver_id()
                
                # Try file system delivery first
                if self.sterling.delivery_directories:
                    delivered = self.sterling.write_to_delivery(
                        filepath,
                        trading_partner=trading_partner
                    )
                    if delivered:
                        result["delivered"] = True
                        logger.info(f"File delivered to Sterling: {filepath}")
                    else:
                        result["errors"].append("Failed to deliver to Sterling")
                
                # Try API delivery if configured
                if self.sterling.api_base_url and trading_partner:
                    api_result = self.sterling.submit_file_via_api(
                        filepath,
                        trading_partner
                    )
                    if api_result.get("success"):
                        result["api_delivered"] = True
                        result["api_response"] = api_result
                    else:
                        result["errors"].append(f"API delivery failed: {api_result.get('error')}")
            
            # Sync to Acumatica if configured
            if self.acumatica and result.get("data"):
                try:
                    acumatica_config = self.config.get("acumatica", {})
                    if acumatica_config.get("auto_sync", False):
                        # Get transaction type from data
                        transaction_type = result["data"].get("transaction_type") or result["data"].get("message_type", "")
                        
                        # Sync customer to CRM
                        if self.acumatica_crm:
                            try:
                                self.acumatica_crm.sync_edi_customer_to_crm(result["data"])
                                result["crm_synced"] = True
                            except Exception as e:
                                logger.warning(f"CRM sync failed: {e}")
                        
                        # Create PO from EDI 850
                        if transaction_type == "850":
                            acumatica_result = self.acumatica.create_po_from_edi_850(result["data"])
                            result["acumatica_synced"] = True
                            result["acumatica_po"] = acumatica_result
                            logger.info(f"Created Acumatica PO from EDI 850: {filepath}")
                            
                            # Create CRM opportunity from PO
                            if self.acumatica_crm:
                                try:
                                    opp_result = self.acumatica_crm.create_opportunity_from_edi_order(result["data"])
                                    result["crm_opportunity"] = opp_result
                                    logger.info(f"Created CRM opportunity from EDI 850: {filepath}")
                                except Exception as e:
                                    logger.warning(f"CRM opportunity creation failed: {e}")
                        
                        # Create Invoice from EDI 810
                        elif transaction_type == "810":
                            acumatica_result = self.acumatica.create_invoice_from_edi_810(result["data"])
                            result["acumatica_synced"] = True
                            result["acumatica_invoice"] = acumatica_result
                            logger.info(f"Created Acumatica Invoice from EDI 810: {filepath}")
                        
                        # Log activity in CRM
                        if self.acumatica_crm:
                            try:
                                self.acumatica_crm.log_edi_activity(result["data"])
                            except Exception as e:
                                logger.warning(f"CRM activity logging failed: {e}")
                                
                except Exception as e:
                    # Use automated error handler
                    error_handling = self.error_handler.handle_error(e, {"context": "Acumatica sync"})
                    logger.warning(f"Acumatica sync failed: {e}")
                    result["errors"].append(f"Acumatica sync error: {str(e)}")
                    result["error_handling"] = error_handling
                    
                    # Retry if appropriate
                    if error_handling.get("retryable") and self.error_handler.should_retry(e, 1):
                        logger.info(f"Retrying Acumatica sync for {filepath}")
                        try:
                            # Retry logic would go here
                            pass
                        except Exception as retry_error:
                            logger.error(f"Retry failed: {retry_error}")
            
            # Move to processed directory
            if not result["errors"]:
                self.sterling.move_to_processed(filepath)
                result["success"] = True
            else:
                # Move to error directory
                self.sterling.move_to_error(filepath)
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)  # milliseconds
            result["processing_time_ms"] = processing_time
            
            # Extract transaction type and trading partner for metrics
            transaction_type = result["data"].get("transaction_type") or result["data"].get("message_type", "") if result.get("data") else ""
            trading_partner = None
            if edi_type == "X12" and envelope:
                trading_partner = envelope.get_receiver_id()
            elif edi_type == "EDIFACT" and envelope:
                trading_partner = envelope.get_receiver_id()
            
            # Record metrics
            metrics_data = {
                "transaction_type": transaction_type,
                "status": result["status"] if "status" in result else ("success" if result["success"] else "failed"),
                "processing_time": processing_time / 1000.0,  # Convert to seconds
                "file_name": Path(filepath).name,
                "trading_partner": trading_partner or "",
                "error_count": len(result.get("errors", []))
            }
            
            self.metrics_collector.record_processing(**metrics_data)
            
            # Update predictive analytics
            if transaction_type:
                self.predictive_analytics.record_processing_time(transaction_type, processing_time / 1000.0)
            
            # Store metrics in SQL Server if configured
            if self.sql_server:
                try:
                    from datetime import datetime
                    metrics_data["processed_date"] = datetime.now()
                    self.sql_server.store_edi_metrics(metrics_data)
                except Exception as e:
                    logger.warning(f"Failed to store metrics in SQL Server: {e}")
            
            # Update AI validator with historical data
            if result.get("data") and transaction_type:
                self.ai_validator.update_historical_data(transaction_type, result["data"])
            
            logger.info(f"File processing completed: {filepath} (success={result['success']})")
            
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}", exc_info=True)
            result["errors"].append(f"Processing error: {str(e)}")
            result["success"] = False
            
            # Calculate processing time even on error
            processing_time = int((time.time() - start_time) * 1000)
            result["processing_time_ms"] = processing_time
            
            # Record metric (even on error)
            try:
                metrics_data = {
                    "transaction_type": result.get("data", {}).get("transaction_type", "") if result.get("data") else "",
                    "status": "failed",
                    "processing_time": processing_time / 1000.0,
                    "file_name": Path(filepath).name,
                    "trading_partner": "",
                    "error_count": len(result.get("errors", []))
                }
                self.metrics_collector.record_processing(**metrics_data)
                
                # Store in SQL Server if configured
                if self.sql_server:
                    from datetime import datetime
                    metrics_data["processed_date"] = datetime.now()
                    self.sql_server.store_edi_metrics(metrics_data)
            except:
                pass
            
            # Move to error directory
            try:
                self.sterling.move_to_error(filepath)
            except:
                pass
        
        return result
    
    def process_directory(self, directory: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Process all EDI files in a directory.
        
        Args:
            directory: Directory path
            **kwargs: Additional arguments passed to process_file
            
        Returns:
            List of processing results
        """
        results = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return results
        
        # Find EDI files
        edi_extensions = ['.edi', '.x12', '.edifact', '.txt']
        for filepath in dir_path.glob('*'):
            if filepath.is_file() and filepath.suffix.lower() in edi_extensions:
                result = self.process_file(str(filepath), **kwargs)
                results.append(result)
        
        logger.info(f"Processed {len(results)} file(s) from {directory}")
        return results
    
    def batch_process(self, filepaths: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Process multiple files in batch.
        
        Args:
            filepaths: List of file paths
            **kwargs: Additional arguments passed to process_file
            
        Returns:
            List of processing results
        """
        results = []
        
        for filepath in filepaths:
            result = self.process_file(filepath, **kwargs)
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r["success"])
        logger.info(f"Batch processing complete: {successful}/{len(results)} successful")
        
        return results

