# Data Sources Directory

This directory contains configurations, caches, and snapshots for external data sources.

## Directory Structure

```
data_sources/
├── cache/                    # Cached data from external sources
│   ├── attack_patterns.jsonl
│   ├── hypotheses.jsonl
│   ├── learned_techniques.jsonl
│   └── research_papers.jsonl
├── configs/                  # Source configurations
│   ├── api_credentials.json (gitignored)
│   ├── rate_limits.json
│   └── update_schedule.json
└── program_snapshots/        # Bug bounty program snapshots
    ├── github.com_latest.json
    └── github.com_2024-01-15T12:00:00.txt
```

## Data Sources

### 1. NVD CVE Feed
- **URL**: https://services.nvd.nist.gov/rest/json/cves/2.0
- **Update Frequency**: Daily
- **Rate Limit**: 50 requests/hour
- **Auth**: Not required

### 2. GitHub Security Advisories
- **URL**: https://api.github.com/advisories
- **Update Frequency**: Daily
- **Rate Limit**: 60 requests/hour (unauthenticated), 5000/hour (authenticated)
- **Auth**: GitHub Personal Access Token (optional, recommended)

### 3. HackerOne Disclosed Reports
- **URL**: https://api.hackerone.com/v1/hackers/disclosed_reports
- **Update Frequency**: Weekly
- **Rate Limit**: Varies by account type
- **Auth**: API token required for full access

### 4. arXiv Security Papers
- **URL**: https://export.arxiv.org/api/query?search_query=cat:cs.CR
- **Update Frequency**: Weekly
- **Rate Limit**: 3 seconds between requests
- **Auth**: Not required

### 5. MITRE CVE Database
- **URL**: https://cve.mitre.org/data/downloads/allitems.csv
- **Update Frequency**: Daily
- **Rate Limit**: No explicit limit
- **Auth**: Not required

## Setup Instructions

### 1. Configure API Credentials

Create `configs/api_credentials.json`:

```json
{
  "github": {
    "token": "ghp_your_personal_access_token",
    "username": "your_username"
  },
  "hackerone": {
    "api_token": "your_api_token",
    "api_identifier": "your_identifier"
  }
}
```

**IMPORTANT**: This file is gitignored. Never commit credentials.
