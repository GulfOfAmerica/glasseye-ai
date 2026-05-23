# GlasseyeOS AI - Enhanced Self-Updater Guide (v2.0)

## Overview

The Enhanced Self-Updater is an **autonomous learning and update system** that continuously improves GlasseyeOS AI's capabilities by:

1. **Monitoring security advisories** from multiple sources
2. **Learning from successful bug bounty reports**
3. **Extracting attack patterns** using NLP
4. **Auto-updating code** (with human approval gates)
5. **Tracking security research** papers
6. **Detecting bug bounty program changes**
7. **Regenerating tools** with new techniques

---

## 🚀 Quick Start

### Basic Usage

```python
from self_updater import EnhancedSelfUpdater

# Create updater instance
updater = EnhancedSelfUpdater()

# Run daily updates
summary = updater.run_daily_updates()
print(f"CVEs added: {summary['updates']['cves']}")

# Run weekly updates
weekly = updater.run_weekly_updates()
print(f"Patterns learned: {weekly['updates']['bounties']}")

updater.close()
```

### Command Line

```bash
# Run full update cycle
python3 self_updater.py

# Manual monitoring
python3 -c "
from self_updater import EnhancedSelfUpdater
u = EnhancedSelfUpdater()
u.monitor_github_advisories()
u.close()
"
```

---

## 📋 Feature Details

### 1. GitHub Security Advisory Monitor

**Purpose**: Auto-fetch and learn from GitHub's Security Advisories API

**Configuration**:
- Updates: Daily
- Filter: High & Critical severity
- Source: https://api.github.com/advisories

**Usage**:

```python
updater = EnhancedSelfUpdater()

# Monitor advisories
new_advisories = updater.monitor_github_advisories()
print(f"Processed {new_advisories} new advisories")

# Advisories are automatically:
# 1. Added to CVE database
# 2. Attack patterns extracted
# 3. Patterns added to knowledge base
```

**Output**:
- CVEs added to knowledge base
- Attack patterns cached in `data_sources/cache/attack_patterns.jsonl`
- Logged to `logs/updates.jsonl`

---

### 2. HackerOne Disclosed Report Learning

**Purpose**: Learn from publicly disclosed bug bounty reports

**Features**:
- Extracts attack steps from vulnerability descriptions
- Learns lessons from successful exploits
- Updates hypothesis generator
- High confidence patterns (real-world validated)

**Usage**:

```python
updater = EnhancedSelfUpdater()

# Learn from disclosed reports
patterns = updater.learn_from_hackerone_disclosed(min_severity='medium')
print(f"Learned {patterns} attack patterns")

# Filter by program
patterns = updater.learn_from_hackerone_disclosed(program='GitHub')
```

**Extracted Data**:
- Attack methodology
- Exploitation steps
- Root cause analysis
- Bounty amounts (for pattern value estimation)
- Success rate indicators

---

### 3. Vulnerability Pattern Extraction (NLP)

**Purpose**: Extract structured attack patterns from unstructured text

**Capabilities**:
- Vulnerability type classification
- Attack vector identification
- Affected component detection
- Exploitation method extraction
- Keyword extraction & ranking

**Usage**:

```python
from self_updater import EnhancedSelfUpdater

updater = EnhancedSelfUpdater()

# Extract pattern from CVE description
description = "Copilot CLI vulnerable to command injection via bash parameter expansion"
pattern = updater.extract_attack_pattern_detailed(description)

print(f"Type: {pattern.vulnerability_type}")
print(f"Vector: {pattern.attack_vector}")
print(f"Component: {pattern.affected_component}")
print(f"Method: {pattern.exploitation_method}")
print(f"Keywords: {pattern.keywords}")
print(f"Confidence: {pattern.confidence_score}")
```

**Pattern Example**:

```python
AttackPattern(
    vulnerability_type='command_injection',
    attack_vector='parameter',
    affected_component='CLI',
    exploitation_method='parameter_manipulation',
    keywords=['command', 'injection', 'bash', 'expansion', 'parameter'],
    confidence_score=0.67
)
```

---

### 4. Self-Code Update (Human Approval)

**Purpose**: Automatically update GlasseyeOS code when new versions available

