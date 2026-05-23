---
id: "2026-05-22-claude-code-exa-slack-で作る朝のニュース自動配信-即時-qa-ボット-01"
title: "Claude Code + Exa + Slack で作る朝のニュース自動配信 & 即時 Q&A ボット"
url: "https://qiita.com/sky_stone/items/050010b70f4144782a26"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

:::note info
この記事では Claude Code・Exa Web Search・Slack MCP を組み合わせて、毎朝のニュースを自動配信するシステムと、Slack でメンションするだけで Q&A に回答してくれるボットを構築した手順を紹介します。

⚠️ 「即時」について: Q&A ボットは subprocess で Claude Code CLI を毎回起動する設計のため、メンションから回答までに 10〜30 秒程度かかります。ミリ秒レスポンスは期待しないでください。
:::

## はじめに ── 毎朝のニュース収集をやめた話

毎朝 30 分ほど、AI 関連ニュース・専門領域の最新研究・為替情報を手でかき集める習慣があった。RSS リーダーを開いて、気になる記事をブックマークして、Slack にメモを貼る。地味だが、積み重なるとかなりの時間と認知コストになる。

「これを自動化できないか？」と思ったのが出発点だ。手動の情報収集は「集める行為」に時間がかかりすぎて、「考える時間」が削られている。ツールに任せるべき仕事だと割り切ることにした。

**この記事の対象読者**: Claude Code を使い慣れており（`claude --print` の使い方を知っている）、Slack ワークスペースの管理者権限（Bot の作成・インストール）を持つ macOS ユーザーを想定しています。Linux・Windows では launchd の代わりに systemd/タスクスケジューラが必要です（本記事では扱いません）。

いくつかの方法を検討したが、最終的に選んだのは **Claude Code + Exa + Slack MCP** の組み合わせだ。Claude Code は CLI から呼び出せるため cron（macOS なら launchd）との相性が良く、Exa は検索の精度が高い。Slack MCP を使えば、検索結果を直接チャンネルに投稿させることができる。

結果として、9 時に Slack の 3 チャンネルへ自動でニュースが届き、チームメンバーがメンションするだけで Exa 検索ベースの Q&A に回答できるシステムが完成した。以下にその構築手順とハマりポイントを解説する。

---

## システム全体像

MCP（Model Context Protocol）は Anthropic が 2024 年に発表したオープン規格で、LLM が外部ツール（API・DB・ファイル等）を呼び出すための共通インターフェイスです。Claude Code は `.mcp.json` に書かれた MCP サーバーを起動し、その公開するツールを `mcp__<サーバー名>__<ツール名>` の形で利用します。今回は Exa（Web 検索）と Slack（メッセージ送信）の 2 つを MCP サーバーとして登録します。

```
[launchd (cron)]
     │
     ▼
[morning-news.sh]
     │ echo prompt | claude --print --allowedTools ...
     ▼
[Claude Code CLI]
     ├── mcp__exa-web-search__web_search_exa  ← 最新ニュースを検索
     └── mcp__slack__slack_post_message       ← 各チャンネルへ投稿
```

```
[Slack ユーザー]
     │ @ボット名 〇〇について教えて
     ▼
[socket-mode-bot.py (slack-bolt)]
     │ subprocess で claude --print を呼び出す
     ▼
[Claude Code CLI]
     └── mcp__exa-web-search__web_search_exa  ← 質問に合わせて検索
     │
     ▼
[スレッドに回答を返信]
```

コンポーネントは大きく 3 つに分かれる。

| コンポーネント | 役割 | バージョン（2026-05時点） |
|---|---|---|
| launchd（macOS の常駐サービス管理システム）+ shell スクリプト | 毎朝 9 時に Claude Code を起動する定期実行エンジン | macOS Sonoma 14.x 標準 |
| Claude Code CLI + MCP | Exa 検索 → Slack 投稿を「考えて実行」するエージェント | v1.x.x |
| slack-bolt + Socket Mode | Slack のメンションを受け取り、Claude Code を呼び出す Q&A レイヤー | slack-bolt 1.28.0 / Python 3.12 |

`.mcp.json` 一つで Exa と Slack の両方の MCP サーバーを管理し、Claude Code がツールを選んで実行してくれる。人間が書くのはプロンプトとシェルスクリプトだけ、というシンプルな設計だ。

