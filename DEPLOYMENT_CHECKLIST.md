# GlasseyeOS AI Enhanced Self-Updater - Deployment Checklist

## ✅ Pre-Deployment

### 1. API Credentials Setup

```bash
cd /home/x/GlasseyeOS-AI/data_sources/configs

# Copy template
cp api_credentials.template.json api_credentials.json

# Edit with your tokens
nano api_credentials.json
```

**Required Credentials**:
- [ ] GitHub Personal Access Token (for higher rate limits)
- [ ] HackerOne API Token (for disclosed reports - optional)
- [ ] NVD API Key (for higher rate limits - optional)

### 2. Test Suite Verification

```bash
cd /home/x/GlasseyeOS-AI

# Run all tests
pytest tests/test_enhanced_self_updater.py -v

# Expected: All 25 tests passing
```

### 3. Directory Permissions

```bash
# Ensure correct permissions
chmod 755 /home/x/GlasseyeOS-AI/data_sources
chmod 700 /home/x/GlasseyeOS-AI/data_sources/configs
chmod 600 /home/x/GlasseyeOS-AI/data_sources/configs/api_credentials.json
```

### 4. Log Directory Setup

```bash
# Create logs directory if needed
mkdir -p /home/x/GlasseyeOS-AI/logs

# Set up log rotation (optional)
sudo nano /etc/logrotate.d/glasseye
```

Example logrotate config:
```
/home/x/GlasseyeOS-AI/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 📅 Scheduling

### Option 1: Crontab

```bash
crontab -e
```

Add these lines:

```cron
# Daily updates at 2 AM UTC
0 2 * * * cd /home/x/GlasseyeOS-AI && /usr/bin/python3 -c "from self_updater import EnhancedSelfUpdater; u = EnhancedSelfUpdater(); u.run_daily_updates(); u.close()" >> /home/x/GlasseyeOS-AI/logs/cron_daily.log 2>&1

# Weekly updates every Monday at 3 AM UTC
0 3 * * 1 cd /home/x/GlasseyeOS-AI && /usr/bin/python3 -c "from self_updater import EnhancedSelfUpdater; u = EnhancedSelfUpdater(); u.run_weekly_updates(); u.close()" >> /home/x/GlasseyeOS-AI/logs/cron_weekly.log 2>&1
```

### Option 2: Systemd Timer (Recommended)

```bash
# Create service file
sudo nano /etc/systemd/system/glasseye-daily-updater.service
```

```ini
[Unit]
Description=GlasseyeOS AI Daily Updates
After=network.target

[Service]
Type=oneshot
User=x
WorkingDirectory=/home/x/GlasseyeOS-AI
ExecStart=/usr/bin/python3 -c "from self_updater import EnhancedSelfUpdater; u = EnhancedSelfUpdater(); u.run_daily_updates(); u.close()"
StandardOutput=append:/home/x/GlasseyeOS-AI/logs/systemd_daily.log
StandardError=append:/home/x/GlasseyeOS-AI/logs/systemd_daily.log

[Install]
WantedBy=multi-user.target
```

```bash
# Create timer file
sudo nano /etc/systemd/system/glasseye-daily-updater.timer
```

```ini
[Unit]
Description=GlasseyeOS AI Daily Update Timer
Requires=glasseye-daily-updater.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable glasseye-daily-updater.timer
sudo systemctl start glasseye-daily-updater.timer

# Verify
sudo systemctl status glasseye-daily-updater.timer
```

---

## 🔍 Monitoring

### 1. Check Update Logs

```bash
# View recent updates
tail -f /home/x/GlasseyeOS-AI/logs/self_updater.log

# View update audit trail
tail -n 20 /home/x/GlasseyeOS-AI/logs/updates.jsonl | jq '.'

# Check for errors
grep ERROR /home/x/GlasseyeOS-AI/logs/self_updater.log
```

### 2. Monitor Knowledge Base Growth

```bash
cd /home/x/GlasseyeOS-AI

# Check CVE count
sqlite3 knowledge_base.db "SELECT COUNT(*) FROM cves;"

# Check pattern count
sqlite3 knowledge_base.db "SELECT COUNT(*) FROM vulnerability_patterns;"

