param(
  [int]$Unit = 0,
  [string]$RunDir = 'ra-llms',
  [switch]$Paused
)

# Works out where the audio actually is right now and writes a script that moves
# the highlight to that point. The state file is only written every second, so
# the saved value is stale by up to a second; the age of the file is added back.

$ErrorActionPreference = 'Stop'

$pages = Join-Path $PSScriptRoot (Join-Path $RunDir 'pages')
if ($Unit -le 0) { throw "give -Unit N" }

$stateP = Join-Path $pages ("unit-{0}.state.json" -f $Unit)
$manP   = Join-Path $pages ("unit-{0}.json" -f $Unit)
if (-not (Test-Path $manP)) { throw "no page $Unit" }

$total = [double](Get-Content -Raw $manP | ConvertFrom-Json).total
$st = $null
if (Test-Path $stateP) { $st = Get-Content -Raw $stateP | ConvertFrom-Json }

$at = 0.0
$live = $false
if ($st) {
  $at = [double]$st.elapsed
  if ($st.playing) {
    $live = $true
    # ConvertFrom-Json turns the ISO stamp into a DateTime on some hosts, and leaves
    # it as a string on others, so accept both.
    $upd = if ($st.updatedAt -is [datetime]) { $st.updatedAt }
           else { [datetime]::Parse([string]$st.updatedAt, [Globalization.CultureInfo]::InvariantCulture) }
    $age = ((Get-Date) - $upd).TotalSeconds
    if ($age -lt 0) { $age = 0 }
    if ($age -gt 30) { $age = 30 }
    $at = [Math]::Min($total, $at + $age)
  }
}

$paused = if ($Paused) { $true } else { -not $live }

$js = @"
async (page) => {
  const SEC = $([Math]::Round($at, 2));
  const PAUSED = $($paused.ToString().ToLower());
  return JSON.stringify(await page.evaluate(([sec, paused]) => {
    if (!window.__raSet) return { error: 'engine not loaded' };
    window.__raSet(sec, paused);
    return { synced: sec, paused: paused };
  }, [SEC, PAUSED]));
}
"@

$out = Join-Path $PSScriptRoot ("sync-page-{0}.js" -f $Unit)
Set-Content -Path $out -Value $js -Encoding UTF8

$mm = [int][Math]::Floor($at / 60)
$ss = [int]([Math]::Floor($at) % 60)
Write-Host ("page {0}  {1}:{2:00} of {3:N2}s  ({4})" -f $Unit, $mm, $ss, $total, $(if ($paused) { 'paused' } else { 'live' }))
Write-Host ("wrote {0}" -f $out)
