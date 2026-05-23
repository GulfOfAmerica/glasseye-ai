# GlasseyeOS AI - Autonomous Bug Bounty Intelligence Platform

**Version:** 1.0.0  
**Status:** Production-Ready Intelligence Platform

---

## 🎯 Mission

GlasseyeOS AI is an autonomous intelligence platform for ethical bug bounty research. It **assists** human security researchers with reconnaissance, vulnerability hypothesis generation, and tool creation while maintaining strict compliance with bug bounty program rules and safe harbor protections.

**CRITICAL:** This is an INTELLIGENCE platform, not an autonomous hacking tool. All exploitation requires human approval.

---

## 🏗️ Architecture

### Core Components

1. **Master Intelligence Engine** (`glasseye_core.py`)
   - Autonomous reconnaissance planning
   - CVE feed monitoring (NVD, GitHub Security Advisories)
   - Attack surface analysis from public documentation
   - Vulnerability hypothesis generation
   - Campaign orchestration with human approval gates

2. **Compliance Guardian** (`compliance_enforcer.py`)
   - Autonomous safety system
   - Verify all actions against safe harbor protections
   - Auto-block out-of-scope testing
   - Prevent PII access attempts
   - Emergency stop mechanism
   - Complete audit trail

3. **Knowledge Base** (`knowledge_base.py`)
   - SQLite-based intelligence database
   - CVE intelligence and patterns
   - Disclosed bug bounty findings
   - Auto-generated tools and skills
   - Active campaign state
   - Learned attack patterns

4. **Self-Update Framework** (`self_updater.py`)
   - Monitor security research repositories
   - Download and analyze new CVE data
   - Update vulnerability patterns database
   - Generate new testing strategies
   - Self-upgrade capability

5. **Agent Orchestrator** (`agent_orchestrator.py`)
   - Multi-agent coordination
   - Spawn specialized sub-agents
   - Distribute fuzzing workload
   - Aggregate findings
   - Prioritize work by expected ROI

---

## 🚀 Quick Start

### Installation

```bash
cd /home/x/GlasseyeOS-AI/

# Install dependencies
pip install -r requirements.txt

# Initialize knowledge base
python knowledge_base.py

# Run tests
python tests/test_all.py

# Run demo
python demo.py
```

### Requirements

Create `requirements.txt`:
```
requests>=2.31.0
pyyaml>=6.0
```

### Basic Usage

```python
from glasseye_core import GlasseyeAI, Target

# Initialize AI engine
ai = GlasseyeAI()

# Define target
target = Target(
    name="GitHub Copilot",
    base_url="https://copilot.github.com",
    program_scope=["*.github.com", "copilot.github.com"],
    out_of_scope=["github.com/blog"],
    safe_harbor={
        "researcher_owned_accounts": True,
        "no_dos": True
    },
    researcher_resources=["test@researcher.com"]
)

# Analyze target (passive reconnaissance)
analysis = ai.analyze_target(target)

print(f"Attack surfaces: {len(analysis['attack_surfaces'])}")
print(f"Hypotheses: {len(analysis['hypotheses'])}")
print(f"Recommended tools: {analysis['recommended_tools']}")

# Generate reconnaissance plan
recon_plan = ai.generate_reconnaissance_plan(target)

# Monitor CVE feeds
cves = ai.monitor_cve_feeds(keywords=["Copilot", "AI"])

ai.close()
```

---

## 🔒 Safety Features

### Human Approval Gates

ALL exploitation requires human approval:

```python
from compliance_enforcer import Action, RiskLevel

action = Action(
    action_type="sql_injection_test",
    target="test@researcher.com",
    description="Test SQL injection on login form",
    risk_level=RiskLevel.HIGH,
    requires_human_approval=True,
    scope_verified=True,
    researcher_owned=True
)

# Approval workflow
approved, reason = ai.compliance.approve_action(
    action, program_scope, researcher_resources
)

if approved and action.requires_human_approval:
    # Wait for human approval
    human_approved = ai.request_human_approval(action, risk_assessment)
    
    if human_approved:
        # Execute test
        pass
    else:
        print("Human denied approval - test cancelled")
```

### Compliance Enforcement

