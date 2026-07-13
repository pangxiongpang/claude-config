# SETUP — Agent 安装指引

> 新机器上把此仓库链接给 agent 后，agent 按本文件执行安装。

## 输入参数

用户需要提供：
1. **新电脑的用户名**（如 `zhangsan`，即 `C:\Users\` 下的目录名）
2. **业务项目目标路径**（如 `D:\案件` 或 `D:\AI\业务`）

可选：
3. **Obsidian 知识库路径**（如 `D:\obsidian\我的库`）

## 安装步骤

### Step 1: 克隆仓库

```bash
git clone <仓库URL> ~/claude-config
# 或放在其他位置
```

### Step 2: 运行安装脚本

```bash
bash ~/claude-config/install.sh -u <用户名> -p <项目目录>
```

脚本会自动：
- 复制 Claude 用户级配置到 `~/.claude/`
- 复制 Claude 项目级配置到 `<项目目录>/.claude/`
- 复制 ZCode 用户级配置到 `~/.zcode/`
- 复制 ZCode 项目级配置到 `<项目目录>/.zcode/`
- 替换所有路径（`11828` → 新用户名、`D:\AI\1.业务` → 新项目路径）
- 检测并更新 Playwright Chromium 路径

### Step 3: 手动确认

1. 运行 `cc switch` 恢复 settings.json（如果之前用 cc 保存过配置）
2. 检查北大法宝 MCP 连接是否正常
3. 确认项目 CLAUDE.md/Agent.md 中的路径已正确替换

### Step 4: 验证

启动一个新会话，检查：
- Claude Code: `/skills` 命令能看到所有 skill
- ZCode: 技能和指令是否正确加载
- 法律相关 skill 能否正常调用

## 安装脚本说明

`install.sh` 参数：
```
-u <用户名>      必填，Windows 用户名（如 zhangsan）
-p <项目目录>    必填，业务项目根目录（如 D:\案件）
-c <配置仓库目录> 可选，仓库本地路径（默认脚本所在目录）
-o <Obsidian目录> 可选，Obsidian 知识库路径
```

示例：
```bash
bash install.sh -u xiong-haochen -p "D:\法律业务" -o "D:\OneDrive\obsidian\知识库"
```
