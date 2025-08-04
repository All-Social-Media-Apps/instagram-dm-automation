#!/usr/bin/env python3
"""
Production deployment script for Instagram DMs Automation
Handles setup, validation, and first-run configuration
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return False
    except Exception as e:
        print(f"💥 {description} error: {e}")
        return False

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Required: Python 3.8 or higher")
        return False

def setup_virtual_environment():
    """Create and activate virtual environment."""
    if not Path("venv").exists():
        print("🏗️ Creating virtual environment...")
        if not run_command("python -m venv venv", "Virtual environment creation"):
            return False
    
    print("✅ Virtual environment ready")
    return True

def install_dependencies():
    """Install required dependencies."""
    activate_cmd = "venv\\Scripts\\activate.bat &&" if os.name == 'nt' else "source venv/bin/activate &&"
    cmd = f"{activate_cmd} pip install --upgrade pip && pip install -r requirements.txt"
    return run_command(cmd, "Dependencies installation")

def run_health_check():
    """Run system health check."""
    activate_cmd = "venv\\Scripts\\activate.bat &&" if os.name == 'nt' else "source venv/bin/activate &&"
    cmd = f"{activate_cmd} python health_check.py"
    return run_command(cmd, "System health check")

def create_sample_config():
    """Create sample configuration files."""
    print("📝 Creating sample configuration...")
    
    # Create sample input file if it doesn't exist
    if not Path("my_input.json").exists():
        sample_input = {
            "sessionId": "YOUR_INSTAGRAM_SESSION_ID_HERE",
            "usernames": ["target_user1", "target_user2"],
            "message": "Hello! This is your custom message.",
            "testMode": True,
            "delayBetweenMessages": 60,
            "maxRetries": 3,
            "headless": True,
            "timeout": 30
        }
        
        with open("my_input.json", "w", encoding="utf-8") as f:
            json.dump(sample_input, f, indent=2)
        print("✅ Created my_input.json - Edit this file with your settings")
    
    return True

def main():
    """Main deployment function."""
    print("🚀 Instagram DMs Automation - Production Deployment")
    print("=" * 60)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Virtual Environment Setup", setup_virtual_environment),
        ("Dependencies Installation", install_dependencies),
        ("System Health Check", run_health_check),
        ("Sample Configuration", create_sample_config)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if step_func():
            success_count += 1
        else:
            print(f"❌ Step failed: {step_name}")
            break
    
    print(f"\n{'='*60}")
    if success_count == len(steps):
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("\n📋 Next Steps:")
        print("1. Edit my_input.json with your Instagram session ID and targets")
        print("2. Test with: python src/main.py validate my_input.json")
        print("3. Run in test mode: python src/main.py run -i my_input.json --test-mode")
        print("4. Go live: python src/main.py run -i my_input.json")
        print("\n🛡️ Always test in --test-mode first!")
        return True
    else:
        print(f"❌ DEPLOYMENT FAILED ({success_count}/{len(steps)} steps completed)")
        print("Please fix the errors above and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
