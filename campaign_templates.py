#!/usr/bin/env python3
"""
Campaign Templates for Bug Bounty Research

Pre-configured campaign workflows for common bounty hunting scenarios.
"""

from agent_orchestrator import CampaignConfig


class CampaignTemplates:
    """Pre-built campaign templates."""
    
    @staticmethod
    def github_copilot_campaign(target: str = "GitHub Copilot Coding Agent") -> CampaignConfig:
        """
        GitHub Copilot bug bounty campaign.
        
        Phases:
        1. OSINT (3 parallel agents)
        2. Attack surface mapping (2 agents)
        3. Hypothesis generation (1 agent)
        4. PoC validation (5 agents, human approval required)
        5. Evidence collection (2 agents)
        6. Report generation (1 agent)
        """
        return CampaignConfig(
            campaign_id="github_copilot_2026",
            target=target,
            program="github-bug-bounty",
            phases=[
                {
                    'name': 'osint',
                    'agents': 3,
                    'parallel': True,
                    'description': 'Passive reconnaissance'
                },
                {
                    'name': 'analysis',
                    'agents': 2,
                    'parallel': True,
                    'description': 'Attack surface mapping'
                },
                {
                    'name': 'hypothesis',
                    'agents': 1,
                    'parallel': False,
                    'description': 'Vulnerability hypothesis generation'
                },
                {
                    'name': 'testing',
                    'agents': 5,
                    'parallel': True,
                    'human_approval': True,
                    'description': 'PoC development and validation'
                },
                {
                    'name': 'documentation',
                    'agents': 2,
                    'parallel': True,
                    'description': 'Evidence collection and report generation'
                }
            ],
            max_parallel_agents=15,
            human_approval_required=True,
            timeout_minutes=240,
            resource_limits={
                'max_memory_gb': 16.0,
                'max_cpu_percent': 80.0
            }
        )
    
    @staticmethod
    def npm_package_campaign(package_name: str) -> CampaignConfig:
        """
        NPM package security audit campaign.
        
        Focus on dependency analysis, supply chain attacks, and package vulnerabilities.
        """
        return CampaignConfig(
            campaign_id=f"npm_audit_{package_name.replace('/', '_')}",
            target=package_name,
            program="npm-security",
            phases=[
                {
                    'name': 'osint',
                    'agents': 2,
                    'parallel': True,
                    'description': 'Package metadata and dependency tree analysis'
                },
                {
                    'name': 'analysis',
                    'agents': 3,
                    'parallel': True,
                    'description': 'Static analysis and vulnerability scanning'
                },
                {
                    'name': 'testing',
                    'agents': 2,
                    'parallel': True,
                    'human_approval': False,  # Automated testing safe for packages
                    'description': 'Automated security testing'
                },
                {
                    'name': 'documentation',
                    'agents': 1,
                    'parallel': False,
                    'description': 'Generate security report'
                }
            ],
            max_parallel_agents=10,
            human_approval_required=False,
            timeout_minutes=120,
            resource_limits={
                'max_memory_gb': 8.0,
                'max_cpu_percent': 70.0
            }
        )
    
    @staticmethod
    def api_fuzzing_campaign(api_base_url: str, scope: list) -> CampaignConfig:
        """
        API fuzzing campaign for web services.
        
        Comprehensive API endpoint testing and fuzzing.
        """
        return CampaignConfig(
            campaign_id=f"api_fuzz_{api_base_url.replace('https://', '').replace('http://', '')}",
            target=api_base_url,
            program="api-security",
            phases=[
                {
                    'name': 'osint',
                    'agents': 2,
                    'parallel': True,
                    'description': 'API endpoint discovery'
                },
                {
                    'name': 'analysis',
                    'agents': 1,
                    'parallel': False,
                    'description': 'OpenAPI/Swagger analysis'
                },
                {
                    'name': 'testing',
                    'agents': 10,
                    'parallel': True,
                    'human_approval': True,
                    'description': 'Parallel API fuzzing'
                },
                {
                    'name': 'documentation',
                    'agents': 1,
                    'parallel': False,
                    'description': 'Findings report'
                }
            ],
            max_parallel_agents=15,
            human_approval_required=True,
            timeout_minutes=180,
            resource_limits={
                'max_memory_gb': 12.0,
                'max_cpu_percent': 75.0
            }
        )
    
    @staticmethod
    def smart_contract_audit_campaign(contract_address: str, blockchain: str = "ethereum") -> CampaignConfig:
        """
        Smart contract security audit campaign.
        
        Multi-tool static analysis and vulnerability detection.
        """
        return CampaignConfig(
            campaign_id=f"contract_audit_{contract_address[:10]}",
            target=contract_address,
            program=f"{blockchain}-security",
            phases=[
                {
                    'name': 'osint',
                    'agents': 1,
                    'parallel': False,
                    'description': 'Contract metadata and transaction analysis'
                },
                {
                    'name': 'analysis',
                    'agents': 5,
                    'parallel': True,
                    'description': 'Multi-tool static analysis (Slither, Mythril, etc.)'
                },
                {
                    'name': 'testing',
                    'agents': 3,
                    'parallel': True,
                    'human_approval': True,
                    'description': 'Symbolic execution and fuzzing'
                },
                {
                    'name': 'documentation',
                    'agents': 1,
                    'parallel': False,
                    'description': 'Comprehensive audit report'
                }
            ],
            max_parallel_agents=10,
            human_approval_required=True,
            timeout_minutes=300,
            resource_limits={
                'max_memory_gb': 20.0,
                'max_cpu_percent': 85.0
            }
        )
    
    @staticmethod
    def web_app_pentest_campaign(target_url: str, scope: list) -> CampaignConfig:
        """
        Web application penetration testing campaign.
        
        Comprehensive web app security assessment.
        """
        return CampaignConfig(
            campaign_id=f"webapp_pentest_{target_url.replace('https://', '').replace('/', '_')}",
            target=target_url,
            program="web-app-security",
            phases=[
                {
                    'name': 'osint',
                    'agents': 3,
                    'parallel': True,
                    'description': 'Subdomain enumeration and technology fingerprinting'
                },
                {
                    'name': 'analysis',
                    'agents': 4,
                    'parallel': True,
                    'description': 'Vulnerability scanning and endpoint mapping'
                },
                {
                    'name': 'hypothesis',
                    'agents': 1,
                    'parallel': False,
                    'description': 'Attack vector identification'
                },
                {
                    'name': 'testing',
                    'agents': 8,
                    'parallel': True,
                    'human_approval': True,
                    'description': 'Manual and automated exploitation'
                },
                {
                    'name': 'documentation',
                    'agents': 2,
                    'parallel': True,
                    'description': 'Evidence gathering and reporting'
                }
            ],
            max_parallel_agents=20,
            human_approval_required=True,
            timeout_minutes=360,
            resource_limits={
                'max_memory_gb': 24.0,
                'max_cpu_percent': 80.0
            }
        )


