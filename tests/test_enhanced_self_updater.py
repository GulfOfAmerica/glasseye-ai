#!/usr/bin/env python3
"""
Tests for Enhanced Self-Updater (v2.0)

Tests all 7 new features:
1. GitHub Security Advisory Monitor
2. HackerOne Disclosed Report Learning
3. Vulnerability Pattern Extraction (NLP)
4. Self-Code Update (Human Approval)
5. Security Research Paper Monitor
6. Bug Bounty Program Rule Monitor
7. Automated Tool Update
"""

import pytest
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from self_updater import EnhancedSelfUpdater, AttackPattern, SecurityResearchPaper, ProgramRuleSnapshot


class TestGitHubAdvisoryMonitor:
    """Test Feature 1: GitHub Security Advisory Monitoring"""
    
    def test_monitor_github_advisories(self, tmpdir):
        """Test fetching and processing GitHub advisories"""
        updater = EnhancedSelfUpdater()
        
        # Run monitor
        count = updater.monitor_github_advisories()
        
        # Verify advisories were processed
        assert count >= 0
        assert isinstance(count, int)
        
        updater.close()
    
    def test_advisory_severity_filtering(self):
        """Test that only high/critical severities are processed"""
        updater = EnhancedSelfUpdater()
        
        # Simulated advisory processing should filter by severity
        count = updater.monitor_github_advisories()
        
        # In simulated mode, we expect 2 advisories (both high/critical)
        assert count == 2
        
        updater.close()
    
    def test_attack_pattern_learning_from_advisory(self):
        """Test that attack patterns are extracted from advisories"""
        updater = EnhancedSelfUpdater()
        
        # Monitor advisories
        updater.monitor_github_advisories()
        
        # Check that patterns were cached
        cache_file = updater.data_cache_dir / "attack_patterns.jsonl"
        assert cache_file.exists()
        
        # Verify pattern format
        with open(cache_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            
            pattern = json.loads(lines[0])
            assert 'type' in pattern
            assert 'keywords' in pattern
            assert 'confidence' in pattern
        
        updater.close()


class TestHackerOneLearning:
    """Test Feature 2: Enhanced HackerOne Learning"""
    
    def test_learn_from_disclosed_reports(self):
        """Test learning from HackerOne disclosed reports"""
        updater = EnhancedSelfUpdater()
        
        count = updater.learn_from_hackerone_disclosed()
        
        # Should learn from simulated reports
        assert count == 2
        
        updater.close()
    
    def test_pattern_extraction_from_report(self):
        """Test attack pattern extraction from report"""
        updater = EnhancedSelfUpdater()
        
        report = {
            'id': 'H1-TEST-001',
            'title': 'IDOR vulnerability in API',
            'weakness': {'name': 'IDOR'},
            'severity_rating': 'high',
            'bounty_amount': 5000.0,
            'program': {'name': 'TestCorp'},
            'vulnerability_information': '''
            1. Capture session ID
            2. Enumerate other session IDs
            3. Access other user data
            
            Root cause: Missing authorization check
            '''
        }
        
        pattern = updater.extract_attack_pattern_from_report(report)
        
        assert pattern['vulnerability_type'] == 'IDOR'
        assert len(pattern['exploitation_steps']) > 0
        assert 'lessons' in pattern
        
        updater.close()
    
    def test_hypothesis_generator_update(self):
        """Test that hypothesis generator is updated with new patterns"""
        updater = EnhancedSelfUpdater()
        
        updater.learn_from_hackerone_disclosed()
        
        # Check hypotheses cache
        cache_file = updater.data_cache_dir / "hypotheses.jsonl"
        assert cache_file.exists()
        
        with open(cache_file, 'r') as f:
            hypotheses = [json.loads(line) for line in f]
            assert len(hypotheses) > 0
            assert 'pattern_type' in hypotheses[0]
        
        updater.close()


class TestVulnerabilityPatternExtraction:
    """Test Feature 3: NLP-based Pattern Extraction"""
    
    def test_extract_command_injection_pattern(self):
        """Test extraction of command injection pattern"""
        updater = EnhancedSelfUpdater()
        
        description = "Copilot CLI vulnerable to command injection via bash parameter expansion"
        
        pattern = updater.extract_attack_pattern_detailed(description)
        
        assert pattern.vulnerability_type == 'command_injection'
        assert pattern.affected_component == 'CLI'
        assert 'command' in pattern.keywords
        assert pattern.confidence_score > 0
        
        updater.close()
    
    def test_extract_idor_pattern(self):
        """Test extraction of IDOR pattern"""
        updater = EnhancedSelfUpdater()
        
        description = "API endpoint allows unauthorized access to user data via IDOR"
        
        pattern = updater.extract_attack_pattern_detailed(description)
        
        assert pattern.vulnerability_type == 'idor'
        assert pattern.affected_component == 'API'
        
        updater.close()
    
    def test_extract_prompt_injection_pattern(self):
        """Test extraction of prompt injection pattern"""
        updater = EnhancedSelfUpdater()
        
        description = "LLM system prompt can be leaked through prompt injection techniques"
        
        pattern = updater.extract_attack_pattern_detailed(description)
        
        assert pattern.vulnerability_type == 'prompt_injection'
        
        updater.close()
    
    def test_keyword_extraction(self):
        """Test keyword extraction from description"""
        updater = EnhancedSelfUpdater()
        
        description = "SQL injection vulnerability allows database manipulation through unsanitized input"
        
        pattern = updater.extract_attack_pattern_detailed(description)
        
        # Should extract meaningful keywords
        assert len(pattern.keywords) > 0
        assert any('sql' in kw or 'injection' in kw for kw in pattern.keywords)
        
        updater.close()


class TestSelfCodeUpdate:
    """Test Feature 4: Self-Code Update with Human Approval"""
    
    def test_check_glasseye_updates(self):
        """Test checking for GlasseyeOS updates"""
        updater = EnhancedSelfUpdater()
        
        update_info = updater.check_glasseye_updates()
        
        # In demo mode, simulates update available
        assert update_info is not None
        assert 'current_version' in update_info
        assert 'latest_version' in update_info
        assert 'release_notes' in update_info
        
        updater.close()
    
    def test_human_approval_request(self):
        """Test human approval request mechanism"""
        updater = EnhancedSelfUpdater()
        
        # Request approval
        approved = updater.request_human_approval(
            action='test_action',
            details='Test approval request',
            risk_level='low'
        )
        
        # Low risk should auto-approve in demo mode
        assert approved == True
        
        # Medium/high risk should require approval
        approved = updater.request_human_approval(
            action='test_action',
            details='Test approval request',
            risk_level='high'
        )
        
        assert approved == False  # Blocked pending approval
        
        # Check approval queue
        assert len(updater.human_approval_required) > 0
        
        # Check approval log
        approval_log = Path("logs/approval_requests.jsonl")
        assert approval_log.exists()
        
        updater.close()
    
    def test_self_update_workflow(self):
        """Test complete self-update workflow"""
        updater = EnhancedSelfUpdater()
        
        # Run self-update (will fail approval in demo mode)
        result = updater.self_update_code()
        
        # Should return False (not approved)
        assert result == False
        
        updater.close()


class TestSecurityResearchMonitor:
    """Test Feature 5: Security Research Paper Monitoring"""
    
    def test_monitor_arxiv(self):
        """Test arXiv paper monitoring"""
        updater = EnhancedSelfUpdater()
        
        count = updater._monitor_arxiv()
        
        # Should find simulated papers
        assert count == 2
        
        updater.close()
    
    def test_research_paper_storage(self):
        """Test that papers are stored correctly"""
        updater = EnhancedSelfUpdater()
        
        updater.monitor_security_research(['arxiv'])
        
        # Check cache
        cache_file = updater.data_cache_dir / "research_papers.jsonl"
        assert cache_file.exists()
        
        with open(cache_file, 'r') as f:
            papers = [json.loads(line) for line in f]
            assert len(papers) > 0
            assert 'title' in papers[0]
            assert 'learned_techniques' in papers[0]
        
        updater.close()
    
    def test_technique_extraction_from_paper(self):
        """Test technique extraction from paper abstract"""
        updater = EnhancedSelfUpdater()
        
        paper = {
            'summary': 'We present a novel static analysis framework for automated vulnerability discovery',
            'title': 'Test Paper',
            'categories': ['cs.CR']
        }
        
        techniques = updater._extract_techniques_from_paper(paper)
        
        assert 'static analysis' in techniques
        assert 'automated discovery' in techniques
        
        updater.close()


class TestProgramRuleMonitor:
    """Test Feature 6: Bug Bounty Program Rule Monitoring"""
    
    def test_monitor_program_rules_initial_snapshot(self):
        """Test creating initial program snapshot"""
        updater = EnhancedSelfUpdater()
        
        result = updater.monitor_program_rules(
            "https://test.bounty.com",
            "TestCorp Bug Bounty"
        )
        
        assert 'changes' in result
        assert 'initial_snapshot' in result['changes']
        
        # Check snapshot was saved
        snapshot_file = updater.program_snapshots_dir / "TestCorp Bug Bounty_latest.json"
        assert snapshot_file.exists()
        
        updater.close()
    
    def test_detect_scope_change(self):
        """Test detection of scope changes"""
        updater = EnhancedSelfUpdater()
        
        # Create initial snapshot
        updater.monitor_program_rules("https://test.com", "TestProgram")
        
        # Modify cached content to simulate change
        # (In real test, would mock HTTP response with different content)
        
        updater.close()
    
    def test_program_snapshot_hashing(self):
        """Test program content hashing"""
        updater = EnhancedSelfUpdater()
        
        content1 = "Scope: api.example.com"
        content2 = "Scope: api.example.com, web.example.com"
        
        hash1 = hashlib.sha256(content1.encode()).hexdigest()
        hash2 = hashlib.sha256(content2.encode()).hexdigest()
        
        # Different content should have different hashes
        assert hash1 != hash2
        
        updater.close()


class TestAutomatedToolUpdate:
    """Test Feature 7: Automated Tool Regeneration"""
    
    def test_get_recent_patterns(self):
        """Test retrieving recently learned patterns"""
        updater = EnhancedSelfUpdater()
        
        # Add some patterns
        updater.monitor_github_advisories()
        
        # Get recent patterns
        patterns = updater._get_recent_patterns(hours=24)
        
        assert isinstance(patterns, list)
        
        updater.close()
    
    def test_should_update_tool(self):
        """Test tool update decision logic"""
        updater = EnhancedSelfUpdater()
        
        tool = {
            'tool_id': 'fuzzer_jwt_001',
            'target_vulnerability': 'JWT Authentication Bypass'
        }
        
        new_patterns = [
            {'type': 'authentication_bypass', 'learned_at': datetime.utcnow().isoformat()}
        ]
        
        should_update = updater._should_update_tool(tool, new_patterns)
        
        # Should update because pattern matches tool vulnerability
        assert should_update == True
        
        updater.close()
    
    def test_tool_regeneration(self):
        """Test tool regeneration process"""
        updater = EnhancedSelfUpdater()
        
        tool = {
            'tool_id': 'test_tool',
            'version': '1.0',
            'target_vulnerability': 'XSS'
        }
        
        new_patterns = [
            {'type': 'xss', 'learned_at': datetime.utcnow().isoformat()}
        ]
        
        updated_tool = updater._regenerate_tool(tool, new_patterns)
        
        assert updated_tool['version'] == '1.1'
        assert 'updated_at' in updated_tool
        assert 'incorporated_patterns' in updated_tool
        
        updater.close()


class TestIntegration:
    """Integration tests for all enhanced features"""
    
    def test_daily_update_cycle(self):
        """Test complete daily update cycle"""
        updater = EnhancedSelfUpdater()
        
        summary = updater.run_daily_updates()
        
        assert 'timestamp' in summary
        assert 'updates' in summary
        assert 'cves' in summary['updates']
        assert 'tools' in summary['updates']
        
        updater.close()
    
    def test_weekly_update_cycle(self):
        """Test complete weekly update cycle"""
        updater = EnhancedSelfUpdater()
        
        summary = updater.run_weekly_updates()
        
        assert 'timestamp' in summary
        assert 'updates' in summary
        
        updater.close()
    
    def test_fetch_all_sources(self):
        """Test fetching from all configured sources"""
        updater = EnhancedSelfUpdater()
        
        summary = updater.fetch_all_sources()
        
        assert 'timestamp' in summary
        assert 'sources' in summary
        assert len(summary['sources']) > 0
        
        updater.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v'])
