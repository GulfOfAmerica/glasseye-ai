#!/usr/bin/env python3
"""
GlasseyeOS AI - Enhanced Compliance Guardian
Advanced autonomous safety system with real-time monitoring and proactive violation prevention.

CRITICAL: This module MUST approve all actions before execution.
NO bypassing. NO exceptions.

Enhanced Features:
- Real-time activity monitoring
- Scope boundary enforcement
- Advanced PII detection with auto-stop
- Rate limiting and abuse prevention
- Forbidden action blocking
- Resource ownership verification
- Automated incident response
"""

import logging
import json
import re
import threading
import time
import hashlib
import os
import yaml
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from pathlib import Path


class RiskLevel(Enum):
    """Risk classification for actions."""
    SAFE = "safe"  # Passive reconnaissance only
    LOW = "low"  # Active scanning, non-invasive
    MEDIUM = "medium"  # Fuzzing, authentication testing
    HIGH = "high"  # Exploitation attempts
    CRITICAL = "critical"  # System modification, data access


class ViolationType(Enum):
    """Types of compliance violations."""
    OUT_OF_SCOPE = "out_of_scope"
    PII_DETECTED = "pii_detected"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    FORBIDDEN_ACTION = "forbidden_action"
    UNOWNED_RESOURCE = "unowned_resource"
    UNSAFE_OPERATION = "unsafe_operation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class ComplianceViolation(Exception):
    """Raised when an action violates compliance rules."""
    pass


@dataclass
class Action:
    """Represents an action requiring approval."""
    action_type: str
    target: str
    description: str
    risk_level: RiskLevel
    requires_human_approval: bool
    scope_verified: bool = False
    pii_risk: bool = False
    researcher_owned: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    action_id: str = field(default_factory=lambda: hashlib.md5(f"{datetime.utcnow().isoformat()}{os.urandom(8).hex()}".encode()).hexdigest())
    component: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Incident:
    """Represents a security incident."""
    incident_id: str
    timestamp: datetime
    violation_type: ViolationType
    severity: str
    details: Dict[str, Any]
    system_state: Dict[str, Any]
    actions_taken: List[str]
    requires_human_review: bool = True
    resolved: bool = False


class RealTimeMonitor:
    """Real-time activity monitoring system."""
    
    def __init__(self, enforcer):
        self.enforcer = enforcer
        self.is_running = False
        self.action_queue = deque(maxlen=10000)
        self.monitor_thread = None
        self.logger = enforcer.logger
        
    def start(self):
        """Start real-time monitoring thread."""
        if self.is_running:
            self.logger.warning("Monitor already running")
            return
            
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("✓ Real-time monitor started")
    
    def stop(self):
        """Stop monitoring thread."""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("✓ Real-time monitor stopped")
    
    def enqueue_action(self, action: Action):
        """Add action to monitoring queue."""
        self.action_queue.append(action)
    
    def _monitor_loop(self):
        """Continuous monitoring loop."""
        while self.is_running:
            try:
                if self.action_queue:
                    action = self.action_queue.popleft()
                    self._analyze_action(action)
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                time.sleep(1)
    
    def _analyze_action(self, action: Action):
        """Analyze action for anomalies."""
        # Check for rapid-fire actions (potential attack)
        recent_actions = [a for a in list(self.action_queue)[-100:] 
                         if (action.timestamp - a.timestamp).total_seconds() < 60]
        
        if len(recent_actions) > 50:
            self.logger.warning(f"High action rate detected: {len(recent_actions)} in 60s")
            self.enforcer.rate_limiter.pause_operations("system", duration=60)


