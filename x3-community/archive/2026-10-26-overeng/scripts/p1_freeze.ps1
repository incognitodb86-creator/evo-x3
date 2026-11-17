# P1 freeze (ALI-123). Nothing is changed except new tags, backups and snapshot files.
$ErrorActionPreference='Continue'
$W='C:\AI\community'; $P="$W\p1"; New-Item -ItemType Directory -Force $P | Out-Null
$C='C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI'
$log="$P\p1.log"; function L($s){ $l="$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') CT $s"; $l; Add-Content $log $l }
L "P1 START"
# 1) backups of live configs
foreach($f in 'C:\AI\director\config\llama-swap.yaml','C:\AI\director\config\director.live.yaml'){
  if(Test-Path $f){ Copy-Item $f "$f.bak-community" -Force; L "BACKUP $f -> $f.bak-community" } else { L "MISSING $f" } }
# 2) git tags (HEAD + working-tree snapshot via stash create; working tree untouched)
foreach($r in 'C:\AI\director','C:\AI\forge-host','C:\AI\forge-bench','C:\Users\derek\5slock\workflows'){
  $head = git -C $r rev-parse HEAD 2>&1
  git -C $r tag -f pre-community-2026-10-20 HEAD 2>&1 | Out-Null
  $wip = (git -C $r stash create "pre-community wip snapshot 2026-10-20" 2>&1) | Select -Last 1
  if($wip -and $wip -match '^[0-9a-f]{40}$'){ git -C $r tag -f pre-community-2026-10-20-wip $wip 2>&1 | Out-Null; L "GIT $r head=$head wip_tag=$wip" } else { L "GIT $r head=$head (clean, no wip commit)" }
  $untracked = (git -C $r ls-files --others --exclude-standard 2>$null | Measure-Object).Count
  L "GIT $r untracked_files=$untracked (not in tags; left in place)"
}
# 3) cm-cli snapshot
$env:COMFYUI_PATH=$C
& "$C\.venv\Scripts\python.exe" "$C\custom_nodes\ComfyUI-Manager\cm-cli.py" save-snapshot --output "$P\comfy-snapshot-20261020.json" *>&1 | Out-File "$P\cm-cli.out" -Encoding utf8
L ("CMCLI exit=$LASTEXITCODE file=" + (Test-Path "$P\comfy-snapshot-20261020.json"))
# 4) env-lock (fresh) + copy of ALI-80 one
Copy-Item 'C:\Users\derek\5slock\runs\ali80-6clip-20261019\env-lock.txt' "$P\env-lock-ali80-20261019.txt" -Force
$out="$P\env-lock-20261020.txt"
"# env lock P1 $(Get-Date -Format 'yyyy-MM-dd HH:mm') CT, AlienPc" | Set-Content $out
"## ComfyUI core: $(git -C $C rev-parse HEAD 2>&1) $(git -C $C describe --tags 2>&1)" | Add-Content $out
Get-ChildItem "$C\custom_nodes" -Directory | % { if (Test-Path "$($_.FullName)\.git") { "$($_.Name) | $(git -C $_.FullName rev-parse HEAD 2>&1) | $(git -C $_.FullName remote get-url origin 2>&1)" } else { "$($_.Name) | no-git |" } } | Add-Content $out
"## sha256" | Add-Content $out
foreach ($f in "models\diffusion_models\10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors","models\text_encoders\qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors","models\vae\minimax_h3_video_vae_int8_convrot.safetensors","models\vae\minimax_h3_audio_vae_fp32.safetensors","models\loras\MysticXXX_MMH3-V4.safetensors","models\loras\HMNSFW-AIO-V2.5.safetensors","models\loras\hm_nsfw_mis_doggy_only_v16_r32_384_minimax-h3_epoch170.safetensors","models\loras\h3_antiburn_universal_v1.safetensors") { $h=Get-FileHash -Algorithm SHA256 "$C\$f"; "$($h.Hash.ToLower())  $((Get-Item "$C\$f").Length)  $f" | Add-Content $out }
"## pip freeze" | Add-Content $out
& "$C\.venv\Scripts\python.exe" -m pip freeze 2>&1 | Add-Content $out
L "ENVLOCK done"
# 5) tests
Set-Location C:\AI\director; & .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --no-header 2>&1 | Out-File "$P\director-pytest.log" -Encoding utf8
L ("DIRECTOR pytest: " + (Get-Content "$P\director-pytest.log" -Tail 1))
Set-Location C:\AI\forge-host; & .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --no-header 2>&1 | Out-File "$P\forgehost-pytest.log" -Encoding utf8
L ("FORGEHOST pytest: " + (Get-Content "$P\forgehost-pytest.log" -Tail 1))
L "P1 DONE"
