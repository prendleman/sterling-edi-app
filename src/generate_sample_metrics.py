"""
Generate sample metrics data for testing Power BI dashboard.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import random

from .metrics_collector import MetricsCollector, ProcessingMetric


def generate_sample_metrics(count: int = 100, output_path: str = "metrics") -> None:
    """
    Generate sample EDI processing metrics for testing.
    
    Args:
        count: Number of sample records to generate
        output_path: Path to store metrics
    """
    collector = MetricsCollector(storage_path=output_path, use_database=True)
    
    # Sample data
    edi_types = ["X12", "EDIFACT"]
    transaction_types = ["850", "855", "810", "856", "ORDERS", "DESADV", "INVOIC"]
    trading_partners = ["ACME Corp", "Global Suppliers", "Tech Distributors", "Retail Partners", "Manufacturing Co"]
    statuses = ["success", "failed"]
    
    base_date = datetime.now() - timedelta(days=30)
    
    print(f"Generating {count} sample metrics...")
    
    for i in range(count):
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        timestamp = (base_date + timedelta(days=days_ago, hours=random.randint(0, 23))).isoformat()
        
        edi_type = random.choice(edi_types)
        transaction_type = random.choice(transaction_types)
        trading_partner = random.choice(trading_partners)
        status = random.choice(statuses)
        
        # Success rate should be higher (80% success)
        if random.random() < 0.8:
            status = "success"
        
        processing_time = random.randint(100, 5000)  # 100ms to 5 seconds
        error_count = random.randint(0, 5) if status == "failed" else random.randint(0, 1)
        warning_count = random.randint(0, 3)
        validation_passed = status == "success" or random.random() < 0.7
        delivered = status == "success" or random.random() < 0.9
        
        metric = ProcessingMetric(
            timestamp=timestamp,
            filepath=f"/sterling/pickup/file_{i:04d}.{transaction_type.lower()}",
            edi_type=edi_type,
            transaction_type=transaction_type,
            trading_partner=trading_partner,
            status=status,
            processing_time_ms=processing_time,
            error_count=error_count,
            warning_count=warning_count,
            validation_passed=validation_passed,
            delivered_to_sterling=delivered
        )
        
        collector._save_to_database(metric)
        
        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{count} metrics...")
    
    print(f"✓ Generated {count} sample metrics")
    
    # Export for Power BI
    powerbi_file = collector.export_for_powerbi()
    print(f"✓ Exported metrics to: {powerbi_file}")
    
    # Print summary
    summary = collector.get_summary_stats()
    print(f"\nSummary Statistics:")
    print(f"  Total Files: {summary['total_files']}")
    print(f"  Success: {summary['success_count']} ({summary['success_rate']}%)")
    print(f"  Failed: {summary['failed_count']}")
    print(f"  Avg Processing Time: {summary['avg_processing_time_ms']:.2f} ms")


if __name__ == "__main__":
    generate_sample_metrics(count=100)

