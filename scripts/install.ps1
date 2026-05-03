param(
  [string]$CloneDir,
  [string]$DestSkillsDir,
  [switch]$Help
)

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/warpdotdev/common-skills/"
$CleanupCloneDir = $false

function Show-Usage {
  Write-Output "Usage: ./install.ps1 [-CloneDir DIR] [-DestSkillsDir DIR]"
  Write-Output ""
  Write-Output "Clone common-skills and copy its skills into $DestSkillsDir."
  Write-Output ""
  Write-Output "Options:"
  Write-Output "  -CloneDir DIR   Directory to clone common-skills into."
  Write-Output "  -DestSkillsDir DIR   Directory to install skills into."
  Write-Output "  -Help           Show this help message."
}

function Should-OverwriteSkill {
  param([string]$SkillName)

  while ($true) {
    $response = Read-Host "Skill '$SkillName' already exists. Overwrite it? [y/N]"

    switch -Regex ($response) {
      '^(y|yes)$' {
        return $true
      }
      '^$|^(n|no)$' {
        return $false
      }
      default {
        Write-Output "Please answer yes or no."
      }
    }
  }
}

if ($Help) {
  if ([string]::IsNullOrWhiteSpace($DestSkillsDir)) {
    $DestSkillsDir = Join-Path $HOME ".agents\skills"
  }
  Show-Usage
  exit 0
}
if ([string]::IsNullOrWhiteSpace($DestSkillsDir)) {
  $DestSkillsDir = Join-Path $HOME ".agents\skills"
}

if ([string]::IsNullOrWhiteSpace($CloneDir)) {
  $CloneDir = Join-Path ([System.IO.Path]::GetTempPath()) ("common-skills." + [System.Guid]::NewGuid().ToString("N"))
  $CleanupCloneDir = $true
}

try {
  if (Test-Path -LiteralPath $CloneDir) {
    if (-not (Test-Path -LiteralPath $CloneDir -PathType Container)) {
      Write-Error "error: clone path already exists and is not a directory: $CloneDir"
      exit 1
    }

    if ((Get-ChildItem -LiteralPath $CloneDir -Force | Select-Object -First 1) -ne $null) {
      Write-Error "error: clone directory already exists and is not empty: $CloneDir"
      exit 1
    }
  }

  New-Item -ItemType Directory -Path $CloneDir -Force | Out-Null
  git clone --depth 1 $RepoUrl $CloneDir

  $SourceSkillsDir = Join-Path $CloneDir ".agents\skills"

  if (-not (Test-Path -LiteralPath $SourceSkillsDir -PathType Container)) {
    Write-Error "error: cloned repo does not contain $SourceSkillsDir"
    exit 1
  }

  New-Item -ItemType Directory -Path $DestSkillsDir -Force | Out-Null

  $InstalledSkills = @()
  $SkippedSkills = @()

  foreach ($SourceSkillDir in (Get-ChildItem -LiteralPath $SourceSkillsDir -Directory | Sort-Object Name)) {
    $SkillName = $SourceSkillDir.Name
    $DestSkillDir = Join-Path $DestSkillsDir $SkillName

    if (Test-Path -LiteralPath $DestSkillDir) {
      if (-not (Should-OverwriteSkill -SkillName $SkillName)) {
        $SkippedSkills += $SkillName
        continue
      }

      Remove-Item -LiteralPath $DestSkillDir -Recurse -Force
    }

    Copy-Item -LiteralPath $SourceSkillDir.FullName -Destination $DestSkillsDir -Recurse
    $InstalledSkills += $SkillName
  }

  Write-Output "Installed common-skills into $DestSkillsDir"

  if ($InstalledSkills.Count -gt 0) {
    Write-Output "Installed skills:"
    $InstalledSkills | ForEach-Object {
      Write-Output "  - $_"
    }
  } else {
    Write-Output "No skills installed."
  }

  if ($SkippedSkills.Count -gt 0) {
    Write-Output "Skipped existing skills:"
    $SkippedSkills | ForEach-Object {
      Write-Output "  - $_"
    }
  }
} finally {
  if ($CleanupCloneDir -and (Test-Path -LiteralPath $CloneDir)) {
    Remove-Item -LiteralPath $CloneDir -Recurse -Force
  }
}
