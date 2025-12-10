# IBM Sterling EDI Application - Architecture

## Overview

The IBM Sterling EDI Application is designed as a modular, extensible system for processing EDI files in IBM Sterling B2B Integrator environments. The architecture follows a pipeline pattern where files flow through distinct processing stages.

## System Architecture

```mermaid
graph TB
    subgraph input["Input Layer"]
        FileMonitor["File Monitor<br/>Monitors Sterling directories"]
        APIServer["REST API Server<br/>HTTP endpoints"]
    end
    
    subgraph core["Core Processing"]
        EDIProcessor["EDI Processor<br/>Main Orchestrator"]
        
        subgraph parsers["Parsers"]
            X12Parser["X12 Parser<br/>ANSI X12 format"]
            EdifactParser["EDIFACT Parser<br/>UN/EDIFACT format"]
        end
        
        EDIValidator["EDI Validator<br/>Syntax & Business Rules"]
        EDITransformer["EDI Transformer<br/>Format Conversion"]
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
        PowerBI["Power BI Generator<br/>Dashboard Creation"]
    end
    
    FileMonitor --> EDIProcessor
    APIServer --> EDIProcessor
    EDIProcessor --> X12Parser
    EDIProcessor --> EdifactParser
    X12Parser --> EDIValidator
    EdifactParser --> EDIValidator
    EDIValidator --> EDITransformer
    EDITransformer --> SterlingIntegration
    EDITransformer --> AcumaticaConnector
    EDITransformer --> ECommerceConnector
    EDIProcessor --> MetricsCollector
    EDIProcessor --> SecurityAudit
    MetricsCollector --> SQLServerIntegration
    MetricsCollector --> PowerBI
    EDIProcessor --> Monitoring
```

## Component Details

### 1. File Monitor

**Purpose**: Monitors directories for new EDI files

**Implementation**:
- Uses `watchdog` library for efficient file system monitoring
- Falls back to polling if `watchdog` is unavailable
- Handles file locking and stability checks

**Key Features**:
- Multiple directory monitoring
- Recursive directory scanning
- File extension filtering
- File stability detection

### 2. EDI Processor

**Purpose**: Main orchestrator for the processing pipeline

**Responsibilities**:
- File type detection (X12 vs EDIFACT)
- Routing to appropriate parser
- Coordinating validation and transformation
- Managing delivery to Sterling
- Error handling and file movement

### 3. X12 Parser

**Purpose**: Parse X12 EDI files

**Capabilities**:
- Automatic separator detection
- Envelope parsing (ISA/IEA, GS/GE, ST/SE)
- Transaction extraction
- Data extraction for common transaction types (850, 855, 810, 856)

**Data Structures**:
- `X12Envelope`: Interchange-level structure
- `X12Transaction`: Transaction set structure
- `X12Segment`: Individual segment structure

### 4. EDIFACT Parser

**Purpose**: Parse EDIFACT EDI files

**Capabilities**:
- UNA segment detection (service string advice)
- Envelope parsing (UNB/UNZ, UNH/UNT)
- Message extraction
- Data extraction for common message types (ORDERS, DESADV, INVOIC)

**Data Structures**:
- `EdifactEnvelope`: Interchange-level structure
- `EdifactMessage`: Message structure
- `EdifactSegment`: Individual segment structure

### 5. EDI Validator

**Purpose**: Validate EDI files for syntax and business rules

**Validation Levels**:
- **Syntax Validation**: Segment structure, element counts, required fields
- **Business Rule Validation**: Transaction-specific rules, code values

**Output**:
- Detailed error reports
- Warning messages
- Validation summary

### 6. EDI Transformer

**Purpose**: Transform EDI data between formats and apply mappings

**Capabilities**:
- X12 ↔ EDIFACT conversion
- Data mapping and transformation
- Field enrichment
- Custom transformation rules

### 7. Sterling Integration

**Purpose**: Integrate with IBM Sterling B2B Integrator

**Integration Methods**:

#### File System Integration
- Reads from Sterling pickup directories
- Writes to Sterling delivery directories
- Handles file naming conventions
- Manages processed/error directories

#### API Integration
- REST API client for Sterling B2B Integrator
- Document submission
- Status queries
- Trading partner configuration retrieval

## Data Flow

### Processing Pipeline

