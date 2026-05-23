#!/usr/bin/env python3
"""
Tool Generator Demo
Demonstrates autonomous tool generation capabilities.
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from tool_generator import ToolGenerator, AttackSurface
from compliance_enforcer import RiskLevel


def demo_fuzzer_generation():
    """Demo: Generate a JSON-RPC fuzzer."""
    print("\n" + "="*60)
    print("DEMO 1: Generating JSON-RPC Fuzzer")
    print("="*60)
    
    gen = ToolGenerator()
    
    try:
        fuzzer_path = gen.generate_fuzzer(
            protocol='JSON-RPC 2.0',
            transport='STDIO',
            target='github-copilot-mcp',
            endpoints=['tools/list', 'tools/call']
        )
        
        print(f"✓ Fuzzer generated: {fuzzer_path}")
        print(f"  - Protocol: JSON-RPC 2.0")
        print(f"  - Transport: STDIO")
        print(f"  - Target: github-copilot-mcp")
        
        # Show first 20 lines
        with open(fuzzer_path, 'r') as f:
            lines = f.readlines()[:20]
            print("\nGenerated code preview:")
            print("".join(lines))
            
    except Exception as e:
        print(f"✗ Error: {e}")
        

def demo_protocol_analyzer():
    """Demo: Generate a protocol analyzer."""
    print("\n" + "="*60)
    print("DEMO 2: Generating Protocol Analyzer")
    print("="*60)
    
    gen = ToolGenerator()
    
    try:
        analyzer_path = gen.generate_protocol_analyzer({
            'name': 'MCP Protocol',
            'target': 'copilot-mcp-server',
            'message_format': 'JSON-RPC 2.0',
            'authentication': 'OAuth tokens'
        })
        
        print(f"✓ Analyzer generated: {analyzer_path}")
        print(f"  - Protocol: MCP Protocol")
        print(f"  - Format: JSON-RPC 2.0")
        print(f"  - Auth: OAuth tokens")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_mcp_skill():
    """Demo: Generate an MCP skill."""
    print("\n" + "="*60)
    print("DEMO 3: Generating MCP Skill")
    print("="*60)
    
    gen = ToolGenerator()
    
    try:
        skill_path = gen.generate_mcp_skill(
            capability='github-api-security-scanner',
            description='Scan GitHub API endpoints for security issues',
            tools_list=[
                'github_api_fuzzer',
                'github_auth_tester',
                'github_rate_limit_analyzer'
            ]
        )
        
        print(f"✓ MCP Skill generated: {skill_path}")
        print(f"  - Capability: github-api-security-scanner")
        print(f"  - Tools: 3 tools included")
        
        # List generated files
        skill_dir = Path(skill_path)
        files = list(skill_dir.glob('*'))
        print(f"\n  Generated files:")
        for f in files:
            print(f"    - {f.name}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_attack_surface_analysis():
    """Demo: Analyze attack surface and generate tools."""
    print("\n" + "="*60)
    print("DEMO 4: Attack Surface Analysis & Tool Generation")
    print("="*60)
    
    # Define an attack surface
    attack_surface = AttackSurface(
        name='github-copilot-mcp-server',
        protocol='JSON-RPC 2.0',
        transport='STDIO',
        authentication='OAuth bearer tokens',
        attack_vectors=[
            'command injection',
            'authorization bypass',
            'prompt injection'
        ],
        endpoints=[
            'tools/list',
            'tools/call',
            'resources/list',
            'resources/read'
        ],
        metadata={
            'version': '1.0.0',
            'vendor': 'GitHub',
            'scope': 'authorized_testing'
        }
    )
    
    print(f"Attack Surface: {attack_surface.name}")
    print(f"  Protocol: {attack_surface.protocol}")
    print(f"  Transport: {attack_surface.transport}")
    print(f"  Auth: {attack_surface.authentication}")
    print(f"  Attack Vectors: {len(attack_surface.attack_vectors)}")
    
    gen = ToolGenerator()
    
    # Analyze
    tools_needed = gen.analyze_attack_surface(attack_surface)
    
    print(f"\n✓ Analysis complete: {len(tools_needed)} tools recommended")
    for tool in tools_needed:
        print(f"    - {tool}")
        
    # Generate all tools
    print(f"\nGenerating tools...")
    
    try:
        generated = gen.generate_tool_from_attack_surface(attack_surface)
        
        print(f"\n✓ Generated {len(generated)} tools:")
        for tool_path in generated:
            print(f"    - {Path(tool_path).name}")
            
    except Exception as e:
        print(f"✗ Error during generation: {e}")
        print(f"   (This may be due to compliance checks - expected in demo)")


def demo_code_validation():
    """Demo: Code validation."""
    print("\n" + "="*60)
    print("DEMO 5: Code Validation")
    print("="*60)
    
    gen = ToolGenerator()
    
    # Valid code
    valid_code = '''
def hello():
    print("Hello, world!")
    return True
'''
    
    print("Testing valid code...")
    result = gen.validate_generated_code(valid_code)
    print(f"  Result: {'✓ PASS' if result else '✗ FAIL'}")
    
    # Invalid code
    invalid_code = '''
def broken(
    print("Missing paren")
'''
    
    print("\nTesting invalid code...")
    result = gen.validate_generated_code(invalid_code)
    print(f"  Result: {'✓ PASS' if result else '✗ FAIL (expected)'}")
    
    # Code with dangerous patterns
    dangerous_code = '''
import os
os.system("rm -rf /")
'''
    
    print("\nTesting dangerous pattern detection...")
    result = gen.validate_generated_code(dangerous_code)
    print(f"  Result: {'✓ PASS with warnings' if result else '✗ FAIL'}")
    print(f"  (Code validation warns about dangerous patterns)")


def demo_template_system():
    """Demo: Template system."""
    print("\n" + "="*60)
    print("DEMO 6: Template System")
    print("="*60)
    
    gen = ToolGenerator()
    
    print("Available tool categories:")
    for category, templates in gen.tool_categories.items():
        print(f"\n  {category.upper()}:")
        for template in templates:
            print(f"    - {template}")
            
    print(f"\nTemplates directory: {gen.templates_dir}")
    
    # List actual template files
    template_files = list(gen.templates_dir.glob('*_template.py'))
    print(f"\nInstalled templates ({len(template_files)}):")
    for template in template_files:
        print(f"    - {template.name}")


def main():
    """Run all demos."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   GlasseyeOS AI - Autonomous Tool Generator Demo            ║
║   Production-grade security tool generation with             ║
║   compliance enforcement and template-based architecture     ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    try:
        demo_template_system()
        demo_code_validation()
        demo_fuzzer_generation()
        demo_protocol_analyzer()
        demo_mcp_skill()
        demo_attack_surface_analysis()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nAll generated tools are in: generated_tools/")
        print("All generated skills are in: generated_skills/")
        print("\nNext steps:")
        print("  1. Review generated tools for correctness")
        print("  2. Customize templates in templates/")
        print("  3. Run unit tests: python tests/test_tool_generator.py")
        print("  4. Integrate with GlasseyeOS core workflow")
        
    except Exception as e:
        print(f"\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0


if __name__ == '__main__':
    sys.exit(main())
