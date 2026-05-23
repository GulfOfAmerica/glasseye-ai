# Configuration Guide

## Overview

This guide explains how to configure the Enhanced Compliance Enforcer using `config/compliance_rules.yaml`.

## Configuration File Location

```
/home/x/GlasseyeOS-AI/config/compliance_rules.yaml
```

## Full Configuration Structure

```yaml
# Safe Harbor Program Definitions
safe_harbor:
  programs: [...]

# Rate Limiting Configuration
rate_limits: {...}

# Forbidden Patterns
forbidden_patterns: [...]

# PII Detection
pii_detection: {...}

# Violation Thresholds
max_violations: 3

# Human Approval Requirements
required_approvals: {...}

# Incident Response
incident_response: {...}

# Researcher Profile
researcher_profile_requirements: {...}

# Monitoring
monitoring: {...}

# Logging
logging: {...}

# Emergency Stop
emergency_stop: {...}
```

---

## 1. Safe Harbor Programs

Define bug bounty programs and their scopes.

```yaml
safe_harbor:
  programs:
    - name: "GitHub Bug Bounty"
      scope:
        domains:
          - "github.com"
          - "copilot.github.com"
          - "npmjs.org"
          - "npmjs.com"
          - "api.github.com"
      prohibited:
        - "DDoS attacks or denial of service"
        - "Social engineering or phishing"
        - "Production system testing without authorization"
        - "PII access or data exfiltration"
      required:
        - "Researcher-owned resources only"
        - "HackerOne account required"
```

**Adding a New Program:**

```yaml
    - name: "Your Program Name"
      scope:
        domains:
          - "target.com"
          - "*.target.com"  # Wildcard for subdomains
          - "staging.target.com"
      prohibited:
        - "Production database access"
        - "Real customer data"
      required:
        - "Test environment only"
```

---

## 2. Rate Limits

Control request rates to prevent DDoS and abuse.

```yaml
rate_limits:
  service_name:
    requests: 100      # Max requests
    window: "1hour"    # Time window
    description: "Service description"
```

**Supported Windows:**
- `"1second"`, `"30seconds"`
- `"1minute"`, `"5minutes"`
- `"1hour"`, `"24hours"`

**Example:**

```yaml
rate_limits:
  github_api:
    requests: 5000
    window: "1hour"
    description: "GitHub API rate limit"
  
  custom_api:
    requests: 100
    window: "1minute"
    description: "Custom API endpoint"
```

**Tuning Guidelines:**
- Start conservative, increase if needed
- Consider service's published limits
- Leave 20% buffer for safety
- Monitor utilization regularly

---

## 3. Forbidden Patterns

Define regex patterns for actions that must be blocked.

```yaml
forbidden_patterns:
  - 'pattern_regex'
  - 'another_pattern'
```

**Pattern Categories:**

**Destructive Filesystem:**
```yaml
  - 'rm\s+-rf\s+/'
  - 'mkfs\.'
  - 'dd\s+if=/dev/zero'
```

**Destructive Database:**
```yaml
  - 'DROP\s+TABLE'
  - 'DROP\s+DATABASE'
  - 'TRUNCATE\s+TABLE'
```

**Credential Theft:**
```yaml
  - 'curl.*password'
  - 'wget.*\.ssh'
  - 'cat.*\.aws/credentials'
```

**Custom Patterns:**
```yaml
  # Block specific command
  - 'dangerous_command'
  
  # Block pattern in any command
  - '.*hack.*production.*'
  
  # Block SQL injection attempts
  - 'union\s+select.*from'
```

**Testing Patterns:**

```python
import re

pattern = r'rm\s+-rf\s+/'
test_cases = [
    "rm -rf /",      # ✓ Should match
    "rm -rf /tmp",   # ✓ Should match
    "rm file.txt"    # ✗ Should not match
]

for test in test_cases:
    match = re.search(pattern, test, re.IGNORECASE)
    print(f"{test}: {'BLOCKED' if match else 'ALLOWED'}")
```

