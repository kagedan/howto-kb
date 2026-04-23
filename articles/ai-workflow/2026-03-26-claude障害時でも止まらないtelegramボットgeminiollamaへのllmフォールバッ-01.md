---
id: "2026-03-26-claude障害時でも止まらないtelegramボットgeminiollamaへのllmフォールバッ-01"
title: "Claude障害時でも止まらないTelegramボット：Gemini・OllamaへのLLMフォールバック実装"
url: "https://zenn.dev/acropapa330/articles/llm_fallback_bot"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "Gemini", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

# Claude障害時でも止まらないTelegramボット：Gemini・OllamaへのLLMフォールバック実装

以前の記事でWSL上にClaude CLIを使ったTelegramボットを構築しました。ところが2026年3月25日、Anthropic側でPartial Outageが発生し、ボットが完全に応答不能になりました。

この反省から、**Claude障害時でも動き続ける冗長構成**を実装しました。

---

## 構成

```
Claude CLI（メイン）
    ↓ 障害・タイムアウト時
Gemini API（フォールバック1）
    ↓ これも失敗時
Ollama ローカルLLM（フォールバック2・完全オフライン対応）
```

各モードにはWeb検索（Brave Search API）とコード実行（Python/Bash）も実装しています。

---

## モード切り替えコマンド

```
/model          → 現在のモードを確認
/model auto     → 自動フォールバック（デフォルト）
/model claude   → Claude CLI のみ
/model gemini   → Gemini API のみ
/model local    → Ollama のみ
/status         → LLMモードを含むステータス表示
```

---

## 実装

### グローバル変数でモード管理

```
LLM_MODE = "auto"
LLM_MODE_LABELS = {
    "auto":   "🤖 Auto（Claude → Gemini → Ollama）",
    "claude": "🟣 Claude CLI",
    "gemini": "🔵 Gemini API",
    "local":  "🟡 Ollama（ローカル）",
}
```

### call\_llm：フォールバックの核心

```
async def call_llm(prompt, allowed_tools=None, permission_mode="acceptEdits",
                   cwd=None, timeout=300) -> str:
    async def _try_claude():
        return await call_claude_cli(prompt=prompt, ...)

    async def _try_gemini():
        r = await call_gemini_api(prompt, timeout=timeout)
        return f"[Gemini]\n{r}" if not r.startswith("❌") else r

    async def _try_ollama():
        r = await call_ollama_api(prompt, timeout=timeout)
        return f"[Ollama]\n{r}" if not r.startswith("❌") else r

    if LLM_MODE == "claude":
        return await _try_claude()
    elif LLM_MODE == "gemini":
        return await _try_gemini()
    elif LLM_MODE == "local":
        return await _try_ollama()
    else:  # auto
        result = await _try_claude()
        if result.startswith("❌"):
            result = await _try_gemini()
        if result.startswith("❌"):
            result = await _try_ollama()
        return result
```

### Gemini API（urllib のみ・追加ライブラリ不要）

WSLのネットワーク制限でpipインストールができなかったため、標準ライブラリの`urllib`だけで実装しました。

```
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

async def call_gemini_api(prompt: str, timeout: int = 300) -> str:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    )
    # 会話履歴をGeminiのマルチターン形式に変換
    contents = []
    if conversation_summary:
        contents.append({"role": "user", "parts": [{"text": f"[要約]\n{conversation_summary}"}]})
        contents.append({"role": "model", "parts": [{"text": "了解しました。"}]})
    for role, content in conversation_history:
        gemini_role = "user" if role == "user" else "model"
        clean = re.sub(r"^\[(Gemini|Ollama|Claude)\]\n?", "", content).strip()
        contents.append({"role": gemini_role, "parts": [{"text": clean}]})

    # 最後のユーザーメッセージを追加
    last_user_text = prompt.split("\nユーザー: ")[-1].strip() if "\nユーザー: " in prompt else prompt
    contents.append({"role": "user", "parts": [{"text": last_user_text}]})

    payload = json.dumps({
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 8192},
        "systemInstruction": {"parts": [{"text": "..."}]},
    }).encode("utf-8")

    loop = asyncio.get_event_loop()
    def _call():
        req = urllib.request.Request(url, data=payload,
                                      headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    return await asyncio.wait_for(loop.run_in_executor(None, _call), timeout=timeout)
```

