# Visual Guide
## Comprehensive Architecture and Data Flow Diagrams

This document provides a comprehensive visual overview of the IBM Sterling EDI Application architecture, data flows, and integration patterns.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Processing Pipeline](#processing-pipeline)
3. [Integration Architecture](#integration-architecture)
4. [Deployment Architecture](#deployment-architecture)
5. [API Architecture](#api-architecture)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [Component Relationships](#component-relationships)

---

## System Architecture

### Complete System Overview

```mermaid
graph TB
    subgraph input["Input Layer"]
        FileMonitor["File Monitor<br/>Directory Watching"]
        APIServer["REST API Server<br/>HTTP Endpoints"]
        CLI["Command Line Interface<br/>CLI Commands"]
    end
    
    subgraph core["Core Processing Engine"]
        EDIProcessor["EDI Processor<br/>Main Orchestrator"]
        
        subgraph parsers["Parsers"]
            X12Parser["X12 Parser<br/>ANSI X12 Format"]
            EdifactParser["EDIFACT Parser<br/>UN/EDIFACT Format"]
        end
        
        EDIValidator["EDI Validator<br/>Syntax & Business Rules"]
        EDITransformer["EDI Transformer<br/>Format Conversion"]
        AIValidator["AI Validator<br/>Intelligent Validation"]
        ErrorHandler["Automated Error Handler<br/>Error Recovery"]
    end
    
    subgraph integrations["Integration Layer"]
        SterlingIntegration["Sterling Integration<br/>File System & API"]
        AcumaticaConnector["Acumatica Connector<br/>ERP/CRM"]
        ECommerceConnector["eCommerce Connector<br/>Shopify/Magento/WooCommerce"]
        SQLServerIntegration["SQL Server Integration<br/>Data Warehouse"]
    end
    
    subgraph support["Support Services"]
        MetricsCollector["Metrics Collector<br/>Performance Tracking"]
        SecurityAudit["Security Audit<br/>Access Logging"]
        Monitoring["System Monitoring<br/>Health Checks"]
        PredictiveAnalytics["Predictive Analytics<br/>Forecasting"]
    end
    
    subgraph output["Output Layer"]
        PowerBI["Power BI Generator<br/>Dashboard Creation"]
        Logs["Log Files<br/>Rotating Logs"]
        Reports["Compliance Reports<br/>GDPR/HIPAA/SOX"]
    end
    
    FileMonitor --> EDIProcessor
    APIServer --> EDIProcessor
    CLI --> EDIProcessor
    
    EDIProcessor --> X12Parser
    EDIProcessor --> EdifactParser
    X12Parser --> EDIValidator
    EdifactParser --> EDIValidator
    EDIValidator --> AIValidator
    AIValidator --> ErrorHandler
    ErrorHandler --> EDITransformer
    
    EDITransformer --> SterlingIntegration
    EDITransformer --> AcumaticaConnector
    EDITransformer --> ECommerceConnector
    EDITransformer --> SQLServerIntegration
    
    EDIProcessor --> MetricsCollector
    EDIProcessor --> SecurityAudit
    EDIProcessor --> Monitoring
    MetricsCollector --> PredictiveAnalytics
    
    MetricsCollector --> SQLServerIntegration
    MetricsCollector --> PowerBI
    SecurityAudit --> Reports
    SQLServerIntegration --> PowerBI
```

---

## Processing Pipeline

### EDI Processing Flow

```mermaid
flowchart TD
    Start([File Detected]) --> ReadFile["Read File Content<br/>from Disk"]
    ReadFile --> DetectType{"Detect EDI Type"}
    
    DetectType -->|X12| X12Parse["Parse X12 Format<br/>ISA/GS/ST Segments"]
    DetectType -->|EDIFACT| EdifactParse["Parse EDIFACT Format<br/>UNB/UNH Segments"]
    DetectType -->|Unknown| ErrorUnknown["Error: Unknown Format"]
    
    X12Parse --> Validate{"Validation<br/>Enabled?"}
    EdifactParse --> Validate
    
    Validate -->|Yes| RunValidation["Run Validation Rules<br/>Syntax & Business Rules"]
    Validate -->|No| TransformCheck{"Transformation<br/>Enabled?"}
    
    RunValidation --> ValidationResult{"Validation<br/>Passed?"}
    
    ValidationResult -->|No| ValidationErrors["Log Validation Errors<br/>Detailed Error Report"]
    ValidationErrors --> MoveToError["Move to Error Directory"]
    MoveToError --> End([End])
    
    ValidationResult -->|Yes| AIValidate{"AI Validation<br/>Enabled?"}
    AIValidate -->|Yes| RunAIValidation["AI Validation<br/>Intelligent Checks"]
    AIValidate -->|No| TransformCheck
    
    RunAIValidation --> AIResult{"AI Validation<br/>Passed?"}
    AIResult -->|No| AIErrors["Log AI Validation Errors"]
    AIErrors --> MoveToError
    AIResult -->|Yes| TransformCheck
    
    TransformCheck -->|Yes| Transform["Transform Data<br/>Format Conversion"]
    TransformCheck -->|No| DeliverCheck{"Delivery<br/>Enabled?"}
    Transform --> DeliverCheck
    
    DeliverCheck -->|Yes| Deliver["Deliver to Sterling<br/>File System or API"]
    DeliverCheck -->|No| SyncCheck{"Sync to<br/>Systems?"}
    Deliver --> SyncCheck
    
    SyncCheck -->|Acumatica| SyncAcumatica["Sync to Acumatica<br/>Orders/Inventory/CRM"]
    SyncCheck -->|eCommerce| SyncECommerce["Sync to eCommerce<br/>Shopify/Magento/WooCommerce"]
    SyncCheck -->|SQL Server| SyncSQL["Store in SQL Server<br/>Data Warehouse"]
    SyncCheck -->|None| CollectMetrics
    
    SyncAcumatica --> CollectMetrics["Collect Metrics<br/>Performance Data"]
    SyncECommerce --> CollectMetrics
    SyncSQL --> CollectMetrics
    
    CollectMetrics --> UpdateDashboard["Update Power BI<br/>Dashboard Data"]
    CollectMetrics --> LogEvent["Log Security Event<br/>Audit Trail"]
    
    UpdateDashboard --> MoveProcessed["Move to Processed Directory"]
    LogEvent --> MoveProcessed
    MoveProcessed --> End
    
    ErrorUnknown --> MoveToError
```

### Error Handling Flow

```mermaid
flowchart TD
    Error([Error Occurred]) --> ErrorType{"Error Type?"}
    
    ErrorType -->|Validation Error| LogValidation["Log Validation Error<br/>Detailed Error Report"]
    ErrorType -->|Processing Error| LogProcessing["Log Processing Error<br/>Stack Trace"]
    ErrorType -->|Integration Error| LogIntegration["Log Integration Error<br/>API/Connection Error"]
    ErrorType -->|System Error| LogSystem["Log System Error<br/>Critical Failure"]
    
    LogValidation --> RetryCheck{"Retry<br/>Enabled?"}
    LogProcessing --> RetryCheck
    LogIntegration --> RetryCheck
    LogSystem --> RetryCheck
    
    RetryCheck -->|Yes| RetryCount{"Retry Count<br/>< Max Retries?"}
    RetryCheck -->|No| MoveError["Move to Error Directory<br/>Archive Failed File"]
    
    RetryCount -->|Yes| Wait["Wait & Retry<br/>Exponential Backoff"]
    RetryCount -->|No| MoveError
    
    Wait --> ProcessAgain["Retry Processing<br/>Full Pipeline"]
    ProcessAgain --> Error
    
    MoveError --> Notify["Notify Administrators<br/>Email/Alert"]
    Notify --> UpdateMetrics["Update Error Metrics<br/>Failure Rate"]
    UpdateMetrics --> GenerateReport["Generate Error Report<br/>For Analysis"]
    GenerateReport --> End([End])
```

---

## Integration Architecture

### Complete Integration Ecosystem

```mermaid
graph TB
    subgraph center["EDI Application<br/>Central Hub"]
        EDIProcessor["EDI Processor"]
        MetricsCollector["Metrics Collector"]
        SecurityAudit["Security Audit"]
    end
    
    subgraph sterling["IBM Sterling B2B Integrator"]
        SterlingFS["File System<br/>Pickup/Delivery Directories"]
        SterlingAPI["REST API<br/>Document Submission"]
        SterlingConfig["Trading Partner<br/>Configuration"]
    end
    
    subgraph acumatica["Acumatica ERP/CRM"]
        SalesOrders["Sales Orders<br/>SO301000"]
        PurchaseOrders["Purchase Orders<br/>PO301000"]
        Inventory["Inventory<br/>IN202500"]
        Customers["Customers<br/>AR303000"]
        Vendors["Vendors<br/>AP303000"]
        Opportunities["Opportunities<br/>CR304000"]
        Contacts["Contacts<br/>CR302000"]
        Activities["Activities<br/>CR306000"]
    end
    
    subgraph ecommerce["eCommerce Platforms"]
        Shopify["Shopify<br/>Orders/Products"]
        Magento["Magento<br/>Orders/Inventory"]
        WooCommerce["WooCommerce<br/>Orders/Products"]
    end
    
    subgraph data["Data Storage"]
        SQLServer["SQL Server<br/>Data Warehouse"]
        MetricsDB["Metrics Database<br/>SQLite"]
        FileSystem["File System<br/>Processed Files"]
    end
    
    subgraph reporting["Reporting & Analytics"]
        PowerBI["Power BI<br/>Executive Dashboards"]
        ComplianceReports["Compliance Reports<br/>GDPR/HIPAA/SOX"]
        ExecutiveReports["Executive Reports<br/>Monthly/Quarterly"]
    end
    
    EDIProcessor --> SterlingFS
    EDIProcessor --> SterlingAPI
    EDIProcessor --> SterlingConfig
    
    EDIProcessor --> SalesOrders
    EDIProcessor --> PurchaseOrders
    EDIProcessor --> Inventory
    EDIProcessor --> Customers
    EDIProcessor --> Vendors
    EDIProcessor --> Opportunities
    EDIProcessor --> Contacts
    EDIProcessor --> Activities
    
    EDIProcessor --> Shopify
    EDIProcessor --> Magento
    EDIProcessor --> WooCommerce
    
    EDIProcessor --> SQLServer
    MetricsCollector --> MetricsDB
    EDIProcessor --> FileSystem
    
    MetricsDB --> PowerBI
    SQLServer --> PowerBI
    SecurityAudit --> ComplianceReports
    MetricsCollector --> ExecutiveReports
```

### Integration Data Flow

```mermaid
sequenceDiagram
    participant TP as Trading Partner
    participant Sterling as IBM Sterling
    participant EDI as EDI Application
    participant Acumatica as Acumatica ERP/CRM
    participant ECommerce as eCommerce Platform
    participant SQL as SQL Server
    participant PowerBI as Power BI
    
    TP->>Sterling: Send EDI File (X12/EDIFACT)
    Sterling->>EDI: File Detected (Pickup Directory)
    EDI->>EDI: Parse & Validate
    EDI->>EDI: Transform if Needed
    EDI->>Sterling: Deliver Processed File
    EDI->>Acumatica: Sync Order/Inventory Data
    EDI->>ECommerce: Sync Order/Product Data
    EDI->>SQL: Store Metrics & Data
    EDI->>EDI: Collect Metrics
    SQL->>PowerBI: Update Dashboard Data
    Acumatica->>PowerBI: Update ERP Metrics
    ECommerce->>PowerBI: Update eCommerce Metrics
```

---

## Deployment Architecture

### Docker Deployment Architecture

```mermaid
graph TB
    subgraph docker["Docker Environment"]
        DockerCompose["Docker Compose<br/>Orchestration"]
        
        subgraph containers["Containers"]
            AppContainer["Application Container<br/>EDI Processor<br/>Python 3.8+"]
            APIContainer["API Container<br/>REST API Server<br/>Flask"]
            DBContainer["Database Container<br/>SQLite/PostgreSQL<br/>Optional"]
        end
        
        subgraph volumes["Volumes"]
            ConfigVolume["Config Volume<br/>YAML Files"]
            DataVolume["Data Volume<br/>Processed Files"]
            LogVolume["Log Volume<br/>Application Logs"]
        end
    end
    
    subgraph external["External Systems"]
        Sterling["IBM Sterling<br/>B2B Integrator"]
        Acumatica["Acumatica<br/>ERP/CRM"]
        ECommerce["eCommerce<br/>Platforms"]
        SQLServer["SQL Server<br/>Data Warehouse"]
    end
    
    subgraph monitoring["Monitoring"]
        HealthChecks["Health Checks<br/>/health endpoint"]
        Metrics["Metrics Collection<br/>Performance Data"]
        Alerts["Alerting<br/>Threshold Monitoring"]
    end
    
    DockerCompose --> AppContainer
    DockerCompose --> APIContainer
    DockerCompose --> DBContainer
    
    AppContainer --> ConfigVolume
    AppContainer --> DataVolume
    AppContainer --> LogVolume
    APIContainer --> ConfigVolume
    
    AppContainer --> Sterling
    AppContainer --> Acumatica
    AppContainer --> ECommerce
    AppContainer --> SQLServer
    
    APIContainer --> HealthChecks
    AppContainer --> Metrics
    Metrics --> Alerts
```

### Network Topology

```mermaid
graph LR
    subgraph internal["Internal Network"]
        DockerHost["Docker Host<br/>192.168.1.x"]
        AppContainer["App Container<br/>Port 5000"]
        APIContainer["API Container<br/>Port 5000"]
    end
    
    subgraph dmz["DMZ"]
        LoadBalancer["Load Balancer<br/>Optional"]
    end
    
    subgraph external["External Systems"]
        Sterling["IBM Sterling<br/>B2B Integrator"]
        Acumatica["Acumatica Cloud<br/>ERP/CRM"]
        ECommerce["eCommerce APIs<br/>Shopify/Magento"]
        SQLServer["SQL Server<br/>Database Server"]
    end
    
    subgraph clients["Clients"]
        WebClient["Web Client<br/>Browser"]
        APIClient["API Client<br/>REST Client"]
        Admin["Administrator<br/>CLI"]
    end
    
    WebClient --> LoadBalancer
    APIClient --> LoadBalancer
    Admin --> DockerHost
    
    LoadBalancer --> APIContainer
    DockerHost --> AppContainer
    
    AppContainer --> Sterling
    AppContainer --> Acumatica
    AppContainer --> ECommerce
    AppContainer --> SQLServer
```

---

## API Architecture

### REST API Request Flow

```mermaid
sequenceDiagram
    participant Client as API Client
    participant API as REST API Server
    participant Security as Security Audit
    participant Processor as EDI Processor
    participant Metrics as Metrics Collector
    participant DB as Database
    
    Client->>API: POST /api/v1/process
    API->>Security: Log Access Request
    Security->>DB: Store Audit Log
    API->>API: Validate Request
    API->>Processor: Process EDI File
    Processor->>Processor: Parse & Validate
    Processor->>Metrics: Record Processing Metrics
    Metrics->>DB: Store Metrics
    Processor-->>API: Return Result
    API->>Security: Log Access Success
    Security->>DB: Update Audit Log
    API-->>Client: Return JSON Response
```

### API Endpoint Architecture

```mermaid
graph TB
    subgraph api["REST API Server"]
        Router["Flask Router<br/>Request Routing"]
        
        subgraph endpoints["API Endpoints"]
            Health["/health<br/>Health Check"]
            Process["/api/v1/process<br/>Process EDI File"]
            Metrics["/api/v1/metrics<br/>Get Metrics"]
            Predictions["/api/v1/predictions<br/>Get Predictions"]
            Compliance["/api/v1/compliance<br/>Compliance Reports"]
        end
        
        subgraph middleware["Middleware"]
            CORS["CORS Handler<br/>Cross-Origin"]
            Auth["Authentication<br/>Future: API Keys"]
            Logging["Request Logging<br/>Access Logs"]
        end
    end
    
    subgraph services["Backend Services"]
        EDIProcessor["EDI Processor<br/>Core Engine"]
        MetricsCollector["Metrics Collector<br/>Data Collection"]
        PredictiveAnalytics["Predictive Analytics<br/>Forecasting"]
        ComplianceReporter["Compliance Reporter<br/>GDPR/HIPAA/SOX"]
    end
    
    Router --> Health
    Router --> Process
    Router --> Metrics
    Router --> Predictions
    Router --> Compliance
    
    Health --> CORS
    Process --> Auth
    Process --> Logging
    Metrics --> Auth
    Predictions --> Auth
    Compliance --> Auth
    
    Process --> EDIProcessor
    Metrics --> MetricsCollector
    Predictions --> PredictiveAnalytics
    Compliance --> ComplianceReporter
```

---

## Data Flow Diagrams

### Metrics Collection Flow

```mermaid
flowchart LR
    Processing["EDI Processing"] --> Collect["Collect Metrics"]
    Collect --> Store["Store in Database"]
    Store --> Aggregate["Aggregate Metrics"]
    Aggregate --> Export["Export to SQL Server"]
    Aggregate --> Dashboard["Update Power BI"]
    Dashboard --> Visualize["Visualize in Dashboard"]
    Export --> Warehouse["Data Warehouse"]
    Warehouse --> Analytics["Business Analytics"]
```

### Security Audit Flow

```mermaid
flowchart TD
    Event["Security Event"] --> Log["Log Event"]
    Log --> Classify{"Event Type?"}
    
    Classify -->|Access| AccessLog["Access Log<br/>User/Resource/Action"]
    Classify -->|Error| ErrorLog["Error Log<br/>Failed Attempt"]
    Classify -->|Compliance| ComplianceLog["Compliance Log<br/>GDPR/HIPAA/SOX"]
    
    AccessLog --> Store["Store in Audit Database"]
    ErrorLog --> Store
    ComplianceLog --> Store
    
    Store --> Analyze["Analyze Patterns"]
    Analyze --> Report["Generate Reports"]
    Report --> Alert{"Alert<br/>Required?"}
    
    Alert -->|Yes| Notify["Notify Security Team"]
    Alert -->|No| Archive["Archive Logs"]
    Notify --> Archive
```

---

## Component Relationships

### Module Dependencies

```mermaid
graph TD
    subgraph core["Core Modules"]
        EDIProcessor["edi_processor.py"]
        X12Parser["x12_parser.py"]
        EdifactParser["edifact_parser.py"]
        EDIValidator["edi_validator.py"]
        EDITransformer["edi_transformer.py"]
    end
    
    subgraph integration["Integration Modules"]
        SterlingIntegration["sterling_integration.py"]
        AcumaticaConnector["acumatica_connector.py"]
        AcumaticaCRM["acumatica_crm_integration.py"]
        ECommerceConnector["ecommerce_connector.py"]
        SQLServerIntegration["sql_server_integration.py"]
    end
    
    subgraph support["Support Modules"]
        MetricsCollector["metrics_collector.py"]
        SecurityAudit["security_audit.py"]
        Monitoring["monitoring.py"]
        PowerBI["powerbi_dashboard.py"]
        AIAutomation["ai_automation.py"]
    end
    
    subgraph utils["Utility Modules"]
        Logger["utils/logger.py"]
        FileUtils["utils/file_utils.py"]
        FileMonitor["file_monitor.py"]
    end
    
    EDIProcessor --> X12Parser
    EDIProcessor --> EdifactParser
    EDIProcessor --> EDIValidator
    EDIProcessor --> EDITransformer
    EDIProcessor --> SterlingIntegration
    EDIProcessor --> AcumaticaConnector
    EDIProcessor --> AcumaticaCRM
    EDIProcessor --> ECommerceConnector
    EDIProcessor --> SQLServerIntegration
    EDIProcessor --> MetricsCollector
    EDIProcessor --> SecurityAudit
    EDIProcessor --> AIAutomation
    
    MetricsCollector --> PowerBI
    MetricsCollector --> SQLServerIntegration
    SecurityAudit --> SQLServerIntegration
    
    EDIProcessor --> Logger
    EDIProcessor --> FileUtils
    FileMonitor --> EDIProcessor
    
    SterlingIntegration --> Logger
    AcumaticaConnector --> Logger
    ECommerceConnector --> Logger
```

---

## Summary

This visual guide provides comprehensive diagrams covering:

- **System Architecture**: Complete component overview
- **Processing Pipeline**: Step-by-step EDI processing flow
- **Integration Architecture**: All external system connections
- **Deployment Architecture**: Docker and network topology
- **API Architecture**: REST API structure and request flow
- **Data Flow Diagrams**: Metrics, security, and data movement
- **Component Relationships**: Module dependencies and structure

For detailed information about any component, refer to the specific documentation files in the `docs/` directory.

