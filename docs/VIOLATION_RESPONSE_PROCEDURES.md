# Violation Response Procedures

## Overview

This document outlines step-by-step procedures for responding to compliance violations detected by the Enhanced Compliance Enforcer.

## Violation Types

### 1. OUT_OF_SCOPE
**Severity:** HIGH  
**Description:** Target is not in bug bounty program scope

**Automated Response:**
1. ✗ Block action immediately
2. Log to audit trail
3. Create incident report
4. Increment violation counter

**Human Response:**
1. Review incident report in `logs/incidents/`
2. Verify target was actually out of scope
3. Check if scope definition needs updating
4. If legitimate: update `compliance_rules.yaml` scope
5. If violation: investigate why system attempted out-of-scope test

**Prevention:**
- Always verify program scope before research
- Update `compliance_rules.yaml` when scope changes
- Use scope boundary checker before fuzzing

---

### 2. PII_DETECTED
**Severity:** CRITICAL  
**Description:** Personally Identifiable Information detected in data

**Automated Response:**
1. 🚨 EMERGENCY STOP triggered
2. Delete local copies of PII data
3. Redact and log sample
4. Create CRITICAL incident report
5. Notify human immediately
6. Require manual review before resume

**Human Response:**
1. **IMMEDIATE:** Review incident report
   ```bash
   cat logs/incidents/violation-YYYYMMDD-HHMMSS-*.json
   ```

2. **Verify PII detection:**
   - Was it real PII or false positive?
   - What type: SSN, credit card, email, phone, API key?

3. **Data handling:**
   - Ensure all PII copies deleted
   - Check if PII was transmitted anywhere
   - Verify no PII in logs/reports

4. **Incident reporting:**
   - If real PII accessed: Report to program immediately
   - Document: How, when, what data, mitigation taken
   - Follow bug bounty program's PII disclosure process

5. **Resume operations:**
   ```python
   enforcer.reset_emergency_stop("RESET_EMERGENCY_STOP")
   ```

**Prevention:**
- Only test with researcher-owned accounts
- Use synthetic data for testing
- Configure approved researcher email domains
- Never attempt to access production user data

---

### 3. RATE_LIMIT_EXCEEDED
**Severity:** MEDIUM  
**Description:** Too many requests to a service in time window

**Automated Response:**
1. ⏸️  Pause service operations
2. Log to audit trail
3. Calculate pause duration
4. Create incident report

**Human Response:**
1. Check rate limit usage:
   ```python
   status = enforcer.get_system_status()
   print(status['rate_limits'])
   ```

2. Verify pause is appropriate:
   - GitHub API: 5000/hour limit
   - npm: 1000/hour limit
   - Web scraping: 60/minute limit

3. Wait for service to resume automatically, OR

4. Adjust rate limits if too restrictive:
   ```yaml
   # config/compliance_rules.yaml
   rate_limits:
     custom_service:
       requests: 100
       window: "1minute"
   ```

**Prevention:**
- Implement exponential backoff
- Batch requests when possible
- Use caching to reduce duplicate requests
- Monitor rate limit usage proactively

---

### 4. FORBIDDEN_ACTION
**Severity:** HIGH to CRITICAL  
**Description:** Action matches forbidden pattern (destructive, unauthorized, etc.)

**Automated Response:**
1. ✗ Block action immediately
2. Log forbidden pattern matched
3. Create incident report
4. Increment violation counter
5. If CRITICAL: trigger emergency stop

**Human Response:**
1. **CRITICAL REVIEW REQUIRED**
   ```bash
   tail -f logs/compliance.log | grep FORBIDDEN
   ```

2. Investigate why forbidden action was attempted:
   - Bug in autonomous agent logic?
   - Misconfigured tool?
   - Legitimate action misclassified?

3. If legitimate action:
   - Review forbidden pattern in `compliance_rules.yaml`
   - Refine regex to be more specific
   - Example: Allow `DELETE FROM test_users` but block `DELETE FROM * WHERE 1=1`

4. If actual violation:
   - Fix agent logic
   - Add additional safeguards
   - Review all recent actions for similar issues

**Forbidden Pattern Categories:**
- Destructive filesystem: `rm -rf /`, `mkfs`, `dd if=/dev/zero`
- Destructive database: `DROP TABLE`, `DELETE ... WHERE 1=1`
- Credential theft: `curl.*password`, `wget.*\.ssh`
- Production access: `ssh prod`, `kubectl.*production`
- Unauthorized scanning: `nmap.*github.com`, `masscan`
- Social engineering: `phishing`, `impersonate`

**Prevention:**
- Review all autonomous agent actions
- Use test/staging environments only
- Implement action approval workflow
- Regular code reviews

---

### 5. UNOWNED_RESOURCE
**Severity:** HIGH  
**Description:** Attempted to test on resource not owned by researcher

**Automated Response:**
1. ✗ Block action
2. Log resource details
3. Create incident report
4. Increment violation counter

**Human Response:**
1. Verify resource ownership:
   - GitHub repo: Is owner researcher's account?
   - Email: Is domain in approved list?
   - Server: Is ownership metadata correct?

2. If owned but not verified:
   - Update researcher profile:
     ```yaml
     researcher_profile:
       github_username: "your_username"
       approved_email_domains:
         - "researcher.test"
         - "hacktest.local"
     ```

3. If not owned:
   - CRITICAL: Do not proceed
   - Never test on non-owned resources
   - Create owned test account/repo instead

**Prevention:**
- Always use researcher-owned test accounts
- Verify ownership before testing
- Maintain approved resource list
- Use disposable test accounts

---

### 6. UNSAFE_OPERATION
**Severity:** MEDIUM  
**Description:** Operation flagged as potentially unsafe

