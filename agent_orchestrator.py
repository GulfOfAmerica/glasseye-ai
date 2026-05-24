#!/usr/bin/env python3
"""
GlasseyeOS AI - Enhanced Agent Orchestrator
Advanced multi-agent coordination for complex bug bounty campaigns.

Features:
- Campaign workflow engine with multi-phase orchestration
- Dynamic agent spawning based on attack surfaces
- Workload balancing across parallel agents
- Result aggregation and deduplication
- Agent-to-agent communication protocol
- Failure recovery and retry logic
- Resource management and limits
"""

import logging
import json
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
import queue
import time
import hashlib
import psutil
from collections import defaultdict


class AgentType(Enum):
    """Available agent types with custom agent mapping."""
    OSINT = "glasseye-osint-intelligence"
    STATIC_ANALYSIS = "glasswing-security-analyzer"
    CONTRACT_AUDITOR = "glasswing-contract-auditor"
    SLITHER_AUDITOR = "mythos-slither-auditor"
    REVERSER = "mythos-reverser"
    BOUNTY_COORDINATOR = "bounty-research-coordinator"
    PLATFORM_ORCHESTRATOR = "platform-orchestrator"
    DYNAMIC_ANALYSIS = "dynamic-fuzzer"
    DOCUMENTATION = "report-generator"
    FUZZING = "fuzzing-agent"
    AUTH_TESTING = "auth-testing-agent"
    MALWARE_ANALYSIS = "malware-analysis-agent"


class CampaignPhase(Enum):
    """Campaign execution phases."""
    RECONNAISSANCE = "reconnaissance"
    ATTACK_SURFACE_MAPPING = "attack_surface_mapping"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    POC_VALIDATION = "poc_validation"
    EVIDENCE_COLLECTION = "evidence_collection"
    REPORT_GENERATION = "report_generation"


class MessageType(Enum):
    """Agent communication message types."""
    DISCOVERY = "discovery"
    FINDING = "finding"
    STATUS_UPDATE = "status_update"
    REQUEST_HELP = "request_help"
    BROADCAST = "broadcast"


@dataclass
class AgentTask:
    """Task for a sub-agent."""
    task_id: str
    agent_type: AgentType
    description: str
    parameters: Dict
    priority: int = 1
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AgentInstance:
    """Running agent instance."""
    agent_id: str
    agent_type: AgentType
    task: AgentTask
    started: str
    status: str = "running"
    pid: Optional[int] = None
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    last_heartbeat: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AgentMessage:
    """Inter-agent communication message."""
    message_id: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcast
    message_type: MessageType
    content: Dict
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    channel: str = "default"


@dataclass
class CampaignConfig:
    """Campaign configuration."""
    campaign_id: str
    target: str
    program: str
    phases: List[Dict]
    max_parallel_agents: int = 10
    human_approval_required: bool = True
    timeout_minutes: int = 120
    resource_limits: Dict = field(default_factory=dict)


@dataclass
class Finding:
    """Security finding from agents."""
    finding_id: str
    vulnerability_type: str
    severity: str
    confidence: float
    location: str
    description: str
    discovered_by: str
    cvss_score: Optional[float] = None
    evidence: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ResourceManager:
    """Manages system resource allocation for agents."""
    
    def __init__(self, max_agents: int = 10, max_memory_gb: float = 16.0, 
                 max_cpu_percent: float = 80.0):
        self.max_agents = max_agents
        self.max_memory_gb = max_memory_gb
        self.max_cpu_percent = max_cpu_percent
        self.logger = logging.getLogger("ResourceManager")
    
    def get_current_usage(self) -> Dict:
        """Get current system resource usage."""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        return {
            'memory_used_gb': memory.used / (1024 ** 3),
            'memory_percent': memory.percent,
            'cpu_percent': cpu,
            'available_memory_gb': memory.available / (1024 ** 3)
        }
    
    def can_spawn_agent(self, active_count: int) -> tuple[bool, str]:
        """Check if resources available to spawn new agent."""
        if active_count >= self.max_agents:
            return False, f"Max agents limit reached ({self.max_agents})"
        
        usage = self.get_current_usage()
        
        if usage['memory_percent'] > 90:
            return False, f"Memory usage critical ({usage['memory_percent']:.1f}%)"
        
        if usage['cpu_percent'] > self.max_cpu_percent:
            return False, f"CPU usage high ({usage['cpu_percent']:.1f}%)"
        
        return True, "Resources available"
    
    def get_resource_stats(self) -> Dict:
        """Get detailed resource statistics."""
        usage = self.get_current_usage()
        return {
            'memory': {
                'used_gb': usage['memory_used_gb'],
                'available_gb': usage['available_memory_gb'],
                'percent': usage['memory_percent'],
                'limit_gb': self.max_memory_gb
            },
            'cpu': {
                'percent': usage['cpu_percent'],
                'limit_percent': self.max_cpu_percent
            },
            'agents': {
                'limit': self.max_agents
            }
        }


