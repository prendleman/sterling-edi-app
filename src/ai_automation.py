"""
AI and Automation Features
Intelligent EDI validation, automated error handling, and predictive analytics.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class AIValidator:
    """AI-powered EDI validation with pattern recognition and anomaly detection."""
    
    def __init__(self):
        """Initialize AI validator."""
        self.validation_patterns = {}
        self.anomaly_threshold = 0.1  # 10% deviation from normal
        self.historical_data = defaultdict(list)
    
    def learn_pattern(self, field_name: str, valid_values: List[Any], pattern: str = None):
        """
        Learn validation pattern from historical data.
        
        Args:
            field_name: Field name to learn pattern for
            valid_values: List of valid values seen
            pattern: Optional regex pattern
        """
        self.validation_patterns[field_name] = {
            "valid_values": set(valid_values),
            "pattern": pattern,
            "count": len(valid_values)
        }
    
    def validate_with_ai(self, data: Dict[str, Any], transaction_type: str) -> Dict[str, Any]:
        """
        Validate EDI data using AI/ML patterns.
        
        Args:
            data: EDI data to validate
            transaction_type: Transaction type (850, 810, etc.)
            
        Returns:
            Validation results with AI insights
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "anomalies": [],
            "confidence": 1.0
        }
        
        # Pattern-based validation
        for field, value in data.items():
            if field in self.validation_patterns:
                pattern_info = self.validation_patterns[field]
                
                # Check if value matches learned pattern
                if pattern_info["pattern"]:
                    if not re.match(pattern_info["pattern"], str(value)):
                        results["warnings"].append(
                            f"Field '{field}' value '{value}' doesn't match learned pattern"
                        )
                        results["confidence"] *= 0.9
                
                # Check if value is in learned valid set
                if pattern_info["valid_values"] and value not in pattern_info["valid_values"]:
                    results["warnings"].append(
                        f"Field '{field}' value '{value}' not seen in historical data"
                    )
                    results["confidence"] *= 0.95
        
        # Anomaly detection
        anomalies = self.detect_anomalies(data, transaction_type)
        if anomalies:
            results["anomalies"] = anomalies
            results["warnings"].extend([f"Anomaly detected: {a}" for a in anomalies])
            results["confidence"] *= 0.8
        
        results["valid"] = len(results["errors"]) == 0
        return results
    
    def detect_anomalies(self, data: Dict[str, Any], transaction_type: str) -> List[str]:
        """
        Detect anomalies in EDI data.
        
        Args:
            data: EDI data
            transaction_type: Transaction type
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        historical = self.historical_data.get(transaction_type, [])
        
        if not historical:
            return anomalies
        
        # Check for unusual values
        for field, value in data.items():
            if field in ["amount", "quantity", "unit_price"]:
                values = [h.get(field) for h in historical if h.get(field)]
                if values:
                    mean_val = statistics.mean(values)
                    std_val = statistics.stdev(values) if len(values) > 1 else 0
                    
                    if std_val > 0:
                        z_score = abs((float(value) - mean_val) / std_val)
                        if z_score > 2:  # More than 2 standard deviations
                            anomalies.append(
                                f"{field} value {value} is {z_score:.2f} standard deviations from mean"
                            )
        
        return anomalies
    
    def update_historical_data(self, transaction_type: str, data: Dict[str, Any]):
        """
        Update historical data for learning.
        
        Args:
            transaction_type: Transaction type
            data: Transaction data
        """
        self.historical_data[transaction_type].append(data)
        
        # Keep only last 1000 records per transaction type
        if len(self.historical_data[transaction_type]) > 1000:
            self.historical_data[transaction_type] = self.historical_data[transaction_type][-1000:]


class AutomatedErrorHandler:
    """Automated error handling and retry logic."""
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        """
        Initialize automated error handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.error_patterns = {
            "connection": ["timeout", "connection", "network", "unreachable"],
            "authentication": ["unauthorized", "forbidden", "auth", "login"],
            "validation": ["invalid", "validation", "format", "parse"],
            "server": ["server error", "500", "503", "service unavailable"]
        }
    
    def classify_error(self, error: Exception) -> str:
        """
        Classify error type for appropriate handling.
        
        Args:
            error: Exception object
            
        Returns:
            Error classification
        """
        error_str = str(error).lower()
        
        for error_type, patterns in self.error_patterns.items():
            if any(pattern in error_str for pattern in patterns):
                return error_type
        
        return "unknown"
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if error should be retried.
        
        Args:
            error: Exception object
            attempt: Current attempt number
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False
        
        error_type = self.classify_error(error)
        
        # Retry connection and server errors
        if error_type in ["connection", "server"]:
            return True
        
        # Don't retry authentication or validation errors
        if error_type in ["authentication", "validation"]:
            return False
        
        return True
    
    def get_retry_delay(self, attempt: int, error_type: str) -> int:
        """
        Calculate retry delay with exponential backoff.
        
        Args:
            attempt: Current attempt number
            error_type: Error classification
            
        Returns:
            Delay in seconds
        """
        base_delay = self.retry_delay
        exponential_delay = base_delay * (2 ** attempt)
        return min(exponential_delay, 60)  # Cap at 60 seconds
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle error with automated recovery suggestions.
        
        Args:
            error: Exception object
            context: Additional context
            
        Returns:
            Error handling result
        """
        error_type = self.classify_error(error)
        
        result = {
            "error_type": error_type,
            "error_message": str(error),
            "suggested_action": self._get_suggested_action(error_type),
            "retryable": error_type in ["connection", "server"]
        }
        
        if context:
            result["context"] = context
        
        return result
    
    def _get_suggested_action(self, error_type: str) -> str:
        """Get suggested action for error type."""
        actions = {
            "connection": "Check network connectivity and retry",
            "authentication": "Verify credentials and API keys",
            "validation": "Review data format and validation rules",
            "server": "Wait for service recovery and retry",
            "unknown": "Review error details and contact support"
        }
        return actions.get(error_type, "Review error and retry if appropriate")


class PredictiveAnalytics:
    """Predictive analytics for EDI processing."""
    
    def __init__(self):
        """Initialize predictive analytics."""
        self.processing_times = defaultdict(list)
        self.error_rates = defaultdict(float)
        self.volume_trends = defaultdict(list)
    
    def record_processing_time(self, transaction_type: str, processing_time: float):
        """
        Record processing time for analysis.
        
        Args:
            transaction_type: Transaction type
            processing_time: Processing time in seconds
        """
        self.processing_times[transaction_type].append(processing_time)
        
        # Keep only last 100 records
        if len(self.processing_times[transaction_type]) > 100:
            self.processing_times[transaction_type] = self.processing_times[transaction_type][-100:]
    
    def predict_processing_time(self, transaction_type: str) -> Tuple[float, float]:
        """
        Predict processing time for transaction type.
        
        Args:
            transaction_type: Transaction type
            
        Returns:
            Tuple of (predicted_time, confidence_interval)
        """
        times = self.processing_times.get(transaction_type, [])
        
        if not times:
            return (0.0, 0.0)
        
        mean_time = statistics.mean(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        
        return (mean_time, std_time)
    
    def predict_volume(self, transaction_type: str, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict transaction volume.
        
        Args:
            transaction_type: Transaction type
            days_ahead: Number of days to predict ahead
            
        Returns:
            Prediction dictionary
        """
        volumes = self.volume_trends.get(transaction_type, [])
        
        if len(volumes) < 7:
            return {"predicted_volume": 0, "confidence": "low"}
        
        # Simple linear trend prediction
        recent_volumes = volumes[-7:]  # Last week
        avg_volume = statistics.mean(recent_volumes)
        
        # Calculate trend
        if len(volumes) >= 14:
            older_avg = statistics.mean(volumes[-14:-7])
            trend = (avg_volume - older_avg) / older_avg if older_avg > 0 else 0
        else:
            trend = 0
        
        predicted_volume = avg_volume * (1 + trend) * days_ahead
        
        return {
            "predicted_volume": int(predicted_volume),
            "trend": trend,
            "confidence": "medium" if len(volumes) >= 14 else "low"
        }
    
    def get_processing_insights(self) -> Dict[str, Any]:
        """
        Get processing insights and recommendations.
        
        Returns:
            Insights dictionary
        """
        insights = {
            "average_processing_times": {},
            "slowest_transactions": [],
            "recommendations": []
        }
        
        # Calculate average processing times
        for trans_type, times in self.processing_times.items():
            if times:
                insights["average_processing_times"][trans_type] = {
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "max": max(times)
                }
        
        # Identify slowest transactions
        for trans_type, times in self.processing_times.items():
            if times:
                avg_time = statistics.mean(times)
                insights["slowest_transactions"].append({
                    "type": trans_type,
                    "average_time": avg_time
                })
        
        insights["slowest_transactions"].sort(key=lambda x: x["average_time"], reverse=True)
        
        # Generate recommendations
        if insights["slowest_transactions"]:
            slowest = insights["slowest_transactions"][0]
            if slowest["average_time"] > 5.0:
                insights["recommendations"].append(
                    f"Consider optimizing {slowest['type']} processing (avg: {slowest['average_time']:.2f}s)"
                )
        
        return insights

