# IBM Sterling EDI Application - API Reference

## Command Line Interface

### Main Entry Point

```bash
python main.py <command> [options]
```

### Commands

#### `process`

Process EDI files.

**Options**:
- `-f, --file <path>`: Process a single file
- `-d, --directory <path>`: Process all files in a directory
- `--no-validate`: Skip validation
- `--no-deliver`: Skip delivery to Sterling

**Examples**:
```bash
# Process single file
python main.py process --file data/sample.x12

# Process directory
python main.py process --directory /sterling/pickup

# Process without validation
python main.py process --file data/sample.x12 --no-validate
```

#### `monitor`

Monitor directories for new files and process automatically.

**Example**:
```bash
python main.py monitor
```

#### `validate`

Validate an EDI file without processing.

**Options**:
- `-f, --file <path>`: File to validate (required)

**Example**:
```bash
python main.py validate --file data/sample.x12
```

## Python API

### EDIProcessor

Main processing class.

```python
from src.edi_processor import EDIProcessor

# Initialize with configuration
processor = EDIProcessor(config)

# Process a single file
result = processor.process_file("path/to/file.x12")

# Process directory
results = processor.process_directory("path/to/directory")

# Batch process
results = processor.batch_process(["file1.x12", "file2.x12"])
```

#### Methods

##### `process_file(filepath, validate=True, transform=False, deliver=True)`

Process a single EDI file.

**Parameters**:
- `filepath` (str): Path to EDI file
- `validate` (bool): Enable validation
- `transform` (bool): Enable transformation
- `deliver` (bool): Enable delivery to Sterling

**Returns**: `Dict[str, Any]` with processing results

##### `process_directory(directory, **kwargs)`

Process all EDI files in a directory.

**Parameters**:
- `directory` (str): Directory path
- `**kwargs`: Additional arguments for `process_file`

**Returns**: `List[Dict[str, Any]]` with processing results

##### `detect_edi_type(content)`

Detect EDI type from content.

**Parameters**:
- `content` (str): EDI file content

**Returns**: `str` ("X12" or "EDIFACT")

### X12Parser

X12 EDI parser.

```python
from src.x12_parser import X12Parser

parser = X12Parser()
envelope = parser.parse_file("file.x12")
transaction = envelope.transactions[0]
data = parser.extract_transaction_data(transaction)
```

#### Methods

##### `parse(content)`

Parse X12 content.

**Parameters**:
- `content` (str): X12 EDI content

**Returns**: `X12Envelope`

##### `parse_file(filepath)`

Parse X12 file.

**Parameters**:
- `filepath` (str): File path

**Returns**: `X12Envelope`

##### `extract_transaction_data(transaction)`

Extract structured data from transaction.

**Parameters**:
- `transaction` (X12Transaction): Transaction object

**Returns**: `Dict[str, Any]`

### EdifactParser

EDIFACT EDI parser.

```python
from src.edifact_parser import EdifactParser

parser = EdifactParser()
envelope = parser.parse_file("file.edifact")
message = envelope.messages[0]
data = parser.extract_message_data(message)
```

#### Methods

##### `parse(content)`

Parse EDIFACT content.

**Parameters**:
- `content` (str): EDIFACT EDI content

**Returns**: `EdifactEnvelope`

##### `parse_file(filepath)`

Parse EDIFACT file.

**Parameters**:
- `filepath` (str): File path

**Returns**: `EdifactEnvelope`

##### `extract_message_data(message)`

Extract structured data from message.

**Parameters**:
- `message` (EdifactMessage): Message object

**Returns**: `Dict[str, Any]`

### EDIValidator

EDI validation engine.

```python
from src.edi_validator import EDIValidator

validator = EDIValidator()
result = validator.validate(content, edi_type="X12")
summary = result.get_summary()
```

#### Methods

##### `validate(content, edi_type=None)`

Validate EDI content.

**Parameters**:
- `content` (str): EDI content
- `edi_type` (str, optional): EDI type ("X12" or "EDIFACT")

**Returns**: `ValidationResult`

### EDITransformer

EDI transformation engine.

```python
from src.edi_transformer import EDITransformer

transformer = EDITransformer()
edifact_content = transformer.transform_x12_to_edifact(x12_content)
x12_content = transformer.transform_edifact_to_x12(edifact_content)
```