**Safety Features**:
- ✅ Human approval required for all code updates
- ✅ Test suite validation before deployment
- ✅ Automatic backup creation
- ✅ Rollback capability on failure
- ✅ Risk level assessment

**Workflow**:

```
1. Check GitHub for new releases
2. Download update package
3. Run test suite on new code
4. REQUEST HUMAN APPROVAL
5. If approved: Apply update
6. If rejected: Keep current version
```

**Usage**:

```python
updater = EnhancedSelfUpdater()

# Check for updates
update_info = updater.check_glasseye_updates()

if update_info:
    print(f"Update available: {update_info['latest_version']}")
    print(f"Release notes:\n{update_info['release_notes']}")
    
    # Attempt self-update (will request approval)
    success = updater.self_update_code()
    
    if success:
        print("Update applied successfully!")
    else:
        print("Update blocked pending human approval")
```

**Approval Mechanism**:

```python
# Approval requests are logged to:
# logs/approval_requests.jsonl

# Check pending approvals
if updater.human_approval_required:
    for request in updater.human_approval_required:
        print(f"Action: {request['action']}")
        print(f"Risk: {request['risk_level']}")
        print(f"Details: {request['details']}")
```

**Risk Levels**:
- **Low**: Auto-approved (config changes, cache updates)
- **Medium**: Requires approval (code updates, tool changes)
- **High**: Requires approval (system-level changes)
- **Critical**: Requires multi-party approval (not implemented)

---

### 5. Security Research Paper Monitor

**Purpose**: Track latest security research from academic & industry sources

**Sources**:
- arXiv.org (cs.CR category)
- Black Hat conference papers
- DEF CON presentations
- Academic security journals

**Usage**:

```python
updater = EnhancedSelfUpdater()

# Monitor all sources
papers = updater.monitor_security_research()

# Monitor specific source
papers = updater.monitor_security_research(['arxiv'])

# Monitor arXiv only
arxiv_papers = updater._monitor_arxiv()
```

**Extracted Techniques**:
- Static analysis methods
- Dynamic testing approaches
- Novel attack vectors
- Defensive techniques
- Automated discovery frameworks

**Data Storage**:

Research papers are cached in `data_sources/cache/research_papers.jsonl`:

```json
{
  "paper_id": "arxiv:2024.12345",
  "title": "Novel Techniques for Automated Vulnerability Discovery",
  "authors": ["Smith, J.", "Doe, A."],
  "source": "arXiv",
  "url": "https://arxiv.org/abs/2024.12345",
  "learned_techniques": ["static analysis", "automated discovery"],
  "added_at": "2024-01-15T10:00:00Z"
}
```

---

### 6. Bug Bounty Program Rule Monitor

**Purpose**: Auto-detect when programs update their rules

**Monitored Changes**:
- ✅ Scope additions/removals
- ✅ Out-of-scope updates
- ✅ Bounty amount changes
- ✅ Safe harbor modifications
- ✅ Prohibited action changes

**Change Detection Method**:

Uses cryptographic hashing to detect changes:

```python
snapshot = ProgramRuleSnapshot(
    program_name="GitHub Bug Bounty",
    snapshot_date="2024-01-15T12:00:00Z",
    scope_hash="a1b2c3d4...",           # SHA256 of scope section
    out_of_scope_hash="e5f6g7h8...",    # SHA256 of out-of-scope section
    bounty_table_hash="i9j0k1l2...",    # SHA256 of bounty table
    safe_harbor_hash="m3n4o5p6...",     # SHA256 of safe harbor rules
    full_content_hash="q7r8s9t0..."     # SHA256 of entire page
)
```

**Usage**:

```python
updater = EnhancedSelfUpdater()

# Monitor single program
changes = updater.monitor_program_rules(
    program_url="https://bounty.github.com",
    program_name="GitHub Bug Bounty"
)

if changes['changes']:
    print(f"Changes detected: {', '.join(changes['changes'])}")
    
    if 'scope_changed' in changes['changes']:
        print("⚠️  SCOPE CHANGED - Review before testing!")
    
    if 'safe_harbor_changed' in changes['changes']:
        print("⚠️  SAFE HARBOR CHANGED - Review new restrictions!")
```

**Automated Actions on Change Detection**:

1. **Log change** to `logs/compliance_updates.jsonl`
2. **Update compliance rules** in compliance enforcer
3. **Alert for manual review**
4. **Archive old snapshot**

**Snapshot Storage**:

```
data_sources/program_snapshots/
├── GitHub_Bug_Bounty_latest.json          # Current snapshot metadata
├── GitHub_Bug_Bounty_2024-01-15T12:00:00.txt  # Archived full content
└── GitHub_Bug_Bounty_2024-01-08T12:00:00.txt  # Previous archive
```

---

### 7. Automated Tool Update

**Purpose**: Regenerate tools when new attack patterns discovered

**Update Triggers**:
- New attack patterns learned (last 24 hours)
- Security research techniques discovered
- Disclosed bounty patterns added
- Manual force regeneration

**Workflow**:

```
1. Identify new patterns relevant to existing tools
2. Regenerate affected tools with new capabilities
3. Run tool test suite
4. If tests pass: Replace old version (with backup)
5. If tests fail: Keep old version, log failure
```

**Usage**:

```python
updater = EnhancedSelfUpdater()

# Auto-update tools based on new patterns
tools_updated = updater.update_generated_tools()
print(f"Updated {tools_updated} tools")

# Force regenerate all tools
tools_updated = updater.update_generated_tools(force_regenerate=True)
```

**Tool Backup**:

Old tool versions are automatically backed up to `tools/backups/`:

```
tools/backups/
├── fuzzer_jwt_001_v1.0_20240115_120000.bak
├── scanner_idor_001_v1.0_20240115_120500.bak
└── ...
```

---

## ⚙️ Configuration

### Update Schedule

Edit `data_sources/configs/update_schedule.json`:

```json
{
  "daily_updates": {
    "enabled": true,
    "time": "02:00",
    "sources": ["nvd_cve", "github_advisories"]
  },
  "weekly_updates": {
    "enabled": true,
    "day": "Monday",
    "time": "03:00",
    "sources": ["hackerone_disclosed", "arxiv_security"]
  }
}
```

### Rate Limiting

Edit `data_sources/configs/rate_limits.json`:

```json
{
  "github_advisories": {
    "requests_per_hour": 5000,
    "retry_after_seconds": 3600
  }
}
```

### API Credentials

Copy `api_credentials.template.json` to `api_credentials.json` and fill in:

```json
{
  "github": {
    "token": "ghp_YOUR_TOKEN_HERE"
  },
  "hackerone": {
    "api_token": "YOUR_H1_TOKEN"
  }
}
```

---

## 🔄 Automation

### Cron Scheduling

Add to crontab for automated updates:

```bash
# Daily updates at 2 AM
0 2 * * * cd /home/x/GlasseyeOS-AI && python3 -c "from self_updater import EnhancedSelfUpdater; u = EnhancedSelfUpdater(); u.run_daily_updates(); u.close()"

# Weekly updates every Monday at 3 AM
0 3 * * 1 cd /home/x/GlasseyeOS-AI && python3 -c "from self_updater import EnhancedSelfUpdater; u = EnhancedSelfUpdater(); u.run_weekly_updates(); u.close()"
```

### Systemd Timer (Alternative)

Create `/etc/systemd/system/glasseye-updater.service`:

```ini
[Unit]
Description=GlasseyeOS AI Daily Updates
After=network.target

[Service]
Type=oneshot
User=x
WorkingDirectory=/home/x/GlasseyeOS-AI
ExecStart=/usr/bin/python3 -c "from self_updater import EnhancedSelfUpdater; u = EnhancedSelfUpdater(); u.run_daily_updates(); u.close()"

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/glasseye-updater.timer`:

```ini
[Unit]
Description=GlasseyeOS AI Daily Update Timer

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable glasseye-updater.timer
sudo systemctl start glasseye-updater.timer
```

---

## 📊 Monitoring & Logs

### Log Files

All activities logged to:

```
logs/
├── self_updater.log         # Main updater log
├── updates.jsonl            # Update audit trail (JSONL)
├── approval_requests.jsonl  # Human approval requests
└── compliance_updates.jsonl # Program rule changes
```

### View Recent Updates

