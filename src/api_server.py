"""
REST API Server
Provides REST API endpoints for EDI processing and integration management.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, Any
import yaml
from pathlib import Path

from .edi_processor import EDIProcessor
from .metrics_collector import MetricsCollector
from .ai_automation import PredictiveAnalytics
from .security_audit import SecurityAudit, ComplianceReporter

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Global instances (initialized on startup)
processor = None
metrics_collector = None
predictive_analytics = None
security_audit = None


def init_app(config_path: str = "config/config.yaml"):
    """Initialize the API server with configuration."""
    global processor, metrics_collector, predictive_analytics, security_audit
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Load branding
    branding = {}
    try:
        with open("config/branding.yaml", 'r') as f:
            branding_data = yaml.safe_load(f)
            branding = branding_data.get("branding", {})
    except:
        pass
    
    # Initialize components
    processor = EDIProcessor(config)
    metrics_collector = MetricsCollector()
    predictive_analytics = PredictiveAnalytics()
    security_audit = SecurityAudit()
    
    logger.info("API Server initialized")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Load branding if available
    company_name = "EDI Processor"
    try:
        import yaml
        with open("config/branding.yaml", 'r') as f:
            branding = yaml.safe_load(f)
            company_name = branding.get("branding", {}).get("company_name", "EDI Processor")
    except:
        pass
    
    return jsonify({
        "status": "healthy",
        "service": "EDI Processor API",
        "company": company_name,
        "version": "2.0.0"
    }), 200


@app.route('/api/v1/process', methods=['POST'])
def process_edi_file():
    """Process an EDI file."""
    try:
        data = request.json
        filepath = data.get('filepath')
        
        if not filepath:
            return jsonify({"error": "filepath is required"}), 400
        
        # Log access
        security_audit.log_access(
            user=request.remote_addr,
            resource=filepath,
            action="process_file",
            success=True
        )
        
        # Process file
        result = processor.process_file(filepath)
        
        return jsonify(result), 200 if result.get("success") else 500
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """Get processing metrics."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        metrics = metrics_collector.get_summary(start_date, end_date)
        
        # Log data access
        security_audit.log_data_access(
            user=request.remote_addr,
            data_type="metrics",
            record_count=1
        )
        
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/predictions', methods=['GET'])
def get_predictions():
    """Get predictive analytics."""
    try:
        transaction_type = request.args.get('transaction_type')
        days_ahead = int(request.args.get('days_ahead', 7))
        
        if transaction_type:
            predicted_time, confidence = predictive_analytics.predict_processing_time(transaction_type)
            volume_prediction = predictive_analytics.predict_volume(transaction_type, days_ahead)
            
            return jsonify({
                "transaction_type": transaction_type,
                "predicted_processing_time": predicted_time,
                "confidence_interval": confidence,
                "volume_prediction": volume_prediction
            }), 200
        else:
            insights = predictive_analytics.get_processing_insights()
            return jsonify(insights), 200
        
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/compliance/access-report', methods=['GET'])
def get_access_report():
    """Get access report for compliance."""
    try:
        start_date = request.args.get('start_date', '2025-01-01')
        end_date = request.args.get('end_date', '2025-12-31')
        
        reporter = ComplianceReporter(security_audit)
        report = reporter.generate_access_report(start_date, end_date)
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Error getting access report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/compliance/data-access-report', methods=['GET'])
def get_data_access_report():
    """Get data access report for compliance."""
    try:
        start_date = request.args.get('start_date', '2025-01-01')
        end_date = request.args.get('end_date', '2025-12-31')
        
        reporter = ComplianceReporter(security_audit)
        report = reporter.generate_data_access_report(start_date, end_date)
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Error getting data access report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/status', methods=['GET'])
def get_status():
    """Get system status."""
    try:
        # Get recent metrics
        metrics = metrics_collector.get_summary()
        
        # Get insights
        insights = predictive_analytics.get_processing_insights()
        
        status = {
            "service": "EDI Processor",
            "status": "operational",
            "metrics": {
                "total_processed": metrics.get("total_processed", 0),
                "success_rate": metrics.get("success_rate", 0),
                "error_rate": metrics.get("error_rate", 0)
            },
            "insights": insights.get("recommendations", [])
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=5000, debug=False)

