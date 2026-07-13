#!/usr/bin/env bash
# ============================================================
# Claude Code 配置安装脚本
# 用法: bash install.sh -u <用户名> -p <项目目录> [-c <配置仓库目录>] [-o <Obsidian目录>]
# ============================================================
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
ask()   { echo -e "${CYAN}[INPUT]${NC} $1"; }

# ---- 解析参数 ----
OLD_USERNAME="11828"
OLD_PROJECT_DIR_WIN="D:\\AI\\1.业务"
OLD_PROJECT_DIR_UNIX="D:/AI/1.业务"
OLD_PROJECT_DIR_GIT="/d/AI/1.业务"

NEW_USERNAME=""
PROJECT_DIR=""  # Unix-style, e.g. /d/案件
PROJECT_DIR_WIN=""  # Windows-style, e.g. D:\案件
CONFIG_REPO_DIR=""
OBSIDIAN_VAULT=""

while getopts "u:p:c:o:h" opt; do
  case $opt in
    u) NEW_USERNAME="$OPTARG" ;;
    p) PROJECT_DIR="$OPTARG" ;;
    c) CONFIG_REPO_DIR="$OPTARG" ;;
    o) OBSIDIAN_VAULT="$OPTARG" ;;
    h) echo "用法: bash install.sh -u <用户名> -p <项目目录> [-c <配置仓库目录>] [-o <Obsidian目录>]"
       exit 0 ;;
    *) error "未知参数"; exit 1 ;;
  esac
done

# ---- 参数校验 ----
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -z "$CONFIG_REPO_DIR" ] && CONFIG_REPO_DIR="$REPO_DIR"
[ -z "$NEW_USERNAME" ] && { ask "新电脑的用户名是什么？(如: zhangsan)"; read -r NEW_USERNAME; }
[ -z "$NEW_USERNAME" ] && { error "用户名不能为空"; exit 1; }

if [ -z "$PROJECT_DIR" ]; then
  ask "业务项目目标路径是什么？(如: /d/案件 或 D:/案件)"
  read -r PROJECT_DIR
fi
[ -z "$PROJECT_DIR" ] && { error "项目路径不能为空"; exit 1; }

# 标准化路径格式
PROJECT_DIR_UNIX="$(echo "$PROJECT_DIR" | sed 's|\\|/|g' | sed 's|\([a-zA-Z]\):|/\1|g')"  # D:\案件 → /d/案件
PROJECT_DIR_WIN="$(echo "$PROJECT_DIR_UNIX" | sed 's|^/\([a-z]\)|\1:|' | sed 's|/|\\|g')"  # /d/案件 → D:\案件
PROJECT_DIR_UNIX_SLASH="$(echo "$PROJECT_DIR_UNIX" | sed 's|/|\\/|g')"  # for sed

# Obsidian vault
USER_HOME_WIN="C:\\Users\\$NEW_USERNAME"
USER_HOME_UNIX="/c/Users/$NEW_USERNAME"
[ -z "$OBSIDIAN_VAULT" ] && OBSIDIAN_VAULT="$USER_HOME_WIN\\OneDrive\\obsidian\\胖胖熊"

echo ""
info "========================================"
info "  Claude Code & ZCode 配置安装"
info "========================================"
info "用户名:       $NEW_USERNAME"
info "项目目录:     $PROJECT_DIR_WIN"
info "配置仓库:     $CONFIG_REPO_DIR"
info "Obsidian:     $OBSIDIAN_VAULT"
info "========================================"
echo ""

# ---- 1. 安装 Claude 用户级配置 ----
info ">>> [Claude] 安装用户级配置到 ~/.claude/..."

TARGET_USER_DIR="$USER_HOME_UNIX/.claude"
mkdir -p "$TARGET_USER_DIR/skills" "$TARGET_USER_DIR/agents" "$TARGET_USER_DIR/memory" "$TARGET_USER_DIR/workflows"

