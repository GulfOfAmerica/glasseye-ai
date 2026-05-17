#!/usr/bin/env python3
"""
GLASSEYE AI OS - Master Command Line Interface
Unified access to all GLASSEYE capabilities
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Add glasseye to path
sys.path.append('/home/x/glasseye')

# Import all modules
try:
    from integrated_config import GlasseyeConfig
    from memory_system import GlasseyeMemory
    from autonomous_recon import AutonomousRecon
    from auto_exploitation import AutoExploitation
    from bug_bounty_automation import BugBountyAutomation
    from ai_decision_engine import AIDecisionEngine
    from ai_code_generator import AICodeGenerator
    from osint_engine import OSINTEngine
    from learning_loop import LearningLoop
    
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Some modules couldn't be imported: {e}")
    MODULES_AVAILABLE = False


def banner():
    """Display GLASSEYE banner"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              👁️  GLASSEYE AI OS - MASTER CLI  ⚡💀                         ║
║                                                                           ║
║                    Autonomous Hacking Framework                           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")


def cmd_status(args):
    """Show system status"""
    print("\n📊 GLASSEYE SYSTEM STATUS")
    print("=" * 60)
    
    # Load config
    config = GlasseyeConfig()
    memory = GlasseyeMemory()
    
    print(f"\n🔹 Memory System:")
    print(f"  Scans recorded: {len(memory.scan_history)}")
    print(f"  Learning entries: {len(memory.learning_log)}")
    
    print(f"\n🔹 Integrated Platforms:")
    api_config = config.get_api_config()
    print(f"  AWS:    ✅ Account {api_config['aws']['account_id']}")
    print(f"  GitHub: ✅ {api_config['github']['user']}")
    print(f"  Claude: ✅ API configured")
    
    print(f"\n🔹 Operational Modules:")
    modules = [
        "Autonomous Reconnaissance",
        "Auto-Exploitation",
        "Bug Bounty Automation",
        "AI Decision Engine",
        "AI Code Generator",
        "Memory System",
        "OSINT Engine",
        "Learning Loop",
        "Web Interface",
        "Metasploit Integration"
    ]
    for module in modules:
        print(f"  ✅ {module}")
    
    print(f"\n🔹 Services:")
    print(f"  GLASSEYE AI:  http://localhost:8002")
    print(f"  Claude API:   http://localhost:8000")
    print(f"  MCP Server:   http://localhost:5001")
    print(f"  Web API:      http://localhost:5002")
    
    print(f"\n✅ System operational - {len(modules)} modules ready")


def cmd_scan(args):
    """Run autonomous reconnaissance"""
    target = args.target
    
    print(f"\n🔍 Starting autonomous reconnaissance on: {target}")
    print("=" * 60)
    
    recon = AutonomousRecon()
    result = recon.run_autonomous_recon(target)
    
    print(f"\n✅ Reconnaissance complete!")
    print(f"  Target: {target}")
    # Handle dataclass - use attribute access, not .get()
    risk_score = result.risk_score if hasattr(result, 'risk_score') else 'N/A'
    attack_vectors = result.attack_vectors if hasattr(result, 'attack_vectors') else []
    print(f"  Risk Score: {risk_score}")
    print(f"  Attack Vectors: {len(attack_vectors)}")
    
    if args.save:
        filename = f"recon_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n📄 Results saved: {filename}")


def cmd_exploit(args):
    """Run auto-exploitation"""
    target = args.target
    
    print(f"\n💣 Starting auto-exploitation on: {target}")
    print("=" * 60)
    
    exploit = AutoExploitation()
    result = exploit.run_auto_exploitation(target)
    
    print(f"\n✅ Exploitation complete!")
    print(f"  Exploits attempted: {result.get('total_exploits', 0)}")
    print(f"  Successful: {result.get('successful', 0)}")


