# GlasseyeOS AI - Safety Architecture Guide

## Overview

The Enhanced Compliance Enforcer is a multi-layered autonomous safety system that prevents violations **before they occur** through real-time monitoring, scope enforcement, and automated incident response.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│              GlasseyeOS Components                          │
│   (Core, Agents, Tools, Orchestrator, Self-Updater)        │
└──────────────────┬──────────────────────────────────────────┘
                   │ All actions intercepted
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         ENHANCED COMPLIANCE ENFORCER                        │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  1. Real-Time Monitor                                 │ │
│  │     - Continuous action monitoring                    │ │
│  │     - Anomaly detection                               │ │
│  │     - Action queue (10,000 capacity)                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  2. Scope Boundary Enforcer                           │ │
│  │     - Program-specific scope verification             │ │
│  │     - Private IP blocking                             │ │
│  │     - Localhost protection                            │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  3. PII Detector (8 pattern types)                    │ │
│  │     - SSN, Credit Cards, Emails, Phones               │ │
│  │     - API Keys (AWS, GitHub, etc.)                    │ │
│  │     - Auto-stop on detection                          │ │
│  │     - Secure redaction                                │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  4. Rate Limiter                                      │ │
│  │     - Service-specific limits                         │ │
│  │     - Automatic service pause                         │ │
│  │     - Usage tracking                                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  5. Forbidden Action Blocker                          │ │
│  │     - 25+ dangerous patterns                          │ │
│  │     - Destructive command blocking                    │ │
│  │     - Production access prevention                    │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  6. Resource Ownership Verifier                       │ │
│  │     - GitHub repo ownership                           │ │
│  │     - Email domain verification                       │ │
│  │     - Server metadata checks                          │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  7. Incident Response System                          │ │
│  │     - Automated violation handling                    │ │
│  │     - Evidence preservation                           │ │
│  │     - Human notification                              │ │
│  │     - Report generation                               │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                   │
                   ▼
         ✓ Approved / ✗ Blocked
```

## Component Details

### 1. Real-Time Monitor

**Purpose:** Continuously watch all system activities and detect anomalies.

**Features:**
- Background monitoring thread
- Action queue with 10,000 event capacity
- Rapid-fire detection (>50 actions/minute triggers warning)
- Automatic rate limiting on suspicious activity

**Implementation:**
```python
class RealTimeMonitor:
    def monitor_loop(self):
        while self.is_running:
            action = self.action_queue.popleft()
            self.analyze_action(action)  # Check for anomalies
            
    def analyze_action(self, action):
        # Detect rapid-fire attacks
        if recent_actions > 50_per_minute:
            self.enforcer.pause_operations()
```

### 2. Scope Boundary Enforcement

**Purpose:** Ensure all testing is within authorized program scope.

**Checks:**
- ✅ Target domain matches program scope
- ✅ No private IP ranges (10.x, 192.168.x, 172.16-31.x)
- ✅ No localhost/127.0.0.1 access
- ✅ No production endpoints

**Example:**
```python
# GitHub Bug Bounty Scope
allowed = ["github.com", "copilot.github.com", "npmjs.org"]

# ✓ ALLOWED
enforcer.enforce_scope_boundary("https://api.github.com/users")

# ✗ BLOCKED
enforcer.enforce_scope_boundary("https://facebook.com/api")
enforcer.enforce_scope_boundary("http://192.168.1.1/admin")
enforcer.enforce_scope_boundary("http://localhost:8080")
```

### 3. PII Detector

**Purpose:** Detect and prevent PII access with immediate stop.

**Detection Patterns:**
- **SSN:** `XXX-XX-XXXX` format
- **Credit Cards:** Luhn algorithm validation
- **Emails:** Non-researcher domains only
- **Phones:** US/International formats
- **Addresses:** Street address patterns
- **API Keys:** AWS, GitHub, generic formats
- **Passwords:** Password-like strings

**Auto-Stop Behavior:**
```python
# When PII is detected:
1. STOP all operations immediately
2. Redact and log PII sample
3. Delete local copies
4. Create incident report
5. Notify human operator
6. Require human review before resuming
```

**Safe Domains:**
- `researcher.test`
- `hacktest.local`
- `bugbounty.test`

### 4. Rate Limiter

**Purpose:** Prevent excessive requests that could trigger DDoS protections.

**Limits:**
| Service | Limit | Window |
|---------|-------|--------|
| GitHub API | 5,000 requests | 1 hour |
| npm Registry | 1,000 requests | 1 hour |
| Web Scraping | 60 requests | 1 minute |
| System-wide | 1,000 requests | 1 minute |

**Behavior:**
```python
# Under limit: ✓ Allow
rate_limiter.check_rate_limit('github_api', action)
# → (True, None)

