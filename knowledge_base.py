#!/usr/bin/env python3
"""
GlasseyeOS AI - Knowledge Base Manager
SQLite database for CVE intelligence, disclosed bounties, generated tools, and campaign state.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict


@dataclass
class CVE:
    """CVE intelligence record."""
    cve_id: str
    cvss_score: float
    attack_vector: str
    vulnerability_type: str
    affected_products: str
    learned_pattern: str
    discovered_date: str = None
    
    def __post_init__(self):
        if self.discovered_date is None:
            self.discovered_date = datetime.now(timezone.utc).isoformat()


@dataclass
class DisclosedBounty:
    """Disclosed bug bounty finding (public data)."""
    report_id: str
    program: str
    title: str
    severity: str
    bounty_amount: int
    attack_pattern: str
    lessons_learned: str
    disclosed_date: str = None
    
    def __post_init__(self):
        if self.disclosed_date is None:
            self.disclosed_date = datetime.now(timezone.utc).isoformat()


@dataclass
class GeneratedTool:
    """Auto-generated tool or skill."""
    tool_id: str
    tool_type: str
    target_vulnerability: str
    code: str
    tests: str
    generated_date: str = None
    
    def __post_init__(self):
        if self.generated_date is None:
            self.generated_date = datetime.now(timezone.utc).isoformat()


@dataclass
class Campaign:
    """Active bug bounty campaign."""
    campaign_id: str
    target: str
    status: str
    hypotheses_count: int
    findings_count: int
    estimated_bounty: int
    started_date: str = None
    
    def __post_init__(self):
        if self.started_date is None:
            self.started_date = datetime.now(timezone.utc).isoformat()


class KnowledgeBase:
    """
    SQLite-based intelligence database for GlasseyeOS AI.
    
    Stores:
    - CVE intelligence and patterns
    - Disclosed bug bounty findings
    - Auto-generated tools and skills
    - Active campaign state
    - Learned attack patterns
    """
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # CVE intelligence table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cves (
                cve_id TEXT PRIMARY KEY,
                cvss_score REAL,
                attack_vector TEXT,
                vulnerability_type TEXT,
                affected_products TEXT,
                learned_pattern TEXT,
                discovered_date TEXT
            )
        """)
        
        # Disclosed bug bounty findings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disclosed_bounties (
                report_id TEXT PRIMARY KEY,
                program TEXT,
                title TEXT,
                severity TEXT,
                bounty_amount INTEGER,
                attack_pattern TEXT,
                lessons_learned TEXT,
                disclosed_date TEXT
            )
        """)
        
        # Generated tools table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_tools (
                tool_id TEXT PRIMARY KEY,
                tool_type TEXT,
                target_vulnerability TEXT,
                code TEXT,
                tests TEXT,
                generated_date TEXT
            )
        """)
        
        # Active campaigns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_campaigns (
                campaign_id TEXT PRIMARY KEY,
                target TEXT,
                status TEXT,
                hypotheses_count INTEGER,
                findings_count INTEGER,
                estimated_bounty INTEGER,
                started_date TEXT
            )
        """)
        
        # Vulnerability patterns table (learned from CVEs and bounties)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerability_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_name TEXT,
                pattern_description TEXT,
                detection_method TEXT,
                exploitation_template TEXT,
                success_rate REAL,
                avg_bounty INTEGER,
                learned_from TEXT,
                created_date TEXT
            )
        """)
        
        # Attack surface analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attack_surfaces (
                surface_id TEXT PRIMARY KEY,
                target TEXT,
                endpoint TEXT,
                method TEXT,
                authentication_required INTEGER,
                parameters TEXT,
                potential_vulnerabilities TEXT,
                analyzed_date TEXT
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cves_vuln_type 
            ON cves(vulnerability_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bounties_program 
            ON disclosed_bounties(program)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_campaigns_status 
            ON active_campaigns(status)
        """)
        
        self.conn.commit()
    
    # === CVE Management ===
    
    def add_cve(self, cve: CVE):
        """Add CVE to knowledge base."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO cves 
            (cve_id, cvss_score, attack_vector, vulnerability_type, 
             affected_products, learned_pattern, discovered_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cve.cve_id, cve.cvss_score, cve.attack_vector,
            cve.vulnerability_type, cve.affected_products,
            cve.learned_pattern, cve.discovered_date
        ))
        self.conn.commit()
    
    def search_cves(self, vulnerability_type: Optional[str] = None,
                    min_cvss: float = 0.0) -> List[Dict]:
        """Search CVEs by type and severity."""
        cursor = self.conn.cursor()
        
        if vulnerability_type:
            cursor.execute("""
                SELECT * FROM cves 
                WHERE vulnerability_type LIKE ? AND cvss_score >= ?
                ORDER BY cvss_score DESC
            """, (f"%{vulnerability_type}%", min_cvss))
        else:
            cursor.execute("""
                SELECT * FROM cves 
                WHERE cvss_score >= ?
                ORDER BY cvss_score DESC
            """, (min_cvss,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # === Disclosed Bounty Management ===
    
    def add_disclosed_bounty(self, bounty: DisclosedBounty):
        """Add disclosed bounty finding."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO disclosed_bounties
            (report_id, program, title, severity, bounty_amount,
             attack_pattern, lessons_learned, disclosed_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bounty.report_id, bounty.program, bounty.title,
            bounty.severity, bounty.bounty_amount, bounty.attack_pattern,
            bounty.lessons_learned, bounty.disclosed_date
        ))
        self.conn.commit()
    
    def search_bounties(self, program: Optional[str] = None,
                       min_bounty: int = 0) -> List[Dict]:
        """Search disclosed bounties."""
        cursor = self.conn.cursor()
        
        if program:
            cursor.execute("""
                SELECT * FROM disclosed_bounties 
                WHERE program LIKE ? AND bounty_amount >= ?
                ORDER BY bounty_amount DESC
            """, (f"%{program}%", min_bounty))
        else:
            cursor.execute("""
                SELECT * FROM disclosed_bounties 
                WHERE bounty_amount >= ?
                ORDER BY bounty_amount DESC
            """, (min_bounty,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # === Tool Management ===
    
    def add_generated_tool(self, tool: GeneratedTool):
        """Add auto-generated tool."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO generated_tools
            (tool_id, tool_type, target_vulnerability, code, tests, generated_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tool.tool_id, tool.tool_type, tool.target_vulnerability,
            tool.code, tool.tests, tool.generated_date
        ))
        self.conn.commit()
    
    def get_tool(self, tool_id: str) -> Optional[Dict]:
        """Retrieve generated tool by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM generated_tools WHERE tool_id = ?", (tool_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_tools(self, tool_type: Optional[str] = None,
                    vulnerability: Optional[str] = None) -> List[Dict]:
        """Search generated tools."""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM generated_tools WHERE 1=1"
        params = []
        
        if tool_type:
            query += " AND tool_type = ?"
            params.append(tool_type)
        
        if vulnerability:
            query += " AND target_vulnerability LIKE ?"
            params.append(f"%{vulnerability}%")
        
        query += " ORDER BY generated_date DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # === Campaign Management ===
    
    def add_campaign(self, campaign: Campaign):
        """Add or update campaign."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO active_campaigns
            (campaign_id, target, status, hypotheses_count, 
             findings_count, estimated_bounty, started_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign.campaign_id, campaign.target, campaign.status,
            campaign.hypotheses_count, campaign.findings_count,
            campaign.estimated_bounty, campaign.started_date
        ))
        self.conn.commit()
    
    def update_campaign_status(self, campaign_id: str, status: str,
                              findings_count: Optional[int] = None):
        """Update campaign status and findings."""
        cursor = self.conn.cursor()
        
        if findings_count is not None:
            cursor.execute("""
                UPDATE active_campaigns 
                SET status = ?, findings_count = ?
                WHERE campaign_id = ?
            """, (status, findings_count, campaign_id))
        else:
            cursor.execute("""
                UPDATE active_campaigns 
                SET status = ?
                WHERE campaign_id = ?
            """, (status, campaign_id))
        
        self.conn.commit()
    
    def get_active_campaigns(self) -> List[Dict]:
        """Get all active campaigns."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM active_campaigns 
            WHERE status IN ('active', 'reconnaissance', 'testing')
            ORDER BY estimated_bounty DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    # === Pattern Learning ===
    
    def add_vulnerability_pattern(self, pattern_name: str, description: str,
                                 detection_method: str, exploitation_template: str,
                                 learned_from: str, success_rate: float = 0.0,
                                 avg_bounty: int = 0) -> str:
        """Add learned vulnerability pattern."""
        import hashlib
        # Use hash to prevent ID collisions
        pattern_hash = hashlib.md5(f"{pattern_name}{learned_from}".encode()).hexdigest()[:8]
        pattern_id = f"pattern_{pattern_hash}"
        created_date = datetime.now(timezone.utc).isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO vulnerability_patterns
            (pattern_id, pattern_name, pattern_description, detection_method,
             exploitation_template, success_rate, avg_bounty, learned_from, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id, pattern_name, description, detection_method,
            exploitation_template, success_rate, avg_bounty, learned_from, created_date
        ))
        self.conn.commit()
        
        return pattern_id
    
    def search_patterns(self, vulnerability_type: Optional[str] = None) -> List[Dict]:
        """Search learned vulnerability patterns."""
        cursor = self.conn.cursor()
        
        if vulnerability_type:
            cursor.execute("""
                SELECT * FROM vulnerability_patterns 
                WHERE pattern_name LIKE ? OR pattern_description LIKE ?
                ORDER BY success_rate DESC, avg_bounty DESC
            """, (f"%{vulnerability_type}%", f"%{vulnerability_type}%"))
        else:
            cursor.execute("""
                SELECT * FROM vulnerability_patterns 
                ORDER BY success_rate DESC, avg_bounty DESC
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    # === Attack Surface Analysis ===
    
    def add_attack_surface(self, target: str, endpoint: str, method: str,
                          authentication_required: bool, parameters: Dict,
                          potential_vulnerabilities: List[str]) -> str:
        """Record discovered attack surface."""
        import hashlib
        # Use hash to prevent ID collisions
        surface_hash = hashlib.md5(f"{target}{endpoint}{method}".encode()).hexdigest()[:8]
        surface_id = f"surface_{surface_hash}"
        analyzed_date = datetime.now(timezone.utc).isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO attack_surfaces
            (surface_id, target, endpoint, method, authentication_required,
             parameters, potential_vulnerabilities, analyzed_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            surface_id, target, endpoint, method, int(authentication_required),
            json.dumps(parameters), json.dumps(potential_vulnerabilities),
            analyzed_date
        ))
        self.conn.commit()
        
        return surface_id
    
    def get_attack_surfaces(self, target: str) -> List[Dict]:
        """Get all attack surfaces for a target."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM attack_surfaces 
            WHERE target = ?
            ORDER BY analyzed_date DESC
        """, (target,))
        
        surfaces = []
        for row in cursor.fetchall():
            surface = dict(row)
            surface['parameters'] = json.loads(surface['parameters'])
            surface['potential_vulnerabilities'] = json.loads(surface['potential_vulnerabilities'])
            surfaces.append(surface)
        
        return surfaces
    
    # === Statistics ===
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as count FROM cves")
        stats['total_cves'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM disclosed_bounties")
        stats['total_bounties'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM generated_tools")
        stats['total_tools'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM active_campaigns")
        stats['total_campaigns'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM vulnerability_patterns")
        stats['total_patterns'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM attack_surfaces")
        stats['total_surfaces'] = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT SUM(estimated_bounty) as total FROM active_campaigns 
            WHERE status IN ('active', 'testing')
        """)
        result = cursor.fetchone()
        stats['total_estimated_bounty'] = result['total'] if result['total'] else 0
        
        return stats
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Demo knowledge base
    print("=== GlasseyeOS AI - Knowledge Base Demo ===\n")
    
    kb = KnowledgeBase()
    
    # Add sample CVE
    print("Adding sample CVE...")
    cve = CVE(
        cve_id="CVE-2024-EXAMPLE",
        cvss_score=9.8,
        attack_vector="Network",
        vulnerability_type="Authentication Bypass",
        affected_products="GitHub Copilot Coding Agent",
        learned_pattern="JWT token validation bypass via algorithm confusion"
    )
    kb.add_cve(cve)
    
    # Add sample disclosed bounty
    print("Adding sample disclosed bounty...")
    bounty = DisclosedBounty(
        report_id="H1-123456",
        program="GitHub Bug Bounty",
        title="IDOR in Copilot API allows access to other users' sessions",
        severity="High",
        bounty_amount=5000,
        attack_pattern="IDOR via predictable session IDs",
        lessons_learned="Always use cryptographically random session identifiers"
    )
    kb.add_disclosed_bounty(bounty)
    
    # Add vulnerability pattern
    print("Adding learned pattern...")
    pattern_id = kb.add_vulnerability_pattern(
        pattern_name="JWT Algorithm Confusion",
        description="JWT tokens accept 'none' algorithm or symmetric key for asymmetric verification",
        detection_method="Attempt to modify JWT algorithm field and verify acceptance",
        exploitation_template="Modify alg field to 'none' or use public key as HMAC secret",
        learned_from="CVE-2024-EXAMPLE",
        success_rate=0.65,
        avg_bounty=3500
    )
    
    # Add campaign
    print("Adding campaign...")
    campaign = Campaign(
        campaign_id="campaign_copilot_2024",
        target="GitHub Copilot",
        status="reconnaissance",
        hypotheses_count=5,
        findings_count=0,
        estimated_bounty=10000
    )
    kb.add_campaign(campaign)
    
    # Show statistics
    print("\nKnowledge Base Statistics:")
    stats = kb.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Search examples
    print("\nSearching for authentication bypass CVEs...")
    auth_cves = kb.search_cves(vulnerability_type="Authentication", min_cvss=7.0)
    print(f"  Found {len(auth_cves)} CVEs")
    
    print("\nSearching for high-bounty findings...")
    high_bounties = kb.search_bounties(min_bounty=3000)
    print(f"  Found {len(high_bounties)} high-value bounties")
    
    print("\n✓ Knowledge base demo complete")
    
    kb.close()