class AgentMessenger:
    """Inter-agent communication system."""
    
    def __init__(self):
        self.message_queue: queue.Queue = queue.Queue()
        self.subscriptions: Dict[str, List[str]] = defaultdict(list)
        self.message_history: List[AgentMessage] = []
        self.logger = logging.getLogger("AgentMessenger")
    
    def send_message(self, from_agent: str, to_agent: str, 
                     message_type: MessageType, content: Dict, 
                     channel: str = "default"):
        """Send direct message to specific agent."""
        msg = AgentMessage(
            message_id=self._generate_message_id(),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            channel=channel
        )
        
        self.message_queue.put(msg)
        self.message_history.append(msg)
        self.logger.info(f"Message {msg.message_id}: {from_agent} -> {to_agent} ({message_type.value})")
    
    def broadcast(self, sender: str, message_type: MessageType, 
                   content: Dict, channel: str = "default"):
        """Broadcast message to all agents."""
        msg = AgentMessage(
            message_id=self._generate_message_id(),
            from_agent=sender,
            to_agent=None,  # Broadcast
            message_type=message_type,
            content=content,
            channel=channel
        )
        
        self.message_queue.put(msg)
        self.message_history.append(msg)
        self.logger.info(f"Broadcast {msg.message_id}: {sender} ({message_type.value}) on {channel}")
    
    def subscribe(self, agent_id: str, channel: str):
        """Subscribe agent to channel."""
        if agent_id not in self.subscriptions[channel]:
            self.subscriptions[channel].append(agent_id)
            self.logger.info(f"Agent {agent_id} subscribed to {channel}")
    
    def get_messages(self, agent_id: str, channel: str = "default") -> List[AgentMessage]:
        """Get messages for specific agent."""
        messages = []
        for msg in self.message_history:
            # Direct message to this agent
            if msg.to_agent == agent_id and msg.channel == channel:
                messages.append(msg)
            # Broadcast message on subscribed channel
            elif msg.to_agent is None and msg.channel == channel:
                if agent_id in self.subscriptions[channel]:
                    messages.append(msg)
        
        return messages
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]


