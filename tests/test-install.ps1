# Smoke test for scripts/install.ps1. Runs the real installer against a throwaway directory, never
# your actual ~/.claude.
#
#   ./tests/test-install.ps1

$ErrorActionPreference = 'Stop'
$repo = Split-Path (Split-Path $PSCommandPath -Parent) -Parent
$script:fails = 0
function Pass($m) { Write-Host "  ok   $m" }
function Fail($m) { Write-Host "  FAIL $m"; $script:fails++ }
function Check($cond, $m) { if ($cond) { Pass $m } else { Fail $m } }

$sandbox = Join-Path ([IO.Path]::GetTempPath()) ("dp-test-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $sandbox | Out-Null

. (Join-Path $repo 'scripts\install.ps1')
Check (-not (Get-ChildItem $sandbox)) 'dot-sourcing has no side effects'

function Run($dir) { Install-DesignPipeline -RepoDir $repo -ClaudeDir $dir *> $null }
function Readable($dir) {
  $f = Join-Path $dir 'skills\design-pipeline\SKILL.md'
  (Test-Path $f) -and ((Get-Content $f -Raw) -match '(?m)^name: design-pipeline')
}

try {
  Write-Host '1. clean install'
  $c1 = Join-Path $sandbox 'clean'
  Run $c1
  Check (Readable $c1) 'skill readable through the install path'

  Write-Host '2. second run is idempotent'
  Run $c1
  Check (@(Get-ChildItem -Force (Join-Path $c1 'skills')).Count -eq 1) 'one entry under skills/'
  Check (-not (Test-Path (Join-Path $c1 '.backups'))) 'no backup made of our own link'
  Check (Test-Path (Join-Path $repo 'skills\design-pipeline\SKILL.md')) 'replacing the link left the repo intact'

  Write-Host '3. a real directory in place is moved outside skills/'
  $c3 = Join-Path $sandbox 'real'
  New-Item -ItemType Directory -Force -Path (Join-Path $c3 'skills\design-pipeline') | Out-Null
  Set-Content (Join-Path $c3 'skills\design-pipeline\SKILL.md') 'old'
  Run $c3
  Check (@(Get-ChildItem (Join-Path $c3 '.backups') -Filter 'design-pipeline.bak-*' -ErrorAction SilentlyContinue).Count -eq 1) 'backed up under .backups/'
  Check (-not (Get-ChildItem (Join-Path $c3 'skills') -Filter '*bak-*')) 'nothing named *.bak-* under skills/'
  Check (Readable $c3) 'new skill installed over it'

  Write-Host '4. a path with a space'
  $c4 = Join-Path $sandbox 'with space\claude'
  Run $c4
  Check (Readable $c4) 'installs under a path with a space'
} finally {
  # Remove the junctions first, so deleting the sandbox can never follow one into the repo.
  Get-ChildItem $sandbox -Recurse -Force -Attributes ReparsePoint -ErrorAction SilentlyContinue | ForEach-Object { $_.Delete() }
  Remove-Item $sandbox -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ''
if ($script:fails -eq 0) { Write-Host 'installer checks passed'; exit 0 } else { Write-Host "$script:fails problem(s) found"; exit 1 }
