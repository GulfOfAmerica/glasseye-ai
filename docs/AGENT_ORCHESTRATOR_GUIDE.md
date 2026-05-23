# Enhanced Multi-Agent Orchestrator Documentation

## Overview

The Enhanced Agent Orchestrator provides production-grade multi-agent coordination for complex bug bounty campaigns. It enables parallel execution, resource management, failure recovery, and sophisticated campaign workflows.

---

## Architecture

### Core Components

1. **EnhancedAgentOrchestrator** - Main orchestration engine
2. **ResourceManager** - System resource allocation and limits
3. **AgentMessenger** - Inter-agent communication system
4. **WorkloadBalancer** - Work distribution across agents
5. **ResultAggregator** - Finding deduplication and prioritization
6. **CampaignWorkflow** - Multi-phase campaign execution

---

## Features

### 1. Campaign Workflow Engine

Execute complete bug bounty campaigns end-to-end with multi-phase workflows:

```python
from agent_orchestrator import EnhancedAgentOrchestrator, CampaignConfig

orchestrator = EnhancedAgentOrchestrator(max_agents=15, max_memory_gb=16.0)

campaign = CampaignConfig(
    campaign_id="github_copilot_2026",
    target="GitHub Copilot Coding Agent",
    program="github-bug-bounty",
    phases=[
        {'name': 'osint', 'agents': 3, 'parallel': True},
        {'name': 'analysis', 'agents': 2, 'parallel': True},
        {'name': 'hypothesis', 'agents': 1, 'parallel': False},
        {'name': 'testing', 'agents': 5, 'parallel': True, 'human_approval': True},
        {'name': 'documentation', 'agents': 2, 'parallel': True}
    ],
    max_parallel_agents=15,
    human_approval_required=True,
    timeout_minutes=240
)

result = orchestrator.execute_campaign(campaign)
```

**Campaign Phases:**
- **OSINT**: Passive reconnaissance
- **Analysis**: Attack surface mapping
- **Hypothesis**: Vulnerability hypothesis generation
- **Testing**: PoC development (requires human approval)
- **Documentation**: Evidence collection and reporting

### 2. Dynamic Agent Spawning

Automatically spawn specialized agents based on discovered attack surfaces:

```python
# Discovered attack surfaces
attack_surface = {
    'category': 'authentication',  # or 'protocol', 'smart_contract', 'binary'
    'description': 'OAuth 2.0 authentication flow'
}

# Orchestrator selects appropriate specialized agent
agent_id = orchestrator.spawn_specialized_agent(attack_surface)
```

**Agent Mapping:**
- `protocol` → Fuzzing Agent
- `authentication` → Auth Testing Agent
- `configuration` → Static Analysis Agent
- `smart_contract` → Contract Auditor
- `binary` → Reverse Engineering Agent
- `extension` → Malware Analysis Agent

### 3. Workload Balancing

Distribute large workloads across multiple parallel agents:

```python
# Distribute 1000 API endpoints across 10 agents
endpoints = [f"/api/endpoint{i}" for i in range(1000)]

agent_ids = orchestrator.distribute_fuzzing_workload_enhanced(
    endpoints=endpoints,
    fuzzing_strategy="comprehensive",
    agent_count=10
)

# Each agent gets ~100 endpoints
# Results automatically aggregated and deduplicated
```

### 4. Result Aggregation & Deduplication

Automatically merge and deduplicate findings from multiple agents:

```python
# Multiple agents may discover the same vulnerability
agent_results = [
    {
        'agent_id': 'agent_1',
        'findings': [
            {'type': 'Auth Bypass', 'location': '/login', 'cvss_score': 9.1}
        ]
    },
    {
        'agent_id': 'agent_2',
        'findings': [
            {'type': 'Auth Bypass', 'location': '/login', 'cvss_score': 9.1},  # Duplicate
            {'type': 'XSS', 'location': '/search', 'cvss_score': 6.5}
        ]
    }
]

unique_findings = orchestrator.result_aggregator.aggregate_from_agents(agent_results)
prioritized = orchestrator.result_aggregator.prioritize_by_impact(unique_findings)

# Output: 2 unique findings, prioritized by CVSS score
```

### 5. Agent Communication Protocol

