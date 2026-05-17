#!/usr/bin/env python3
"""
GLASSEYE AI OS - OSINT Engine
Social media, threat intelligence, and reconnaissance
"""

import sys
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any
import requests

sys.path.append('/home/x/glasseye')
from memory_system import GlasseyeMemory


@dataclass
class OSINTResult:
    """OSINT finding"""
    source: str
    data_type: str
    data: Dict[str, Any]
    confidence: float
    timestamp: str


class OSINTEngine:
    """OSINT collection and analysis"""
    
    def __init__(self):
        self.memory = GlasseyeMemory()
        print("🔍 OSINT Engine initialized")
    
    def collect_domain_intel(self, domain: str) -> List[OSINTResult]:
        """Collect intelligence about a domain"""
        results = []
        
        # WHOIS lookup
        try:
            whois_data = self._run_whois(domain)
            results.append(OSINTResult(
                source='whois',
                data_type='registration',
                data=whois_data,
                confidence=0.95,
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"  ⚠️  WHOIS error: {e}")
        
        # DNS enumeration
        try:
            dns_data = self._run_dns_enum(domain)
            results.append(OSINTResult(
                source='dns',
                data_type='infrastructure',
                data=dns_data,
                confidence=0.9,
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"  ⚠️  DNS error: {e}")
        
        # Certificate transparency
        try:
            cert_data = self._check_crt_sh(domain)
            results.append(OSINTResult(
                source='crt.sh',
                data_type='certificates',
                data=cert_data,
                confidence=0.85,
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"  ⚠️  Certificate lookup error: {e}")
        
        return results
    
    def collect_social_intel(self, username: str) -> List[OSINTResult]:
        """Collect social media intelligence"""
        results = []
        
        platforms = [
            'github.com',
            'twitter.com',
            'linkedin.com',
            'reddit.com'
        ]
        
        for platform in platforms:
            try:
                profile_data = self._check_username(username, platform)
                if profile_data.get('found'):
                    results.append(OSINTResult(
                        source=platform,
                        data_type='social_profile',
                        data=profile_data,
                        confidence=0.8,
                        timestamp=datetime.now().isoformat()
                    ))
            except Exception as e:
                print(f"  ⚠️  {platform} error: {e}")
        
        return results
    
    def collect_email_intel(self, email: str) -> List[OSINTResult]:
        """Collect email-related intelligence"""
        results = []
        
        # Check haveibeenpwned
        try:
            breach_data = self._check_breaches(email)
            if breach_data:
                results.append(OSINTResult(
                    source='haveibeenpwned',
                    data_type='data_breach',
                    data=breach_data,
                    confidence=0.95,
                    timestamp=datetime.now().isoformat()
                ))
        except Exception as e:
            print(f"  ⚠️  Breach check error: {e}")
        
        return results
    
    def collect_ip_intel(self, ip: str) -> List[OSINTResult]:
        """Collect IP address intelligence"""
        results = []
        
        # Shodan lookup (if API key available)
        try:
            shodan_data = self._check_shodan(ip)
            if shodan_data:
                results.append(OSINTResult(
                    source='shodan',
                    data_type='host_services',
                    data=shodan_data,
                    confidence=0.9,
                    timestamp=datetime.now().isoformat()
                ))
        except Exception as e:
            print(f"  ⚠️  Shodan error: {e}")
        
        # Reverse DNS
        try:
            rdns_data = self._reverse_dns(ip)
            results.append(OSINTResult(
                source='rdns',
                data_type='hostname',
                data=rdns_data,
                confidence=0.85,
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"  ⚠️  Reverse DNS error: {e}")
        
        return results
    
    def _run_whois(self, domain: str) -> Dict:
        """Run WHOIS lookup"""
        result = subprocess.run(
            ['whois', domain],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            'domain': domain,
            'raw_output': result.stdout[:1000],  # First 1000 chars
            'found': result.returncode == 0
        }
    
    def _run_dns_enum(self, domain: str) -> Dict:
        """DNS enumeration"""
        records = {}
        
        for record_type in ['A', 'AAAA', 'MX', 'TXT', 'NS']:
            try:
                result = subprocess.run(
                    ['dig', '+short', record_type, domain],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                records[record_type] = result.stdout.strip().split('\n')
            except:
                records[record_type] = []
        
        return {
            'domain': domain,
            'records': records
        }
    
    def _check_crt_sh(self, domain: str) -> Dict:
        """Check certificate transparency logs"""
        try:
            url = f'https://crt.sh/?q=%.{domain}&output=json'
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                certs = response.json()
                return {
                    'domain': domain,
                    'certificates_found': len(certs),
                    'subdomains': list(set([c.get('name_value', '') for c in certs[:50]]))
                }
        except:
            pass
        
        return {'domain': domain, 'certificates_found': 0, 'subdomains': []}
    
    def _check_username(self, username: str, platform: str) -> Dict:
        """Check if username exists on platform"""
        # Simplified check (in production, use proper APIs)
        return {
            'username': username,
            'platform': platform,
            'found': False,  # Would check actual platform
            'profile_url': f'https://{platform}/{username}'
        }
    
    def _check_breaches(self, email: str) -> Dict:
        """Check data breaches (placeholder)"""
        # In production, use haveibeenpwned API
        return {
            'email': email,
            'breached': False,
            'breaches': []
        }
    
    def _check_shodan(self, ip: str) -> Dict:
        """Shodan lookup (placeholder)"""
        # In production, use Shodan API
        return {
            'ip': ip,
            'services': [],
            'found': False
        }
    
    def _reverse_dns(self, ip: str) -> Dict:
        """Reverse DNS lookup"""
        try:
            result = subprocess.run(
                ['dig', '+short', '-x', ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            hostname = result.stdout.strip()
            
            return {
                'ip': ip,
                'hostname': hostname if hostname else 'No PTR record',
                'found': bool(hostname)
            }
        except:
            return {'ip': ip, 'hostname': 'Error', 'found': False}
    
    def run_full_osint(self, target: str, target_type: str = 'domain') -> Dict:
        """Run complete OSINT collection"""
        print(f"\n🔍 Running OSINT collection on {target} (type: {target_type})")
        
        results = []
        
        if target_type == 'domain':
            results.extend(self.collect_domain_intel(target))
        elif target_type == 'username':
            results.extend(self.collect_social_intel(target))
        elif target_type == 'email':
            results.extend(self.collect_email_intel(target))
        elif target_type == 'ip':
            results.extend(self.collect_ip_intel(target))
        
        print(f"✅ OSINT collection complete: {len(results)} results")
        
        return {
            'target': target,
            'target_type': target_type,
            'results': [asdict(r) for r in results],
            'total_findings': len(results),
            'timestamp': datetime.now().isoformat()
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GLASSEYE OSINT Engine')
    parser.add_argument('target', help='Target for OSINT collection')
    parser.add_argument('--type', default='domain', 
                       choices=['domain', 'username', 'email', 'ip'],
                       help='Target type')
    
    args = parser.parse_args()
    
    engine = OSINTEngine()
    result = engine.run_full_osint(args.target, args.type)
    
    # Save results
    output_file = f'osint_results_{args.target}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Results saved: {output_file}")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