# Check disclosed bounties
sqlite3 knowledge_base.db "SELECT COUNT(*) FROM disclosed_bounties;"
```

### 3. Cache Size Monitoring

```bash
# Check cache sizes
du -sh /home/x/GlasseyeOS-AI/data_sources/cache/*

# If cache grows too large (>1GB), consider cleanup:
# Keep only last 10000 entries
tail -n 10000 data_sources/cache/attack_patterns.jsonl > data_sources/cache/attack_patterns.jsonl.tmp
mv data_sources/cache/attack_patterns.jsonl.tmp data_sources/cache/attack_patterns.jsonl
```

### 4. Approval Queue Check

```bash
# Check pending approvals
cat /home/x/GlasseyeOS-AI/logs/approval_requests.jsonl | jq 'select(.status == "pending")'

# Count pending approvals
grep '"status": "pending"' /home/x/GlasseyeOS-AI/logs/approval_requests.jsonl | wc -l
```

---

## 🔧 Configuration Tuning

### Rate Limiting

If hitting rate limits, adjust `data_sources/configs/rate_limits.json`:

```json
{
  "github_advisories": {
    "requests_per_hour": 60,  // Reduce from 5000 if no auth token
    "retry_after_seconds": 3600
  }
}
```

### Update Frequency

Adjust `data_sources/configs/update_schedule.json`:

```json
{
  "daily_updates": {
    "enabled": true,
    "time": "02:00",  // Change to preferred time
    "sources": ["nvd_cve", "github_advisories"]
  }
}
```

---

## 🧪 Testing in Production

### 1. Dry Run

```bash
cd /home/x/GlasseyeOS-AI

# Run updates manually to verify
python3 -c "
from self_updater import EnhancedSelfUpdater
u = EnhancedSelfUpdater()
summary = u.run_daily_updates()
print('Daily updates:', summary)
u.close()
"
```

### 2. Monitor First Automated Run

```bash
# Check cron/systemd logs after first scheduled run
tail -f /home/x/GlasseyeOS-AI/logs/cron_daily.log
# or
journalctl -u glasseye-daily-updater.service -f
```

### 3. Verify Knowledge Base Updates

```bash
# Before and after comparison
sqlite3 knowledge_base.db "SELECT COUNT(*) as total_cves FROM cves;"

# Wait for update to run

sqlite3 knowledge_base.db "SELECT COUNT(*) as total_cves FROM cves;"
```

---

## 🚨 Troubleshooting

### Issue: Rate Limit Exceeded

**Symptoms**: `429 Too Many Requests` in logs

**Solution**:
1. Add API authentication token
2. Reduce requests_per_hour in rate_limits.json
3. Increase update frequency (daily → weekly)

### Issue: Pattern Extraction Failing

**Symptoms**: 0 patterns learned from sources with data

**Solution**:
1. Check logs for NLP extraction errors
2. Verify keyword lists in `extract_attack_pattern_detailed()`
3. Add domain-specific keywords

### Issue: Self-Update Blocked

**Symptoms**: Updates available but not applying

**Solution**:
1. Check approval queue: `cat logs/approval_requests.jsonl`
2. Review approval request details
3. Manually approve if safe:
   ```python
   # In Python console
   from self_updater import EnhancedSelfUpdater
   u = EnhancedSelfUpdater()
   u.self_update_code()  # Will show approval details
   ```

### Issue: Tools Not Regenerating

**Symptoms**: New patterns learned but tools not updated

**Solution**:
1. Check pattern cache: `cat data_sources/cache/attack_patterns.jsonl | jq '.'`
2. Verify pattern relevance to tools
3. Force regeneration:
   ```python
   from self_updater import EnhancedSelfUpdater
   u = EnhancedSelfUpdater()
   u.update_generated_tools(force_regenerate=True)
   ```

---

## 📊 Health Check Script

Create `/home/x/GlasseyeOS-AI/health_check.sh`:

```bash
#!/bin/bash

echo "=== GlasseyeOS AI Self-Updater Health Check ==="
echo

# Check if updater is running
echo "1. Checking for running updater processes..."
pgrep -f "self_updater.py" && echo "✅ Updater process found" || echo "ℹ️  No active update in progress"

# Check recent logs
echo
echo "2. Recent log activity (last 5 entries)..."
tail -n 5 logs/self_updater.log

# Check knowledge base
echo
echo "3. Knowledge base statistics..."
sqlite3 knowledge_base.db << SQL
SELECT 'CVEs: ' || COUNT(*) FROM cves;
SELECT 'Patterns: ' || COUNT(*) FROM vulnerability_patterns;
SELECT 'Tools: ' || COUNT(*) FROM generated_tools;
SELECT 'Bounties: ' || COUNT(*) FROM disclosed_bounties;
SQL

# Check cache sizes
echo
echo "4. Cache sizes..."
du -sh data_sources/cache/* 2>/dev/null || echo "No caches yet"

# Check pending approvals
echo
echo "5. Pending approvals..."
PENDING=$(grep -c '"status": "pending"' logs/approval_requests.jsonl 2>/dev/null || echo "0")
echo "Pending approvals: $PENDING"

# Check last update time
echo
echo "6. Last update..."
tail -n 1 logs/updates.jsonl | jq -r '"\(.timestamp) - \(.source): \(.items_added) items"' 2>/dev/null || echo "No updates yet"

echo
echo "✅ Health check complete"
```

```bash
chmod +x health_check.sh
./health_check.sh
```

---

## 📋 Deployment Checklist Summary

- [ ] API credentials configured
- [ ] Test suite passing (25/25 tests)
- [ ] Directory permissions set correctly
- [ ] Log rotation configured (optional)
- [ ] Cron or systemd timer scheduled
- [ ] First manual run successful
- [ ] Monitoring scripts in place
- [ ] Health check script created
- [ ] Rate limits configured appropriately
- [ ] Update schedule configured
- [ ] Backup strategy in place (knowledge_base.db)

---

## 🎯 Post-Deployment

### Week 1 Checklist

- [ ] Day 1: Monitor first automated update
- [ ] Day 2: Check knowledge base growth
- [ ] Day 3: Review approval requests
- [ ] Day 7: Verify weekly updates ran successfully

### Week 2-4 Monitoring

- [ ] Weekly: Review update logs for errors
- [ ] Weekly: Check cache sizes
- [ ] Weekly: Verify program rule monitoring
- [ ] Monthly: Review and approve self-code updates

---

**Deployment Ready!** 🚀

Follow this checklist to ensure smooth production deployment.
