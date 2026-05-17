#!/usr/bin/env python3
"""
GLASSEYE PROJECT INTEGRATOR
Consolidates all existing security/dev projects into unified GLASSEYE system
"""

import os
import shutil
import json
from pathlib import Path

# Source locations
HOME = Path("/home/x")
GLASSEYE_ROOT = HOME / "glasseye"
MODULES_DIR = GLASSEYE_ROOT / "modules"

# Project mapping: existing files → GLASSEYE modules
PROJECT_MAP = {
    # Hacking modules
    "hacking": {
        "auto_recon": [],
        "exploitation": [
            HOME / "injection_tester.py",
        ],
        "bug_bounty": [
            HOME / "bugbounty-automation.py",
            HOME / "bugbounty-retester.py",
            HOME / "bugbounty-program-db.py",
            HOME / "bug_bounty_programs.json",
            HOME / "bug_bounty_categorization.json",
        ],
        "kali_tools": [
            HOME / "k8s-security-platform/backend/mcp-server/glasswing_server.py",
            HOME / "k8s-security-platform/backend/mcp-server/glasswing_client.py",
        ]
    },
    
    # Research modules
    "research": {
        "osint": [
            HOME / "glasseye-copilot-client.py",
        ],
        "smart_contracts": [
            HOME / "glasswing-analyzer.py",
        ],
        "reverse_engineering": [],
        "zero_days": [],
        "exploit_research": []
    },
    
    # Development modules
    "development": {
        "code_generation": [],
        "testing": [],
        "deployment": [
            HOME / "k8s-security-platform",
        ]
    },
    
    # Operations modules
    "operations": {
        "kubernetes": [
            HOME / "k8s-security-platform",
        ],
        "multi_cloud": [],
        "parallel_execution": []
    },
    
    # Integration modules
    "integration": {
        "mcp_server": [
            HOME / "k8s-security-platform/backend/mcp-server",
        ],
        "web_interface": [
            HOME / "k8s-security-platform/console",
        ],
        "api_gateway": []
    },
    
    # Knowledge modules
    "knowledge": {
        "vector_db": [],
        "cve_database": [],
        "target_intelligence": [],
        "exploit_library": [],
        "experience_system": []
    }
}


