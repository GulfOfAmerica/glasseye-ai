#!/usr/bin/env python3
"""
GLASSEYE AI Server - OpenMythos Pentesting Model API
Provides vulnerability analysis, code generation, and security intelligence
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import json
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GLASSEYE-AI")

# Initialize FastAPI
app = FastAPI(
    title="GlassEye Pentesting Agent API",
    description="AI-powered security analysis and code generation",
    version="1.0.0"
)

# Model placeholder (lightweight for CPU)
class OpenMythosModel:
    def __init__(self):
        self.name = "openmythos_tiny"
        self.params = 493962
        self.device = "cpu"
        logger.info(f"Initialized {self.name} with {self.params} parameters on {self.device}")
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for security vulnerabilities"""
        vulnerabilities = []
        
        # SQL Injection detection
        if any(keyword in code.lower() for keyword in ['execute', 'query', 'select', 'insert', 'update', 'delete']):
            if 'format' in code or '%s' in code or '+' in code:
                vulnerabilities.append({
                    "type": "SQL Injection",
                    "severity": "CRITICAL",
                    "description": "Potential SQL injection via string concatenation or formatting",
                    "recommendation": "Use parameterized queries or prepared statements"
                })
        
        # Command Injection detection
        if any(func in code for func in ['os.system', 'subprocess.call', 'eval(', 'exec(']):
            if any(var in code for var in ['input', 'request', 'user', 'params']):
                vulnerabilities.append({
                    "type": "Command Injection",
                    "severity": "CRITICAL",
                    "description": "User input passed to system commands or eval",
                    "recommendation": "Sanitize input, use allowlists, avoid eval/exec"
                })
        
        # XSS detection
        if 'render_template' in code or 'innerHTML' in code:
            if not 'escape' in code and not 'sanitize' in code:
                vulnerabilities.append({
                    "type": "Cross-Site Scripting (XSS)",
                    "severity": "HIGH",
                    "description": "Unescaped user input rendered in templates",
                    "recommendation": "Use proper output encoding/escaping"
                })
        
        # Path Traversal
        if 'open(' in code and ('request' in code or 'input' in code):
            if '..' not in code or 'normpath' not in code:
                vulnerabilities.append({
                    "type": "Path Traversal",
                    "severity": "HIGH",
                    "description": "User-controlled file paths without validation",
                    "recommendation": "Validate paths, use allowlists, normalize paths"
                })
        
        return {
            "vulnerabilities": vulnerabilities,
            "risk_score": len(vulnerabilities) * 25,
            "secure": len(vulnerabilities) == 0
        }
    
    def generate_payload(self, prompt: str) -> str:
        """Generate security testing payloads"""
        prompt_lower = prompt.lower()
        
        if 'sql injection' in prompt_lower:
            return "' OR '1'='1' -- "
        elif 'xss' in prompt_lower:
            return "<script>alert('XSS')</script>"
        elif 'command injection' in prompt_lower:
            return "; cat /etc/passwd"
        elif 'directory traversal' in prompt_lower or 'path traversal' in prompt_lower:
            return "../../../../etc/passwd"
        elif 'xxe' in prompt_lower:
            return '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'
        else:
            return f"Generated payload for: {prompt}"

# Initialize model
model = OpenMythosModel()

# Request models
class AnalyzeRequest(BaseModel):
    code: str
    language: Optional[str] = "python"

class GenerateRequest(BaseModel):
    prompt: str
    attack_type: Optional[str] = None

# Routes
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "GlassEye Pentesting Agent API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /agents": "List available agents",
            "POST /analyze": "Analyze code for vulnerabilities",
            "POST /generate": "Generate security content"
        },
        "docs": "/docs",
        "model": {
            "name": model.name,
            "params": model.params,
            "device": model.device
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": model.name,
        "device": model.device
    }

@app.get("/agents")
async def list_agents():
    """List available AI agents"""
    return {
        "agents": [
            {
                "name": "vulnerability_scanner",
                "description": "Analyzes code for security vulnerabilities",
                "capabilities": ["SQL injection", "XSS", "Command injection", "Path traversal"]
            },
            {
                "name": "payload_generator",
                "description": "Generates security testing payloads",
                "capabilities": ["SQL injection", "XSS", "XXE", "Command injection"]
            },
            {
                "name": "exploit_advisor",
                "description": "Provides exploitation guidance and recommendations",
                "capabilities": ["Attack vector analysis", "Privilege escalation", "Lateral movement"]
            }
        ]
    }

@app.post("/analyze")
async def analyze_code(request: AnalyzeRequest):
    """Analyze code for security vulnerabilities"""
    try:
        logger.info(f"Analyzing {len(request.code)} characters of {request.language} code")
        result = model.analyze_code(request.code)
        return JSONResponse(content={
            "success": True,
            "language": request.language,
            "analysis": result
        })
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_content(request: GenerateRequest):
    """Generate security testing content"""
    try:
        logger.info(f"Generating payload for: {request.prompt}")
        payload = model.generate_payload(request.prompt)
        return JSONResponse(content={
            "success": True,
            "prompt": request.prompt,
            "generated": payload,
            "type": request.attack_type
        })
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 Starting GLASSEYE AI Server on http://0.0.0.0:8002")
    logger.info(f"📊 Model: {model.name} ({model.params} params)")
    logger.info("📚 Documentation: http://localhost:8002/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
        access_log=True
    )