The Compliance Guardian enforces:

✅ **Safe Harbor Protections**
- Only test in-scope targets
- No DoS attacks
- No social engineering
- Researcher-owned test accounts only
- No PII access

✅ **Automatic Blocking**
- Out-of-scope targets
- Destructive commands (`DROP TABLE`, `rm -rf`)
- PII-containing data
- Non-researcher-owned resources

✅ **Emergency Stop**
- Triggers on multiple violations
- Halts all operations immediately
- Requires admin password to reset

✅ **Audit Trail**
- All actions logged to `logs/compliance_audit.jsonl`
- Timestamp, action, target, approval status
- Immutable append-only log

---

## 🧠 Intelligence Capabilities

### 1. CVE Monitoring

Auto-monitor vulnerability feeds:

```python
from self_updater import SelfUpdater

updater = SelfUpdater()

# Daily CVE updates
daily_summary = updater.run_daily_updates()
print(f"New CVEs: {daily_summary['updates']['cves']}")

# Weekly disclosed bounty updates
weekly_summary = updater.run_weekly_updates()
print(f"New bounties: {weekly_summary['updates']['bounties']}")
```

**Sources:**
- NVD (National Vulnerability Database)
- GitHub Security Advisories
- HackerOne disclosed reports
- PortSwigger research

### 2. Vulnerability Hypothesis Generation

AI-powered hypothesis generation based on:
- Known Copilot CVE patterns
- Learned patterns from disclosed bounties
- Attack surface analysis
- Historical success rates

```python
# Generate hypotheses
hypotheses = ai.generate_vulnerability_hypotheses(attack_surfaces, target)

for h in hypotheses:
    print(f"Type: {h.vulnerability_type}")
    print(f"Confidence: {h.confidence}")
    print(f"Expected bounty: ${h.expected_bounty}")
    print(f"PoC template: {h.poc_template}")
```

### 3. Attack Surface Analysis

Passive attack surface mapping:

```python
analysis = ai.analyze_target(target)

for surface in analysis['attack_surfaces']:
    print(f"Endpoint: {surface['endpoint']}")
    print(f"Potential vulns: {surface['potential_vulnerabilities']}")
```

### 4. Tool Auto-Generation

Generate custom tools for discovered vulnerabilities:

```python
from knowledge_base import GeneratedTool

# AI generates fuzzer for specific vulnerability
tool = GeneratedTool(
    tool_id="fuzzer_jwt_001",
    tool_type="fuzzer",
    target_vulnerability="JWT Authentication Bypass",
    code="""<generated Python fuzzer code>""",
    tests="""<generated test suite>"""
)

kb.add_generated_tool(tool)
```

---

## 🤖 Multi-Agent Orchestration

### Coordinate Parallel Reconnaissance

```python
from agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Coordinate full reconnaissance campaign
campaign = orchestrator.coordinate_reconnaissance(
    target="api.example.com",
    scope=["*.example.com"]
)

print(f"Phases: {len(campaign['phases'])}")
print(f"Findings: {len(campaign['findings'])}")
```

### Distribute Fuzzing Workload

```python
endpoints = [f"/api/endpoint{i}" for i in range(100)]

# Distribute across multiple fuzzing agents
fuzzer_agents = orchestrator.distribute_fuzzing_workload(
    endpoints, 
    fuzzing_strategy="comprehensive"
)

print(f"Spawned {len(fuzzer_agents)} parallel fuzzers")
```

### Prioritize by ROI

```python
bounty_estimates = {
    "authentication_bypass": 5000,
    "IDOR": 3000,
    "XSS": 1500
}

prioritized_tasks = orchestrator.prioritize_work(tasks, bounty_estimates)
```

---

## 📊 Knowledge Base

### Schema