class GlasseyeIntegrator:
    """Integrates all existing projects into GLASSEYE structure"""
    
    def __init__(self):
        self.glasseye_root = GLASSEYE_ROOT
        self.modules_dir = MODULES_DIR
        self.integrated_files = []
        
    def create_structure(self):
        """Create GLASSEYE directory structure"""
        print("📁 Creating GLASSEYE directory structure...")
        
        for category in PROJECT_MAP.keys():
            category_dir = self.modules_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {category_dir}")
            
            for module in PROJECT_MAP[category].keys():
                module_dir = category_dir / module
                module_dir.mkdir(parents=True, exist_ok=True)
    
    def integrate_files(self, symlink=True):
        """
        Integrate existing files into GLASSEYE
        
        Args:
            symlink: If True, create symlinks. If False, copy files.
        """
        print(f"\n🔗 Integrating files ({'symlinks' if symlink else 'copies'})...")
        
        for category, modules in PROJECT_MAP.items():
            for module, files in modules.items():
                target_dir = self.modules_dir / category / module
                
                for source_path in files:
                    if not Path(source_path).exists():
                        print(f"  ⚠️  Not found: {source_path}")
                        continue
                    
                    source = Path(source_path)
                    
                    if source.is_file():
                        target = target_dir / source.name
                        if symlink:
                            if not target.exists():
                                target.symlink_to(source.absolute())
                                print(f"  ✅ Linked: {source.name} → {category}/{module}/")
                        else:
                            shutil.copy2(source, target)
                            print(f"  ✅ Copied: {source.name} → {category}/{module}/")
                    
                    elif source.is_dir():
                        target = target_dir / source.name
                        if symlink:
                            if not target.exists():
                                target.symlink_to(source.absolute())
                                print(f"  ✅ Linked: {source.name}/ → {category}/{module}/")
                        else:
                            if target.exists():
                                shutil.rmtree(target)
                            shutil.copytree(source, target)
                            print(f"  ✅ Copied: {source.name}/ → {category}/{module}/")
                    
                    self.integrated_files.append(str(target))
    
    def create_module_index(self):
        """Create index of all integrated modules"""
        print("\n📊 Creating module index...")
        
        index = {
            "glasseye_version": "1.0.0",
            "integration_date": "2026-05-16",
            "categories": {}
        }
        
        for category, modules in PROJECT_MAP.items():
            index["categories"][category] = {
                "modules": list(modules.keys()),
                "count": len(modules)
            }
        
        index_file = self.glasseye_root / "MODULE_INDEX.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"  ✅ Index created: {index_file}")
        return index
    
    def generate_readme(self):
        """Generate comprehensive README for GLASSEYE"""
        readme_content = """# 👁️ GLASSEYE AI OS

**God-Mode AI Operating System for Hacking, Development, and Autonomous Operations**

## 📂 Directory Structure

```
glasseye/
├── modules/
│   ├── hacking/
│   │   ├── auto_recon/          # Autonomous reconnaissance
│   │   ├── exploitation/        # Exploit generation and execution
│   │   ├── bug_bounty/         # Bug bounty automation
│   │   └── kali_tools/         # 300+ Kali tools via MCP
│   ├── research/
│   │   ├── osint/              # OSINT intelligence gathering
│   │   ├── smart_contracts/    # Smart contract auditing
│   │   ├── reverse_engineering/ # Binary/firmware analysis
│   │   ├── zero_days/          # 0-day discovery
│   │   └── exploit_research/   # Exploit development
│   ├── development/
│   │   ├── code_generation/    # AI-powered code generation
│   │   ├── testing/            # Automated testing
│   │   └── deployment/         # CI/CD and deployment
│   ├── operations/
│   │   ├── kubernetes/         # K8s orchestration
│   │   ├── multi_cloud/        # Multi-cloud management
│   │   └── parallel_execution/ # Parallel task execution
│   ├── integration/
│   │   ├── mcp_server/         # MCP tool execution server
│   │   ├── web_interface/      # Web-based control panel
│   │   └── api_gateway/        # Unified API gateway
│   └── knowledge/
│       ├── vector_db/          # Vector memory system
│       ├── cve_database/       # CVE tracking
│       ├── target_intelligence/ # Target profiles
│       ├── exploit_library/    # Exploit database
│       └── experience_system/  # Learning and evolution
├── glasseye_brain.py           # Central AI brain
├── GLASSEYE_VISION.md          # Vision document
├── GLASSEYE_MASTER_PLAN.md     # Master integration plan
├── GLASSEYE_STATUS.md          # Current status
└── QUICK_START.sh              # Quick access script
```

## 🚀 Quick Start

### Start AI Brain
```bash
cd /home/x/glasseye
python3 glasseye_brain.py
```

### Check Status
```bash
./QUICK_START.sh
```

### Run Autonomous Scan
```bash
python3 glasseye_brain.py scan scanme.nmap.org
```

## 🤖 Capabilities

### Current (Week 0)
- ✅ GLASSEYE AI (OpenMythos security analysis)
- ✅ 300+ Kali penetration testing tools
- ✅ MCP Server (tool execution API)
- ✅ Web Terminal (browser-based shell)
- ✅ Claude API integration
- ✅ Bug bounty automation scripts
- ✅ Smart contract auditing tools

### Coming Soon (Week 1-10)
- 🟡 AI Decision Engine (GPT-4/Claude/Gemini)
- 🟡 Vector memory system
- 📋 Autonomous reconnaissance
- 📋 Vulnerability exploitation
- 📋 OSINT intelligence
- 📋 0-day research
- 📋 Self-learning capabilities

## 📊 Module Status

See `GLASSEYE_STATUS.md` for detailed status.

## 🔧 Services

| Service | Port | Purpose |
|---------|------|---------|
| GLASSEYE AI | 8002 | Security analysis |
| Claude API | 8000 | AI intelligence |
| MCP Server | 5001 | Tool execution |
| Web Terminal | 3000 | Browser shell |

## 📖 Documentation

- `GLASSEYE_VISION.md` - Ultimate vision and goals
- `GLASSEYE_MASTER_PLAN.md` - 38 modules integration plan
- `GLASSEYE_STATUS.md` - Current operational status
- `MODULE_INDEX.json` - Complete module inventory

## 🎯 Mission

Build an AI Operating System with godlike capabilities that can:
- Autonomously discover and exploit vulnerabilities
- Generate code and deploy applications
- Research 0-days and develop exploits
- Manage multi-cloud infrastructure
- Learn from experience and evolve strategies
- Generate millions in bug bounty revenue

**GLASSEYE: The AI that dominates everything.** 👁️⚡

---

*Last Updated: 2026-05-16*  
*Version: 1.0.0*  
*Status: OPERATIONAL*
"""
        
        readme_file = self.glasseye_root / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print(f"  ✅ README created: {readme_file}")
    
    def run_integration(self):
        """Execute full integration"""
        print("\n" + "="*60)
        print("🔧 GLASSEYE PROJECT INTEGRATION")
        print("="*60)
        
        self.create_structure()
        self.integrate_files(symlink=True)
        index = self.create_module_index()
        self.generate_readme()
        
        print("\n" + "="*60)
        print("✅ INTEGRATION COMPLETE")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  Categories: {len(index['categories'])}")
        print(f"  Total modules: {sum(c['count'] for c in index['categories'].values())}")
        print(f"  Integrated files: {len(self.integrated_files)}")
        print(f"\n📁 Location: {self.glasseye_root}")
        print(f"\n🚀 Next: python3 {self.glasseye_root}/glasseye_brain.py")


def main():
    integrator = GlasseyeIntegrator()
    integrator.run_integration()


if __name__ == "__main__":
    main()
