# Package Contents

This document lists all files included in the IBM Sterling EDI Application package.

## Root Files

- `README.md` - Main documentation and quick start guide
- `requirements.txt` - Python dependencies
- `main.py` - Application entry point
- `create_package.ps1` - Windows script to create ZIP package
- `create_package.sh` - Linux/Unix script to create ZIP package
- `PACKAGE_CONTENTS.md` - This file

## Configuration Files (`config/`)

- `config.yaml` - Main application configuration
- `sterling_config.yaml` - IBM Sterling B2B Integrator configuration

## Source Code (`src/`)

### Core Modules
- `edi_processor.py` - Main EDI processing orchestrator
- `x12_parser.py` - X12 EDI parser
- `edifact_parser.py` - EDIFACT EDI parser
- `edi_validator.py` - EDI validation engine
- `edi_transformer.py` - EDI transformation engine
- `file_monitor.py` - File system monitoring
- `sterling_integration.py` - IBM Sterling integration
- `metrics_collector.py` - Metrics tracking for dashboard
- `powerbi_dashboard.py` - Power BI dashboard generator
- `generate_sample_metrics.py` - Sample metrics data generator

### Utilities (`src/utils/`)
- `logger.py` - Logging utilities
- `file_utils.py` - File operation utilities

## Tests (`tests/`)

- `test_x12_parser.py` - X12 parser unit tests
- `test_edifact_parser.py` - EDIFACT parser unit tests
- `test_validator.py` - Validator unit tests

### Sample Data (`tests/sample_data/`)
- `sample_850.x12` - Sample X12 Purchase Order
- `sample_855.x12` - Sample X12 PO Acknowledgment
- `sample_810.x12` - Sample X12 Invoice
- `sample_855.edifact` - Sample EDIFACT ORDERS message

## Scripts (`scripts/`)

- `deploy.ps1` - Windows deployment script
- `deploy.sh` - Linux/Unix deployment script
- `setup_sterling_dirs.sh` - Sterling directory setup script

## Documentation (`docs/`)

- `DEPLOYMENT.md` - Comprehensive deployment guide
- `ARCHITECTURE.md` - System architecture documentation
- `API_REFERENCE.md` - API and usage reference
- `DASHBOARD.md` - Power BI dashboard guide

## Package Creation

To create a deployment ZIP package:

**Windows:**
```powershell
.\create_package.ps1
```

**Linux/Unix:**
```bash
chmod +x create_package.sh
./create_package.sh
```

This will create `sterling_edi_app.zip` containing all necessary files for deployment.

## File Count Summary

- Python source files: 13
- Configuration files: 2
- Test files: 3
- Sample data files: 4
- Documentation files: 4
- Deployment scripts: 3
- Total: ~29 files

## Size Estimate

Approximate package size: 200-300 KB (uncompressed), 50-100 KB (compressed ZIP)

