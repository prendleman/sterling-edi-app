"""
Power BI Financial Dashboards Generator
Generates multiple financial-focused Power BI dashboards using v7 PBIP method.
Based on create_full_reports_with_visuals_v7.py from aq_wp_selenium_bot.
"""

import json
import uuid
import shutil
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


def guid():
    """Generate a GUID."""
    return str(uuid.uuid4())


# Financial Dashboard Colors
FINANCIAL_COLORS = {
    "revenue_green": "#4A9B4A",
    "expense_red": "#D32F2F",
    "profit_blue": "#2196F3",
    "neutral": "#F5F5F5",
    "navy": "#1B365D",
    "gold": "#C4962E",
    "warning": "#FF9800"
}


class PowerBIFinancialDashboardGenerator:
    """Generates Power BI financial dashboards using v7 PBIP method."""
    
    def __init__(self, output_dir: str = "dashboards"):
        """
        Initialize financial dashboard generator.
        
        Args:
            output_dir: Directory to output PBIX files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
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
        """Get brand colors, fallback to default financial colors."""
        if self.branding.get("colors"):
            colors = self.branding["colors"]
            return {
                "revenue_green": colors.get("success", FINANCIAL_COLORS["revenue_green"]),
                "expense_red": colors.get("error", FINANCIAL_COLORS["expense_red"]),
                "profit_blue": colors.get("accent", FINANCIAL_COLORS["profit_blue"]),
                "neutral": colors.get("background_light", FINANCIAL_COLORS["neutral"]),
                "navy": colors.get("primary", FINANCIAL_COLORS["navy"]),
                "gold": colors.get("secondary", FINANCIAL_COLORS["gold"]),
                "warning": colors.get("warning", FINANCIAL_COLORS["warning"])
            }
        return FINANCIAL_COLORS
    
    def generate_all_dashboards(self) -> List[str]:
        """
        Generate all financial dashboards.
        
        Returns:
            List of generated dashboard file paths
        """
        dashboards = []
        
        # Generate Financial Metrics Dashboard
        dashboards.append(self.generate_financial_metrics_dashboard())
        
        # Generate Sales Analytics Dashboard
        dashboards.append(self.generate_sales_analytics_dashboard())
        
        # Generate Inventory Operations Dashboard
        dashboards.append(self.generate_inventory_operations_dashboard())
        
        # Generate AR/AP Dashboard
        dashboards.append(self.generate_ar_ap_dashboard())
        
        logger.info(f"Generated {len(dashboards)} financial dashboards")
        return dashboards
    
    def generate_financial_metrics_dashboard(self) -> str:
        """Generate Financial Metrics Dashboard (P&L, Cash Flow, Budget Variance)."""
        return self._create_pbip_file_v7(
            name="FinancialMetricsDashboard",
            tables_config=self._get_financial_metrics_tables(),
            relationships=[],
            visuals_config=self._get_financial_metrics_visuals(),
            theme_colors=FINANCIAL_COLORS
        )
    
    def generate_sales_analytics_dashboard(self) -> str:
        """Generate Sales Analytics Dashboard."""
        return self._create_pbip_file_v7(
            name="SalesAnalyticsDashboard",
            tables_config=self._get_sales_tables(),
            relationships=[],
            visuals_config=self._get_sales_visuals(),
            theme_colors=FINANCIAL_COLORS
        )
    
    def generate_inventory_operations_dashboard(self) -> str:
        """Generate Inventory & Operations Dashboard."""
        return self._create_pbip_file_v7(
            name="InventoryOperationsDashboard",
            tables_config=self._get_inventory_tables(),
            relationships=[],
            visuals_config=self._get_inventory_visuals(),
            theme_colors=FINANCIAL_COLORS
        )
    
    def generate_ar_ap_dashboard(self) -> str:
        """Generate Accounts Receivable/Payable Dashboard."""
        return self._create_pbip_file_v7(
            name="ARAPDashboard",
            tables_config=self._get_ar_ap_tables(),
            relationships=[],
            visuals_config=self._get_ar_ap_visuals(),
            theme_colors=FINANCIAL_COLORS
        )
    
    def _create_pbip_file_v7(self, name: str, tables_config: List[Dict], relationships: List[Dict],
                             visuals_config: Dict, theme_colors: Dict = None) -> str:
        """Create PBIP file with branding support."""
        if theme_colors is None:
            theme_colors = self._get_brand_colors()
        """
        Create a PBIP file using v7 method (based on create_full_reports_with_visuals_v7.py).
        """
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
        with open(self.output_dir / f"{name}.pbip", 'w', encoding='utf-8') as f:
            json.dump({
                "version": "1.0",
                "artifacts": [{"report": {"path": f"{name}.Report"}}],
                "settings": {"enableAutoRecovery": True}
            }, f, indent=2)
        
        # 2. Create .platform files
        def create_platform_file(path, display_name, ptype):
            platform_dir = path / ".platform"
            platform_dir.mkdir(exist_ok=True)
            with open(platform_dir / "platform.json", 'w', encoding='utf-8') as f:
                json.dump({
                    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                    "metadata": {"type": ptype, "displayName": display_name},
                    "config": {"version": "2.0", "logicalId": guid()}
                }, f, indent=2)
        
        create_platform_file(report_dir, name, "Report")
        create_platform_file(model_dir, name, "SemanticModel")
        
        # 3. Create definition.pbir
        with open(report_dir / "definition.pbir", 'w', encoding='utf-8') as f:
            json.dump({
                "version": "4.0",
                "datasetReference": {
                    "byPath": {"path": f"../{name}.SemanticModel"},
                    "byConnection": None
                }
            }, f, indent=2)
        
        # 4. Build pages with visuals (v7 method)
        page_sections = []
        for page_idx, (page_name, page_visuals) in enumerate(visuals_config.items()):
            visual_containers = []
            for v in page_visuals:
                # Build projections and prototypeQuery for data binding (v7 method)
                projections = {}
                prototype_query = None
                table = v.get("table")
                measure = v.get("measure")
                category = v.get("category")
                categories = v.get("categories", [])
                values = v.get("values", [])
                x_axis = v.get("x_axis")
                y_axis = v.get("y_axis")
                legend = v.get("legend")
                size = v.get("size")
                
                visual_type = v["type"]
                
                # Card visuals
                if visual_type == "card":
                    if measure and table:
                        measure_name = measure.replace("[", "").replace("]", "")
                        projections["Values"] = [{"queryRef": f"{table}.{measure_name}"}]
                        prototype_query = {
                            "Version": 2,
                            "From": [{"Name": "t", "Entity": table, "Type": 0}],
                            "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": f"{table}.{measure_name}"}]
                        }
                
                # Chart visuals
                elif visual_type in ["clusteredBarChart", "barChart", "lineChart", "pieChart", "areaChart"]:
                    select_items = []
                    if category and table:
                        projections["Category"] = [{"queryRef": f"{table}.{category}"}]
                        select_items.append({"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": category}, "Name": f"{table}.{category}"})
                    if measure and table:
                        measure_name = measure.replace("[", "").replace("]", "")
                        projections["Y"] = [{"queryRef": f"{table}.{measure_name}"}]
                        select_items.append({"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": f"{table}.{measure_name}"})
                    if legend and table:
                        projections["Legend"] = [{"queryRef": f"{table}.{legend}"}]
                        select_items.append({"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": legend}, "Name": f"{table}.{legend}"})
                    
                    if select_items:
                        prototype_query = {
                            "Version": 2,
                            "From": [{"Name": "t", "Entity": table, "Type": 0}],
                            "Select": select_items
                        }
                        if category:
                            prototype_query["GroupBy"] = [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": category}}]
                
                # Gauge visuals
                elif visual_type == "gauge":
                    if measure and table:
                        measure_name = measure.replace("[", "").replace("]", "")
                        projections["Value"] = [{"queryRef": f"{table}.{measure_name}"}]
                        prototype_query = {
                            "Version": 2,
                            "From": [{"Name": "t", "Entity": table, "Type": 0}],
                            "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": measure_name}, "Name": f"{table}.{measure_name}"}]
                        }
                
                # Create visual container (v7 method)
                single_visual = {
                    "visualType": visual_type,
                    "projections": projections,
                    "vcObjects": {
                        "title": [{
                            "properties": {
                                "text": {"expr": {"Literal": {"Value": f"'{v['title']}'"}}},
                                "show": {"expr": {"Literal": {"Value": "true"}}}
                            }
                        }]
                    },
                    "objects": {}
                }
                
                if prototype_query:
                    single_visual["prototypeQuery"] = prototype_query
                
                # Add minimal visual-specific styling
                if visual_type == "card":
                    single_visual["objects"]["labels"] = [{"properties": {}}]
                    single_visual["objects"]["card"] = [{"properties": {}}]
                elif visual_type in ["clusteredBarChart", "lineChart", "pieChart"]:
                    single_visual["objects"]["general"] = [{"properties": {}}]
                
                container = {
                    "x": v["x"], "y": v["y"], "z": v.get("z", 0), "width": v["w"], "height": v["h"],
                    "config": json.dumps({
                        "name": guid(),
                        "layouts": [{"id": 0, "position": {"x": v["x"], "y": v["y"], "z": v.get("z", 0), "width": v["w"], "height": v["h"]}}],
                        "singleVisual": single_visual
                    }),
                    "filters": "[]",
                    "tabOrder": v.get("tabOrder", 0)
                }
                visual_containers.append(container)
            
            page_sections.append({
                "name": f"ReportSection{page_idx + 1}",
                "displayName": page_name,
                "displayOption": 0,
                "width": 1280,
                "height": 720,
                "visualContainers": visual_containers
            })
        
        # 5. Create report.json (v7 method)
        report_json_content = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
            "sections": page_sections,
            "publicCustomVisuals": [],
            "resourcePackages": []
        }
        with open(report_dir / "report.json", 'w', encoding='utf-8') as f:
            json.dump(report_json_content, f, indent=2)
        
        # 6. Create definition.pbism
        with open(model_dir / "definition.pbism", 'w', encoding='utf-8') as f:
            json.dump({"version": "4.0", "settings": {}}, f, indent=2)
        
        # 7. Build semantic model (v7 method)
        self._build_semantic_model_v7(model_dir, name, tables_config, relationships)
        
        pbip_file = self.output_dir / f"{name}.pbip"
        logger.info(f"Created PBIP: {pbip_file.name}")
        return str(pbip_file)
    
    def _build_semantic_model_v7(self, model_dir: Path, name: str, tables_config: List[Dict], relationships: List[Dict]):
        """Build semantic model using v7 method (exact from reference)."""
        type_map = {"string": "type text", "double": "type number", "int64": "Int64.Type", "dateTime": "type date", "boolean": "type logical"}
        
        model_tables = []
        for table_config in tables_config:
            table_name = table_config["name"]
            columns = table_config["columns"]
            measures = table_config.get("measures", [])
            csv_file = table_config.get("csv")
            
            col_types = ", ".join([f"{{\"{c[0]}\", {type_map.get(c[1], 'type text')}}}" for c in columns])
            cols = [{"name": c[0], "dataType": c[1], "sourceColumn": c[0], "lineageTag": guid()} for c in columns]
            msrs = [{"name": m[0], "expression": m[1], "formatString": m[2] if len(m) > 2 else "", "lineageTag": guid()} for m in measures]
            
            table_def = {
                "name": table_name,
                "lineageTag": guid(),
                "columns": cols,
                "measures": msrs
            }
            
            # Add partition if CSV file specified (for sample data)
            if csv_file:
                sample_path = (self.output_dir / "sample_data").as_posix()
                table_def["partitions"] = [{
                    "name": table_name,
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            f"    Source = Folder.Files(SampleDataFolder),",
                            f"    {csv_file.replace('.csv', '')}_File = Source{{[Name=\"{csv_file}\"]}}[Content],",
                            f"    ImportedCSV = Csv.Document({csv_file.replace('.csv', '')}_File, [Delimiter=\",\", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.None]),",
                            f"    PromotedHeaders = Table.PromoteHeaders(ImportedCSV, [PromoteAllScalars=true]),",
                            f"    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{{col_types}}})",
                            "in",
                            "    ChangedTypes"
                        ]
                    }
                }]
            
            model_tables.append(table_def)
        
        # Build relationships
        model_relationships = []
        for rel in relationships:
            model_relationships.append({
                "name": rel.get("name", guid()),
                "fromTable": rel["fromTable"],
                "fromColumn": rel["fromColumn"],
                "toTable": rel["toTable"],
                "toColumn": rel["toColumn"],
                "fromCardinality": rel.get("fromCardinality", "many"),
                "toCardinality": rel.get("toCardinality", "one"),
                "isActive": rel.get("isActive", True),
                "crossFilteringBehavior": rel.get("crossFilteringBehavior", "bothDirections")
            })
        
        # Create sample data folder expression if needed
        expressions = []
        if any(t.get("csv") for t in tables_config):
            sample_path = (self.output_dir / "sample_data").as_posix()
            expressions.append({
                "name": "SampleDataFolder",
                "kind": "m",
                "expression": [f"let Source = \"{sample_path}/\" in Source"]
            })
        
        model_bim = {
            "name": name,
            "compatibilityLevel": 1567,
            "model": {
                "culture": "en-US",
                "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
                "defaultPowerBIDataSourceVersion": "powerBI_V3",
                "sourceQueryCulture": "en-US",
                "expressions": expressions,
                "tables": model_tables,
                "relationships": model_relationships
            }
        }
        
        with open(model_dir / "model.bim", 'w', encoding='utf-8') as f:
            json.dump(model_bim, f, indent=2)
    
    # Financial Metrics Dashboard Configuration
    
    def _get_financial_metrics_tables(self) -> List[Dict]:
        """Get table configuration for Financial Metrics Dashboard."""
        return [
            {
                "name": "FinancialData",
                "columns": [
                    ("Date", "dateTime"),
                    ("Account", "string"),
                    ("AccountType", "string"),
                    ("Amount", "double"),
                    ("BudgetAmount", "double"),
                    ("Period", "string"),
                    ("Year", "int64")
                ],
                "measures": [
                    ("Total Revenue", "SUM(FinancialData[Amount])", "$#,##0.00"),
                    ("Total Expenses", "SUM(FinancialData[Amount])", "$#,##0.00"),
                    ("Net Income", "[Total Revenue] - [Total Expenses]", "$#,##0.00"),
                    ("Budget Variance", "SUM(FinancialData[Amount]) - SUM(FinancialData[BudgetAmount])", "$#,##0.00"),
                    ("Variance %", "DIVIDE([Budget Variance], SUM(FinancialData[BudgetAmount]), 0)", "0.00%"),
                    ("Revenue YTD", "TOTALYTD(SUM(FinancialData[Amount]), FinancialData[Date])", "$#,##0.00"),
                    ("Expenses YTD", "TOTALYTD(SUM(FinancialData[Amount]), FinancialData[Date])", "$#,##0.00")
                ]
            }
        ]
    
    def _get_financial_metrics_visuals(self) -> Dict:
        """Get visuals configuration for Financial Metrics Dashboard."""
        return {
            "P&L Overview": [
                {"x": 20, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Total Revenue", "table": "FinancialData", "measure": "[Total Revenue]"},
                {"x": 240, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Total Expenses", "table": "FinancialData", "measure": "[Total Expenses]"},
                {"x": 460, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Net Income", "table": "FinancialData", "measure": "[Net Income]"},
                {"x": 680, "y": 20, "w": 200, "h": 150, "type": "gauge", "title": "Budget Variance %", "table": "FinancialData", "measure": "[Variance %]"},
                {"x": 20, "y": 190, "w": 600, "h": 400, "type": "lineChart", "title": "Revenue Trend", "table": "FinancialData", "measure": "[Total Revenue]", "category": "Date"},
                {"x": 640, "y": 190, "w": 600, "h": 400, "type": "lineChart", "title": "Expense Trend", "table": "FinancialData", "measure": "[Total Expenses]", "category": "Date"},
                {"x": 20, "y": 610, "w": 600, "h": 400, "type": "barChart", "title": "P&L by Account Type", "table": "FinancialData", "measure": "[Amount]", "category": "AccountType"},
                {"x": 640, "y": 610, "w": 600, "h": 400, "type": "lineChart", "title": "Actual vs Budget", "table": "FinancialData", "measure": "[Amount]", "category": "Date"}
            ],
            "Budget Analysis": [
                {"x": 20, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Budget Variance", "table": "FinancialData", "measure": "[Budget Variance]"},
                {"x": 240, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Variance %", "table": "FinancialData", "measure": "[Variance %]"},
                {"x": 20, "y": 190, "w": 800, "h": 500, "type": "lineChart", "title": "Actual vs Budget Trend", "table": "FinancialData", "measure": "[Amount]", "category": "Date"},
                {"x": 840, "y": 190, "w": 400, "h": 500, "type": "barChart", "title": "Variance by Account", "table": "FinancialData", "measure": "[Budget Variance]", "category": "Account"}
            ]
        }
    
    # Sales Dashboard Configuration
    
    def _get_sales_tables(self) -> List[Dict]:
        """Get table configuration for Sales Dashboard."""
        return [
            {
                "name": "Sales",
                "columns": [
                    ("Date", "dateTime"),
                    ("CustomerID", "string"),
                    ("ProductID", "string"),
                    ("Amount", "double"),
                    ("Quantity", "double"),
                    ("Region", "string")
                ],
                "measures": [
                    ("Total Sales", "SUM(Sales[Amount])", "$#,##0.00"),
                    ("Sales YTD", "TOTALYTD(SUM(Sales[Amount]), Sales[Date])", "$#,##0.00"),
                    ("Avg Sale", "AVERAGE(Sales[Amount])", "$#,##0.00"),
                    ("Sales Count", "COUNTROWS(Sales)", "#,##0")
                ]
            }
        ]
    
    def _get_sales_visuals(self) -> Dict:
        """Get visuals configuration for Sales Dashboard."""
        return {
            "Sales Overview": [
                {"x": 20, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Total Sales", "table": "Sales", "measure": "[Total Sales]"},
                {"x": 240, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Sales YTD", "table": "Sales", "measure": "[Sales YTD]"},
                {"x": 460, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Avg Sale", "table": "Sales", "measure": "[Avg Sale]"},
                {"x": 680, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Sales Count", "table": "Sales", "measure": "[Sales Count]"},
                {"x": 20, "y": 190, "w": 600, "h": 400, "type": "lineChart", "title": "Sales Trend", "table": "Sales", "measure": "[Total Sales]", "category": "Date"},
                {"x": 640, "y": 190, "w": 400, "h": 400, "type": "barChart", "title": "Sales by Region", "table": "Sales", "measure": "[Total Sales]", "category": "Region"},
                {"x": 1060, "y": 190, "w": 400, "h": 400, "type": "pieChart", "title": "Sales by Customer", "table": "Sales", "measure": "[Total Sales]", "category": "CustomerID"}
            ]
        }
    
    # Inventory Dashboard Configuration
    
    def _get_inventory_tables(self) -> List[Dict]:
        """Get table configuration for Inventory Dashboard."""
        return [
            {
                "name": "Inventory",
                "columns": [
                    ("Date", "dateTime"),
                    ("ItemID", "string"),
                    ("Location", "string"),
                    ("QuantityOnHand", "double"),
                    ("QuantityAvailable", "double"),
                    ("UnitCost", "double"),
                    ("ItemClass", "string")
                ],
                "measures": [
                    ("Total Inventory Value", "SUM(Inventory[QuantityOnHand] * Inventory[UnitCost])", "$#,##0.00"),
                    ("Total Items", "COUNTROWS(Inventory)", "#,##0"),
                    ("Avg Inventory Value", "AVERAGE(Inventory[QuantityOnHand] * Inventory[UnitCost])", "$#,##0.00")
                ]
            }
        ]
    
    def _get_inventory_visuals(self) -> Dict:
        """Get visuals configuration for Inventory Dashboard."""
        return {
            "Inventory Overview": [
                {"x": 20, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Total Inventory Value", "table": "Inventory", "measure": "[Total Inventory Value]"},
                {"x": 240, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Total Items", "table": "Inventory", "measure": "[Total Items]"},
                {"x": 20, "y": 190, "w": 600, "h": 400, "type": "barChart", "title": "Inventory by Location", "table": "Inventory", "measure": "[Total Inventory Value]", "category": "Location"},
                {"x": 640, "y": 190, "w": 600, "h": 400, "type": "barChart", "title": "Inventory by Item Class", "table": "Inventory", "measure": "[Total Inventory Value]", "category": "ItemClass"}
            ]
        }
    
    # AR/AP Dashboard Configuration
    
    def _get_ar_ap_tables(self) -> List[Dict]:
        """Get table configuration for AR/AP Dashboard."""
        return [
            {
                "name": "ARTransactions",
                "columns": [
                    ("Date", "dateTime"),
                    ("CustomerID", "string"),
                    ("InvoiceNbr", "string"),
                    ("Amount", "double"),
                    ("Balance", "double"),
                    ("DaysPastDue", "int64")
                ],
                "measures": [
                    ("Total AR", "SUM(ARTransactions[Balance])", "$#,##0.00"),
                    ("Overdue AR", "SUM(ARTransactions[Balance])", "$#,##0.00"),
                    ("Avg Days Past Due", "AVERAGE(ARTransactions[DaysPastDue])", "#,##0")
                ]
            },
            {
                "name": "APTransactions",
                "columns": [
                    ("Date", "dateTime"),
                    ("VendorID", "string"),
                    ("InvoiceNbr", "string"),
                    ("Amount", "double"),
                    ("Balance", "double"),
                    ("DaysPastDue", "int64")
                ],
                "measures": [
                    ("Total AP", "SUM(APTransactions[Balance])", "$#,##0.00"),
                    ("Overdue AP", "SUM(APTransactions[Balance])", "$#,##0.00")
                ]
            }
        ]
    
    def _get_ar_ap_visuals(self) -> Dict:
        """Get visuals configuration for AR/AP Dashboard."""
        return {
            "AR Analysis": [
                {"x": 20, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Total AR", "table": "ARTransactions", "measure": "[Total AR]"},
                {"x": 240, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Overdue AR", "table": "ARTransactions", "measure": "[Overdue AR]"},
                {"x": 20, "y": 190, "w": 600, "h": 400, "type": "barChart", "title": "AR by Customer", "table": "ARTransactions", "measure": "[Total AR]", "category": "CustomerID"},
                {"x": 640, "y": 190, "w": 600, "h": 400, "type": "barChart", "title": "Aging Analysis", "table": "ARTransactions", "measure": "[Total AR]", "category": "DaysPastDue"}
            ],
            "AP Analysis": [
                {"x": 20, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Total AP", "table": "APTransactions", "measure": "[Total AP]"},
                {"x": 240, "y": 20, "w": 200, "h": 150, "type": "card", "title": "Overdue AP", "table": "APTransactions", "measure": "[Overdue AP]"},
                {"x": 20, "y": 190, "w": 800, "h": 500, "type": "barChart", "title": "AP by Vendor", "table": "APTransactions", "measure": "[Total AP]", "category": "VendorID"}
            ]
        }
