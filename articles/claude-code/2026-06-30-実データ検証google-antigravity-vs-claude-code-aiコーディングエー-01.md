---
id: "2026-06-30-実データ検証google-antigravity-vs-claude-code-aiコーディングエー-01"
title: "【実データ検証】Google Antigravity vs Claude Code — AIコーディングエージェントのデータ移植性を徹底比較"
url: "https://qiita.com/revolutionbyhiddenvalues/items/f903ea30c32ea5859f42"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "Gemini"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIコーディングエージェントを日常的に使っていると、ふと気になることがあります。

**「このデータ、別のPCに移行できるの？」**
**「もし別のAIツールに乗り換えたら、今までの設定や会話は持っていける？」**

本記事では、**Google Antigravity (Gemini Code Assist)** と **Claude Desktop / Claude Code** の2つのAIコーディングエージェントについて、**実際のWindows環境のデータを調査**し、移植可能性を比較分析しました。

## 調査環境

- **OS**: Windows 11
- **Antigravity**: Gemini Code Assist（VS Code拡張）
- **Claude**: Claude Desktop アプリ v1.1.5749

## Antigravity（Gemini）のデータ構造

### 保存場所

全データは以下のディレクトリに集約されています：

```
%USERPROFILE%\.gemini\antigravity\
```

### 実測データ

| 項目 | 値 |
|------|-----|
| **合計サイズ** | 311.91 MB |
| **ファイル数** | 6,456 |

### ディレクトリ構成

```
.gemini\antigravity\
├── conversations/          # 会話データ (.pb Protocol Buffers)
├── brain/                  # アーティファクト (Markdown, JSON, 画像)
├── browser_recordings/     # ブラウザ操作スクリーンショット (JPG)
├── knowledge/              # ナレッジベース
├── code_tracker/           # コード変更追跡
├── implicit/               # 暗黙コンテキスト (.pb)
├── annotations/            # 注釈データ (.pbtxt)
├── playground/             # プレイグラウンド
├── html_artifacts/         # HTML成果物
├── installation_id         # インストール固有UUID
├── mcp_config.json         # MCP設定
├── user_settings.pb        # ユーザー設定
└── browserAllowlist.txt    # ブラウザ許可リスト
```

### 各ディレクトリの移植性

| ディレクトリ | 内容 | 形式 | 移植性 |
|--------------|------|------|--------|
| `conversations/` | 会話履歴 | `.pb` (Protocol Buffers) | ❌ 低い |
| `brain/` | 生成ドキュメント・計画書 | Markdown, JSON, 画像 | ✅ 高い |
| `browser_recordings/` | 操作記録 | JPG | ✅ 高い（大容量注意） |
| `implicit/` | AI内部コンテキスト | `.pb` バイナリ | ❌ 低い |
| `annotations/` | 注釈 | `.pbtxt` テキスト | ⚠️ 中間 |

### 重要な発見

**会話データ（`conversations/*.pb`）がProtocol Buffers形式** であるため、Antigravity専用のスキーマ定義がないとデシリアライズできません。最大の会話ファイルは **2.3MB** に達しており、テキストエディタでは読めません。

一方、`brain/` ディレクトリにはアーティファクト（実装計画、ガイドドキュメントなど）がMarkdown形式で保存されており、これらは自由にコピー・利用できます。

```
brain/
└── 676ec81d-.../
    ├── command_log_and_ifthen_guide.md         # 14KB
    ├── github_gitlab_mirror_guide.md           # 22KB
    ├── notion_github_actions_n8n_guide.md      # 21KB
    └── *.metadata.json                         # メタデータ
```

**容量の最大要因は `browser_recordings/`** で、ブラウザサブエージェントの操作記録として数千枚のJPGスクリーンショットが保存されます。

## Claude Desktop / Claude Code のデータ構造

### 保存場所

Claude は複数の場所にデータが分散しています：

```
# Claude Desktop
%APPDATA%\Claude\

# Claude Code CLI（インストール時）
%USERPROFILE%\.claude\

# プロジェクト内
<project>/.claude/
<project>/CLAUDE.md
<project>/.mcp.json
```

### 実測データ

| 項目 | 値 |
|------|-----|
| **合計サイズ** | 19.17 MB |
| **ファイル数** | 316 |

### ディレクトリ構成（Claude Desktop）

```
%APPDATA%\Claude\
├── claude_desktop_config.json   # MCP・プリファレンス設定
├── config.json                  # ロケール・テーマ
├── window-state.json            # ウィンドウ状態
├── git-worktrees.json           # Git worktree設定
├── ant-did                      # デバイスID (Base64)
├── logs/                        # アプリケーションログ
├── IndexedDB/                   # LevelDB（会話キャッシュ）
├── Local Storage/               # ブラウザストレージ
├── Cache/                       # Electronキャッシュ
└── sentry/                      # エラーレポート
```

### 設定ファイルの中身

Claude の設定ファイルは **全て人間可読なJSON** です：

