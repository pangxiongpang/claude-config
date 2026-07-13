# Claude Code & ZCode 配置仓库

一键同步全部 AI 助手配置（Claude Code + ZCode），换电脑时只需把 repo 链接给 agent 即可自动恢复。

## 目录结构

```
claude-config/
├── claude/                   # Claude Code 配置
│   ├── user/                 #   → ~/.claude/
│   │   ├── CLAUDE.md         #     全局指令
│   │   ├── .mcp.json         #     MCP 服务器配置
│   │   ├── skills/           #     全局基础技能
│   │   ├── agents/           #     自定义 agent 定义
│   │   ├── memory/           #     持久记忆
│   │   └── statusline.*      #     终端状态栏
│   └── projects/             #   → <项目目录>/.claude/
│       └── yewu/             #     业务项目
│           ├── CLAUDE.md     #     项目指令
│           ├── skills/       #     法律专项技能
│           ├── memory/       #     项目记忆
│           └── generate_ai_manual.py  # AI 配置手册生成器
├── zcode/                    # ZCode AI 助手配置
│   ├── user/                 #   → ~/.zcode/
│   │   ├── AGENTS.md         #     用户级指令
│   │   └── skills/           #     ZCode 技能
│   │       └── watch/        #     视频分析技能
│   └── projects/             #   → <项目目录>/.zcode/
│       └── yewu/
│           └── Agent.md      #     项目级指令
├── install.sh                # 一键安装脚本
├── SETUP.md                  # 给 agent 的安装指引
└── README.md
```

## 换电脑快速恢复

```bash
# 1. 克隆仓库
git clone https://github.com/pangxiongpang/claude-config.git

# 2. 运行安装脚本
bash claude-config/install.sh -u <新用户名> -p <项目目标路径>
```

或直接给 agent 指令：

> "这是我的 AI 配置仓库 https://github.com/pangxiongpang/claude-config ，按照 SETUP.md 帮我同步配置。我的用户名是 xxx，项目放在 D:\xxx。"

## 日常更新

修改任何配置后，提交并推送：
```bash
cd D:\AI\claude-config
git add -A
git commit -m "update: 同步配置"
git push
```

AI 配置手册更新后会自动提示同步到本仓库。