#### Methods

##### `transform_x12_to_edifact(x12_content, message_type="ORDERS")`

Transform X12 to EDIFACT.

**Parameters**:
- `x12_content` (str): X12 EDI content
- `message_type` (str): Target EDIFACT message type

**Returns**: `str` (EDIFACT content)

##### `transform_edifact_to_x12(edifact_content, transaction_type="850")`

Transform EDIFACT to X12.

**Parameters**:
- `edifact_content` (str): EDIFACT EDI content
- `transaction_type` (str): Target X12 transaction type

**Returns**: `str` (X12 content)

##### `apply_mapping(data, mapping_config)`

Apply data mapping transformation.

**Parameters**:
- `data` (Dict): Source data
- `mapping_config` (Dict): Mapping configuration

**Returns**: `Dict` (transformed data)

### SterlingIntegration

IBM Sterling B2B Integrator integration.

```python
from src.sterling_integration import SterlingIntegration

sterling = SterlingIntegration(
    pickup_directories=["/sterling/pickup"],
    delivery_directories=["/sterling/delivery"],
    api_base_url="https://sterling-server:9080",
    api_username="user",
    api_password="pass"
)
```

#### Methods

##### `read_from_pickup(trading_partner=None)`

Read files from pickup directories.

**Parameters**:
- `trading_partner` (str, optional): Filter by trading partner

**Returns**: `List[str]` (file paths)

##### `write_to_delivery(filepath, trading_partner=None, file_type="EDI")`

Write file to delivery directory.

**Parameters**:
- `filepath` (str): Source file path
- `trading_partner` (str, optional): Trading partner name
- `file_type` (str): File type identifier

**Returns**: `bool` (success)

##### `submit_file_via_api(filepath, trading_partner, document_type="EDI")`

Submit file via API.

**Parameters**:
- `filepath` (str): File path
- `trading_partner` (str): Trading partner ID
- `document_type` (str): Document type

**Returns**: `Dict[str, Any]` (API response)

##### `get_processing_status(document_id)`

Get processing status from API.

**Parameters**:
- `document_id` (str): Document ID

**Returns**: `Dict[str, Any]` (status information)

### FileMonitor

File system monitoring.

```python
from src.file_monitor import FileMonitor

def process_file(filepath):
    print(f"Processing: {filepath}")

monitor = FileMonitor(
    watch_directories=["/sterling/pickup"],
    callback=process_file
)
monitor.start()
```

#### Methods

##### `start()`

Start monitoring directories.

##### `stop()`

Stop monitoring directories.

##### `is_alive()`

Check if monitor is running.

**Returns**: `bool`

## Data Structures

### X12Envelope

X12 interchange envelope.

**Attributes**:
- `isa_segment`: ISA segment
- `iea_segment`: IEA segment
- `functional_groups`: List of functional groups
- `transactions`: List of transactions

**Methods**:
- `get_sender_id()`: Get sender ID
- `get_receiver_id()`: Get receiver ID

### X12Transaction

X12 transaction set.

**Attributes**:
- `transaction_type`: Transaction type code
- `control_number`: Control number
- `segments`: List of segments

**Methods**:
- `get_segments(name)`: Get segments by name
- `get_segment(name, index=0)`: Get first segment by name

### ValidationResult

Validation result.

**Attributes**:
- `is_valid`: Validation status
- `errors`: List of errors
- `warnings`: List of warnings

**Methods**:
- `get_summary()`: Get validation summary

## Configuration

### Configuration Dictionary Structure

```python
config = {
    "app": {
        "log_level": "INFO"
    },
    "processing": {
        "validate": True,
        "deliver": True
    },
    "sterling": {
        "pickup_directories": ["/sterling/pickup"],
        "delivery_directories": ["/sterling/delivery"],
        "api_base_url": "https://sterling-server:9080",
        "api_username": "user",
        "api_password": "pass"
    }
}
```

## Error Handling

All methods may raise exceptions. Common exceptions:

- `ValueError`: Invalid input or configuration
- `FileNotFoundError`: File not found
- `PermissionError`: File permission issues
- `requests.RequestException`: API call failures

Always wrap API calls in try/except blocks for production code.