cp "$CONFIG_REPO_DIR/claude/user/CLAUDE.md" "$TARGET_USER_DIR/"
cp "$CONFIG_REPO_DIR/claude/user/.mcp.json" "$TARGET_USER_DIR/" 2>/dev/null || warn ".mcp.json 不存在，跳过"
cp "$CONFIG_REPO_DIR/claude/user/statusline.sh" "$TARGET_USER_DIR/" 2>/dev/null || true
cp "$CONFIG_REPO_DIR/claude/user/statusline.py" "$TARGET_USER_DIR/" 2>/dev/null || true
[ -d "$CONFIG_REPO_DIR/claude/user/skills" ] && cp -r "$CONFIG_REPO_DIR/claude/user/skills/"* "$TARGET_USER_DIR/skills/" 2>/dev/null || true
[ -d "$CONFIG_REPO_DIR/claude/user/agents" ] && cp -r "$CONFIG_REPO_DIR/claude/user/agents/"* "$TARGET_USER_DIR/agents/" 2>/dev/null || true
[ -d "$CONFIG_REPO_DIR/claude/user/memory" ] && cp -r "$CONFIG_REPO_DIR/claude/user/memory/"* "$TARGET_USER_DIR/memory/" 2>/dev/null || true

info "[Claude] 用户级配置复制完成"

# ---- 2. 安装 Claude 项目级配置 ----
info ">>> [Claude] 安装项目级配置到 $PROJECT_DIR_UNIX/.claude/..."

TARGET_PROJECT_DIR="$PROJECT_DIR_UNIX/.claude"
mkdir -p "$TARGET_PROJECT_DIR/skills" "$TARGET_PROJECT_DIR/memory"

cp "$CONFIG_REPO_DIR/claude/projects/yewu/CLAUDE.md" "$TARGET_PROJECT_DIR/"
cp "$CONFIG_REPO_DIR/claude/projects/yewu/generate_ai_manual.py" "$TARGET_PROJECT_DIR/" 2>/dev/null || true
[ -d "$CONFIG_REPO_DIR/claude/projects/yewu/skills" ] && cp -r "$CONFIG_REPO_DIR/claude/projects/yewu/skills/"* "$TARGET_PROJECT_DIR/skills/" 2>/dev/null || true
[ -d "$CONFIG_REPO_DIR/claude/projects/yewu/memory" ] && cp -r "$CONFIG_REPO_DIR/claude/projects/yewu/memory/"* "$TARGET_PROJECT_DIR/memory/" 2>/dev/null || true

info "[Claude] 项目级配置复制完成"

# ---- 2b. 安装 ZCode 用户级配置 ----
info ">>> [ZCode] 安装用户级配置到 ~/.zcode/..."

TARGET_ZCODE_USER_DIR="$USER_HOME_UNIX/.zcode"
mkdir -p "$TARGET_ZCODE_USER_DIR/skills"

[ -f "$CONFIG_REPO_DIR/zcode/user/AGENTS.md" ] && cp "$CONFIG_REPO_DIR/zcode/user/AGENTS.md" "$TARGET_ZCODE_USER_DIR/"
[ -d "$CONFIG_REPO_DIR/zcode/user/skills" ] && cp -r "$CONFIG_REPO_DIR/zcode/user/skills/"* "$TARGET_ZCODE_USER_DIR/skills/" 2>/dev/null || true

info "[ZCode] 用户级配置复制完成"

# ---- 2c. 安装 ZCode 项目级配置 ----
info ">>> [ZCode] 安装项目级配置到 $PROJECT_DIR_UNIX/.zcode/..."

TARGET_ZCODE_PROJECT_DIR="$PROJECT_DIR_UNIX/.zcode"
mkdir -p "$TARGET_ZCODE_PROJECT_DIR"

[ -f "$CONFIG_REPO_DIR/zcode/projects/yewu/Agent.md" ] && cp "$CONFIG_REPO_DIR/zcode/projects/yewu/Agent.md" "$TARGET_ZCODE_PROJECT_DIR/"

info "[ZCode] 项目级配置复制完成"

# ---- 3. 路径替换 ----
info ">>> 替换路径占位符..."

