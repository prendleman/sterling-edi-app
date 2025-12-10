"""
Integration Examples
Practical examples showing how to use the EDI application with various integrations.
"""

from src.edi_processor import EDIProcessor
from src.acumatica_connector import AcumaticaConnector
from src.acumatica_crm_integration import AcumaticaCRMIntegration
from src.ecommerce_connector import ECommerceConnector
from src.sql_server_integration import SQLServerIntegration
from src.ai_automation import PredictiveAnalytics
from src.security_audit import SecurityAudit, ComplianceReporter
import yaml


def example_1_basic_edi_processing():
    """Example 1: Basic EDI file processing."""
    print("Example 1: Basic EDI Processing")
    print("-" * 50)
    
    # Load configuration
    with open("config/config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize processor
    processor = EDIProcessor(config)
    
    # Process a single file
    result = processor.process_file("tests/sample_data/sample_850.x12")
    
    if result["success"]:
        print(f"✓ Successfully processed: {result['filepath']}")
        print(f"  Transaction Type: {result['data'].get('transaction_type')}")
    else:
        print(f"✗ Failed: {result['errors']}")


def example_2_acumatica_integration():
    """Example 2: Acumatica ERP integration."""
    print("\nExample 2: Acumatica Integration")
    print("-" * 50)
    
    # Initialize Acumatica connector
    acumatica = AcumaticaConnector(
        base_url="https://your-instance.acumatica.com",
        username="admin",
        password="password"
    )
    
    # Get sales orders
    orders = acumatica.get_sales_orders(status="Open")
    print(f"Found {len(orders)} open sales orders")
    
    # Get inventory
    inventory = acumatica.get_inventory_items()
    print(f"Found {len(inventory)} inventory items")


def example_3_crm_integration():
    """Example 3: Acumatica CRM integration."""
    print("\nExample 3: CRM Integration")
    print("-" * 50)
    
    # Initialize connectors
    acumatica = AcumaticaConnector(
        base_url="https://your-instance.acumatica.com",
        username="admin",
        password="password"
    )
    crm = AcumaticaCRMIntegration(acumatica)
    
    # Get sales pipeline
    pipeline = crm.get_sales_pipeline_summary()
    print(f"Total Opportunities: {pipeline['total_opportunities']}")
    print(f"Pipeline Value: ${pipeline['total_pipeline_value']:,.2f}")
    
    # Get account 360 view
    account_view = crm.get_account_360_view("CUSTOMER001")
    print(f"Account Contacts: {len(account_view['contacts'])}")
    print(f"Account Opportunities: {len(account_view['opportunities'])}")


def example_4_ecommerce_sync():
    """Example 4: eCommerce order sync."""
    print("\nExample 4: eCommerce Integration")
    print("-" * 50)
    
    # Initialize eCommerce connector (Shopify example)
    shopify = ECommerceConnector(
        platform="shopify",
        base_url="https://your-store.myshopify.com",
        access_token="your-access-token"
    )
    
    # Get recent orders
    orders = shopify.get_orders(status="pending", limit=10)
    print(f"Found {len(orders)} pending orders")
    
    # Convert to Acumatica format
    if orders:
        acumatica_order = shopify.sync_order_to_acumatica_format(orders[0])
        print(f"Converted order {orders[0].get('order_number')} to Acumatica format")


def example_5_sql_server_metrics():
    """Example 5: SQL Server metrics storage."""
    print("\nExample 5: SQL Server Integration")
    print("-" * 50)
    
    # Initialize SQL Server connector
    sql_server = SQLServerIntegration(
        server="localhost",
        database="EDI_Metrics",
        use_windows_auth=True
    )
    
    # Create metrics table
    sql_server.create_metrics_table()
    
    # Get metrics summary
    summary = sql_server.get_edi_metrics_summary()
    print(f"Total Transactions: {summary['total_transactions']}")
    print(f"Average Processing Time: {summary['average_processing_time']:.2f}s")


def example_6_ai_predictive_analytics():
    """Example 6: AI predictive analytics."""
    print("\nExample 6: Predictive Analytics")
    print("-" * 50)
    
    # Initialize predictive analytics
    analytics = PredictiveAnalytics()
    
    # Record some processing times
    analytics.record_processing_time("850", 2.5)
    analytics.record_processing_time("850", 2.8)
    analytics.record_processing_time("850", 2.3)
    
    # Predict processing time
    predicted_time, confidence = analytics.predict_processing_time("850")
    print(f"Predicted Processing Time: {predicted_time:.2f}s (±{confidence:.2f}s)")
    
    # Get insights
    insights = analytics.get_processing_insights()
    print(f"Recommendations: {insights['recommendations']}")


def example_7_security_audit():
    """Example 7: Security audit and compliance."""
    print("\nExample 7: Security Audit")
    print("-" * 50)
    
    # Initialize security audit
    audit = SecurityAudit()
    
    # Log access
    audit.log_access("admin", "EDI_Processor", "process_file", True)
    audit.log_data_access("admin", "EDI_Transactions", 100)
    
    # Generate compliance report
    reporter = ComplianceReporter(audit)
    access_report = reporter.generate_access_report("2025-01-01", "2025-12-31")
    print(f"Total Access Attempts: {access_report['total_access_attempts']}")
    print(f"Successful: {access_report['successful']}")
    
    # Export compliance report
    audit.export_compliance_report("compliance_report.csv", "2025-01-01", "2025-12-31")
    print("Compliance report exported")


def example_8_end_to_end_workflow():
    """Example 8: Complete end-to-end workflow."""
    print("\nExample 8: End-to-End Workflow")
    print("-" * 50)
    
    # Load configuration
    with open("config/config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize processor (with all integrations)
    processor = EDIProcessor(config)
    
    # Process EDI file
    result = processor.process_file("tests/sample_data/sample_850.x12")
    
    if result["success"]:
        print("✓ EDI file processed")
        print(f"  - Sterling: {'Delivered' if result.get('delivered') else 'Not delivered'}")
        print(f"  - Acumatica: {'Synced' if result.get('acumatica_synced') else 'Not synced'}")
        print(f"  - CRM: {'Synced' if result.get('crm_synced') else 'Not synced'}")
        print(f"  - SQL Server: {'Stored' if result.get('sql_stored') else 'Not stored'}")


if __name__ == "__main__":
    print("=" * 60)
    print("EDI Application Integration Examples")
    print("=" * 60)
    
    # Run examples (comment out ones that require actual connections)
    example_1_basic_edi_processing()
    # example_2_acumatica_integration()  # Requires Acumatica instance
    # example_3_crm_integration()  # Requires Acumatica instance
    # example_4_ecommerce_sync()  # Requires eCommerce platform
    # example_5_sql_server_metrics()  # Requires SQL Server
    example_6_ai_predictive_analytics()
    example_7_security_audit()
    # example_8_end_to_end_workflow()  # Requires all integrations configured
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)

