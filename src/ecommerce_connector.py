"""
eCommerce Platform Connector
Generic connector for eCommerce platforms (Shopify, Magento, WooCommerce).
Supports order sync, inventory sync, and product management.
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ECommerceConnector:
    """Generic eCommerce platform connector."""
    
    def __init__(self,
                 platform: str,
                 base_url: str = None,
                 api_key: str = None,
                 api_secret: str = None,
                 access_token: str = None,
                 timeout: int = 30):
        """
        Initialize eCommerce connector.
        
        Args:
            platform: Platform type ('shopify', 'magento', 'woocommerce')
            base_url: Platform API base URL
            api_key: API key (if required)
            api_secret: API secret (if required)
            access_token: OAuth access token (if required)
            timeout: Request timeout in seconds
        """
        self.platform = platform.lower()
        self.base_url = base_url.rstrip('/') if base_url else None
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set up platform-specific headers
        self._setup_headers()
    
    def _setup_headers(self):
        """Set up platform-specific headers."""
        if self.platform == "shopify":
            self.session.headers.update({
                "X-Shopify-Access-Token": self.access_token or "",
                "Content-Type": "application/json"
            })
        elif self.platform == "magento":
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token or ''}",
                "Content-Type": "application/json"
            })
        elif self.platform == "woocommerce":
            # WooCommerce uses Basic Auth
            if self.api_key and self.api_secret:
                from requests.auth import HTTPBasicAuth
                self.session.auth = HTTPBasicAuth(self.api_key, self.api_secret)
            self.session.headers.update({
                "Content-Type": "application/json"
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make API request to eCommerce platform.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response dictionary
        """
        if not self.base_url:
            raise ValueError("Base URL not configured")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"eCommerce API request failed: {e}")
            raise
    
    # Order Operations
    
    def get_orders(self,
                  status: str = None,
                  start_date: str = None,
                  end_date: str = None,
                  limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get orders from eCommerce platform.
        
        Args:
            status: Filter by order status
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of orders to return
            
        Returns:
            List of order dictionaries
        """
        if self.platform == "shopify":
            endpoint = "/admin/api/2023-10/orders.json"
            params = {"limit": limit}
            if status:
                params["status"] = status
            if start_date:
                params["created_at_min"] = start_date
            if end_date:
                params["created_at_max"] = end_date
            
            response = self._make_request("GET", endpoint, params=params)
            return response.get("orders", [])
        
        elif self.platform == "magento":
            endpoint = "/rest/V1/orders"
            params = {"searchCriteria[pageSize]": limit}
            if status:
                params["searchCriteria[filterGroups][0][filters][0][field]"] = "status"
                params["searchCriteria[filterGroups][0][filters][0][value]"] = status
            
            response = self._make_request("GET", endpoint, params=params)
            return response.get("items", [])
        
        elif self.platform == "woocommerce":
            endpoint = "/wp-json/wc/v3/orders"
            params = {"per_page": limit}
            if status:
                params["status"] = status
            if start_date:
                params["after"] = start_date
            if end_date:
                params["before"] = end_date
            
            return self._make_request("GET", endpoint, params=params)
        
        return []
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get a specific order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order dictionary
        """
        if self.platform == "shopify":
            endpoint = f"/admin/api/2023-10/orders/{order_id}.json"
            response = self._make_request("GET", endpoint)
            return response.get("order", {})
        
        elif self.platform == "magento":
            endpoint = f"/rest/V1/orders/{order_id}"
            return self._make_request("GET", endpoint)
        
        elif self.platform == "woocommerce":
            endpoint = f"/wp-json/wc/v3/orders/{order_id}"
            return self._make_request("GET", endpoint)
        
        return {}
    
    def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """
        Update order status.
        
        Args:
            order_id: Order ID
            status: New status
            
        Returns:
            Updated order dictionary
        """
        if self.platform == "shopify":
            endpoint = f"/admin/api/2023-10/orders/{order_id}.json"
            data = {"order": {"id": order_id, "status": status}}
            response = self._make_request("PUT", endpoint, json=data)
            return response.get("order", {})
        
        elif self.platform == "magento":
            endpoint = f"/rest/V1/orders/{order_id}"
            data = {"status": status}
            return self._make_request("PUT", endpoint, json=data)
        
        elif self.platform == "woocommerce":
            endpoint = f"/wp-json/wc/v3/orders/{order_id}"
            data = {"status": status}
            return self._make_request("PUT", endpoint, json=data)
        
        return {}
    
    # Product/Inventory Operations
    
    def get_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get products from eCommerce platform.
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of product dictionaries
        """
        if self.platform == "shopify":
            endpoint = "/admin/api/2023-10/products.json"
            params = {"limit": limit}
            response = self._make_request("GET", endpoint, params=params)
            return response.get("products", [])
        
        elif self.platform == "magento":
            endpoint = "/rest/V1/products"
            params = {"searchCriteria[pageSize]": limit}
            response = self._make_request("GET", endpoint, params=params)
            return response.get("items", [])
        
        elif self.platform == "woocommerce":
            endpoint = "/wp-json/wc/v3/products"
            params = {"per_page": limit}
            return self._make_request("GET", endpoint, params=params)
        
        return []
    
    def get_inventory(self, product_id: str = None) -> List[Dict[str, Any]]:
        """
        Get inventory levels.
        
        Args:
            product_id: Optional product ID to filter by
            
        Returns:
            List of inventory dictionaries
        """
        if self.platform == "shopify":
            endpoint = "/admin/api/2023-10/inventory_levels.json"
            params = {}
            if product_id:
                params["inventory_item_ids"] = product_id
            response = self._make_request("GET", endpoint, params=params)
            return response.get("inventory_levels", [])
        
        elif self.platform == "magento":
            endpoint = "/rest/V1/inventory/sources"
            return self._make_request("GET", endpoint)
        
        elif self.platform == "woocommerce":
            # WooCommerce inventory is part of product data
            if product_id:
                product = self.get_product(product_id)
                return [{"product_id": product_id, "stock_quantity": product.get("stock_quantity", 0)}]
            else:
                products = self.get_products()
                return [{"product_id": p.get("id"), "stock_quantity": p.get("stock_quantity", 0)} for p in products]
        
        return []
    
    def update_inventory(self, product_id: str, quantity: int, location_id: str = None) -> Dict[str, Any]:
        """
        Update inventory quantity.
        
        Args:
            product_id: Product ID
            quantity: New quantity
            location_id: Location ID (if multi-location)
            
        Returns:
            Updated inventory dictionary
        """
        if self.platform == "shopify":
            endpoint = "/admin/api/2023-10/inventory_levels/set.json"
            data = {
                "location_id": location_id or 1,
                "inventory_item_id": product_id,
                "available": quantity
            }
            return self._make_request("POST", endpoint, json=data)
        
        elif self.platform == "magento":
            endpoint = f"/rest/V1/products/{product_id}/stockItems/{product_id}"
            data = {"qty": quantity}
            return self._make_request("PUT", endpoint, json=data)
        
        elif self.platform == "woocommerce":
            endpoint = f"/wp-json/wc/v3/products/{product_id}"
            data = {"stock_quantity": quantity}
            return self._make_request("PUT", endpoint, json=data)
        
        return {}
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """
        Get a specific product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product dictionary
        """
        if self.platform == "shopify":
            endpoint = f"/admin/api/2023-10/products/{product_id}.json"
            response = self._make_request("GET", endpoint)
            return response.get("product", {})
        
        elif self.platform == "magento":
            endpoint = f"/rest/V1/products/{product_id}"
            return self._make_request("GET", endpoint)
        
        elif self.platform == "woocommerce":
            endpoint = f"/wp-json/wc/v3/products/{product_id}"
            return self._make_request("GET", endpoint)
        
        return {}
    
    # Integration Helpers
    
    def sync_order_to_acumatica_format(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert eCommerce order to Acumatica Sales Order format.
        
        Args:
            order: eCommerce order dictionary
            
        Returns:
            Acumatica Sales Order format dictionary
        """
        # Extract order data based on platform
        if self.platform == "shopify":
            order_number = order.get("order_number", "")
            customer_email = order.get("email", "")
            line_items = order.get("line_items", [])
            total = float(order.get("total_price", 0))
        
        elif self.platform == "magento":
            order_number = order.get("increment_id", "")
            customer_email = order.get("customer_email", "")
            line_items = order.get("items", [])
            total = float(order.get("grand_total", 0))
        
        elif self.platform == "woocommerce":
            order_number = str(order.get("id", ""))
            customer_email = order.get("billing", {}).get("email", "")
            line_items = order.get("line_items", [])
            total = float(order.get("total", 0))
        
        else:
            return {}
        
        # Convert to Acumatica format
        acumatica_order = {
            "OrderType": {"value": "SO"},
            "CustomerID": {"value": customer_email},  # May need mapping
            "OrderDate": {"value": datetime.now().strftime("%Y-%m-%d")},
            "OrderNbr": {"value": order_number},
            "Details": []
        }
        
        # Add line items
        for idx, item in enumerate(line_items):
            if self.platform == "shopify":
                product_id = item.get("sku", "")
                quantity = float(item.get("quantity", 0))
                price = float(item.get("price", 0))
            elif self.platform == "magento":
                product_id = item.get("sku", "")
                quantity = float(item.get("qty_ordered", 0))
                price = float(item.get("price", 0))
            elif self.platform == "woocommerce":
                product_id = item.get("sku", "")
                quantity = float(item.get("quantity", 0))
                price = float(item.get("price", 0))
            else:
                continue
            
            acumatica_order["Details"].append({
                "InventoryID": {"value": product_id},
                "OrderQty": {"value": quantity},
                "UnitPrice": {"value": price},
                "LineNbr": {"value": idx + 1}
            })
        
        return acumatica_order
    
    def sync_inventory_from_acumatica(self, acumatica_inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sync inventory from Acumatica to eCommerce platform.
        
        Args:
            acumatica_inventory: List of inventory items from Acumatica
            
        Returns:
            Sync results dictionary
        """
        results = {"updated": 0, "errors": []}
        
        for item in acumatica_inventory:
            try:
                product_id = item.get("InventoryID", "")
                quantity = item.get("QuantityOnHand", 0)
                
                self.update_inventory(product_id, quantity)
                results["updated"] += 1
            except Exception as e:
                results["errors"].append(f"Failed to update {product_id}: {str(e)}")
        
        return results