# 在所有配置中替换路径（Claude + ZCode）
for target_dir in "$TARGET_USER_DIR" "$TARGET_PROJECT_DIR" "$TARGET_ZCODE_USER_DIR" "$TARGET_ZCODE_PROJECT_DIR"; do
  [ -d "$target_dir" ] || continue
  find "$target_dir" \( -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.json" \) -type f 2>/dev/null | while read -r f; do
    # Windows 路径: C:\Users\11828 → C:\Users\NEW_USERNAME
    sed -i "s/\\\\Users\\\\$OLD_USERNAME\\\\/\\\\Users\\\\$NEW_USERNAME\\\\/g" "$f" 2>/dev/null || true
    # Unix 路径: C:/Users/11828 → C:/Users/NEW_USERNAME
    sed -i "s|/c/Users/$OLD_USERNAME/|/c/Users/$NEW_USERNAME/|g" "$f" 2>/dev/null || true
    sed -i "s|C:/Users/$OLD_USERNAME/|C:/Users/$NEW_USERNAME/|g" "$f" 2>/dev/null || true
    # 项目路径: D:\AI\1.业务 → NEW_PROJECT_DIR
    sed -i "s/$OLD_PROJECT_DIR_WIN/$PROJECT_DIR_WIN/g" "$f" 2>/dev/null || true
    sed -i "s|$OLD_PROJECT_DIR_UNIX|$PROJECT_DIR_UNIX|g" "$f" 2>/dev/null || true
    # 替换 __USERNAME__ 和 __PROJECT_DIR__ 占位符（兼容模板版本）
    sed -i "s|__USERNAME__|$NEW_USERNAME|g" "$f" 2>/dev/null || true
    sed -i "s|__PROJECT_DIR__|$PROJECT_DIR_UNIX|g" "$f" 2>/dev/null || true
    sed -i "s|__CONFIG_REPO_DIR__|$CONFIG_REPO_DIR|g" "$f" 2>/dev/null || true
  done
done

info "路径替换完成"

# ---- 4. 更新 Playwright Chromium 路径 ----
info ">>> 检测 Playwright Chromium 路径..."

# 查找已安装的 Chromium
CHROME_PATH=$(find "$USER_HOME_UNIX/AppData/Local/ms-playwright" -name "chrome.exe" -path "*/chromium-*/chrome-win64/chrome.exe" 2>/dev/null | head -1)

if [ -n "$CHROME_PATH" ]; then
  CHROME_UNIX="$(echo "$CHROME_PATH" | sed 's|\\|/|g')"
  # 更新 law_validate.py 中的 Chromium 路径
  LAW_VALIDATE="$TARGET_PROJECT_DIR/skills/law-validation/law_validate.py"
  if [ -f "$LAW_VALIDATE" ]; then
    sed -i "s|MCP_CHROMIUM_PATH = \".*\"|MCP_CHROMIUM_PATH = \"$CHROME_UNIX\"|" "$LAW_VALIDATE"
    sed -i "s|PYTHON_CHROMIUM_PATH = \".*\"|PYTHON_CHROMIUM_PATH = \"$CHROME_UNIX\"|" "$LAW_VALIDATE"
    info "  ✓ 已更新 Chromium 路径: $CHROME_UNIX"
  fi
else
  warn "未找到 Playwright Chromium，安装后需手动运行: playwright install chromium"
  warn "然后手动更新 law_validate.py 中的 Chromium 路径"
fi

# ---- 5. 安装完成 ----
echo ""
info "========================================"
info "  安装完成！"
info "========================================"
echo ""
info "请手动执行以下操作:"
echo ""
echo "  1. 运行 cc switch 恢复 settings.json（如需要）"
echo "  2. 验证 MCP 连接:"
echo "     - 检查 ~/.claude/.mcp.json 中北大法宝 Token 是否有效"
echo "  3. 验证项目配置:"
echo "     - 确认 $PROJECT_DIR_WIN/.claude/CLAUDE.md 内容正确"
echo "  4. 安装 Python 依赖:"
echo "     - pip install playwright PyMuPDF ..."
echo ""
info "下次更新 AI 配置手册后，同步到本仓库:"
echo "  cd $CONFIG_REPO_DIR && git add -A && git commit -m \"chore: 同步配置\" && git push"
echo ""
