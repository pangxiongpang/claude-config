# Claude Code & ZCode 配置仓库

一键同步全部 AI 助手配置（Claude Code + ZCode），换电脑时只需把 repo 链接给 agent 即可自动恢复。

## 目录结构

```
claude-config/
├── claude/                       # Claude Code 配置
│   ├── user/                     #   → ~/.claude/
│   │   ├── CLAUDE.md             #     全局指令
│   │   ├── .mcp.json             #     MCP 服务器配置（token 已占位符化）
│   │   ├── skills/               #     全局基础技能（9个）
│   │   ├── agents/               #     自定义 agent 定义
│   │   ├── memory/               #     持久记忆
│   │   └── statusline.*          #     终端状态栏
│   └── projects/                 #   → <项目目录>/.claude/
│       └── yewu/                 #     业务项目
│           ├── CLAUDE.md         #     项目指令
│           ├── skills/           #     法律专项技能（12个 + watch）
│           ├── memory/           #     项目记忆
│           └── generate_ai_manual.py  # AI 配置手册生成器
├── zcode/                        # ZCode AI 助手配置
│   ├── user/                     #   → ~/.zcode/
│   │   ├── AGENTS.md             #     用户级指令
│   │   └── skills/               #     ZCode 技能
│   │       └── watch/            #     视频分析技能（真实文件）
│   └── projects/                 #   → <项目目录>/.zcode/
│       └── yewu/
│           └── Agent.md          #     项目级指令
├── sync_to_repo.py               # 一键同步脚本（本机 → 仓库）
├── install.sh                    # 一键安装脚本（仓库 → 新电脑）
├── SETUP.md                      # 给 agent 的安装指引
├── AI配置手册.md                  # 配置总览（自动生成）
└── README.md
```

## 换电脑快速恢复

```bash
# 1. 克隆仓库
git clone https://github.com/pangxiongpang/claude-config.git

# 2. 运行安装脚本
bash claude-config/install.sh -u <新用户名> -p <项目目标路径>

# 3. 填写北大法宝 token
# 编辑 ~/.claude/.mcp.json，把 YOUR_PKULAW_TOKEN 替换为真实 token
```

或直接给 agent 指令：

> "这是我的 AI 配置仓库 https://github.com/pangxiongpang/claude-config ，按照 SETUP.md 帮我同步配置。我的用户名是 xxx，项目放在 D:\xxx。"

## 日常同步（修改配置后）

在本机运行同步脚本，自动提交推送：
```bash
python D:\AI\claude-config\sync_to_repo.py
```

脚本会自动：
- 同步所有规范文件、skills、MCP 配置到仓库
- 将 .mcp.json 中的真实 token 替换为占位符（不上传密钥）
- 生成最新配置手册
- git commit + push

## 安全说明

`.mcp.json` 中的 API token 在入库时**自动替换为占位符** `YOUR_PKULAW_TOKEN`，不会上传真实密钥。新电脑安装后需手动填写一次。
