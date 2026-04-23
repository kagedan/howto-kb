---
id: "2026-04-14-bash-is-all-you-need-を-deno-でやってみた-01"
title: "Bash is all you need を Deno でやってみた"
url: "https://zenn.dev/kt3k/articles/fdc37740fb6e59"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

`Bash is all you need` は以下の reddit スレッドで紹介されている小さなコーディングエージェントのデモです。

<https://www.reddit.com/r/ClaudeAI/comments/1ql4t00/write_a_claude_code_with_16_line_code_bash_is_all/>

作者は [ShareAI Lab](https://github.com/shareAI-lab) という組織の開発者で、[Kode-Agent](https://github.com/shareAI-lab/Kode-Agent) という OSS の Coding Agent を開発したり、[learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) という Claude Code ライクな agent をゼロから開発するチュートリアルを書いています。

コーディングエージェントから機能を落として行った時に何が残るかを追求したところ、bash だけが必要だった、というのが上のスレッドの趣旨です。

この記事では上のスレッドで紹介されているデモを Deno で再実装して実際にどのくらい動くかを検証してみました。

## コード

```
import Anthropic from "@anthropic-ai/sdk"
import { text } from "node:stream/consumers"

const client = new Anthropic()
const dec = new TextDecoder()

const TOOL_DESCRIPTION = `
シェルコマンドを実行する。
Patterns:
- Read: cat/grep/find/ls
- Write: echo '...' > file
- Subagent: deno -A --env agent.ts "task description"
`.trim()

const bashTool: Anthropic.Tool = {
  name: "bash",
  description: TOOL_DESCRIPTION,
  input_schema: {
    type: "object",
    properties: { command: { type: "string" } },
    required: ["command"],
  },
}

const SYSTEM =
  `CLI agent at ${Deno.cwd()}. Use bash. Spawn subagent for complex tasks.`

async function chat(prompt: string, history: Anthropic.MessageParam[] = []) {
  history.push({ role: "user", content: prompt })
  while (true) {
    const r = await client.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 8000,
      system: SYSTEM,
      tools: [bashTool],
      messages: history,
    })
    history.push({ role: "assistant", content: r.content })
    if (r.stop_reason !== "tool_use") {
      // tool_use でなければ終了
      return r.content.filter((b) => "text" in b).map((b) => b.text).join("")
    }
    const results = [] as Anthropic.ToolResultBlockParam[]
    for (const b of r.content) {
      if (b.type === "tool_use") {
        // bash 呼び出し
        const command = (b.input as { command: string }).command
        console.log(`bash -c %c"${command}"`, "color: cyan")
        let output: string
        if (confirm("Allow?")) {
          if (command.startsWith("deno -A --env agent.ts")) {
            const cp = await Deno.spawn("bash", {
              args: ["-c", command],
              stdout: "piped",
              stderr: "piped",
            })
            const stdout = cp.stdout.tee()
            stdout[0].pipeTo(Deno.stdout.writable, { preventClose: true })
            const stderr = cp.stderr.tee()
            stderr[0].pipeTo(Deno.stderr.writable, { preventClose: true })
            output = await Promise.all([text(stdout[1]), text(stderr[1])])
              .then(([a, b]) => a + b)
          } else {
            const { stdout, stderr } = await Deno.spawnAndWait("bash", {
              args: ["-c", command],
            })
            output = dec.decode(stdout) + dec.decode(stderr)
          }
        } else {
          output = "permission denied by user"
        }
        results.push({
          type: "tool_result",
          content: output,
          tool_use_id: b.id,
        })
      } else if (b.type === "text") {
        console.log("⏺", b.text)
      }
    }
    history.push({ role: "user", content: results })
  }
}

async function main() {
  if (Deno.args.length > 0) {
    // サブエージェントモード
    const id = Math.random().toString(36).slice(2, 5)
    console.log(`subagent ${id} started`)
    console.log(await chat(Deno.args[0]))
    console.log(`subagent ${id} ended`)
    return
  }
  // 履歴
  const h = [] as Anthropic.MessageParam[]

  while (true) {
    const p = prompt(">>")
    // 空入力 or q で終了
    if (p === null || p === "" || p === "q") {
      return
    }
    console.log(await chat(p, h))
  }
}

main()
```

## 解説

### システムプロンプト + ツール定義

```
import Anthropic from "@anthropic-ai/sdk"
const client = new Anthropic()
const TOOL_DESCRIPTION = `
シェルコマンドを実行する。
Patterns:
- Read: cat/grep/find/ls
- Write: echo '...' > file
- Subagent: deno -A --env agent.ts "task description"
`.trim()

const bashTool: Anthropic.Tool = {
  name: "bash",
  description: TOOL_DESCRIPTION,
  input_schema: {
    type: "object",
    properties: { command: { type: "string" } },
    required: ["command"],
  },
}

const SYSTEM =
  `CLI agent at ${Deno.cwd()}. Use bash. Spawn subagent for complex tasks.`
```

上記の箇所で、LLM に渡す tool の定義と、システムプロンプトを定義しています。簡単なタスクには bash のビルトイン関数を、複雑なタスクではサブエージェントを分解されたタスクで呼び出せということを指示しています。

### chat 関数

```
async function chat(prompt: string, history: Anthropic.MessageParam[] = []) {
  history.push({ role: "user", content: prompt })
  while (true) {
    /// ...
  }
}
```

ユーザーからのプロンプトをヒストリー積んで、bash tool の呼び出しループを開始しています。LLM がツールを使うのをやめて、回答を返してくるまでループします。

```
    ...
    const r = await client.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 8000,
      system: SYSTEM,
      tools: [bashTool],
      messages: history,
    })
    history.push({ role: "assistant", content: r.content })
    ...
```

システムプロンプトとツール定義を渡しながら LLM を呼び出しています。ここでは Sonnet 4.6 を使っています。

```
    ...
    if (r.stop_reason !== "tool_use") {
      // tool_use でなければ終了
      return r.content.filter((b) => "text" in b).map((b) => b.text).join("")
    }
    ...
```

LLM の回答が tool\_use でなかった場合は回答を表示して終了

```
    ...
    const results = [] as Anthropic.ToolResultBlockParam[]
    for (const b of r.content) {
      if (b.type === "tool_use") {
        // bash 呼び出し
        const command = (b.input as { command: string }).command
        console.log(`bash -c %c"${command}"`, "color: cyan")
        let output: string
        if (confirm("Allow?")) {
          if (command.startsWith("deno -A --env agent.ts")) {
            // サブエージェント呼び出し処理 ...
          } else {
            const { stdout, stderr } = await Deno.spawnAndWait("bash", {
              args: ["-c", command],
            })
            output = dec.decode(stdout) + dec.decode(stderr)
          }
        } else {
          output = "permission denied by user"
        }
        results.push({
          type: "tool_result",
          content: output,
          tool_use_id: b.id,
        })
      } else if (b.type === "text") {
        console.log("⏺", b.text)
      }
    }
    history.push({ role: "user", content: results })
    ...
```

LLM の回答が tool 呼び出しだった場合、LLM が選んだコマンドを実際に bash に渡して実行します。ここでは、流石にそのまま任意コマンドを実行するのは怖いので、`confirm("Allow?")` の呼び出しで、ユーザーに対してコマンド実行許可の確認をとっています。

コマンドの結果は role="user" で会話のヒストリーに積んでいます。

なお、コマンドの結果は、参照元に従って単純に (標準出力全体 + 標準エラー全体) を文字列として LLM に見せています。

```
          ...
          if (command.startsWith("deno -A --env agent.ts")) {
            const cp = await Deno.spawn("bash", {
              args: ["-c", command],
              stdout: "piped",
              stderr: "piped",
            })
            const stdout = cp.stdout.tee()
            stdout[0].pipeTo(Deno.stdout.writable, { preventClose: true })
            const stderr = cp.stderr.tee()
            stderr[0].pipeTo(Deno.stderr.writable, { preventClose: true })
            output = await Promise.all([text(stdout[1]), text(stderr[1])])
              .then(([a, b]) => a + b)
          } else {
            ...
          }
```

tool 選択がサブエージェント呼び出しだった場合、サブプロセスでの許可プロンプトを親に伝えたいため、少し呼び出しが複雑になっています (stdin は `inherit` にし、stdout, stderr は `piped` にした上で表示用と、subagent として結果を親に伝える為に stream を分岐しています)。

### メイン処理

```
async function main() {
  if (Deno.args.length > 0) {
    // サブエージェントモード
    const id = Math.random().toString(36).slice(2, 5)
    console.log(`subagent ${id} started`)
    console.log(await chat(Deno.args[0]))
    console.log(`subagent ${id} ended`)
    return
  }
  // 履歴
  const h = [] as Anthropic.MessageParam[]

  while (true) {
    const p = prompt(">>")
    // 空入力 or q で終了
    if (p === null || p === "" || p === "q") {
      return
    }
    console.log(await chat(p, h))
  }
}
```

引数があるかどうかでサブエージェントかどうかを見分けています。サブエージェントだった場合は1回 chat (= タスク) を回して終了。そうでなかった場合は、(ユーザープロンプト => AI 回答) のループを回します。

## 実行結果

### プロンプト: コードレビューして

```
$ deno -A --env agent.ts
>> read the source code and summarize very briefly
bash -c "find . -type f | head -50 && echo "---" && cat README.md 2>/dev/null || true"
Allow? [y/N] y
bash -c "cat agent.ts"
Allow? [y/N] y
## Summary

**bash-is-all-you-need-with-deno** is a minimal CLI coding agent (~80 lines) built with Deno and the Anthropic SDK.

### How it works:
1. **Single tool** — Claude is given only one tool: `bash`, which can run any shell command.
2. **Agentic loop** — It repeatedly calls Claude, executes bash commands, feeds results back, until Claude stops requesting tools.
3. **User approval** — Before each bash command runs, the user is prompted `Allow?` for safety.
4. **Two modes:**
   - **Interactive** (`deno -A agent.ts`) — REPL loop with persistent message history.
   - **Subagent** (`deno -A agent.ts "task"`) — Single-shot execution, enabling Claude to spawn child agents for complex subtasks.

The core idea (inspired by a Reddit thread) is that `bash` alone is sufficient as a universal tool — Claude can read/write files, search code, and delegate to subagents, all through shell commands.
```

`read the source code and summarize very briefly` というプロンプトをエージェントに投げています (このデモプロジェクト自体をレビューさせています)。`find`, `head`, `echo`, `cat` などを駆使して、まずは `agent.ts` ファイルを発見しています。そして `agent.ts` を読み、その内容を正しくレビューしていることが分かります。

```
$ deno -A --env agent.ts
>> count the html tags in www.google.com
⏺ I'll fetch the Google homepage and count the HTML tags for you!
bash -c "curl -s https://www.google.com | grep -oP '<[a-zA-Z][a-zA-Z0-9]*' | sort | uniq -c | sort -rn"
Allow? [y/N] y
bash -c "curl -s https://www.google.com | grep -oE '<[a-zA-Z][a-zA-Z0-9]*' | sort | uniq -c | sort -rn"
Allow? [y/N] y
Here's a summary of the **HTML tags found on www.google.com**:

> ⚠️ Note: Some results like `<e`, `<d`, `<arguments`, `<this`, etc. are **not real HTML tags** — they are JavaScript code patterns that happen to match the `<word` pattern. Below is a clean breakdown of **actual HTML tags only**:

| Count | Tag |
|-------|-----|
| 19 | `<div` |
| 19 | `<a` |
| 10 | `<input` |
| 9 | `<script` |
| 6 | `<span` |
| 5 | `<br` |
| 4 | `<meta` |
| 4 | `<b` |
| 3 | `<td` |
| 1 | `<tr` |
| 1 | `<title` |
| 1 | `<table` |
| 1 | `<svg` |
| 1 | `<style` |
| 1 | `<path` |
| 1 | `<p` |
| 1 | `<img` |
| 1 | `<image` |
| 1 | `<html` |
| 1 | `<head` |
| 1 | `<form` |
| 1 | `<center` |
| 1 | `<body` |

### 📊 Total: ~**101 real HTML tag instances** across **23 unique tag types**

Google's homepage is intentionally **very minimal** in its HTML structure — most of the complexity is loaded dynamically via JavaScript.
```

最初に `count the html tags in www.google.com` というプロンプトを投げています。

`curl`, `grep`, `sort`, `uniq` を駆使して、ビルトインコマンドのパイプだけでタグを数えています。最初の呼び出しで GNU grep 限定の `-P` オプションを指定していますが、筆者の環境は mac だったため、コマンドが失敗し、それを察した LLM が `grep -E` に置き換えて正しくカウント出来ています。

### プロンプト: ip address を表示するスクリプトを書いて

```
$ deno -A --env agent.ts
>> write a script to check the current ip address of the machine
bash -c "ls"
Allow? [y/N] y
bash -c "cat deno.json"
Allow? [y/N] y
bash -c "deno -A --env agent.ts "Write a script called check_ip.sh that checks the current IP address of the machine. It should show both the local/private IP and the public IP address. Make it readable with clear labels.""
Allow? [y/N] y
subagent 0u2 started
bash -c "cat << 'EOF' > check_ip.sh
#!/bin/bash

# ─────────────────────────────────────────
#         IP Address Checker Script
# ─────────────────────────────────────────

BOLD="\033[1m"
CYAN="\033[1;36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

print_header() {
  echo ""
  echo -e "${CYAN}╔══════════════════════════════════════╗${RESET}"
  echo -e "${CYAN}║        🌐  IP Address Checker        ║${RESET}"
  echo -e "${CYAN}╚══════════════════════════════════════╝${RESET}"
  echo ""
}

print_section() {
  echo -e "${BOLD}$1${RESET}"
  echo -e "  ──────────────────────────────────"
}

get_local_ip() {
  print_section "🔒  Local / Private IP Address"

  # Try ip command first (Linux), fall back to ifconfig (macOS/BSD)
  if command -v ip &>/dev/null; then
    LOCAL_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K[\d.]+')
  elif command -v ifconfig &>/dev/null; then
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
  fi

  if [[ -n "$LOCAL_IP" ]]; then
    echo -e "  ${GREEN}✔  IP Address : ${BOLD}$LOCAL_IP${RESET}"
  else
    echo -e "  ${RED}✘  Could not determine local IP address.${RESET}"
  fi
  echo ""
}

get_public_ip() {
  print_section "🌍  Public / External IP Address"

  # Try multiple public IP services for reliability
  PUBLIC_IP=$(curl -sf --max-time 5 https://api.ipify.org \
           || curl -sf --max-time 5 https://ifconfig.me \
           || curl -sf --max-time 5 https://icanhazip.com \
           || curl -sf --max-time 5 https://ipecho.net/plain)

  if [[ -n "$PUBLIC_IP" ]]; then
    echo -e "  ${GREEN}✔  IP Address : ${BOLD}$PUBLIC_IP${RESET}"
  else
    echo -e "  ${RED}✘  Could not determine public IP. Check your internet connection.${RESET}"
  fi
  echo ""
}

print_footer() {
  echo -e "${CYAN}  ──────────────────────────────────────${RESET}"
  echo -e "  ${YELLOW}Checked at: $(date '+%Y-%m-%d %H:%M:%S %Z')${RESET}"
  echo -e "${CYAN}  ──────────────────────────────────────${RESET}"
  echo ""
}

print_header
get_local_ip
get_public_ip
print_footer
EOF
chmod +x check_ip.sh
echo "Script created successfully!""
Allow? [y/N] y
bash -c "./check_ip.sh"
Allow? [y/N] y
Working perfectly! Here's a breakdown of everything the script does:

---

### 📄 `check_ip.sh` — What's inside

...コマンドの説明(長いので省略)...
```

最初に `write a script to check the current ip address of the machine` というプロンプトを投げています。

まず `ls` して、`deno.json` を読んでいます (サブエージェントの呼び出し方を考えているのかもしれません)。

次に `Write a script called check_ip.sh that checks the current IP address of the machine. It should show both the local/private IP and the public IP address. Make it readable with clear labels.` というプロンプトでサブエージェントを呼び出しています。

サブエージェントは上のタスク定義でスクリプトが思いついたようで、`check_ip.sh` に内容を書き込んでいます。

その後、作った `./check_ip.sh` を実行し動作確認した上で、出来たスクリプトの仕様説明を回答しています。

### 上よりも複雑なタスク

ここまでうまく動いた例を挙げてきましたが。より複雑なタスクだと、うまく遂行できないことが多いようでした。

例えば「任意の与えられた URL のタグを数える TypeScript を書いて」というプロンプトだと、仕様を指示したサブエージェントが起動され、そのサブエージェントが、ほぼ似たような指示でさらにサブエージェントを起動。その挙動が延々繰り返されて、いつまでも実装がされないという挙動になってしまいました。

より複雑なタスクをやらせたい場合は、システムプロンプトのチューニングもしくはツールの改良が必要なようでした。

## まとめ

* Bash ツールだけが使える AI エージェントで、コーディングエージェントの原型のようなものが出来た
* Bash のビルトイン関数だけで出来るタスクは割と遂行できる
* 複雑なタスクになるほど、タスク分解がうまく行かず、サブエージェント呼び出しの無限ループに陥ることが多い

## 参照

この記事のコードは以下のレポジトリからも参照できます (モデルを gpt-5.4 に変えたバージョンと実行例なども置いてあります)。

<https://github.com/kt3k/bash-is-all-you-need-with-deno>
