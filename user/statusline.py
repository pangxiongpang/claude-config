import sys, json, os

# Force UTF-8 on Windows to avoid GBK encoding issues
if os.name == "nt":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

data = json.load(sys.stdin)

# --- model ---
model = (data.get("model") or {}).get("display_name") or (data.get("model") or {}).get("id", "?")

# --- context ---
cw = data.get("context_window") or {}
used_pct = cw.get("used_percentage") or 0
in_tok = cw.get("total_input_tokens") or 0
out_tok = cw.get("total_output_tokens") or 0

# --- cost ---
cost = data.get("total_cost_usd")
if cost is None:
    ml = model.lower()
    if "deepseek" in ml and "v4" in ml:
        ri, ro = (0.27, 1.10) if "flash" in ml else (0.55, 2.19)
    elif "claude" in ml:
        if "sonnet" in ml:
            ri, ro = 3.0, 15.0
        elif "opus" in ml:
            ri, ro = 15.0, 75.0
        elif "haiku" in ml:
            ri, ro = 0.80, 4.0
        else:
            ri, ro = 3.0, 15.0
    else:
        ri, ro = 3.0, 15.0
    cost = round((in_tok * ri + out_tok * ro) / 1_000_000, 6)

# --- nothing yet ---
if in_tok == 0 and out_tok == 0:
    print(f"\033[1m{model}\033[0m | no usage")
    sys.exit(0)

# --- formatters ---
def bar(pct):
    fill = min(round(pct / 100 * 10), 10)
    if pct >= 90:
        c = "31"
    elif pct >= 65:
        c = "33"
    else:
        c = "32"
    return f"\033[{c}m" + "█" * fill + "▁" * (10 - fill) + "\033[0m"

def tok(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)

def usd(c):
    if c <= 0:
        return ""
    if c >= 1:
        return f"${c:.2f}"
    if c >= 0.01:
        return f"{c*100:.1f}¢"
    return f"{c*100:.2f}¢"

# --- assemble ---
parts = [
    f"\033[1m{model}\033[0m",
    f"{bar(used_pct)} {used_pct:.0f}%",
    f"in:\033[36m{tok(in_tok)}\033[0m",
    f"out:\033[36m{tok(out_tok)}\033[0m",
]
cost_s = usd(cost)
if cost_s:
    parts.append(f"\033[35m{cost_s}\033[0m")

print(" | ".join(parts))
