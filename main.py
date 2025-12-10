#!/usr/bin/env python3
"""
IBM Sterling EDI Application
Main entry point for EDI processing.
"""

import sys
import argparse
import yaml
import logging
from pathlib import Path

from src.edi_processor import EDIProcessor
from src.file_monitor import FileMonitor, PollingFileMonitor
from src.powerbi_dashboard import PowerBIDashboardGenerator
from src.powerbi_financial_dashboards import PowerBIFinancialDashboardGenerator
from src.metrics_collector import MetricsCollector
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}


def load_sterling_config(config_path: str = "config/sterling_config.yaml") -> dict:
    """Load Sterling configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.warning(f"Error loading Sterling config: {e}")
        return {}


def load_acumatica_config(config_path: str = "config/acumatica_config.yaml") -> dict:
    """Load Acumatica configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.warning(f"Error loading Acumatica config: {e}")
        return {}


def load_ecommerce_config(config_path: str = "config/ecommerce_config.yaml") -> dict:
    """Load eCommerce configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.warning(f"Error loading eCommerce config: {e}")
        return {}


def load_sql_server_config(config_path: str = "config/sql_server_config.yaml") -> dict:
    """Load SQL Server configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.warning(f"Error loading SQL Server config: {e}")
        return {}


def merge_configs(base_config: dict, sterling_config: dict, acumatica_config: dict = None,
                 ecommerce_config: dict = None, sql_server_config: dict = None) -> dict:
    """Merge all configurations."""
    merged = base_config.copy()
    
    # Merge Sterling config
    if sterling_config:
        merged["sterling"] = {
            "pickup_directories": sterling_config.get("file_system", {}).get("pickup_directories", []),
            "delivery_directories": sterling_config.get("file_system", {}).get("delivery_directories", []),
            "api_base_url": sterling_config.get("api", {}).get("base_url"),
            "api_username": sterling_config.get("api", {}).get("username"),
            "api_password": sterling_config.get("api", {}).get("password")
        }
    
    # Merge Acumatica config
    if acumatica_config:
        acumatica_settings = acumatica_config.get("acumatica", {})
        merged["acumatica"] = {
            "enabled": acumatica_settings.get("enabled", False),
            "base_url": acumatica_settings.get("base_url"),
            "username": acumatica_settings.get("username"),
            "password": acumatica_settings.get("password"),
            "tenant": acumatica_settings.get("tenant"),
            "branch": acumatica_settings.get("branch"),
            "auto_sync": acumatica_settings.get("auto_sync", False)
        }
    
    # Merge eCommerce config
    if ecommerce_config:
        ecommerce_settings = ecommerce_config.get("ecommerce", {})
        merged["ecommerce"] = {
            "enabled": ecommerce_settings.get("enabled", False),
            "platform": ecommerce_settings.get("platform"),
            "base_url": ecommerce_settings.get("base_url"),
            "api_key": ecommerce_settings.get("api_key"),
            "api_secret": ecommerce_settings.get("api_secret"),
            "access_token": ecommerce_settings.get("access_token")
        }
    
    # Merge SQL Server config
    if sql_server_config:
        sql_settings = sql_server_config.get("sql_server", {})
        merged["sql_server"] = {
            "enabled": sql_settings.get("enabled", False),
            "server": sql_settings.get("server"),
            "database": sql_settings.get("database"),
            "username": sql_settings.get("username"),
            "password": sql_settings.get("password"),
            "use_windows_auth": sql_settings.get("use_windows_auth", True),
            "driver": sql_settings.get("driver", "ODBC Driver 17 for SQL Server"),
            "auto_create_tables": sql_settings.get("auto_create_tables", True)
        }
    
    return merged


def process_single_file(filepath: str, config: dict):
    """Process a single EDI file."""
    processor = EDIProcessor(config)
    result = processor.process_file(filepath)
    
    if result["success"]:
        print(f"✓ Successfully processed: {filepath}")
        if result.get("data"):
            print(f"  EDI Type: {result['edi_type']}")
            print(f"  Transaction/Message: {result['data'].get('transaction_type') or result['data'].get('message_type')}")
    else:
        print(f"✗ Failed to process: {filepath}")
        for error in result.get("errors", []):
            print(f"  Error: {error}")
    
    return result


def process_directory(directory: str, config: dict):
    """Process all EDI files in a directory."""
    processor = EDIProcessor(config)
    results = processor.process_directory(directory)
    
    successful = sum(1 for r in results if r["success"])
    print(f"\nProcessed {successful}/{len(results)} files successfully")
    
    return results