# Demo usage
if __name__ == "__main__":
    print("=== Campaign Templates ===\n")
    
    templates = CampaignTemplates()
    
    # Example 1: GitHub Copilot campaign
    copilot_campaign = templates.github_copilot_campaign()
    print(f"1. GitHub Copilot Campaign: {copilot_campaign.campaign_id}")
    print(f"   Phases: {len(copilot_campaign.phases)}")
    print(f"   Max agents: {copilot_campaign.max_parallel_agents}")
    print(f"   Timeout: {copilot_campaign.timeout_minutes} min\n")
    
    # Example 2: NPM package audit
    npm_campaign = templates.npm_package_campaign("@github/copilot-sdk")
    print(f"2. NPM Package Campaign: {npm_campaign.campaign_id}")
    print(f"   Target: {npm_campaign.target}")
    print(f"   Phases: {len(npm_campaign.phases)}\n")
    
    # Example 3: API fuzzing
    api_campaign = templates.api_fuzzing_campaign("https://api.example.com", ["*.example.com"])
    print(f"3. API Fuzzing Campaign: {api_campaign.campaign_id}")
    print(f"   Max parallel agents: {api_campaign.max_parallel_agents}\n")
    
    # Example 4: Smart contract audit
    contract_campaign = templates.smart_contract_audit_campaign("0x1234567890abcdef")
    print(f"4. Smart Contract Audit: {contract_campaign.campaign_id}")
    print(f"   Timeout: {contract_campaign.timeout_minutes} min\n")
    
    # Example 5: Web app pentest
    webapp_campaign = templates.web_app_pentest_campaign("https://target.com", ["*.target.com"])
    print(f"5. Web App Pentest: {webapp_campaign.campaign_id}")
    print(f"   Phases: {len(webapp_campaign.phases)}")
    
    print("\n✓ All campaign templates ready for use")
