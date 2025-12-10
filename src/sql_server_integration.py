"""
SQL Server Integration
Database operations and data warehouse integration.
"""

import logging
import pyodbc
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SQLServerIntegration:
    """SQL Server database integration."""
    
    def __init__(self,
                 server: str,
                 database: str,
                 username: str = None,
                 password: str = None,
                 use_windows_auth: bool = False,
                 driver: str = "ODBC Driver 17 for SQL Server"):
        """
        Initialize SQL Server integration.
        
        Args:
            server: SQL Server instance (e.g., 'localhost' or 'server\\instance')
            database: Database name
            username: SQL Server username (if not using Windows auth)
            password: SQL Server password (if not using Windows auth)
            use_windows_auth: Use Windows authentication
            driver: ODBC driver name
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.use_windows_auth = use_windows_auth
        self.driver = driver
        self.connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Build SQL Server connection string."""
        if self.use_windows_auth:
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
        return conn_str
    
    def get_connection(self):
        """Get database connection."""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            raise
    
    def execute_query(self, query: str, parameters: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results.
        
        Args:
            query: SQL query
            parameters: Query parameters
            
        Returns:
            List of result dictionaries
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Fetch all results
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_non_query(self, query: str, parameters: tuple = None) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query
            parameters: Query parameters
            
        Returns:
            Number of rows affected
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_batch(self, query: str, parameters_list: List[tuple]) -> int:
        """
        Execute batch insert/update.
        
        Args:
            query: SQL query
            parameters_list: List of parameter tuples
            
        Returns:
            Total number of rows affected
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            total_affected = 0
            for params in parameters_list:
                cursor.execute(query, params)
                total_affected += cursor.rowcount
            
            conn.commit()
            return total_affected
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    # EDI Metrics Storage
    
    def store_edi_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Store EDI processing metrics in SQL Server.
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            True if successful
        """
        query = """
        INSERT INTO EDI_Metrics 
        (TransactionType, Status, ProcessingTime, FileName, ProcessedDate, TradingPartner, ErrorCount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        parameters = (
            metrics.get("transaction_type", ""),
            metrics.get("status", ""),
            metrics.get("processing_time", 0),
            metrics.get("file_name", ""),
            metrics.get("processed_date", datetime.now()),
            metrics.get("trading_partner", ""),
            metrics.get("error_count", 0)
        )
        
        try:
            self.execute_non_query(query, parameters)
            return True
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            return False
    
    def get_edi_metrics_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Get EDI metrics summary from SQL Server.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Summary dictionary
        """
        query = """
        SELECT 
            TransactionType,
            Status,
            COUNT(*) as Count,
            AVG(ProcessingTime) as AvgProcessingTime,
            SUM(ErrorCount) as TotalErrors
        FROM EDI_Metrics
        WHERE 1=1
        """
        
        params = []
        if start_date:
            query += " AND ProcessedDate >= ?"
            params.append(start_date)
        if end_date:
            query += " AND ProcessedDate <= ?"
            params.append(end_date)
        
        query += " GROUP BY TransactionType, Status"
        
        results = self.execute_query(query, tuple(params) if params else None)
        
        summary = {
            "total_transactions": sum(r["Count"] for r in results),
            "by_type": {},
            "by_status": {},
            "average_processing_time": 0,
            "total_errors": 0
        }
        
        total_time = 0
        for row in results:
            trans_type = row["TransactionType"]
            status = row["Status"]
            
            summary["by_type"][trans_type] = summary["by_type"].get(trans_type, 0) + row["Count"]
            summary["by_status"][status] = summary["by_status"].get(status, 0) + row["Count"]
            
            total_time += row["AvgProcessingTime"] * row["Count"]
            summary["total_errors"] += row["TotalErrors"]
        
        if summary["total_transactions"] > 0:
            summary["average_processing_time"] = total_time / summary["total_transactions"]
        
        return summary
    
    # Data Warehouse Operations
    
    def create_metrics_table(self):
        """Create EDI metrics table if it doesn't exist."""
        query = """
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[EDI_Metrics]') AND type in (N'U'))
        BEGIN
            CREATE TABLE [dbo].[EDI_Metrics] (
                [ID] INT IDENTITY(1,1) PRIMARY KEY,
                [TransactionType] NVARCHAR(50),
                [Status] NVARCHAR(50),
                [ProcessingTime] FLOAT,
                [FileName] NVARCHAR(255),
                [ProcessedDate] DATETIME,
                [TradingPartner] NVARCHAR(100),
                [ErrorCount] INT,
                [CreatedDate] DATETIME DEFAULT GETDATE()
            )
            
            CREATE INDEX IX_EDI_Metrics_ProcessedDate ON [dbo].[EDI_Metrics](ProcessedDate)
            CREATE INDEX IX_EDI_Metrics_TransactionType ON [dbo].[EDI_Metrics](TransactionType)
            CREATE INDEX IX_EDI_Metrics_Status ON [dbo].[EDI_Metrics](Status)
        END
        """
        
        try:
            self.execute_non_query(query)
            logger.info("EDI_Metrics table created or already exists")
            return True
        except Exception as e:
            logger.error(f"Failed to create metrics table: {e}")
            return False
    
    def export_to_data_warehouse(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """
        Export data to data warehouse table.
        
        Args:
            table_name: Target table name
            data: Data to export
            
        Returns:
            True if successful
        """
        if not data:
            return True
        
        # Get column names from first record
        columns = list(data[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join(columns)
        
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        parameters_list = [tuple(record.values()) for record in data]
        
        try:
            self.execute_batch(query, parameters_list)
            logger.info(f"Exported {len(data)} records to {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to export to data warehouse: {e}")
            return False
    
    def get_reporting_data(self, report_type: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Get data for reporting/analytics.
        
        Args:
            report_type: Type of report
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Report data
        """
        queries = {
            "processing_summary": """
                SELECT 
                    CAST(ProcessedDate AS DATE) as Date,
                    TransactionType,
                    COUNT(*) as TransactionCount,
                    AVG(ProcessingTime) as AvgProcessingTime,
                    SUM(CASE WHEN Status = 'Success' THEN 1 ELSE 0 END) as SuccessCount,
                    SUM(CASE WHEN Status = 'Failed' THEN 1 ELSE 0 END) as FailedCount
                FROM EDI_Metrics
                WHERE 1=1
            """,
            "trading_partner_summary": """
                SELECT 
                    TradingPartner,
                    COUNT(*) as TransactionCount,
                    AVG(ProcessingTime) as AvgProcessingTime,
                    SUM(ErrorCount) as TotalErrors
                FROM EDI_Metrics
                WHERE 1=1
            """
        }
        
        query = queries.get(report_type)
        if not query:
            return []
        
        params = []
        if start_date:
            query += " AND ProcessedDate >= ?"
            params.append(start_date)
        if end_date:
            query += " AND ProcessedDate <= ?"
            params.append(end_date)
        
        if report_type == "processing_summary":
            query += " GROUP BY CAST(ProcessedDate AS DATE), TransactionType ORDER BY Date DESC"
        elif report_type == "trading_partner_summary":
            query += " GROUP BY TradingPartner ORDER BY TransactionCount DESC"
        
        return self.execute_query(query, tuple(params) if params else None)