class WorkloadBalancer:
    """Distributes work across multiple agents."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def distribute_fuzzing_targets(self, targets: List[str], 
                                   agent_count: int = 5) -> List[List[str]]:
        """Split targets into equal chunks for parallel agents."""
        if not targets:
            return []
        
        chunk_size = max(1, len(targets) // agent_count)
        chunks = []
        
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i + chunk_size]
            chunks.append(chunk)
        
        self.logger.info(f"Split {len(targets)} targets into {len(chunks)} chunks")
        return chunks
    
    def balance_by_priority(self, tasks: List[AgentTask], 
                           agent_count: int) -> List[List[AgentTask]]:
        """Distribute tasks across agents by priority."""
        # Sort by priority (high to low)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        
        # Round-robin distribution
        chunks: List[List[AgentTask]] = [[] for _ in range(agent_count)]
        
        for idx, task in enumerate(sorted_tasks):
            agent_idx = idx % agent_count
            chunks[agent_idx].append(task)
        
        self.logger.info(f"Balanced {len(tasks)} tasks across {agent_count} agents")
        return chunks


class ResultAggregator:
    """Aggregates and deduplicates findings from multiple agents."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.findings: List[Finding] = []
        self.fingerprints: set = set()
    
    def add_finding(self, finding: Finding) -> bool:
        """Add finding if unique."""
        fingerprint = self._generate_fingerprint(finding)
        
        if fingerprint in self.fingerprints:
            self.logger.debug(f"Duplicate finding: {finding.vulnerability_type} at {finding.location}")
            return False
        
        self.findings.append(finding)
        self.fingerprints.add(fingerprint)
        self.logger.info(f"New finding: {finding.vulnerability_type} (severity: {finding.severity})")
        return True
    
    def aggregate_from_agents(self, agent_results: List[Dict]) -> List[Finding]:
        """Aggregate findings from multiple agent results."""
        unique_findings = []
        
        for result in agent_results:
            if 'findings' not in result:
                continue
            
            for finding_data in result['findings']:
                finding = Finding(
                    finding_id=self._generate_finding_id(),
                    vulnerability_type=finding_data.get('type', 'Unknown'),
                    severity=finding_data.get('severity', 'Unknown'),
                    confidence=finding_data.get('confidence', 0.5),
                    location=finding_data.get('location', 'Unknown'),
                    description=finding_data.get('description', ''),
                    discovered_by=result.get('agent_id', 'Unknown'),
                    cvss_score=finding_data.get('cvss_score'),
                    evidence=finding_data.get('evidence', {})
                )
                
                if self.add_finding(finding):
                    unique_findings.append(finding)
        
        self.logger.info(f"Aggregated {len(unique_findings)} unique findings")
        return unique_findings
    
    def prioritize_by_impact(self, findings: Optional[List[Finding]] = None) -> List[Finding]:
        """Sort findings by severity and CVSS score."""
        findings_to_sort = findings or self.findings
        
        severity_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'Unknown': 0}
        
        sorted_findings = sorted(
            findings_to_sort,
            key=lambda f: (
                severity_order.get(f.severity, 0),
                f.cvss_score or 0.0,
                f.confidence
            ),
            reverse=True
        )
        
        return sorted_findings
    
    def _generate_fingerprint(self, finding: Finding) -> str:
        """Generate unique fingerprint for deduplication."""
        data = f"{finding.vulnerability_type}_{finding.location}_{finding.severity}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _generate_finding_id(self) -> str:
        """Generate unique finding ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return f"finding_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"


class CampaignWorkflow:
    """Orchestrates multi-phase bug bounty campaigns."""
    
    def __init__(self, orchestrator: 'EnhancedAgentOrchestrator'):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger("CampaignWorkflow")
    
    def execute_campaign(self, config: CampaignConfig) -> Dict:
        """Execute complete campaign workflow."""
        self.logger.info(f"Starting campaign: {config.campaign_id} for {config.target}")
        
        campaign_result = {
            'campaign_id': config.campaign_id,
            'target': config.target,
            'program': config.program,
            'started': datetime.now(timezone.utc).isoformat(),
            'phases': [],
            'findings': [],
            'status': 'running'
        }
        
        try:
            for phase_config in config.phases:
                phase_name = phase_config['name']
                self.logger.info(f"Executing phase: {phase_name}")
                
                phase_result = self._execute_phase(phase_config, config, campaign_result)
                campaign_result['phases'].append(phase_result)
                
                # Check for human approval requirement
                if phase_config.get('human_approval') and config.human_approval_required:
                    self.logger.info(f"Phase {phase_name} requires human approval")
                    approved = self._request_human_approval(phase_result)
                    
                    if not approved:
                        self.logger.warning(f"Phase {phase_name} not approved, stopping campaign")
                        campaign_result['status'] = 'stopped_by_human'
                        break
            
            campaign_result['completed'] = datetime.now(timezone.utc).isoformat()
            campaign_result['status'] = 'completed'
            
        except Exception as e:
            self.logger.error(f"Campaign failed: {e}")
            campaign_result['status'] = 'failed'
            campaign_result['error'] = str(e)
        
        return campaign_result
    
    def _execute_phase(self, phase_config: Dict, campaign_config: CampaignConfig,
                       campaign_result: Dict) -> Dict:
        """Execute single campaign phase."""
        phase_name = phase_config['name']
        agent_count = phase_config.get('agents', 1)
        parallel = phase_config.get('parallel', False)
        
        phase_result = {
            'name': phase_name,
            'started': datetime.now(timezone.utc).isoformat(),
            'agent_count': agent_count,
            'parallel': parallel,
            'findings': []
        }
        
        # Spawn agents based on phase type
        if phase_name == 'osint':
            tasks = self._spawn_osint_agents(campaign_config.target, agent_count)
        elif phase_name == 'analysis':
            tasks = self._spawn_analysis_agents(campaign_result, agent_count)
        elif phase_name == 'hypothesis':
            tasks = self._spawn_hypothesis_agents(campaign_result)
        elif phase_name == 'testing':
            tasks = self._spawn_testing_agents(campaign_result, agent_count)
        elif phase_name == 'documentation':
            tasks = self._spawn_documentation_agents(campaign_result, agent_count)
        else:
            tasks = []
        
        # Execute tasks
        if parallel:
            results = self._execute_parallel(tasks)
        else:
            results = self._execute_sequential(tasks)
        
        phase_result['results'] = results
        phase_result['completed'] = datetime.now(timezone.utc).isoformat()
        
        return phase_result
    
    def _spawn_osint_agents(self, target: str, count: int) -> List[AgentTask]:
        """Spawn parallel OSINT agents."""
        tasks = []
        
        for i in range(count):
            task = AgentTask(
                task_id=f"osint_{i}",
                agent_type=AgentType.OSINT,
                description=f"OSINT reconnaissance {i+1}/{count}",
                parameters={'target': target, 'depth': 'comprehensive'},
                priority=10
            )
            tasks.append(task)
        
        return tasks
    
    def _spawn_analysis_agents(self, campaign_result: Dict, count: int) -> List[AgentTask]:
        """Spawn analysis agents based on OSINT findings."""
        tasks = []
        
        # Extract attack surfaces from previous phases
        attack_surfaces = self._extract_attack_surfaces(campaign_result)
        
        for i in range(count):
            task = AgentTask(
                task_id=f"analysis_{i}",
                agent_type=AgentType.STATIC_ANALYSIS,
                description=f"Attack surface analysis {i+1}/{count}",
                parameters={'surfaces': attack_surfaces},
                priority=8
            )
            tasks.append(task)
        
        return tasks
    
    def _spawn_hypothesis_agents(self, campaign_result: Dict) -> List[AgentTask]:
        """Generate vulnerability hypotheses."""
        return [AgentTask(
            task_id="hypothesis_gen",
            agent_type=AgentType.STATIC_ANALYSIS,
            description="Generate vulnerability hypotheses",
            parameters={'campaign_data': campaign_result},
            priority=7
        )]
    
    def _spawn_testing_agents(self, campaign_result: Dict, count: int) -> List[AgentTask]:
        """Spawn testing agents for approved hypotheses."""
        tasks = []
        
        for i in range(count):
            task = AgentTask(
                task_id=f"testing_{i}",
                agent_type=AgentType.DYNAMIC_ANALYSIS,
                description=f"PoC validation {i+1}/{count}",
                parameters={'campaign_data': campaign_result},
                priority=6
            )
            tasks.append(task)
        
        return tasks
    
    def _spawn_documentation_agents(self, campaign_result: Dict, count: int) -> List[AgentTask]:
        """Spawn documentation agents."""
        tasks = []
        
        for i in range(count):
            task = AgentTask(
                task_id=f"docs_{i}",
                agent_type=AgentType.DOCUMENTATION,
                description=f"Report generation {i+1}/{count}",
                parameters={'findings': campaign_result.get('findings', [])},
                priority=5
            )
            tasks.append(task)
        
        return tasks
    
    def _execute_parallel(self, tasks: List[AgentTask]) -> List[Dict]:
        """Execute tasks in parallel."""
        results = []
        agents = []
        
        for task in tasks:
            agent_id = self.orchestrator.spawn_agent(task.agent_type, task)
            agents.append((agent_id, task))
        
        # Wait for all agents
        for agent_id, task in agents:
            if task.result:
                results.append(task.result)
        
        return results
    
    def _execute_sequential(self, tasks: List[AgentTask]) -> List[Dict]:
        """Execute tasks sequentially."""
        results = []
        
        for task in tasks:
            agent_id = self.orchestrator.spawn_agent(task.agent_type, task)
            if task.result:
                results.append(task.result)
        
        return results
    
    def _extract_attack_surfaces(self, campaign_result: Dict) -> List[Dict]:
        """Extract attack surfaces from campaign data."""
        surfaces = []
        
        for phase in campaign_result.get('phases', []):
            for result in phase.get('results', []):
                if 'attack_surfaces' in result:
                    surfaces.extend(result['attack_surfaces'])
        
        return surfaces
    
    def _request_human_approval(self, phase_result: Dict) -> bool:
        """Request human approval (simulated)."""
        self.logger.info("=" * 60)
        self.logger.info("HUMAN APPROVAL REQUIRED")
        self.logger.info(f"Phase: {phase_result['name']}")
        self.logger.info(f"Findings: {len(phase_result.get('findings', []))}")
        self.logger.info("=" * 60)
        
        # In production, would wait for actual human input
        # For demo, auto-approve
        return True


class EnhancedAgentOrchestrator:
    """
    Enhanced multi-agent coordinator for complex bug bounty campaigns.
    
    New Capabilities:
    - Campaign workflow engine
    - Dynamic agent spawning
    - Workload balancing
    - Result aggregation & deduplication
    - Agent communication protocol
    - Failure recovery & retry logic
    - Resource management
    """
    
    def __init__(self, max_agents: int = 10, max_memory_gb: float = 16.0):
        self.logger = self._setup_logging()
        self.task_queue = queue.PriorityQueue()
        self.active_agents: Dict[str, AgentInstance] = {}
        self.completed_tasks: List[AgentTask] = []
        self.max_concurrent_agents = max_agents
        
        # Enhanced components
        self.resource_manager = ResourceManager(max_agents, max_memory_gb)
        self.messenger = AgentMessenger()
        self.workload_balancer = WorkloadBalancer(self.logger)
        self.result_aggregator = ResultAggregator(self.logger)
        self.campaign_workflow = CampaignWorkflow(self)
        
        # Failure tracking
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.idle_check_interval = 300  # 5 minutes
        
        # Available custom agents
        self.available_agents = {
            'osint': AgentType.OSINT,
            'contract-auditor': AgentType.CONTRACT_AUDITOR,
            'security-analyzer': AgentType.STATIC_ANALYSIS,
            'bounty-coordinator': AgentType.BOUNTY_COORDINATOR,
            'slither-auditor': AgentType.SLITHER_AUDITOR,
            'reverser': AgentType.REVERSER,
            'platform-orchestrator': AgentType.PLATFORM_ORCHESTRATOR
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configure orchestrator logging."""
        logger = logging.getLogger("AgentOrchestrator")
        logger.setLevel(logging.INFO)
        
        fh = logging.FileHandler("logs/agent_orchestrator.log")
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def submit_task(self, task: AgentTask):
        """
        Submit task to queue.
        
        Tasks are prioritized by:
        1. Priority value (1-10, higher = more urgent)
        2. Expected bounty value
        3. FIFO for same priority
        """
        self.logger.info(f"Submitting task: {task.task_id} (priority: {task.priority})")
        
        # PriorityQueue uses (priority, item) tuples
        # Lower priority number = higher priority, so negate
        # Add unique counter to break ties and avoid comparison of AgentTask objects
        import time
        self.task_queue.put((-task.priority, time.time(), task))
    
    def spawn_agent(self, agent_type: AgentType, task: AgentTask) -> str:
        """
        Spawn specialized sub-agent with resource checking.
        
        Returns agent_id or raises exception if resources unavailable.
        """
        # Check resource availability
        can_spawn, reason = self.resource_manager.can_spawn_agent(len(self.active_agents))
        
        if not can_spawn:
            self.logger.warning(f"Cannot spawn agent: {reason}")
            # Try to clean up idle agents
            self._terminate_idle_agents()
            
            # Recheck
            can_spawn, reason = self.resource_manager.can_spawn_agent(len(self.active_agents))
            if not can_spawn:
                raise RuntimeError(f"Resource limit: {reason}")
        
        agent_id = f"{agent_type.value}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        agent = AgentInstance(
            agent_id=agent_id,
            agent_type=agent_type,
            task=task,
            started=datetime.now(timezone.utc).isoformat(),
            status="running"
        )
        
        self.active_agents[agent_id] = agent
        task.status = "running"
        
        self.logger.info(f"Spawned agent: {agent_id} for task {task.task_id}")
        
        # Subscribe to communication channels
        self.messenger.subscribe(agent_id, "default")
        self.messenger.subscribe(agent_id, task.agent_type.value)
        
        # In production: Launch actual sub-agent via task tool
        # For demo: Simulate execution
        self._simulate_agent_execution(agent)
        
        return agent_id
    
    def spawn_specialized_agent(self, attack_surface: Dict) -> str:
        """
        Dynamically spawn agent based on attack surface type.
        
        Maps attack surface categories to specialized agent types.
        """
        agent_mapping = {
            'protocol': AgentType.FUZZING,
            'authentication': AgentType.AUTH_TESTING,
            'configuration': AgentType.STATIC_ANALYSIS,
            'extension': AgentType.MALWARE_ANALYSIS,
            'smart_contract': AgentType.CONTRACT_AUDITOR,
            'binary': AgentType.REVERSER
        }
        
        category = attack_surface.get('category', 'unknown')
        agent_type = agent_mapping.get(category, AgentType.STATIC_ANALYSIS)
        
        task = AgentTask(
            task_id=f"dynamic_{category}_{int(time.time())}",
            agent_type=agent_type,
            description=f"Analyze {category} attack surface",
            parameters={'attack_surface': attack_surface},
            priority=7
        )
        
        self.logger.info(f"Spawning specialized {agent_type.value} for {category}")
        return self.spawn_agent(agent_type, task)
    
    def spawn_custom_agent(self, agent_name: str, task_params: Dict) -> str:
        """Spawn from available custom agents."""
        if agent_name not in self.available_agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent_type = self.available_agents[agent_name]
        
        task = AgentTask(
            task_id=f"{agent_name}_{int(time.time())}",
            agent_type=agent_type,
            description=f"Custom task: {agent_name}",
            parameters=task_params,
            priority=5
        )
        
        return self.spawn_agent(agent_type, task)
    
    def _simulate_agent_execution(self, agent: AgentInstance):
        """Simulate agent execution (for demo)."""
        # In production, would launch actual agent process
        # For demo, just mark as completed
        
        self.logger.info(f"Agent {agent.agent_id} executing task: {agent.task.description}")
        
        # Simulate results based on agent type
        if agent.agent_type == AgentType.OSINT:
            result = {
                "subdomains": ["api.target.com", "dev.target.com"],
                "technologies": ["Node.js", "Express", "MongoDB"],
                "emails": ["contact@target.com"],
                "social_profiles": ["twitter.com/target"]
            }
        elif agent.agent_type == AgentType.STATIC_ANALYSIS:
            result = {
                "vulnerabilities": [
                    {"type": "IDOR", "confidence": 0.7, "location": "/api/users/:id"},
                    {"type": "XSS", "confidence": 0.5, "location": "/search"}
                ],
                "dependencies": ["express@4.17.1", "mongoose@5.12.0"],
                "outdated": ["express"]
            }
        elif agent.agent_type == AgentType.DYNAMIC_ANALYSIS:
            result = {
                "endpoints_tested": 15,
                "findings": [
                    {"type": "Rate Limiting Bypass", "severity": "Medium"}
                ],
                "coverage": 0.65
            }
        else:
            result = {"status": "completed"}
        
        agent.task.result = result
        agent.task.status = "completed"
        agent.status = "completed"
        
        self.completed_tasks.append(agent.task)
        
        self.logger.info(f"Agent {agent.agent_id} completed task")
    
    def handle_agent_failure(self, agent_id: str, task: AgentTask) -> Optional[str]:
        """
        Handle agent failure with retry logic.
        
        Steps:
        1. Log failure
        2. Increment retry count
        3. Spawn replacement if under max retries
        4. Escalate to human if max retries exceeded
        """
        self.logger.error(f"Agent {agent_id} failed task {task.task_id}")
        
        task.retry_count += 1
        task.error = f"Agent {agent_id} failed"
        
        # Track failures
        self.failure_counts[task.task_id] += 1
        
        if task.retry_count < task.max_retries:
            self.logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count + 1}/{task.max_retries})")
            
            # Create new task instance with incremented retry
            retry_task = AgentTask(
                task_id=f"{task.task_id}_retry_{task.retry_count}",
                agent_type=task.agent_type,
                description=f"{task.description} (retry {task.retry_count})",
                parameters=task.parameters,
                priority=task.priority + 1,  # Increase priority for retries
                retry_count=task.retry_count,
                max_retries=task.max_retries
            )
            
            try:
                replacement_id = self.spawn_agent(task.agent_type, retry_task)
                self.logger.info(f"Spawned replacement agent: {replacement_id}")
                return replacement_id
            except RuntimeError as e:
                self.logger.error(f"Cannot spawn replacement: {e}")
                self._escalate_to_human(task, "resource_exhaustion")
                return None
        else:
            self.logger.error(f"Max retries exceeded for task {task.task_id}")
            self._escalate_to_human(task, "repeated_failures")
            return None
    
    def _escalate_to_human(self, task: AgentTask, reason: str):
        """Escalate failed task to human operator."""
        self.logger.critical("=" * 60)
        self.logger.critical("HUMAN INTERVENTION REQUIRED")
        self.logger.critical(f"Task: {task.task_id}")
        self.logger.critical(f"Description: {task.description}")
        self.logger.critical(f"Reason: {reason}")
        self.logger.critical(f"Retries attempted: {task.retry_count}/{task.max_retries}")
        self.logger.critical("=" * 60)
    
    def _terminate_idle_agents(self):
        """Terminate agents idle for more than configured interval."""
        now = datetime.now(timezone.utc)
        to_terminate = []
        
        for agent_id, agent in self.active_agents.items():
            last_heartbeat = datetime.fromisoformat(agent.last_heartbeat)
            idle_time = (now - last_heartbeat).total_seconds()
            
            if idle_time > self.idle_check_interval and agent.status == "running":
                self.logger.warning(f"Agent {agent_id} idle for {idle_time:.0f}s, terminating")
                to_terminate.append(agent_id)
        
        for agent_id in to_terminate:
            agent = self.active_agents[agent_id]
            agent.status = "terminated"
            agent.task.status = "failed"
            agent.task.error = "Idle timeout"
            del self.active_agents[agent_id]
        
        if to_terminate:
            self.logger.info(f"Terminated {len(to_terminate)} idle agents")
    
    def distribute_fuzzing_workload_enhanced(self, endpoints: List[str], 
                                            fuzzing_strategy: str,
                                            agent_count: Optional[int] = None) -> List[str]:
        """
        Enhanced fuzzing workload distribution using workload balancer.
        
        Returns list of spawned agent IDs.
        """
        if agent_count is None:
            agent_count = min(5, self.max_concurrent_agents)
        
        self.logger.info(f"Distributing {len(endpoints)} endpoints across {agent_count} agents")
        
        # Use workload balancer to create chunks
        chunks = self.workload_balancer.distribute_fuzzing_targets(endpoints, agent_count)
        
        agent_ids = []
        
        for idx, chunk in enumerate(chunks):
            task = AgentTask(
                task_id=f"fuzzer_batch_{idx}_{int(time.time())}",
                agent_type=AgentType.DYNAMIC_ANALYSIS,
                description=f"Fuzz batch {idx+1}/{len(chunks)} ({len(chunk)} endpoints)",
                parameters={
                    "endpoints": chunk,
                    "strategy": fuzzing_strategy
                },
                priority=5
            )
            
            try:
                agent_id = self.spawn_agent(AgentType.DYNAMIC_ANALYSIS, task)
                agent_ids.append(agent_id)
                
                # Send message to other fuzzers about work assignment
                self.messenger.broadcast(
                    sender=agent_id,
                    message_type=MessageType.STATUS_UPDATE,
                    content={"status": "started", "endpoints": len(chunk)},
                    channel="fuzzing"
                )
            except RuntimeError as e:
                self.logger.error(f"Failed to spawn fuzzer {idx}: {e}")
        
        self.logger.info(f"Spawned {len(agent_ids)} fuzzing agents")
        return agent_ids
    
    def execute_campaign(self, config: CampaignConfig) -> Dict:
        """
        Execute complete bug bounty campaign.
        
        Wrapper for campaign workflow engine.
        """
        return self.campaign_workflow.execute_campaign(config)
    
    def send_agent_message(self, from_agent: str, to_agent: Optional[str],
                          message_type: MessageType, content: Dict,
                          channel: str = "default"):
        """
        Send message between agents.
        
        Use to_agent=None for broadcast.
        """
        if to_agent:
            self.messenger.send_message(from_agent, to_agent, message_type, content, channel)
        else:
            self.messenger.broadcast(from_agent, message_type, content, channel)
    
    def get_resource_usage(self) -> Dict:
        """Get current resource usage statistics."""
        return self.resource_manager.get_resource_stats()
    
    def coordinate_reconnaissance(self, target: str, scope: List[str]) -> Dict:
        """
        Coordinate parallel reconnaissance campaign.
        
        Phases:
        1. OSINT (passive) - glasseye-osint-intelligence
        2. Static analysis - glasswing-security-analyzer
        3. Dynamic analysis - custom fuzzer
        4. Documentation - report generator
        
        Returns aggregated findings.
        """
        self.logger.info(f"Coordinating reconnaissance for: {target}")
        
        campaign = {
            "target": target,
            "started": datetime.now(timezone.utc).isoformat(),
            "phases": [],
            "findings": []
        }
        
        # Phase 1: OSINT
        osint_task = AgentTask(
            task_id=f"osint_{target}",
            agent_type=AgentType.OSINT,
            description=f"Passive OSINT for {target}",
            parameters={"target": target, "scope": scope},
            priority=10  # High priority
        )
        
        self.submit_task(osint_task)
        osint_agent = self.spawn_agent(AgentType.OSINT, osint_task)
        campaign["phases"].append({"phase": "OSINT", "agent": osint_agent})
        
        # Phase 2: Static Analysis (parallel)
        static_task = AgentTask(
            task_id=f"static_{target}",
            agent_type=AgentType.STATIC_ANALYSIS,
            description=f"Static analysis for {target}",
            parameters={"target": target},
            priority=8
        )
        
        self.submit_task(static_task)
        static_agent = self.spawn_agent(AgentType.STATIC_ANALYSIS, static_task)
        campaign["phases"].append({"phase": "Static Analysis", "agent": static_agent})
        
        # Phase 3: Dynamic Analysis
        dynamic_task = AgentTask(
            task_id=f"dynamic_{target}",
            agent_type=AgentType.DYNAMIC_ANALYSIS,
            description=f"Dynamic fuzzing for {target}",
            parameters={"target": target, "scope": scope},
            priority=6
        )
        
        self.submit_task(dynamic_task)
        dynamic_agent = self.spawn_agent(AgentType.DYNAMIC_ANALYSIS, dynamic_task)
        campaign["phases"].append({"phase": "Dynamic Analysis", "agent": dynamic_agent})
        
        # Aggregate findings
        campaign["findings"] = self.aggregate_findings([osint_task, static_task, dynamic_task])
        campaign["completed"] = datetime.now(timezone.utc).isoformat()
        
        self.logger.info(f"Reconnaissance campaign complete: {len(campaign['findings'])} findings")
        
        return campaign
    
    def distribute_fuzzing_workload(self, endpoints: List[str], 
                                   fuzzing_strategy: str) -> List[str]:
        """
        Distribute fuzzing workload across multiple agents.
        
        Splits endpoints into batches and assigns to parallel fuzzers.
        
        Returns list of agent IDs.
        """
        self.logger.info(f"Distributing fuzzing for {len(endpoints)} endpoints")
        
        # Split endpoints into batches
        batch_size = max(1, len(endpoints) // self.max_concurrent_agents)
        batches = [endpoints[i:i+batch_size] for i in range(0, len(endpoints), batch_size)]
        
        agent_ids = []
        
        for idx, batch in enumerate(batches):
            task = AgentTask(
                task_id=f"fuzzer_batch_{idx}",
                agent_type=AgentType.DYNAMIC_ANALYSIS,
                description=f"Fuzz batch {idx+1}/{len(batches)}",
                parameters={
                    "endpoints": batch,
                    "strategy": fuzzing_strategy
                },
                priority=5
            )
            
            self.submit_task(task)
            agent_id = self.spawn_agent(AgentType.DYNAMIC_ANALYSIS, task)
            agent_ids.append(agent_id)
        
        self.logger.info(f"Spawned {len(agent_ids)} fuzzing agents")
        
        return agent_ids
    
    def aggregate_findings(self, tasks: List[AgentTask]) -> List[Dict]:
        """
        Aggregate and deduplicate findings from multiple agents.
        
        Returns consolidated list of unique findings.
        """
        self.logger.info(f"Aggregating findings from {len(tasks)} tasks")
        
        all_findings = []
        seen_fingerprints = set()
        
        for task in tasks:
            if task.result is None:
                continue
            
            # Extract findings based on task type
            if task.agent_type == AgentType.STATIC_ANALYSIS:
                findings = task.result.get("vulnerabilities", [])
                for finding in findings:
                    # Create fingerprint for deduplication
                    fingerprint = f"{finding['type']}_{finding['location']}"
                    
                    if fingerprint not in seen_fingerprints:
                        all_findings.append({
                            "source": "static_analysis",
                            "type": finding["type"],
                            "confidence": finding["confidence"],
                            "location": finding["location"]
                        })
                        seen_fingerprints.add(fingerprint)
            
            elif task.agent_type == AgentType.DYNAMIC_ANALYSIS:
                findings = task.result.get("findings", [])
                for finding in findings:
                    fingerprint = f"{finding['type']}_{finding.get('location', 'unknown')}"
                    
                    if fingerprint not in seen_fingerprints:
                        all_findings.append({
                            "source": "dynamic_analysis",
                            "type": finding["type"],
                            "severity": finding["severity"]
                        })
                        seen_fingerprints.add(fingerprint)
        
        self.logger.info(f"Aggregated {len(all_findings)} unique findings")
        
        return all_findings
    
    def prioritize_work(self, tasks: List[AgentTask], 
                       bounty_estimates: Dict[str, int]) -> List[AgentTask]:
        """
        Prioritize tasks by expected ROI.
        
        ROI = (Expected Bounty * Confidence) / Effort
        
        Returns sorted list of tasks.
        """
        self.logger.info(f"Prioritizing {len(tasks)} tasks")
        
        scored_tasks = []
        
        for task in tasks:
            # Get bounty estimate
            vuln_type = task.parameters.get("vulnerability_type", "unknown")
            expected_bounty = bounty_estimates.get(vuln_type, 1000)
            
            # Estimate effort (in hours)
            effort_estimates = {
                AgentType.OSINT: 2,
                AgentType.STATIC_ANALYSIS: 4,
                AgentType.DYNAMIC_ANALYSIS: 8,
                AgentType.DOCUMENTATION: 1
            }
            effort = effort_estimates.get(task.agent_type, 5)
            
            # Calculate ROI (assuming 70% confidence)
            roi = (expected_bounty * 0.7) / effort
            
            scored_tasks.append((roi, task))
        
        # Sort by ROI (descending)
        scored_tasks.sort(key=lambda x: x[0], reverse=True)
        
        prioritized = [task for roi, task in scored_tasks]
        
        self.logger.info("Tasks prioritized by ROI")
        
        return prioritized
    
    def get_status(self) -> Dict:
        """
        Get orchestrator status.
        
        Returns counts and active agents.
        """
        return {
            "active_agents": len(self.active_agents),
            "queued_tasks": self.task_queue.qsize(),
            "completed_tasks": len(self.completed_tasks),
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "type": agent.agent_type.value,
                    "status": agent.status,
                    "task": agent.task.description
                }
                for agent in self.active_agents.values()
            ]
        }
    
    def shutdown(self):
        """Gracefully shutdown all agents."""
        self.logger.info("Shutting down orchestrator...")
        
        for agent_id, agent in self.active_agents.items():
            if agent.status == "running":
                self.logger.info(f"Stopping agent: {agent_id}")
                agent.status = "stopped"
        
        self.active_agents.clear()
        self.logger.info("All agents stopped")


