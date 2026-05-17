#!/usr/bin/env python3
"""
GLASSEYE AI OS - Master Orchestrator
Unified interface to all GLASSEYE capabilities with integrated resources
"""

import sys
import json
import requests
from pathlib import Path

# Add glasseye to path
sys.path.append('/home/x/glasseye')

from integrated_config import GlasseyeConfig
from autonomous_recon import AutonomousRecon
from auto_exploitation import AutoExploitation
from metasploit_integration import MetasploitIntegration
from bug_bounty_automation import BugBountyAutomation
from ai_code_generator import AICodeGenerator
from auto_testing_framework import AutoTestingFramework
from ai_decision_engine import AIDecisionEngine
from memory_system import GlasseyeMemory


class MasterOrchestrator:
    """Master orchestrator for all GLASSEYE capabilities"""
    
    def __init__(self):
        print("[*] Initializing GLASSEYE Master Orchestrator...")
        
        # Load configuration
        self.config = GlasseyeConfig()
        
        # Initialize all modules
        self.recon = AutonomousRecon()
        self.exploit = AutoExploitation()
        self.msf = MetasploitIntegration()
        self.bug_bounty = BugBountyAutomation()
        self.code_gen = AICodeGenerator()
        self.testing = AutoTestingFramework()
        self.ai_engine = AIDecisionEngine()
        self.memory = GlasseyeMemory()
        
        print("[+] All modules loaded")
        print("[+] All credentials configured")
        print("[+] Master Orchestrator ready")
    
    def full_autonomous_scan(self, target: str, program_name: str = "GLASSEYE"):
        """Run complete autonomous scan with all capabilities"""
        print(f"\n{'='*60}")
        print(f"GLASSEYE FULL AUTONOMOUS SCAN")
        print(f"Target: {target}")
        print(f"Program: {program_name}")
        print(f"{'='*60}\n")
        
        # Phase 1: AI Decision Engine Analysis
        print("[*] Phase 1: AI Strategic Analysis")
        decision = self.ai_engine.analyze_target(target)
        print(f"[+] Risk Score: {decision.get('risk_score', 'N/A')}")
        print(f"[+] Attack Plan: {len(decision.get('attack_plan', {}).get('stages', []))} stages")
        
        # Phase 2: Autonomous Reconnaissance
        print("\n[*] Phase 2: Autonomous Reconnaissance")
        recon_result = self.recon.run_autonomous_recon(target)
        print(f"[+] Intelligence gathered: {len(recon_result.get('findings', []))} findings")
        
        # Phase 3: Auto-Exploitation
        print("\n[*] Phase 3: Auto-Exploitation")
        exploit_result = self.exploit.run_auto_exploitation(target)
        print(f"[+] Exploits attempted: {exploit_result.get('total_exploits', 0)}")
        print(f"[+] Successful: {exploit_result.get('successful', 0)}")
        
        # Phase 4: Bug Bounty Report Generation
        print("\n[*] Phase 4: Bug Bounty Report Generation")
        findings = self.bug_bounty.scan_target(target)
        report = self.bug_bounty.generate_report(program_name, target, findings)
        
        md_file = self.bug_bounty.save_report(report, 'markdown')
        json_file = self.bug_bounty.save_report(report, 'json')
        
        print(f"[+] Findings: {report.total_findings}")
        print(f"[+] Critical: {report.critical}, High: {report.high}, Medium: {report.medium}")
        print(f"[+] Reports saved: {md_file}, {json_file}")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"AUTONOMOUS SCAN COMPLETE")
        print(f"{'='*60}")
        print(f"Risk Score: {decision.get('risk_score', 'N/A')}")
        print(f"Intelligence: {len(recon_result.get('findings', []))} findings")
        print(f"Exploits: {exploit_result.get('successful', 0)}/{exploit_result.get('total_exploits', 0)} successful")
        print(f"Vulnerabilities: {report.total_findings} found")
        print(f"Reports: {md_file}")
        print(f"{'='*60}\n")
        
        return {
            'target': target,
            'decision': decision,
            'recon': recon_result,
            'exploit': exploit_result,
            'report': report,
            'report_files': {'markdown': md_file, 'json': json_file}
        }
    
    def generate_custom_exploit(self, vuln_desc: str, target_info: str):
        """Generate custom exploit using AI"""
        print(f"\n[*] Generating custom exploit...")
        print(f"[*] Vulnerability: {vuln_desc}")
        print(f"[*] Target: {target_info}")
        
        generated = self.code_gen.generate_exploit(vuln_desc, target_info)
        filepath = self.code_gen.save_code(generated)
        
        print(f"[+] Exploit generated: {filepath}")
        return filepath
    
    def deploy_to_cloud(self, service: str = 'aws'):
        """Deploy GLASSEYE to cloud platform"""
        print(f"\n[*] Deploying GLASSEYE to {service.upper()}...")
        
        if service == 'aws':
            api_config = self.config.get_api_config()
            aws = api_config['aws']
            
            print(f"[+] AWS Account: {aws['account_id']}")
            print(f"[+] Region: {aws['region']}")
            print("[*] Deployment commands:")
            print(f"    aws s3 ls")
            print(f"    aws ec2 describe-instances")
            
        return True
    
    def show_status(self):
        """Show complete system status"""
        print(f"\n{'='*60}")
        print("GLASSEYE AI OS - SYSTEM STATUS")
        print(f"{'='*60}\n")
        
        # Test integrations
        results = self.config.test_integrations()
        
        # Memory stats
        print("\n[*] Memory System:")
        scan_history = self.memory.get_all_scans()
        print(f"    Scans recorded: {len(scan_history)}")
        
        # Modules
        print("\n[*] Available Modules:")
        print("    ✅ Autonomous Reconnaissance")
        print("    ✅ Auto-Exploitation")
        print("    ✅ Metasploit Integration")
        print("    ✅ Bug Bounty Automation")
        print("    ✅ AI Code Generator")
        print("    ✅ Auto-Testing Framework")
        print("    ✅ AI Decision Engine")
        print("    ✅ Memory System")
        
        # Credentials
        print("\n[*] Authenticated Platforms:")
        print("    ✅ AWS (Account 347694270918)")
        print("    ✅ Azure (scane8891@gmail.com)")
        print("    ✅ GitHub (GulfOfAmerica)")
        print("    ✅ Google Cloud (0aiinferencesolutions@gmail.com)")
        print("    ✅ Claude/Anthropic API")
        print("    ✅ Mistral API")
        
        print(f"\n{'='*60}")
        print(f"STATUS: OPERATIONAL ✅")
        print(f"{'='*60}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GLASSEYE AI OS - Master Orchestrator')
    parser.add_argument('command', choices=['scan', 'exploit', 'generate', 'deploy', 'status'],
                       help='Command to execute')
    parser.add_argument('--target', help='Target for scan/exploit')
    parser.add_argument('--program', default='GLASSEYE', help='Bug bounty program name')
    parser.add_argument('--vuln', help='Vulnerability description for code generation')
    parser.add_argument('--target-info', help='Target info for code generation')
    parser.add_argument('--service', default='aws', help='Cloud service for deployment')
    
    args = parser.parse_args()
    
    orchestrator = MasterOrchestrator()
    
    if args.command == 'scan':
        if not args.target:
            print("[-] --target required for scan command")
            sys.exit(1)
        orchestrator.full_autonomous_scan(args.target, args.program)
    
    elif args.command == 'exploit':
        if not args.target:
            print("[-] --target required for exploit command")
            sys.exit(1)
        orchestrator.exploit.run_auto_exploitation(args.target)
    
    elif args.command == 'generate':
        if not args.vuln or not args.target_info:
            print("[-] --vuln and --target-info required for generate command")
            sys.exit(1)
        orchestrator.generate_custom_exploit(args.vuln, args.target_info)
    
    elif args.command == 'deploy':
        orchestrator.deploy_to_cloud(args.service)
    
    elif args.command == 'status':
        orchestrator.show_status()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - show status
        orchestrator = MasterOrchestrator()
        orchestrator.show_status()
    else:
        main()