---

## 事前準備 ── MCP・トークンの取得

:::note warn
**セットアップで詰まりやすい4つの落とし穴**
1. `claude` コマンドのパスが launchd に通っていない（→ シェルスクリプトで `export PATH` を明示）
2. `.mcp.json` のあるディレクトリで Claude を実行していない（→ スクリプトに `cd /path/to/project` を入れる）
3. Slack App の Event Subscriptions に `app_mention`（ボットへの @メンションイベント）を追加していない
4. ボットをチャンネルに招待していない（→ `/invite @ボット名`）
:::

### 必要なアカウント・API キー

- **Exa API キー**: [exa.ai](https://exa.ai) でアカウント作成後、ダッシュボードから発行
- **Slack Bot Token (`xoxb-...`)**: Slack App を作成し、Bot Token Scopes に `chat:write` `channels:read` `channels:history` を追加
- **Slack App Token (`xapp-...`)**: Socket Mode 用。App Settings > Basic Information > App-Level Tokens から `connections:write` スコープで発行

### `.mcp.json` の配置

プロジェクトディレクトリのルートに `.mcp.json` を置く。Claude Code はこのファイルを自動で読んで MCP サーバーを起動する。

:::note warn
2026-05 時点で `@modelcontextprotocol/server-slack` は公式アーカイブ済みです（`modelcontextprotocol/servers-archived` に移管）。npm からのインストール自体は可能ですが、今後のメンテナンスは停止しています。代替として `korotovsky/slack-mcp-server` 等のコミュニティ実装を検討してください。本記事では動作確認時点のパッケージをそのまま掲載しています。
:::

```json
{
  "mcpServers": {
    "exa-web-search": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": { "EXA_API_KEY": "YOUR_EXA_API_KEY" }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-YOUR-BOT-TOKEN",
        "SLACK_TEAM_ID": "YOUR-TEAM-ID"
      }
    }
  }
}
```

:::note warn
`EXA_API_KEY` と `SLACK_BOT_TOKEN` は `.gitignore` に `.mcp.json` を追加するか、環境変数として外部から注入する形にしよう。`.mcp.json` をそのままコミットしないこと。
:::

### Node.js と Python のセットアップ

```bash
# npx 経由で MCP サーバーを使うため Node.js が必要
brew install node

# slack-bolt のインストール
pip3 install slack-bolt
```

---

## 朝のニュース自動配信を作る

### シェルスクリプト: morning-news.sh

Claude Code CLI に渡すプロンプトを組み立て、パイプで流し込む。`--print` オプションで対話なし実行、`--allowedTools` で使えるツールを明示的に制限するのがポイントだ。

```bash
#!/bin/zsh
export PATH="/Users/username/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
cd /path/to/your/project

TODAY=$(TZ=Asia/Tokyo date '+%Y年%m月%d日')

PROMPT="今日の日付は${TODAY}です。
以下の3テーマについて最新ニュースを検索し、それぞれ指定のSlackチャンネルに投稿してください。
検索には mcp__exa-web-search__web_search_exa ツールを優先して使用してください。
Slack投稿には mcp__slack__slack_post_message ツールを使用してください。

## テーマ1: AI最新情報
- 日本語: 「AI 最新ニュース ${TODAY}」
- 英語: 「AI artificial intelligence news ${TODAY}」
- 投稿先チャンネルID: YOUR_CHANNEL_ID (#ai-news)

## テーマ2: 専門領域の最新研究
- 日本語・英語・中国語など、関連言語で検索
- 投稿先チャンネルID: YOUR_CHANNEL_ID (#research-news)

## テーマ3: 世界情勢・FX
- 日本語・英語で検索
- 投稿先チャンネルID: YOUR_CHANNEL_ID (#the-news)"

echo "$PROMPT" | claude \
  --print \
  --allowedTools "mcp__exa-web-search__web_search_exa,mcp__slack__slack_post_message"
```

**設計上のポイント:**

- `cd /path/to/your/project` は必須。ここに `.mcp.json` があるため、カレントディレクトリを合わせないと MCP サーバーが起動しない
- `TODAY` を日本語でプロンプトに埋め込むことで、Claude が「今日のニュース」を意識した検索クエリを生成してくれる
- `--allowedTools` を明示することで、意図しないファイル操作などを防ぐ

### launchd で毎朝 9 時に実行する

macOS の launchd を使って定期実行を設定する。`~/Library/LaunchAgents/` に plist ファイルを置けば、ログインセッションで動く（cron と違い macOS では推奨の方法）。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.username.morning-news</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>/path/to/morning-news.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>9</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/path/to/logs/morning-news.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/logs/morning-news-error.log</string>
</dict>
</plist>
```

```bash
# plist を登録・有効化
launchctl load ~/Library/LaunchAgents/com.username.morning-news.plist

# 手動でテスト実行
launchctl start com.username.morning-news
```

ログを `StandardOutPath` / `StandardErrorPath` で指定しておくと、デバッグ時に重宝する。動かないと思ったときはまずここを確認する癖をつけよう。なお、本セクションで起きやすいトラブルは記事末尾の[ハマりポイントと解決策まとめ](#ハマりポイントと解決策まとめ)に集約してある。

---

## Slack Q&A ボットを作る（Socket Mode）

Socket Mode を一言で言うと「自宅 Mac から公開 URL なしで Slack イベントを受け取るための WebSocket 接続方式」です。

### なぜ Socket Mode を選んだか

Webhook 方式では外部からのリクエストを受け付けるためにパブリック URL が必要になる。自宅サーバーや ngrok を使う方法もあるが、Socket Mode なら Slack 側から WebSocket で接続を張るため、ローカルマシンでそのまま動かせる。個人・小規模チーム用途にちょうどいい。

### socket-mode-bot.py

Python から直接 Anthropic SDK（`anthropic` パッケージ）を呼ぶ方法もありますが、今回は `.mcp.json` ベースの MCP サーバー設定（Exa・Slack のツール）をそのまま流用したかったため、Claude Code CLI を subprocess（Python から外部コマンドを呼び出すモジュール）で呼ぶ構成にしました。MCP サーバーを管理する設定ファイルが 1 つで済むというシンプルさを優先した選択です。

```python
import os, subprocess, re, logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.INFO)

