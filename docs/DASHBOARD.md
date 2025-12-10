# Power BI Dashboard Guide

## Overview

The IBM Sterling EDI Application includes a Power BI dashboard generator that creates comprehensive visualizations of EDI processing metrics. The dashboard provides real-time insights into processing performance, pass/fail rates, error analysis, and trading partner statistics.

## Features

### Dashboard Pages

1. **Overview Dashboard**
   - Total files processed
   - Success and failure counts
   - Success rate gauge
   - Pass/Fail distribution (donut chart)
   - Transaction type distribution (pie chart)

2. **Pass/Fail Analysis**
   - Overall success rate gauge
   - Pass/Fail breakdown by transaction type
   - Pass/Fail breakdown by trading partner
   - Pass/Fail trends over time

3. **Transaction Type Analysis**
   - Transaction type distribution
   - Files processed by transaction type
   - Success rate by transaction type
   - Detailed transaction metrics table

4. **Time Series Analysis**
   - Processing volume trends
   - Success/Fail trends over time
   - Average processing time trends
   - Error count trends

5. **Error Analysis**
   - Total errors and warnings
   - Errors by transaction type
   - Error trends over time
   - Detailed error metrics table

## Generating the Dashboard

### Step 1: Collect Metrics

Metrics are automatically collected when processing EDI files:

```bash
# Process files (metrics collected automatically)
python main.py process --directory /path/to/edi/files
```

### Step 2: Generate Sample Data (Optional)

For testing or demonstration purposes, generate sample metrics:

```bash
python main.py dashboard --generate-sample-metrics
```

This creates 100 sample processing records with realistic distributions.

### Step 3: Generate Dashboard

Generate the Power BI dashboard:

```bash
python main.py dashboard
```

This creates a `.pbip` file in the `dashboards/` directory.

### Step 4: Open in Power BI Desktop

1. Open **Power BI Desktop**
2. Go to **File > Open > Browse**
3. Navigate to `dashboards/EDIProcessingDashboard.pbip`
4. Click **Open**
5. The dashboard will load with your metrics data

## Metrics Data

### Data Storage

Metrics are stored in:
- **SQLite Database**: `metrics/metrics.db` (default)
- **JSON Export**: `metrics/powerbi_data.json` (for Power BI import)

### Metrics Collected

For each processed file, the following metrics are recorded:

- **Timestamp**: When the file was processed
- **Filepath**: Source file location
- **EDI Type**: X12 or EDIFACT
- **Transaction Type**: 850, 855, 810, ORDERS, etc.
- **Trading Partner**: Partner identifier
- **Status**: success or failed
- **Processing Time**: Time taken in milliseconds
- **Error Count**: Number of validation errors
- **Warning Count**: Number of warnings
- **Validation Passed**: Boolean flag
- **Delivered to Sterling**: Boolean flag

## Dashboard Customization

### Modifying Visualizations

The dashboard is generated programmatically. To customize:

1. Edit `src/powerbi_dashboard.py`
2. Modify the visualization methods:
   - `_create_overview_page()`
   - `_create_pass_fail_page()`
   - `_create_transaction_type_page()`
   - `_create_timeseries_page()`
   - `_create_error_analysis_page()`

3. Regenerate the dashboard:
```bash
python main.py dashboard
```

### Adding New Measures

To add new DAX measures:

1. Edit `src/powerbi_dashboard.py`
2. Add measures to the `measures` array in `_create_semantic_model()`
3. Regenerate the dashboard

Example:
```python
{
    "name": "Custom Measure",
    "expression": "SUM(ProcessingMetrics[ProcessingTimeMs]) / COUNTROWS(ProcessingMetrics)",
    "formatString": "#,##0.00",
    "lineageTag": guid()
}
```

## Configuration

### Metrics Collection Settings

Edit `config/config.yaml`:

```yaml
metrics:
  enabled: true
  storage_path: "metrics"
  use_database: true  # Use SQLite (True) or JSON (False)
```

### Dashboard Output Location

The dashboard is generated in the `dashboards/` directory by default. To change:

Edit `src/powerbi_dashboard.py`:
```python
generator = PowerBIDashboardGenerator(
    output_dir="custom/path",  # Change this
    metrics_collector=metrics_collector
)
```

## Troubleshooting

### Dashboard Won't Open

1. **Check Power BI Desktop Version**: Ensure you have Power BI Desktop installed (latest version recommended)

2. **Check File Path**: Ensure the `.pbip` file exists and path is correct

3. **Check Metrics Data**: Verify metrics exist:
```bash
# Check database
sqlite3 metrics/metrics.db "SELECT COUNT(*) FROM processing_metrics;"

# Or check JSON
cat metrics/powerbi_data.json
```

4. **Regenerate Dashboard**: Try regenerating:
```bash
python main.py dashboard
```

### No Data in Dashboard

1. **Generate Sample Data**: If you haven't processed any files:
```bash
python main.py dashboard --generate-sample-metrics
```

2. **Check Metrics Collection**: Ensure metrics collection is enabled in config

3. **Process Some Files**: Process actual EDI files to collect real metrics

### Visualizations Not Displaying

1. **Check Data Model**: Open Power BI Desktop and verify the data model loaded correctly

2. **Check Measures**: Verify DAX measures are correct in the model

3. **Refresh Data**: In Power BI Desktop, click **Refresh** to reload data

## Best Practices

1. **Regular Dashboard Updates**: Regenerate dashboard periodically to include latest metrics

2. **Data Retention**: Consider archiving old metrics periodically to maintain performance

3. **Backup Metrics**: Backup the `metrics/` directory regularly

4. **Custom Dashboards**: Create multiple dashboards for different audiences (executive, operations, technical)

## Advanced Usage

### Exporting Metrics

Export metrics for external analysis:

```python
from src.metrics_collector import MetricsCollector

collector = MetricsCollector()
metrics = collector.get_metrics(
    start_date="2024-01-01",
    end_date="2024-12-31",
    status="success"
)

# Export to CSV
import pandas as pd
df = pd.DataFrame(metrics)
df.to_csv("metrics_export.csv", index=False)
```

### Custom Queries

Query specific metrics:

```python
from src.metrics_collector import MetricsCollector

collector = MetricsCollector()

# Get metrics by transaction type
metrics_850 = collector.get_metrics(transaction_type="850")

# Get failed files
failed = collector.get_metrics(status="failed")

# Get summary statistics
summary = collector.get_summary_stats()
print(f"Success Rate: {summary['success_rate']}%")
```

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review the metrics database directly
3. Verify Power BI Desktop is up to date
4. Consult Power BI documentation for visualization customization

