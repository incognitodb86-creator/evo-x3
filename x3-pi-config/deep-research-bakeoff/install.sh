#!/bin/bash
set -x
cd ~/evo-x3
python3 -m venv .venv-ldr && .venv-ldr/bin/pip install -q --upgrade pip && .venv-ldr/bin/pip install -q --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple torch && .venv-ldr/bin/pip install -q local-deep-research && echo LDR_OK
python3 -m venv .venv-gptr && .venv-gptr/bin/pip install -q --upgrade pip && .venv-gptr/bin/pip install -q gpt-researcher && echo GPTR_OK
.venv-ldr/bin/pip show local-deep-research | head -3; .venv-gptr/bin/pip show gpt-researcher | head -3
du -sh .venv-ldr .venv-gptr
echo INSTALL_DONE
