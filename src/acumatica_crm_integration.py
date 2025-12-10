"""
Acumatica CRM Integration
Specialized integration layer for Acumatica CRM functionality.
Builds on the Acumatica connector to provide CRM-specific workflows.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .acumatica_connector import AcumaticaConnector

logger = logging.getLogger(__name__)


class AcumaticaCRMIntegration:
    """Specialized CRM integration layer for Acumatica."""
    
    def __init__(self, acumatica_connector: AcumaticaConnector):
        """
        Initialize CRM integration.
        
        Args:
            acumatica_connector: AcumaticaConnector instance
        """
        self.acumatica = acumatica_connector
    
    def sync_edi_customer_to_crm(self, edi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync EDI customer data to Acumatica CRM as a contact/account.
        
        Args:
            edi_data: Parsed EDI data with customer information
            
        Returns:
            Created contact/account dictionary
        """
        # Extract customer data from EDI
        parties = edi_data.get("data", {}).get("data", {}).get("parties", [])
        if not parties:
            raise ValueError("No customer/party data found in EDI")
        
        customer_data = parties[0]
        customer_name = customer_data.get("name", "")
        customer_id = customer_data.get("id", "")
        
        # Check if account exists
        accounts = self.acumatica.get_accounts()
        existing_account = next((a for a in accounts if a.get("AccountName", {}).get("value") == customer_name), None)
        
        if existing_account:
            account_id = existing_account.get("AccountID", {}).get("value")
            logger.info(f"Account exists: {account_id}")
        else:
            # Create new account
            account_data = {
                "AccountName": {"value": customer_name},
                "AccountID": {"value": customer_id or customer_name[:20]},
                "AccountClass": {"value": "Customer"},
                "Status": {"value": "Active"}
            }
            existing_account = self.acumatica.create_account(account_data)
            account_id = existing_account.get("AccountID", {}).get("value")
            logger.info(f"Created new account: {account_id}")
        
        # Create or update contact
        contacts = self.acumatica.get_contacts(account_id=account_id)
        existing_contact = contacts[0] if contacts else None
        
        if existing_contact:
            logger.info(f"Contact exists for account: {account_id}")
            return existing_contact
        else:
            contact_data = {
                "AccountID": {"value": account_id},
                "DisplayName": {"value": customer_name},
                "ContactType": {"value": "Primary"},
                "Status": {"value": "Active"}
            }
            contact = self.acumatica.create_contact(contact_data)
            logger.info(f"Created new contact for account: {account_id}")
            return contact
    
    def create_opportunity_from_edi_order(self, edi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create CRM opportunity from EDI order (850 Purchase Order).
        
        Args:
            edi_data: Parsed EDI 850 data
            
        Returns:
            Created opportunity dictionary
        """
        # Extract order data
        order_data = edi_data.get("data", {}).get("data", {})
        po_number = order_data.get("po_number", "")
        po_date = order_data.get("po_date", datetime.now().strftime("%Y-%m-%d"))
        parties = order_data.get("parties", [])
        line_items = order_data.get("line_items", [])
        
        # Calculate total value
        total_value = sum([
            float(item.get("quantity", 0) or 0) * float(item.get("unit_price", 0) or 0)
            for item in line_items
        ])
        
        # Get or create account
        customer_name = parties[0].get("name", "") if parties else ""
        accounts = self.acumatica.get_accounts()
        account = next((a for a in accounts if a.get("AccountName", {}).get("value") == customer_name), None)
        
        if not account:
            # Create account first
            account_data = {
                "AccountName": {"value": customer_name},
                "AccountClass": {"value": "Customer"},
                "Status": {"value": "Active"}
            }
            account = self.acumatica.create_account(account_data)
        
        account_id = account.get("AccountID", {}).get("value")
        
        # Create opportunity
        opportunity_data = {
            "AccountID": {"value": account_id},
            "Subject": {"value": f"Purchase Order {po_number}"},
            "Stage": {"value": "Qualified"},
            "Status": {"value": "New"},
            "Estimation": {"value": total_value},
            "CurrencyID": {"value": "USD"},
            "Probability": {"value": 75},
            "ExpectedCloseDate": {"value": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")}
        }
        
        opportunity = self.acumatica.create_opportunity(opportunity_data)
        logger.info(f"Created opportunity from EDI order: {po_number}")
        return opportunity
    
    def log_edi_activity(self, edi_data: Dict[str, Any], activity_type: str = "EDI Processing") -> Dict[str, Any]:
        """
        Log EDI processing as a CRM activity.
        
        Args:
            edi_data: Parsed EDI data
            activity_type: Type of activity (default: "EDI Processing")
            
        Returns:
            Created activity dictionary
        """
        # Extract customer info
        parties = edi_data.get("data", {}).get("data", {}).get("parties", [])
        customer_name = parties[0].get("name", "") if parties else ""
        
        # Find account
        accounts = self.acumatica.get_accounts()
        account = next((a for a in accounts if a.get("AccountName", {}).get("value") == customer_name), None)
        
        if not account:
            return {}
        
        account_id = account.get("AccountID", {}).get("value")
        contacts = self.acumatica.get_contacts(account_id=account_id)
        contact_id = contacts[0].get("ContactID", {}).get("value") if contacts else None
        
        # Create activity
        transaction_type = edi_data.get("data", {}).get("transaction_type") or edi_data.get("data", {}).get("message_type", "")
        activity_data = {
            "Type": {"value": activity_type},
            "Subject": {"value": f"EDI {transaction_type} Processed"},
            "AccountID": {"value": account_id},
            "ContactID": {"value": contact_id} if contact_id else None,
            "StartDate": {"value": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")},
            "Status": {"value": "Completed"},
            "Description": {"value": f"EDI transaction {transaction_type} processed successfully"}
        }
        
        activity = self.acumatica.create_activity(activity_data)
        logger.info(f"Logged EDI activity for account: {account_id}")
        return activity
    
    def get_sales_pipeline_summary(self) -> Dict[str, Any]:
        """
        Get sales pipeline summary from CRM.
        
        Returns:
            Dictionary with pipeline statistics
        """
        all_opportunities = self.acumatica.get_opportunities()
        
        summary = {
            "total_opportunities": len(all_opportunities),
            "by_stage": {},
            "total_pipeline_value": 0,
            "weighted_pipeline_value": 0
        }
        
        for opp in all_opportunities:
            stage = opp.get("Stage", {}).get("value", "Unknown")
            value = float(opp.get("Estimation", {}).get("value", 0) or 0)
            probability = float(opp.get("Probability", {}).get("value", 0) or 0)
            
            summary["by_stage"][stage] = summary["by_stage"].get(stage, 0) + 1
            summary["total_pipeline_value"] += value
            summary["weighted_pipeline_value"] += (value * probability / 100)
        
        return summary
    
    def get_account_360_view(self, account_id: str) -> Dict[str, Any]:
        """
        Get 360-degree view of an account (CRM + ERP data).
        
        Args:
            account_id: Account ID
            
        Returns:
            Dictionary with comprehensive account information
        """
        view = {
            "account": None,
            "contacts": [],
            "opportunities": [],
            "activities": [],
            "cases": [],
            "sales_orders": [],
            "ar_transactions": []
        }
        
        # Get account
        accounts = self.acumatica.get_accounts()
        view["account"] = next((a for a in accounts if a.get("AccountID", {}).get("value") == account_id), None)
        
        if not view["account"]:
            return view
        
        # Get CRM data
        view["contacts"] = self.acumatica.get_contacts(account_id=account_id)
        view["opportunities"] = self.acumatica.get_opportunities(account_id=account_id)
        view["activities"] = self.acumatica.get_activities(account_id=account_id)
        view["cases"] = self.acumatica.get_cases(account_id=account_id)
        
        # Get ERP data
        customer_id = view["account"].get("AccountID", {}).get("value")
        view["sales_orders"] = self.acumatica.get_sales_orders(customer_id=customer_id)
        view["ar_transactions"] = self.acumatica.get_ar_transactions(customer_id=customer_id)
        
        return view