```sql
-- CVE intelligence
CREATE TABLE cves (
    cve_id TEXT PRIMARY KEY,
    cvss_score REAL,
    attack_vector TEXT,
    vulnerability_type TEXT,
    affected_products TEXT,
    learned_pattern TEXT
);

-- Disclosed bug bounty findings
CREATE TABLE disclosed_bounties (
    report_id TEXT PRIMARY KEY,
    program TEXT,
    title TEXT,
    severity TEXT,
    bounty_amount INTEGER,
    attack_pattern TEXT,
    lessons_learned TEXT
);

-- Generated tools
CREATE TABLE generated_tools (
    tool_id TEXT PRIMARY KEY,
    tool_type TEXT,
    target_vulnerability TEXT,
    code TEXT,
    tests TEXT
);

-- Active campaigns
CREATE TABLE active_campaigns (
    campaign_id TEXT PRIMARY KEY,
    target TEXT,
    status TEXT,
    hypotheses_count INTEGER,
    findings_count INTEGER,
    estimated_bounty INTEGER
);

-- Learned vulnerability patterns
CREATE TABLE vulnerability_patterns (
    pattern_id TEXT PRIMARY KEY,
    pattern_name TEXT,
    pattern_description TEXT,
    detection_method TEXT,
    exploitation_template TEXT,
    success_rate REAL,
    avg_bounty INTEGER,
    learned_from TEXT
);

-- Attack surfaces
CREATE TABLE attack_surfaces (
    surface_id TEXT PRIMARY KEY,
    target TEXT,
    endpoint TEXT,
    method TEXT,
    authentication_required INTEGER,
    parameters TEXT,
    potential_vulnerabilities TEXT
);
```

### Usage

```python
from knowledge_base import KnowledgeBase, CVE, DisclosedBounty

kb = KnowledgeBase()

# Add CVE
cve = CVE(
    cve_id="CVE-2024-12345",
    cvss_score=8.5,
    attack_vector="Network",
    vulnerability_type="Authentication Bypass",
    affected_products="GitHub Copilot",
    learned_pattern="JWT algorithm confusion"
)
kb.add_cve(cve)

# Search CVEs
auth_cves = kb.search_cves(vulnerability_type="Authentication", min_cvss=7.0)

# Get statistics
stats = kb.get_stats()
print(f"Total CVEs: {stats['total_cves']}")
print(f"Total bounties: {stats['total_bounties']}")
print(f"Generated tools: {stats['total_tools']}")

kb.close()
```

---

## 🛡️ Compliance & Ethics

### Safe Harbor Compliance

GlasseyeOS AI enforces **strict compliance** with bug bounty program rules:

1. **Scope Verification**
   - All targets verified against program scope
   - Out-of-scope targets automatically blocked
   - Wildcard subdomain matching

2. **Researcher-Owned Resources**
   - Testing only on researcher-controlled accounts
   - API keys and test data owned by researcher
   - No testing on production user data

3. **No Destructive Actions**
   - Forbidden patterns automatically blocked
   - Emergency stop on suspicious activity
   - Audit logging for accountability

4. **Human Approval Required**
   - All HIGH and CRITICAL risk actions require human approval
   - Risk assessment displayed before approval
   - Safe default: DENY

### Audit Trail

All actions logged to `logs/compliance_audit.jsonl`:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "action_type": "sql_injection_test",
  "target": "api.example.com",
  "description": "Test SQL injection on login",
  "risk_level": "high",
  "approved": true,
  "reason": "All compliance checks passed - HUMAN APPROVAL REQUIRED"
}
```

---

## 🔧 Configuration

### Safe Harbor Rules (`config/safe_harbor_rules.yaml`)

```yaml
risk_levels:
  HIGH:
    description: "Exploitation attempts"
    human_approval_required: true
    researcher_owned_required: true

thresholds:
  max_violations: 3
  emergency_stop_enabled: true
```

### CVE Feeds (`config/cve_feeds.yaml`)

```yaml
nvd:
  url: "https://services.nvd.nist.gov/rest/json/cves/2.0"
  update_frequency: "daily"
  filters:
    keywords: ["AI", "LLM", "Copilot"]
    min_cvss: 7.0
```

### Agent Configuration (`config/agent_configs.yaml`)

```yaml
osint_agent:
  agent_type: "glasseye-osint-intelligence"
  max_concurrent_tasks: 3
  timeout_minutes: 30

orchestration:
  max_total_concurrent_agents: 10
  queue_strategy: "priority"