```mermaid
flowchart TD
    Start([File Detected]) --> ReadFile["Read File Content"]
    ReadFile --> DetectType{"Detect EDI Type"}
    DetectType -->|X12| X12Parse["Parse X12 Format"]
    DetectType -->|EDIFACT| EdifactParse["Parse EDIFACT Format"]
    DetectType -->|Unknown| Error1["Error: Unknown Format"]
    
    X12Parse --> Validate{"Validation<br/>Enabled?"}
    EdifactParse --> Validate
    
    Validate -->|Yes| RunValidation["Run Validation Rules"]
    Validate -->|No| TransformCheck{"Transformation<br/>Enabled?"}
    RunValidation --> ValidationResult{"Validation<br/>Passed?"}
    
    ValidationResult -->|No| ValidationErrors["Log Validation Errors"]
    ValidationErrors --> MoveToError["Move to Error Directory"]
    MoveToError --> End([End])
    
    ValidationResult -->|Yes| TransformCheck
    TransformCheck -->|Yes| Transform["Transform Data"]
    TransformCheck -->|No| AIValidateCheck{"AI Validation<br/>Enabled?"}
    Transform --> AIValidateCheck
    
    AIValidateCheck -->|Yes| AIValidate["AI Validation"]
    AIValidateCheck -->|No| DeliverCheck{"Delivery<br/>Enabled?"}
    AIValidate --> DeliverCheck
    
    DeliverCheck -->|Yes| Deliver["Deliver to Sterling"]
    DeliverCheck -->|No| SyncCheck{"Sync to<br/>Systems?"}
    Deliver --> SyncCheck
    
    SyncCheck -->|Acumatica| SyncAcumatica["Sync to Acumatica"]
    SyncCheck -->|eCommerce| SyncECommerce["Sync to eCommerce"]
    SyncCheck -->|SQL Server| SyncSQL["Store in SQL Server"]
    SyncCheck -->|None| CollectMetrics
    
    SyncAcumatica --> CollectMetrics["Collect Metrics"]
    SyncECommerce --> CollectMetrics
    SyncSQL --> CollectMetrics
    
    CollectMetrics --> MoveProcessed["Move to Processed Directory"]
    MoveProcessed --> End
    
    Error1 --> MoveToError
```

### Error Handling Flow

```mermaid
flowchart TD
    Error([Error Occurred]) --> ErrorType{"Error Type?"}
    
    ErrorType -->|Validation Error| LogValidation["Log Validation Error"]
    ErrorType -->|Processing Error| LogProcessing["Log Processing Error"]
    ErrorType -->|Integration Error| LogIntegration["Log Integration Error"]
    ErrorType -->|System Error| LogSystem["Log System Error"]
    
    LogValidation --> RetryCheck{"Retry<br/>Enabled?"}
    LogProcessing --> RetryCheck
    LogIntegration --> RetryCheck
    LogSystem --> RetryCheck
    
    RetryCheck -->|Yes| RetryCount{"Retry Count<br/>< Max?"}
    RetryCheck -->|No| MoveError["Move to Error Directory"]
    
    RetryCount -->|Yes| Wait["Wait & Retry"]
    RetryCount -->|No| MoveError
    
    Wait --> ProcessAgain["Retry Processing"]
    ProcessAgain --> Error
    
    MoveError --> Notify["Notify Administrators"]
    Notify --> UpdateMetrics["Update Error Metrics"]
    UpdateMetrics --> End([End])
```

### Integration Data Flow

```mermaid
flowchart LR
    subgraph ediApp["EDI Application"]
        ProcessedData["Processed EDI Data"]
    end
    
    subgraph sterling["IBM Sterling"]
        SterlingFS["File System<br/>Pickup/Delivery"]
        SterlingAPI["REST API<br/>Document Submission"]
    end
    
    subgraph acumatica["Acumatica ERP/CRM"]
        SalesOrders["Sales Orders"]
        Inventory["Inventory"]
        Customers["Customers"]
        Opportunities["Opportunities"]
    end
    
    subgraph ecommerce["eCommerce Platforms"]
        Shopify["Shopify"]
        Magento["Magento"]
        WooCommerce["WooCommerce"]
    end
    
    subgraph data["Data Storage"]
        SQLServer["SQL Server<br/>Data Warehouse"]
        MetricsDB["Metrics Database"]
    end
    
    subgraph reporting["Reporting"]
        PowerBI["Power BI<br/>Dashboards"]
    end
    
    ProcessedData --> SterlingFS
    ProcessedData --> SterlingAPI
    ProcessedData --> SalesOrders
    ProcessedData --> Inventory
    ProcessedData --> Customers
    ProcessedData --> Opportunities
    ProcessedData --> Shopify
    ProcessedData --> Magento
    ProcessedData --> WooCommerce
    ProcessedData --> SQLServer
    ProcessedData --> MetricsDB
    MetricsDB --> PowerBI
    SQLServer --> PowerBI
```