---

## 4. PII Detection

Configure PII detection behavior.

```yaml
pii_detection:
  enabled: true
  auto_stop: true  # Emergency stop on PII detection
  
  approved_email_domains:
    - "researcher.test"
    - "hacktest.local"
    - "bugbounty.test"
```

**Adding Approved Domains:**

```yaml
  approved_email_domains:
    - "your-domain.test"
    - "your-company.local"
```

**Note:** PII patterns are hardcoded in Python for security. To modify patterns, edit `PIIDetector` class in `compliance_enforcer.py`.

---

## 5. Violation Thresholds

Control when emergency stop is triggered.

```yaml
max_violations: 3  # Emergency stop after this many violations
```

**Recommended Values:**
- **Strict:** `1-2` violations
- **Balanced:** `3-5` violations
- **Lenient:** `6-10` violations

**Considerations:**
- Lower threshold = more sensitive
- Higher threshold = more forgiving of false positives
- Balance security vs operational flexibility

---

## 6. Human Approval Requirements

Define which risk levels require human approval.

```yaml
required_approvals:
  high: true      # HIGH risk actions need approval
  critical: true  # CRITICAL risk actions need approval
```

**Risk Levels:**
- **SAFE:** Passive reconnaissance (no approval)
- **LOW:** Active scanning, non-invasive (no approval)
- **MEDIUM:** Fuzzing, auth testing (optional approval)
- **HIGH:** Exploitation attempts (requires approval)
- **CRITICAL:** System modification, data access (requires approval)

**Custom Configuration:**

```yaml
required_approvals:
  safe: false
  low: false
  medium: true   # Also require approval for medium risk
  high: true
  critical: true
```

---

## 7. Incident Response

Configure automated incident handling.

```yaml
incident_response:
  enabled: true
  auto_report: true       # Automatically create reports
  notify_human: true      # Send notifications
  preserve_evidence: true # Save system state
  
  severity_levels:
    CRITICAL:
      - PII_DETECTED
      - OUT_OF_SCOPE
      - FORBIDDEN_ACTION
    HIGH:
      - UNOWNED_RESOURCE
      - RATE_LIMIT_EXCEEDED
    MEDIUM:
      - UNSAFE_OPERATION
    LOW:
      - UNAUTHORIZED_ACCESS
```

**Customizing Severity:**

```yaml
  severity_levels:
    CRITICAL:
      - PII_DETECTED
      - CUSTOM_CRITICAL_VIOLATION
    HIGH:
      - OUT_OF_SCOPE
```

---

## 8. Researcher Profile Requirements

Define what constitutes a valid researcher profile.

```yaml
researcher_profile_requirements:
  required_fields:
    - id
    - github_username
    - approved_email_domains
    - hackerone_username
  
  verification_methods:
    github_repo: "owner_match"
    email_account: "domain_match"
    test_server: "metadata_verification"
```

**Example Researcher Profile:**

```python
researcher_profile = {
    'id': 'researcher-001',
    'github_username': 'your_github_username',
    'approved_email_domains': [
        'researcher.test',
        'your-domain.test'
    ],
    'hackerone_username': 'your_h1_username'
}
```

---

## 9. Monitoring Configuration

Configure real-time monitoring behavior.

```yaml
monitoring:
  enabled: true
  real_time: true
  queue_size: 10000  # Action queue capacity
  
  anomaly_detection:
    enabled: true
    rapid_fire_threshold: 50  # Actions per minute
```

**Tuning Anomaly Detection:**

```yaml
  anomaly_detection:
    enabled: true
    rapid_fire_threshold: 100   # More lenient
    window_seconds: 60          # Detection window
    auto_pause_duration: 300    # Pause for 5 minutes
```

---

## 10. Logging Configuration

Configure audit logging and incident reporting.

