# PDF Watermark Remover - Windows PowerShell Installer
# Auto-detects platform and installs to appropriate location

param(
    [string]$Platform = "",
    [switch]$User,
    [switch]$DryRun,
    [switch]$All,
    [switch]$Help
)

$SKILL_NAME = "pdf-watermark-remover"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Helper functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Detect platform
function Get-Platform {
    if (Test-Path "$env:USERPROFILE\.claude") {
        return "claude-code"
    }
    elseif (Test-Path "$env:USERPROFILE\.cursor" -or Test-Path ".cursor") {
        return "cursor"
    }
    elseif (Test-Path "$env:USERPROFILE\.agents") {
        return "universal"
    }
    elseif (Test-Path ".github") {
        return "copilot"
    }
    elseif (Test-Path ".windsurf" -or Test-Path "$env:USERPROFILE\.windsurf") {
        return "windsurf"
    }
    elseif (Test-Path ".clinerules") {
        return "cline"
    }
    elseif (Test-Path "$env:USERPROFILE\.gemini") {
        return "gemini"
    }
    elseif (Test-Path ".kiro") {
        return "kiro"
    }
    elseif (Test-Path ".trae") {
        return "trae"
    }
    elseif (Test-Path "$env:USERPROFILE\.config\goose") {
        return "goose"
    }
    elseif (Test-Path "$env:USERPROFILE\.config\opencode") {
        return "opencode"
    }
    elseif (Test-Path ".roo") {
        return "roo-code"
    }
    elseif (Test-Path ".agents") {
        return "antigravity"
    }
    else {
        return "universal"
    }
}

# Get install path for platform
function Get-InstallPath {
    param(
        [string]$Platform,
        [bool]$UserLevel = $false
    )

    switch ($Platform) {
        "claude-code" {
            if ($UserLevel) {
                return "$env:USERPROFILE\.claude\skills\$SKILL_NAME"
            }
            else {
                return ".claude\skills\$SKILL_NAME"
            }
        }
        "cursor" {
            if ($UserLevel) {
                return "$env:USERPROFILE\.cursor\rules\$SKILL_NAME"
            }
            else {
                return ".cursor\rules\$SKILL_NAME"
            }
        }
        "copilot" {
            return ".github\skills\$SKILL_NAME"
        }
        "windsurf" {
            if ($UserLevel) {
                return "$env:USERPROFILE\.windsurf\rules\$SKILL_NAME"
            }
            else {
                return ".windsurf\rules\$SKILL_NAME"
            }
        }
        "cline" {
            return ".clinerules\$SKILL_NAME"
        }
        { $_ -in "codex", "universal", "antigravity" } {
            if ($UserLevel) {
                return "$env:USERPROFILE\.agents\skills\$SKILL_NAME"
            }
            else {
                return ".agents\skills\$SKILL_NAME"
            }
        }
        "gemini" {
            return "$env:USERPROFILE\.gemini\skills\$SKILL_NAME"
        }
        "kiro" {
            return ".kiro\skills\$SKILL_NAME"
        }
        "trae" {
            return ".trae\rules\$SKILL_NAME"
        }
        "goose" {
            return "$env:USERPROFILE\.config\goose\skills\$SKILL_NAME"
        }
        "opencode" {
            return "$env:USERPROFILE\.config\opencode\skills\$SKILL_NAME"
        }
        "roo-code" {
            return ".roo\rules\$SKILL_NAME"
        }
        default {
            if ($UserLevel) {
                return "$env:USERPROFILE\.agents\skills\$SKILL_NAME"
            }
            else {
                return ".agents\skills\$SKILL_NAME"
            }
        }
    }
}

# Install skill
function Install-Skill {
    param(
        [string]$Platform,
        [string]$InstallPath
    )

    Write-Info "Installing $SKILL_NAME for $Platform..."

    # Create directory
    $parentDir = Split-Path -Parent $InstallPath
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    # Copy files
    Copy-Item -Path "$SCRIPT_DIR\*" -Destination $InstallPath -Recurse -Force

    Write-Info "Installed to: $InstallPath"
}

# Main installation
function Main {
    # Parse arguments
    if ($Help) {
        Write-Host "Usage: .\install.ps1 [OPTIONS]"
        Write-Host ""
        Write-Host "Options:"
        Write-Host "  -Platform PLATFORM  Install for specific platform"
        Write-Host "  -User               Install to user-level directory"
        Write-Host "  -DryRun             Show what would be installed"
        Write-Host "  -All                Install to all detected platforms"
        Write-Host "  -Help               Show this help message"
        return
    }

    # Auto-detect platform if not specified
    if ([string]::IsNullOrEmpty($Platform)) {
        $Platform = Get-Platform
        Write-Info "Auto-detected platform: $Platform"
    }

    # Get install path
    $installPath = Get-InstallPath -Platform $Platform -UserLevel $User

    # Dry run mode
    if ($DryRun) {
        Write-Info "Dry run mode - would install to:"
        Write-Host "  $installPath"
        return
    }

    # Install
    Install-Skill -Platform $Platform -InstallPath $installPath

    # Post-install instructions
    Write-Host ""
    Write-Info "Installation complete!"
    Write-Host ""
    Write-Host "To use the skill, open a new session and type:"
    Write-Host ""
    Write-Host "  /pdf-watermark-remover Remove watermark from document.pdf"
    Write-Host ""
    Write-Host "Or simply:"
    Write-Host ""
    Write-Host "  Remove watermark from this PDF"
    Write-Host ""

    # Check prerequisites
    Write-Info "Checking prerequisites..."
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    }

    if ($pythonCmd) {
        & $pythonCmd.Source "$installPath\scripts\remove_watermark.py" --check-prereqs
    }
    else {
        Write-Warn "Python not found. Please install Python 3.7+ and run:"
        Write-Host "  pip install PyMuPDF"
    }
}

# Run main function
Main