## Configuration Management

### Configuration Files

1. **config.yaml**: Application-level settings
   - Processing options
   - Monitoring settings
   - Validation rules
   - Performance tuning

2. **sterling_config.yaml**: Sterling-specific settings
   - Directory paths
   - API configuration
   - Trading partner settings
   - File naming conventions

### Configuration Loading

- YAML-based configuration
- Environment variable support (for sensitive data)
- Configuration merging (base + Sterling)
- Runtime configuration updates

## Logging

### Log Structure

- **Location**: `logs/` directory
- **Format**: Rotating log files with date stamps
- **Rotation**: 10MB per file, 5 backups
- **Levels**: DEBUG, INFO, WARNING, ERROR

### Log Categories

- File operations
- Processing results
- Validation errors
- API calls
- System events

## Extensibility

### Adding New Transaction Types

1. Extend parser with new extraction method
2. Add validation rules
3. Update transformer mappings
4. Add sample data

### Adding New Validations

1. Create validation method in `EDIValidator`
2. Add to validation pipeline
3. Configure in validation rules

### Custom Transformations

1. Define mapping configuration
2. Implement transformation logic
3. Configure in transformation settings

## Performance Considerations

### Optimization Strategies

- **Parallel Processing**: Multiple files processed concurrently
- **Batch Processing**: Group files for efficient processing
- **Caching**: Cache parsed structures for repeated access
- **Lazy Loading**: Load data only when needed

### Scalability

- Stateless processing (can run multiple instances)
- File-based integration (no shared state)
- Horizontal scaling support
- Resource-efficient design

## Security

### Security Features

- Secure credential storage (environment variables)
- File permission management
- API authentication
- Log sanitization (no sensitive data)

### Best Practices

- Run with minimal required permissions
- Use service accounts
- Encrypt sensitive configuration
- Regular security updates

## Testing

### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end processing
- **Sample Data**: Realistic EDI files for testing

### Test Coverage

- Parser functionality
- Validation rules
- Transformation logic
- Error handling

## Deployment Architecture

```mermaid
graph TB
    subgraph deployment["Deployment Options"]
        Standalone["Standalone<br/>Python Script"]
        Service["System Service<br/>Windows/Linux"]
        Docker["Docker Container<br/>Containerized"]
        Cloud["Cloud Platform<br/>Azure/AWS/GCP"]
    end
    
    subgraph dockerArch["Docker Architecture"]
        DockerCompose["Docker Compose<br/>Orchestration"]
        AppContainer["Application Container<br/>EDI Processor"]
        APIContainer["API Container<br/>REST API Server"]
        DBContainer["Database Container<br/>SQLite/PostgreSQL"]
    end
    
    subgraph monitoring["Monitoring & Logging"]
        LogFiles["Log Files<br/>Rotating Logs"]
        HealthChecks["Health Checks<br/>API Endpoints"]
        Metrics["Metrics Collection<br/>Performance Data"]
        Alerts["Alerting System<br/>Threshold Monitoring"]
    end
    
    subgraph external["External Systems"]
        Sterling["IBM Sterling<br/>B2B Integrator"]
        Acumatica["Acumatica<br/>ERP/CRM"]
        ECommerce["eCommerce<br/>Platforms"]
        SQLServer["SQL Server<br/>Data Warehouse"]
    end
    
    Docker --> DockerCompose
    DockerCompose --> AppContainer
    DockerCompose --> APIContainer
    DockerCompose --> DBContainer
    
    AppContainer --> LogFiles
    APIContainer --> HealthChecks
    AppContainer --> Metrics
    Metrics --> Alerts
    
    AppContainer --> Sterling
    AppContainer --> Acumatica
    AppContainer --> ECommerce
    AppContainer --> SQLServer
```

### Deployment Options

1. **Standalone**: Run as Python script
2. **Service**: Install as system service
3. **Container**: Docker container deployment
4. **Cloud**: Cloud platform deployment

### Monitoring

- Log file monitoring
- Process status checks
- File processing metrics
- Error rate tracking

