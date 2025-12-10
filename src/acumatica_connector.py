"""
Acumatica ERP Connector
Provides REST API integration with Acumatica ERP system.
Supports common operations: Sales Orders, Purchase Orders, Inventory, Customers, Financials.
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AcumaticaConnector:
    """Integration with Acumatica ERP via REST API."""
    
    def __init__(self,
                 base_url: str,
                 username: str = None,
                 password: str = None,
                 tenant: str = None,
                 branch: str = None,
                 timeout: int = 30):
        """
        Initialize Acumatica connector.
        
        Args:
            base_url: Acumatica instance URL (e.g., https://acumatica.example.com)
            username: API username
            password: API password
            tenant: Tenant name (if multi-tenant)
            branch: Branch ID (if multi-branch)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.tenant = tenant
        self.branch = branch
        self.timeout = timeout
        self.session = requests.Session()
        self.auth_token = None
        
        # Set up session
        if username and password:
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """
        Authenticate with Acumatica API.
        
        Returns:
            True if authentication successful
        """
        try:
            auth_url = f"{self.base_url}/entity/auth/login"
            
            payload = {
                "name": self.username,
                "password": self.password
            }
            
            if self.tenant:
                payload["tenant"] = self.tenant
            if self.branch:
                payload["branch"] = self.branch
            
            response = self.session.post(
                auth_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                # Extract cookies/session from response
                self.auth_token = response.cookies.get('ASP.NET_SessionId')
                logger.info("Acumatica authentication successful")
                return True
            else:
                logger.error(f"Acumatica authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error authenticating with Acumatica: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        Make API request to Acumatica.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Acumatica API request failed: {e}")
            raise
    
    # Sales Order Operations
    
    def get_sales_orders(self, 
                        order_type: str = None,
                        status: str = None,
                        customer_id: str = None,
                        start_date: str = None,
                        end_date: str = None) -> List[Dict[str, Any]]:
        """
        Get sales orders from Acumatica.
        
        Args:
            order_type: Filter by order type
            status: Filter by status
            customer_id: Filter by customer
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            List of sales order dictionaries
        """
        endpoint = "/entity/Default/20.200.001/SalesOrder"
        params = {}
        
        if order_type:
            params["$filter"] = f"OrderType eq '{order_type}'"
        if status:
            params["$filter"] = (params.get("$filter", "") + f" and Status eq '{status}'").lstrip(" and ")
        if customer_id:
            params["$filter"] = (params.get("$filter", "") + f" and CustomerID eq '{customer_id}'").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_sales_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new sales order in Acumatica.
        
        Args:
            order_data: Sales order data dictionary
            
        Returns:
            Created sales order dictionary
        """
        endpoint = "/entity/Default/20.200.001/SalesOrder"
        return self._make_request("POST", endpoint, data=order_data)
    
    def update_sales_order(self, order_nbr: str, order_type: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing sales order.
        
        Args:
            order_nbr: Order number
            order_type: Order type
            order_data: Updated order data
            
        Returns:
            Updated sales order dictionary
        """
        endpoint = f"/entity/Default/20.200.001/SalesOrder/{order_type}/{order_nbr}"
        return self._make_request("PUT", endpoint, data=order_data)
    
    # Purchase Order Operations
    
    def get_purchase_orders(self,
                           order_type: str = None,
                           status: str = None,
                           vendor_id: str = None) -> List[Dict[str, Any]]:
        """
        Get purchase orders from Acumatica.
        
        Args:
            order_type: Filter by order type
            status: Filter by status
            vendor_id: Filter by vendor
            
        Returns:
            List of purchase order dictionaries
        """
        endpoint = "/entity/Default/20.200.001/PurchaseOrder"
        params = {}
        
        if order_type:
            params["$filter"] = f"OrderType eq '{order_type}'"
        if status:
            params["$filter"] = (params.get("$filter", "") + f" and Status eq '{status}'").lstrip(" and ")
        if vendor_id:
            params["$filter"] = (params.get("$filter", "") + f" and VendorID eq '{vendor_id}'").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new purchase order in Acumatica.
        
        Args:
            po_data: Purchase order data dictionary
            
        Returns:
            Created purchase order dictionary
        """
        endpoint = "/entity/Default/20.200.001/PurchaseOrder"
        return self._make_request("POST", endpoint, data=po_data)
    
    # Inventory Operations
    
    def get_inventory_items(self,
                           item_class: str = None,
                           item_status: str = None) -> List[Dict[str, Any]]:
        """
        Get inventory items from Acumatica.
        
        Args:
            item_class: Filter by item class
            item_status: Filter by item status
            
        Returns:
            List of inventory item dictionaries
        """
        endpoint = "/entity/Default/20.200.001/InventoryItem"
        params = {}
        
        if item_class:
            params["$filter"] = f"ItemClass eq '{item_class}'"
        if item_status:
            params["$filter"] = (params.get("$filter", "") + f" and ItemStatus eq '{item_status}'").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def get_inventory_quantities(self, item_id: str = None) -> List[Dict[str, Any]]:
        """
        Get inventory quantities.
        
        Args:
            item_id: Filter by item ID
            
        Returns:
            List of inventory quantity dictionaries
        """
        endpoint = "/entity/Default/20.200.001/InventoryQuantityAvailable"
        params = {}
        
        if item_id:
            params["$filter"] = f"InventoryID eq '{item_id}'"
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    # Customer/Vendor Operations
    
    def get_customers(self, customer_class: str = None) -> List[Dict[str, Any]]:
        """
        Get customers from Acumatica.
        
        Args:
            customer_class: Filter by customer class
            
        Returns:
            List of customer dictionaries
        """
        endpoint = "/entity/Default/20.200.001/Customer"
        params = {}
        
        if customer_class:
            params["$filter"] = f"CustomerClass eq '{customer_class}'"
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def get_vendors(self, vendor_class: str = None) -> List[Dict[str, Any]]:
        """
        Get vendors from Acumatica.
        
        Args:
            vendor_class: Filter by vendor class
            
        Returns:
            List of vendor dictionaries
        """
        endpoint = "/entity/Default/20.200.001/Vendor"
        params = {}
        
        if vendor_class:
            params["$filter"] = f"VendorClass eq '{vendor_class}'"
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    # Financial Operations
    
    def get_ar_transactions(self,
                           customer_id: str = None,
                           start_date: str = None,
                           end_date: str = None) -> List[Dict[str, Any]]:
        """
        Get Accounts Receivable transactions.
        
        Args:
            customer_id: Filter by customer
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of AR transaction dictionaries
        """
        endpoint = "/entity/Default/20.200.001/AccountsReceivable"
        params = {}
        
        if customer_id:
            params["$filter"] = f"CustomerID eq '{customer_id}'"
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def get_ap_transactions(self,
                           vendor_id: str = None,
                           start_date: str = None,
                           end_date: str = None) -> List[Dict[str, Any]]:
        """
        Get Accounts Payable transactions.
        
        Args:
            vendor_id: Filter by vendor
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of AP transaction dictionaries
        """
        endpoint = "/entity/Default/20.200.001/AccountsPayable"
        params = {}
        
        if vendor_id:
            params["$filter"] = f"VendorID eq '{vendor_id}'"
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    # EDI Integration Helpers
    
    def create_po_from_edi_850(self, edi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Acumatica Purchase Order from EDI 850 (Purchase Order) data.
        
        Args:
            edi_data: Parsed EDI 850 data dictionary
            
        Returns:
            Created purchase order dictionary
        """
        # Map EDI data to Acumatica PO format
        po_data = {
            "OrderType": {"value": "Normal"},
            "VendorID": {"value": edi_data.get("data", {}).get("parties", [{}])[0].get("name", "")},
            "OrderDate": {"value": edi_data.get("data", {}).get("po_date", datetime.now().strftime("%Y-%m-%d"))},
            "OrderNbr": {"value": edi_data.get("data", {}).get("po_number", "")},
            "Details": []
        }
        
        # Add line items
        for item in edi_data.get("data", {}).get("line_items", []):
            po_data["Details"].append({
                "InventoryID": {"value": item.get("product_id", "")},
                "OrderQty": {"value": float(item.get("quantity", 0))},
                "UnitCost": {"value": float(item.get("unit_price", 0))},
                "LineNbr": {"value": int(item.get("line_number", 0))}
            })
        
        return self.create_purchase_order(po_data)
    
    def create_invoice_from_edi_810(self, edi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Acumatica AR Invoice from EDI 810 (Invoice) data.
        
        Args:
            edi_data: Parsed EDI 810 data dictionary
            
        Returns:
            Created invoice dictionary
        """
        # Map EDI data to Acumatica AR Invoice format
        invoice_data = {
            "Type": {"value": "Invoice"},
            "CustomerID": {"value": edi_data.get("data", {}).get("parties", [{}])[0].get("name", "")},
            "DocDate": {"value": edi_data.get("data", {}).get("invoice_date", datetime.now().strftime("%Y-%m-%d"))},
            "ReferenceNbr": {"value": edi_data.get("data", {}).get("invoice_number", "")},
            "Details": []
        }
        
        # Add line items
        for item in edi_data.get("data", {}).get("line_items", []):
            invoice_data["Details"].append({
                "InventoryID": {"value": item.get("product_id", "")},
                "Quantity": {"value": float(item.get("quantity", 0))},
                "UnitPrice": {"value": float(item.get("unit_price", 0))},
                "LineNbr": {"value": int(item.get("line_number", 0))}
            })
        
        return self.create_sales_order(invoice_data)
    
    # CRM Operations (Acumatica has built-in CRM)
    
    def get_contacts(self, 
                    contact_type: str = None,
                    status: str = None,
                    account_id: str = None) -> List[Dict[str, Any]]:
        """
        Get contacts from Acumatica CRM.
        
        Args:
            contact_type: Filter by contact type
            status: Filter by status
            account_id: Filter by account ID
            
        Returns:
            List of contact dictionaries
        """
        endpoint = "/entity/Default/20.200.001/Contact"
        params = {}
        
        if contact_type:
            params["$filter"] = f"ContactType eq '{contact_type}'"
        if status:
            params["$filter"] = (params.get("$filter", "") + f" and Status eq '{status}'").lstrip(" and ")
        if account_id:
            params["$filter"] = (params.get("$filter", "") + f" and AccountID eq '{account_id}'").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new contact in Acumatica CRM.
        
        Args:
            contact_data: Contact data dictionary
            
        Returns:
            Created contact dictionary
        """
        endpoint = "/entity/Default/20.200.001/Contact"
        return self._make_request("POST", endpoint, data=contact_data)
    
    def get_opportunities(self,
                        stage: str = None,
                        status: str = None,
                        account_id: str = None,
                        start_date: str = None,
                        end_date: str = None) -> List[Dict[str, Any]]:
        """
        Get opportunities from Acumatica CRM.
        
        Args:
            stage: Filter by opportunity stage
            status: Filter by status
            account_id: Filter by account ID
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of opportunity dictionaries
        """
        endpoint = "/entity/Default/20.200.001/Opportunity"
        params = {}
        
        if stage:
            params["$filter"] = f"Stage eq '{stage}'"
        if status:
            params["$filter"] = (params.get("$filter", "") + f" and Status eq '{status}'").lstrip(" and ")
        if account_id:
            params["$filter"] = (params.get("$filter", "") + f" and AccountID eq '{account_id}'").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new opportunity in Acumatica CRM.
        
        Args:
            opportunity_data: Opportunity data dictionary
            
        Returns:
            Created opportunity dictionary
        """
        endpoint = "/entity/Default/20.200.001/Opportunity"
        return self._make_request("POST", endpoint, data=opportunity_data)
    
    def update_opportunity(self, opportunity_id: str, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing opportunity.
        
        Args:
            opportunity_id: Opportunity ID
            opportunity_data: Updated opportunity data
            
        Returns:
            Updated opportunity dictionary
        """
        endpoint = f"/entity/Default/20.200.001/Opportunity/{opportunity_id}"
        return self._make_request("PUT", endpoint, data=opportunity_data)
    
    def get_activities(self,
                     contact_id: str = None,
                     account_id: str = None,
                     activity_type: str = None,
                     start_date: str = None,
                     end_date: str = None) -> List[Dict[str, Any]]:
        """
        Get activities from Acumatica CRM.
        
        Args:
            contact_id: Filter by contact ID
            account_id: Filter by account ID
            activity_type: Filter by activity type (Call, Meeting, Task, etc.)
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of activity dictionaries
        """
        endpoint = "/entity/Default/20.200.001/Activity"
        params = {}
        
        if contact_id:
            params["$filter"] = f"ContactID eq '{contact_id}'"
        if account_id:
            params["$filter"] = (params.get("$filter", "") + f" and AccountID eq '{account_id}'").lstrip(" and ")
        if activity_type:
            params["$filter"] = (params.get("$filter", "") + f" and Type eq '{activity_type}'").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new activity in Acumatica CRM.
        
        Args:
            activity_data: Activity data dictionary
            
        Returns:
            Created activity dictionary
        """
        endpoint = "/entity/Default/20.200.001/Activity"
        return self._make_request("POST", endpoint, data=activity_data)
    
    def get_cases(self,
                 status: str = None,
                 priority: str = None,
                 account_id: str = None) -> List[Dict[str, Any]]:
        """
        Get cases from Acumatica CRM.
        
        Args:
            status: Filter by case status
            priority: Filter by priority
            account_id: Filter by account ID
            
        Returns:
            List of case dictionaries
        """
        endpoint = "/entity/Default/20.200.001/Case"
        params = {}
        
        if status:
            params["$filter"] = f"Status eq '{status}'"
        if priority:
            params["$filter"] = (params.get("$filter", "") + f" and Priority eq '{priority}'").lstrip(" and ")
        if account_id:
            params["$filter"] = (params.get("$filter", "") + f" and AccountID eq '{account_id}'").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new case in Acumatica CRM.
        
        Args:
            case_data: Case data dictionary
            
        Returns:
            Created case dictionary
        """
        endpoint = "/entity/Default/20.200.001/Case"
        return self._make_request("POST", endpoint, data=case_data)
    
    def get_leads(self,
                 status: str = None,
                 source: str = None,
                 converted: bool = None) -> List[Dict[str, Any]]:
        """
        Get leads from Acumatica CRM.
        
        Args:
            status: Filter by lead status
            source: Filter by lead source
            converted: Filter by converted status (True/False)
            
        Returns:
            List of lead dictionaries
        """
        endpoint = "/entity/Default/20.200.001/Lead"
        params = {}
        
        if status:
            params["$filter"] = f"Status eq '{status}'"
        if source:
            params["$filter"] = (params.get("$filter", "") + f" and Source eq '{source}'").lstrip(" and ")
        if converted is not None:
            params["$filter"] = (params.get("$filter", "") + f" and Converted eq {str(converted).lower()}").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new lead in Acumatica CRM.
        
        Args:
            lead_data: Lead data dictionary
            
        Returns:
            Created lead dictionary
        """
        endpoint = "/entity/Default/20.200.001/Lead"
        return self._make_request("POST", endpoint, data=lead_data)
    
    def convert_lead_to_opportunity(self, lead_id: str, opportunity_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert a lead to an opportunity.
        
        Args:
            lead_id: Lead ID to convert
            opportunity_data: Optional opportunity data for conversion
            
        Returns:
            Created opportunity dictionary
        """
        # Get lead first
        lead = self._make_request("GET", f"/entity/Default/20.200.001/Lead/{lead_id}")
        
        # Create opportunity from lead
        if not opportunity_data:
            opportunity_data = {
                "AccountID": {"value": lead.get("AccountID", {}).get("value", "")},
                "ContactID": {"value": lead.get("ContactID", {}).get("value", "")},
                "Subject": {"value": lead.get("Subject", {}).get("value", "")},
                "Stage": {"value": "Qualified"},
                "Status": {"value": "New"}
            }
        
        return self.create_opportunity(opportunity_data)
    
    def get_accounts(self,
                    account_class: str = None,
                    status: str = None,
                    industry: str = None) -> List[Dict[str, Any]]:
        """
        Get accounts from Acumatica CRM.
        
        Args:
            account_class: Filter by account class
            status: Filter by status
            industry: Filter by industry
            
        Returns:
            List of account dictionaries
        """
        endpoint = "/entity/Default/20.200.001/Account"
        params = {}
        
        if account_class:
            params["$filter"] = f"AccountClass eq '{account_class}'"
        if status:
            params["$filter"] = (params.get("$filter", "") + f" and Status eq '{status}'").lstrip(" and ")
        if industry:
            params["$filter"] = (params.get("$filter", "") + f" and Industry eq '{industry}'").lstrip(" and ")
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new account in Acumatica CRM.
        
        Args:
            account_data: Account data dictionary
            
        Returns:
            Created account dictionary
        """
        endpoint = "/entity/Default/20.200.001/Account"
        return self._make_request("POST", endpoint, data=account_data)
    
    def get_crm_summary(self, account_id: str = None) -> Dict[str, Any]:
        """
        Get CRM summary statistics for an account or overall.
        
        Args:
            account_id: Optional account ID to filter by
            
        Returns:
            Dictionary with CRM summary statistics
        """
        summary = {}
        
        # Get opportunities
        opps = self.get_opportunities(account_id=account_id)
        summary["total_opportunities"] = len(opps)
        summary["open_opportunities"] = len([o for o in opps if o.get("Status", {}).get("value") != "Closed"])
        summary["total_pipeline_value"] = sum([float(o.get("Estimation", {}).get("value", 0) or 0) for o in opps])
        
        # Get activities
        activities = self.get_activities(account_id=account_id)
        summary["total_activities"] = len(activities)
        summary["recent_activities"] = len([a for a in activities if a.get("Date", {}).get("value")])  # Simplified
        
        # Get cases
        cases = self.get_cases(account_id=account_id)
        summary["total_cases"] = len(cases)
        summary["open_cases"] = len([c for c in cases if c.get("Status", {}).get("value") != "Closed"])
        
        # Get contacts
        contacts = self.get_contacts(account_id=account_id)
        summary["total_contacts"] = len(contacts)
        
        return summary
    
    def logout(self):
        """Logout from Acumatica session."""
        try:
            logout_url = f"{self.base_url}/entity/auth/logout"
            self.session.post(logout_url, timeout=self.timeout)
            logger.info("Acumatica logout successful")
        except Exception as e:
            logger.warning(f"Error during logout: {e}")