```bash
# View last 10 updates
tail -n 10 logs/updates.jsonl | jq '.'

# View today's updates
grep "$(date +%Y-%m-%d)" logs/updates.jsonl | jq '.'

# View approval requests
cat logs/approval_requests.jsonl | jq 'select(.risk_level == "high")'
```

### Check Cache Sizes

```bash
# View cache sizes
du -sh data_sources/cache/*

# Count patterns learned
wc -l data_sources/cache/attack_patterns.jsonl
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd /home/x/GlasseyeOS-AI
pytest tests/test_enhanced_self_updater.py -v
```

Test individual features:

```bash
# Test GitHub advisory monitor
pytest tests/test_enhanced_self_updater.py::TestGitHubAdvisoryMonitor -v

# Test pattern extraction
pytest tests/test_enhanced_self_updater.py::TestVulnerabilityPatternExtraction -v

# Test self-update mechanism
pytest tests/test_enhanced_self_updater.py::TestSelfCodeUpdate -v
```

---

## 🔧 Troubleshooting

### Rate Limit Errors

**Problem**: `429 Too Many Requests` errors

**Solution**:
1. Check logs: `grep "rate limit" logs/self_updater.log`
2. Add API authentication for higher limits
3. Adjust `rate_limits.json` to be more conservative

### Failed Pattern Extraction

**Problem**: Patterns not being extracted from CVEs

**Solution**:
1. Check keyword lists in `extract_attack_pattern_detailed()`
2. Add domain-specific keywords
3. Review NLP extraction logic

### Tool Regeneration Failures

**Problem**: Tools not updating with new patterns

**Solution**:
1. Check test results: `pytest tests/test_enhanced_self_updater.py::TestAutomatedToolUpdate`
2. Verify pattern cache: `cat data_sources/cache/attack_patterns.jsonl | jq '.'`
3. Force regeneration: `update_generated_tools(force_regenerate=True)`

---

## 📈 Performance

### Resource Usage

Typical resource usage during updates:

- **CPU**: 5-15% (pattern extraction)
- **Memory**: 50-100 MB
- **Disk I/O**: Low (JSONL caching)
- **Network**: Depends on API response sizes

### Optimization

```python
# Process in batches to reduce memory
for chunk in chunked_cves:
    updater.process_cve_batch(chunk)

# Use caching to avoid redundant fetches
if updater.data_cache_dir.exists():
    patterns = load_from_cache()
```

---

## 🔐 Security Considerations

1. **API Credentials**: Store in `api_credentials.json` (gitignored)
2. **Rate Limiting**: Respect source rate limits
3. **Input Validation**: All external data validated before processing
4. **Sanitization**: User-controlled data sanitized
5. **HTTPS Only**: All external requests use HTTPS
6. **Human Approval**: Critical actions require human approval

---

## 📚 API Reference

See code documentation in `self_updater.py`:

```python
class EnhancedSelfUpdater:
    def monitor_github_advisories(self) -> int
    def learn_from_hackerone_disclosed(self, min_severity='medium') -> int
    def extract_attack_pattern_detailed(self, cve_description: str) -> AttackPattern
    def check_glasseye_updates(self) -> Optional[Dict]
    def monitor_security_research(self, sources=None) -> int
    def monitor_program_rules(self, program_url: str, program_name: str) -> Dict
    def update_generated_tools(self, force_regenerate=False) -> int
```

---

## 🎯 Roadmap

Future enhancements:

- [ ] Vector embeddings for better pattern matching
- [ ] LLM-powered pattern extraction
- [ ] Automated testing of generated exploits (sandboxed)
- [ ] Multi-party approval for critical updates
- [ ] Integration with threat intelligence feeds
- [ ] Real-time monitoring (webhooks)
- [ ] ML model for vulnerability severity prediction

---

## 💡 Tips & Best Practices

1. **Start small**: Enable only critical sources initially
2. **Monitor logs**: Review `self_updater.log` daily
3. **Test regularly**: Run test suite after configuration changes
4. **Backup data**: Regular backups of `knowledge_base.db`
5. **Review approvals**: Check `approval_requests.jsonl` frequently
6. **Update schedules**: Align with program activity (business hours)

---

**Version**: 2.0.0  
**Last Updated**: January 2024  
**Maintainer**: GlasseyeOS AI Development Team