# Over limit: ✗ Block + Pause
rate_limiter.check_rate_limit('github_api', action)
# → (False, "Rate limit exceeded: 5001/5000 in 1hour")
# → Service paused for 1 hour
```

### 5. Forbidden Action Blocker

**Purpose:** Block dangerous operations that violate safe harbor.

**Blocked Categories:**

**Destructive Filesystem:**
- `rm -rf /`
- `mkfs.*`
- `dd if=/dev/zero`
- `shred -`

**Destructive Database:**
- `DROP TABLE`
- `DROP DATABASE`
- `DELETE FROM ... WHERE 1=1`
- `TRUNCATE TABLE`

**Credential Theft:**
- `curl.*password`
- `wget.*\.ssh`
- `cat.*\.aws/credentials`
- `exfiltrate`

**Production Access:**
- `ssh prod`
- `kubectl.*production`
- `aws s3.*prod-bucket`

**Unauthorized Scanning:**
- `nmap.*github.com`
- `masscan`
- `sqlmap --dump-all`

**Social Engineering:**
- `phishing`
- `impersonate`
- `fake.*email`

### 6. Resource Ownership Verifier

**Purpose:** Ensure all testing uses researcher-owned resources only.

**Verification Types:**

**GitHub Repositories:**
```python
resource = {
    'type': 'github_repo',
    'owner': 'researcher_username',  # Must match profile
    'name': 'test-repo'
}
```

**Email Accounts:**
```python
resource = {
    'type': 'email_account',
    'email': 'test@researcher.test'  # Domain must be approved
}
```

**Test Servers:**
```python
resource = {
    'type': 'test_server',
    'owner_metadata': {'owner_id': 'researcher-001'}
}
```

### 7. Incident Response System

**Purpose:** Automated handling of compliance violations.

**Workflow:**

```
Violation Detected
       ↓
1. STOP Operations
       ↓
2. Capture System State
       ↓
3. Determine Severity (CRITICAL/HIGH/MEDIUM/LOW)
       ↓
4. Execute Response Actions
   - PII: Delete local copies
   - Critical: Emergency stop
       ↓
5. Create Incident Report
   → logs/incidents/violation-YYYYMMDD-HHMMSS-{id}.json
       ↓
6. Notify Human Operator
       ↓
7. Require Human Review Before Resume
```

**Incident Report Structure:**
```json
{
  "incident_id": "abc123def456",
  "timestamp": "2026-05-18T17:30:45Z",
  "violation_type": "PII_DETECTED",
  "severity": "CRITICAL",
  "details": {
    "pii_types": ["SSN", "EMAIL"],
    "data_sample": "[REDACTED]",
    "data_location": "memory"
  },
  "system_state": {
    "violations_count": 1,
    "emergency_stop": true,
    "active_monitors": true
  },
  "actions_taken": [
    "deleted_local_copies",
    "emergency_stop_triggered"
  ],
  "requires_human_review": true,
  "resolved": false
}
```

## Action Approval Workflow

```
┌─────────────────────┐
│  Component Action   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ intercept_action()  │  ← Rate limit check
│                     │  ← Forbidden pattern check
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ verify_safe_harbor()│  ← Emergency stop check
│                     │  ← Risk level verification
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│check_scope_boundary │  ← Domain whitelist
│                     │  ← Private IP block
│                     │  ← Localhost block
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   scan_for_pii()    │  ← 8 PII patterns
│                     │  ← Auto-stop on detect
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│verify_researcher_   │  ← Ownership verification
│       _owned()      │
└──────────┬──────────┘
           │
           ▼
    ✓ APPROVED / ✗ BLOCKED