```

---

## 📁 Directory Structure

```
GlasseyeOS-AI/
├── glasseye_core.py           # Main AI engine
├── compliance_enforcer.py     # Safety guardian
├── knowledge_base.py          # Intelligence DB
├── self_updater.py            # Auto-update system
├── agent_orchestrator.py      # Multi-agent coordination
├── demo.py                    # Demonstration script
├── knowledge_base.db          # SQLite database
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── config/
│   ├── safe_harbor_rules.yaml  # Compliance rules
│   ├── cve_feeds.yaml          # Data sources
│   └── agent_configs.yaml      # Sub-agent configs
├── tools/                      # Auto-generated tools
├── skills/                     # Auto-generated skills
├── logs/                       # Audit trails & logs
│   ├── compliance.log
│   ├── compliance_audit.jsonl
│   ├── glasseye_ai.log
│   ├── self_updater.log
│   └── agent_orchestrator.log
└── tests/
    └── test_all.py             # Unit tests
```

---

## 🧪 Testing

Run comprehensive test suite:

```bash
python tests/test_all.py
```

**Test Coverage:**
- Compliance enforcement (safe harbor, scope, PII)
- Knowledge base operations (CRUD, search)
- AI intelligence engine (recon, hypotheses, CVE monitoring)
- Agent orchestration (spawning, coordination, aggregation)

---

## 🎬 Demo

Run the interactive demo:

```bash
python demo.py
```

**Demo Features:**
1. Compliance enforcement with multiple scenarios
2. CVE monitoring and pattern learning
3. Target analysis and reconnaissance planning
4. Vulnerability hypothesis generation
5. Multi-agent coordination
6. Knowledge base statistics

---

## 🔄 Integration with Existing Infrastructure

### Connect to Existing Bug Bounty Tools

```python
# Integration with existing vulnerability DB
existing_db = "/root/bounty-research/azure-ai-integration/vuln_intelligence.db"

# Import existing findings
import sqlite3
conn = sqlite3.connect(existing_db)
# ... import logic
```

### Compliance Checklist Integration

```python
# Load existing compliance checklist
checklist_path = "/root/bounty-research/compliance-checklist-copilot-agent.md"

# Verify compliance before testing
with open(checklist_path) as f:
    compliance_rules = parse_compliance_checklist(f.read())
```

---

## 🚨 Emergency Stop

If violations detected or manual stop required:

```python
from compliance_enforcer import ComplianceEnforcer

enforcer = ComplianceEnforcer()

# Trigger emergency stop
enforcer.trigger_emergency_stop("Manual emergency stop requested")

# Reset (requires admin password)
enforcer.reset_emergency_stop("RESET_EMERGENCY_STOP")
```

---

## 📈 Monitoring & Metrics

### Knowledge Base Statistics

```python
stats = kb.get_stats()
# {
#   'total_cves': 42,
#   'total_bounties': 15,
#   'total_tools': 8,
#   'total_campaigns': 3,
#   'total_patterns': 25,
#   'total_surfaces': 67,
#   'total_estimated_bounty': 45000
# }
```

### Orchestrator Status

```python
status = orchestrator.get_status()
# {
#   'active_agents': 5,
#   'queued_tasks': 12,
#   'completed_tasks': 38
# }
```

---

## 🤝 Contributing

**This is a security research tool. Contributions must:**
1. Maintain strict compliance enforcement
2. Preserve human approval gates
3. Enhance safety features
4. Include comprehensive tests
5. Document ethical usage

---

## ⚖️ Legal & Ethics

### Permitted Use

✅ Authorized bug bounty research  
✅ Security testing on owned/permitted systems  
✅ Vulnerability research and disclosure  
✅ Educational security research

### Prohibited Use

❌ Unauthorized penetration testing  
❌ Malicious hacking or computer crimes  
❌ Bypassing security controls without permission  
❌ Testing outside bug bounty program scope

### Disclaimer

**This tool is for AUTHORIZED security research only.** Users are responsible for:
- Obtaining proper authorization
- Following bug bounty program rules
- Complying with all applicable laws
- Ethical disclosure of vulnerabilities

The authors assume no liability for misuse.

---

## 📞 Support

**Documentation:** This README  
**Tests:** `python tests/test_all.py`  
**Demo:** `python demo.py`  
**Logs:** `logs/` directory  
**Config:** `config/` directory

---

## 🏆 Acknowledgments

Built for ethical security research.  
Inspired by responsible disclosure and bug bounty best practices.

**Remember:** With great power comes great responsibility. Use wisely.

---

## 📝 License

For authorized security research use only.  
See program terms and safe harbor agreements.

---

**Version 1.0.0** | Last Updated: 2024-01-15  
**Status:** Production-Ready Intelligence Platform ✅

## 🛠️ Autonomous Tool Generator

### Overview

The Tool Generator autonomously creates security testing tools based on discovered attack surfaces. It uses a template-based architecture with compliance enforcement and automatic code validation.

### Quick Start

```bash
# Generate a JSON-RPC fuzzer
python3 tool_generator.py --fuzzer "JSON-RPC 2.0" --target copilot-mcp-server

