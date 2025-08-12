# AdvancedSIEM - AI-Powered Security Information and Event Management System

An advanced SIEM system with integrated AI-powered detection, real-time log analysis, and intelligent correlation capabilities.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/BadBoy0170/SIEMcli.git
cd AdvancedSIEM

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the SIEM
python3 src/siem_core.py
```

## Features

- **Real-time Log Collection**
  - System logs
  - Network logs
  - Application logs
  - Custom log sources support
  - Automatic log file creation and monitoring

- **AI-Powered Detection**
  - Machine learning-based anomaly detection
  - Deep learning pattern recognition
  - Signature-based detection
  - Adaptive learning from historical data
  - Hybrid detection approach (ML + Rule-based)

- **Advanced Analytics**
  - Pattern matching
  - Event correlation
  - Frequency analysis
  - Sequence detection
  - Similarity analysis

- **Smart Alerting**
  - Severity-based prioritization
  - Alert correlation
  - False positive reduction
  - Customizable thresholds
  - Real-time notifications

## Directory Structure

```
AdvancedSIEM/
├── config/
│   └── custom_signatures.yaml    # Custom detection signatures
├── logs/
│   ├── system.log               # System logs
│   ├── network.log              # Network logs
│   └── app.log                  # Application logs
├── src/
│   ├── siem_core.py            # Main SIEM engine
│   ├── collectors.py           # Log collectors
│   ├── analyzer.py            # Log analyzer
│   └── ai_detection.py        # AI detection engine
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## Configuration

### Custom Signatures

You can add custom detection signatures in `config/custom_signatures.yaml`:

```yaml
custom_threats:
  - name: "Custom Malware Pattern"
    pattern: "your_pattern_here"
    severity: "HIGH"

web_attacks:
  - name: "Custom Web Attack"
    pattern: "attack_pattern"
    severity: "CRITICAL"
```

### Log Sources

By default, the SIEM monitors these log files:
- `logs/system.log`: System-level events
- `logs/network.log`: Network traffic and security events
- `logs/app.log`: Application-specific logs

## Usage

### Running the SIEM

1. Start the SIEM:
```bash
python3 src/siem_core.py
```

2. The system will:
   - Display a banner with version information
   - Initialize all components
   - Start monitoring configured log files
   - Begin real-time analysis

### Testing

Run the test suite to verify functionality:
```bash
python3 test_siem.py
```

This will:
- Test all components
- Generate sample events
- Verify detection capabilities

### Adding Log Sources

1. Create a new log file in the `logs` directory
2. Update `src/collectors.py` to include the new log source:
```python
self.source_configs = {
    'your_source': {
        'paths': ['logs/your_log.log'],
        'patterns': ['error', 'warning', 'critical']
    }
}
```

### Adding Custom Signatures

1. Open `config/custom_signatures.yaml`
2. Add your signature under appropriate category:
```yaml
your_category:
  - name: "Signature Name"
    pattern: "regex_pattern"
    severity: "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
```

## Detection Capabilities

### 1. Signature-Based Detection

Detects known patterns including:
- Malware and backdoors
- Command injection
- SQL injection
- Privilege escalation
- Data exfiltration
- Reconnaissance activities

### 2. AI-Based Detection

- Anomaly detection using Isolation Forest
- Pattern recognition using neural networks
- Adaptive learning from historical data
- Feature extraction for different log types

### 3. Event Correlation

- Rule-based correlation
- Temporal correlation
- Sequence detection
- Frequency analysis

## Monitoring and Alerts

The SIEM provides real-time alerts for:
- Critical security events
- Anomalous behavior
- Pattern matches
- Correlated events

Alert severity levels:
- CRITICAL: Immediate action required
- HIGH: Requires prompt attention
- MEDIUM: Should be investigated
- LOW: Informational

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   sudo chmod 644 logs/*.log
   sudo chown $USER logs/
   ```

2. **Module Import Errors**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Log File Access**
   - Ensure log files exist
   - Check file permissions
   - Verify paths in configuration

### Performance Tuning

1. **Memory Usage**
   - Adjust `maxlen` in event history
   - Modify batch processing size
   - Configure cleanup intervals

2. **CPU Usage**
   - Adjust processing intervals
   - Optimize pattern matching
   - Configure event batching

## Security Considerations

1. **Log File Security**
   - Use appropriate file permissions
   - Implement log rotation
   - Secure backup storage

2. **Detection Rules**
   - Regularly update signatures
   - Tune detection thresholds
   - Monitor false positives

3. **System Access**
   - Restrict file access
   - Use secure configurations
   - Monitor system resources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests:
1. Check existing issues
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected behavior
   - System information 