app = App(token=os.environ["SLACK_BOT_TOKEN"])
CLAUDE_PATH = "/path/to/.npm-global/bin/claude"
PROJECT_DIR = "/path/to/your/project"

@app.event("app_mention")
def handle_mention(event, client, logger):
    # メンション部分（<@UXXXXXXXX>）を除去して質問文を取り出す
    question = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()
    channel = event["channel"]
    thread_ts = event.get("thread_ts", event["ts"])

    # 即時フィードバック: 調査中メッセージをスレッドに投稿
    client.chat_postMessage(
        channel=channel,
        thread_ts=thread_ts,
        text=f"🔍 「{question}」を調査中です..."
    )

    # Claude Code を subprocess で呼び出す
    result = subprocess.run(
        [CLAUDE_PATH, "--print",
         "--allowedTools", "mcp__exa-web-search__web_search_exa"],
        input=f"以下の質問にExa検索で回答してください。\n質問: {question}",
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=PROJECT_DIR,
        timeout=120
    )

    answer = result.stdout.strip() or "⚠️ 回答できませんでした。"
    client.chat_postMessage(
        channel=channel,
        thread_ts=thread_ts,
        text=answer
    )

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

**設計上のポイント:**

- `thread_ts` を使って、質問と回答を同じスレッドにまとめる
- 「調査中」メッセージを先に送ることで、ユーザーが不安にならないよう配慮する
- `cwd=PROJECT_DIR` を必ず指定すること（`.mcp.json` の場所を Claude Code に教えるため）
- `timeout=120`（2分）を設定。Exa 検索 + Claude 応答で実際に 10〜30 秒かかるため、短いタイムアウトでは頻繁に失敗する

### launchd で常時起動させる

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.username.socket-mode-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/python3</string>
        <string>/path/to/socket-mode-bot.py</string>
    </array>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key>
    <string>/path/to/logs/socket-mode-bot.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/logs/socket-mode-bot-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/path/to/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>SLACK_BOT_TOKEN</key>
        <string>xoxb-YOUR-BOT-TOKEN</string>
        <key>SLACK_APP_TOKEN</key>
        <string>xapp-YOUR-APP-TOKEN</string>
    </dict>