# Generate a protocol analyzer
python3 tool_generator.py --analyzer "HTTP API" --target github-api

# Generate an MCP skill
python3 tool_generator.py --skill "api-security-scanner" --target my-target

# Generate from attack surface
python3 demo_tool_generator.py
```

### Tool Generation Workflow

```python
from tool_generator import ToolGenerator, AttackSurface

# Define attack surface
attack_surface = AttackSurface(
    name='github-copilot-mcp',
    protocol='JSON-RPC 2.0',
    transport='STDIO',
    authentication='OAuth',
    attack_vectors=['command injection', 'auth bypass'],
    endpoints=['/tools/list', '/tools/call']
)

# Generate tools
gen = ToolGenerator()
tools = gen.generate_tool_from_attack_surface(attack_surface)

# Tools are saved to generated_tools/ directory
```

### Available Templates

**Fuzzers:**
- `json_rpc_fuzzer_template.py` - JSON-RPC 2.0 protocol fuzzer
- `http_api_fuzzer_template.py` - HTTP API fuzzer (planned)
- `websocket_fuzzer_template.py` - WebSocket fuzzer (planned)

**Analyzers:**
- `protocol_analyzer_template.py` - Generic protocol analyzer
- `config_analyzer_template.py` - Configuration file analyzer (planned)
- `dependency_scanner_template.py` - Dependency vulnerability scanner (planned)

**PoC Generators:**
- `command_injection_poc_template.py` - Command injection PoC
- `auth_bypass_poc_template.py` - Authorization bypass PoC (planned)
- `ssrf_poc_template.py` - SSRF PoC (planned)

**Evidence Collectors:**
- `network_recorder_template.py` - Network traffic capture
- `log_aggregator_template.py` - Log collection (planned)
- `screenshot_automation_template.py` - Screenshot capture (planned)

**MCP Skills:**
- `mcp_skill_template_template.py` - Foundry/VS Code skill template

### Customizing Templates

Templates use `{placeholder}` syntax for variable substitution:

```python
# Example template
"""
Target: {target}
Protocol: {protocol}
Generated: {timestamp}

class {target}_Fuzzer:
    def __init__(self):
        self.target = "{target}"
        self.protocol = "{protocol}"
"""
```

Parameters are automatically substituted during generation.

### Generated Tool Features

All generated tools include:
- ✅ Full error handling and logging
- ✅ Command-line argument parsing
- ✅ Dry-run mode for safe testing
- ✅ Compliance notices and authorization checks
- ✅ Unit test stubs
- ✅ Comprehensive documentation
- ✅ Executable permissions

### MCP Skill Generation

Generated MCP skills are compatible with Foundry and VS Code:

```bash
python3 tool_generator.py --skill "github-security-scanner" --target github-api
```

Creates:
```
generated_skills/github-security-scanner/
├── skill.yaml          # MCP manifest
├── skill.py            # Implementation
└── README.md           # Documentation
```

### Testing Generated Tools

```bash
# Run unit tests for tool generator
python3 tests/test_tool_generator.py

# Test a generated tool (dry-run)
./generated_tools/copilot-mcp-demo_json_rpc_fuzzer.py --dry-run --target test.example.com

