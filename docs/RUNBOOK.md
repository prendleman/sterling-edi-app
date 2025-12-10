# Operations Runbook

This runbook provides step-by-step procedures for common operational tasks.

## Table of Contents

1. [Startup Procedures](#startup-procedures)
2. [Shutdown Procedures](#shutdown-procedures)
3. [Monitoring](#monitoring)
4. [Troubleshooting](#troubleshooting)
5. [Backup and Recovery](#backup-and-recovery)
6. [Performance Tuning](#performance-tuning)
7. [Incident Response](#incident-response)

## Startup Procedures

### Starting the Application

#### Standalone Mode
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Start file monitor
python main.py monitor --config config/config.yaml
```

#### Docker Mode
```bash
# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f edi-processor
```

#### API Server Mode
```bash
# Start API server
python -m src.api_server

# Or with Docker
docker-compose up
```

### Verification Steps

1. Check health endpoint: `curl http://localhost:5000/health`
2. Verify log files are being created in `logs/` directory
3. Check metrics directory exists and is writable
4. Verify Sterling directories are accessible
5. Test with sample file: `python main.py process tests/sample_data/sample_850.x12`

## Shutdown Procedures

### Graceful Shutdown

#### Standalone Mode
```bash
# Stop file monitor (Ctrl+C or kill signal)
# Process will finish current file before stopping
```

#### Docker Mode
```bash
# Graceful shutdown
docker-compose down

# Force shutdown
docker-compose down --timeout 0
```

### Post-Shutdown Checks

1. Verify no files are locked
2. Check for incomplete processing
3. Review error directory for failed files
4. Archive logs if needed

## Monitoring

### Health Checks

```bash
# API health check
curl http://localhost:5000/health

# System status
curl http://localhost:5000/api/v1/status
```

### Key Metrics to Monitor

1. **Processing Rate**: Files processed per hour
2. **Error Rate**: Percentage of failed files
3. **Processing Time**: Average and P95 processing times
4. **Queue Depth**: Number of files waiting to be processed
5. **System Resources**: CPU, memory, disk space

### Log Monitoring

```bash
# Watch logs in real-time
tail -f logs/edi_processor_*.log

# Search for errors
grep -i error logs/edi_processor_*.log

# Check recent activity
tail -n 100 logs/edi_processor_*.log
```

## Troubleshooting

### Common Issues

#### Issue: Files Not Processing

**Symptoms**: Files accumulating in pickup directory

**Diagnosis**:
1. Check if process is running: `ps aux | grep python`
2. Check logs for errors: `tail -f logs/edi_processor_*.log`
3. Verify directory permissions
4. Check disk space: `df -h`

**Resolution**:
- Restart the service
- Check file permissions
- Verify configuration

#### Issue: High Error Rate

**Symptoms**: Many files in error directory

**Diagnosis**:
1. Review error logs
2. Check validation rules
3. Verify Sterling connectivity
4. Check Acumatica API status

**Resolution**:
- Review and fix validation rules
- Check network connectivity
- Verify API credentials
- Review error files for patterns

#### Issue: Slow Processing

**Symptoms**: Processing times increasing

**Diagnosis**:
1. Check system resources: `top`, `htop`
2. Review processing metrics
3. Check database performance
4. Review network latency

**Resolution**:
- Increase processing workers
- Optimize database queries
- Check network connectivity
- Review file sizes

### Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| E001 | File read error | Check file permissions and format |
| E002 | Parse error | Verify EDI format |
| E003 | Validation error | Review validation rules |
| E004 | Delivery error | Check Sterling connectivity |
| E005 | API error | Verify API credentials and connectivity |

## Backup and Recovery

### Backup Procedures

#### Configuration Backup
```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/

# Backup to remote location
scp config_backup_*.tar.gz backup-server:/backups/
```

#### Metrics Backup
```bash
# Backup metrics database
cp metrics/edi_metrics.db backups/metrics_$(date +%Y%m%d).db

# Or export to SQL
sqlite3 metrics/edi_metrics.db .dump > backups/metrics_$(date +%Y%m%d).sql
```

#### Log Backup
```bash
# Archive old logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/*.log

# Remove old logs (keep last 30 days)
find logs/ -name "*.log" -mtime +30 -delete
```

### Recovery Procedures

#### Configuration Recovery
```bash
# Restore configuration
tar -xzf config_backup_YYYYMMDD.tar.gz

# Verify configuration
python main.py validate --config config/config.yaml
```

#### Metrics Recovery
```bash
# Restore metrics database
cp backups/metrics_YYYYMMDD.db metrics/edi_metrics.db

# Or restore from SQL
sqlite3 metrics/edi_metrics.db < backups/metrics_YYYYMMDD.sql
```

## Performance Tuning

### Configuration Tuning

Edit `config/config.yaml`:

```yaml
performance:
  max_workers: 4  # Increase for more parallelism
  batch_size: 100  # Increase for batch processing
  cache_size: 1000  # Increase for better caching
```

### System Tuning

1. **Increase file handles**: `ulimit -n 65536`
2. **Optimize database**: Regular VACUUM for SQLite
3. **Network tuning**: Adjust timeouts for slow networks
4. **Memory**: Allocate sufficient memory for processing

## Incident Response

### Severity Levels

- **Critical**: System down, no processing
- **High**: High error rate, significant delays
- **Medium**: Some errors, minor delays
- **Low**: Warnings, no impact

### Response Procedures

#### Critical Incident

1. **Immediate Actions**:
   - Check system status
   - Review recent logs
   - Verify connectivity
   - Notify stakeholders

2. **Investigation**:
   - Identify root cause
   - Check system resources
   - Review configuration changes
   - Check external dependencies

3. **Resolution**:
   - Apply fix
   - Restart service if needed
   - Verify recovery
   - Document incident

#### High Priority Incident

1. Monitor error rates
2. Review error logs
3. Check system resources
4. Apply fixes
5. Document resolution

### Escalation

- **Level 1**: Operations team (first 30 minutes)
- **Level 2**: Development team (after 30 minutes)
- **Level 3**: Management (after 2 hours)

## Maintenance Windows

### Scheduled Maintenance

- **Weekly**: Log rotation, metrics cleanup
- **Monthly**: Configuration review, performance analysis
- **Quarterly**: Full system review, updates

### Maintenance Checklist

- [ ] Backup configuration
- [ ] Backup metrics
- [ ] Review logs
- [ ] Check disk space
- [ ] Verify connectivity
- [ ] Test with sample files
- [ ] Update documentation

