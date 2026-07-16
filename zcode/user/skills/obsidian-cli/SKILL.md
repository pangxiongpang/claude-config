---
name: obsidian-cli
description: Interact with Obsidian vaults using the Obsidian CLI to read, create, search, and manage notes, tasks, properties, and more. Also supports plugin and theme development with commands to reload plugins, run JavaScript, capture errors, take screenshots, and inspect the DOM. Use when the user asks to interact with their Obsidian vault, manage notes, search vault content, perform vault operations from the command line, or develop and debug Obsidian plugins and themes.
---

# Obsidian CLI

Use the `obsidian` CLI to interact with a running Obsidian instance. Requires Obsidian to be open.

## Command reference

Run `obsidian help` to see all available commands. This is always up to date. Full docs: https://help.obsidian.md/cli

## Syntax

**Parameters** take a value with `=`. Quote values with spaces:

```bash
obsidian create name="My Note" content="Hello world"
```

**Flags** are boolean switches with no value:

```bash
obsidian create name="My Note" silent overwrite
```

For multiline content use `\n` for newline and `\t` for tab.

## File targeting

Many commands accept `file` or `path` to target a file. Without either, the active file is used.

- `file=<name>` — resolves like a wikilink (name only, no path or extension needed)
- `path=<path>` — exact path from vault root, e.g. `folder/note.md`

## Vault targeting

Commands target the most recently focused vault by default. Use `vault=<name>` as the first parameter to target a specific vault:

```bash
obsidian vault="My Vault" search query="test"
```

## Common patterns

```bash
obsidian read file="My Note"
obsidian create name="New Note" content="# Hello" template="Template" silent
obsidian append file="My Note" content="New line"
obsidian search query="search term" limit=10
obsidian daily:read
obsidian daily:append content="- [ ] New task"
obsidian property:set name="status" value="done" file="My Note"
obsidian tasks daily todo
obsidian tags sort=count counts
obsidian backlinks file="My Note"
```

Use `--copy` on any command to copy output to clipboard. Use `silent` to prevent files from opening. Use `total` on list commands to get a count.

---

## Writing large files (>4000 bytes)

`create` 和 `append` 的 `content=` 参数有约 **4000 字节**的长度上限。超出此限制会静默失败（退出码 0、提示成功，但文件实际未写入或未追加）。**单次 `content=` 必须控制在 4000 字节以内。**

### 分块写入策略（强制用于大文件）

将内容按行数拆分为每块 ≤4000 字节，`create` 首块后逐块 `append`：

```bash
SRC="/tmp/source.md"          # 源文件（临时文件）
TARGET="folder/target.md"     # vault 内目标路径
VAULT="胖胖熊"

# 块1: create 首块（≤4000 字节）
obsidian vault="$VAULT" create path="$TARGET" \
  content="$(awk 'NR>=1 && NR<=30' "$SRC")" overwrite silent
sleep 1

# 块2-N: append 后续块
obsidian vault="$VAULT" append path="$TARGET" \
  content="$(awk 'NR>=31 && NR<=60' "$SRC")" silent
sleep 1

obsidian vault="$VAULT" append path="$TARGET" \
  content="$(awk 'NR>=61 && NR<=99' "$SRC")" silent
```

### 注意事项

| 要点 | 说明 |
|------|------|
| `silent` | **必须加**。不加则每次操作弹出 Obsidian 窗口/打开文件 |
| `sleep 1` | create 与 append 之间留 1 秒给 Obsidian 同步；不加可能导致 append 丢失参数 |
| `awk 'NR>=a && NR<=b'` | 精确提取行范围。`head\|tail` 管道可能丢失段落间空行 |
| Obsidian 运行状态 | **必须已打开**且目标 vault 已加载 |
| 块边界空行 | append 可能在块边界丢失段落间空行（~0.04% 内容影响，不影响渲染） |

### 完整示例：写入 5000+ 字文件

```bash
# 准备源内容到临时文件
cat > /tmp/my_note.md <<'EOF'
# Title

... 5000+ 字内容 ...

EOF

# 确认 Obsidian 已打开、目标 vault 已加载
# 然后分块写入：
obsidian vault="胖胖熊" create path="未命名.md" \
  content="$(awk 'NR>=1 && NR<=25' /tmp/my_note.md)" overwrite silent
sleep 1
obsidian vault="胖胖熊" append path="未命名.md" \
  content="$(awk 'NR>=26 && NR<=50' /tmp/my_note.md)" silent
sleep 1
obsidian vault="胖胖熊" append path="未命名.md" \
  content="$(awk 'NR>=51 && NR<=75' /tmp/my_note.md)" silent
sleep 1
obsidian vault="胖胖熊" append path="未命名.md" \
  content="$(awk 'NR>=76 && NR<=99' /tmp/my_note.md)" silent

rm /tmp/my_note.md
```

---

## Plugin development

### Develop/test cycle

After making code changes to a plugin or theme, follow this workflow:

1. **Reload** the plugin to pick up changes:
   ```bash
   obsidian plugin:reload id=my-plugin
   ```
2. **Check for errors** — if errors appear, fix and repeat from step 1:
   ```bash
   obsidian dev:errors
   ```
3. **Verify visually** with a screenshot or DOM inspection:
   ```bash
   obsidian dev:screenshot path=screenshot.png
   obsidian dev:dom selector=".workspace-leaf" text
   ```
4. **Check console output** for warnings or unexpected logs:
   ```bash
   obsidian dev:console level=error
   ```

### Additional developer commands

Run JavaScript in the app context:

```bash
obsidian eval code="app.vault.getFiles().length"
```

Inspect CSS values:

```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```

Toggle mobile emulation:

```bash
obsidian dev:mobile on
```

Run `obsidian help` to see additional developer commands including CDP and debugger controls.
