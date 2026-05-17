#!/usr/bin/env python3
"""
GLASSEYE MEMORY SYSTEM
Persistent memory and intelligence storage using simple JSON + future vector DB

This system provides:
- Perfect recall of all past operations
- Target intelligence database
- Exploit library
- Learning from success/failure patterns
- Quick retrieval of relevant context
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

MEMORY_DIR = Path("/home/x/glasseye/memory")
MEMORY_DIR.mkdir(exist_ok=True)

# Memory storage files
SCAN_HISTORY = MEMORY_DIR / "scan_history.json"
TARGET_INTEL = MEMORY_DIR / "target_intelligence.json"
EXPLOIT_LIBRARY = MEMORY_DIR / "exploit_library.json"
LEARNING_LOG = MEMORY_DIR / "learning_log.json"
DECISIONS = MEMORY_DIR / "decisions.json"


@dataclass
class ScanRecord:
    """Record of a security scan"""
    target: str
    timestamp: str
    tools_used: List[str]
    findings: List[Dict]
    success: bool
    duration_minutes: int
    
@dataclass
class TargetProfile:
    """Intelligence profile for a target"""
    target: str
    first_seen: str
    last_scanned: str
    scan_count: int
    technologies: List[str]
    vulnerabilities: List[Dict]
    risk_score: float
    notes: str


class GlasseyeMemory:
    """
    Persistent memory system for GLASSEYE
    
    Future enhancements:
    - Vector database (Pinecone/Weaviate) for semantic search
    - Embeddings for similar target matching
    - Time-series analysis of vulnerability trends
    - Automatic CVE correlation
    """
    
    def __init__(self):
        self.scan_history: List[Dict] = self._load_json(SCAN_HISTORY, [])
        self.target_intel: Dict[str, Dict] = self._load_json(TARGET_INTEL, {})
        self.exploit_lib: Dict[str, Dict] = self._load_json(EXPLOIT_LIBRARY, {})
        self.learning_log: List[Dict] = self._load_json(LEARNING_LOG, [])
        self.decisions: List[Dict] = self._load_json(DECISIONS, [])
        
        print("💾 GLASSEYE Memory System loaded")
        print(f"  📊 Scans in history: {len(self.scan_history)}")
        print(f"  🎯 Targets tracked: {len(self.target_intel)}")
        print(f"  💣 Exploits stored: {len(self.exploit_lib)}")
        print(f"  🧠 Learning entries: {len(self.learning_log)}")
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Load JSON file or return default"""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, path: Path, data: Any):
        """Save data to JSON file"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_scan(self, scan_record: ScanRecord):
        """Store a scan record"""
        self.scan_history.append(asdict(scan_record))
        self._save_json(SCAN_HISTORY, self.scan_history)
        
        # Update target intelligence
        self._update_target_intel(scan_record)
        
        print(f"💾 Scan recorded: {scan_record.target}")
    
    def _update_target_intel(self, scan: ScanRecord):
        """Update target intelligence profile"""
        target = scan.target
        
        if target not in self.target_intel:
            self.target_intel[target] = {
                "target": target,
                "first_seen": scan.timestamp,
                "last_scanned": scan.timestamp,
                "scan_count": 1,
                "technologies": [],
                "vulnerabilities": scan.findings,
                "risk_score": 0.0,
                "notes": ""
            }
        else:
            profile = self.target_intel[target]
            profile["last_scanned"] = scan.timestamp
            profile["scan_count"] += 1
            profile["vulnerabilities"].extend(scan.findings)
        
        self._save_json(TARGET_INTEL, self.target_intel)
    
    def get_target_history(self, target: str) -> Optional[Dict]:
        """Retrieve all intelligence on a target"""
        return self.target_intel.get(target)
    
    def search_similar_targets(self, target: str) -> List[Dict]:
        """Find targets with similar characteristics (simple version)"""
        # TODO: Use vector embeddings for semantic similarity
        # For now, simple domain matching
        results = []
        for t, data in self.target_intel.items():
            if target in t or t in target:
                results.append(data)
        return results
    
    def store_decision(self, decision: Dict):
        """Store an AI decision for learning"""
        self.decisions.append(decision)
        self._save_json(DECISIONS, self.decisions)
        print(f"💾 Decision stored: {decision.get('action', 'unknown')}")
    
    def store_learning(self, lesson: Dict):
        """Store a learning lesson"""
        self.learning_log.append({
            **lesson,
            "timestamp": datetime.now().isoformat()
        })
        self._save_json(LEARNING_LOG, self.learning_log)
        print(f"🧠 Learning stored: {lesson.get('topic', 'unknown')}")
    
    def store_exploit(self, vuln_type: str, exploit_data: Dict):
        """Store an exploit in the library"""
        if vuln_type not in self.exploit_lib:
            self.exploit_lib[vuln_type] = []
        
        self.exploit_lib[vuln_type].append({
            **exploit_data,
            "added": datetime.now().isoformat()
        })
        self._save_json(EXPLOIT_LIBRARY, self.exploit_lib)
        print(f"💣 Exploit stored: {vuln_type}")
    
    def get_exploit(self, vuln_type: str) -> List[Dict]:
        """Retrieve exploits for a vulnerability type"""
        return self.exploit_lib.get(vuln_type, [])
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            "total_scans": len(self.scan_history),
            "targets_tracked": len(self.target_intel),
            "exploits_stored": sum(len(v) for v in self.exploit_lib.values()),
            "learning_entries": len(self.learning_log),
            "decisions_made": len(self.decisions),
            "successful_scans": sum(1 for s in self.scan_history if s.get("success", False))
        }
    
    def get_recent_scans(self, limit: int = 10) -> List[Dict]:
        """Get most recent scans"""
        return sorted(
            self.scan_history,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )[:limit]
    
    def get_high_value_targets(self, min_vuln_count: int = 3) -> List[Dict]:
        """Get targets with multiple vulnerabilities"""
        return [
            intel for intel in self.target_intel.values()
            if len(intel.get("vulnerabilities", [])) >= min_vuln_count
        ]


def main():
    """Demo memory system"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║           💾 GLASSEYE MEMORY SYSTEM 💾                   ║
    ║              Perfect Recall Activated                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    memory = GlasseyeMemory()
    
    # Demo: Store a scan
    print("\n📝 Storing demo scan...")
    scan = ScanRecord(
        target="scanme.nmap.org",
        timestamp=datetime.now().isoformat(),
        tools_used=["nmap", "nikto"],
        findings=[
            {"type": "open_port", "port": 22, "service": "ssh"},
            {"type": "open_port", "port": 80, "service": "http"}
        ],
        success=True,
        duration_minutes=5
    )
    memory.record_scan(scan)
    
    # Demo: Store a decision
    print("\n🧠 Storing demo decision...")
    memory.store_decision({
        "target": "scanme.nmap.org",
        "action": "reconnaissance",
        "reasoning": "Standard scan approach for unknown target",
        "confidence": 0.85
    })
    
    # Demo: Store learning
    print("\n📚 Storing demo learning...")
    memory.store_learning({
        "topic": "nmap_efficiency",
        "lesson": "Using -sV -sC flags provides good service detection balance",
        "context": "Scanning public targets",
        "confidence": 0.9
    })
    
    # Show stats
    print("\n📊 Memory Statistics:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Show recent activity
    print("\n🕒 Recent Scans:")
    for scan in memory.get_recent_scans(5):
        print(f"  - {scan['target']} ({scan['timestamp'][:10]})")
    
    print("\n✅ Memory system operational!")


if __name__ == "__main__":
    main()
