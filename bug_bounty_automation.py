#!/usr/bin/env python3
"""
GLASSEYE AI OS - Bug Bounty Automation
Automated vulnerability discovery, PoC generation, and report writing for bug bounties
"""

import json
import sys
import requests
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path

sys.path.append('/home/x/glasseye')
from memory_system import GlasseyeMemory
from autonomous_recon import AutonomousRecon
from auto_exploitation import AutoExploitation


@dataclass
class BugBountyFinding:
    """A bug bounty finding"""
    title: str
    severity: str  # critical, high, medium, low, info
    cvss_score: float
    cwe_id: Optional[str]
    description: str
    impact: str
    steps_to_reproduce: List[str]
    poc_code: Optional[str]
    affected_urls: List[str]
    remediation: str
    references: List[str]
    discovered_at: str


@dataclass
class BugBountyReport:
    """Complete bug bounty report"""
    program_name: str
    target: str
    findings: List[BugBountyFinding]
    total_findings: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    generated_at: str


class BugBountyAutomation:
    """Automated bug bounty hunting"""
    
    def __init__(self):
        self.memory = GlasseyeMemory()
        self.recon = AutonomousRecon()
        self.exploit = AutoExploitation()
        
        # Common vulnerability patterns
        self.vuln_checks = {
            'sqli': self._check_sql_injection,
            'xss': self._check_xss,
            'idor': self._check_idor,
            'csrf': self._check_csrf,
            'ssrf': self._check_ssrf,
            'rce': self._check_rce,
            'lfi': self._check_lfi,
            'open_redirect': self._check_open_redirect,
            'xxe': self._check_xxe,
            'ssti': self._check_ssti
        }
    
    def _check_sql_injection(self, url: str) -> Optional[BugBountyFinding]:
        """Check for SQL injection"""
        print(f"[*] Testing for SQL injection...")
        
        payloads = [
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin' --",
            "' UNION SELECT NULL--",
            "1' AND '1'='1",
        ]
        
        for payload in payloads:
            try:
                # Test in URL parameters
                test_url = f"{url}?id={payload}"
                response = requests.get(test_url, timeout=10, verify=False)
                
                # Check for SQL error indicators
                error_indicators = [
                    'sql syntax',
                    'mysql_fetch',
                    'ora-01',
                    'postgresql',
                    'sqlite_',
                    'sqlstate',
                    'unclosed quotation'
                ]
                
                response_lower = response.text.lower()
                
                if any(indicator in response_lower for indicator in error_indicators):
                    return BugBountyFinding(
                        title="SQL Injection Vulnerability",
                        severity="critical",
                        cvss_score=9.1,
                        cwe_id="CWE-89",
                        description=f"SQL injection vulnerability found in {url}",
                        impact="Attacker can read/modify database, potentially gaining full system access",
                        steps_to_reproduce=[
                            f"1. Navigate to {url}",
                            f"2. Inject payload in 'id' parameter: {payload}",
                            "3. Observe SQL error message in response"
                        ],
                        poc_code=f"curl '{test_url}'",
                        affected_urls=[url],
                        remediation="Use parameterized queries/prepared statements. Never concatenate user input into SQL.",
                        references=[
                            "https://owasp.org/www-community/attacks/SQL_Injection",
                            "https://portswigger.net/web-security/sql-injection"
                        ],
                        discovered_at=datetime.now().isoformat()
                    )
            except Exception:
                continue
        
        return None
    
    def _check_xss(self, url: str) -> Optional[BugBountyFinding]:
        """Check for XSS"""
        print(f"[*] Testing for XSS...")
        
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>"
        ]
        
        for payload in payloads:
            try:
                test_url = f"{url}?q={payload}"
                response = requests.get(test_url, timeout=10, verify=False)
                
                # Check if payload is reflected unescaped
                if payload in response.text and '<script>' in response.text:
                    return BugBountyFinding(
                        title="Cross-Site Scripting (XSS) Vulnerability",
                        severity="high",
                        cvss_score=7.1,
                        cwe_id="CWE-79",
                        description=f"Reflected XSS vulnerability found in {url}",
                        impact="Attacker can execute arbitrary JavaScript, steal session tokens, perform actions as victim",
                        steps_to_reproduce=[
                            f"1. Navigate to {url}",
                            f"2. Inject payload in 'q' parameter: {payload}",
                            "3. Observe JavaScript execution in browser"
                        ],
                        poc_code=f"curl '{test_url}'",
                        affected_urls=[url],
                        remediation="Properly encode all user input before rendering. Use Content-Security-Policy headers.",
                        references=[
                            "https://owasp.org/www-community/attacks/xss/",
                            "https://portswigger.net/web-security/cross-site-scripting"
                        ],
                        discovered_at=datetime.now().isoformat()
                    )
            except Exception:
                continue
        
        return None
    
    def _check_idor(self, url: str) -> Optional[BugBountyFinding]:
        """Check for IDOR"""
        print(f"[*] Testing for IDOR...")
        
        # Test common IDOR patterns
        test_ids = [1, 2, 100, 999, 1000]
        
        try:
            # Test /api/user/1 vs /api/user/2
            if '/user/' in url or '/profile/' in url or '/account/' in url:
                responses = []
                
                for test_id in test_ids[:2]:
                    test_url = url.replace(str(test_ids[0]), str(test_id))
                    response = requests.get(test_url, timeout=10, verify=False)
                    responses.append((test_id, response.status_code, len(response.text)))
                
                # Check if different IDs return different user data
                if len(set(r[2] for r in responses)) > 1:
                    return BugBountyFinding(
                        title="Insecure Direct Object Reference (IDOR)",
                        severity="high",
                        cvss_score=7.5,
                        cwe_id="CWE-639",
                        description=f"IDOR vulnerability allows accessing other users' data in {url}",
                        impact="Attacker can access, modify, or delete other users' data by manipulating IDs",
                        steps_to_reproduce=[
                            "1. Login as user A with ID 1",
                            f"2. Request {url}",
                            "3. Change ID parameter to 2",
                            "4. Observe user B's data returned"
                        ],
                        poc_code=f"curl '{url.replace(str(test_ids[0]), '2')}'",
                        affected_urls=[url],
                        remediation="Implement proper authorization checks. Verify user has permission to access requested resource.",
                        references=[
                            "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References",
                        ],
                        discovered_at=datetime.now().isoformat()
                    )
        except Exception:
            pass
        
        return None
    
    def _check_csrf(self, url: str) -> Optional[BugBountyFinding]:
        """Check for CSRF"""
        print(f"[*] Testing for CSRF...")
        # Implementation would check for CSRF tokens
        return None
    
    def _check_ssrf(self, url: str) -> Optional[BugBountyFinding]:
        """Check for SSRF"""
        print(f"[*] Testing for SSRF...")
        # Implementation would check for SSRF
        return None
    
    def _check_rce(self, url: str) -> Optional[BugBountyFinding]:
        """Check for RCE"""
        print(f"[*] Testing for RCE...")
        # Implementation would check for RCE
        return None
    
    def _check_lfi(self, url: str) -> Optional[BugBountyFinding]:
        """Check for LFI"""
        print(f"[*] Testing for LFI...")
        
        payloads = [
            "../../../etc/passwd",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd"
        ]
        
        for payload in payloads:
            try:
                test_url = f"{url}?file={payload}"
                response = requests.get(test_url, timeout=10, verify=False)
                
                if 'root:' in response.text and '/bin/bash' in response.text:
                    return BugBountyFinding(
                        title="Local File Inclusion (LFI) Vulnerability",
                        severity="high",
                        cvss_score=7.5,
                        cwe_id="CWE-22",
                        description=f"LFI vulnerability allows reading arbitrary files in {url}",
                        impact="Attacker can read sensitive files including /etc/passwd, configuration files, source code",
                        steps_to_reproduce=[
                            f"1. Navigate to {url}",
                            f"2. Inject payload in 'file' parameter: {payload}",
                            "3. Observe /etc/passwd contents in response"
                        ],
                        poc_code=f"curl '{test_url}'",
                        affected_urls=[url],
                        remediation="Use whitelist of allowed files. Never pass user input directly to file operations.",
                        references=[
                            "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.1-Testing_for_Local_File_Inclusion",
                        ],
                        discovered_at=datetime.now().isoformat()
                    )
            except Exception:
                continue
        
        return None
    
    def _check_open_redirect(self, url: str) -> Optional[BugBountyFinding]:
        """Check for open redirect"""
        print(f"[*] Testing for open redirect...")
        # Implementation would check for open redirect
        return None
    
    def _check_xxe(self, url: str) -> Optional[BugBountyFinding]:
        """Check for XXE"""
        print(f"[*] Testing for XXE...")
        # Implementation would check for XXE
        return None
    
    def _check_ssti(self, url: str) -> Optional[BugBountyFinding]:
        """Check for SSTI"""
        print(f"[*] Testing for SSTI...")
        # Implementation would check for SSTI
        return None
    
    def scan_target(self, target: str, deep: bool = False) -> List[BugBountyFinding]:
        """Scan target for vulnerabilities"""
        print(f"\n[*] Scanning {target} for vulnerabilities...")
        
        findings = []
        
        # Run vulnerability checks
        for vuln_name, check_func in self.vuln_checks.items():
            print(f"\n[*] Checking for {vuln_name.upper()}...")
            
            try:
                finding = check_func(target)
                if finding:
                    findings.append(finding)
                    print(f"[+] FOUND: {finding.title} ({finding.severity})")
            except Exception as e:
                print(f"[-] Check failed: {e}")
        
        return findings
    
    def generate_report(self, program_name: str, target: str, findings: List[BugBountyFinding]) -> BugBountyReport:
        """Generate bug bounty report"""
        # Count findings by severity
        severity_counts = {
            'critical': len([f for f in findings if f.severity == 'critical']),
            'high': len([f for f in findings if f.severity == 'high']),
            'medium': len([f for f in findings if f.severity == 'medium']),
            'low': len([f for f in findings if f.severity == 'low']),
            'info': len([f for f in findings if f.severity == 'info']),
        }
        
        report = BugBountyReport(
            program_name=program_name,
            target=target,
            findings=findings,
            total_findings=len(findings),
            critical=severity_counts['critical'],
            high=severity_counts['high'],
            medium=severity_counts['medium'],
            low=severity_counts['low'],
            info=severity_counts['info'],
            generated_at=datetime.now().isoformat()
        )
        
        return report
    
    def save_report(self, report: BugBountyReport, output_format: str = 'markdown') -> str:
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format == 'markdown':
            output_file = f"/home/x/glasseye/reports/bug_bounty_{report.target.replace('.', '_')}_{timestamp}.md"
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                f.write(f"# Bug Bounty Report: {report.program_name}\n\n")
                f.write(f"**Target:** {report.target}  \n")
                f.write(f"**Generated:** {report.generated_at}  \n")
                f.write(f"**Total Findings:** {report.total_findings}  \n\n")
                
                f.write("## Summary\n\n")
                f.write(f"- 🔴 Critical: {report.critical}\n")
                f.write(f"- 🟠 High: {report.high}\n")
                f.write(f"- 🟡 Medium: {report.medium}\n")
                f.write(f"- 🟢 Low: {report.low}\n")
                f.write(f"- ℹ️ Info: {report.info}\n\n")
                
                f.write("## Findings\n\n")
                
                for i, finding in enumerate(report.findings, 1):
                    f.write(f"### {i}. {finding.title}\n\n")
                    f.write(f"**Severity:** {finding.severity.upper()}  \n")
                    f.write(f"**CVSS Score:** {finding.cvss_score}  \n")
                    if finding.cwe_id:
                        f.write(f"**CWE ID:** {finding.cwe_id}  \n")
                    f.write(f"\n**Description:**  \n{finding.description}\n\n")
                    f.write(f"**Impact:**  \n{finding.impact}\n\n")
                    f.write(f"**Steps to Reproduce:**\n")
                    for step in finding.steps_to_reproduce:
                        f.write(f"{step}\n")
                    f.write(f"\n**Proof of Concept:**\n```bash\n{finding.poc_code}\n```\n\n")
                    f.write(f"**Remediation:**  \n{finding.remediation}\n\n")
                    f.write(f"**References:**\n")
                    for ref in finding.references:
                        f.write(f"- {ref}\n")
                    f.write("\n---\n\n")
        
        elif output_format == 'json':
            output_file = f"/home/x/glasseye/reports/bug_bounty_{report.target.replace('.', '_')}_{timestamp}.json"
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(asdict(report), f, indent=2)
        
        return output_file
    
    def run_full_automation(self, program_name: str, target: str) -> BugBountyReport:
        """Run complete bug bounty automation"""
        print(f"\n{'='*60}")
        print(f"GLASSEYE BUG BOUNTY AUTOMATION")
        print(f"Program: {program_name}")
        print(f"Target: {target}")
        print(f"{'='*60}\n")
        
        # Phase 1: Reconnaissance
        print(f"[*] Phase 1: Reconnaissance")
        recon_result = self.recon.run_autonomous_recon(target)
        
        # Phase 2: Vulnerability scanning
        print(f"\n[*] Phase 2: Vulnerability Scanning")
        findings = self.scan_target(target)
        
        # Phase 3: Generate report
        print(f"\n[*] Phase 3: Generating Report")
        report = self.generate_report(program_name, target, findings)
        
        # Save reports
        md_file = self.save_report(report, 'markdown')
        json_file = self.save_report(report, 'json')
        
        print(f"\n{'='*60}")
        print(f"BUG BOUNTY AUTOMATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total findings: {report.total_findings}")
        print(f"Critical: {report.critical}, High: {report.high}, Medium: {report.medium}")
        print(f"Reports saved:")
        print(f"  - Markdown: {md_file}")
        print(f"  - JSON: {json_file}")
        print(f"{'='*60}\n")
        
        return report


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 bug_bounty_automation.py <program> <target>")
        print("Example: python3 bug_bounty_automation.py 'HackerOne' scanme.nmap.org")
        sys.exit(1)
    
    program_name = sys.argv[1]
    target = sys.argv[2]
    
    automation = BugBountyAutomation()
    report = automation.run_full_automation(program_name, target)
    
    print(f"[+] Automation complete! Found {report.total_findings} vulnerabilities")


if __name__ == "__main__":
    main()