if __name__ == "__main__":
    # Demo enhanced agent orchestrator
    print("=" * 70)
    print("GlasseyeOS AI - Enhanced Multi-Agent Orchestrator Demo")
    print("=" * 70)
    print()
    
    orchestrator = EnhancedAgentOrchestrator(max_agents=10, max_memory_gb=16.0)
    
    # Test 1: Resource Management
    print("1. Resource Management")
    print("   " + "-" * 60)
    resources = orchestrator.get_resource_usage()
    print(f"   Memory: {resources['memory']['used_gb']:.1f}GB / {resources['memory']['limit_gb']}GB")
    print(f"   CPU: {resources['cpu']['percent']:.1f}% / {resources['cpu']['limit_percent']}%")
    print(f"   Agent limit: {resources['agents']['limit']}")
    print()
    
    # Test 2: Dynamic Agent Spawning
    print("2. Dynamic Agent Spawning Based on Attack Surfaces")
    print("   " + "-" * 60)
    
    attack_surfaces = [
        {'category': 'protocol', 'description': 'JSON-RPC protocol'},
        {'category': 'authentication', 'description': 'OAuth 2.0 flow'},
        {'category': 'smart_contract', 'description': 'Solidity contract'},
    ]
    
    for surface in attack_surfaces:
        agent_id = orchestrator.spawn_specialized_agent(surface)
        print(f"   {surface['category']}: spawned {agent_id[:40]}...")
    print()
    
    # Test 3: Enhanced Workload Distribution
    print("3. Enhanced Fuzzing Workload Distribution")
    print("   " + "-" * 60)
    
    endpoints = [f"/api/v1/endpoint{i}" for i in range(50)]
    fuzzer_agents = orchestrator.distribute_fuzzing_workload_enhanced(
        endpoints, 
        fuzzing_strategy="comprehensive",
        agent_count=5
    )
    
    print(f"   Total endpoints: {len(endpoints)}")
    print(f"   Fuzzer agents spawned: {len(fuzzer_agents)}")
    print(f"   Endpoints per agent: ~{len(endpoints) // len(fuzzer_agents)}")
    print()
    
    # Test 4: Agent Communication
    print("4. Inter-Agent Communication")
    print("   " + "-" * 60)
    
    # Simulate discovery message
    if fuzzer_agents:
        orchestrator.send_agent_message(
            from_agent=fuzzer_agents[0],
            to_agent=None,  # Broadcast
            message_type=MessageType.DISCOVERY,
            content={'finding': 'Admin panel found at /admin', 'priority': 'high'},
            channel="fuzzing"
        )
        print(f"   Broadcast: Agent found admin panel")
        
        # Check messages
        messages = orchestrator.messenger.get_messages(fuzzer_agents[1], "fuzzing")
        print(f"   Messages received by other agents: {len(messages)}")
    print()
    
    # Test 5: Campaign Workflow Execution
    print("5. Campaign Workflow Execution")
    print("   " + "-" * 60)
    
    campaign_config = CampaignConfig(
        campaign_id="github_copilot_2026",
        target="GitHub Copilot Coding Agent",
        program="github-bug-bounty",
        phases=[
            {'name': 'osint', 'agents': 3, 'parallel': True},
            {'name': 'analysis', 'agents': 2, 'parallel': True},
            {'name': 'hypothesis', 'agents': 1, 'parallel': False},
            {'name': 'testing', 'agents': 2, 'parallel': True, 'human_approval': True},
            {'name': 'documentation', 'agents': 1, 'parallel': False}
        ],
        max_parallel_agents=10,
        human_approval_required=True,
        timeout_minutes=120
    )
    
    campaign_result = orchestrator.execute_campaign(campaign_config)
    
    print(f"   Campaign: {campaign_result['campaign_id']}")
    print(f"   Target: {campaign_result['target']}")
    print(f"   Status: {campaign_result['status']}")
    print(f"   Phases executed: {len(campaign_result['phases'])}")
    
    for phase in campaign_result['phases']:
        print(f"     - {phase['name']}: {phase['agent_count']} agents ({'parallel' if phase['parallel'] else 'sequential'})")
    print()
    
    # Test 6: Result Aggregation & Deduplication
    print("6. Result Aggregation & Deduplication")
    print("   " + "-" * 60)
    
    # Simulate findings from multiple agents
    agent_results = [
        {
            'agent_id': 'agent_1',
            'findings': [
                {'type': 'Authentication Bypass', 'severity': 'Critical', 'confidence': 0.9,
                 'location': '/api/login', 'description': 'JWT bypass', 'cvss_score': 9.1},
                {'type': 'IDOR', 'severity': 'High', 'confidence': 0.8,
                 'location': '/api/users/:id', 'description': 'User IDOR', 'cvss_score': 7.5}
            ]
        },
        {
            'agent_id': 'agent_2',
            'findings': [
                {'type': 'Authentication Bypass', 'severity': 'Critical', 'confidence': 0.9,
                 'location': '/api/login', 'description': 'JWT bypass (duplicate)', 'cvss_score': 9.1},
                {'type': 'XSS', 'severity': 'Medium', 'confidence': 0.7,
                 'location': '/search', 'description': 'Reflected XSS', 'cvss_score': 6.1}
            ]
        }
    ]
    
    unique_findings = orchestrator.result_aggregator.aggregate_from_agents(agent_results)
    prioritized = orchestrator.result_aggregator.prioritize_by_impact(unique_findings)
    
    print(f"   Total findings from agents: {sum(len(r['findings']) for r in agent_results)}")
    print(f"   Unique findings (after dedup): {len(unique_findings)}")
    print(f"   Prioritized by impact:")
    
    for idx, finding in enumerate(prioritized, 1):
        print(f"     {idx}. {finding.vulnerability_type} ({finding.severity}) - CVSS: {finding.cvss_score}")
    print()
    
    # Test 7: Failure Recovery
    print("7. Failure Recovery & Retry Logic")
    print("   " + "-" * 60)
    
    failed_task = AgentTask(
        task_id="test_failure",
        agent_type=AgentType.DYNAMIC_ANALYSIS,
        description="Test failure handling",
        parameters={'test': True},
        priority=5,
        max_retries=3
    )
    
    # Simulate failure and retry
    print(f"   Task: {failed_task.task_id}")
    print(f"   Max retries: {failed_task.max_retries}")
    print(f"   Simulating failure...")
    
    replacement = orchestrator.handle_agent_failure("failed_agent_123", failed_task)
    
    if replacement:
        print(f"   Replacement agent spawned: {replacement[:40]}...")
    else:
        print(f"   Task escalated to human after {failed_task.retry_count} retries")
    print()
    
    # Test 8: Custom Agent Spawning
    print("8. Custom Agent Invocation")
    print("   " + "-" * 60)
    
    available = orchestrator.available_agents
    print(f"   Available custom agents: {len(available)}")
    
    for agent_name, agent_type in list(available.items())[:3]:
        print(f"     - {agent_name}: {agent_type.value}")
    
    # Spawn custom OSINT agent
    try:
        custom_agent = orchestrator.spawn_custom_agent(
            agent_name='osint',
            task_params={'target': 'example.com', 'depth': 'comprehensive'}
        )
    except RuntimeError as e:
        print(f'   Note: {e} (agents still active from previous steps)')
        custom_agent = None
    if custom_agent:
        print(f"   Spawned custom OSINT agent: {custom_agent[:40]}...")
    print()
    
    # Test 9: Orchestrator Status
    print("9. Orchestrator Status")
    print("   " + "-" * 60)
    
    status = orchestrator.get_status()
    print(f"   Active agents: {status['active_agents']}")
    print(f"   Queued tasks: {status['queued_tasks']}")
    print(f"   Completed tasks: {status['completed_tasks']}")
    print(f"   Message queue size: {orchestrator.messenger.message_queue.qsize()}")
    print(f"   Total findings tracked: {len(orchestrator.result_aggregator.findings)}")
    print()
    
    # Summary
    print("=" * 70)
    print("✓ Enhanced Multi-Agent Orchestrator Demo Complete")
    print()
    print("New Capabilities Demonstrated:")
    print("  ✓ Resource management and limits")
    print("  ✓ Dynamic agent spawning by attack surface")
    print("  ✓ Enhanced workload balancing")
    print("  ✓ Inter-agent communication (pub/sub)")
    print("  ✓ Campaign workflow engine")
    print("  ✓ Result aggregation & deduplication")
    print("  ✓ Failure recovery & retry logic")
    print("  ✓ Custom agent invocation")
    print("=" * 70)
    
    orchestrator.shutdown()

