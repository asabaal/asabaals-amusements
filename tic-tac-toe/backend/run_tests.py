#!/usr/bin/env python3
"""
Test runner for Tic-Tac-Toe AI Arena
Follows safe server launch protocol
"""

import subprocess
import time
import sys
import os

def run_server():
    """Start server using safe silent-detachment protocol"""
    print("Starting server with safe silent-detachment protocol...")
    cmd = ["python", "main.py"]
    process = subprocess.Popen(
        cmd,
        cwd=os.path.dirname(__file__),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)  # Wait for server to start
    return process

def stop_server():
    """Stop server safely"""
    print("Stopping server...")
    subprocess.run(["pkill", "-f", "python.*main.py"])
    time.sleep(1)

def run_test_suite():
    """Run all test suites"""
    test_modules = [
        ("tests.test_game", "Game logic"),
        ("tests.test_agents", "Agent system"),
        ("tests.test_models", "Data models"),
        ("tests.test_api_integration", "API integration"),
        ("tests.test_ollama_mock", "Ollama client"),
        ("tests.test_edge_cases", "Edge cases")
    ]
    
    results = []
    
    for module, description in test_modules:
        print(f"Running {description} tests...")
        result = subprocess.run([sys.executable, "-m", "unittest", module], 
                             cwd=os.path.dirname(__file__))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        print(f"{description} tests: {status}")
        results.append(result)
    
    # Overall result
    all_passed = all(r.returncode == 0 for r in results)
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.returncode == 0)
    
    print(f"\nTest Summary: {passed_tests}/{total_tests} test suites passed")
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    return all_passed

if __name__ == "__main__":
    try:
        # Start server
        server_process = run_server()
        
        try:
            # Run tests
            success = run_test_suite()
        finally:
            # Always stop server
            stop_server()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        stop_server()
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        stop_server()
        sys.exit(1)