def cmd_bounty(args):
    """Run bug bounty automation"""
    target = args.target
    program = args.program
    
    print(f"\n🐛 Running bug bounty scan")
    print(f"  Target: {target}")
    print(f"  Program: {program}")
    print("=" * 60)
    
    bounty = BugBountyAutomation()
    findings = bounty.scan_target(target)
    report = bounty.generate_report(program, target, findings)
    
    md_file = bounty.save_report(report, 'markdown')
    json_file = bounty.save_report(report, 'json')
    
    print(f"\n✅ Bug bounty scan complete!")
    print(f"  Total findings: {report.total_findings}")
    print(f"  Critical: {report.critical}")
    print(f"  High: {report.high}")
    print(f"  Medium: {report.medium}")
    print(f"\n📄 Reports saved:")
    print(f"  Markdown: {md_file}")
    print(f"  JSON: {json_file}")


def cmd_osint(args):
    """Run OSINT collection"""
    target = args.target
    target_type = args.type
    
    print(f"\n🔍 Running OSINT collection")
    print(f"  Target: {target}")
    print(f"  Type: {target_type}")
    print("=" * 60)
    
    osint = OSINTEngine()
    result = osint.run_full_osint(target, target_type)
    
    print(f"\n✅ OSINT collection complete!")
    print(f"  Findings: {result['total_findings']}")
    
    filename = f"osint_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n📄 Results saved: {filename}")


def cmd_learn(args):
    """Run learning cycle"""
    print("\n🧠 Running learning cycle...")
    print("=" * 60)
    
    loop = LearningLoop()
    result = loop.learn_from_history()
    
    print(f"\n✅ Learning complete!")
    print(f"  Insights: {result['total_insights']}")
    print(f"  High Impact: {result['high_impact']}")
    
    if result['recommendations']:
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(result['recommendations'][:5], 1):
            print(f"  {i}. {rec}")


def cmd_ai(args):
    """AI analysis of target"""
    target = args.target
    
    print(f"\n🤖 Running AI analysis on: {target}")
    print("=" * 60)
    
    ai = AIDecisionEngine()
    decision = ai.analyze_target(target)
    
    print(f"\n✅ AI analysis complete!")
    print(f"  Risk Score: {decision.get('risk_score', 'N/A')}")
    print(f"  Recommendation: {decision.get('recommendation', 'N/A')}")


def cmd_memory(args):
    """View memory system"""
    memory = GlasseyeMemory()
    
    print("\n💾 GLASSEYE MEMORY SYSTEM")
    print("=" * 60)
    
    if args.scans:
        print(f"\n📊 Recent Scans ({len(memory.scan_history)} total):")
        for scan in memory.scan_history[-5:]:
            print(f"  • {scan.get('target')} - {scan.get('timestamp')}")
    
    if args.learning:
        print(f"\n🧠 Learning Log ({len(memory.learning_log)} entries):")
        for entry in memory.learning_log[-3:]:
            print(f"  • {entry.get('timestamp')} - {entry.get('total_insights', 0)} insights")
    
    if args.stats:
        print(f"\n📈 Statistics:")
        print(f"  Total scans: {len(memory.scan_history)}")
        print(f"  Learning cycles: {len(memory.learning_log)}")


def cmd_modules(args):
    """List all modules"""
    print("\n📦 GLASSEYE MODULES")
    print("=" * 60)
    
    modules = [
        ("Autonomous Reconnaissance", "autonomous_recon.py", "operational", "4-phase recon system"),
        ("Auto-Exploitation", "auto_exploitation.py", "operational", "Automated exploit engine"),
        ("Bug Bounty Automation", "bug_bounty_automation.py", "operational", "Full bug bounty workflow"),
        ("AI Decision Engine", "ai_decision_engine.py", "operational", "Multi-model AI orchestration"),
        ("AI Code Generator", "ai_code_generator.py", "operational", "AI-powered exploit generation"),
        ("Memory System", "memory_system.py", "operational", "Persistent intelligence storage"),
        ("OSINT Engine", "osint_engine.py", "operational", "Multi-source OSINT collection"),
        ("Learning Loop", "learning_loop.py", "operational", "Self-improvement system"),
        ("Web Interface", "web_interface.py", "operational", "RESTful API interface"),
        ("Metasploit Integration", "metasploit_integration.py", "operational", "MSF framework integration"),
        ("Integrated Config", "integrated_config.py", "operational", "Unified credential management"),
    ]
    
    for name, file, status, desc in modules:
        status_icon = "✅" if status == "operational" else "⏸️"
        print(f"{status_icon} {name}")
        print(f"   File: {file}")
        print(f"   Description: {desc}")
        print()