```yaml
logging:
  audit_log: "logs/compliance_audit.jsonl"
  incident_dir: "logs/incidents"
  compliance_log: "logs/compliance.log"
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Log Levels:**
- **DEBUG:** Very verbose, all details
- **INFO:** Normal operations (recommended)
- **WARNING:** Only warnings and errors
- **ERROR:** Only errors and critical
- **CRITICAL:** Only critical events

---

## 11. Emergency Stop

Configure emergency stop behavior.

```yaml
emergency_stop:
  enabled: true
  reset_password: "RESET_EMERGENCY_STOP"  # ⚠️ CHANGE IN PRODUCTION
  auto_trigger_on:
    - max_violations_exceeded
    - pii_detected
    - critical_incident
```

**⚠️ SECURITY:**
- **CHANGE** default password in production
- Use strong, unique password
- Store securely (password manager)
- Rotate regularly

---

## Configuration Examples

### Strict Security (Production)

```yaml
max_violations: 1
required_approvals:
  low: true
  medium: true
  high: true
  critical: true

rate_limits:
  github_api:
    requests: 3000  # Conservative
    window: "1hour"

monitoring:
  anomaly_detection:
    rapid_fire_threshold: 25  # Very sensitive
```

### Balanced (Testing)

```yaml
max_violations: 3
required_approvals:
  high: true
  critical: true

rate_limits:
  github_api:
    requests: 5000
    window: "1hour"

monitoring:
  anomaly_detection:
    rapid_fire_threshold: 50
```

### Lenient (Development)

```yaml
max_violations: 5
required_approvals:
  critical: true  # Only critical requires approval

rate_limits:
  github_api:
    requests: 10000  # High limit
    window: "1hour"

monitoring:
  anomaly_detection:
    rapid_fire_threshold: 100
```

---

## Reloading Configuration

**After editing `compliance_rules.yaml`:**

```python
# Restart the enforcer to reload config
from compliance_enforcer import ComplianceEnforcer

enforcer = ComplianceEnforcer()  # Loads updated config
```

**Or reload in running system:**

```python
# Reload configuration dynamically
enforcer.compliance_rules = enforcer._load_compliance_rules()
print("✓ Configuration reloaded")
```

---

## Validation

**Validate YAML syntax:**

```bash
python3 -c "
import yaml
with open('config/compliance_rules.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('✓ Configuration valid')
    print(f'Programs: {len(config[\"safe_harbor\"][\"programs\"])}')
    print(f'Rate limits: {len(config[\"rate_limits\"])}')
    print(f'Forbidden patterns: {len(config[\"forbidden_patterns\"])}')
"
```

**Test configuration:**

```bash
python3 -c "
from compliance_enforcer import ComplianceEnforcer
e = ComplianceEnforcer()
print(e.get_system_status())
"
```

---

## Troubleshooting

**Config file not found:**
```
FileNotFoundError: config/compliance_rules.yaml
```
→ Create file or check path

**Invalid YAML syntax:**
```
yaml.scanner.ScannerError: ...
```
→ Check indentation, colons, quotes

**Pattern not matching:**
```python
# Test pattern in isolation
import re
pattern = r'your_pattern'
test = "your test string"
print(re.search(pattern, test, re.IGNORECASE))
```

**Rate limit not working:**
```python
# Check rate limit config
from compliance_enforcer import ComplianceEnforcer
e = ComplianceEnforcer()
print(e.rate_limiter.limits)
```

---

## Best Practices

1. ✅ **Version control:** Keep config in Git
2. ✅ **Backup:** Backup before changes
3. ✅ **Test:** Validate after edits
4. ✅ **Document:** Comment complex patterns
5. ✅ **Review:** Regular security reviews
6. ✅ **Monitor:** Watch audit logs after changes
7. ✅ **Rollback:** Keep previous working config

---

**Last Updated:** 2026-05-18  
**Version:** 2.0
