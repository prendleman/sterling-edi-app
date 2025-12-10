"""
IBM Sterling B2B Integrator Integration
Provides file system and API integration with Sterling.
"""

import os
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .utils.file_utils import safe_move_file, safe_copy_file, ensure_directory_exists

logger = logging.getLogger(__name__)


class SterlingIntegration:
    """Integration with IBM Sterling B2B Integrator."""
    
    def __init__(self, 
                 pickup_directories: List[str] = None,
                 delivery_directories: List[str] = None,
                 api_base_url: str = None,
                 api_username: str = None,
                 api_password: str = None,
                 api_timeout: int = 30):
        """
        Initialize Sterling integration.
        
        Args:
            pickup_directories: Sterling pickup directories to read from
            delivery_directories: Sterling delivery directories to write to
            api_base_url: Sterling API base URL (e.g., https://sterling-server:9080)
            api_username: API username
            api_password: API password
            api_timeout: API request timeout in seconds
        """
        self.pickup_directories = [Path(d) for d in (pickup_directories or [])]
        self.delivery_directories = [Path(d) for d in (delivery_directories or [])]
        self.api_base_url = api_base_url
        self.api_username = api_username
        self.api_password = api_password
        self.api_timeout = api_timeout
        self.api_session = None
        
        # Ensure directories exist
        for directory in self.pickup_directories + self.delivery_directories:
            ensure_directory_exists(str(directory))
    
    # File System Integration Methods
    
    def read_from_pickup(self, trading_partner: Optional[str] = None) -> List[str]:
        """
        Read EDI files from Sterling pickup directories.
        
        Args:
            trading_partner: Optional trading partner name to filter files
            
        Returns:
            List of file paths
        """
        files = []
        
        for pickup_dir in self.pickup_directories:
            if not pickup_dir.exists():
                logger.warning(f"Pickup directory does not exist: {pickup_dir}")
                continue
            
            # Look for EDI files
            for filepath in pickup_dir.glob('*'):
                if not filepath.is_file():
                    continue
                
                # Filter by trading partner if specified
                if trading_partner and trading_partner.lower() not in filepath.name.lower():
                    continue
                
                # Check for common EDI extensions
                if filepath.suffix.lower() in ['.edi', '.x12', '.edifact', '.txt']:
                    files.append(str(filepath))
        
        logger.info(f"Found {len(files)} file(s) in pickup directories")
        return files
    
    def write_to_delivery(self, 
                         filepath: str,
                         trading_partner: Optional[str] = None,
                         file_type: str = "EDI") -> bool:
        """
        Write EDI file to Sterling delivery directory.
        
        Args:
            filepath: Source file path
            trading_partner: Trading partner name (used in filename)
            file_type: File type identifier
            
        Returns:
            True if successful
        """
        if not self.delivery_directories:
            logger.error("No delivery directories configured")
            return False
        
        # Use first delivery directory (or could implement routing logic)
        delivery_dir = self.delivery_directories[0]
        
        # Generate Sterling-compliant filename
        source_file = Path(filepath)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        if trading_partner:
            filename = f"{trading_partner}_{file_type}_{timestamp}{source_file.suffix}"
        else:
            filename = f"{file_type}_{timestamp}{source_file.suffix}"
        
        destination = delivery_dir / filename
        
        # Copy file to delivery directory
        if safe_copy_file(filepath, str(destination)):
            logger.info(f"File delivered to Sterling: {destination}")
            return True
        else:
            logger.error(f"Failed to deliver file to Sterling: {destination}")
            return False
    
    def move_to_processed(self, filepath: str, processed_dir: str = "processed") -> bool:
        """
        Move file to processed directory (after successful processing).
        
        Args:
            filepath: File to move
            processed_dir: Processed directory (relative to pickup directory)
            
        Returns:
            True if successful
        """
        source_path = Path(filepath)
        
        # Find which pickup directory this file is in
        pickup_dir = None
        for pd in self.pickup_directories:
            try:
                source_path.relative_to(pd)
                pickup_dir = pd
                break
            except ValueError:
                continue
        
        if not pickup_dir:
            logger.warning(f"File not in any pickup directory: {filepath}")
            return False
        
        processed_path = pickup_dir / processed_dir / source_path.name
        ensure_directory_exists(str(processed_path.parent))
        
        return safe_move_file(filepath, str(processed_path))
    
    def move_to_error(self, filepath: str, error_dir: str = "error") -> bool:
        """
        Move file to error directory (after failed processing).
        
        Args:
            filepath: File to move
            error_dir: Error directory (relative to pickup directory)
            
        Returns:
            True if successful
        """
        source_path = Path(filepath)
        
        # Find which pickup directory this file is in
        pickup_dir = None
        for pd in self.pickup_directories:
            try:
                source_path.relative_to(pd)
                pickup_dir = pd
                break
            except ValueError:
                continue
        
        if not pickup_dir:
            logger.warning(f"File not in any pickup directory: {filepath}")
            return False
        
        error_path = pickup_dir / error_dir / source_path.name
        ensure_directory_exists(str(error_path.parent))
        
        return safe_move_file(filepath, str(error_path))
    
    # API Integration Methods
    
    def _get_api_session(self) -> Optional[requests.Session]:
        """Get or create API session."""
        if not self.api_base_url:
            return None
        
        if not self.api_session:
            self.api_session = requests.Session()
            if self.api_username and self.api_password:
                self.api_session.auth = (self.api_username, self.api_password)
        
        return self.api_session
    
    def submit_file_via_api(self, 
                           filepath: str,
                           trading_partner: str,
                           document_type: str = "EDI") -> Dict[str, Any]:
        """
        Submit EDI file to Sterling via API.
        
        Args:
            filepath: Path to EDI file
            trading_partner: Trading partner identifier
            document_type: Document type
            
        Returns:
            API response dictionary
        """
        session = self._get_api_session()
        if not session:
            logger.error("API not configured")
            return {"success": False, "error": "API not configured"}
        
        try:
            # Read file content
            with open(filepath, 'rb') as f:
                file_content = f.read()
            
            # Prepare API request
            url = f"{self.api_base_url}/api/v1/documents"
            files = {
                'file': (Path(filepath).name, file_content, 'application/octet-stream')
            }
            data = {
                'trading_partner': trading_partner,
                'document_type': document_type
            }
            
            # Submit file
            response = session.post(
                url,
                files=files,
                data=data,
                timeout=self.api_timeout
            )
            
            response.raise_for_status()
            
            result = {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.content else {}
            }
            
            logger.info(f"File submitted via API: {filepath}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_processing_status(self, document_id: str) -> Dict[str, Any]:
        """
        Get processing status from Sterling API.
        
        Args:
            document_id: Document ID from previous submission
            
        Returns:
            Status information
        """
        session = self._get_api_session()
        if not session:
            logger.error("API not configured")
            return {"success": False, "error": "API not configured"}
        
        try:
            url = f"{self.api_base_url}/api/v1/documents/{document_id}/status"
            response = session.get(url, timeout=self.api_timeout)
            response.raise_for_status()
            
            return {
                "success": True,
                "status": response.json() if response.content else {}
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_trading_partner_config(self, trading_partner: str) -> Dict[str, Any]:
        """
        Get trading partner configuration from Sterling API.
        
        Args:
            trading_partner: Trading partner identifier
            
        Returns:
            Trading partner configuration
        """
        session = self._get_api_session()
        if not session:
            logger.error("API not configured")
            return {"success": False, "error": "API not configured"}
        
        try:
            url = f"{self.api_base_url}/api/v1/trading-partners/{trading_partner}"
            response = session.get(url, timeout=self.api_timeout)
            response.raise_for_status()
            
            return {
                "success": True,
                "config": response.json() if response.content else {}
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_trading_partners(self) -> List[str]:
        """
        List all trading partners from Sterling API.
        
        Returns:
            List of trading partner identifiers
        """
        session = self._get_api_session()
        if not session:
            logger.error("API not configured")
            return []
        
        try:
            url = f"{self.api_base_url}/api/v1/trading-partners"
            response = session.get(url, timeout=self.api_timeout)
            response.raise_for_status()
            
            data = response.json() if response.content else {}
            return data.get("trading_partners", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []

