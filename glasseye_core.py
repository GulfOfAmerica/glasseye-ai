#!/usr/bin/env python3
"""
GlasseyeOS AI - Master Intelligence Engine
Autonomous reconnaissance planning and vulnerability hypothesis generation.

CRITICAL: Intelligence gathering only. Human approval required for exploitation.
"""

import logging
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import requests
from urllib.parse import urlparse

from compliance_enforcer import ComplianceEnforcer, Action, RiskLevel
from knowledge_base import KnowledgeBase, CVE, DisclosedBounty, Campaign


@dataclass
class Target:
    """Bug bounty target."""
    name: str
    base_url: str
    program_scope: List[str]
    out_of_scope: List[str]
    safe_harbor: Dict
    researcher_resources: List[str]


@dataclass
class VulnerabilityHypothesis:
    """Generated vulnerability hypothesis."""
    hypothesis_id: str
    target: str
    vulnerability_type: str
    confidence: float
    expected_bounty: int
    attack_pattern: str
    poc_template: str
    requires_approval: bool
    risk_level: RiskLevel


@dataclass
class ReconnaissancePlan:
    """Autonomous reconnaissance plan."""
    plan_id: str
    target: str
    phases: List[Dict]
    estimated_duration: str
    tools_required: List[str]
    compliance_approved: bool


class GlasseyeAI:
    """
    Master Intelligence Engine for bug bounty research.
    
    Capabilities:
    - Autonomous reconnaissance planning
    - CVE feed monitoring
    - Attack surface analysis
    - Vulnerability hypothesis generation
    - Campaign orchestration with human approval gates
    """
    
    def __init__(self, config_path: str = "config/glasseye_config.yaml"):
        self.config_path = config_path
        self.logger = self._setup_logging()
        self.kb = KnowledgeBase()
        self.compliance = ComplianceEnforcer()
        
        # Known vulnerability patterns (learned from Copilot CVEs)
        self.known_patterns = self._load_known_patterns()
        
    def _setup_logging(self) -> logging.Logger:
        """Configure AI engine logging."""
        logger = logging.getLogger("GlasseyeAI")
        logger.setLevel(logging.INFO)
        
        fh = logging.FileHandler("logs/glasseye_ai.log")
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _load_known_patterns(self) -> Dict:
        """Load known vulnerability patterns from Copilot CVEs."""
        return {
            "prompt_injection": {
                "description": "System prompt leakage via crafted user input",
                "detection": "Test with prompt boundary markers and meta-instructions",
                "cvss_score": 6.5,
                "avg_bounty": 2500
            },
            "path_traversal": {
                "description": "File access outside intended directory via path manipulation",
                "detection": "Test file operations with ../ sequences and absolute paths",
                "cvss_score": 7.5,
                "avg_bounty": 4000
            },
            "code_execution": {
                "description": "Arbitrary code execution via unsafe eval or command injection",
                "detection": "Test code interpretation endpoints with system commands",
                "cvss_score": 9.0,
                "avg_bounty": 7500
            },
            "authentication_bypass": {
                "description": "Access control bypass via session manipulation",
                "detection": "Test session handling with modified tokens and IDs",
                "cvss_score": 8.5,
                "avg_bounty": 5000
            }
        }
    
    def analyze_target(self, target: Target) -> Dict:
        """
        Comprehensive target analysis.
        
        Steps:
        1. Passive reconnaissance (safe, no approval needed)
        2. Technology stack identification
        3. Attack surface mapping
        4. Vulnerability hypothesis generation
        
        Returns analysis report with compliance status.
        """
        self.logger.info(f"Starting target analysis: {target.name}")
        
        analysis = {
            "target": target.name,
            "started": datetime.utcnow().isoformat(),
            "attack_surfaces": [],
            "hypotheses": [],
            "recommended_tools": [],
            "compliance_status": "pending"
        }
        
        # Step 1: Passive reconnaissance (compliance check)
        recon_action = Action(
            action_type="passive_reconnaissance",
            target=target.base_url,
            description=f"Passive reconnaissance on {target.base_url}",
            risk_level=RiskLevel.SAFE,
            requires_human_approval=False,
            scope_verified=True
        )
        
        approved, reason = self.compliance.approve_action(
            recon_action, target.program_scope, target.researcher_resources
        )
        
        if not approved:
            analysis["compliance_status"] = f"BLOCKED: {reason}"
            self.logger.warning(f"Target analysis blocked: {reason}")
            return analysis
        
        # Step 2: Technology stack identification
        tech_stack = self._identify_technology_stack(target.base_url)
        analysis["technology_stack"] = tech_stack
        
        # Step 3: Attack surface mapping
        attack_surfaces = self._map_attack_surface(target)
        analysis["attack_surfaces"] = attack_surfaces
        
        # Step 4: Vulnerability hypothesis generation
        hypotheses = self.generate_vulnerability_hypotheses(attack_surfaces, target)
        analysis["hypotheses"] = [asdict(h) for h in hypotheses]
        
        # Step 5: Recommend tools
        analysis["recommended_tools"] = self._recommend_tools(hypotheses)
        
        analysis["compliance_status"] = "approved"
        analysis["completed"] = datetime.utcnow().isoformat()
        
        self.logger.info(f"Target analysis complete: {len(hypotheses)} hypotheses generated")
        
        return analysis
    
    def _identify_technology_stack(self, url: str) -> Dict:
        """
        Passive technology identification.
        
        Analyzes:
        - HTTP headers
        - HTML meta tags
        - JavaScript frameworks
        - Error pages
        """
        self.logger.info(f"Identifying technology stack for: {url}")
        
        tech_stack = {
            "server": "Unknown",
            "framework": "Unknown",
            "languages": [],
            "libraries": []
        }
        
        try:
            # Simple HEAD request for headers (passive)
            response = requests.head(url, timeout=5, allow_redirects=True)
            
            # Analyze headers
            headers = response.headers
            if 'Server' in headers:
                tech_stack["server"] = headers['Server']
            
            if 'X-Powered-By' in headers:
                tech_stack["framework"] = headers['X-Powered-By']
            
            # Common framework detection patterns
            if 'X-AspNet-Version' in headers:
                tech_stack["framework"] = "ASP.NET"
                tech_stack["languages"].append("C#")
            
            if 'X-Rails-' in str(headers):
                tech_stack["framework"] = "Ruby on Rails"
                tech_stack["languages"].append("Ruby")
            
        except Exception as e:
            self.logger.warning(f"Technology identification failed: {e}")
        
        return tech_stack
    
    def _map_attack_surface(self, target: Target) -> List[Dict]:
        """
        Map attack surface from public documentation.
        
        Discovers:
        - API endpoints
        - Authentication mechanisms
        - Input parameters
        - File upload capabilities
        """
        self.logger.info(f"Mapping attack surface for: {target.name}")
        
        surfaces = []
        
        # Example: Common endpoints to test
        common_endpoints = [
            "/api/v1/",
            "/graphql",
            "/api/",
            "/rest/",
            "/api/users",
            "/api/auth",
            "/api/session"
        ]
        
        for endpoint in common_endpoints:
            full_url = target.base_url + endpoint
            
            # Check if in scope
            if self.compliance.check_scope_boundaries(full_url, target.program_scope):
                surface = {
                    "endpoint": endpoint,
                    "url": full_url,
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "authentication": "Unknown",
                    "potential_vulnerabilities": []
                }
                
                # Analyze potential vulnerabilities based on endpoint
                if "auth" in endpoint or "login" in endpoint:
                    surface["potential_vulnerabilities"].extend([
                        "authentication_bypass",
                        "credential_stuffing",
                        "session_fixation"
                    ])
                
                if "user" in endpoint:
                    surface["potential_vulnerabilities"].extend([
                        "IDOR",
                        "mass_assignment",
                        "privilege_escalation"
                    ])
                
                if "api" in endpoint:
                    surface["potential_vulnerabilities"].extend([
                        "API_abuse",
                        "rate_limiting_bypass",
                        "parameter_pollution"
                    ])
                
                surfaces.append(surface)
                
                # Store in knowledge base
                self.kb.add_attack_surface(
                    target=target.name,
                    endpoint=endpoint,
                    method="GET,POST",
                    authentication_required=True,
                    parameters={},
                    potential_vulnerabilities=surface["potential_vulnerabilities"]
                )
        
        return surfaces
    
    def generate_vulnerability_hypotheses(self, attack_surfaces: List[Dict], 
                                         target: Target) -> List[VulnerabilityHypothesis]:
        """
        Generate testable vulnerability hypotheses based on attack surfaces.
        
        Uses:
        - Known patterns from Copilot CVEs
        - Learned patterns from knowledge base
        - Attack surface analysis
        
        Returns ranked list of hypotheses.
        """
        self.logger.info(f"Generating vulnerability hypotheses for {len(attack_surfaces)} surfaces")
        
        hypotheses = []
        
        for surface in attack_surfaces:
            endpoint = surface["endpoint"]
            potential_vulns = surface["potential_vulnerabilities"]
            
            for vuln_type in potential_vulns:
                # Check if we have a known pattern
                if vuln_type in self.known_patterns:
                    pattern = self.known_patterns[vuln_type]
                    
                    hypothesis = VulnerabilityHypothesis(
                        hypothesis_id=self._generate_hypothesis_id(endpoint, vuln_type),
                        target=endpoint,
                        vulnerability_type=vuln_type,
                        confidence=0.6,  # Medium confidence from pattern matching
                        expected_bounty=pattern["avg_bounty"],
                        attack_pattern=pattern["description"],
                        poc_template=self._generate_poc_template(vuln_type, endpoint),
                        requires_approval=True,
                        risk_level=self._classify_risk_level(vuln_type)
                    )
                    
                    hypotheses.append(hypothesis)
        
        # Rank by expected bounty and confidence
        hypotheses.sort(key=lambda h: h.expected_bounty * h.confidence, reverse=True)
        
        self.logger.info(f"Generated {len(hypotheses)} vulnerability hypotheses")
        
        return hypotheses
    
    def _generate_hypothesis_id(self, endpoint: str, vuln_type: str) -> str:
        """Generate unique hypothesis ID."""
        content = f"{endpoint}_{vuln_type}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _classify_risk_level(self, vuln_type: str) -> RiskLevel:
        """Classify risk level based on vulnerability type."""
        high_risk = ["code_execution", "authentication_bypass", "path_traversal"]
        medium_risk = ["IDOR", "privilege_escalation", "session_fixation"]
        
        if vuln_type in high_risk:
            return RiskLevel.HIGH
        elif vuln_type in medium_risk:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_poc_template(self, vuln_type: str, endpoint: str) -> str:
        """Generate PoC template for vulnerability type."""
        templates = {
            "IDOR": f"""
# IDOR Test for {endpoint}
# 1. Create two researcher-owned test accounts
# 2. Authenticate as User A, note resource ID
# 3. Authenticate as User B
# 4. Attempt to access User A's resource
# 5. If successful, IDOR vulnerability confirmed

curl -X GET '{endpoint}/resource/USER_A_ID' \\
  -H 'Authorization: Bearer USER_B_TOKEN'
""",
            "authentication_bypass": f"""
# Authentication Bypass Test for {endpoint}
# Test JWT algorithm confusion
# 1. Capture valid JWT token
# 2. Modify algorithm to 'none'
# 3. Remove signature
# 4. Attempt access

# Example JWT manipulation
import jwt
token = jwt.decode(original_token, options={{"verify_signature": False}})
token['alg'] = 'none'
bypass_token = jwt.encode(token, key='', algorithm='none')
""",
            "path_traversal": f"""
# Path Traversal Test for {endpoint}
# Test file access outside intended directory
# 1. Identify file parameter
# 2. Test with ../ sequences
# 3. Test with absolute paths

curl -X GET '{endpoint}?file=../../../etc/passwd'
curl -X GET '{endpoint}?file=/etc/passwd'
""",
        }
        
        return templates.get(vuln_type, f"# Manual testing required for {vuln_type}")
    
    def _recommend_tools(self, hypotheses: List[VulnerabilityHypothesis]) -> List[str]:
        """Recommend tools based on hypotheses."""
        tools = set()
        
        for h in hypotheses:
            if h.vulnerability_type == "IDOR":
                tools.add("Burp Suite - Autorize extension")
            elif h.vulnerability_type in ["authentication_bypass", "session_fixation"]:
                tools.add("JWT_Tool")
                tools.add("Burp Suite - Session handling")
            elif h.vulnerability_type == "path_traversal":
                tools.add("DotDotPwn")
            elif "API" in h.vulnerability_type:
                tools.add("Postman")
                tools.add("Custom API fuzzer")
        
        return list(tools)
    
    def generate_reconnaissance_plan(self, target: Target) -> ReconnaissancePlan:
        """
        Generate autonomous reconnaissance plan.
        
        Phases:
        1. Passive OSINT (no approval needed)
        2. Active scanning (requires approval)
        3. Vulnerability testing (requires approval per test)
        """
        self.logger.info(f"Generating reconnaissance plan for: {target.name}")
        
        phases = [
            {
                "phase": 1,
                "name": "Passive OSINT",
                "actions": [
                    "DNS enumeration (passive)",
                    "Subdomain discovery (certificate transparency)",
                    "Public repository search (GitHub, GitLab)",
                    "Technology stack identification",
                    "Historical data (Wayback Machine)"
                ],
                "risk_level": "SAFE",
                "approval_required": False,
                "estimated_duration": "2-4 hours"
            },
            {
                "phase": 2,
                "name": "Active Scanning",
                "actions": [
                    "Port scanning (approved ranges only)",
                    "Service enumeration",
                    "Web application crawling",
                    "API endpoint discovery",
                    "Authentication mechanism analysis"
                ],
                "risk_level": "LOW",
                "approval_required": True,
                "estimated_duration": "4-8 hours"
            },
            {
                "phase": 3,
                "name": "Vulnerability Testing",
                "actions": [
                    "Test hypotheses (one at a time)",
                    "Custom tool generation",
                    "Proof-of-concept development",
                    "Finding validation"
                ],
                "risk_level": "HIGH",
                "approval_required": True,
                "estimated_duration": "Ongoing"
            }
        ]
        
        plan = ReconnaissancePlan(
            plan_id=f"recon_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            target=target.name,
            phases=phases,
            estimated_duration="1-2 weeks",
            tools_required=[
                "Amass (subdomain enumeration)",
                "Nmap (port scanning)",
                "Burp Suite (web testing)",
                "Custom tools (auto-generated)"
            ],
            compliance_approved=False  # Requires phase-by-phase approval
        )
        
        self.logger.info(f"Reconnaissance plan generated: {plan.plan_id}")
        
        return plan
    
    def monitor_cve_feeds(self, keywords: List[str] = None) -> List[CVE]:
        """
        Monitor CVE feeds for relevant vulnerabilities.
        
        Sources:
        - NVD (National Vulnerability Database)
        - GitHub Security Advisories
        - HackerOne disclosed reports
        
        Filters by keywords if provided.
        """
        if keywords is None:
            keywords = ["Copilot", "AI", "LLM", "GPT", "authentication", "API"]
        
        self.logger.info(f"Monitoring CVE feeds with keywords: {keywords}")
        
        discovered_cves = []
        
        # In production, would query NVD API
        # For demo, return known Copilot-related patterns
        
        # Example: Simulated CVE discovery
        example_cves = [
            CVE(
                cve_id="CVE-2024-COPILOT-1",
                cvss_score=7.5,
                attack_vector="Network",
                vulnerability_type="Prompt Injection",
                affected_products="GitHub Copilot",
                learned_pattern="System prompt leakage via multi-turn conversation manipulation"
            ),
            CVE(
                cve_id="CVE-2024-COPILOT-2",
                cvss_score=8.5,
                attack_vector="Network",
                vulnerability_type="Path Traversal",
                affected_products="GitHub Copilot Workspace",
                learned_pattern="File access outside workspace via symbolic link exploitation"
            )
        ]
        
        for cve in example_cves:
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in cve.affected_products.lower() or \
                   keyword.lower() in cve.vulnerability_type.lower():
                    discovered_cves.append(cve)
                    self.kb.add_cve(cve)
                    break
        
        self.logger.info(f"Discovered {len(discovered_cves)} relevant CVEs")
        
        return discovered_cves
    
    def learn_from_disclosure(self, report_data: Dict) -> str:
        """
        Learn from HackerOne disclosed report.
        
        Extracts:
        - Attack pattern
        - Vulnerability type
        - Bounty amount
        - Lessons learned
        
        Updates knowledge base with pattern.
        """
        self.logger.info(f"Learning from disclosure: {report_data.get('title', 'Unknown')}")
        
        # Add to knowledge base
        bounty = DisclosedBounty(
            report_id=report_data.get('report_id', 'unknown'),
            program=report_data.get('program', 'Unknown'),
            title=report_data['title'],
            severity=report_data.get('severity', 'Unknown'),
            bounty_amount=report_data.get('bounty', 0),
            attack_pattern=report_data.get('attack_pattern', ''),
            lessons_learned=report_data.get('lessons', '')
        )
        
        self.kb.add_disclosed_bounty(bounty)
        
        # Extract and add vulnerability pattern
        pattern_id = self.kb.add_vulnerability_pattern(
            pattern_name=report_data['title'],
            description=report_data.get('attack_pattern', ''),
            detection_method=report_data.get('detection', 'Manual testing'),
            exploitation_template=report_data.get('poc', ''),
            learned_from=f"HackerOne Report {bounty.report_id}",
            success_rate=0.5,  # Initial estimate
            avg_bounty=bounty.bounty_amount
        )
        
        self.logger.info(f"Pattern learned: {pattern_id}")
        
        return pattern_id
    
    def request_human_approval(self, action: Action, risk_assessment: Dict) -> bool:
        """
        Request human approval for high-risk action.
        
        Displays:
        - Action details
        - Risk assessment
        - Compliance status
        - Expected outcome
        
        Returns True if approved (in production, would wait for human input).
        """
        self.logger.warning(f"HUMAN APPROVAL REQUIRED: {action.action_type}")
        
        print("\n" + "="*60)
        print("🚨 HUMAN APPROVAL REQUIRED 🚨")
        print("="*60)
        print(f"\nAction: {action.action_type}")
        print(f"Target: {action.target}")
        print(f"Description: {action.description}")
        print(f"Risk Level: {action.risk_level.value.upper()}")
        print(f"\nRisk Assessment:")
        for key, value in risk_assessment.items():
            print(f"  {key}: {value}")
        print("\n" + "="*60)
        print("In production: This would pause and wait for human approval.")
        print("For demo: Simulating approval denial (SAFE DEFAULT)")
        print("="*60 + "\n")
        
        # SAFE DEFAULT: Return False (deny) in demo
        # In production, would wait for actual human input
        return False
    
    def close(self):
        """Cleanup resources."""
        self.kb.close()