```json
// claude_desktop_config.json
{
  "preferences": {
    "coworkWebSearchEnabled": true
  }
}
```

```json
// config.json
{
  "locale": "ja-JP",
  "userThemeMode": "system"
}
```

### Claude Code CLI の設定構造

Claude Code は**設定スコープの階層構造**が明確に定義されています：

```
[マネージド (組織)] → [ユーザー] → [プロジェクト] → [ローカル]
     ↓                    ↓              ↓              ↓
C:\Program Files\    ~/.claude\      .claude/       .claude/
ClaudeCode/         settings.json   settings.json  settings.local.json
                    CLAUDE.md       CLAUDE.md
```

プロジェクト設定（`.claude/settings.json`, `CLAUDE.md`）は **Gitリポジトリに含めてチームで共有する** 設計思想です。

## 比較分析

### データ量

```
Antigravity:  ████████████████████████████████  312 MB
Claude:       ██                                 19 MB
```

Antigravityが16倍以上のデータ量を使用しています。主因は`browser_recordings/`（ブラウザ操作スクリーンショットの大量JPG）です。

### ファイル形式

| 形式 | Antigravity | Claude |
|------|-------------|--------|
| **Protocol Buffers (.pb)** | 会話、設定、コンテキスト | ❌ 使用なし |
| **JSON** | MCP設定のみ | 全設定ファイル |
| **Markdown** | アーティファクトのみ | `CLAUDE.md` (指示ファイル) |
| **LevelDB** | ❌ 使用なし | IndexedDB（キャッシュ） |

### 移行シナリオ別比較

#### 🖥️ 別PCへの移行

| | Antigravity | Claude |
|--|-------------|--------|
| 手順 | 312MBフォルダ全コピー + `installation_id`問題対処 | ログインするだけ |
| 会話データ | ローカル`.pb`をコピーする必要あり | ☁️ クラウドに保存済み |
| 設定 | 一部`.pb`形式で手動移行困難 | JSONファイル数個をコピー |
| **難易度** | ⚠️ 中〜高 | ✅ 簡単 |

#### 💾 バックアップ・復元

| | Antigravity | Claude |
|--|-------------|--------|
| 会話 | 手動バックアップ必須（312MB） | クラウドに自動保存 |
| 設定 | `mcp_config.json` + `.pb`のコピー | `claude_desktop_config.json`のコピー |
| 成果物 | `brain/`のMarkdownをコピー | クラウドに保存済み |
| **難易度** | ⚠️ 手動管理が必要 | ✅ ほぼ不要 |

#### 👥 チームメンバーへの設定共有

| | Antigravity | Claude |
|--|-------------|--------|
| 方法 | `.agents/workflows/*.md`をGitコミット | `.claude/settings.json` + `CLAUDE.md`をGitコミット |
| **難易度** | ✅ 同等 | ✅ 同等 |

#### 🔀 他のAIツールへの移行

| | Antigravity | Claude |
|--|-------------|--------|
| 会話データ | ❌ `.pb`専用形式で読めない | ⚠️ UIエクスポート or API経由 |
| 設定 | JSON部分のみ可読 | 全てJSON、可読 |
| ナレッジ | `brain/`のMarkdownは移行可能 | `CLAUDE.md`は移行可能 |

## まとめ

| 評価項目 | Antigravity | Claude |
|---------|:-----------:|:------:|
| ローカルデータの軽さ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 別PCへの移行容易性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 設定ファイルの可読性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| チーム共有のしやすさ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 他ツールへの移行性 | ⭐⭐ | ⭐⭐⭐ |
| クラウドバックアップ | ⭐ | ⭐⭐⭐⭐⭐ |
| ローカル完結性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### 結論

**移植可能性ではClaudeが圧倒的に優位**です。その理由は：

1. **クラウドファースト設計** — 会話データがクラウドに保存されるため、ログインだけで環境が復元される
2. **全JSON設定** — 設定ファイルが全て人間可読で、手動編集もバージョン管理も容易
3. **Git統合思想** — プロジェクト設定をGitリポジトリで管理する前提の設計
4. **軽量なローカルデータ** — 19MB vs 312MBと16倍の差

一方、**Antigravityはローカル完結性**に優れています。クラウドに依存しないため、オフライン環境やデータ主権を重視する場合は有利です。また、`brain/`ディレクトリのMarkdownアーティファクト（実装計画、ガイドドキュメントなど）は移植性が高く、有用なドキュメント資産として活用できます。

**選択のポイント：**
- 🔄 **頻繁にPC移行・マルチデバイス** → Claude
- 🔒 **データをローカルに保持したい** → Antigravity
- 👥 **チーム開発の設定共有** → どちらも同等
- 📦 **将来的なツール乗り換え** → Claude（データ形式がオープン）

---

> 本記事のデータは2026年3月時点の実環境から取得したものです。各ツールのバージョンアップにより構造が変更される可能性があります。
