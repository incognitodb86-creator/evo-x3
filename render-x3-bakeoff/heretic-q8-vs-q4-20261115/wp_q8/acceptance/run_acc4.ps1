# acc4 batch (dry only, never --queue). Preflight one sample per group first; abort unless READY or an intended hard stop.
# Usage:
#   .\run_acc4.ps1                         # preflight then all suites
#   .\run_acc4.ps1 -FailedOnly             # preflight then the acc4 + PM FAIL rerun set
#   .\run_acc4.ps1 -SkipPreflight -FailedOnly
param(
  [string]$Root = "C:\AI\community\runs\wp_accept4d_20261113",
  [string]$SharedState = "C:\AI\render\writer_pipeline\acceptance\shared_state_acc4d",
  [string]$PriorRoot = "C:\AI\community\runs\wp_accept4c_20261113",
  [switch]$FailedOnly,
  [switch]$SkipPreflight
)
$ErrorActionPreference = "Continue"
$acc = "C:\AI\render\writer_pipeline\acceptance\wp_accept.py"
$py  = "C:\Program Files\Python312\python.exe"
New-Item -ItemType Directory -Force $Root | Out-Null
$log = Join-Path $Root "batch.log"
"start $(Get-Date -Format s) FailedOnly=$FailedOnly" | Out-File $log -Encoding utf8

function Invoke-Suite {
  param([string]$Suite, [string]$Out, [string]$Only = "", [string]$Prior = "")
  $env:PYTHONIOENCODING = "utf-8"
  $cmd = "`"$py`" `"$acc`" $Suite `"$Out`" --arm A --fresh --shared-state `"$SharedState`""
  if ($Only)  { $cmd += " --only `"$Only`"" }
  if ($Prior) { $cmd += " --prior-root `"$Prior`"" }
  cmd /c "$cmd >> `"$log`" 2>&1"
  return $LASTEXITCODE
}

# Preflight: one sample per group. Youth is the only intended hard stop (not in this list).
$preflight = @(
  @{ Suite = "modes";    Case = "m09_gonzo";        Name = "cowgirl" },
  @{ Suite = "mmf";      Case = "mmf3_s3_still";    Name = "mmf_still" },
  @{ Suite = "mmf";      Case = "mmf1_generated";   Name = "mmf_generated" },
  @{ Suite = "lostfeat"; Case = "lf21_male_solo";   Name = "male_solo" },
  @{ Suite = "lostfeat"; Case = "lf22_ffm";         Name = "ffm" },
  @{ Suite = "fantasy";  Case = "f4_carry";         Name = "former_low_score" }
)
if (-not $SkipPreflight) {
  $pfRoot = Join-Path $Root "preflight"
  New-Item -ItemType Directory -Force $pfRoot | Out-Null
  "== preflight $(Get-Date -Format s)" | Out-File $log -Append -Encoding utf8
  $failed = @()
  foreach ($g in $preflight) {
    $out = Join-Path $pfRoot $g.Suite
    Invoke-Suite -Suite $g.Suite -Out $out -Only $g.Case | Out-Null
    $sum = Join-Path $out "summary.json"
    $status = "MISSING"
    if (Test-Path $sum) {
      $status = & $py -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); rows=d.get('rows') or []; print((rows[0].get('status') if rows else 'EMPTY') or 'NONE')" $sum
    }
    "== preflight $($g.Name) $($g.Case) status=$status" | Out-File $log -Append -Encoding utf8
    if ($status -ne "READY") { $failed += "$($g.Name)/$($g.Case)=$status" }
  }
  if ($failed.Count -gt 0) {
    "PREFLIGHT_FAIL $($failed -join '; ')" | Out-File $log -Append -Encoding utf8
    Write-Error "PREFLIGHT_FAIL: $($failed -join '; ')"
    exit 2
  }
  "PREFLIGHT_OK $(Get-Date -Format s)" | Out-File $log -Append -Encoding utf8
}

# Rerun map: acc4 NOT_READY plus PM FAILs, plus long-scene parents so --continue works.
$rerun = @{
  four     = "missionary,talk"
  modes    = "m03_talk,m04_strip,m07_forced,m09_gonzo,m13_defeat,m14_toy_solo,m16_threesome,m17_spoof"
  combos   = "c1a_pov_doggy,c1b_pov_continue,c2_mmf_spitroast,c3a_strip,c3b_sex_after_strip,c7_restraint_forced,c9_unknown"
  mmf      = "mmf1_generated,mmf2_continued,mmf3_s3_still"
  pi       = "pi_missionary_f002"
  t1       = "t1_c1,t1_c2,t1_c3"
  t2single = "t2s_c1_talk,t2s_c2_reveal,t2s_c3_strip,t2s_c4_transition,t2s_c5_act"
  t2multi  = "t2m_c1_talk,t2m_c2_reveal,t2m_c3_strip,t2m_c4_transition,t2m_c5_act,t2m_c6_ext"
  fantasy  = "f2a_orc,f2b_orc_ext,f3_fairy,f4_carry,f5_youth_seed"
  lostfeat = "lf03_fairy,lf04_giant_carry,lf05_tentacles,lf06_telekinesis,lf08_bts,lf12_ff_cunni,lf13_ff_scissor,lf18_piledriver,lf19_reverse,lf21_male_solo,lf22_ffm,lf23_mmf_double_bj,lf24_handjob,lf25_sleep,lf26_hypno,lf27_mdma"
}
$suites = if ($FailedOnly) { @('four','modes','combos','mmf','pi','t1','t2single','t2multi','fantasy','lostfeat') } else { @('four','modes','combos','mmf','pi','t1','t2single','t2multi','fantasy','lostfeat') }

foreach ($s in $suites) {
  "== $s $(Get-Date -Format s)" | Out-File $log -Append -Encoding utf8
  $out = Join-Path $Root $s
  $prior = Join-Path $PriorRoot $s
  if ($FailedOnly) {
    Invoke-Suite -Suite $s -Out $out -Only $rerun[$s] -Prior $prior | Out-Null
  } else {
    Invoke-Suite -Suite $s -Out $out | Out-Null
  }
}

# Long-scene gap: 30+ clip plan (no writer calls; dry plan only)
$planDir = Join-Path $Root "t3plan"
New-Item -ItemType Directory -Force $planDir | Out-Null
& $py "C:\AI\render\writer_pipeline\acceptance\t3_plan.py" $planDir
"T3_PLAN written $(Get-Date -Format s)" | Out-File $log -Append -Encoding utf8
"done $(Get-Date -Format s)" | Out-File $log -Append -Encoding utf8

