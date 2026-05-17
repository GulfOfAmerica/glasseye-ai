#!/usr/bin/env python3
"""GLASSEYE AWS ECS/Fargate Deployment Orchestrator"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class GlasseyeAWSDeployer:
    def __init__(self):
        self.deployment_id = f"glasseye-{int(time.time())}"
        self.region = "us-east-1"
        self.account_id = "347694270918"
        self.results = {
            "deployment_id": self.deployment_id,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "steps": [],
            "errors": [],
            "warnings": []
        }
    
    def log_step(self, step_name, status, details=""):
        """Log deployment step"""
        step = {
            "step": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.results["steps"].append(step)
        
        icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
        print(f"{icon} {step_name}: {status}")
        if details:
            print(f"   {details}")
    
    def run_command(self, cmd, timeout=300):
        """Execute shell command with timeout"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)
    
    def check_aws_credentials(self):
        """Verify AWS credentials"""
        success, stdout, stderr = self.run_command("aws sts get-caller-identity")
        if success:
            self.log_step("AWS Credentials Check", "success", "Authenticated to AWS")
            return True
        else:
            self.log_step("AWS Credentials Check", "failed", stderr)
            self.results["errors"].append("AWS credentials not configured")
            return False
    
    def create_ecr_repository(self):
        """Create ECR repository if it doesn't exist"""
        repo_name = "glasseye-ai"
        
        # Check if repo exists
        check_cmd = f"aws ecr describe-repositories --repository-names {repo_name} --region {self.region} 2>/dev/null"
        exists, _, _ = self.run_command(check_cmd)
        
        if exists:
            self.log_step("ECR Repository", "success", f"Repository {repo_name} already exists")
            return True
        
        # Create repository
        create_cmd = f"aws ecr create-repository --repository-name {repo_name} --region {self.region}"
        success, stdout, stderr = self.run_command(create_cmd)
        
        if success:
            self.log_step("ECR Repository Creation", "success", f"Created {repo_name}")
            return True
        else:
            self.log_step("ECR Repository Creation", "failed", stderr)
            self.results["errors"].append(f"Failed to create ECR repository: {stderr}")
            return False
    
    def build_docker_image(self):
        """Build Docker image"""
        print("\n🔨 Building Docker image...")
        
        build_cmd = "cd /home/x/glasseye && docker build -t glasseye-ai:latest ."
        success, stdout, stderr = self.run_command(build_cmd, timeout=600)
        
        if success:
            self.log_step("Docker Build", "success", "Image built successfully")
            return True
        else:
            self.log_step("Docker Build", "failed", stderr[-500:])
            self.results["errors"].append("Docker build failed")
            return False
    
    def push_to_ecr(self):
        """Push Docker image to ECR"""
        print("\n📤 Pushing to ECR...")
        
        # Login to ECR
        login_cmd = f"aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {self.account_id}.dkr.ecr.{self.region}.amazonaws.com"
        success, _, stderr = self.run_command(login_cmd)
        
        if not success:
            self.log_step("ECR Login", "failed", stderr)
            return False
        
        self.log_step("ECR Login", "success", "Logged into ECR")
        
        # Tag image
        ecr_uri = f"{self.account_id}.dkr.ecr.{self.region}.amazonaws.com/glasseye-ai:latest"
        tag_cmd = f"docker tag glasseye-ai:latest {ecr_uri}"
        success, _, stderr = self.run_command(tag_cmd)
        
        if not success:
            self.log_step("Docker Tag", "failed", stderr)
            return False
        
        # Push image
        push_cmd = f"docker push {ecr_uri}"
        success, stdout, stderr = self.run_command(push_cmd, timeout=900)
        
        if success:
            self.log_step("ECR Push", "success", f"Pushed to {ecr_uri}")
            self.results["ecr_uri"] = ecr_uri
            return True
        else:
            self.log_step("ECR Push", "failed", stderr[-500:])
            self.results["errors"].append("ECR push failed")
            return False
    
    def create_deployment_summary(self):
        """Create deployment summary"""
        self.results["status"] = "success" if not self.results["errors"] else "partial"
        
        summary = {
            "deployment_id": self.deployment_id,
            "status": self.results["status"],
            "timestamp": self.results["timestamp"],
            "total_steps": len(self.results["steps"]),
            "successful_steps": len([s for s in self.results["steps"] if s["status"] == "success"]),
            "failed_steps": len([s for s in self.results["steps"] if s["status"] == "failed"]),
            "ecr_uri": self.results.get("ecr_uri", "N/A"),
            "region": self.region,
            "account": self.account_id
        }
        
        return summary
    
    def deploy(self):
        """Execute full deployment"""
        print(f"\n🚀 GLASSEYE AWS DEPLOYMENT ORCHESTRATION")
        print(f"{'='*60}\n")
        
        # Step 1: Check AWS credentials
        if not self.check_aws_credentials():
            return self.results
        
        # Step 2: Create ECR repository
        if not self.create_ecr_repository():
            return self.results
        
        # Step 3: Build Docker image
        if not self.build_docker_image():
            return self.results
        
        # Step 4: Push to ECR
        if not self.push_to_ecr():
            return self.results
        
        # Generate summary
        summary = self.create_deployment_summary()
        self.results["summary"] = summary
        
        print(f"\n{'='*60}")
        print("📊 DEPLOYMENT SUMMARY")
        print(f"{'='*60}")
        print(json.dumps(summary, indent=2))
        
        return self.results

if __name__ == "__main__":
    deployer = GlasseyeAWSDeployer()
    results = deployer.deploy()
    
    # Save results
    results_file = Path("/home/x/glasseye/deployment_results.json")
    results_file.write_text(json.dumps(results, indent=2))
    print(f"\n✅ Results saved to: {results_file}")
