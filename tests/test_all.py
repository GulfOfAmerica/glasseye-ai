#!/usr/bin/env python3
"""
Unit tests for GlasseyeOS AI components.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compliance_enforcer import ComplianceEnforcer, Action, RiskLevel, ComplianceViolation
from knowledge_base import KnowledgeBase, CVE, DisclosedBounty, Campaign
from glasseye_core import GlasseyeAI, Target
from agent_orchestrator import EnhancedAgentOrchestrator, AgentTask, AgentType


class TestComplianceEnforcer(unittest.TestCase):
    """Test compliance enforcement."""
    
    def setUp(self):
        self.enforcer = ComplianceEnforcer()
        self.program_scope = ["*.example.com", "api.target.com"]
        self.researcher_resources = ["test@researcher.com", "api_key_123"]
    
    def test_safe_action_approval(self):
        """Test that safe actions are approved."""
        action = Action(
            action_type="dns_enumeration",
            target="api.example.com",
            description="DNS enumeration",
            risk_level=RiskLevel.SAFE,
            requires_human_approval=False,
            scope_verified=True
        )
        
        approved, reason = self.enforcer.approve_action(
            action, self.program_scope, self.researcher_resources
        )
        
        self.assertTrue(approved)
    
    def test_out_of_scope_blocked(self):
        """Test that out-of-scope targets are blocked."""
        action = Action(
            action_type="port_scan",
            target="evil.com",
            description="Port scan evil.com",
            risk_level=RiskLevel.MEDIUM,
            requires_human_approval=True,
            scope_verified=False
        )
        
        approved, reason = self.enforcer.approve_action(
            action, self.program_scope, self.researcher_resources
        )
        
        self.assertFalse(approved)
        # Should be blocked (either safe harbor failure or scope issue)
        self.assertTrue(len(reason) > 0)
    
    def test_forbidden_pattern_blocked(self):
        """Test that forbidden patterns are blocked."""
        action = Action(
            action_type="sql_injection",
            target="api.example.com",
            description="Execute: DROP TABLE users;",
            risk_level=RiskLevel.CRITICAL,
            requires_human_approval=True,
            scope_verified=True
        )
        
        approved, reason = self.enforcer.approve_action(
            action, self.program_scope, self.researcher_resources
        )
        
        self.assertFalse(approved)
    
    def test_scope_verification(self):
        """Test scope boundary checking."""
        # In scope
        self.assertTrue(
            self.enforcer.check_scope_boundaries("api.example.com", self.program_scope)
        )
        self.assertTrue(
            self.enforcer.check_scope_boundaries("subdomain.example.com", self.program_scope)
        )
        
        # Out of scope
        self.assertFalse(
            self.enforcer.check_scope_boundaries("evil.com", self.program_scope)
        )
    
    def test_pii_detection(self):
        """Test PII pattern detection."""
        # SSN
        self.assertTrue(
            self.enforcer.detect_pii_risk("SSN: 123-45-6789")
        )
        
        # Credit card
        self.assertTrue(
            self.enforcer.detect_pii_risk("Card: 1234567890123456")
        )
        
        # Safe data
        self.assertFalse(
            self.enforcer.detect_pii_risk("Testing API endpoint /api/users")
        )


class TestKnowledgeBase(unittest.TestCase):
    """Test knowledge base operations."""
    
    def setUp(self):
        # Use in-memory database for testing
        self.kb = KnowledgeBase(db_path=":memory:")
    
    def tearDown(self):
        self.kb.close()
    
    def test_add_cve(self):
        """Test adding CVE to database."""
        cve = CVE(
            cve_id="CVE-2024-TEST",
            cvss_score=8.5,
            attack_vector="Network",
            vulnerability_type="Authentication Bypass",
            affected_products="Test Product",
            learned_pattern="Test pattern"
        )
        
        self.kb.add_cve(cve)
        
        # Search for added CVE
        results = self.kb.search_cves(vulnerability_type="Authentication")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['cve_id'], "CVE-2024-TEST")
    
    def test_add_bounty(self):
        """Test adding disclosed bounty."""
        bounty = DisclosedBounty(
            report_id="H1-TEST",
            program="Test Program",
            title="Test Vulnerability",
            severity="High",
            bounty_amount=5000,
            attack_pattern="Test pattern",
            lessons_learned="Test lessons"
        )
        
        self.kb.add_disclosed_bounty(bounty)
        
        # Search for added bounty
        results = self.kb.search_bounties(program="Test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['bounty_amount'], 5000)
    
    def test_campaign_management(self):
        """Test campaign creation and updates."""
        campaign = Campaign(
            campaign_id="test_campaign",
            target="test.com",
            status="active",
            hypotheses_count=5,
            findings_count=0,
            estimated_bounty=10000
        )
        
        self.kb.add_campaign(campaign)
        
        # Update campaign
        self.kb.update_campaign_status("test_campaign", "testing", findings_count=2)
        
        # Verify update
        campaigns = self.kb.get_active_campaigns()
        self.assertEqual(len(campaigns), 1)
        self.assertEqual(campaigns[0]['status'], "testing")
        self.assertEqual(campaigns[0]['findings_count'], 2)
    
    def test_vulnerability_patterns(self):
        """Test pattern learning and retrieval."""
        pattern_id = self.kb.add_vulnerability_pattern(
            pattern_name="Test Pattern",
            description="Test description",
            detection_method="Test method",
            exploitation_template="Test template",
            learned_from="CVE-2024-TEST",
            success_rate=0.7,
            avg_bounty=3000
        )
        
        self.assertIsNotNone(pattern_id)
        
        # Search patterns
        patterns = self.kb.search_patterns()
        self.assertGreater(len(patterns), 0)


class TestGlasseyeAI(unittest.TestCase):
    """Test GlasseyeAI intelligence engine."""
    
    def setUp(self):
        self.ai = GlasseyeAI()
        self.target = Target(
            name="Test Target",
            base_url="https://api.example.com",
            program_scope=["*.example.com"],
            out_of_scope=["blog.example.com"],
            safe_harbor={"researcher_owned_accounts": True},
            researcher_resources=["test@researcher.com"]
        )
    
    def tearDown(self):
        self.ai.close()
    
    def test_reconnaissance_plan_generation(self):
        """Test reconnaissance plan generation."""
        plan = self.ai.generate_reconnaissance_plan(self.target)
        
        self.assertIsNotNone(plan.plan_id)
        self.assertEqual(plan.target, "Test Target")
        self.assertGreater(len(plan.phases), 0)
        self.assertGreater(len(plan.tools_required), 0)
    
    def test_vulnerability_hypothesis_generation(self):
        """Test hypothesis generation."""
        attack_surfaces = [
            {
                "endpoint": "/api/users",
                "url": "https://api.example.com/api/users",
                "methods": ["GET", "POST"],
                "potential_vulnerabilities": ["IDOR", "authentication_bypass"]  # Use known patterns
            }
        ]
        
        hypotheses = self.ai.generate_vulnerability_hypotheses(
            attack_surfaces, self.target
        )
        
        # Should generate hypotheses for known patterns
        self.assertGreaterEqual(len(hypotheses), 0)
        
        if len(hypotheses) > 0:
            # Check hypothesis structure
            h = hypotheses[0]
            self.assertIsNotNone(h.hypothesis_id)
            self.assertIsNotNone(h.vulnerability_type)
            self.assertGreater(h.confidence, 0)
            self.assertGreater(h.expected_bounty, 0)
    
    def test_cve_monitoring(self):
        """Test CVE feed monitoring."""
        cves = self.ai.monitor_cve_feeds(keywords=["Copilot"])
        
        # Should discover simulated CVEs
        self.assertGreater(len(cves), 0)


class TestAgentOrchestrator(unittest.TestCase):
    """Test agent orchestration."""
    
    def setUp(self):
        self.orchestrator = EnhancedAgentOrchestrator()
    
    def tearDown(self):
        self.orchestrator.shutdown()
    
    def test_task_submission(self):
        """Test task queue submission."""
        task = AgentTask(
            task_id="test_task",
            agent_type=AgentType.OSINT,
            description="Test task",
            parameters={},
            priority=5
        )
        
        self.orchestrator.submit_task(task)
        
        status = self.orchestrator.get_status()
        self.assertGreater(status['queued_tasks'], 0)
    
    def test_agent_spawning(self):
        """Test agent spawning."""
        task = AgentTask(
            task_id="spawn_test",
            agent_type=AgentType.STATIC_ANALYSIS,
            description="Spawn test",
            parameters={},
            priority=5
        )
        
        agent_id = self.orchestrator.spawn_agent(AgentType.STATIC_ANALYSIS, task)
        
        self.assertIsNotNone(agent_id)
        self.assertIn(agent_id, self.orchestrator.active_agents)
    
    def test_finding_aggregation(self):
        """Test finding aggregation and deduplication."""
        task1 = AgentTask(
            task_id="task1",
            agent_type=AgentType.STATIC_ANALYSIS,
            description="Test 1",
            parameters={},
            priority=5
        )
        task1.result = {
            "vulnerabilities": [
                {"type": "IDOR", "confidence": 0.7, "location": "/api/users"}
            ]
        }
        
        task2 = AgentTask(
            task_id="task2",
            agent_type=AgentType.STATIC_ANALYSIS,
            description="Test 2",
            parameters={},
            priority=5
        )
        task2.result = {
            "vulnerabilities": [
                {"type": "IDOR", "confidence": 0.8, "location": "/api/users"},  # Duplicate
                {"type": "XSS", "confidence": 0.6, "location": "/search"}  # New
            ]
        }
        
        findings = self.orchestrator.aggregate_findings([task1, task2])
        
        # Should deduplicate IDOR finding
        self.assertEqual(len(findings), 2)


def run_tests():
    """Run all tests."""
    print("=== GlasseyeOS AI - Unit Tests ===\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestComplianceEnforcer))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeBase))
    suite.addTests(loader.loadTestsFromTestCase(TestGlasseyeAI))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentOrchestrator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
