---
id: "2026-03-22-claudeが考えるollamaが思い出す2つのaiで動くopenclaw構成を図解-01"
title: "Claudeが「考える」。Ollamaが「思い出す」。2つのAIで動くOpenClaw構成を図解"
url: "https://zenn.dev/kobarutosato/articles/b305465f8dd4e0"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## 「設定は通った。でも何が動いてるかわからない…」

![](https://static.zenn.studio/user-upload/afb6ede99f2e-20260322.png)

OpenClawをセットアップしたあなたへ。

Slackで返事は返ってくる。Claude APIも動いてる。でも **裏側で何が起きてるか** 知らないと、エラーが出た瞬間に詰む。

* メモリが拾われない
* 2回目以降レスポンスが返らない
* Ollamaが勝手に落ちる

こんなトラブルに遭遇したとき、**アーキテクチャを知ってるか知ってないか** で対応時間が5倍変わります。

このガイドは、**OpenClawの内部構造を完全図解** します。読み終わったとき、あなたは：

✅ なぜ2つのAIが必要か理解できる  
✅ 5つのコンポーネントの役割が把握できる  
✅ データがどう流れるか追える  
✅ トラブルを自分で切り分けられる

---

## 📋 目次

っg

1. [設計思想：Claudeが「考える」Ollamaが「思い出す」](#%E8%A8%AD%E8%A8%88%E6%80%9D%E6%83%B3)
2. [5つのコンポーネント：全体像を掴む](#%E3%82%B3%E3%83%B3%E3%83%9D%E3%83%BC%E3%83%8D%E3%83%B3%E3%83%88)
3. [データフロー図解：メッセージから返答まで](#%E3%83%87%E3%83%BC%E3%82%BF%E3%83%95%E3%83%AD%E3%83%BC)
4. [Memory Searchの仕組み](#%E3%83%A1%E3%83%A2%E3%83%AA%E3%82%B5%E3%83%BC%E3%83%81)
5. [メモリのライフサイクル](#%E3%83%A9%E3%82%A4%E3%83%95%E3%82%B5%E3%82%A4%E3%82%AF%E3%83%AB)
6. [最小構成セットアップ【コピペで動く】](#%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97)
7. [よくあるトラブル＆切り分け方](#%E3%83%88%E3%83%A9%E3%83%96%E3%83%AB)
8. [ファイル構成：何が壊れた時に見るべきファイル](#%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E6%A7%8B%E6%88%90)

---

## 1. 設計思想：Claudeが「考える」Ollamaが「思い出す」 {#設計思想}

### OpenClawのコア設計は2行で説明できる

```
Claude（クラウド） → 「考える」: 推論・会話生成・判断
Ollama（ローカル） → 「思い出す」: 過去のメモ・会話の検索
```

このシンプルな役割分担がすべての鍵です。

### Claudeだけだと困る理由

Claudeは強い。日本語も完璧。でも **過去を覚えていない**。

```
昨日の打ち合わせ内容 → Claude は知らない
先週書いたメモ     → Claude は知らない
毎回「はじめまして」状態
```

毎回、何百万トークンのコンテキストウィンドウを使っても、セッションが終わると全部忘れる。これが LLM の宿命です。

### では、メモをどこに保存する？

ここで必要になるのが **Memory Search**。

```
ユーザーのメッセージ
    ↓
Ollama が「過去のメモから関連情報を検索」
    ↓
検索結果を Claude のプロンプトに注入
    ↓
Claude が「文脈を踏まえて」返答
```

### なぜ Embedding はローカルに？

検索には **Embedding（テキスト → ベクトル変換）** が必要です。

**Claude API で Embedding を使う場合：**

* 毎回 API 呼び出し → コスト増
* メモリデータがクラウドに送信 → プライバシーリスク
* 往復レイテンシ → 遅い

**Ollama でローカル Embedding：**

---

## 2. 5つのコンポーネント：全体像を掴む {#コンポーネント}

```
┌─────────────────────────────────────────────────────┐
│                     Slack（入口）                    │
│          ユーザー ← メッセージ ↔ Slack Bot        │
└────────────────┬────────────────────────────────────┘
                 │ (Socket Mode)
                 ↓
┌─────────────────────────────────────────────────────┐
│              Gateway（中継役・ルーター）              │
│         ws://127.0.0.1:18789 で待ち受け             │
│      メッセージ受信 → セッション管理 → ルーティング   │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────┐   ┌──────────────────────┐
│   Agent（司令塔）        │   │ Claude API（頭脳）  │
│ ・SOUL.md（性格定義）   │ ↔ │ ・推論エンジン      │
│ ・USER.md（ユーザ情報） │   │ ・claude-sonnet-4-6│
│ ・Memory結果をプロンプト│   │ ・日本語最高品質    │
│  に注入                 │   │                     │
└──────────────┬───────────┘   └──────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────┐
│   Ollama + memory.sqlite（記憶係）                   │
│  ・nomic-embed-text: テキストをベクトルに変換       │
│  ・memory.sqlite: ローカルベクトルストア           │
│  ・コサイン類似度で関連メモを検索                   │
└──────────────────────────────────────────────────────┘
```

### 各コンポーネントの詳細

| コンポーネント | 役割 | 実装 | 特徴 |
| --- | --- | --- | --- |
| **Slack** | 入口。ユーザーとの接点 | Socket Mode | 公開URL不要。ローカル開発向き |
| **Gateway** | メッセージ中継・セッション管理 | ws://127.0.0.1:18789 | ステートレス。複数Agent対応可 |
| **Agent** | 全体の司令塔。プロンプト組立 | SOUL.md + USER.md | 意思決定の中核。モデル選択も行う |
| **Claude API** | 推論エンジン | claude-sonnet-4-6 | クラウド実行。高品質。有料 |
| **Ollama** | ベクトル化＋検索 | nomic-embed-text | ローカル実行。無料。高速 |

---

## 3. データフロー図解：メッセージから返答まで {#データフロー}

![](https://static.zenn.studio/user-upload/184e7fc11983-20260322.png)

### 【パターン A】Memory Search 未使用（シンプルな会話）

```
1. Slack で @Bot にメンション
   └─ "今日の会議、何時？"
        ↓
2. Gateway が Socket Mode で受信
        ↓
3. Agent が受信メッセージを解析
   - SOUL.md を読む
   - USER.md を読む
        ↓
4. Claude API に送信
   (過去のメモなし。会話履歴のみ)
        ↓
5. Claude が応答生成
   - Ollama は何もしない
   - Memory.sqlite も触らない
        ↓
6. Slack に返信
   └─ "18時のはずです"
```

**所要時間：** 1〜3秒（Claude API のレイテンシ）

---

## 4. Memory Search の仕組み {#メモリサーチ}

### Embedding（埋め込み）とは？

テキストを「意味を持つ数値の列」に変換する処理です。

```
入力：「営業予算の配分について」

処理：nomic-embed-text
  ↓
出力：[0.234, -0.891, 0.123, ..., -0.456]
      (768 次元のベクトル)

別のテキスト：「営業部の予算案」
  ↓
出力：[0.245, -0.878, 0.134, ..., -0.432]
      (768 次元のベクトル)

→ この 2 つは「意味が近い」から、ベクトル同士の距離が小さい
```

### コサイン類似度で検索

ユーザーが「予算」と言ったら：

```
ユーザー入力を Embedding
  ↓
「予算」 → [0.100, -0.900, ..., -0.400]
  ↓
memory.sqlite の全メモと比較
  ├─ 「営業予算」 → コサイン類似度 0.92
  ├─ 「来月の祝日」 → コサイン類似度 0.05
  └─ 「企画予算」 → コサイン類似度 0.88
  ↓
上位 N 件（デフォルト 3 件）を抽出
```

つまり、**完全一致しなくても「似た意味」なら拾える** ということです。

### Memory Search の有効化

```
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "sources": ["memory", "sessions"],
        "provider": "openai",
        "remote": {
          "baseUrl": "http://localhost:11434/v1/",
          "apiKey": "ollama"
        },
        "model": "nomic-embed-text"
      }
    }
  }
}
```

**sources の選択肢：**

| sources | 対象 | 用途 |
| --- | --- | --- |
| `"memory"` | `workspace/memory/*.md` | 手書きメモ + エージェント自動生成メモ |
| `"sessions"` | `agents/main/sessions/*.jsonl` | 過去の全会話ログ |

両方有効にすると、メモと会話の両方を検索します。

---

## 5. メモリのライフサイクル {#ライフサイクル}

### 4 つのステップ

```
┌──────────────┐
│ Write（保存）│ ← メモを作成・配置
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ Index（索引化）│ ← Embedding + sqlite に格納
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ Search（検索）│ ← メッセージ受信時に自動実行
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ Use（活用）  │ ← Claude のプロンプトに注入
└──────────────┘
```

### Step 1：保存（Write）

3 つのルート：

```
# ルート A：手動で Markdown ファイルを配置
$ echo "予算案：営業 100万、企画 50万" > ~/.openclaw/workspace/memory/budget_2024.md

# ルート B：エージェントが会話中に自動生成
（Agent が重要情報を認識 → メモ自動作成）

# ルート C：会話セッションが自動保存
$ cat ~/.openclaw/agents/main/sessions/2024-03-22.jsonl
{"role": "user", "content": "予算は？"}
{"role": "assistant", "content": "営業は..."}
```

### Step 2：インデックス構築（Index）

メモを Embedding して`memory.sqlite`に格納：

```
openclaw memory index --force
```

このコマンドが実行される場面：

* ✅ エージェント起動時（自動）
* ✅ `workspace/memory/`にファイルが追加されたとき（自動）
* ⚠️ **「メモを追加したのに拾われない」ときは手動実行**

### Step 3：検索（Search）

毎回のメッセージ受信時に自動実行：

```
Slack で "予算は？" → 
  Ollama が background で検索 → 
  上位 3 件のメモを Claude に注入
```

`memorySearch.enabled: true` なら、ユーザーが何もしなくても動きます。

### Step 4：活用（Use）

```
Claude へのプロンプト：

<instruction>
You are a helpful assistant. Use the following memory snippets if relevant:

<memory>
File: budget_2024.md
Content: 予算案：営業 100万、企画 50万
Similarity: 0.92
</memory>

User: 予算は？
</instruction>

Claude: "営業部で 100万円の予算が配分されています"
```

---

## 6. 最小構成セットアップ【コピペで動く】 {#セットアップ}

### 前提環境

* macOS + Homebrew
* Anthropic API キー

### Step 0：5 分で環境確認

```
# Mac か確認
uname -s
# Darwin が返ってくれば OK

# Homebrew あるか確認
brew --version

# API キー あるか確認
echo $ANTHROPIC_API_KEY
# 何か返ってくれば OK
```

### Step 1：Ollama をインストール＆起動（2 分）

```
# インストール
brew install ollama

# バックグラウンドで起動
brew services start ollama

# Embedding モデルを取得
ollama pull nomic-embed-text
```

**動作確認：**

```
curl http://localhost:11434/v1/models
```

返却例：

```
{
  "object": "list",
  "data": [
    {
      "id": "nomic-embed-text:latest",
      "object": "model",
      "owned_by": "nomic",
      "permissions": []
    }
  ]
}
```

✅ OK、次へ。

### Step 2：openclaw.json を編集（3 分）

```
# ホームディレクトリに .openclaw フォルダを作成
mkdir -p ~/.openclaw

# openclaw.json を作成
cat > ~/.openclaw/openclaw.json << 'EOF'
{
  "version": "0.1.0",
  "slack": {
    "appToken": "xapp-YOUR_APP_TOKEN",
    "botToken": "xoxb-YOUR_BOT_TOKEN"
  },
  "anthropic": {
    "apiKey": "${ANTHROPIC_API_KEY}"
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-6"
      },
      "memorySearch": {
        "enabled": true,
        "sources": ["memory", "sessions"],
        "provider": "openai",
        "remote": {
          "baseUrl": "http://localhost:11434/v1/",
          "apiKey": "ollama"
        },
        "model": "nomic-embed-text"
      }
    }
  }
}
EOF
```

**⚠️ 重要：Slack トークンを取得**

1. [Slack API ダッシュボード](https://api.slack.com/apps)に移動
2. アプリを選択 → OAuth & Permissions
3. Bot Token Scopes に以下を追加：
   * `chat:write`
   * `app_mentions:read`
   * `files:read`
4. App-Level Tokens で Socket Mode トークン生成
5. `xapp-...` と `xoxb-...` を上記ファイルに貼り付け

### Step 3：メモリをインデックス化（1 分）

```
openclaw memory index --force
```

### Step 4：起動＆テスト（2 分）

Slack で Bot にメンション：

返答が返ってくれば成功です。

### Step 5：メモを作成してテスト（1 分）

```
# メモを作成
mkdir -p ~/.openclaw/workspace/memory

echo "プロジェクト X の締め切りは 3 月 31 日" > ~/.openclaw/workspace/memory/project.md

# インデックス再構築
openclaw memory index --force
```

Slack で聞いてみる：

```
@OpenClaw_Bot プロジェクトの期限は？
```

メモの内容が返ってくれば、Memory Search が動いています。

---

## 7. よくあるトラブル＆切り分け方 {#トラブル}

### トラブル 1：Ollama が起動しない

**症状：**

```
curl: (7) Failed to connect to localhost port 11434
```

**切り分けフロー：**

```
# ステップ 1：プロセス確認
lsof -i :11434
# 何か返ってくれば別プロセスが使用。殺す：
# kill -9 <PID>

# ステップ 2：Homebrew 経由で再起動
brew services restart ollama

# ステップ 3：2 秒待ってから確認
sleep 2
curl http://localhost:11434/v1/models

# ステップ 4：それでもダメなら手動起動＆ログ確認
ollama serve
# エラーメッセージが出る
```

**よくある原因：**

* M1/M2 Mac で GPU メモリ不足 → メモリ増設 or Rosetta モード
* ファイアウォールが port 11434 をブロック

### トラブル 2：Memory Search が拾われない

**チェックリスト【この順で実行】：**

```
# 1. Ollama が動いているか
curl http://localhost:11434/v1/models
# → nomic-embed-text:latest が返ってくれば OK

# 2. Embedding が実際に動くか
curl http://localhost:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "nomic-embed-text", "input": "テスト"}'
# → "embedding": [...] が返ってくれば OK

# 3. インデックスファイルが存在するか
ls -lh ~/.openclaw/memory/main.sqlite
# → ファイルがあれば OK。なければ以下を実行：
openclaw memory index --force

# 4. メモ自体が存在するか
ls -la ~/.openclaw/workspace/memory/
# → .md ファイルがなければメモを作成

# 5. openclaw.json の設定を確認
cat ~/.openclaw/openclaw.json | grep -A 5 memorySearch
# → enabled: true か確認
```

**8 割はこれで解決：**

```
# メモが追加されたのに拾われない場合
openclaw memory index --force
```

**既知バグ：2 回目以降が fetch failed**

GitHub Issue #10931：

```
# 症状：1 回目は動くが、2 回目以降が失敗

# 解決策：
openclaw gateway restart
```

### トラブル 3：Slack に返答が返ってこない

**症状：**

```
@Bot にメンションしたが何も返ってこない
1 分待っても無反応
```

**ログを見る：**

```
# ログを追跡
openclaw logs

# または詳細ログ
openclaw logs --level debug
```

**チェックリスト：**

```
# 1. .env が正しいか
cat ~/.openclaw/openclaw.json | grep -E "appToken|botToken"
# → xapp- と xoxb- で始まるトークンが入っているか

# 2. Slack アプリで Socket Mode が有効か
# [Slack API Dashboard] → [アプリ] → [Socket Mode] → 有効化

# 3. Bot に必要なスコープが付いているか
# [Slack API Dashboard] → [アプリ] → [OAuth & Permissions]
# 以下が必須：
#   - chat:write
#   - app_mentions:read
#   - files:read

# 4. ワークスペースに Bot が追加されているか
# Slack 側で #random など に @Bot がいるか確認

# 5. Gateway が起動しているか
ps aux | grep openclaw
# → openclaw が複数行返ってくれば OK
```

!

**最後の手段：完全リセット**

```
# Gateway + Agent を再起動
openclaw gateway restart
openclaw start

# それでもダメなら
pkill -f openclaw
rm -rf ~/.openclaw/agents/main/sessions/
openclaw start
```

⚠️ セッションログが削除されるので注意

---

## 8. ファイル構成：何が壊れたとき何を見るべきか {#ファイル構成}

```
~/.openclaw/
├── openclaw.json                 ← メイン設定ファイル
├── memory/
│   └── main.sqlite              ← ベクトルインデックス（重要）
├── agents/
│   └── main/
│       ├── agent/
│       │   └── models.json       ← モデル定義
│       └── sessions/
│           ├── 2024-03-22.jsonl  ← 会話ログ
│           └── 2024-03-21.jsonl
└── workspace/
    ├── SOUL.md                  ← AI の性格定義（重要）
    ├── USER.md                  ← ユーザー情報
    ├── HEARTBEAT.md             ← 定期タスク
    └── memory/
        ├── budget_2024.md        ← 手書きメモ
        ├── project.md
        └── ...
```

### 「何が起きた？」別・確認ファイル

| 症状 | 確認すべきファイル |
| --- | --- |
| **返答が来ない** | `openclaw.json`（トークン）、ログ |
| **メモが拾われない** | `memory/main.sqlite`、`workspace/memory/` |
| **AI の性格がおかしい** | `SOUL.md`、`USER.md` |
| **古いメモが混ざってる** | `workspace/memory/`（削除）→ 再インデックス |
| **会話が長くなると遅い** | `agents/main/sessions/`（古いセッション削除） |

### 3 つの黄金ファイル

これだけ覚えておけば 80% 対応できます：

```
# 設定を変えたい
~/.openclaw/openclaw.json

# メモリが動かない
~/.openclaw/memory/main.sqlite

# AI の振る舞いを変えたい
~/.openclaw/workspace/SOUL.md
```

---

## 最後に：アーキテクチャを知ることの価値

OpenClaw は設計がシンプルです。だからこそ **内部構造を理解することで、トラブル対応が一気に速くなります。**

* 「Memory Search が動かない」→ Ollama か、インデックスか、メモか → 3 つの可能性に絞れる
* 「返答が遅い」→ Claude か、Ollama か、Gateway か → 切り分けられる
* 「古い情報が混ざる」→ `memory/` のメモを削除して再インデックス → 解決

**次のステップ：**

1. 最小構成をセットアップして、実際に動かす
2. メモを 5 件作成して、Memory Search の威力を実感する
3. `SOUL.md` を編集して、AI の性格をカスタマイズする

では、OpenClaw での AI 相棒との対話、楽しんでください。

---

**このガイドが役に立ったら、シェア・フォローをお願いします。**

Zenn での技術解説記事、随時更新中です。

デモ  
![](https://static.zenn.studio/user-upload/e684fc230362-20260322.png)
