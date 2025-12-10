# REST API Reference

The EDI application provides a REST API for programmatic access to EDI processing and system management.

## API Architecture

```mermaid
graph TB
    subgraph clients["API Clients"]
        WebClient["Web Client<br/>Browser"]
        RESTClient["REST Client<br/>curl/Postman"]
        PythonClient["Python Client<br/>requests library"]
        Integration["External Integration<br/>Third-party Systems"]
    end
    
    subgraph api["REST API Server"]
        Router["Flask Router<br/>Request Routing"]
        
        subgraph endpoints["API Endpoints"]
            Health["/health<br/>Health Check"]
            Process["/api/v1/process<br/>Process EDI File"]
            Metrics["/api/v1/metrics<br/>Get Metrics"]
            Predictions["/api/v1/predictions<br/>Get Predictions"]
            Status["/api/v1/status<br/>System Status"]
            Compliance["/api/v1/compliance<br/>Compliance Reports"]
        end
        
        subgraph middleware["Middleware"]
            CORS["CORS Handler<br/>Cross-Origin Support"]
            Logging["Request Logging<br/>Access Logs"]
            ErrorHandler["Error Handler<br/>Exception Handling"]
        end
    end
    
    subgraph services["Backend Services"]
        EDIProcessor["EDI Processor<br/>Core Processing Engine"]
        MetricsCollector["Metrics Collector<br/>Data Collection"]
        PredictiveAnalytics["Predictive Analytics<br/>Forecasting"]
        ComplianceReporter["Compliance Reporter<br/>GDPR/HIPAA/SOX"]
        SecurityAudit["Security Audit<br/>Access Logging"]
    end
    
    WebClient --> Router
    RESTClient --> Router
    PythonClient --> Router
    Integration --> Router
    
    Router --> Health
    Router --> Process
    Router --> Metrics
    Router --> Predictions
    Router --> Status
    Router --> Compliance
    
    Health --> CORS
    Process --> Logging
    Process --> ErrorHandler
    Metrics --> Logging
    Predictions --> Logging
    Compliance --> Logging
    
    Process --> EDIProcessor
    Metrics --> MetricsCollector
    Predictions --> PredictiveAnalytics
    Compliance --> ComplianceReporter
    Process --> SecurityAudit
```

### Request/Response Flow

```mermaid
sequenceDiagram
    participant Client as API Client
    participant API as REST API Server
    participant Security as Security Audit
    participant Processor as EDI Processor
    participant Metrics as Metrics Collector
    participant DB as Database
    
    Client->>API: HTTP Request (POST/GET)
    API->>Security: Log Access Request
    Security->>DB: Store Audit Log Entry
    API->>API: Validate Request Format
    API->>API: Check Authentication (Future)
    
    alt Process Request
        API->>Processor: Process EDI File
        Processor->>Processor: Parse & Validate
        Processor->>Metrics: Record Processing Metrics
        Metrics->>DB: Store Metrics Data
        Processor-->>API: Return Processing Result
    else Get Metrics
        API->>Metrics: Retrieve Metrics
        Metrics->>DB: Query Metrics Data
        Metrics-->>API: Return Metrics
    else Get Predictions
        API->>Metrics: Get Predictive Analytics
        Metrics->>DB: Query Historical Data
        Metrics-->>API: Return Predictions
    end
    
    API->>Security: Log Access Success
    Security->>DB: Update Audit Log
    API-->>Client: HTTP Response (JSON)
```

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Currently, the API uses IP-based access logging. For production, implement proper authentication (API keys, OAuth, etc.).

## Endpoints

### Health Check

**GET** `/health`

Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "EDI Processor API",
  "version": "1.4.0"
}
```

### Process EDI File

**POST** `/api/v1/process`

Process an EDI file.

**Request Body:**
```json
{
  "filepath": "/path/to/edi/file.x12"
}
```

**Response:**
```json
{
  "filepath": "/path/to/edi/file.x12",
  "success": true,
  "edi_type": "X12",
  "data": {
    "transaction_type": "850",
    "po_number": "PO12345"
  },
  "processing_time_ms": 250
}
```

### Get Metrics

**GET** `/api/v1/metrics`

Get processing metrics.

**Query Parameters:**
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "total_processed": 1000,
  "success_count": 950,
  "failed_count": 50,
  "success_rate": 0.95,
  "error_rate": 0.05
}
```

### Get Predictions

**GET** `/api/v1/predictions`

Get predictive analytics.

**Query Parameters:**
- `transaction_type` (optional): Filter by transaction type
- `days_ahead` (optional): Days to predict ahead (default: 7)

**Response:**
```json
{
  "transaction_type": "850",
  "predicted_processing_time": 2.5,
  "confidence_interval": 0.3,
  "volume_prediction": {
    "predicted_volume": 150,
    "trend": 0.05,
    "confidence": "medium"
  }
}
```

### Get System Status

**GET** `/api/v1/status`

Get system status and health.

**Response:**
```json
{
  "service": "EDI Processor",
  "status": "operational",
  "metrics": {
    "total_processed": 1000,
    "success_rate": 0.95,
    "error_rate": 0.05
  },
  "insights": [
    "Consider optimizing 850 processing"
  ]
}
```

### Compliance Reports

**GET** `/api/v1/compliance/access-report`

Get access report for compliance.

**Query Parameters:**
- `start_date` (optional): Start date (default: 2025-01-01)
- `end_date` (optional): End date (default: 2025-12-31)

**GET** `/api/v1/compliance/data-access-report`

Get data access report for compliance.

**Query Parameters:**
- `start_date` (optional): Start date (default: 2025-01-01)
- `end_date` (optional): End date (default: 2025-12-31)

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "error": "Error message description"
}
```

## Running the API Server

### Standalone

```bash
python -m src.api_server
```

### Docker

```bash
docker-compose up
```

The API will be available at `http://localhost:5000`

## Example Usage

### Using curl

```bash
# Health check
curl http://localhost:5000/health

# Process file
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"filepath": "tests/sample_data/sample_850.x12"}'

# Get metrics
curl http://localhost:5000/api/v1/metrics?start_date=2025-01-01&end_date=2025-12-31
```

### Using Python

```python
import requests

# Process file
response = requests.post('http://localhost:5000/api/v1/process', 
                        json={'filepath': 'tests/sample_data/sample_850.x12'})
result = response.json()

# Get metrics
response = requests.get('http://localhost:5000/api/v1/metrics')
metrics = response.json()
```

