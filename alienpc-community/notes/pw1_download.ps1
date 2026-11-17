# PW1 (ALI-163 bakeoff): download the H3 Omni prompt-rewriter weights (GGUF route, node README table
# "Q4_K_M base + projector + Q8_0 adapter" + the lightx2v safetensors adapter the task names).
# Detached, resumable, logged. No GPU, no ComfyUI call.
$ErrorActionPreference = 'Continue'
$LLM   = 'C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\LLM'
$OMNI  = Join-Path $LLM 'Qwen2.5-Omni-7B-GGUF'
$ADP   = Join-Path $LLM 'MiniMax-H3-Prompt-Rewriter-LoRA-Omni'
$LX    = Join-Path $ADP 'lightx2v-safetensors'
New-Item -ItemType Directory -Force -Path $OMNI,$ADP,$LX | Out-Null
$jobs = @(
  @{ u='https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF/resolve/main/Qwen2.5-Omni-7B-Q4_K_M.gguf';        d=(Join-Path $OMNI 'Qwen2.5-Omni-7B-Q4_K_M.gguf') },
  @{ u='https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF/resolve/main/mmproj-Qwen2.5-Omni-7B-Q8_0.gguf';   d=(Join-Path $OMNI 'mmproj-Qwen2.5-Omni-7B-Q8_0.gguf') },
  @{ u='https://huggingface.co/pytraveler/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF/resolve/main/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf'; d=(Join-Path $ADP 'MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf') },
  @{ u='https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/resolve/main/adapter_model.safetensors'; d=(Join-Path $LX 'adapter_model.safetensors') },
  @{ u='https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/resolve/main/adapter_config.json';  d=(Join-Path $LX 'adapter_config.json') },
  @{ u='https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/resolve/main/README.md';            d=(Join-Path $LX 'README.md') },
  @{ u='https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/resolve/main/requirements.txt';     d=(Join-Path $LX 'requirements.txt') },
  @{ u='https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/resolve/main/system_prompt.py';     d=(Join-Path $LX 'system_prompt.py') }
)
foreach ($j in $jobs) {
  Write-Output ("START " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + " CT " + $j.d)
  & curl.exe -sSL --fail --retry 8 --retry-delay 5 -C - --connect-timeout 30 -o $j.d $j.u
  Write-Output ("DONE rc=$LASTEXITCODE " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + " CT " + $j.d + " bytes=" + $(if (Test-Path $j.d) { (Get-Item $j.d).Length } else { 'missing' }))
}
Write-Output "ALL DONE"
