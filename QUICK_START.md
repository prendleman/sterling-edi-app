# Quick Start Guide

Get up and running with the IBM Sterling EDI Application in minutes.

## Installation

1. **Extract the package:**
```bash
unzip sterling_edi_app.zip
cd sterling_edi_app
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure (optional):**
   - Edit `config/config.yaml` for general settings
   - Edit `config/sterling_config.yaml` for Sterling directories

## Quick Test

### Test with Sample Files

```bash
# Validate a sample file
python main.py validate --file tests/sample_data/sample_850.x12

# Process a sample file
python main.py process --file tests/sample_data/sample_850.x12
```

### Generate Power BI Dashboard

```bash
# Generate sample metrics and dashboard
python main.py dashboard --generate-sample-metrics

# Open Power BI Desktop and load:
# dashboards/EDIProcessingDashboard.pbip
```

## Common Commands

```bash
# Process a single file
python main.py process --file path/to/file.x12

# Process all files in directory
python main.py process --directory /path/to/edi/files

# Validate a file
python main.py validate --file path/to/file.x12

# Monitor directories (runs continuously)
python main.py monitor

# Generate dashboard
python main.py dashboard
```

## Next Steps

- See [README.md](README.md) for full documentation
- See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment
- See [docs/DASHBOARD.md](docs/DASHBOARD.md) for dashboard customization

## Troubleshooting

**Issue: Module not found**
```bash
pip install -r requirements.txt
```

**Issue: No metrics in dashboard**
```bash
python main.py dashboard --generate-sample-metrics
```

**Issue: Configuration errors**
- Check `config/config.yaml` and `config/sterling_config.yaml`
- Ensure paths are correct for your system

