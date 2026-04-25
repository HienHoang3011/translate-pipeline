#!/usr/bin/env python3
"""
Setup script để install vLLM và dependencies.
Chạy: python setup_vllm.py
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a shell command with description."""
    print(f"\n{'='*60}")
    print(f"Installing: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"ERROR: Failed to install {description}")
        sys.exit(1)
    print(f"Successfully installed: {description}")

def main():
    print("vLLM Setup Script")
    print("This will install vLLM and all required dependencies")
    
    # 1. Install vLLM with CUDA support
    run_command(
        "uv pip install --upgrade vllm --torch-backend=auto --extra-index-url https://wheels.vllm.ai/nightly",
        "vLLM"
    )
    
    # 2. Install transformers
    run_command(
        "uv pip install --upgrade transformers",
        "Transformers"
    )
    
    # 3. Install torch (should be already installed but ensure latest)
    run_command(
        "uv pip install --upgrade torch",
        "PyTorch"
    )
    
    # 4. Install accelerate
    run_command(
        "uv pip install --upgrade accelerate",
        "Accelerate"
    )
    
    # 5. Install OpenAI (for vLLM API client)
    run_command(
        "uv pip install --upgrade openai",
        "OpenAI Python SDK"
    )
    
    print("\n" + "="*60)
    print("All packages installed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start vLLM server: python start_vllm.py")
    print("2. In another terminal, run: python main.py --input_file <json_file>")

if __name__ == "__main__":
    main()