def monitor_directories(config: dict, sterling_config: dict):
    """Start monitoring directories for new files."""
    processor = EDIProcessor(config)
    
    # Get watch directories
    watch_dirs = config.get("monitoring", {}).get("watch_directories", [])
    if not watch_dirs:
        watch_dirs = sterling_config.get("file_system", {}).get("pickup_directories", [])
    
    if not watch_dirs:
        logger.error("No watch directories configured")
        return
    
    def process_callback(filepath: str):
        """Callback for file processing."""
        result = processor.process_file(filepath)
        if result["success"]:
            logger.info(f"Successfully processed: {filepath}")
        else:
            logger.error(f"Failed to process: {filepath}")
    
    # Try to use watchdog-based monitor, fall back to polling
    try:
        monitor = FileMonitor(
            watch_directories=watch_dirs,
            callback=process_callback,
            file_extensions=config.get("processing", {}).get("file_extensions"),
            recursive=config.get("monitoring", {}).get("recursive", True)
        )
        monitor.start()
        print(f"Monitoring directories: {', '.join(watch_dirs)}")
        print("Press Ctrl+C to stop...")
        
        try:
            while monitor.is_alive():
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            monitor.stop()
    except ImportError:
        logger.warning("watchdog not available, using polling monitor")
        monitor = PollingFileMonitor(
            watch_directories=watch_dirs,
            callback=process_callback,
            file_extensions=config.get("processing", {}).get("file_extensions"),
            poll_interval=config.get("monitoring", {}).get("poll_interval", 5.0)
        )
        monitor.start()
        print(f"Polling directories: {', '.join(watch_dirs)}")
        print("Press Ctrl+C to stop...")
        
        try:
            while monitor.is_running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            monitor.stop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="IBM Sterling EDI Processing Application"
    )
    parser.add_argument(
        "command",
        choices=["process", "monitor", "validate", "dashboard", "financial-dashboards"],
        help="Command to execute"
    )
    parser.add_argument(
        "-f", "--file",
        help="Process a single file"
    )
    parser.add_argument(
        "-d", "--directory",
        help="Process all files in a directory"
    )
    parser.add_argument(
        "-c", "--config",
        default="config/config.yaml",
        help="Configuration file path"
    )
    parser.add_argument(
        "-s", "--sterling-config",
        default="config/sterling_config.yaml",
        help="Sterling configuration file path"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation"
    )
    parser.add_argument(
        "--no-deliver",
        action="store_true",
        help="Skip delivery to Sterling"
    )
    parser.add_argument(
        "--generate-sample-metrics",
        action="store_true",
        help="Generate sample metrics data (for dashboard testing)"
    )
    
    args = parser.parse_args()
    
    # Load configurations
    config = load_config(args.config)
    sterling_config = load_sterling_config(args.sterling_config)
    acumatica_config = load_acumatica_config("config/acumatica_config.yaml")
    ecommerce_config = load_ecommerce_config("config/ecommerce_config.yaml")
    sql_server_config = load_sql_server_config("config/sql_server_config.yaml")
    config = merge_configs(config, sterling_config, acumatica_config, ecommerce_config, sql_server_config)
    
    # Set log level
    log_level = config.get("app", {}).get("log_level", "INFO")
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    # Execute command
    if args.command == "process":
        if args.file:
            process_single_file(
                args.file,
                config
            )
        elif args.directory:
            process_directory(
                args.directory,
                config
            )
        else:
            parser.error("Must specify either --file or --directory")
    
    elif args.command == "monitor":
        monitor_directories(config, sterling_config)
    
    elif args.command == "validate":
        if not args.file:
            parser.error("--file required for validate command")
        
        from src.edi_validator import EDIValidator
        validator = EDIValidator()
        
        with open(args.file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        result = validator.validate(content)
        summary = result.get_summary()
        
        print(f"Validation Result: {'VALID' if summary['is_valid'] else 'INVALID'}")
        print(f"Errors: {summary['error_count']}")
        print(f"Warnings: {summary['warning_count']}")
        
        if summary['errors']:
            print("\nErrors:")
            for error in summary['errors']:
                print(f"  - {error['message']}")
        
        if summary['warnings']:
            print("\nWarnings:")
            for warning in summary['warnings']:
                print(f"  - {warning['message']}")
    
    elif args.command == "dashboard":
        # Generate sample metrics if requested
        if args.generate_sample_metrics:
            from src.generate_sample_metrics import generate_sample_metrics
            print("Generating sample metrics data...")
            generate_sample_metrics(count=100)
            print("\nSample metrics generated. Generating dashboard...\n")
        
        # Generate Power BI dashboard
        metrics_collector = MetricsCollector(
            storage_path=config.get("metrics", {}).get("storage_path", "metrics"),
            use_database=config.get("metrics", {}).get("use_database", True)
        )
        
        generator = PowerBIDashboardGenerator(
            output_dir="dashboards",
            metrics_collector=metrics_collector
        )
        
        dashboard_name = "EDIProcessingDashboard"
        pbip_file = generator.generate_dashboard(dashboard_name)
        
        print(f"\n✓ Power BI dashboard generated: {pbip_file}")
        print(f"\nTo view the dashboard:")
        print(f"1. Open Power BI Desktop")
        print(f"2. File > Open > Browse")
        print(f"3. Navigate to: {pbip_file}")
        print(f"4. The dashboard will load with your EDI processing metrics")
    
    elif args.command == "financial-dashboards":
        # Generate financial dashboards
        generator = PowerBIFinancialDashboardGenerator(output_dir="dashboards")
        
        print("Generating financial dashboards...")
        dashboards = generator.generate_all_dashboards()
        
        print(f"\n✓ Generated {len(dashboards)} financial dashboards:")
        for dashboard in dashboards:
            print(f"  - {dashboard}")
        
        print(f"\nTo view the dashboards:")
        print(f"1. Open Power BI Desktop")
        print(f"2. File > Open > Browse")
        print(f"3. Navigate to: dashboards/")
        print(f"4. Open any of the generated .pbip files")


if __name__ == "__main__":
    main()

