# Installs skills/design-pipeline into %USERPROFILE%\.claude\skills as a USER-LEVEL skill, not a
# plugin: a plugin copy would appear beside the user-level one under a second, namespaced name.
#
#   ./scripts/install.ps1
#
# A directory junction works WITHOUT administrator rights or Developer Mode, unlike a symbolic link,
# and keeps the installed copy pointing at the repo so `git pull` updates it in place. Copy-Item is
# the last resort.
#
# Dot-sourcing this file has no side effects: it only defines a function, so
# tests/test-install.ps1 can point -ClaudeDir at a sandbox. It installs only when run directly.
# Mirrors scripts/install.sh.

function Install-DesignPipeline {
  [CmdletBinding()]
  param(
    [string] $RepoDir = (Split-Path (Split-Path $PSCommandPath -Parent) -Parent),
    [string] $ClaudeDir = (Join-Path $env:USERPROFILE '.claude')
  )

  Write-Host "`n==> Installing design-pipeline into $ClaudeDir"
  $src = Join-Path $RepoDir 'skills\design-pipeline'
  $dst = Join-Path $ClaudeDir 'skills\design-pipeline'
  if (-not (Test-Path $src)) { Write-Warning "missing $src"; return }
  New-Item -ItemType Directory -Force -Path (Join-Path $ClaudeDir 'skills') | Out-Null

  $existing = Get-Item $dst -Force -ErrorAction SilentlyContinue
  if ($existing) {
    if ($existing.LinkType) {
      # Our own junction: remove the link only. (Remove-Item -Recurse on a junction can follow it
      # into the repo on older PowerShell, so delete the reparse point itself.)
      $existing.Delete()
    } else {
      # Back up OUTSIDE <claude>\skills. A "design-pipeline.bak-<stamp>" folder left in there is
      # itself read as a skill, so Claude would list a second, stale copy under the backup's name.
      $bakDir = Join-Path $ClaudeDir '.backups'
      New-Item -ItemType Directory -Force -Path $bakDir | Out-Null
      $bak = Join-Path $bakDir "design-pipeline.bak-$((Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss'))"
      Write-Warning "$dst is not a link; moving it to $bak"
      Move-Item $dst $bak
    }
  }

  try {
    New-Item -ItemType Junction -Path $dst -Target $src -ErrorAction Stop | Out-Null
    Write-Host "    linked $dst"
  } catch {
    Copy-Item $src $dst -Recurse -Force
    Write-Host "    copied $dst (links unavailable: re-run this script after a git pull)"
  }

  # Report the dependencies, but never fail the install on them: a missing design skill limits a
  # phase of a run, it does not make this install wrong. `python`, not `python3`: on Windows
  # `python3` is often the Microsoft Store stub.
  if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "`n==> Dependency check"
    & python (Join-Path $dst 'scripts\preflight.py') --skills-root (Join-Path $ClaudeDir 'skills')
    # Without this the preflight's exit 1 leaks out as the install's own exit code: a caller that
    # exits with $LASTEXITCODE (GitHub's pwsh wrapper does) reports a good install as failed.
    $global:LASTEXITCODE = 0
  } else {
    Write-Warning 'no python found; run the preflight by hand'
  }
}

if ($MyInvocation.InvocationName -ne '.') { Install-DesignPipeline }
