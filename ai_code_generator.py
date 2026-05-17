#!/usr/bin/env python3
"""
GLASSEYE AI OS - AI Code Generator
Generate exploit code, scripts, and tools using AI (Claude/GPT-4)
"""

import json
import requests
import sys
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class GeneratedCode:
    """Generated code artifact"""
    code_type: str  # exploit, script, tool, payload
    language: str
    description: str
    code: str
    dependencies: List[str]
    usage_instructions: str
    generated_at: str


class AICodeGenerator:
    """AI-powered code generation"""
    
    def __init__(self):
        self.claude_url = "http://localhost:8000"
        self.glasseye_url = "http://localhost:8002"
        
    def generate_exploit(self, vulnerability_description: str, target_info: str) -> GeneratedCode:
        """Generate exploit code for a vulnerability"""
        print(f"[*] Generating exploit code...")
        
        prompt = f"""Generate a Python exploit script for the following vulnerability:

Vulnerability: {vulnerability_description}
Target Information: {target_info}

Requirements:
1. Clean, well-commented Python code
2. Error handling
3. Command-line arguments for target specification
4. Clear output/logging
5. Safe execution (ask for confirmation before destructive actions)

Provide ONLY the Python code, no explanations."""

        code = self._call_ai_model(prompt)
        
        return GeneratedCode(
            code_type="exploit",
            language="python",
            description=vulnerability_description,
            code=code,
            dependencies=self._extract_dependencies(code),
            usage_instructions=self._extract_usage(code),
            generated_at=datetime.now().isoformat()
        )
    
    def generate_recon_script(self, target_type: str, objectives: List[str]) -> GeneratedCode:
        """Generate reconnaissance script"""
        print(f"[*] Generating reconnaissance script...")
        
        objectives_str = '\n'.join(f"- {obj}" for obj in objectives)
        
        prompt = f"""Generate a Bash reconnaissance script for:

Target Type: {target_type}
Objectives:
{objectives_str}

Requirements:
1. Use common tools (nmap, dig, curl, etc.)
2. Error handling
3. Clear output format
4. Save results to files
5. Progress indicators

Provide ONLY the Bash script, no explanations."""

        code = self._call_ai_model(prompt)
        
        return GeneratedCode(
            code_type="script",
            language="bash",
            description=f"Reconnaissance script for {target_type}",
            code=code,
            dependencies=self._extract_tools(code),
            usage_instructions="./recon.sh <target>",
            generated_at=datetime.now().isoformat()
        )
    
    def generate_automation_tool(self, tool_description: str, features: List[str]) -> GeneratedCode:
        """Generate automation tool"""
        print(f"[*] Generating automation tool...")
        
        features_str = '\n'.join(f"- {feat}" for feat in features)
        
        prompt = f"""Generate a Python automation tool:

Description: {tool_description}
Features:
{features_str}

Requirements:
1. Object-oriented design
2. CLI interface with argparse
3. Configuration file support
4. Logging
5. Modular architecture

Provide ONLY the Python code, no explanations."""

        code = self._call_ai_model(prompt)
        
        return GeneratedCode(
            code_type="tool",
            language="python",
            description=tool_description,
            code=code,
            dependencies=self._extract_dependencies(code),
            usage_instructions=self._extract_usage(code),
            generated_at=datetime.now().isoformat()
        )
    
    def generate_payload(self, payload_type: str, target_platform: str, delivery_method: str) -> GeneratedCode:
        """Generate payload code"""
        print(f"[*] Generating payload...")
        
        prompt = f"""Generate a {payload_type} payload for:

Target Platform: {target_platform}
Delivery Method: {delivery_method}

Requirements:
1. Stealthy execution
2. Error handling
3. Clean exit
4. No unnecessary output
5. Obfuscation where appropriate

Provide ONLY the code, no explanations."""

        code = self._call_ai_model(prompt)
        
        # Detect language from payload type
        language_map = {
            'powershell': 'powershell',
            'bash': 'bash',
            'python': 'python',
            'php': 'php',
            'javascript': 'javascript'
        }
        language = language_map.get(payload_type.lower(), 'unknown')
        
        return GeneratedCode(
            code_type="payload",
            language=language,
            description=f"{payload_type} payload for {target_platform}",
            code=code,
            dependencies=[],
            usage_instructions=f"Execute on {target_platform} via {delivery_method}",
            generated_at=datetime.now().isoformat()
        )
    
    def _call_ai_model(self, prompt: str) -> str:
        """Call AI model (Claude or GLASSEYE)"""
        # Try Claude first
        try:
            response = requests.post(
                f"{self.claude_url}/chat",
                json={
                    "model": "claude",
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
        except Exception as e:
            print(f"[!] Claude API unavailable: {e}")
        
        # Fallback to GLASSEYE
        try:
            response = requests.post(
                f"{self.glasseye_url}/analyze",
                json={"text": prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('analysis', '')
        except Exception as e:
            print(f"[!] GLASSEYE API unavailable: {e}")
        
        # Ultimate fallback: template
        return self._generate_template(prompt)
    
    def _generate_template(self, prompt: str) -> str:
        """Generate template code when AI is unavailable"""
        print(f"[!] AI unavailable, generating template...")
        
        if 'exploit' in prompt.lower():
            return '''#!/usr/bin/env python3
"""
Auto-generated exploit template
Edit this template to match your specific vulnerability
"""

import sys
import requests

def exploit(target):
    """Main exploit function"""
    print(f"[*] Targeting: {target}")
    
    # TODO: Implement exploit logic here
    
    print(f"[+] Exploit complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 exploit.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    exploit(target)
'''
        
        elif 'recon' in prompt.lower() or 'bash' in prompt.lower():
            return '''#!/bin/bash
# Auto-generated reconnaissance script
# Edit this template to match your specific needs

TARGET=$1

if [ -z "$TARGET" ]; then
    echo "Usage: ./recon.sh <target>"
    exit 1
fi

echo "[*] Reconnaissance on $TARGET"

# TODO: Add reconnaissance commands here
# nmap -sV $TARGET
# dig $TARGET
# curl -I https://$TARGET

echo "[+] Reconnaissance complete!"
'''
        
        else:
            return '''#!/usr/bin/env python3
"""
Auto-generated tool template
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Auto-generated tool')
    parser.add_argument('target', help='Target specification')
    args = parser.parse_args()
    
    print(f"[*] Processing: {args.target}")
    
    # TODO: Implement tool logic here
    
    print(f"[+] Complete!")

if __name__ == "__main__":
    main()
'''
    
    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract Python dependencies from code"""
        deps = []
        
        for line in code.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # Extract module name
                parts = line.strip().split()
                if len(parts) >= 2:
                    module = parts[1].split('.')[0]
                    if module not in ['sys', 'os', 'json', 'time', 'datetime']:
                        deps.append(module)
        
        return list(set(deps))
    
    def _extract_tools(self, code: str) -> List[str]:
        """Extract required tools from bash script"""
        tools = []
        common_tools = ['nmap', 'dig', 'curl', 'wget', 'netcat', 'nc', 'nikto', 'gobuster', 
                       'sqlmap', 'hydra', 'john', 'hashcat']
        
        for tool in common_tools:
            if tool in code:
                tools.append(tool)
        
        return list(set(tools))
    
    def _extract_usage(self, code: str) -> str:
        """Extract usage instructions from code"""
        for line in code.split('\n'):
            if 'Usage:' in line or 'usage:' in line:
                return line.strip().replace('#', '').strip()
        
        return "See code comments for usage"
    
    def save_code(self, generated: GeneratedCode) -> str:
        """Save generated code to file"""
        # Determine file extension
        ext_map = {
            'python': '.py',
            'bash': '.sh',
            'powershell': '.ps1',
            'php': '.php',
            'javascript': '.js'
        }
        ext = ext_map.get(generated.language, '.txt')
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"glasseye_{generated.code_type}_{timestamp}{ext}"
        filepath = f"/home/x/glasseye/generated/{filename}"
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save code
        with open(filepath, 'w') as f:
            f.write(generated.code)
        
        # Make executable if script
        if ext in ['.py', '.sh']:
            Path(filepath).chmod(0o755)
        
        # Save metadata
        meta_file = filepath + '.meta.json'
        with open(meta_file, 'w') as f:
            json.dump({
                'code_type': generated.code_type,
                'language': generated.language,
                'description': generated.description,
                'dependencies': generated.dependencies,
                'usage_instructions': generated.usage_instructions,
                'generated_at': generated.generated_at
            }, f, indent=2)
        
        print(f"[+] Code saved to: {filepath}")
        print(f"[+] Metadata saved to: {meta_file}")
        
        if generated.dependencies:
            print(f"[*] Dependencies: {', '.join(generated.dependencies)}")
        print(f"[*] Usage: {generated.usage_instructions}")
        
        return filepath


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ai_code_generator.py <command> [args...]")
        print("\nCommands:")
        print("  exploit <vuln_desc> <target_info>  - Generate exploit")
        print("  recon <target_type> <objectives>   - Generate recon script")
        print("  tool <description> <features>      - Generate automation tool")
        print("  payload <type> <platform> <method> - Generate payload")
        sys.exit(1)
    
    command = sys.argv[1]
    generator = AICodeGenerator()
    
    if command == 'exploit':
        if len(sys.argv) < 4:
            print("Usage: ai_code_generator.py exploit <vuln_desc> <target_info>")
            sys.exit(1)
        
        vuln_desc = sys.argv[2]
        target_info = sys.argv[3]
        
        generated = generator.generate_exploit(vuln_desc, target_info)
        filepath = generator.save_code(generated)
        
    elif command == 'recon':
        if len(sys.argv) < 4:
            print("Usage: ai_code_generator.py recon <target_type> <objective1,objective2,...>")
            sys.exit(1)
        
        target_type = sys.argv[2]
        objectives = sys.argv[3].split(',')
        
        generated = generator.generate_recon_script(target_type, objectives)
        filepath = generator.save_code(generated)
        
    elif command == 'tool':
        if len(sys.argv) < 4:
            print("Usage: ai_code_generator.py tool <description> <feature1,feature2,...>")
            sys.exit(1)
        
        description = sys.argv[2]
        features = sys.argv[3].split(',')
        
        generated = generator.generate_automation_tool(description, features)
        filepath = generator.save_code(generated)
        
    elif command == 'payload':
        if len(sys.argv) < 5:
            print("Usage: ai_code_generator.py payload <type> <platform> <method>")
            sys.exit(1)
        
        payload_type = sys.argv[2]
        platform = sys.argv[3]
        method = sys.argv[4]
        
        generated = generator.generate_payload(payload_type, platform, method)
        filepath = generator.save_code(generated)
    
    else:
        print(f"[-] Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
