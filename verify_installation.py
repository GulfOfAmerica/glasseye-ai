#!/usr/bin/env python3
"""
Verify Enhanced Compliance Guardian Installation
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("Enhanced Compliance Guardian - Installation Verification")
print("=" * 70)
print()

checks = []

# 1. Check compliance_enforcer.py exists and size
enforcer_path = Path("compliance_enforcer.py")
if enforcer_path.exists():
    size = enforcer_path.stat().st_size
    lines = len(enforcer_path.read_text().splitlines())
    checks.append(("✓", f"compliance_enforcer.py exists ({lines} lines, {size} bytes)"))
else:
    checks.append(("✗", "compliance_enforcer.py NOT FOUND"))

# 2. Check config file
config_path = Path("config/compliance_rules.yaml")
if config_path.exists():
    size = config_path.stat().st_size
    lines = len(config_path.read_text().splitlines())
    checks.append(("✓", f"compliance_rules.yaml exists ({lines} lines, {size} bytes)"))
else:
    checks.append(("✗", "compliance_rules.yaml NOT FOUND"))

# 3. Check test file
test_path = Path("tests/test_compliance_enforcer.py")
if test_path.exists():
    size = test_path.stat().st_size
    lines = len(test_path.read_text().splitlines())
    checks.append(("✓", f"test_compliance_enforcer.py exists ({lines} lines, {size} bytes)"))
else:
    checks.append(("✗", "test_compliance_enforcer.py NOT FOUND"))

# 4. Check documentation
docs = [
    "docs/SAFETY_ARCHITECTURE.md",
    "docs/VIOLATION_RESPONSE_PROCEDURES.md",
    "docs/CONFIGURATION_GUIDE.md"
]

for doc in docs:
    doc_path = Path(doc)
    if doc_path.exists():
        size = doc_path.stat().st_size / 1024  # KB
        checks.append(("✓", f"{doc_path.name} exists ({size:.1f} KB)"))
    else:
        checks.append(("✗", f"{doc_path.name} NOT FOUND"))

# 5. Test imports
try:
    from compliance_enforcer import (
        ComplianceEnforcer, Action, RiskLevel, ViolationType,
        PIIDetector, RateLimiter, IncidentResponse, RealTimeMonitor
    )
    checks.append(("✓", "All modules import successfully"))
except Exception as e:
    checks.append(("✗", f"Import failed: {e}"))

# 6. Test initialization
try:
    enforcer = ComplianceEnforcer()
    checks.append(("✓", "ComplianceEnforcer initializes successfully"))
    
    # Check components
    if hasattr(enforcer, 'pii_detector'):
        checks.append(("✓", "PIIDetector component present"))
    if hasattr(enforcer, 'rate_limiter'):
        checks.append(("✓", "RateLimiter component present"))
    if hasattr(enforcer, 'incident_response'):
        checks.append(("✓", "IncidentResponse component present"))
    if hasattr(enforcer, 'monitor'):
        checks.append(("✓", "RealTimeMonitor component present"))
    
    # Check monitoring
    if enforcer.monitor.is_running:
        checks.append(("✓", "Real-time monitoring active"))
    
    # Shutdown cleanly
    enforcer.shutdown()
    checks.append(("✓", "Clean shutdown successful"))
    
except Exception as e:
    checks.append(("✗", f"Initialization failed: {e}"))

# Print results
print("Installation Checks:")
print("-" * 70)
for status, message in checks:
    print(f"{status} {message}")

print()
print("-" * 70)

# Summary
passed = sum(1 for status, _ in checks if status == "✓")
failed = sum(1 for status, _ in checks if status == "✗")

print(f"Total Checks: {len(checks)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print()

if failed == 0:
    print("✅ INSTALLATION VERIFIED - ALL SYSTEMS OPERATIONAL")
    sys.exit(0)
else:
    print("⚠️  INSTALLATION INCOMPLETE - See failures above")
    sys.exit(1)