</dict>
</plist>
```

`<key>KeepAlive</key><true/>` を設定すると、プロセスが落ちたときに launchd が自動で再起動してくれる。Socket Mode ボットはこれが必須と言っていい。

```bash
launchctl load ~/Library/LaunchAgents/com.username.socket-mode-bot.plist
```

---

## ハマりポイントと解決策まとめ

### 1. launchd から claude コマンドが見つからない

**症状:** 手動では `claude` が動くのに、launchd 経由だと `command not found` エラーがログに残る。

**原因:** launchd が起動するシェルは `.zshrc` や `.bash_profile` を読まないため、`PATH` が通っていない。

**解決策:** シェルスクリプトの冒頭で `export PATH=...` を明示的に設定する。特に `~/.npm-global/bin` を忘れがちなので注意。

```bash
export PATH="/Users/username/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
```

### 1.5 launchd 配下で日本語が文字化け・エンコードエラーになる

launchd は対話シェルではないため `.zshrc`/`.bashrc` が読まれず、`PATH` だけでなく `LANG` `LC_ALL` などのロケール環境変数も空のまま起動する。結果、Python・Node.js・CLI 出力が ASCII / Latin-1 にフォールバックし、日本語まわりで様々な症状が出る。**対症療法より「plist の `EnvironmentVariables` で必要な環境変数を明示渡し」が根本解決。**

**症状A: `UnicodeDecodeError: 'ascii' codec can't decode...`**

- **原因:** launchd 配下では `locale.getpreferredencoding()` が C ロケール（ASCII）になり、`subprocess.run(..., text=True)` のデフォルトデコーダが ASCII になる
- **解決策:** `subprocess.run(..., encoding="utf-8")` を明示する（本記事の `socket-mode-bot.py` は対応済み）

**症状B: Claude Code CLI の出力がモジバケする（「?」「æ¥」などが混ざる）**

- **原因:** `LC_ALL`/`LANG` 未設定で Node.js が Latin-1 にフォールバックする
- **解決策:** plist の `EnvironmentVariables` に `LANG` を追加

```xml
<key>LANG</key>
<string>ja_JP.UTF-8</string>
```

**症状C: Python の `print()` で `UnicodeEncodeError`**

- **原因:** Python の stdout エンコーディングが C ロケール配下で ASCII になる
- **解決策:** plist の `EnvironmentVariables` に `PYTHONIOENCODING` を追加

```xml
<key>PYTHONIOENCODING</key>
<string>utf-8</string>
```

socket-mode-bot 用の plist の `EnvironmentVariables` セクションには、`PATH` と各種トークンに加えて以下も併記しておくと安心:

```xml
<key>LANG</key><string>ja_JP.UTF-8</string>
<key>PYTHONIOENCODING</key><string>utf-8</string>
```

### 2. MCP サーバーが起動しない / ツールが見つからない

**症状:** Claude Code を実行しても `mcp__exa-web-search__web_search_exa` ツールが使われず、Web 検索が走らない。

**原因:** `.mcp.json` のあるディレクトリで Claude を実行していなかった。

**解決策:** シェルスクリプトに `cd /path/to/your/project` を入れること。subprocess 呼び出しの場合は `cwd=PROJECT_DIR` を必ず渡す。

### 3. Slack の `app_mention` イベントが届かない

**症状:** ボットにメンションしても何も反応しない。

**原因1:** Slack App の Event Subscriptions で `app_mention` を Subscribe していなかった。

**解決策1:** Slack App ダッシュボード > Event Subscriptions > Subscribe to bot events に `app_mention` を追加して再インストール。

### 4. subprocess でのタイムアウト

**症状:** 複雑な質問で Claude Code が Exa を複数回叩くとタイムアウトしてしまう。

**原因:** デフォルト `timeout` が短すぎた。

**解決策:** `timeout=120`（2 分）以上に設定する。それでも足りない場合は `timeout=180` や非同期処理（asyncio + Thread）を検討する。

### 5. プロンプトに `--allowedTools` を書き忘れる

