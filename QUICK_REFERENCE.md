# GlasseyeOS AI - Enhanced Self-Updater Quick Reference

## 🚀 Quick Commands

### Run Updates

```bash
# Daily updates
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); u.run_daily_updates(); u.close()"

# Weekly updates
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); u.run_weekly_updates(); u.close()"

# All sources
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); u.fetch_all_sources(); u.close()"
```

### Monitor Specific Sources

```bash
# GitHub advisories
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); print(f'{u.monitor_github_advisories()} new advisories'); u.close()"

# HackerOne disclosed
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); print(f'{u.learn_from_hackerone_disclosed()} patterns learned'); u.close()"

# Security research
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); print(f'{u.monitor_security_research()} papers'); u.close()"

# Program rules
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); print(u.monitor_program_rules('https://bounty.github.com', 'GitHub')); u.close()"
```

## 📊 Check Status

### Knowledge Base Stats

```bash
# CVE count
sqlite3 knowledge_base.db "SELECT COUNT(*) FROM cves;"

# Pattern count
sqlite3 knowledge_base.db "SELECT COUNT(*) FROM vulnerability_patterns;"

# Recent CVEs
sqlite3 knowledge_base.db "SELECT cve_id, cvss_score, vulnerability_type FROM cves ORDER BY ROWID DESC LIMIT 5;"
```

### View Logs

```bash
# Recent updates
tail -n 20 logs/updates.jsonl | jq '.'

# Today's updates
grep "$(date +%Y-%m-%d)" logs/updates.jsonl | jq '.'

# Errors only
grep ERROR logs/self_updater.log | tail -n 10

# Pending approvals
cat logs/approval_requests.jsonl | jq 'select(.status == "pending")'
```

### Cache Status

```bash
# Cache sizes
du -sh data_sources/cache/*

# Pattern count
wc -l data_sources/cache/attack_patterns.jsonl

# Recent patterns
tail -n 5 data_sources/cache/attack_patterns.jsonl | jq '.'

# Research papers
wc -l data_sources/cache/research_papers.jsonl
```

## 🔧 Configuration

### API Credentials

```bash
cd data_sources/configs
nano api_credentials.json
```

### Update Schedule

```bash
cd data_sources/configs
nano update_schedule.json
```

### Rate Limits

```bash
cd data_sources/configs
nano rate_limits.json
```

## 🧪 Testing

```bash
# All tests
pytest tests/test_enhanced_self_updater.py -v

# Specific feature
pytest tests/test_enhanced_self_updater.py::TestGitHubAdvisoryMonitor -v

# With output
pytest tests/test_enhanced_self_updater.py -v -s
```

## 📈 Monitoring

### Health Check

```bash
./health_check.sh
```

### Live Monitoring

```bash
# Watch logs
tail -f logs/self_updater.log

# Watch updates
watch -n 60 'tail -n 5 logs/updates.jsonl | jq .'

# Monitor knowledge base growth
watch -n 300 'sqlite3 knowledge_base.db "SELECT COUNT(*) as cves FROM cves; SELECT COUNT(*) as patterns FROM vulnerability_patterns;"'
```

## 🚨 Troubleshooting

### Clear Caches

```bash
rm data_sources/cache/*.jsonl
```

### Force Tool Regeneration

```bash
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); u.update_generated_tools(force_regenerate=True); u.close()"
```

### Check For Updates

```bash
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); info=u.check_glasseye_updates(); print(info); u.close()"
```

## 📋 Cron Setup

```bash
crontab -e
```

Add:
```cron
0 2 * * * cd /home/x/GlasseyeOS-AI && /usr/bin/python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); u.run_daily_updates(); u.close()" >> /home/x/GlasseyeOS-AI/logs/cron.log 2>&1
```

## 🔍 Pattern Analysis

```bash
# Most common vulnerability types
cat data_sources/cache/attack_patterns.jsonl | jq -r '.type' | sort | uniq -c | sort -rn | head -10

# High confidence patterns
cat data_sources/cache/attack_patterns.jsonl | jq 'select(.confidence > 0.8)'

# Recent patterns (last 24h)
cat data_sources/cache/attack_patterns.jsonl | jq 'select(.learned_at > "'$(date -d '24 hours ago' -Iseconds)'")'
```

## 📝 Files & Locations

| Item | Location |
|------|----------|
| Main Script | `/home/x/GlasseyeOS-AI/self_updater.py` |
| Tests | `/home/x/GlasseyeOS-AI/tests/test_enhanced_self_updater.py` |
| Knowledge Base | `/home/x/GlasseyeOS-AI/knowledge_base.db` |
| Logs | `/home/x/GlasseyeOS-AI/logs/` |
| Configs | `/home/x/GlasseyeOS-AI/data_sources/configs/` |
| Cache | `/home/x/GlasseyeOS-AI/data_sources/cache/` |
| Snapshots | `/home/x/GlasseyeOS-AI/data_sources/program_snapshots/` |

## 🎯 Common Tasks

### Daily Routine

```bash
# 1. Check overnight updates
tail -n 20 logs/updates.jsonl | jq '.'

# 2. Review approvals
cat logs/approval_requests.jsonl | jq 'select(.status == "pending")'

# 3. Check KB growth
sqlite3 knowledge_base.db "SELECT COUNT(*) FROM cves; SELECT COUNT(*) FROM vulnerability_patterns;"
```

### Weekly Routine

```bash
# 1. Review weekly updates
grep "$(date +%Y-%m-%d -d '7 days ago')" logs/updates.jsonl | jq '.'

# 2. Check program rule changes
ls -lt data_sources/program_snapshots/ | head -10

# 3. Review new research papers
tail -n 10 data_sources/cache/research_papers.jsonl | jq '.title'

# 4. Update tools
python3 -c "from self_updater import EnhancedSelfUpdater; u=EnhancedSelfUpdater(); u.update_generated_tools(); u.close()"
```

## 📚 Documentation

- **Complete Guide**: [ENHANCED_SELF_UPDATER_GUIDE.md](./ENHANCED_SELF_UPDATER_GUIDE.md)
- **Deployment**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- **Mission Report**: [SELF_UPDATE_MISSION_COMPLETE.md](./SELF_UPDATE_MISSION_COMPLETE.md)

---

**Version**: 2.0.0  
**Quick ref for common operations**
