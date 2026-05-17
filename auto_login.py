#!/usr/bin/env python3
"""
GLASSEYE AI OS - Automatic Login and Authentication System
Logs into all discovered platforms and services
"""

import os
import json
import subprocess
import requests
from pathlib import Path

class AutoLogin:
    """Automatic authentication to all platforms"""
    
    def __init__(self):
        self.creds_file = "/home/x/glasseye/MASTER_CREDENTIALS.json"
        self.load_credentials()
        
    def load_credentials(self):
        """Load master credentials"""
        with open(self.creds_file, 'r') as f:
            self.creds = json.load(f)
        print(f"[+] Loaded credentials for {self.creds['owner']}")
    
    def login_github(self):
        """Authenticate to GitHub"""
        print("\n[*] Logging into GitHub...")
        
        token = self.creds['github_accounts']['primary']['token']
        
        # Test token
        headers = {'Authorization': f'token {token}'}
        response = requests.get('https://api.github.com/user', headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print(f"[+] GitHub: Logged in as {user['login']}")
            print(f"    Repos: {user['public_repos']} public, {user.get('total_private_repos', 0)} private")
            return True
        else:
            print(f"[-] GitHub login failed: {response.status_code}")
            return False
    
    def login_aws(self):
        """Authenticate to AWS"""
        print("\n[*] Logging into AWS...")
        
        aws_creds = self.creds['cloud_platforms']['aws']
        
        # Configure AWS
        os.environ['AWS_ACCESS_KEY_ID'] = aws_creds['access_key_id']
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_creds['secret_access_key']
        
        # Test
        try:
            result = subprocess.run(
                ['aws', 'sts', 'get-caller-identity'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                identity = json.loads(result.stdout)
                print(f"[+] AWS: Logged in as {identity['Arn']}")
                print(f"    Account: {identity['Account']}")
                return True
            else:
                print(f"[-] AWS login failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"[-] AWS error: {e}")
            return False
    
    def test_local_services(self):
        """Test local GLASSEYE services"""
        print("\n[*] Testing local services...")
        
        services = [
            ("GLASSEYE AI", "http://localhost:8002/health"),
            ("Claude API", "http://localhost:8000/health"),
            ("MCP Server", "http://localhost:5001/health"),
        ]
        
        for name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[+] {name}: ACTIVE")
                else:
                    print(f"[-] {name}: Status {response.status_code}")
            except Exception as e:
                print(f"[-] {name}: {e}")
    
    def check_huggingface(self):
        """Check for HuggingFace token"""
        print("\n[*] Checking HuggingFace...")
        
        token_file = Path.home() / ".huggingface" / "token"
        
        if token_file.exists():
            token = token_file.read_text().strip()
            print(f"[+] HuggingFace token found: {token[:10]}...")
            
            # Test token
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('https://huggingface.co/api/whoami-v2', headers=headers)
            
            if response.status_code == 200:
                user = response.json()
                print(f"[+] HuggingFace: Logged in as {user.get('name', 'unknown')}")
                return True
        else:
            print(f"[-] HuggingFace token not found")
        
        return False
    
    def run_full_authentication(self):
        """Authenticate to all platforms"""
        print(f"\n{'='*60}")
        print(f"GLASSEYE AUTO-LOGIN SYSTEM")
        print(f"Owner: {self.creds['owner']}")
        print(f"{'='*60}")
        
        results = {
            'github': self.login_github(),
            'aws': self.login_aws(),
            'local_services': self.test_local_services(),
            'huggingface': self.check_huggingface(),
        }
        
        print(f"\n{'='*60}")
        print(f"AUTHENTICATION SUMMARY")
        print(f"{'='*60}")
        successful = sum(1 for v in results.values() if v is True)
        print(f"Successful logins: {successful}/{len(results)}")
        print(f"{'='*60}\n")
        
        return results

def main():
    auto = AutoLogin()
    results = auto.run_full_authentication()
    
    print("[+] Auto-login complete!")
    print("[*] All credentials stored in: /home/x/glasseye/MASTER_CREDENTIALS.json")
    print("[*] Access level: FULL CONTROL")

if __name__ == "__main__":
    main()
