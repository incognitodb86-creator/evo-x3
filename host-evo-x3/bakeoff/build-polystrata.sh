#!/bin/bash
set -x
export SDK=$HOME/rocm/install
export ROCM_PATH=$SDK HIP_PATH=$SDK HIP_PLATFORM=amd
export PATH=$SDK/bin:$SDK/lib/llvm/bin:$PATH
export LD_LIBRARY_PATH=$SDK/lib:$SDK/lib/rocm_sysdeps/lib:$SDK/lib/llvm/lib:${LD_LIBRARY_PATH:-}
cd /srv/bakeoff/src/PolyStrata
CL=$SDK/lib/llvm/bin/clang++; [ -x $CL ] || CL=$SDK/llvm/bin/clang++
BC=$SDK/lib/llvm/amdgcn/bitcode; [ -d $BC ] || BC=$SDK/amdgcn/bitcode
cmake -S . -B build-halo -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DSTRATA_ENABLE_HIP=ON -DSTRATA_ENABLE_CUDA=OFF -DSTRATA_PREFILL_MMQ=ON -DSTRATA_BUILD_TESTS=OFF \
  -DCMAKE_HIP_ARCHITECTURES=gfx1151 \
  -DCMAKE_HIP_COMPILER=$CL -DCMAKE_HIP_COMPILER_ROCM_ROOT=$SDK \
  "-DCMAKE_PREFIX_PATH=$SDK;$SDK/lib/rocm_sysdeps;$SDK/lib/llvm" \
  "-DCMAKE_HIP_FLAGS=--rocm-path=$SDK --rocm-device-lib-path=$BC" \
  -DSTRATA_GGML_DIR=/srv/bakeoff/src/PolyStrata/third_party/llama.cpp
echo CMAKE_EXIT $?
cmake --build build-halo --target strata strata-poly -j 24
echo BUILD_EXIT $?
ls -la build-halo/strata build-halo/strata-poly
date
