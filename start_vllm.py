#!/usr/bin/env python3
"""
Start vLLM server for local inference.
Chạy: python start_vllm.py
"""

import subprocess
import time
import requests
import sys
from workflow.utils.model_loader import DEFAULT_MODEL_ID

def wait_for_server(timeout=300, interval=10):
    """Wait for vLLM server to be ready."""
    print(f"Waiting for server to be ready (timeout: {timeout}s)...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:5000/health")
            if response.status_code == 200:
                print("✓ Server is up and running!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        elapsed = int(time.time() - start_time)
        print(f"  [{elapsed}s] Still waiting... (check every {interval}s)")
        time.sleep(interval)
    
    print("✗ Server failed to start within timeout")
    return False

def main():
    model = DEFAULT_MODEL_ID
    
    print("Starting vLLM server...")
    print(f"Model: {model}")
    print("API: http://localhost:5000/v1")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        # Start vLLM server
        process = subprocess.Popen(
            [
                "vllm", "serve",
                model,
                "--host", "0.0.0.0",
                "--port", "5000",
                "--gpu-memory-utilization", "0.9",
                "--max-model-len", "16384",
                "--dtype", "auto",
                "--tensor-parallel-size", "1"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait for server to be ready
        if wait_for_server():
            print("\n" + "="*60)
            print("vLLM Server is ready!")
            print("="*60)
            print("\nServer Details:")
            print(f"  Base URL: http://localhost:5000/v1")
            print(f"  Model: {model}")
            print("\nYou can now run the translation pipeline:")
            print("  python main.py --input_file <json_file>")
            print("\nPress Ctrl+C to stop the server\n")
            
            # Keep server running
            process.wait()
        else:
            print("Failed to connect to server")
            process.terminate()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down vLLM server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Server stopped.")

if __name__ == "__main__":
    main()