**ポイント**：Geminiに会話履歴をそのまま渡すと `[Ollama]` `[Gemini]` などのプレフィックスを「モデル比較の例示」と誤解してロールプレイを始めます。履歴保存時にプレフィックスを除去することで解決しました。

```
async def add_to_history(user_text: str, assistant_text: str):
    ...
    clean_assistant = re.sub(r"^\[(Gemini|Ollama|Claude)\]\n?", "", assistant_text).strip()
    conversation_history.append(("assistant", clean_assistant))
```

### Ollama（ローカルLLM）

```
async def call_ollama_api(prompt: str, timeout: int = 300) -> str:
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "qwen3.5:0.8b")
    payload = json.dumps({
        "model": ollama_model,
        "prompt": prompt,
        "stream": False,
        "think": False,  # Thinkingモードを無効化（重要！）
    }).encode("utf-8")
    ...
```

**ポイント**：qwen3.5はデフォルトでThinkingモード（推論過程を延々と出力）が有効です。APIで `"think": false` を渡すことで無効化できます。コマンドラインの `/no_think` では効きません。

### Ollamaのインストール（WSL）

```
# zstdが必要
sudo apt-get install -y zstd
curl -fsSL https://ollama.com/install.sh -o /tmp/ollama_install.sh
sh /tmp/ollama_install.sh

# モデルをダウンロード（0.8b = 約1GB）
ollama pull qwen3.5:0.8b
```

WSL起動時に自動起動させる場合：

```
echo "ollama serve > /dev/null 2>&1 &" >> ~/.bashrc
```

---

## Web検索（Brave Search API）

Claude CLIは自前のWebSearchツールを持っていますが、Gemini/Ollamaにはありません。Python側でBrave Search APIを叩いて結果をプロンプトに埋め込みます。

```
_SEARCH_NEEDED_PATTERNS = re.compile(
    r"(最新|今日|明日|天気|ニュース|調べて|教えて|検索|...)",
    re.IGNORECASE,
)

def brave_search(query: str, count: int = 5) -> list[dict]:
    url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.request.quote(query)}&count={count}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY,
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return [{"title": r["title"], "snippet": r["description"], "url": r["url"]}
                for r in data.get("web", {}).get("results", [])]
```

**ハマりポイント**：`Accept-Encoding: gzip` ヘッダーを付けると422エラーになります。

### 検索結果の渡し方

単純にプロンプトに追加するだけだとGeminiが「複数モデルの比較」を始めました。厳しい指示を直接埋め込むことで解決：

```
strict_instruction = (
    "【重要な指示】上記の検索結果を参考に、以下の質問に日本語で簡潔に答えてください。"
    "[Ollama][Gemini][Claude]などのモデル名を使ったロールプレイや比較は絶対にしないこと。"
    f"質問: {user_question}"
)
return f"{search_ctx}\n\n{strict_instruction}"
```

---

## コード実行（Python/Bash）

LLMが生成したコードブロックを自動実行します。

```
_DANGEROUS_PATTERNS = re.compile(
    r"(rm\s+-rf|rm\s+-f\s+/|sudo|mkfs|dd\s+if=|chmod\s+777\s+/)",
    re.IGNORECASE,
)

def execute_code(lang: str, code: str, timeout: int = 300) -> str:
    if is_dangerous(code):
        return "❌ 危険なコマンドが含まれているため実行をブロックしました"
    if lang in ("python", "python3", "py"):
        result = subprocess.run(["python3", "-c", code], ...)
    else:
        result = subprocess.run(code, shell=True, ...)
    return result.stdout + result.stderr
```

コードブロックの検出：

```
def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    for m in re.finditer(r"```(bash|sh|python|python3|py)?\s*\n(.*?)```", text, re.DOTALL):
        lang = m.group(1) or "bash"
        code = m.group(2).strip()
        yield lang, code
```

---

## .envに追加が必要な設定

```
GEMINI_API_KEY=your_gemini_api_key
BRAVE_API_KEY=your_brave_api_key
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:0.8b
```

---

## おわりに

Claude障害時でも以下の順でフォールバックするようになりました：

1. **Claude CLI**：ツール（Bash/WebSearch）も使える最強モード
2. **Gemini API**：Web検索・コード実行対応、完全にライブラリ不要
3. **Ollama**：完全オフライン動作、ネット障害時の最終手段
