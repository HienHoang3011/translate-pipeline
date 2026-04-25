#!/usr/bin/env python3
"""
Setup script để install vLLM và dependencies vào .venv.
Chạy: python setup_vllm.py
"""

import subprocess
import sys
import os
import platform

def get_venv_python():
    """Get the python executable path from .venv"""
    if platform.system() == "Windows":
        venv_python = os.path.join(".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(".venv", "bin", "python")
    
    if not os.path.exists(venv_python):
        print(f"ERROR: Virtual environment not found at {venv_python}")
        print("Please run: uv venv to create the virtual environment first")
        sys.exit(1)
    
    return venv_python

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
    print("This will install vLLM and all required dependencies into .venv\n")
    
    venv_python = get_venv_python()
    print(f"Using Python from .venv: {venv_python}\n")
    
    # 1. Install vLLM with CUDA support
    run_command(
        f'uv pip install --python {venv_python} --upgrade vllm --torch-backend=auto --extra-index-url https://wheels.vllm.ai/nightly',
        "vLLM"
    )
    
    # 2. Install transformers
    run_command(
        f'uv pip install --python {venv_python} --upgrade transformers',
        "Transformers"
    )
    
    # 3. Install torch (should be already installed but ensure latest)
    run_command(
        f'uv pip install --python {venv_python} --upgrade torch',
        "PyTorch"
    )
    
    # 4. Install accelerate
    run_command(
        f'uv pip install --python {venv_python} --upgrade accelerate',
        "Accelerate"
    )
    
    # 5. Install OpenAI (for vLLM API client)
    run_command(
        f'uv pip install --python {venv_python} --upgrade openai',
        "OpenAI Python SDK"
    )
    
    print("\n" + "="*60)
    print("All packages installed successfully in .venv!")
    print("="*60)
    print("\nNext steps:")
    print("1. Activate venv (if not already):")
    if platform.system() == "Windows":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("\n2. Start vLLM server: python start_vllm.py")
    print("3. In another terminal, run: python main.py --input_file <json_file>")

if __name__ == "__main__":
    main()