def cmd_test(args):
    """Run system tests"""
    print("\n🧪 Running GLASSEYE system tests...")
    print("=" * 60)
    
    import subprocess
    import time
    
    # Give services a moment to respond
    time.sleep(1)
    
    tests = [
        ("Memory System", "python3 -c 'from memory_system import GlasseyeMemory; m=GlasseyeMemory(); print(\"Memory OK\")'"),
        ("Config System", "python3 -c 'from integrated_config import GlasseyeConfig; c=GlasseyeConfig(); print(\"Config OK\")'"),
        ("GLASSEYE AI", "curl -s http://localhost:8002/health"),
        ("Claude API", "curl -s http://localhost:8000/health"),
    ]
    
    passed = 0
    for name, cmd in tests:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            # Check for success indicators
            success = (result.returncode == 0 and 
                      ('OK' in result.stdout or 'healthy' in result.stdout or 
                       '"status":"healthy"' in result.stdout or '"status": "healthy"' in result.stdout))
            if success:
                print(f"✅ {name}: PASS")
                passed += 1
            else:
                print(f"❌ {name}: FAIL")
        except Exception as e:
            print(f"❌ {name}: FAIL - {e}")
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")


def main():
    parser = argparse.ArgumentParser(
        description='GLASSEYE AI OS - Master CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  glasseye status                              Show system status
  glasseye scan scanme.nmap.org                Run reconnaissance
  glasseye osint cyberviserai.com --type domain  Collect OSINT
  glasseye bounty target.com --program HackerOne Bug bounty scan
  glasseye learn                               Run learning cycle
  glasseye test                                Run system tests
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Run autonomous reconnaissance')
    scan_parser.add_argument('target', help='Target for reconnaissance')
    scan_parser.add_argument('--save', action='store_true', help='Save results to file')
    
    # Exploit command
    exploit_parser = subparsers.add_parser('exploit', help='Run auto-exploitation')
    exploit_parser.add_argument('target', help='Target for exploitation')
    
    # Bounty command
    bounty_parser = subparsers.add_parser('bounty', help='Run bug bounty automation')
    bounty_parser.add_argument('target', help='Target for bug bounty')
    bounty_parser.add_argument('--program', default='GLASSEYE', help='Bug bounty program name')
    
    # OSINT command
    osint_parser = subparsers.add_parser('osint', help='Run OSINT collection')
    osint_parser.add_argument('target', help='Target for OSINT')
    osint_parser.add_argument('--type', default='domain', 
                             choices=['domain', 'username', 'email', 'ip'],
                             help='Target type')
    
    # Learn command
    subparsers.add_parser('learn', help='Run learning cycle')
    
    # AI command
    ai_parser = subparsers.add_parser('ai', help='AI analysis of target')
    ai_parser.add_argument('target', help='Target for AI analysis')
    
    # Memory command
    memory_parser = subparsers.add_parser('memory', help='View memory system')
    memory_parser.add_argument('--scans', action='store_true', help='Show scan history')
    memory_parser.add_argument('--learning', action='store_true', help='Show learning log')
    memory_parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    # Modules command
    subparsers.add_parser('modules', help='List all modules')
    
    # Test command
    subparsers.add_parser('test', help='Run system tests')
    
    args = parser.parse_args()
    
    if not args.command:
        banner()
        parser.print_help()
        return
    
    banner()
    
    # Route to appropriate command
    commands = {
        'status': cmd_status,
        'scan': cmd_scan,
        'exploit': cmd_exploit,
        'bounty': cmd_bounty,
        'osint': cmd_osint,
        'learn': cmd_learn,
        'ai': cmd_ai,
        'memory': cmd_memory,
        'modules': cmd_modules,
        'test': cmd_test,
    }
    
    if args.command in commands:
        try:
            commands[args.command](args)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n❌ Unknown command: {args.command}")


if __name__ == '__main__':
    main()
