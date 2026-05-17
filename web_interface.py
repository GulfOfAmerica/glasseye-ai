#!/usr/bin/env python3
"""
GLASSEYE AI OS - Web Interface
God-mode control panel for cyberviserai.com
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add glasseye to path
sys.path.append('/home/x/glasseye')

from integrated_config import GlasseyeConfig
from memory_system import GlasseyeMemory
from autonomous_recon import AutonomousRecon
from ai_decision_engine import AIDecisionEngine

app = Flask(__name__)
CORS(app)

# Initialize
config = GlasseyeConfig()
memory = GlasseyeMemory()
recon = AutonomousRecon()
ai_engine = AIDecisionEngine()


@app.route('/')
def index():
    """Main dashboard"""
    return jsonify({
        'title': 'GLASSEYE AI OS',
        'version': '1.0',
        'status': 'operational',
        'endpoints': {
            '/api/status': 'System status',
            '/api/scan': 'Start reconnaissance (POST)',
            '/api/history': 'Scan history',
            '/api/targets': 'Target intelligence',
            '/api/modules': 'List modules',
            '/api/credentials': 'Platform status'
        }
    })


@app.route('/api/status')
def status():
    """System status"""
    return jsonify({
        'glasseye': {
            'status': 'operational',
            'scans_completed': len(memory.scan_history),
            'targets_tracked': len(memory.target_profiles)
        },
        'services': {
            'glasseye_ai': 'http://localhost:8002/health',
            'claude_api': 'http://localhost:8000/health',
            'mcp_server': 'http://localhost:5001/health'
        },
        'platforms': {
            'aws': 'connected',
            'github': 'connected',
            'azure': 'connected',
            'google_cloud': 'connected'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/scan', methods=['POST'])
def scan():
    """Start autonomous reconnaissance"""
    data = request.json
    target = data.get('target')
    
    if not target:
        return jsonify({'error': 'Target required'}), 400
    
    try:
        result = recon.run_autonomous_recon(target)
        return jsonify({
            'status': 'success',
            'target': target,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/history')
def history():
    """Scan history"""
    return jsonify({
        'scans': memory.scan_history[-10:],  # Last 10 scans
        'total': len(memory.scan_history)
    })


@app.route('/api/targets')
def targets():
    """Target intelligence"""
    return jsonify({
        'targets': list(memory.target_profiles.values()),
        'total': len(memory.target_profiles)
    })


@app.route('/api/modules')
def modules():
    """List operational modules"""
    modules = [
        {'name': 'Autonomous Reconnaissance', 'status': 'operational', 'version': '1.0'},
        {'name': 'Auto-Exploitation', 'status': 'operational', 'version': '1.0'},
        {'name': 'Bug Bounty Automation', 'status': 'operational', 'version': '1.0'},
        {'name': 'AI Decision Engine', 'status': 'operational', 'version': '2.0'},
        {'name': 'Memory System', 'status': 'operational', 'version': '1.0'},
        {'name': 'Metasploit Integration', 'status': 'operational', 'version': '1.0'},
        {'name': 'AI Code Generator', 'status': 'operational', 'version': '1.0'},
        {'name': 'Auto-Testing Framework', 'status': 'operational', 'version': '1.0'},
        {'name': 'Web Interface', 'status': 'operational', 'version': '1.0'},
        {'name': 'OSINT Engine', 'status': 'building', 'version': '0.1'},
        {'name': 'Learning Loop', 'status': 'building', 'version': '0.1'}
    ]
    
    return jsonify({
        'modules': modules,
        'total': len(modules),
        'operational': len([m for m in modules if m['status'] == 'operational'])
    })


@app.route('/api/credentials')
def credentials():
    """Platform connection status"""
    api_config = config.get_api_config()
    
    return jsonify({
        'aws': {'status': 'connected', 'account': api_config['aws']['account_id']},
        'github': {'status': 'connected', 'user': api_config['github']['user']},
        'claude': {'status': 'connected', 'service': 'Anthropic API'},
        'azure': {'status': 'connected'},
        'google_cloud': {'status': 'connected'}
    })


@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    """AI-powered target analysis"""
    data = request.json
    target = data.get('target')
    
    if not target:
        return jsonify({'error': 'Target required'}), 400
    
    try:
        decision = ai_engine.analyze_target(target)
        return jsonify({
            'status': 'success',
            'analysis': decision
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'GLASSEYE Web Interface',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("👁️⚡💀 GLASSEYE Web Interface starting...")
    print(f"🌐 Access at: http://localhost:5002")
    print(f"🌐 Production: https://cyberviserai.com")
    app.run(host='0.0.0.0', port=5002, debug=False)
