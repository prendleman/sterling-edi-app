"""
Power BI Dashboard Generator
Generates Power BI PBIX files programmatically for EDI processing metrics.
Based on PBIP generator approach from aq_wp_selenium_bot.
"""

import json
import uuid
import shutil
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


def guid():
    """Generate a GUID."""
    return str(uuid.uuid4())


# EDI Application Brand Colors
EDI_COLORS = {
    "success_green": "#4A9B4A",
    "error_red": "#D32F2F",
    "warning_orange": "#FF9800",
    "navy": "#1B365D",
    "light_blue": "#2196F3",
    "neutral": "#F5F5F5",
    "white": "#FFFFFF",
    "dark_gray": "#424242"
}


class PowerBIDashboardGenerator:
    """Generates Power BI PBIX files for EDI processing metrics."""
    
    def __init__(self, output_dir: str = "dashboards", metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize Power BI dashboard generator.
        
        Args:
            output_dir: Directory to output PBIX files
            metrics_collector: MetricsCollector instance (creates new if None)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Load branding configuration
        self.branding = self._load_branding()
    
    def _load_branding(self) -> Dict[str, Any]:
        """Load branding configuration."""
        try:
            branding_path = Path("config/branding.yaml")
            if branding_path.exists():
                with open(branding_path, 'r') as f:
                    branding = yaml.safe_load(f)
                    return branding.get("branding", {})
        except Exception as e:
            logger.warning(f"Could not load branding config: {e}")
        
        return {}
    
    def _get_brand_colors(self) -> Dict[str, str]:
        """Get brand colors, fallback to default EDI colors."""
        if self.branding.get("colors"):
            colors = self.branding["colors"]
            return {
                "success_green": colors.get("success", EDI_COLORS["success_green"]),
                "error_red": colors.get("error", EDI_COLORS["error_red"]),
                "warning_orange": colors.get("warning", EDI_COLORS["warning_orange"]),
                "navy": colors.get("primary", EDI_COLORS["navy"]),
                "light_blue": colors.get("accent", EDI_COLORS["light_blue"]),
                "neutral": colors.get("background_light", EDI_COLORS["neutral"]),
                "white": colors.get("background", EDI_COLORS["white"]),
                "dark_gray": colors.get("text", EDI_COLORS["dark_gray"])
            }
        return EDI_COLORS
    
    def _get_company_name(self) -> str:
        """Get company name for branding."""
        return self.branding.get("company_name", "EDI Processing")
    
    def generate_dashboard(self, name: str = "EDIProcessingDashboard") -> str:
        """
        Generate Power BI dashboard PBIX file.
        
        Args:
            name: Dashboard name
            
        Returns:
            Path to generated PBIX file
        """
        logger.info(f"Generating Power BI dashboard: {name}")
        
        # Export metrics for Power BI
        metrics_file = self.metrics_collector.export_for_powerbi()
        
        # Create PBIP structure
        report_dir = self.output_dir / f"{name}.Report"
        model_dir = self.output_dir / f"{name}.SemanticModel"
        
        # Clean up if exists
        if report_dir.exists():
            shutil.rmtree(report_dir)
        if model_dir.exists():
            shutil.rmtree(model_dir)
        
        report_dir.mkdir(parents=True, exist_ok=True)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Create .pbip main file
        pbip_file = self.output_dir / f"{name}.pbip"
        with open(pbip_file, 'w', encoding='utf-8') as f:
            json.dump({
                "version": "1.0",
                "artifacts": [{"report": {"path": f"{name}.Report"}}],
                "settings": {"enableAutoRecovery": True}
            }, f, indent=2)
        
        # 2. Create .platform files
        self._create_platform_file(report_dir, name, "Report")
        self._create_platform_file(model_dir, name, "SemanticModel")
        
        # 3. Create definition.pbir
        with open(report_dir / "definition.pbir", 'w', encoding='utf-8') as f:
            json.dump({
                "version": "4.0",
                "datasetReference": {
                    "byPath": {"path": f"../{name}.SemanticModel"},
                    "byConnection": None
                }
            }, f, indent=2)
        
        # 4. Create semantic model (data model)
        self._create_semantic_model(model_dir, name, metrics_file)
        
        # 5. Create report pages with visuals
        self._create_report_pages(report_dir, name)
        
        logger.info(f"Dashboard generated: {pbip_file}")
        return str(pbip_file)
    
    def _create_platform_file(self, path: Path, display_name: str, ptype: str):
        """Create .platform file."""
        platform_dir = path / ".platform"
        platform_dir.mkdir(exist_ok=True)
        with open(platform_dir / "platform.json", 'w', encoding='utf-8') as f:
            json.dump({
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                "metadata": {"type": ptype, "displayName": display_name},
                "config": {"version": "2.0", "logicalId": guid()}
            }, f, indent=2)
    
    def _create_semantic_model(self, model_dir: Path, name: str, metrics_file: str):
        """Create semantic model with tables and measures."""
        # Get absolute path to metrics file
        metrics_path = Path(metrics_file).absolute()
        metrics_dir = metrics_path.parent
        
        # Create model.bim file (Tabular model) - using proper Power BI format
        model_bim = {
            "name": name,
            "compatibilityLevel": 1567,
            "model": {
                "culture": "en-US",
                "dataAccessOptions": {
                    "legacyRedirects": True,
                    "returnErrorValuesAsNull": True
                },
                "defaultPowerBIDataSourceVersion": "powerBI_V3",
                "sourceQueryCulture": "en-US",
                "expressions": [{
                    "name": "MetricsDataFolder",
                    "kind": "m",
                    "expression": [f"let Source = \"{metrics_dir}\" in Source"]
                }],
                "tables": [
                    {
                        "name": "ProcessingMetrics",
                        "lineageTag": guid(),
                        "columns": [
                            {"name": "Date", "dataType": "dateTime", "sourceColumn": "Date", "lineageTag": guid()},
                            {"name": "Time", "dataType": "string", "sourceColumn": "Time", "lineageTag": guid()},
                            {"name": "DateTime", "dataType": "dateTime", "sourceColumn": "DateTime", "lineageTag": guid()},
                            {"name": "Filepath", "dataType": "string", "sourceColumn": "Filepath", "lineageTag": guid()},
                            {"name": "EDIType", "dataType": "string", "sourceColumn": "EDIType", "lineageTag": guid()},
                            {"name": "TransactionType", "dataType": "string", "sourceColumn": "TransactionType", "lineageTag": guid()},
                            {"name": "TradingPartner", "dataType": "string", "sourceColumn": "TradingPartner", "lineageTag": guid()},
                            {"name": "Status", "dataType": "string", "sourceColumn": "Status", "lineageTag": guid()},
                            {"name": "ProcessingTimeMs", "dataType": "int64", "sourceColumn": "ProcessingTimeMs", "lineageTag": guid()},
                            {"name": "ErrorCount", "dataType": "int64", "sourceColumn": "ErrorCount", "lineageTag": guid()},
                            {"name": "WarningCount", "dataType": "int64", "sourceColumn": "WarningCount", "lineageTag": guid()},
                            {"name": "ValidationPassed", "dataType": "boolean", "sourceColumn": "ValidationPassed", "lineageTag": guid()},
                            {"name": "DeliveredToSterling", "dataType": "boolean", "sourceColumn": "DeliveredToSterling", "lineageTag": guid()},
                            {"name": "IsSuccess", "dataType": "int64", "sourceColumn": "IsSuccess", "lineageTag": guid()},
                            {"name": "IsFailed", "dataType": "int64", "sourceColumn": "IsFailed", "lineageTag": guid()}
                        ],
                        "measures": [
                            {
                                "name": "Total Files",
                                "expression": "COUNTROWS(ProcessingMetrics)",
                                "formatString": "#,##0",
                                "lineageTag": guid()
                            },
                            {
                                "name": "Success Count",
                                "expression": "SUM(ProcessingMetrics[IsSuccess])",
                                "formatString": "#,##0",
                                "lineageTag": guid()
                            },
                            {
                                "name": "Failed Count",
                                "expression": "SUM(ProcessingMetrics[IsFailed])",
                                "formatString": "#,##0",
                                "lineageTag": guid()
                            },
                            {
                                "name": "Success Rate",
                                "expression": "DIVIDE([Success Count], [Total Files], 0) * 100",
                                "formatString": "0.00%",
                                "lineageTag": guid()
                            },
                            {
                                "name": "Avg Processing Time",
                                "expression": "AVERAGE(ProcessingMetrics[ProcessingTimeMs])",
                                "formatString": "#,##0",
                                "lineageTag": guid()
                            },
                            {
                                "name": "Total Errors",
                                "expression": "SUM(ProcessingMetrics[ErrorCount])",
                                "formatString": "#,##0",
                                "lineageTag": guid()
                            },
                            {
                                "name": "Total Warnings",
                                "expression": "SUM(ProcessingMetrics[WarningCount])",
                                "formatString": "#,##0",
                                "lineageTag": guid()
                            }
                        ],
                        "partitions": [{
                            "name": "ProcessingMetrics",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f"    Source = Folder.Files(MetricsDataFolder),",
                                    f"    MetricsFile = Source{{[Name=\"{metrics_path.name}\"]}}[Content],",
                                    "    ImportedJSON = Json.Document(MetricsFile),",
                                    "    ToTable = Table.FromList(ImportedJSON, Splitter.SplitByNothing(), null, null, ExtraValues.Error),",
                                    "    Expanded = Table.ExpandRecordColumn(ToTable, \"Column1\", {\"Date\", \"Time\", \"DateTime\", \"Filepath\", \"EDIType\", \"TransactionType\", \"TradingPartner\", \"Status\", \"ProcessingTimeMs\", \"ErrorCount\", \"WarningCount\", \"ValidationPassed\", \"DeliveredToSterling\", \"IsSuccess\", \"IsFailed\"}, {\"Date\", \"Time\", \"DateTime\", \"Filepath\", \"EDIType\", \"TransactionType\", \"TradingPartner\", \"Status\", \"ProcessingTimeMs\", \"ErrorCount\", \"WarningCount\", \"ValidationPassed\", \"DeliveredToSterling\", \"IsSuccess\", \"IsFailed\"}),",
                                    "    ChangedTypes = Table.TransformColumnTypes(Expanded, {{\"Date\", type date}, {\"Time\", type text}, {\"DateTime\", type datetime}, {\"Filepath\", type text}, {\"EDIType\", type text}, {\"TransactionType\", type text}, {\"TradingPartner\", type text}, {\"Status\", type text}, {\"ProcessingTimeMs\", Int64.Type}, {\"ErrorCount\", Int64.Type}, {\"WarningCount\", Int64.Type}, {\"ValidationPassed\", type logical}, {\"DeliveredToSterling\", type logical}, {\"IsSuccess\", Int64.Type}, {\"IsFailed\", Int64.Type}})",
                                    "in",
                                    "    ChangedTypes"
                                ]
                            }
                        }]
                    }
                ]
            }
        }
        
        with open(model_dir / "model.bim", 'w', encoding='utf-8') as f:
            json.dump(model_bim, f, indent=2)
    
    def _create_report_pages(self, report_dir: Path, name: str):
        """Create report pages with visuals."""
        pages = []
        
        # Page 1: Overview Dashboard
        pages.append(self._create_overview_page())
        
        # Page 2: Pass/Fail Analysis
        pages.append(self._create_pass_fail_page())
        
        # Page 3: Transaction Type Analysis
        pages.append(self._create_transaction_type_page())
        
        # Page 4: Time Series Analysis
        pages.append(self._create_timeseries_page())
        
        # Page 5: Error Analysis
        pages.append(self._create_error_analysis_page())
        
        # Create layout.json
        layout = {
            "sections": pages
        }
        
        with open(report_dir / "layout.json", 'w', encoding='utf-8') as f:
            json.dump(layout, f, indent=2)
    
    def _create_overview_page(self) -> Dict[str, Any]:
        """Create overview dashboard page."""
        colors = self._get_brand_colors()
        return {
            "id": guid(),
            "displayName": "Overview",
            "name": "ReportSection",
            "sections": [
                {
                    "id": guid(),
                    "displayName": "Section 1",
                    "name": "PageSection",
                    "visualContainers": [
                        # Total Files Card
                        self._create_card_visual("Total Files", "[Total Files]", colors["navy"]),
                        # Success Count Card
                        self._create_card_visual("Success Count", "[Success Count]", colors["success_green"]),
                        # Failed Count Card
                        self._create_card_visual("Failed Count", "[Failed Count]", colors["error_red"]),
                        # Success Rate Gauge
                        self._create_gauge_visual("Success Rate", "[Success Rate]", colors["success_green"]),
                        # Pass/Fail Donut Chart
                        self._create_donut_visual("Pass/Fail Distribution", "Status", "[Total Files]"),
                        # Transaction Type Pie Chart
                        self._create_pie_visual("Transaction Types", "TransactionType", "[Total Files]")
                    ]
                }
            ]
        }
    
    def _create_pass_fail_page(self) -> Dict[str, Any]:
        """Create pass/fail analysis page."""
        colors = self._get_brand_colors()
        return {
            "id": guid(),
            "displayName": "Pass/Fail Analysis",
            "name": "ReportSection",
            "sections": [
                {
                    "id": guid(),
                    "displayName": "Section 1",
                    "name": "PageSection",
                    "visualContainers": [
                        # Success Rate Gauge
                        self._create_gauge_visual("Overall Success Rate", "[Success Rate]", colors["success_green"]),
                        # Pass/Fail by Transaction Type
                        self._create_bar_chart("Pass/Fail by Transaction Type", "TransactionType", "Status", "[Total Files]"),
                        # Pass/Fail by Trading Partner
                        self._create_bar_chart("Pass/Fail by Trading Partner", "TradingPartner", "Status", "[Total Files]"),
                        # Pass/Fail Trend Over Time
                        self._create_line_chart("Pass/Fail Trend", "Date", "Status", "[Total Files]")
                    ]
                }
            ]
        }
    
    def _create_transaction_type_page(self) -> Dict[str, Any]:
        """Create transaction type analysis page."""
        return {
            "id": guid(),
            "displayName": "Transaction Type Analysis",
            "name": "ReportSection",
            "sections": [
                {
                    "id": guid(),
                    "displayName": "Section 1",
                    "name": "PageSection",
                    "visualContainers": [
                        # Transaction Type Distribution
                        self._create_pie_visual("Transaction Distribution", "TransactionType", "[Total Files]"),
                        # Transaction Type Bar Chart
                        self._create_bar_chart("Files by Transaction Type", "TransactionType", None, "[Total Files]"),
                        # Success Rate by Transaction Type
                        self._create_bar_chart("Success Rate by Type", "TransactionType", None, "[Success Rate]"),
                        # Transaction Type Table
                        self._create_table_visual("Transaction Details", ["TransactionType", "Status", "Total Files", "Success Rate"])
                    ]
                }
            ]
        }
    
    def _create_timeseries_page(self) -> Dict[str, Any]:
        """Create time series analysis page."""
        return {
            "id": guid(),
            "displayName": "Time Series Analysis",
            "name": "ReportSection",
            "sections": [
                {
                    "id": guid(),
                    "displayName": "Section 1",
                    "name": "PageSection",
                    "visualContainers": [
                        # Processing Volume Over Time
                        self._create_line_chart("Processing Volume", "Date", None, "[Total Files]"),
                        # Success/Fail Trend
                        self._create_line_chart("Success/Fail Trend", "Date", "Status", "[Total Files]"),
                        # Average Processing Time Trend
                        self._create_line_chart("Avg Processing Time", "Date", None, "[Avg Processing Time]"),
                        # Error Count Trend
                        self._create_line_chart("Error Count Trend", "Date", None, "[Total Errors]")
                    ]
                }
            ]
        }
    
    def _create_error_analysis_page(self) -> Dict[str, Any]:
        """Create error analysis page."""
        colors = self._get_brand_colors()
        return {
            "id": guid(),
            "displayName": "Error Analysis",
            "name": "ReportSection",
            "sections": [
                {
                    "id": guid(),
                    "displayName": "Section 1",
                    "name": "PageSection",
                    "visualContainers": [
                        # Total Errors Card
                        self._create_card_visual("Total Errors", "[Total Errors]", colors["error_red"]),
                        # Total Warnings Card
                        self._create_card_visual("Total Warnings", "[Total Warnings]", colors["warning_orange"]),
                        # Errors by Transaction Type
                        self._create_bar_chart("Errors by Transaction Type", "TransactionType", None, "[Total Errors]"),
                        # Error Trend
                        self._create_line_chart("Error Trend", "Date", None, "[Total Errors]"),
                        # Error Details Table
                        self._create_table_visual("Error Details", ["TransactionType", "ErrorCount", "WarningCount", "Status"])
                    ]
                }
            ]
        }
    
    def _create_card_visual(self, title: str, measure: str, color: str) -> Dict[str, Any]:
        """Create a card/KPI visual."""
        return {
            "id": guid(),
            "visual": {
                "visualType": "card",
                "projections": {
                    "Values": [{"queryRef": "ProcessingMetrics.Total Files"}]
                },
                "vcObjects": {
                    "title": [{
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                            "show": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": "ProcessingMetrics", "Type": 0}],
                    "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure.replace("[", "").replace("]", "")}, "Name": f"ProcessingMetrics.{measure.replace('[', '').replace(']', '')}"}]
                }
            },
            "x": 0,
            "y": 0,
            "z": 0,
            "width": 200,
            "height": 150
        }
    
    def _create_gauge_visual(self, title: str, measure: str, color: str) -> Dict[str, Any]:
        """Create a gauge visual."""
        measure_name = measure.replace("[", "").replace("]", "")
        return {
            "id": guid(),
            "visual": {
                "visualType": "gauge",
                "projections": {
                    "Value": [{"queryRef": f"ProcessingMetrics.{measure_name}"}]
                },
                "vcObjects": {
                    "title": [{
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                            "show": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": "ProcessingMetrics", "Type": 0}],
                    "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": f"ProcessingMetrics.{measure_name}"}]
                }
            },
            "x": 0,
            "y": 0,
            "z": 0,
            "width": 300,
            "height": 300
        }
    
    def _create_donut_visual(self, title: str, category: str, measure: str) -> Dict[str, Any]:
        """Create a donut chart visual."""
        measure_name = measure.replace("[", "").replace("]", "")
        return {
            "id": guid(),
            "visual": {
                "visualType": "donutChart",
                "projections": {
                    "Category": [{"queryRef": f"ProcessingMetrics.{category}"}],
                    "Y": [{"queryRef": f"ProcessingMetrics.{measure_name}"}]
                },
                "vcObjects": {
                    "title": [{
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                            "show": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": "ProcessingMetrics", "Type": 0}],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": category}, "Name": f"ProcessingMetrics.{category}"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": f"ProcessingMetrics.{measure_name}"}
                    ],
                    "GroupBy": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": category}}]
                }
            },
            "x": 0,
            "y": 0,
            "z": 0,
            "width": 400,
            "height": 400
        }
    
    def _create_pie_visual(self, title: str, category: str, measure: str) -> Dict[str, Any]:
        """Create a pie chart visual."""
        return self._create_donut_visual(title, category, measure)  # Same structure
    
    def _create_bar_chart(self, title: str, category: str, legend: Optional[str], measure: str) -> Dict[str, Any]:
        """Create a bar chart visual."""
        measure_name = measure.replace("[", "").replace("]", "")
        projections = {
            "Category": [{"queryRef": f"ProcessingMetrics.{category}"}],
            "Y": [{"queryRef": f"ProcessingMetrics.{measure_name}"}]
        }
        
        select_items = [
            {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": category}, "Name": f"ProcessingMetrics.{category}"},
            {"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": f"ProcessingMetrics.{measure_name}"}
        ]
        
        if legend:
            projections["Legend"] = [{"queryRef": f"ProcessingMetrics.{legend}"}]
            select_items.insert(1, {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": legend}, "Name": f"ProcessingMetrics.{legend}"})
        
        return {
            "id": guid(),
            "visual": {
                "visualType": "barChart",
                "projections": projections,
                "vcObjects": {
                    "title": [{
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                            "show": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": "ProcessingMetrics", "Type": 0}],
                    "Select": select_items,
                    "GroupBy": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": category}]
                }
            },
            "x": 0,
            "y": 0,
            "z": 0,
            "width": 500,
            "height": 400
        }
    
    def _create_line_chart(self, title: str, category: str, legend: Optional[str], measure: str) -> Dict[str, Any]:
        """Create a line chart visual."""
        measure_name = measure.replace("[", "").replace("]", "")
        projections = {
            "Category": [{"queryRef": f"ProcessingMetrics.{category}"}],
            "Y": [{"queryRef": f"ProcessingMetrics.{measure_name}"}]
        }
        
        select_items = [
            {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": category}, "Name": f"ProcessingMetrics.{category}"},
            {"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": f"ProcessingMetrics.{measure_name}"}
        ]
        
        if legend:
            projections["Legend"] = [{"queryRef": f"ProcessingMetrics.{legend}"}]
            select_items.insert(1, {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": legend}, "Name": f"ProcessingMetrics.{legend}"})
        
        return {
            "id": guid(),
            "visual": {
                "visualType": "lineChart",
                "projections": projections,
                "vcObjects": {
                    "title": [{
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                            "show": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": "ProcessingMetrics", "Type": 0}],
                    "Select": select_items,
                    "GroupBy": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": category}]
                }
            },
            "x": 0,
            "y": 0,
            "z": 0,
            "width": 600,
            "height": 400
        }
    
    def _create_table_visual(self, title: str, columns: List[str]) -> Dict[str, Any]:
        """Create a table visual."""
        projections = {
            "Values": [{"queryRef": f"ProcessingMetrics.{col}"} for col in columns]
        }
        
        select_items = []
        for col in columns:
            # Determine if it's a measure or column
            if col in ["Total Files", "Success Count", "Failed Count", "Success Rate", "Avg Processing Time", "Total Errors", "Total Warnings"]:
                select_items.append({"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": col}, "Name": f"ProcessingMetrics.{col}"})
            else:
                select_items.append({"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": col}, "Name": f"ProcessingMetrics.{col}"})
        
        return {
            "id": guid(),
            "visual": {
                "visualType": "tableEx",
                "projections": projections,
                "vcObjects": {
                    "title": [{
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                            "show": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": "ProcessingMetrics", "Type": 0}],
                    "Select": select_items
                }
            },
            "x": 0,
            "y": 0,
            "z": 0,
            "width": 800,
            "height": 500
        }

