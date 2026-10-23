# ALI-163 FINAL: extract per-clip m4a (audio track, stream copy) and 5 evenly spaced frames.
# CPU only, local files only, no -y, no URLs. ffmpeg/ffprobe from the AGENTS.md path.
$Bin = 'C:\Users\derek\AppData\Local\Microsoft\Winget\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin'
$FFmpeg = Join-Path $Bin 'ffmpeg.exe'
$Runs  = 'C:\AI\community\runs'
$Frams = 'C:\AI\community\notes\hc_final_frames'
New-Item -ItemType Directory -Force -Path $Frams | Out-Null

$ids = @('ali147_pool_hc_c1_s51100001','ali147_pool_hc_r1_s51130001','ali147_pool_hc_r2_s51130002','ali147_pool_hc_r4_s51130004','ali147_pool_hc_r5_s51130005','ali147_pool_hc_r6_s51130006')
foreach ($id in $ids) {
  $mp4 = Join-Path $Runs "$id\$id.mp4"
  if (-not (Test-Path -LiteralPath $mp4)) { Write-Output "MISSING $mp4"; continue }
  $m4a = Join-Path $Runs "$id\$id.m4a"
  if (-not (Test-Path -LiteralPath $m4a)) {
    & $FFmpeg -hide_banner -loglevel error -nostdin -i $mp4 -vn -c:a copy $m4a | Out-Null
  }
  Write-Output ("M4A " + $id + " " + (Test-Path -LiteralPath $m4a))
  # 5 evenly spaced timestamps, shared across clips so row 0 (OLD clip 1) and row 1 (NEW clip 1) line up
  $ts = @(0.50, 2.60, 5.00, 7.40, 9.60)
  $i = 0
  foreach ($t in $ts) {
    $out = Join-Path $Frams ("{0}_f{1}.png" -f $id, $i)
    if (-not (Test-Path -LiteralPath $out)) {
      & $FFmpeg -hide_banner -loglevel error -nostdin -ss $t -i $mp4 -frames:v 1 -an $out | Out-Null
    }
    Write-Output ("FRAME " + $id + " t=" + $t + " " + (Test-Path -LiteralPath $out))
    $i++
  }
}
