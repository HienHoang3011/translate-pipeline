#!/usr/bin/env python3
"""
Start vLLM server for local inference with configurable parameters.
Chạy: python start_vllm.py [options]

Examples:
  python start_vllm.py
  python start_vllm.py --port 5001 --gpu-memory 0.7
  python start_vllm.py --model "google/gemma-2-9b-it" --max-len 4096
"""

import subprocess
import time
import requests
import sys
import argparse
from workflow.utils.model_loader import DEFAULT_MODEL_ID

def wait_for_server(host, port, timeout=300, interval=10):
    """Wait for vLLM server to be ready."""
    url = f"http://{host}:{port}/health"
    print(f"Waiting for server to be ready (timeout: {timeout}s)...")
    print(f"Health check URL: {url}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
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
    parser = argparse.ArgumentParser(
        description="Start vLLM server with configurable parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_vllm.py
  python start_vllm.py --port 5001 --gpu-memory 0.7
  python start_vllm.py --model "google/gemma-2-9b-it" --max-len 4096
  python start_vllm.py --host 0.0.0.0 --port 8000 --dtype float16
        """
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL_ID,
        help=f"Model ID to load (default: {DEFAULT_MODEL_ID})"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run server on (default: 5000)"
    )
    
    parser.add_argument(
        "--gpu-memory",
        type=float,
        default=0.85,
        help="GPU memory utilization (0.0-1.0, default: 0.85)"
    )
    
    parser.add_argument(
        "--max-len",
        type=int,
        default=8192,
        help="Maximum model length (default: 8192)"
    )
    
    parser.add_argument(
        "--dtype",
        type=str,
        default="auto",
        choices=["auto", "float16", "float32", "bfloat16"],
        help="Data type for model (default: auto)"
    )
    
    parser.add_argument(
        "--tensor-parallel",
        type=int,
        default=1,
        help="Tensor parallelism size (default: 1)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Server startup timeout in seconds (default: 300)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not 0 < args.gpu_memory <= 1.0:
        print("ERROR: --gpu-memory must be between 0 and 1")
        sys.exit(1)
    
    if args.port < 1024 or args.port > 65535:
        print("ERROR: --port must be between 1024 and 65535")
        sys.exit(1)
    
    model = args.model
    host = args.host
    port = args.port
    
    print("Starting vLLM server...")
    print(f"Model: {model}")
    print(f"API: http://{host}:{port}/v1")
    print(f"GPU Memory: {args.gpu_memory * 100}%")
    print(f"Max Length: {args.max_len}")
    print(f"Data Type: {args.dtype}")
    print(f"Tensor Parallel: {args.tensor_parallel}")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        # Start vLLM server - show logs in real-time
        print("vLLM Server Output:")
        print("-" * 60)
        process = subprocess.Popen(
            [
                "vllm", "serve",
                model,
                "--host", host,
                "--port", str(port),
                "--gpu-memory-utilization", str(args.gpu_memory),
                "--max-model-len", str(args.max_len),
                "--dtype", args.dtype,
                "--tensor-parallel-size", str(args.tensor_parallel)
            ],
            stdout=None,  # Show logs on console
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait for server to be ready
        if wait_for_server(host, port, timeout=args.timeout):
            print("\n" + "="*60)
            print("vLLM Server is ready!")
            print("="*60)
            print("\nServer Details:")
            print(f"  Base URL: http://{host}:{port}/v1")
            print(f"  Model: {model}")
            print("\nYou can now run the translation pipeline:")
            print(f"  python main.py --input_file <json_file>")
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
