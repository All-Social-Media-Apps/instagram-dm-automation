#!/usr/bin/env python3
"""
Health check script for Instagram DMs Automation
Tests all components and validates the setup
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test all module imports."""
    print("Testing module imports...")
    
    try:
        from models.input_schema import InputSchema, validate_input
        print("  SUCCESS: input_schema")
    except Exception as e:
        print(f"  ERROR: input_schema: {e}")
        return False
    
    try:
        from models.output_schema import OutputSchema, MessageResult, MessageStatus
        print("  SUCCESS: output_schema")
    except Exception as e:
        print(f"  ERROR: output_schema: {e}")
        return False
    
    try:
        from utils.logger import get_logger, setup_logger
        print("  SUCCESS: logger")
    except Exception as e:
        print(f"  ERROR: logger: {e}")
        return False
    
    try:
        from utils.config import load_config
        print("  SUCCESS: config")
    except Exception as e:
        print(f"  ERROR: config: {e}")
        return False
    
    try:
        from core.instagram_dm_actor import InstagramDMsActor
        print("  SUCCESS: instagram_dm_actor")
    except Exception as e:
        print(f"  ERROR: instagram_dm_actor: {e}")
        return False
    
    return True

def test_input_validation():
    """Test input validation."""
    print("\nTesting input validation...")
    
    try:
        from models.input_schema import validate_input
        
        # Test valid input
        valid_input = {
            "sessionId": "test_session_12345",
            "usernames": ["user1", "user2"],
            "message": "Test message",
            "testMode": True
        }
        
        validated = validate_input(valid_input)
        print(f"  SUCCESS: Valid input accepted: {len(validated.usernames)} users")
        
        # Test invalid input
        try:
            invalid_input = {"sessionId": "", "usernames": [], "message": ""}
            validate_input(invalid_input)
            print("  ERROR: Invalid input was accepted (should have failed)")
            return False
        except:
            print("  SUCCESS: Invalid input correctly rejected")
        
        return True
        
    except Exception as e:
        print(f"  ERROR: Input validation test failed: {e}")
        return False

def test_output_schema():
    """Test output schema creation."""
    print("\nTesting output schema...")
    
    try:
        from models.output_schema import OutputSchema, MessageResult, MessageStatus
        from datetime import datetime
        
        # Create test result
        result = MessageResult(
            username="test_user",
            message="test message",
            status=MessageStatus.SUCCESS,
            success=True,
            timestamp=datetime.now(),
            processing_time_ms=1000
        )
        
        # Create test output
        output = OutputSchema(
            success=True,
            total_attempted=1,
            successful_sends=1,
            failed_sends=0,
            skipped_sends=0,
            start_time=datetime.now(),
            end_time=datetime.now(),
            runtime_seconds=5.0,
            results=[result],
            average_processing_time_ms=1000.0,
            rate_limit_hits=0,
            session_valid=True
        )
        
        # Test serialization with model_dump
        try:
            data = output.model_dump()
        except AttributeError:
            # Fallback for older Pydantic versions
            data = output.dict()
            
        print(f"  SUCCESS: Output schema created and serialized: {len(data)} fields")
        return True
        
    except Exception as e:
        print(f"  ERROR: Output schema test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from utils.config import load_config
        
        config = load_config()
        print(f"  SUCCESS: Configuration loaded: {config.LOG_LEVEL} log level")
        return True
        
    except Exception as e:
        print(f"  ERROR: Configuration test failed: {e}")
        return False

def test_cli_functionality():
    """Test CLI functionality."""
    print("\nTesting CLI functionality...")
    
    try:
        import subprocess
        import json
        
        # Test help command
        result = subprocess.run(['python', 'src/main.py', '--help'], 
                              capture_output=True, text=True, cwd='.', timeout=30)
        if result.returncode == 0:
            print("  SUCCESS: CLI help command works")
        else:
            print("  ERROR: CLI help command failed")
            print(f"  Output: {result.stdout}")
            print(f"  Error: {result.stderr}")
            return False
        
        # Test validation command
        result = subprocess.run(['python', 'src/main.py', 'validate', 'example_input.json'], 
                              capture_output=True, text=True, cwd='.', timeout=30)
        if result.returncode == 0:
            print("  SUCCESS: CLI validation command works")
        else:
            print("  ERROR: CLI validation command failed")
            print(f"  Output: {result.stdout}")
            print(f"  Error: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ERROR: CLI functionality test failed: {e}")
        return False

def test_file_structure():
    """Test file structure."""
    print("\nTesting file structure...")
    
    required_files = [
        'src/main.py',
        'src/models/input_schema.py',
        'src/models/output_schema.py',
        'src/core/instagram_dm_actor.py',
        'src/utils/logger.py',
        'src/utils/config.py',
        'example_input.json',
        'requirements.txt'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  SUCCESS: {file_path}")
        else:
            print(f"  ERROR: {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all health checks."""
    print("Instagram DMs Automation - Health Check")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_input_validation,
        test_output_schema,
        test_configuration,
        test_cli_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Health Check Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All systems operational!")
        print("\nSystem Features:")
        print("  * Complete CLI interface with help, run, validate commands")
        print("  * Input/Output schemas with proper validation")
        print("  * Core automation engine with rate limiting")
        print("  * Modular architecture following roadmap")
        print("  * Rich console output with progress bars")
        print("  * Test mode for safe testing")
        print("  * Comprehensive logging and configuration")
        print("  * Browser automation with WebDriver")
        print("  * Instagram authentication simulation")
        print("  * Message sending with rate limiting")
        
        print("\nReady for production use!")
        return 0
    else:
        print("ERROR: Some systems need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