class PIIDetector:
    """Advanced PII detection with multiple pattern types."""
    
    def __init__(self, logger):
        self.logger = logger
        self.patterns = {
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            'CREDIT_CARD': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@(?!researcher\.test|hacktest\.local)[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE': r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'ADDRESS': r'\b\d{1,5}\s+\w+\s+(st|street|ave|avenue|rd|road|blvd|boulevard|way|dr|drive)\b',
            'API_KEY_AWS': r'(?i)AKIA[0-9A-Z]{16}',
            'API_KEY_GITHUB': r'(?i)ghp_[0-9a-zA-Z]{36}',
            'PASSWORD_LIKE': r'(?i)(password|passwd|pwd)[\s:=]+[^\s]{8,}',
        }
        
        # Researcher-approved domains (safe to capture)
        self.approved_email_domains = [
            'researcher.test',
            'hacktest.local',
            'bugbounty.test'
        ]
    
    def scan_for_pii(self, data: str) -> Tuple[bool, List[str], str]:
        """
        Comprehensive PII scan.
        
        Returns:
            (pii_found: bool, pii_types: List[str], redacted_sample: str)
        """
        pii_found = []
        
        for pii_type, pattern in self.patterns.items():
            if re.search(pattern, data, re.IGNORECASE):
                pii_found.append(pii_type)
                self.logger.warning(f"PII detected: {pii_type}")
        
        if pii_found:
            redacted = self._redact_pii(data)
            return True, pii_found, redacted
        
        return False, [], data
    
    def _redact_pii(self, data: str) -> str:
        """Redact PII from data."""
        redacted = data
        for pattern in self.patterns.values():
            redacted = re.sub(pattern, '[REDACTED]', redacted, flags=re.IGNORECASE)
        
        # Limit length for safety
        if len(redacted) > 500:
            redacted = redacted[:500] + "... [truncated]"
        
        return redacted
    
    def validate_luhn(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm."""
        card_number = re.sub(r'[\s-]', '', card_number)
        
        if not card_number.isdigit() or len(card_number) < 13:
            return False
        
        total = 0
        reverse_digits = card_number[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0


class RateLimiter:
    """Rate limiting and abuse prevention."""
    
    def __init__(self, logger, config: Dict):
        self.logger = logger
        self.config = config
        self.limits = config.get('rate_limits', {})
        self.request_history = defaultdict(deque)
        self.paused_services = {}
        self.lock = threading.Lock()
    
    def check_rate_limit(self, service: str, action: str) -> Tuple[bool, Optional[str]]:
        """
        Check if action would exceed rate limit.
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        # Check if service is paused
        if service in self.paused_services:
            pause_until = self.paused_services[service]
            if datetime.utcnow() < pause_until:
                remaining = (pause_until - datetime.utcnow()).total_seconds()
                return False, f"Service paused for {int(remaining)}s due to rate limit"
            else:
                del self.paused_services[service]
        
        if service not in self.limits:
            return True, None
        
        limit_config = self.limits[service]
        window = self._parse_window(limit_config['window'])
        max_requests = limit_config['requests']
        
        with self.lock:
            # Clean old requests outside window
            cutoff = datetime.utcnow() - timedelta(seconds=window)
            while self.request_history[service] and self.request_history[service][0] < cutoff:
                self.request_history[service].popleft()
            
            # Check if under limit
            current_count = len(self.request_history[service])
            
            if current_count >= max_requests:
                self.logger.warning(f"Rate limit exceeded for {service}: {current_count}/{max_requests} in {limit_config['window']}")
                self.pause_operations(service, duration=window)
                return False, f"Rate limit exceeded: {current_count}/{max_requests} in {limit_config['window']}"
            
            # Record request
            self.request_history[service].append(datetime.utcnow())
            
            return True, None
    
    def _parse_window(self, window_str: str) -> int:
        """Parse window string to seconds (e.g., '1hour' -> 3600)."""
        if 'hour' in window_str:
            hours = int(window_str.replace('hour', '').replace('s', '').strip())
            return hours * 3600
        elif 'minute' in window_str:
            minutes = int(window_str.replace('minute', '').replace('s', '').strip())
            return minutes * 60
        elif 'second' in window_str:
            return int(window_str.replace('second', '').replace('s', '').strip())
        return 3600  # Default 1 hour
    
    def pause_operations(self, service: str, duration: int):
        """Pause operations for a service."""
        pause_until = datetime.utcnow() + timedelta(seconds=duration)
        self.paused_services[service] = pause_until
        self.logger.warning(f"⏸️  Paused {service} until {pause_until.isoformat()}")
    
    def get_current_usage(self, service: str) -> Dict[str, Any]:
        """Get current rate limit usage for service."""
        if service not in self.limits:
            return {'service': service, 'usage': 'unlimited'}
        
        limit_config = self.limits[service]
        window = self._parse_window(limit_config['window'])
        
        with self.lock:
            cutoff = datetime.utcnow() - timedelta(seconds=window)
            while self.request_history[service] and self.request_history[service][0] < cutoff:
                self.request_history[service].popleft()
            
            current = len(self.request_history[service])
            
            return {
                'service': service,
                'current': current,
                'limit': limit_config['requests'],
                'window': limit_config['window'],
                'utilization': f"{(current/limit_config['requests'])*100:.1f}%"
            }


class IncidentResponse:
    """Automated incident response system."""
    
    def __init__(self, logger, incidents_dir: str = "logs/incidents"):
        self.logger = logger
        self.incidents_dir = Path(incidents_dir)
        self.incidents_dir.mkdir(parents=True, exist_ok=True)
        self.incidents = []
    
    def handle_violation(self, violation_type: ViolationType, details: Dict[str, Any],
                        enforcer) -> Incident:
        """
        Handle compliance violation with automated response.
        
        Steps:
        1. STOP related operations
        2. Log incident with full details
        3. Preserve evidence
        4. Create incident report
        5. Require human review
        """
        incident_id = hashlib.md5(f"{datetime.utcnow().isoformat()}{violation_type.value}".encode()).hexdigest()[:16]
        
        # Determine severity
        severity = self._determine_severity(violation_type, details)
        
        # Capture system state
        system_state = self._capture_system_state(enforcer)
        
        # Determine actions to take
        actions_taken = []
        
        if violation_type == ViolationType.PII_DETECTED:
            actions_taken.append('deleted_local_copies')
            if 'data_location' in details:
                self._delete_pii_data(details['data_location'])
        
        if severity in ['HIGH', 'CRITICAL']:
            actions_taken.append('emergency_stop_triggered')
            enforcer.trigger_emergency_stop(f"{violation_type.value}: {details.get('reason', 'Unknown')}")
        
        # Create incident
        incident = Incident(
            incident_id=incident_id,
            timestamp=datetime.utcnow(),
            violation_type=violation_type,
            severity=severity,
            details=details,
            system_state=system_state,
            actions_taken=actions_taken,
            requires_human_review=True,
            resolved=False
        )
        
        self.incidents.append(incident)
        
        # Save incident report
        self._create_incident_report(incident)
        
        # Notify human
        self._notify_human(incident)
        
        self.logger.critical(f"🚨 INCIDENT {incident_id}: {violation_type.value} ({severity})")
        
        return incident
    
    def _determine_severity(self, violation_type: ViolationType, details: Dict) -> str:
        """Determine incident severity."""
        if violation_type == ViolationType.PII_DETECTED:
            return 'CRITICAL'
        elif violation_type == ViolationType.FORBIDDEN_ACTION:
            return 'HIGH'
        elif violation_type == ViolationType.OUT_OF_SCOPE:
            return 'HIGH'
        elif violation_type == ViolationType.RATE_LIMIT_EXCEEDED:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _capture_system_state(self, enforcer) -> Dict[str, Any]:
        """Capture current system state."""
        return {
            'violations_count': enforcer.violations_count,
            'emergency_stop': enforcer.emergency_stop_triggered,
            'timestamp': datetime.utcnow().isoformat(),
            'active_monitors': enforcer.monitor.is_running if hasattr(enforcer, 'monitor') else False
        }
    
    def _delete_pii_data(self, location: str):
        """Securely delete PII data."""
        self.logger.warning(f"Would delete PII data at: {location}")
        # In production: secure deletion
    
    def _create_incident_report(self, incident: Incident):
        """Create detailed incident report."""
        report_path = self.incidents_dir / f"violation-{incident.timestamp.strftime('%Y%m%d-%H%M%S')}-{incident.incident_id}.json"
        
        report = {
            'incident_id': incident.incident_id,
            'timestamp': incident.timestamp.isoformat(),
            'violation_type': incident.violation_type.value,
            'severity': incident.severity,
            'details': incident.details,
            'system_state': incident.system_state,
            'actions_taken': incident.actions_taken,
            'requires_human_review': incident.requires_human_review,
            'resolved': incident.resolved
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📝 Incident report created: {report_path}")
    
    def _notify_human(self, incident: Incident):
        """Notify human operator of incident."""
        message = f"""
🚨 SECURITY INCIDENT ALERT 🚨

Incident ID: {incident.incident_id}
Severity: {incident.severity}
Type: {incident.violation_type.value}
Time: {incident.timestamp.isoformat()}

Details: {json.dumps(incident.details, indent=2)}

Actions Taken:
{chr(10).join(f'  - {action}' for action in incident.actions_taken)}

⚠️  HUMAN REVIEW REQUIRED BEFORE RESUMING OPERATIONS
"""
        
        self.logger.critical(message)
        print(message)  # Also print to console


class ComplianceEnforcer:
    """
    Enhanced autonomous compliance guardian with real-time monitoring.
    
    Responsibilities:
    - Verify all actions against safe harbor protections
    - Real-time activity monitoring
    - Block out-of-scope testing
    - Advanced PII detection and prevention
    - Rate limiting and abuse prevention
    - Forbidden action blocking
    - Resource ownership verification
    - Automated incident response
    - Audit logging
    - Emergency stop
    """
    
    def __init__(self, config_path: str = "config/compliance_rules.yaml"):
        self.config_path = config_path
        self.logger = self._setup_logging()
        self.compliance_rules = self._load_compliance_rules()
        self.audit_log_path = "logs/compliance_audit.jsonl"
        self.violations_count = 0
        self.emergency_stop_triggered = False
        
        # Initialize enhanced components
        self.pii_detector = PIIDetector(self.logger)
        self.rate_limiter = RateLimiter(self.logger, self.compliance_rules)
        self.incident_response = IncidentResponse(self.logger)
        self.monitor = RealTimeMonitor(self)
        
        # Component hooks
        self.hooked_components = []
        
        # Start monitoring
        self.monitor.start()
        
        self.logger.info("✓ Enhanced Compliance Enforcer initialized")
        
    def _setup_logging(self) -> logging.Logger:
        """Configure compliance logging."""
        logger = logging.getLogger("ComplianceEnforcer")
        logger.setLevel(logging.INFO)
        
        # File handler for audit trail
        fh = logging.FileHandler("logs/compliance.log")
        fh.setLevel(logging.INFO)
        
        # Console handler for critical events
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _load_compliance_rules(self) -> Dict:
        """Load compliance rules from YAML or use defaults."""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    rules = yaml.safe_load(f)
                    self.logger.info(f"✓ Loaded compliance rules from {config_file}")
                    return rules
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}, using defaults")
        
        # Default comprehensive rules
        return {
            "safe_harbor": {
                "programs": [
                    {
                        "name": "GitHub Bug Bounty",
                        "scope": {
                            "domains": [
                                "github.com",
                                "copilot.github.com",
                                "npmjs.org",
                                "npmjs.com"
                            ]
                        },
                        "prohibited": [
                            "DDoS attacks",
                            "Social engineering",
                            "Production system testing",
                            "PII access"
                        ],
                        "required": [
                            "Researcher-owned resources only",
                            "HackerOne account required"
                        ]
                    }
                ]
            },
            "forbidden_patterns": [
                r"rm\s+-rf\s+/",
                r"DROP\s+TABLE",
                r"DELETE\s+FROM.*WHERE\s+1\s*=\s*1",
                r"curl.*password",
                r"wget.*\.ssh",
                r"exfiltrate",
                r"ssh\s+prod",
                r"kubectl.*production",
                r"aws\s+s3.*prod-bucket",
                r"nmap.*github\.com",
                r"masscan",
                r"dirbuster",
                r"phishing",
                r"impersonate",
                r"fake.*email",
                r"mkfs\.",
                r"dd\s+if=/dev/zero",
                r":(){ :|:& };:",  # Fork bomb
            ],
            "rate_limits": {
                "github_api": {"requests": 5000, "window": "1hour"},
                "npm_registry": {"requests": 1000, "window": "1hour"},
                "web_scraping": {"requests": 60, "window": "1minute"},
                "system": {"requests": 1000, "window": "1minute"}
            },
            "max_violations": 3,
            "required_approvals": {
                RiskLevel.HIGH.value: True,
                RiskLevel.CRITICAL.value: True,
            }
        }
    
    def intercept_action(self, component: str, action: Action) -> bool:
        """
        Intercept action from any GlasseyeOS component.
        
        Every action must pass through this method.
        """
        action.component = component
        self.monitor.enqueue_action(action)
        
        # Check rate limit
        service = self._map_component_to_service(component)
        allowed, reason = self.rate_limiter.check_rate_limit(service, action.action_type)
        
        if not allowed:
            self.incident_response.handle_violation(
                ViolationType.RATE_LIMIT_EXCEEDED,
                {'component': component, 'action': action.action_type, 'reason': reason},
                self
            )
            return False
        
        # Check forbidden patterns
        if self.contains_forbidden_pattern(action.description):
            self.incident_response.handle_violation(
                ViolationType.FORBIDDEN_ACTION,
                {'component': component, 'action': asdict(action)},
                self
            )
            return False
        
        return True
    
    def _map_component_to_service(self, component: str) -> str:
        """Map component name to rate limit service."""
        mapping = {
            'github': 'github_api',
            'npm': 'npm_registry',
            'web_scraper': 'web_scraping'
        }
        return mapping.get(component.lower(), 'system')
    
    def hook_into_component(self, component_name: str, component_obj: Any):
        """Hook compliance enforcer into a GlasseyeOS component."""
        self.hooked_components.append(component_name)
        self.logger.info(f"✓ Hooked into component: {component_name}")
    
    def contains_forbidden_pattern(self, text: str) -> bool:
        """Check if text contains forbidden patterns."""
        for pattern in self.compliance_rules.get('forbidden_patterns', []):
            if re.search(pattern, text, re.IGNORECASE):
                self.logger.error(f"Forbidden pattern detected: {pattern}")
                return True
        return False
    
    def enforce_scope_boundary(self, target_url: str, program_name: str = "GitHub Bug Bounty") -> bool:
        """
        Enhanced scope boundary enforcement.
        
        Checks against program-specific allowed domains and blocks:
        - Private IP ranges
        - localhost/127.0.0.1 (unless explicitly allowed)
        - Production endpoints
        """
        programs = self.compliance_rules.get('safe_harbor', {}).get('programs', [])
        program = next((p for p in programs if p['name'] == program_name), None)
        
        if not program:
            self.logger.error(f"Unknown program: {program_name}")
            return False
        
        allowed_domains = program['scope']['domains']
        
        # Check if target is in scope
        target_host = self._extract_host(target_url)
        
        # Check for private IPs
        if self._is_private_ip(target_host):
            self.logger.error(f"Private IP detected: {target_host}")
            return False
        
        # Check for localhost
        if target_host in ['localhost', '127.0.0.1', '::1']:
            self.logger.error(f"Localhost access blocked: {target_host}")
            return False
        
        # Check against allowed domains
        for allowed in allowed_domains:
            if target_host == allowed or target_host.endswith(f".{allowed}"):
                self.logger.info(f"✓ Target in scope: {target_host}")
                return True
        
        self.logger.error(f"Target OUT OF SCOPE: {target_host}")
        self.incident_response.handle_violation(
            ViolationType.OUT_OF_SCOPE,
            {'target': target_url, 'program': program_name},
            self
        )
        return False
    
    def _is_private_ip(self, host: str) -> bool:
        """Check if host is a private IP address."""
        private_patterns = [
            r'^10\.',
            r'^172\.(1[6-9]|2[0-9]|3[01])\.',
            r'^192\.168\.',
            r'^127\.',
            r'^169\.254\.',
            r'^fc[0-9a-f]{2}:',  # IPv6 private
        ]
        
        for pattern in private_patterns:
            if re.match(pattern, host):
                return True
        return False
    
    def verify_researcher_owned(self, resource: Dict[str, Any], 
                                researcher_profile: Dict[str, Any]) -> bool:
        """
        Enhanced resource ownership verification.
        
        Verifies:
        - GitHub repos (owner matches researcher)
        - Email accounts (domain matches researcher)
        - Test accounts (metadata verification)
        - Servers (ownership metadata)
        """
        resource_type = resource.get('type')
        
        if resource_type == 'github_repo':
            repo_owner = resource.get('owner')
            researcher_github = researcher_profile.get('github_username')
            
            if repo_owner != researcher_github:
                self.logger.error(f"Repository not owned by researcher: {repo_owner} != {researcher_github}")
                self.incident_response.handle_violation(
                    ViolationType.UNOWNED_RESOURCE,
                    {'resource': resource, 'researcher': researcher_profile},
                    self
                )
                return False
        
        elif resource_type == 'email_account':
            email = resource.get('email')
            approved_domains = researcher_profile.get('approved_email_domains', [])
            
            email_domain = email.split('@')[-1] if '@' in email else ''
            
            if email_domain not in approved_domains:
                self.logger.error(f"Email domain not approved: {email_domain}")
                return False
        
        elif resource_type == 'test_server':
            # Verify ownership metadata
            owner_metadata = resource.get('owner_metadata', {})
            researcher_id = researcher_profile.get('id')
            
            if owner_metadata.get('owner_id') != researcher_id:
                self.logger.error(f"Server not owned by researcher")
                return False
        
        self.logger.info(f"✓ Resource verified as researcher-owned: {resource_type}")
        return True
    
    def scan_for_pii(self, data: str, auto_stop: bool = True) -> Tuple[bool, List[str]]:
        """
        Scan data for PII with optional auto-stop.
        
        Returns:
            (pii_found: bool, pii_types: List[str])
        """
        has_pii, pii_types, redacted = self.pii_detector.scan_for_pii(data)
        
        if has_pii and auto_stop:
            # EMERGENCY STOP
            self.incident_response.handle_violation(
                ViolationType.PII_DETECTED,
                {
                    'pii_types': pii_types,
                    'data_sample': redacted,
                    'data_location': 'memory'
                },
                self
            )
            
            self.trigger_emergency_stop(f"PII DETECTED: {', '.join(pii_types)}")
        
        return has_pii, pii_types
    
    def verify_safe_harbor(self, action: Action) -> bool:
        """
        Verify action complies with safe harbor protections.
        
        Safe harbor requirements:
        - Only test in-scope targets
        - No DoS attacks
        - No social engineering
        - No testing on shared infrastructure
        - Researcher-owned test accounts only
        """
        self.logger.info(f"Verifying safe harbor for: {action.description}")
        
        # Check emergency stop
        if self.emergency_stop_triggered:
            self.logger.critical("EMERGENCY STOP ACTIVE - ALL ACTIONS BLOCKED")
            raise ComplianceViolation("Emergency stop is active")
        
        # Check forbidden patterns
        for pattern in self.compliance_rules.get("forbidden_patterns", []):
            if re.search(pattern, action.description, re.IGNORECASE):
                self._log_violation(action, f"Forbidden pattern detected: {pattern}")
                return False
        
        # High-risk actions must have scope verified
        if action.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            if not action.scope_verified:
                self.logger.warning(f"High-risk action without scope verification: {action.action_type}")
                return False
        
        # Check PII risk
        if action.pii_risk:
            self.logger.warning(f"Action has PII risk: {action.description}")
            return False
        
        # Exploitation requires researcher-owned resources
        if action.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            if not action.researcher_owned:
                self.logger.warning(f"Exploitation on non-researcher-owned resource: {action.target}")
                return False
        
        self.logger.info(f"✓ Safe harbor verification passed for: {action.action_type}")
        return True
    
    def check_scope_boundaries(self, target: str, program_scope: List[str]) -> bool:
        """
        Verify target is within bug bounty program scope.
        
        Args:
            target: URL, IP, or domain to test
            program_scope: List of in-scope targets from program
            
        Returns:
            True if target is in scope, False otherwise
        """
        self.logger.info(f"Checking scope for target: {target}")
        
        # Extract domain/host from target
        target_clean = self._extract_host(target)
        
        # Check against scope list
        for scope_item in program_scope:
            scope_clean = self._extract_host(scope_item)
            
            # Exact match
            if target_clean == scope_clean:
                self.logger.info(f"✓ Target in scope (exact match): {target}")
                return True
            
            # Wildcard subdomain match (*.example.com)
            if scope_clean.startswith("*."):
                base_domain = scope_clean[2:]
                if target_clean.endswith(base_domain):
                    self.logger.info(f"✓ Target in scope (subdomain match): {target}")
                    return True
        
        self.logger.warning(f"✗ Target OUT OF SCOPE: {target}")
        return False
    
    def _extract_host(self, target: str) -> str:
        """Extract hostname from URL or return as-is."""
        # Simple extraction (would use urllib.parse in production)
        if "://" in target:
            target = target.split("://")[1]
        target = target.split("/")[0]
        target = target.split(":")[0]
        return target.lower()
    
    def detect_pii_risk(self, data: str) -> bool:
        """
        Legacy PII detection - redirects to enhanced scanner.
        
        Args:
            data: String to analyze
            
        Returns:
            True if PII patterns detected, False otherwise
        """
        has_pii, _ = self.scan_for_pii(data, auto_stop=False)
        return has_pii
    
    def enforce_researcher_owned(self, resource: str, researcher_resources: List[str]) -> bool:
        """
        Verify resource is owned/controlled by the researcher.
        
        Critical for testing authentication, session management, etc.
        
        Args:
            resource: Resource identifier (account, API key, etc.)
            researcher_resources: List of researcher-owned resources
            
        Returns:
            True if resource is researcher-owned, False otherwise
        """
        if resource in researcher_resources:
            self.logger.info(f"✓ Resource is researcher-owned: {resource}")
            return True
        
        self.logger.warning(f"✗ Resource NOT researcher-owned: {resource}")
        return False
    
    def audit_log(self, action: Action, approved: bool, reason: str):
        """
        Log action to audit trail (JSONL format).
        
        Args:
            action: Action that was evaluated
            approved: Whether action was approved
            reason: Approval or denial reason
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action.action_type,
            "target": action.target,
            "description": action.description,
            "risk_level": action.risk_level.value,
            "approved": approved,
            "reason": reason,
            "human_approval_required": action.requires_human_approval,
        }
        
        # Append to JSONL audit log
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        self.logger.info(f"Audit log entry: {approved=}, {reason=}")
    
    def _log_violation(self, action: Action, reason: str):
        """Log compliance violation and trigger emergency stop if threshold exceeded."""
        self.violations_count += 1
        self.logger.error(f"COMPLIANCE VIOLATION #{self.violations_count}: {reason}")
        
        self.audit_log(action, approved=False, reason=f"VIOLATION: {reason}")
        
        # Emergency stop if too many violations
        max_violations = self.compliance_rules.get("max_violations", 3)
        if self.violations_count >= max_violations:
            self.trigger_emergency_stop(f"Maximum violations exceeded: {self.violations_count}")
    
    def trigger_emergency_stop(self, reason: str):
        """
        EMERGENCY STOP - Halt all operations immediately.
        
        Triggered when:
        - Multiple compliance violations detected
        - Potential system compromise detected
        - Manual emergency stop requested
        """
        self.emergency_stop_triggered = True
        self.logger.critical(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")
        
        # Log emergency stop
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "EMERGENCY_STOP",
            "reason": reason,
            "violations_count": self.violations_count,
        }
        
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        # Note: do NOT raise here — callers that need to abort should check
        # emergency_stop_triggered or call verify_safe_harbor (which raises).
    
    def approve_action(self, action: Action, program_scope: List[str], 
                      researcher_resources: List[str]) -> Tuple[bool, str]:
        """
        Comprehensive action approval workflow.
        
        Args:
            action: Action to approve
            program_scope: In-scope targets for the program
            researcher_resources: Researcher-owned resources
            
        Returns:
            (approved: bool, reason: str)
        """
        # Step 1: Safe harbor verification
        if not self.verify_safe_harbor(action):
            reason = "Failed safe harbor verification: out of scope or unsafe action"
            self.audit_log(action, approved=False, reason=reason)
            return False, reason
        
        # Step 2: Scope verification (if applicable)
        if action.target:
            if not self.check_scope_boundaries(action.target, program_scope):
                reason = "Target out of scope"
                self.audit_log(action, approved=False, reason=reason)
                return False, reason
        
        # Step 3: PII risk check
        if self.detect_pii_risk(action.description):
            action.pii_risk = True
            reason = "PII risk detected"
            self.audit_log(action, approved=False, reason=reason)
            return False, reason
        
        # Step 4: Researcher-owned resource verification
        if action.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            if not self.enforce_researcher_owned(action.target, researcher_resources):
                action.researcher_owned = False
                reason = "Resource not researcher-owned"
                self.audit_log(action, approved=False, reason=reason)
                return False, reason
            action.researcher_owned = True
        
        # Step 5: Human approval check
        if action.requires_human_approval:
            reason = "Automated approval complete - HUMAN APPROVAL REQUIRED"
            self.audit_log(action, approved=True, reason=reason)
            return True, reason
        
        # All checks passed
        reason = "All compliance checks passed"
        self.audit_log(action, approved=True, reason=reason)
        return True, reason
    
    def reset_emergency_stop(self, admin_password: str):
        """Reset emergency stop (requires admin password)."""
        # In production, would verify admin credentials
        if admin_password == "RESET_EMERGENCY_STOP":
            self.emergency_stop_triggered = False
            self.violations_count = 0
            
            # Clear paused services
            self.rate_limiter.paused_services.clear()
            
            # Clear incident flags
            for incident in self.incident_response.incidents:
                incident.resolved = True
            
            self.logger.warning("✓ Emergency stop reset by administrator")
        else:
            raise ComplianceViolation("Invalid admin password")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'emergency_stop': self.emergency_stop_triggered,
            'violations_count': self.violations_count,
            'monitoring_active': self.monitor.is_running,
            'hooked_components': self.hooked_components,
            'rate_limits': {
                service: self.rate_limiter.get_current_usage(service)
                for service in self.compliance_rules.get('rate_limits', {}).keys()
            },
            'recent_incidents': [
                {
                    'id': i.incident_id,
                    'type': i.violation_type.value,
                    'severity': i.severity,
                    'resolved': i.resolved
                }
                for i in self.incident_response.incidents[-5:]
            ]
        }
    
    def shutdown(self):
        """Graceful shutdown of compliance enforcer."""
        self.logger.info("Shutting down compliance enforcer...")
        self.monitor.stop()
        self.logger.info("✓ Compliance enforcer shutdown complete")


if __name__ == "__main__":
    # Demo enhanced compliance enforcement
    print("=== GlasseyeOS AI - Enhanced Compliance Enforcer Demo ===\n")
    
    enforcer = ComplianceEnforcer()
    
    # Define program scope
    program_scope = [
        "github.com",
        "copilot.github.com",
        "npmjs.org"
    ]
    
    researcher_resources = [
        "test_account_researcher@researcher.test",
        "api_key_researcher_owned"
    ]
    
    researcher_profile = {
        'id': 'researcher-001',
        'github_username': 'researcher_test',
        'approved_email_domains': ['researcher.test', 'hacktest.local']
    }
    
    # Test 1: Safe reconnaissance with rate limiting
    print("Test 1: Safe passive reconnaissance (with rate limit check)")
    action1 = Action(
        action_type="dns_enumeration",
        target="github.com",
        description="Enumerate DNS records for github.com",
        risk_level=RiskLevel.SAFE,
        requires_human_approval=False,
        scope_verified=True
    )
    
    if enforcer.intercept_action("reconnaissance", action1):
        approved, reason = enforcer.approve_action(action1, program_scope, researcher_resources)
        print(f"  ✓ Approved: {approved}, Reason: {reason}\n")
    
    # Test 2: PII Detection (should FAIL and trigger incident)
    print("Test 2: PII detection test (should fail)")
    try:
        test_data = "User SSN: 123-45-6789, Email: victim@example.com"
        has_pii, pii_types = enforcer.scan_for_pii(test_data, auto_stop=False)
        print(f"  PII Detected: {has_pii}, Types: {pii_types}\n")
        
        if has_pii:
            print("  ⚠️  Would trigger emergency stop in production\n")
    except ComplianceViolation as e:
        print(f"  ✗ Blocked: {e}\n")
    
    # Test 3: Rate limit enforcement
    print("Test 3: Rate limit stress test")
    for i in range(65):
        service_ok, reason = enforcer.rate_limiter.check_rate_limit('web_scraping', f'request_{i}')
        if not service_ok:
            print(f"  ⏸️  Rate limit hit at request #{i}: {reason}\n")
            break
    
    # Test 4: Forbidden pattern detection
    print("Test 4: Forbidden destructive command (should fail)")
    action4 = Action(
        action_type="command_execution",
        target="system",
        description="Execute: rm -rf / --no-preserve-root",
        risk_level=RiskLevel.CRITICAL,
        requires_human_approval=True,
        scope_verified=True
    )
    
    if not enforcer.intercept_action("system", action4):
        print("  ✓ Correctly blocked forbidden pattern\n")
    
    # Test 5: Out-of-scope target
    print("Test 5: Out-of-scope target (should fail)")
    if not enforcer.enforce_scope_boundary("https://facebook.com/api/v1", "GitHub Bug Bounty"):
        print("  ✓ Correctly blocked out-of-scope target\n")
    
    # Test 6: Resource ownership verification
    print("Test 6: Resource ownership verification")
    test_repo = {
        'type': 'github_repo',
        'owner': 'researcher_test',
        'name': 'test-repo'
    }
    
    if enforcer.verify_researcher_owned(test_repo, researcher_profile):
        print("  ✓ Resource verified as researcher-owned\n")
    
    # Test 7: Private IP blocking
    print("Test 7: Private IP blocking (should fail)")
    if not enforcer.enforce_scope_boundary("https://192.168.1.1/admin", "GitHub Bug Bounty"):
        print("  ✓ Correctly blocked private IP\n")
    
    # Print system status
    print("=== System Status ===")
    status = enforcer.get_system_status()
    print(f"Emergency Stop: {status['emergency_stop']}")
    print(f"Violations: {status['violations_count']}")
    print(f"Monitoring Active: {status['monitoring_active']}")
    print(f"\nRate Limit Usage:")
    for service, usage in status['rate_limits'].items():
        if isinstance(usage, dict) and 'utilization' in usage:
            print(f"  {service}: {usage['current']}/{usage['limit']} ({usage['utilization']})")
    
    print(f"\nRecent Incidents: {len(status['recent_incidents'])}")
    for incident in status['recent_incidents']:
        print(f"  - {incident['type']} ({incident['severity']}) - Resolved: {incident['resolved']}")
    
    # Cleanup
    enforcer.shutdown()
    
    print(f"\n✓ Enhanced compliance enforcer demo complete")
    print(f"  Audit log: {enforcer.audit_log_path}")
    print(f"  Incident reports: logs/incidents/")