if __name__ == "__main__":
    # Demo GlasseyeAI
    print("=== GlasseyeOS AI - Intelligence Engine Demo ===\n")
    
    ai = GlasseyeAI()
    
    # Define target
    target = Target(
        name="GitHub Copilot",
        base_url="https://copilot.github.com",
        program_scope=[
            "*.github.com",
            "copilot.github.com",
            "api.github.com"
        ],
        out_of_scope=[
            "github.com/blog",
            "gist.github.com"
        ],
        safe_harbor={
            "researcher_owned_accounts": True,
            "no_dos": True,
            "no_social_engineering": True
        },
        researcher_resources=[
            "researcher_test_account@example.com",
            "researcher_api_key_123"
        ]
    )
    
    # Test 1: CVE monitoring
    print("\n1. Monitoring CVE feeds...")
    cves = ai.monitor_cve_feeds(keywords=["Copilot", "AI"])
    print(f"   Found {len(cves)} relevant CVEs\n")
    
    # Test 2: Generate reconnaissance plan
    print("2. Generating reconnaissance plan...")
    recon_plan = ai.generate_reconnaissance_plan(target)
    print(f"   Plan ID: {recon_plan.plan_id}")
    print(f"   Phases: {len(recon_plan.phases)}")
    print(f"   Estimated duration: {recon_plan.estimated_duration}\n")
    
    # Test 3: Target analysis
    print("3. Analyzing target...")
    analysis = ai.analyze_target(target)
    print(f"   Compliance: {analysis['compliance_status']}")
    print(f"   Attack surfaces: {len(analysis['attack_surfaces'])}")
    print(f"   Hypotheses: {len(analysis['hypotheses'])}")
    print(f"   Recommended tools: {len(analysis['recommended_tools'])}\n")
    
    # Test 4: Show top hypothesis
    if analysis['hypotheses']:
        top_hypothesis = analysis['hypotheses'][0]
        print("4. Top vulnerability hypothesis:")
        print(f"   Type: {top_hypothesis['vulnerability_type']}")
        print(f"   Confidence: {top_hypothesis['confidence']}")
        print(f"   Expected bounty: ${top_hypothesis['expected_bounty']}")
        print(f"   Requires approval: {top_hypothesis['requires_approval']}\n")
    
    # Test 5: Human approval simulation
    if analysis['hypotheses']:
        hypothesis = analysis['hypotheses'][0]
        action = Action(
            action_type="vulnerability_testing",
            target=hypothesis['target'],
            description=f"Test {hypothesis['vulnerability_type']} on {hypothesis['target']}",
            risk_level=RiskLevel[hypothesis['risk_level']],
            requires_human_approval=True,
            scope_verified=True,
            researcher_owned=True
        )
        
        risk_assessment = {
            "Vulnerability Type": hypothesis['vulnerability_type'],
            "Confidence": f"{hypothesis['confidence'] * 100}%",
            "Expected Impact": "High",
            "Data at Risk": "None (researcher-owned resources)",
            "Compliance Status": "Approved"
        }
        
        approved = ai.request_human_approval(action, risk_assessment)
        print(f"5. Approval result: {'APPROVED' if approved else 'DENIED (safe default)'}\n")
    
    # Show knowledge base stats
    stats = ai.kb.get_stats()
    print("Knowledge Base Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✓ GlasseyeAI demo complete")
    
    ai.close()