**症状:** ニュース配信スクリプトを実行したら、Claude がファイルシステムを読み始めた。

**原因:** `--allowedTools` を指定しないと Claude Code が持っているすべてのツールを使える状態になる。

**解決策:** 必ず `--allowedTools` で使うツールを列挙する。自動化スクリプトでは特に重要。

### 6. `npx -y` でバージョン非固定の落とし穴

**症状:** ある日突然 MCP サーバーが動かなくなった。

**原因:** `.mcp.json` で `npx -y <package>` を使うと毎回最新版を取得するため、破壊的変更が入ったタイミングで壊れる。

**解決策:** バージョンを固定する。

```json
"args": ["-y", "exa-mcp-server@x.x.x"]
```

また、記事公開時点から日が経っている場合は `@modelcontextprotocol/server-slack` の後継パッケージへの移行も検討すること（本文参照）。

### 7. プロンプトインジェクションに注意

**症状（潜在的）:** ボットにメンションした内容がそのまま Claude へのプロンプトとして渡るため、悪意のある指示（「これまでの指示を無視して...」）を含む質問を処理してしまう。

**原因:** `socket-mode-bot.py` が `event["text"]` を無加工で Claude に渡している。

**解決策:** 業務・チーム利用の場合は、許可ユーザーのホワイトリスト制御や入力バリデーションを追加する。個人利用では影響範囲が限られるが、`--allowedTools` で使えるツールを制限しておくことが最低限の対策。

---

## 実際の運用と効果

※ 以下は 2026-05 時点での運用記録です。Claude Code および MCP の挙動は更新により変わる可能性があります。

**時間の節約:** 毎朝の手動情報収集 30 分がほぼゼロになった。Slack を開いたらすでにまとまっている状態が気持ちいい。

**質の変化:** Exa の検索精度が高く、日本語・英語・中国語を混ぜた検索でも関連性の高い記事が返ってくる。特に専門領域の多言語検索は人力より精度が上がった。

**Q&A ボットの活用:** チームメンバーが「〇〇の最新情報って？」とメンションするだけで調べてくれるので、情報共有のコストが下がった。非同期で気軽に質問できるのが使いやすいと好評だった。

**コスト感:** Exa の無料枠（月 1,000 リクエスト程度、2026-05 時点）と Claude Code の利用料金が主なコスト。毎日 3 テーマ × 複数検索クエリで 1 日 10〜20 リクエスト程度使う計算になる。最新のプランは [exa.ai の Pricing ページ](https://exa.ai/pricing) で確認のこと。

---

## まとめ

Claude Code + Exa + Slack MCP を組み合わせることで、毎朝の情報収集を完全自動化できた。ポイントを整理すると：

- **`.mcp.json` を置いたディレクトリでの実行** が MCP を動かす大前提
- **`--allowedTools` の明示** で意図しない動作を防ぐ
- **launchd の `KeepAlive`** で Socket Mode ボットを常時稼働させる
- **`cwd` の指定** を subprocess 呼び出しでは忘れずに

MCP のエコシステムは急速に広がっており、Exa・Slack 以外にも Notion・GitHub・Google Workspace など様々なサーバーが公開されている。今回作ったシェルスクリプトのテーマや投稿先チャンネルを変えるだけで、用途を大きく広げることができる。

「Claude に考えさせて、ツールに実行させる」という設計は、思ったよりずっとシンプルで強力だった。毎朝の 30 分を取り戻せたのが一番の収穫だ。

### 次に拡張するなら

最小コストで効果が大きい拡張例：

- **PROMPT の変数化**: `morning-news.sh` のプロンプトを外部ファイルに切り出すと、テーマ変更がコード編集なしでできる
- **`slack_get_thread_replies` の追加**: Q&A ボットがスレッドの文脈を読めるようになり、フォローアップ質問に答えられる
- **MCP の追加**: `@modelcontextprotocol/server-github`（GitHub Issues 通知）、`@notionhq/notion-mcp-server`（Notion への保存）など、`.mcp.json` に1エントリ追加するだけで機能拡張できる

---

*動作確認環境（2026-05-22 時点）: macOS Sonoma 14.x / Claude Code CLI v1.x.x / Node.js 22.x / Python 3.12 / slack-bolt 1.28.0*
