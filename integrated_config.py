#!/usr/bin/env python3
"""
GLASSEYE AI OS - Integrated Configuration
Master configuration with all discovered credentials and resources
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class GlasseyeConfig:
    """Master configuration for GLASSEYE AI OS"""
    
    def __init__(self):
        self.load_credentials()
        self.configure_environment()
    
    def load_credentials(self):
        """Load all discovered credentials"""
        creds_file = Path("/home/x/glasseye/COMPLETE_CREDENTIALS.json")
        
        with open(creds_file, 'r') as f:
            self.creds = json.load(f)
        
        print(f"[+] Loaded credentials for {self.creds['owner']}")
    
    def configure_environment(self):
        """Set environment variables for all services"""
        
        # AWS
        aws = self.creds['cloud_platforms']['aws']
        os.environ['AWS_ACCESS_KEY_ID'] = aws['access_key_id']
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws['secret_access_key']
        os.environ['AWS_DEFAULT_REGION'] = aws['region']
        os.environ['AWS_ACCOUNT_ID'] = aws['account_id']
        
        # GitHub
        github = self.creds['github']['primary_account']
        os.environ['GITHUB_TOKEN'] = github['token']
        os.environ['GITHUB_USER'] = github['username']
        
        # AI APIs
        ai = self.creds['ai_platforms']
        os.environ['ANTHROPIC_API_KEY'] = ai['anthropic_claude']['api_key']
        os.environ['MISTRAL_API_KEY'] = ai['mistral']['api_key']
        
        # Local Services
        services = self.creds['local_services']
        os.environ['MCP_SERVER_KEY'] = services['mcp_server']['api_key']
        os.environ['GLASSEYE_PORT'] = str(services['glasseye_ai']['port'])
        os.environ['CLAUDE_API_PORT'] = str(services['claude_api']['port'])
        
        # Domain
        domain = self.creds['domain_and_emails']
        os.environ['PRIMARY_DOMAIN'] = domain['primary_domain']
        os.environ['PRIMARY_EMAIL'] = domain['emails']['primary']
        
        print("[+] Environment configured with all credentials")
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get unified API configuration"""
        return {
            'aws': {
                'access_key': os.environ['AWS_ACCESS_KEY_ID'],
                'secret_key': os.environ['AWS_SECRET_ACCESS_KEY'],
                'region': os.environ['AWS_DEFAULT_REGION'],
                'account_id': os.environ['AWS_ACCOUNT_ID']
            },
            'github': {
                'token': os.environ['GITHUB_TOKEN'],
                'user': os.environ['GITHUB_USER']
            },
            'ai_apis': {
                'anthropic': os.environ['ANTHROPIC_API_KEY'],
                'mistral': os.environ['MISTRAL_API_KEY']
            },
            'local_services': {
                'mcp_server': {
                    'url': 'http://localhost:5001',
                    'api_key': os.environ['MCP_SERVER_KEY']
                },
                'glasseye_ai': {
                    'url': f"http://localhost:{os.environ['GLASSEYE_PORT']}"
                },
                'claude_api': {
                    'url': f"http://localhost:{os.environ['CLAUDE_API_PORT']}",
                    'api_key': os.environ['ANTHROPIC_API_KEY']
                }
            },
            'domain': {
                'primary': os.environ['PRIMARY_DOMAIN'],
                'email': os.environ['PRIMARY_EMAIL']
            }
        }
    
    def save_env_file(self):
        """Save environment file for easy loading"""
        env_file = Path("/home/x/glasseye/.env.integrated")
        
        with open(env_file, 'w') as f:
            f.write("# GLASSEYE AI OS - Integrated Environment\n")
            f.write("# Auto-generated from discovered credentials\n\n")
            
            f.write("# AWS\n")
            f.write(f"AWS_ACCESS_KEY_ID={os.environ['AWS_ACCESS_KEY_ID']}\n")
            f.write(f"AWS_SECRET_ACCESS_KEY={os.environ['AWS_SECRET_ACCESS_KEY']}\n")
            f.write(f"AWS_DEFAULT_REGION={os.environ['AWS_DEFAULT_REGION']}\n")
            f.write(f"AWS_ACCOUNT_ID={os.environ['AWS_ACCOUNT_ID']}\n\n")
            
            f.write("# GitHub\n")
            f.write(f"GITHUB_TOKEN={os.environ['GITHUB_TOKEN']}\n")
            f.write(f"GITHUB_USER={os.environ['GITHUB_USER']}\n\n")
            
            f.write("# AI APIs\n")
            f.write(f"ANTHROPIC_API_KEY={os.environ['ANTHROPIC_API_KEY']}\n")
            f.write(f"MISTRAL_API_KEY={os.environ['MISTRAL_API_KEY']}\n\n")
            
            f.write("# Local Services\n")
            f.write(f"MCP_SERVER_KEY={os.environ['MCP_SERVER_KEY']}\n")
            f.write(f"GLASSEYE_PORT={os.environ['GLASSEYE_PORT']}\n")
            f.write(f"CLAUDE_API_PORT={os.environ['CLAUDE_API_PORT']}\n\n")
            
            f.write("# Domain\n")
            f.write(f"PRIMARY_DOMAIN={os.environ['PRIMARY_DOMAIN']}\n")
            f.write(f"PRIMARY_EMAIL={os.environ['PRIMARY_EMAIL']}\n")
        
        os.chmod(env_file, 0o600)
        print(f"[+] Environment file saved: {env_file}")
        
        return env_file
    
    def test_integrations(self):
        """Test all integrated services"""
        import requests
        
        print("\n[*] Testing integrations...")
        
        results = {}
        
        # Test AWS
        try:
            import subprocess
            result = subprocess.run(
                ['aws', 'sts', 'get-caller-identity'],
                capture_output=True,
                text=True,
                timeout=10
            )
            results['aws'] = result.returncode == 0
            if results['aws']:
                print("[+] AWS: Connected")
            else:
                print(f"[-] AWS: Failed")
        except Exception as e:
            results['aws'] = False
            print(f"[-] AWS: {e}")
        
        # Test GitHub
        try:
            headers = {'Authorization': f"token {os.environ['GITHUB_TOKEN']}"}
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            results['github'] = response.status_code == 200
            if results['github']:
                print(f"[+] GitHub: Connected as {response.json()['login']}")
            else:
                print(f"[-] GitHub: Failed")
        except Exception as e:
            results['github'] = False
            print(f"[-] GitHub: {e}")
        
        # Test Local Services
        services = [
            ('GLASSEYE AI', f"http://localhost:{os.environ['GLASSEYE_PORT']}/health"),
            ('Claude API', f"http://localhost:{os.environ['CLAUDE_API_PORT']}/health"),
            ('MCP Server', 'http://localhost:5001/health')
        ]
        
        for name, url in services:
            try:
                response = requests.get(url, timeout=5)
                results[name] = response.status_code == 200
                if results[name]:
                    print(f"[+] {name}: Active")
                else:
                    print(f"[-] {name}: Status {response.status_code}")
            except Exception as e:
                results[name] = False
                print(f"[-] {name}: {e}")
        
        return results


def main():
    print("="*60)
    print("GLASSEYE AI OS - INTEGRATED CONFIGURATION")
    print("="*60)
    
    config = GlasseyeConfig()
    
    # Save environment file
    env_file = config.save_env_file()
    
    # Get API config
    api_config = config.get_api_config()
    
    # Save API config
    config_file = Path("/home/x/glasseye/api_config.json")
    with open(config_file, 'w') as f:
        json.dump(api_config, f, indent=2)
    os.chmod(config_file, 0o600)
    
    print(f"[+] API config saved: {config_file}")
    
    # Test integrations
    results = config.test_integrations()
    
    print("\n" + "="*60)
    print("INTEGRATION TEST RESULTS")
    print("="*60)
    successful = sum(1 for v in results.values() if v is True)
    print(f"Successful: {successful}/{len(results)}")
    print("="*60)
    
    print("\n[+] Integration complete!")
    print("[*] To load environment: source /home/x/glasseye/.env.integrated")
    print("[*] API config: /home/x/glasseye/api_config.json")


if __name__ == "__main__":
    main()
