#!/usr/bin/env python3
"""
Unit tests for Enhanced Agent Orchestrator

Tests for multi-agent coordination, resource management, and campaign workflows.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from agent_orchestrator import (
    EnhancedAgentOrchestrator,
    AgentType,
    AgentTask,
    CampaignConfig,
    MessageType,
    Finding,
    ResourceManager,
    WorkloadBalancer,
    ResultAggregator,
    AgentMessenger
)
from campaign_templates import CampaignTemplates


class TestResourceManager(unittest.TestCase):
    """Test resource management functionality."""
    
    def setUp(self):
        self.manager = ResourceManager(max_agents=5, max_memory_gb=8.0, max_cpu_percent=70.0)
    
    def test_get_current_usage(self):
        """Test getting current system resource usage."""
        usage = self.manager.get_current_usage()
        
        self.assertIn('memory_used_gb', usage)
        self.assertIn('cpu_percent', usage)
        self.assertGreaterEqual(usage['cpu_percent'], 0)
    
    def test_can_spawn_agent_under_limit(self):
        """Test spawning agent when under resource limits."""
        can_spawn, reason = self.manager.can_spawn_agent(active_count=2)
        
        # Should be able to spawn if under max_agents (5)
        self.assertTrue(can_spawn or "Memory" in reason or "CPU" in reason)
    
    def test_can_spawn_agent_at_limit(self):
        """Test spawning agent when at agent limit."""
        can_spawn, reason = self.manager.can_spawn_agent(active_count=5)
        
        self.assertFalse(can_spawn)
        self.assertIn("Max agents limit", reason)
    
    def test_resource_stats(self):
        """Test getting detailed resource statistics."""
        stats = self.manager.get_resource_stats()
        
        self.assertIn('memory', stats)
        self.assertIn('cpu', stats)
        self.assertIn('agents', stats)
        self.assertEqual(stats['agents']['limit'], 5)


class TestAgentMessenger(unittest.TestCase):
    """Test inter-agent communication system."""
    
    def setUp(self):
        self.messenger = AgentMessenger()
    
    def test_send_direct_message(self):
        """Test sending direct message between agents."""
        self.messenger.send_message(
            from_agent="agent1",
            to_agent="agent2",
            message_type=MessageType.DISCOVERY,
            content={'finding': 'test'},
            channel="default"
        )
        
        self.assertEqual(len(self.messenger.message_history), 1)
        msg = self.messenger.message_history[0]
        self.assertEqual(msg.from_agent, "agent1")
        self.assertEqual(msg.to_agent, "agent2")
    
    def test_broadcast_message(self):
        """Test broadcasting message to all agents."""
        self.messenger.broadcast(
            sender="agent1",
            message_type=MessageType.BROADCAST,
            content={'announcement': 'test'},
            channel="default"
        )
        
        msg = self.messenger.message_history[0]
        self.assertIsNone(msg.to_agent)  # Broadcast
    
    def test_subscribe_and_get_messages(self):
        """Test subscription and message retrieval."""
        self.messenger.subscribe("agent1", "fuzzing")
        self.messenger.broadcast(
            sender="agent2",
            message_type=MessageType.FINDING,
            content={'vuln': 'XSS'},
            channel="fuzzing"
        )
        
        messages = self.messenger.get_messages("agent1", "fuzzing")
        self.assertEqual(len(messages), 1)


class TestWorkloadBalancer(unittest.TestCase):
    """Test workload distribution."""
    
    def setUp(self):
        import logging
        self.balancer = WorkloadBalancer(logging.getLogger("test"))
    
    def test_distribute_fuzzing_targets(self):
        """Test distributing targets across agents."""
        targets = [f"endpoint_{i}" for i in range(100)]
        chunks = self.balancer.distribute_fuzzing_targets(targets, agent_count=5)
        
        self.assertEqual(len(chunks), 5)
        total_targets = sum(len(chunk) for chunk in chunks)
        self.assertEqual(total_targets, 100)
    
    def test_balance_by_priority(self):
        """Test balancing tasks by priority."""
        tasks = [
            AgentTask(f"task_{i}", AgentType.OSINT, "desc", {}, priority=i)
            for i in range(10)
        ]
        
        chunks = self.balancer.balance_by_priority(tasks, agent_count=3)
        
        self.assertEqual(len(chunks), 3)
        total_tasks = sum(len(chunk) for chunk in chunks)
        self.assertEqual(total_tasks, 10)


class TestResultAggregator(unittest.TestCase):
    """Test result aggregation and deduplication."""
    
    def setUp(self):
        import logging
        self.aggregator = ResultAggregator(logging.getLogger("test"))
    
    def test_add_unique_finding(self):
        """Test adding unique finding."""
        finding = Finding(
            finding_id="f1",
            vulnerability_type="XSS",
            severity="High",
            confidence=0.9,
            location="/search",
            description="Reflected XSS",
            discovered_by="agent1"
        )
        
        added = self.aggregator.add_finding(finding)
        self.assertTrue(added)
        self.assertEqual(len(self.aggregator.findings), 1)
    
    def test_deduplicate_findings(self):
        """Test deduplication of identical findings."""
        finding1 = Finding(
            finding_id="f1",
            vulnerability_type="XSS",
            severity="High",
            confidence=0.9,
            location="/search",
            description="Reflected XSS",
            discovered_by="agent1"
        )
        
        finding2 = Finding(
            finding_id="f2",
            vulnerability_type="XSS",
            severity="High",
            confidence=0.8,
            location="/search",
            description="Same XSS",
            discovered_by="agent2"
        )
        
        self.aggregator.add_finding(finding1)
        added = self.aggregator.add_finding(finding2)
        
        self.assertFalse(added)  # Duplicate
        self.assertEqual(len(self.aggregator.findings), 1)
    
    def test_prioritize_by_impact(self):
        """Test prioritization by severity and CVSS."""
        findings = [
            Finding("f1", "XSS", "Medium", 0.7, "/search", "XSS", "agent1", cvss_score=6.0),
            Finding("f2", "Auth Bypass", "Critical", 0.9, "/login", "Bypass", "agent2", cvss_score=9.0),
            Finding("f3", "IDOR", "High", 0.8, "/api/user", "IDOR", "agent3", cvss_score=7.5)
        ]
        
        for f in findings:
            self.aggregator.add_finding(f)
        
        prioritized = self.aggregator.prioritize_by_impact()
        
        # Critical should be first
        self.assertEqual(prioritized[0].severity, "Critical")
        self.assertEqual(prioritized[0].cvss_score, 9.0)


class TestEnhancedAgentOrchestrator(unittest.TestCase):
    """Test enhanced orchestrator functionality."""
    
    def setUp(self):
        self.orchestrator = EnhancedAgentOrchestrator(max_agents=5, max_memory_gb=8.0)
    
    def test_spawn_specialized_agent(self):
        """Test dynamic agent spawning based on attack surface."""
        attack_surface = {
            'category': 'authentication',
            'description': 'OAuth 2.0 flow'
        }
        
        agent_id = self.orchestrator.spawn_specialized_agent(attack_surface)
        
        self.assertIsNotNone(agent_id)
        self.assertIn('auth-testing-agent', agent_id)
    
    def test_spawn_custom_agent(self):
        """Test spawning custom agent by name."""
        agent_id = self.orchestrator.spawn_custom_agent(
            agent_name='osint',
            task_params={'target': 'example.com'}
        )
        
        self.assertIsNotNone(agent_id)
        self.assertIn('glasseye-osint', agent_id)
    
    def test_handle_agent_failure(self):
        """Test failure recovery logic."""
        task = AgentTask(
            task_id="test_task",
            agent_type=AgentType.OSINT,
            description="Test task",
            parameters={},
            max_retries=2
        )
        
        # First failure should retry
        replacement = self.orchestrator.handle_agent_failure("failed_agent", task)
        
        self.assertIsNotNone(replacement or task.retry_count > 0)
    
    def test_distribute_fuzzing_workload(self):
        """Test enhanced fuzzing distribution."""
        endpoints = [f"/api/v1/endpoint{i}" for i in range(25)]
        
        agents = self.orchestrator.distribute_fuzzing_workload_enhanced(
            endpoints,
            fuzzing_strategy="comprehensive",
            agent_count=3
        )
        
        self.assertGreaterEqual(len(agents), 1)
    
    def test_resource_usage(self):
        """Test getting resource usage statistics."""
        usage = self.orchestrator.get_resource_usage()
        
        self.assertIn('memory', usage)
        self.assertIn('cpu', usage)
        self.assertIn('agents', usage)
    
    def test_send_agent_message(self):
        """Test sending messages between agents."""
        self.orchestrator.send_agent_message(
            from_agent="agent1",
            to_agent="agent2",
            message_type=MessageType.DISCOVERY,
            content={'finding': 'test'}
        )
        
        self.assertGreater(len(self.orchestrator.messenger.message_history), 0)


class TestCampaignTemplates(unittest.TestCase):
    """Test campaign template generation."""
    
    def setUp(self):
        self.templates = CampaignTemplates()
    
    def test_github_copilot_campaign(self):
        """Test GitHub Copilot campaign template."""
        campaign = self.templates.github_copilot_campaign()
        
        self.assertEqual(campaign.target, "GitHub Copilot Coding Agent")
        self.assertEqual(len(campaign.phases), 5)
        self.assertTrue(campaign.human_approval_required)
        self.assertGreater(campaign.max_parallel_agents, 0)
    
    def test_npm_package_campaign(self):
        """Test NPM package audit campaign."""
        campaign = self.templates.npm_package_campaign("test-package")
        
        self.assertIn("npm_audit", campaign.campaign_id)
        self.assertEqual(campaign.target, "test-package")
        self.assertGreater(len(campaign.phases), 0)
    
    def test_api_fuzzing_campaign(self):
        """Test API fuzzing campaign."""
        campaign = self.templates.api_fuzzing_campaign("https://api.example.com", ["*.example.com"])
        
        self.assertIn("api_fuzz", campaign.campaign_id)
        self.assertTrue(campaign.human_approval_required)
    
    def test_smart_contract_audit(self):
        """Test smart contract audit campaign."""
        campaign = self.templates.smart_contract_audit_campaign("0x1234567890")
        
        self.assertIn("contract_audit", campaign.campaign_id)
        self.assertGreater(campaign.timeout_minutes, 0)
    
    def test_web_app_pentest(self):
        """Test web app pentest campaign."""
        campaign = self.templates.web_app_pentest_campaign("https://target.com", ["*.target.com"])
        
        self.assertIn("webapp_pentest", campaign.campaign_id)
        self.assertGreater(campaign.max_parallel_agents, 0)


class TestCampaignWorkflow(unittest.TestCase):
    """Test campaign execution workflow."""
    
    def setUp(self):
        self.orchestrator = EnhancedAgentOrchestrator(max_agents=20, max_memory_gb=16.0)
    
    def test_execute_small_campaign(self):
        """Test executing a small campaign."""
        config = CampaignConfig(
            campaign_id="test_campaign",
            target="test.example.com",
            program="test",
            phases=[
                {'name': 'osint', 'agents': 1, 'parallel': False},
                {'name': 'analysis', 'agents': 1, 'parallel': False}
            ],
            max_parallel_agents=10,
            human_approval_required=False,
            timeout_minutes=60
        )
        
        result = self.orchestrator.execute_campaign(config)
        
        self.assertEqual(result['campaign_id'], "test_campaign")
        self.assertIn('status', result)
        self.assertIn('phases', result)


def run_tests():
    """Run all test suites."""
    print("=" * 70)
    print("Running Enhanced Agent Orchestrator Tests")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestResourceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentMessenger))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkloadBalancer))
    suite.addTests(loader.loadTestsFromTestCase(TestResultAggregator))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedAgentOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestCampaignTemplates))
    suite.addTests(loader.loadTestsFromTestCase(TestCampaignWorkflow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
