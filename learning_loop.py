#!/usr/bin/env python3
"""
GLASSEYE AI OS - Learning Loop
Self-improvement system that learns from results
"""

import sys
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter

sys.path.append('/home/x/glasseye')
from memory_system import GlasseyeMemory


@dataclass
class LearningInsight:
    """A learned insight"""
    category: str
    insight: str
    confidence: float
    evidence_count: int
    impact: str  # 'high', 'medium', 'low'
    timestamp: str


class LearningLoop:
    """Self-improvement through analysis of past results"""
    
    def __init__(self):
        self.memory = GlasseyeMemory()
        print("🧠 Learning Loop initialized")
    
    def analyze_scan_patterns(self) -> List[LearningInsight]:
        """Analyze patterns in scan history"""
        insights = []
        
        if len(self.memory.scan_history) < 3:
            return insights
        
        # Analyze successful techniques
        tool_usage = Counter()
        success_rates = {}
        
        for scan in self.memory.scan_history:
            tools_used = scan.get('tools_used', [])
            success = scan.get('success', False)
            
            for tool in tools_used:
                tool_usage[tool] += 1
                if tool not in success_rates:
                    success_rates[tool] = {'successes': 0, 'total': 0}
                
                success_rates[tool]['total'] += 1
                if success:
                    success_rates[tool]['successes'] += 1
        
        # Generate insights from most used tools
        for tool, count in tool_usage.most_common(3):
            if count >= 2:
                success_rate = success_rates[tool]['successes'] / success_rates[tool]['total']
                
                insights.append(LearningInsight(
                    category='tool_effectiveness',
                    insight=f'{tool} is effective with {success_rate:.0%} success rate',
                    confidence=0.7 + (count / len(self.memory.scan_history)) * 0.3,
                    evidence_count=count,
                    impact='high' if success_rate > 0.7 else 'medium',
                    timestamp=datetime.now().isoformat()
                ))
        
        return insights
    
    def analyze_vulnerability_patterns(self) -> List[LearningInsight]:
        """Learn patterns in discovered vulnerabilities"""
        insights = []
        
        vuln_types = Counter()
        vuln_severity = Counter()
        
        for target in self.memory.target_profiles.values():
            vulns = target.get('vulnerabilities', [])
            for vuln in vulns:
                vuln_types[vuln.get('type', 'unknown')] += 1
                vuln_severity[vuln.get('severity', 'unknown')] += 1
        
        # Learn about common vulnerability types
        for vuln_type, count in vuln_types.most_common(3):
            if count >= 2:
                insights.append(LearningInsight(
                    category='vulnerability_patterns',
                    insight=f'{vuln_type} vulnerabilities found frequently ({count} occurrences)',
                    confidence=0.8,
                    evidence_count=count,
                    impact='high',
                    timestamp=datetime.now().isoformat()
                ))
        
        return insights
    
    def analyze_attack_vectors(self) -> List[LearningInsight]:
        """Learn successful attack vectors"""
        insights = []
        
        attack_vectors = Counter()
        
        for scan in self.memory.scan_history:
            vectors = scan.get('results', {}).get('attack_vectors', [])
            for vector in vectors:
                attack_vectors[vector] += 1
        
        for vector, count in attack_vectors.most_common(5):
            if count >= 2:
                insights.append(LearningInsight(
                    category='attack_vectors',
                    insight=f'{vector} is a common attack surface ({count} targets)',
                    confidence=0.75,
                    evidence_count=count,
                    impact='high' if count > 3 else 'medium',
                    timestamp=datetime.now().isoformat()
                ))
        
        return insights
    
    def analyze_timing_patterns(self) -> List[LearningInsight]:
        """Learn about optimal scan timing"""
        insights = []
        
        scan_durations = []
        for scan in self.memory.scan_history:
            duration = scan.get('duration', 0)
            if duration > 0:
                scan_durations.append(duration)
        
        if scan_durations:
            avg_duration = sum(scan_durations) / len(scan_durations)
            
            insights.append(LearningInsight(
                category='timing_optimization',
                insight=f'Average scan duration: {avg_duration:.1f} minutes',
                confidence=0.9,
                evidence_count=len(scan_durations),
                impact='medium',
                timestamp=datetime.now().isoformat()
            ))
        
        return insights
    
    def generate_recommendations(self, insights: List[LearningInsight]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Group insights by category
        by_category = {}
        for insight in insights:
            if insight.category not in by_category:
                by_category[insight.category] = []
            by_category[insight.category].append(insight)
        
        # Generate recommendations from high-impact insights
        for category, category_insights in by_category.items():
            high_impact = [i for i in category_insights if i.impact == 'high']
            
            if high_impact:
                top_insight = max(high_impact, key=lambda x: x.confidence)
                recommendations.append(
                    f"[{category}] {top_insight.insight} - "
                    f"Confidence: {top_insight.confidence:.0%}"
                )
        
        return recommendations
    
    def learn_from_history(self) -> Dict[str, Any]:
        """Run complete learning cycle"""
        print("\n🧠 Running learning cycle...")
        
        insights = []
        insights.extend(self.analyze_scan_patterns())
        insights.extend(self.analyze_vulnerability_patterns())
        insights.extend(self.analyze_attack_vectors())
        insights.extend(self.analyze_timing_patterns())
        
        recommendations = self.generate_recommendations(insights)
        
        # Store learning
        learning_data = {
            'timestamp': datetime.now().isoformat(),
            'insights': [asdict(i) for i in insights],
            'recommendations': recommendations,
            'total_insights': len(insights),
            'high_impact': len([i for i in insights if i.impact == 'high'])
        }
        
        # Save to memory
        self.memory.learning_log.append(learning_data)
        self.memory._save_json(
            self.memory.memory_dir / 'learning_log.json',
            self.memory.learning_log
        )
        
        print(f"✅ Learning complete: {len(insights)} insights, "
              f"{len(recommendations)} recommendations")
        
        return learning_data
    
    def get_learning_summary(self) -> Dict:
        """Get summary of learned knowledge"""
        return {
            'total_learning_cycles': len(self.memory.learning_log),
            'total_insights': sum(
                len(l.get('insights', [])) for l in self.memory.learning_log
            ),
            'recent_recommendations': self.memory.learning_log[-1].get('recommendations', [])
            if self.memory.learning_log else []
        }


def main():
    """Run learning cycle"""
    loop = LearningLoop()
    
    print("🧠 GLASSEYE Learning Loop")
    print("=" * 60)
    
    result = loop.learn_from_history()
    
    print(f"\n📊 Learning Results:")
    print(f"  Insights: {result['total_insights']}")
    print(f"  High Impact: {result['high_impact']}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # Save to file
    output_file = f'learning_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Results saved: {output_file}")


if __name__ == '__main__':
    main()