Enable agents to share discoveries in real-time:

```python
# Agent A broadcasts discovery
orchestrator.send_agent_message(
    from_agent="fuzzer_agent_1",
    to_agent=None,  # Broadcast to all
    message_type=MessageType.DISCOVERY,
    content={'finding': 'Admin panel at /admin', 'priority': 'high'},
    channel="fuzzing"
)

# Other agents subscribed to "fuzzing" channel receive message
messages = orchestrator.messenger.get_messages("fuzzer_agent_2", "fuzzing")
```

**Message Types:**
- `DISCOVERY` - New attack surface found
- `FINDING` - Vulnerability discovered
- `STATUS_UPDATE` - Agent status change
- `REQUEST_HELP` - Agent needs assistance
- `BROADCAST` - General announcement

### 6. Failure Recovery & Retry Logic

Automatic retry with exponential backoff and human escalation:

```python
# Agent fails during execution
orchestrator.handle_agent_failure(agent_id="failed_agent", task=failed_task)

# Automatic retry (up to max_retries)
# If all retries fail, escalate to human operator
```

**Failure Handling:**
1. Log failure details
2. Increment retry count
3. Spawn replacement agent with same task
4. If max retries exceeded, escalate to human
5. If resource exhaustion, terminate idle agents and retry

### 7. Resource Management

Prevent resource exhaustion with configurable limits:

```python
orchestrator = EnhancedAgentOrchestrator(
    max_agents=10,
    max_memory_gb=16.0
)

# Check resource usage
usage = orchestrator.get_resource_usage()
print(f"Memory: {usage['memory']['used_gb']:.1f}GB / {usage['memory']['limit_gb']}GB")
print(f"CPU: {usage['cpu']['percent']:.1f}%")
print(f"Active agents: {len(orchestrator.active_agents)}")

# Automatic cleanup of idle agents (idle > 5 minutes)
# Resource checks before spawning new agents
```

---

## Campaign Templates

Pre-configured workflows for common scenarios. See `campaign_templates.py`.

---

## Custom Agent Integration

Available custom agents:

```python
AVAILABLE_AGENTS = {
    'osint': 'glasseye-osint-intelligence',
    'contract-auditor': 'glasswing-contract-auditor',
    'security-analyzer': 'glasswing-security-analyzer',
    'bounty-coordinator': 'bounty-research-coordinator',
    'slither-auditor': 'mythos-slither-auditor',
    'reverser': 'mythos-reverser',
    'platform-orchestrator': 'platform-orchestrator'
}

# Spawn custom agent
agent_id = orchestrator.spawn_custom_agent(
    agent_name='osint',
    task_params={'target': 'example.com', 'depth': 'comprehensive'}
)
```

---

## Best Practices

### 1. Human Approval for Testing

Always require human approval before active testing:

```python
config = CampaignConfig(
    ...
    phases=[
        {'name': 'testing', 'agents': 5, 'parallel': True, 'human_approval': True}
    ],
    human_approval_required=True
)
```

### 2. Resource Limits

Set conservative limits initially, then scale up.

### 3. Result Aggregation

Always aggregate and prioritize findings after campaigns.

---

## Troubleshooting

### Resource Exhaustion

**Problem**: "Max agents limit reached"

**Solution**: Terminate idle agents or increase limits

### Campaign Failures

**Problem**: Campaign stops unexpectedly

**Solution**: Check `result['error']` and agent status

---

## API Reference

### EnhancedAgentOrchestrator

**Constructor:**
```python
EnhancedAgentOrchestrator(max_agents=10, max_memory_gb=16.0)
```

**Key Methods:**
- `spawn_agent(agent_type, task)`
- `spawn_specialized_agent(attack_surface)`
- `spawn_custom_agent(agent_name, task_params)`
- `execute_campaign(config)`
- `distribute_fuzzing_workload_enhanced(endpoints, strategy, agent_count)`
- `handle_agent_failure(agent_id, task)`
- `send_agent_message(from_agent, to_agent, message_type, content)`
- `get_resource_usage()`
- `get_status()`
- `shutdown()`

---

**For examples see `agent_orchestrator.py`, `campaign_templates.py`, and `tests/test_agent_orchestrator.py`**
