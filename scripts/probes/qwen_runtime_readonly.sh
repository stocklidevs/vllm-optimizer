#!/usr/bin/env bash
set -u

VENV="$HOME/qwen3next-venv"

echo "QWEN_VENV"
ls -la "$VENV/bin" | grep -E '(python|vllm|pip)$' || true

echo "PYTHON_VERSION"
"$VENV/bin/python" --version || true

echo "VLLM_PATH"
"$VENV/bin/python" -c 'import shutil; print(shutil.which("vllm"))' || true

echo "VLLM_VERSION"
"$VENV/bin/python" -c 'import importlib.metadata as m; print(m.version("vllm"))' || true

echo "TORCH_VERSION_AND_CUDA"
"$VENV/bin/python" -c 'import torch; print(torch.__version__); print(torch.cuda.is_available())' || true

echo "VLLM_HELP"
"$VENV/bin/vllm" --help | head -40 || true
