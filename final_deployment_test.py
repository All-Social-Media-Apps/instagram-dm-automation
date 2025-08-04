#!/usr/bin/env python3
"""
Final deployment test for Instagram DMs Automation
Tests all functionality to ensure production readiness
"""

import sys
import json
import subprocess
from pathlib import Path
import time

def run_test(name, command, timeout=30):
    """Run a test command and return success status."""
    print(f"\nTesting: {name}")
    print(f"Command: {' '.join(command)}")
    print("-" * 40)
    
    try:
        start_time = time.time()
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd='.')
        end_time = time.time()
        
        print(f"Exit code: {result.returncode}")
        print(f"Runtime: {end_time - start_time:.2f}s")
        
        if result.returncode == 0:
            print("STATUS: SUCCESS")
            if result.stdout:
                print("Output:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            return True
        else:
            print("STATUS: FAILED")
            if result.stderr:
                print("Error:", result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"STATUS: TIMEOUT (>{timeout}s)")
        return False
    except Exception as e:
        print(f"STATUS: ERROR - {e}")
        return False

def main():
    """Run comprehensive deployment tests."""
    print("Instagram DMs Automation - Final Deployment Test")
    print("=" * 60)
    
    tests = [
        ("CLI Help", ['python', 'src/main.py', '--help']),
        ("Input Validation", ['python', 'src/main.py', 'validate', 'example_input.json']),
        ("Test Mode Run (CLI)", [
            'python', 'src/main.py', 'run', 
            '-s', 'test_session_123', 
            '-u', 'test_user', 
            '-m', 'Test message', 
            '--test-mode',
            '-o', 'final_test_cli.json'
        ]),
        ("Test Mode Run (File)", [
            'python', 'src/main.py', 'run', 
            '-i', 'example_input.json',
            '--test-mode',
            '-o', 'final_test_file.json'
        ])
    ]
    
    passed = 0
    total = len(tests)
    
    for name, command in tests:
        if run_test(name, command, timeout=120):  # Longer timeout for automation runs
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: System is ready for production deployment!")
        
        # Check output files
        output_files = ['final_test_cli.json', 'final_test_file.json']
        for file_path in output_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    print(f"  * {file_path}: {data.get('total_attempted', 0)} messages processed")
                except:
                    print(f"  * {file_path}: File exists but couldn't parse JSON")
        
        print("\nQuick Start Guide:")
        print("1. Validate your input file:")
        print("   python src/main.py validate your_input.json")
        print("")
        print("2. Run in test mode first:")
        print("   python src/main.py run -i your_input.json --test-mode")
        print("")
        print("3. Run for real (remove --test-mode):")
        print("   python src/main.py run -i your_input.json")
        
        return True
    else:
        print("\nERROR: System needs attention before production use")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