**Automated Response:**
1. ⚠️  Log warning
2. May require human approval
3. Create incident report

**Human Response:**
1. Review operation details
2. Assess risk level
3. Approve or deny manually
4. Update rules if needed

---

### 7. UNAUTHORIZED_ACCESS
**Severity:** MEDIUM to HIGH  
**Description:** Attempted access to unauthorized resource

**Automated Response:**
1. ✗ Block access
2. Log attempt details
3. Create incident report

**Human Response:**
1. Review what was accessed
2. Verify authorization scope
3. Check for lateral movement
4. Update access controls

---

## Emergency Stop Procedures

### When Emergency Stop is Triggered

**Indicator:**
```
🚨 EMERGENCY STOP TRIGGERED: [reason]
```

**Status:**
- ✗ ALL actions blocked
- ⏸️  All operations paused
- 📝 Incident reports created
- 🔒 System locked

### Recovery Steps

1. **Assess Situation:**
   ```bash
   # View recent incidents
   ls -lt logs/incidents/ | head -n 5
   
   # Check system status
   python3 -c "
   from compliance_enforcer import ComplianceEnforcer
   e = ComplianceEnforcer()
   print(e.get_system_status())
   "
   ```

2. **Review All Incidents:**
   ```bash
   # Read latest incident
   cat logs/incidents/violation-*.json | jq '.'
   ```

3. **Investigate Root Cause:**
   - What triggered emergency stop?
   - PII detected? Out of scope? Forbidden action?
   - Was it legitimate or false positive?

4. **Remediate Issues:**
   - Fix code bugs
   - Update configuration
   - Improve filters/patterns
   - Add safeguards

5. **Verify Safety:**
   - Run test suite
   - Check all violations resolved
   - Review system status

6. **Reset Emergency Stop:**
   ```python
   from compliance_enforcer import ComplianceEnforcer
   
   enforcer = ComplianceEnforcer()
   enforcer.reset_emergency_stop("RESET_EMERGENCY_STOP")
   
   print("✓ Emergency stop reset")
   print(enforcer.get_system_status())
   ```

7. **Resume Monitoring:**
   - Verify monitor is running
   - Check rate limits reset
   - Confirm audit logging active

---

## Incident Investigation Template

```markdown
# Incident Investigation Report

**Incident ID:** [from incident report]
**Date/Time:** [YYYY-MM-DD HH:MM:SS UTC]
**Violation Type:** [OUT_OF_SCOPE, PII_DETECTED, etc.]
**Severity:** [CRITICAL, HIGH, MEDIUM, LOW]

## Summary
[Brief description of what happened]

## Timeline
- [HH:MM] Action initiated: [description]
- [HH:MM] Violation detected: [trigger]
- [HH:MM] Automated response: [actions taken]
- [HH:MM] Human notified
- [HH:MM] Investigation started

## Root Cause
[What caused the violation?]

## Impact Assessment
- Data accessed: [Yes/No, details]
- PII involved: [Yes/No, details]
- Systems affected: [list]
- Scope violation: [Yes/No, details]

## Remediation Actions
1. [Action taken]
2. [Action taken]
3. [Action taken]

## Prevention Measures
1. [Preventive measure]
2. [Preventive measure]

## Resolution
- Emergency stop reset: [Yes/No]
- Operations resumed: [Date/Time]
- Follow-up required: [Yes/No, details]

**Investigator:** [Name]
**Date Closed:** [YYYY-MM-DD]
```

---

## Audit Log Review

### Daily Review
```bash
# Check today's violations
grep "VIOLATION" logs/compliance.log | tail -n 20

# Check recent denials
grep "approved.*False" logs/compliance_audit.jsonl | tail -n 10 | jq '.'
```

### Weekly Review
```bash
# Count violations by type
cat logs/compliance_audit.jsonl | \
  grep "approved.*false" | \
  jq -r '.reason' | \
  sort | uniq -c | sort -rn

# Check rate limit utilization trends
python3 -c "
from compliance_enforcer import ComplianceEnforcer
e = ComplianceEnforcer()
for service, usage in e.get_system_status()['rate_limits'].items():
    print(f'{service}: {usage}')
"
```

### Monthly Review
```bash
# Generate incident summary
find logs/incidents/ -name "violation-*.json" -mtime -30 | \
  xargs cat | jq -s '
    group_by(.violation_type) | 
    map({type: .[0].violation_type, count: length})
  '
```

---

## Escalation Matrix

| Violation Type | Severity | Response Time | Escalation |
|----------------|----------|---------------|------------|
| PII_DETECTED | CRITICAL | Immediate | Security Lead + Program Manager |
| FORBIDDEN_ACTION (destructive) | CRITICAL | Immediate | Security Lead |
| OUT_OF_SCOPE | HIGH | 1 hour | Security Lead |
| UNOWNED_RESOURCE | HIGH | 1 hour | Researcher Lead |
| RATE_LIMIT_EXCEEDED | MEDIUM | 4 hours | Engineering |
| FORBIDDEN_ACTION (benign) | MEDIUM | 4 hours | Engineering |
| UNSAFE_OPERATION | LOW | 24 hours | Engineering |

---

## Contact Information

**Security Lead:** [Contact]  
**Program Manager:** [Contact]  
**Researcher Lead:** [Contact]  
**Engineering:** [Contact]

**Emergency Hotline:** [Number]  
**Incident Email:** security-incidents@[domain]

---

## References

- [Safety Architecture Guide](SAFETY_ARCHITECTURE.md)
- [Configuration Guide](CONFIGURATION_GUIDE.md)
- Bug Bounty Program Safe Harbor: [URL]
- Compliance Rules: `config/compliance_rules.yaml`

---

**Last Updated:** 2026-05-18  
**Version:** 2.0