# Test with verbose logging
./generated_tools/copilot-mcp-demo_json_rpc_fuzzer.py --verbose --target test.example.com
```

### Code Validation

Generated code is automatically validated for:
- ✅ Python syntax correctness
- ⚠️ Dangerous pattern detection (eval, os.system, etc.)
- ✅ Compliance with safe harbor policies
- ✅ Proper error handling

### Integration with GlasseyeOS Core

```python
from glasseye_core import GlasseyeAI
from tool_generator import ToolGenerator

ai = GlasseyeAI()
gen = ToolGenerator()

# Analyze target and generate tools
target_analysis = ai.analyze_target("example.com")
attack_surfaces = target_analysis['attack_surfaces']

for surface in attack_surfaces:
    tools = gen.generate_tool_from_attack_surface(surface)
    print(f"Generated {len(tools)} tools for {surface.name}")
```

### Advanced Usage

**Custom template directories:**
```python
gen = ToolGenerator(
    templates_dir='/custom/templates',
    output_dir='/custom/output',
    skills_dir='/custom/skills'
)
```

**Attack surface analysis only:**
```python
tools_needed = gen.analyze_attack_surface(attack_surface)
# Returns: ['json_rpc_fuzzer', 'protocol_analyzer', ...]
```

**Generate specific tool types:**
```python
# Fuzzer
fuzzer_path = gen.generate_fuzzer(
    protocol='JSON-RPC 2.0',
    transport='STDIO',
    target='my-server',
    endpoints=['/api/v1']
)

# Protocol analyzer
analyzer_path = gen.generate_protocol_analyzer({
    'name': 'MCP Protocol',
    'target': 'copilot',
    'message_format': 'JSON',
    'authentication': 'Bearer tokens'
})

# PoC template
poc_path = gen.generate_poc_template(
    vulnerability_type='command_injection',
    target='demo-app',
    details={'endpoint': '/api/exec', 'payload': '; id'}
)

# MCP skill
skill_path = gen.generate_mcp_skill(
    capability='security-audit',
    description='Run security audits',
    tools_list=['fuzzer', 'scanner', 'analyzer']
)
```

### Demo

Run the interactive demo:

```bash
python3 demo_tool_generator.py
```

This demonstrates:
1. Template system overview
2. Code validation
3. Fuzzer generation
4. Protocol analyzer generation
5. MCP skill generation
6. Attack surface analysis with multi-tool generation



---

## 🆕 Enhanced Self-Updater v2.0

GlasseyeOS AI now features an **autonomous learning and update system** that continuously improves by monitoring security research and bug bounty disclosures.

### New Capabilities

1. **GitHub Security Advisory Monitor** - Auto-fetch and learn from GitHub advisories
2. **HackerOne Disclosed Learning** - Extract attack patterns from real-world exploits
3. **Vulnerability Pattern Extraction** - NLP-based pattern recognition from CVE text
4. **Self-Code Updates** - Auto-update with human approval gates
5. **Security Research Monitor** - Track arXiv, Black Hat, DEF CON papers
6. **Program Rule Monitor** - Auto-detect bug bounty scope/rule changes
7. **Automated Tool Updates** - Regenerate tools with new techniques

### Quick Start

```bash
# Run enhanced self-updater
python3 self_updater.py

# Or programmatically
from self_updater import EnhancedSelfUpdater
u = EnhancedSelfUpdater()
u.run_daily_updates()
u.close()
```

### Documentation

- **Complete Guide**: [ENHANCED_SELF_UPDATER_GUIDE.md](./ENHANCED_SELF_UPDATER_GUIDE.md)
- **Deployment**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- **Mission Report**: [SELF_UPDATE_MISSION_COMPLETE.md](./SELF_UPDATE_MISSION_COMPLETE.md)
- **Tests**: [tests/test_enhanced_self_updater.py](./tests/test_enhanced_self_updater.py)

### Knowledge Base Growth

The system autonomously learns from:
- **Daily**: NVD CVEs, GitHub advisories (5-10 new patterns/day)
- **Weekly**: HackerOne reports, arXiv papers (20-30 new patterns/week)
- **Continuous**: Bug bounty program rule monitoring

**Expected Growth**: 10x knowledge base size in first 30 days 📈