```

## Configuration

All rules are configurable via `config/compliance_rules.yaml`:

```yaml
safe_harbor:
  programs:
    - name: "GitHub Bug Bounty"
      scope:
        domains: ["github.com", "npmjs.org"]
      prohibited: ["DDoS", "Social engineering"]

rate_limits:
  github_api: {requests: 5000, window: "1hour"}

forbidden_patterns:
  - 'rm\s+-rf\s+/'
  - 'DROP\s+TABLE'

max_violations: 3  # Emergency stop threshold
```

## Emergency Stop

**Triggers:**
- Max violations exceeded (default: 3)
- PII detected
- Critical incident

**Effects:**
- ✗ ALL actions blocked
- ⏸️  All operations paused
- 📝 Incident report created
- 👤 Human notification sent
- 🔒 Requires admin reset

**Reset:**
```python
enforcer.reset_emergency_stop("RESET_EMERGENCY_STOP")
```

## Integration

### Hook into Components

```python
# In glasseye_core.py, agent_orchestrator.py, etc.
from compliance_enforcer import ComplianceEnforcer, Action, RiskLevel

enforcer = ComplianceEnforcer()

# Before executing any action
action = Action(
    action_type="api_request",
    target="https://api.github.com/repos",
    description="List GitHub repositories",
    risk_level=RiskLevel.LOW,
    requires_human_approval=False
)

# Step 1: Intercept (rate limit + forbidden check)
if not enforcer.intercept_action("github_client", action):
    raise ComplianceViolation("Action blocked by enforcer")

# Step 2: Full approval workflow
approved, reason = enforcer.approve_action(
    action,
    program_scope=["github.com"],
    researcher_resources=["researcher_test"]
)

if not approved:
    logger.error(f"Action denied: {reason}")
    return

# Step 3: Execute action
execute_action(action)
```

## Audit Trail

All actions are logged to `logs/compliance_audit.jsonl`:

```json
{"timestamp": "2026-05-18T17:30:45Z", "action_type": "api_request", "approved": true, "reason": "All checks passed"}
{"timestamp": "2026-05-18T17:31:12Z", "action_type": "port_scan", "approved": false, "reason": "Target out of scope"}
```

## System Status

```python
status = enforcer.get_system_status()

# Returns:
{
  "emergency_stop": false,
  "violations_count": 2,
  "monitoring_active": true,
  "hooked_components": ["core", "orchestrator"],
  "rate_limits": {
    "github_api": {"current": 150, "limit": 5000, "utilization": "3.0%"}
  },
  "recent_incidents": [
    {"id": "abc123", "type": "OUT_OF_SCOPE", "severity": "HIGH", "resolved": false}
  ]
}
```

## Best Practices

1. **Always intercept first:** Call `intercept_action()` before `approve_action()`
2. **Configure per-program:** Use YAML config for program-specific rules
3. **Monitor incident reports:** Review `logs/incidents/` regularly
4. **Test violations:** Use test suite to verify all scenarios
5. **Reset emergency stop:** Only after investigation complete

## Testing

Run comprehensive test suite:

```bash
cd /home/x/GlasseyeOS-AI
python3 tests/test_compliance_enforcer.py
```

Tests cover:
- ✓ PII detection (SSN, cards, emails, phones, API keys)
- ✓ Rate limiting (under/over limits, service pause)
- ✓ Scope enforcement (in/out of scope, private IPs, localhost)
- ✓ Forbidden actions (filesystem, database, credentials, production)
- ✓ Resource ownership (GitHub, email, servers)
- ✓ Incident response (creation, severity, notifications)
- ✓ Complete workflows (approval, rejection, emergency stop)

## Security Guarantees

✅ **No bypassing:** Every action MUST pass through enforcer  
✅ **Defense in depth:** 7 independent safety layers  
✅ **Fail-secure:** Violations trigger stop, not continue  
✅ **Auditable:** Complete JSONL audit trail  
✅ **Incident response:** Automated handling with human review  
✅ **Configurable:** YAML-based rules, no code changes  
✅ **Real-time:** Sub-second violation detection  

---

**Last Updated:** 2026-05-18  
**Version:** 2.0 (Enhanced)
