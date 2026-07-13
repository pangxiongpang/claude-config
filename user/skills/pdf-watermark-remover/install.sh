#!/bin/sh
# PDF Watermark Remover - Cross-platform installer
# Auto-detects platform and installs to appropriate location

set -e

SKILL_NAME="pdf-watermark-remover"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect platform
detect_platform() {
    if [ -d "$HOME/.claude" ]; then
        echo "claude-code"
    elif [ -d "$HOME/.cursor" ] || [ -d ".cursor" ]; then
        echo "cursor"
    elif [ -d "$HOME/.agents" ]; then
        echo "universal"
    elif [ -d ".github" ]; then
        echo "copilot"
    elif [ -d ".windsurf" ] || [ -d "$HOME/.windsurf" ]; then
        echo "windsurf"
    elif [ -d ".clinerules" ]; then
        echo "cline"
    elif [ -d "$HOME/.gemini" ]; then
        echo "gemini"
    elif [ -d ".kiro" ]; then
        echo "kiro"
    elif [ -d ".trae" ]; then
        echo "trae"
    elif [ -d "$HOME/.config/goose" ]; then
        echo "goose"
    elif [ -d "$HOME/.config/opencode" ]; then
        echo "opencode"
    elif [ -d ".roo" ]; then
        echo "roo-code"
    elif [ -d ".agents" ]; then
        echo "antigravity"
    else
        echo "universal"
    fi
}

# Get install path for platform
get_install_path() {
    local platform="$1"
    local user_level="${2:-false}"

    case "$platform" in
        claude-code)
            if [ "$user_level" = "true" ]; then
                echo "$HOME/.claude/skills/$SKILL_NAME"
            else
                echo ".claude/skills/$SKILL_NAME"
            fi
            ;;
        cursor)
            if [ "$user_level" = "true" ]; then
                echo "$HOME/.cursor/rules/$SKILL_NAME"
            else
                echo ".cursor/rules/$SKILL_NAME"
            fi
            ;;
        copilot)
            echo ".github/skills/$SKILL_NAME"
            ;;
        windsurf)
            if [ "$user_level" = "true" ]; then
                echo "$HOME/.windsurf/rules/$SKILL_NAME"
            else
                echo ".windsurf/rules/$SKILL_NAME"
            fi
            ;;
        cline)
            echo ".clinerules/$SKILL_NAME"
            ;;
        codex|universal|antigravity)
            if [ "$user_level" = "true" ]; then
                echo "$HOME/.agents/skills/$SKILL_NAME"
            else
                echo ".agents/skills/$SKILL_NAME"
            fi
            ;;
        gemini)
            echo "$HOME/.gemini/skills/$SKILL_NAME"
            ;;
        kiro)
            echo ".kiro/skills/$SKILL_NAME"
            ;;
        trae)
            echo ".trae/rules/$SKILL_NAME"
            ;;
        goose)
            echo "$HOME/.config/goose/skills/$SKILL_NAME"
            ;;
        opencode)
            echo "$HOME/.config/opencode/skills/$SKILL_NAME"
            ;;
        roo-code)
            echo ".roo/rules/$SKILL_NAME"
            ;;
        *)
            if [ "$user_level" = "true" ]; then
                echo "$HOME/.agents/skills/$SKILL_NAME"
            else
                echo ".agents/skills/$SKILL_NAME"
            fi
            ;;
    esac
}

# Install skill
install_skill() {
    local platform="$1"
    local install_path="$2"

    info "Installing $SKILL_NAME for $platform..."

    # Create directory
    mkdir -p "$(dirname "$install_path")"

    # Copy files
    cp -R "$SCRIPT_DIR/"* "$install_path/"

    # Make scripts executable
    chmod +x "$install_path/scripts/"*.py 2>/dev/null || true
    chmod +x "$install_path/install.sh" 2>/dev/null || true

    info "Installed to: $install_path"
}

# Main installation
main() {
    local platform=""
    local user_level="false"
    local dry_run="false"
    local install_all="false"

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --platform)
                platform="$2"
                shift 2
                ;;
            --user)
                user_level="true"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            --all)
                install_all="true"
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --platform PLATFORM  Install for specific platform"
                echo "  --user               Install to user-level directory"
                echo "  --dry-run            Show what would be installed"
                echo "  --all                Install to all detected platforms"
                echo "  --help               Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Auto-detect platform if not specified
    if [ -z "$platform" ]; then
        platform=$(detect_platform)
        info "Auto-detected platform: $platform"
    fi

    # Get install path
    local install_path
    install_path=$(get_install_path "$platform" "$user_level")

    # Dry run mode
    if [ "$dry_run" = "true" ]; then
        info "Dry run mode - would install to:"
        echo "  $install_path"
        exit 0
    fi

    # Install
    install_skill "$platform" "$install_path"

    # Post-install instructions
    echo ""
    info "Installation complete!"
    echo ""
    echo "To use the skill, open a new session and type:"
    echo ""
    echo "  /pdf-watermark-remover Remove watermark from document.pdf"
    echo ""
    echo "Or simply:"
    echo ""
    echo "  Remove watermark from this PDF"
    echo ""

    # Check prerequisites
    info "Checking prerequisites..."
    if command -v python3 >/dev/null 2>&1; then
        python3 "$install_path/scripts/remove_watermark.py" --check-prereqs
    elif command -v python >/dev/null 2>&1; then
        python "$install_path/scripts/remove_watermark.py" --check-prereqs
    else
        warn "Python not found. Please install Python 3.7+ and run:"
        echo "  pip install PyMuPDF"
    fi
}

# Run main function
main "$@"