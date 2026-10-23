param(
  [int]$Unit = 0,
  [string]$RunDir = 'ra-llms',
  [double]$From = -1,
  [double]$Tick = 1,
  [switch]$Show,
  [switch]$Pause,
  [switch]$Reset,
  [switch]$Status
)

# Plays one page of the lesson at a time.
#
# Each page has its own audio file and its own manifest, both sliced out of the
# master recording, so the voice for a page can only ever run for that page.
# Nothing can roll on into the next unit. Finish a page, mark it, move on.
#
#   ra-page.ps1 -Status          where every page is up to
#   ra-page.ps1 -Unit 5          play page 5 from where it stopped
#   ra-page.ps1 -Unit 5 -From 0  play page 5 from the top
#   ra-page.ps1 -Unit 5 -Show    print page 5's position, change nothing
#   ra-page.ps1 -Pause           stop the running player cleanly
#   ra-page.ps1 -Unit 5 -Reset   forget page 5's position

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$run   = Join-Path $PSScriptRoot $RunDir
$pages = Join-Path $run 'pages'
if (-not (Test-Path $pages)) { throw "no pages folder at $pages - run split-pages.py first" }

function Read-State([int]$n) {
  $p = Join-Path $pages ("unit-{0}.state.json" -f $n)
  if (-not (Test-Path $p)) { return $null }
  try { return Get-Content -Raw $p | ConvertFrom-Json } catch { return $null }
}

function Save-State([int]$n, $h) {
  $h | ConvertTo-Json | Set-Content -Path (Join-Path $pages ("unit-{0}.state.json" -f $n)) -Encoding UTF8
}

function Page-Dur([int]$n) {
  $j = Get-Content -Raw (Join-Path $pages ("unit-{0}.json" -f $n)) | ConvertFrom-Json
  return [double]$j.total
}

function Page-Slug([int]$n) {
  $j = Get-Content -Raw (Join-Path $pages ("unit-{0}.json" -f $n)) | ConvertFrom-Json
  return [string]$j.units[0].slug
}

function Page-Nums {
  $out = @()
  foreach ($f in Get-ChildItem -Path $pages -Filter 'unit-*.json' | Sort-Object Name) {
    if ($f.Name -match 'unit-(\d+)\.json$') { $out += [int]$Matches[1] }
  }
  return $out
}

function Clock([double]$s) {
  return ('{0}:{1:00}' -f [int][Math]::Floor($s / 60), [int]([Math]::Floor($s) % 60))
}

if ($Status) {
  Write-Host ("{0,4}  {1,8}  {2,8}  {3,-9}  {4}" -f 'page', 'length', 'at', 'state', 'slug')
  foreach ($n in Page-Nums) {
    $d = Page-Dur $n
    $st = Read-State $n
    $at = if ($st) { [double]$st.elapsed } else { 0.0 }
    $state = if (-not $st) { 'not started' }
             elseif ($st.finished) { 'done' }
             elseif ($st.playing) { 'playing' }
             else { 'paused' }
    Write-Host ("{0,4}  {1,8}  {2,8}  {3,-9}  {4}" -f $n, (Clock $d), (Clock $at), $state, (Page-Slug $n))
  }
  exit 0
}

if ($Unit -le 0) { throw "give -Unit N, or -Status to see the pages" }

$wavP = Join-Path $pages ("unit-{0}.wav" -f $Unit)
if (-not (Test-Path $wavP)) { throw "no audio for page $Unit at $wavP" }

$total   = Page-Dur $Unit
$slug    = Page-Slug $Unit
$stateP  = Join-Path $pages ("unit-{0}.state.json" -f $Unit)
$pauseP  = Join-Path $pages ("unit-{0}.pause" -f $Unit)
$remP    = Join-Path $pages ("unit-{0}.remainder.wav" -f $Unit)

if ($Reset) {
  Remove-Item $stateP, $pauseP, $remP -Force -ErrorAction SilentlyContinue
  Write-Host ("page {0} reset" -f $Unit)
  exit 0
}

if ($Pause) {
  New-Item -ItemType File -Path $pauseP -Force | Out-Null
  Write-Host "pause requested"
  exit 0
}

$st = Read-State $Unit
$at = if ($st) { [double]$st.elapsed } else { 0.0 }

if ($Show) {
  Write-Host ("page {0}  {1}  of {2}  ({3})" -f $Unit, (Clock $at), (Clock $total), $slug)
  if ($st -and $st.finished) { Write-Host "done" } elseif ($st -and $st.playing) { Write-Host "playing" } else { Write-Host "paused" }
  exit 0
}

if ($From -ge 0) { $at = $From }
$at = [Math]::Max(0.0, [Math]::Min($total, $at))

if ($at -ge $total - 0.5) {
  Write-Host ("page {0} already finished. use -From 0 to replay." -f $Unit)
  exit 0
}

Remove-Item $pauseP -Force -ErrorAction SilentlyContinue

if ($at -gt 0.05) {
  & ffmpeg -hide_banner -loglevel error -y -ss $at -t ($total - $at) -i $wavP -c:a pcm_s16le -ar 24000 -ac 1 $remP 2>$null
  $play = $remP
} else {
  $play = $wavP
}
if (-not (Test-Path $play)) { throw "failed to prepare audio" }

Save-State $Unit ([pscustomobject]@{
  unit = $Unit; elapsed = [Math]::Round($at, 2); playing = $true
  finished = $false; updatedAt = (Get-Date).ToString('o')
})

Write-Host ("page {0}  {1}  of {2}  {3}" -f $Unit, (Clock $at), (Clock $total), $slug)

$player = New-Object System.Media.SoundPlayer $play
$sw = [Diagnostics.Stopwatch]::StartNew()
$player.Play()

$lastSave = 0.0
$stopped = $false
while ($sw.Elapsed.TotalSeconds -lt ($total - $at) - 0.2) {
  Start-Sleep -Milliseconds 500
  if (Test-Path $pauseP) { $stopped = $true; break }
  if (($sw.Elapsed.TotalSeconds - $lastSave) -ge $Tick) {
    $lastSave = $sw.Elapsed.TotalSeconds
    Save-State $Unit ([pscustomobject]@{
      unit = $Unit; elapsed = [Math]::Round($at + $lastSave, 2); playing = $true
      finished = $false; updatedAt = (Get-Date).ToString('o')
    })
  }
}

$player.Stop()
$player.Dispose()
$sw.Stop()

$now = [Math]::Round([Math]::Min($total, $at + $sw.Elapsed.TotalSeconds), 2)

if ($stopped) {
  Remove-Item $pauseP -Force -ErrorAction SilentlyContinue
  Save-State $Unit ([pscustomobject]@{
    unit = $Unit; elapsed = $now; playing = $false; finished = $false
    updatedAt = (Get-Date).ToString('o')
  })
  Write-Host ("paused at {0}  ({1:N2}s)" -f (Clock $now), $now)
  exit 0
}

Save-State $Unit ([pscustomobject]@{
  unit = $Unit; elapsed = $total; playing = $false; finished = $true
  updatedAt = (Get-Date).ToString('o')
})
Remove-Item $remP -Force -ErrorAction SilentlyContinue
Write-Host ("page {0} done - mark it as completed" -f $Unit)
