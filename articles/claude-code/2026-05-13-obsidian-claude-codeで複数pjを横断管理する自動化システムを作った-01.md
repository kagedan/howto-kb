---
id: "2026-05-13-obsidian-claude-codeで複数pjを横断管理する自動化システムを作った-01"
title: "Obsidian × Claude Codeで複数PJを横断管理する自動化システムを作った"
url: "https://qiita.com/Tadashi_Kudo/items/91ba2359ece21272668c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "Python"]
date_published: "2026-05-13"
date_collected: "2026-05-13"
summary_by: "auto-rss"
query: ""
---

# Obsidian × Claude Codeで複数PJを横断管理する自動化システムを作った

## はじめに

「Obsidian + Claude Codeで第二の脳を作ろう」という記事が海外でよく話題になる。CLAUDE.mdを置いて、フォルダを5個作って、Claudeに読ませる——というアプローチだ。

それ自体は悪くないが、**Claudeがフォルダを直読みする設計には限界がある**。1,000ノートを超えたとき、毎回全ファイルを読み込むのはトークン的にも速度的にも現実的ではない。

この記事では、筆者が実際に稼働させているシステムを公開する。

- **vault-rag**: sqlite-vec + bge-m3によるセマンティック検索MCP
- **AI-AGENT.md / CLAUDE.md**: ベンダー非依存の2層設計
- **スキルシステム**: 44本のClaude Codeスキル
- **scheduled-tasks**: 36本の自律エージェント定期実行

現時点のインデックス規模: **1,172ノート / 22,813チャンク**

## 全体アーキテクチャ

```
┌─────────────────────────────────────────────┐
│  Layer 1: Obsidian Vault（SSOT）            │
│  .md ファイル群 / Google Drive sync         │
└────────────────┬────────────────────────────┘
                 │ launchd 15分間隔インデックス
┌────────────────▼────────────────────────────┐
│  Layer 2: vault-rag MCP                     │
│  sqlite-vec + bge-m3 1024dim                │
│  search_vault / find_similar_notes          │
└────────────────┬────────────────────────────┘
                 │ MCP stdio
┌────────────────▼────────────────────────────┐
│  Layer 3: Claude Code                       │
│  AI-AGENT.md（中立層）+ CLAUDE.md（adapter）│
│  44スキル / 36 scheduled-tasks              │
└─────────────────────────────────────────────┘
```

Claudeは**ファイルを直読みしない**。すべてMCP経由でベクトル検索する。これによりトークン消費を大幅に抑えつつ、意味的に近いノートだけを取得できる。

## vault-rag: セマンティック検索をMCP化する

### 技術スタック

| 要素 | 採用技術 | 理由 |
|------|---------|------|
| ベクトルDB | sqlite-vec（WALモード） | Google Driveのファイルロック問題を回避 |
| Embedding | bge-m3 1024dim | sentence-transformers、Ollama不使用 |
| MCPフレームワーク | mcp[cli] (FastMCP) | 公式Python SDKに同梱 |
| 自動更新 | launchd 15分間隔 | Vault編集後に自動でインデックス更新 |

### MCPサーバーの実装（抜粋）

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "vault-rag",
    instructions="Obsidian Vault semantic search powered by bge-m3 + sqlite-vec",
)

@mcp.tool()
def search_vault(
    query: str,
    top_k: int = 5,
    pj_filter: str | None = None,
) -> list[dict]:
    """セマンティック検索。pj_filterでプロジェクト絞り込み可。"""
    return semantic_search(query, top_k, pj_filter)

@mcp.tool()
def find_similar_notes(file_path: str, top_k: int = 5) -> list[dict]:
    """指定ノートに意味的に近いノートを返す。"""
    return get_similar_notes(file_path, top_k)
```

`.mcp.json`にstdioサーバーとして登録するだけで、Claude Codeから`mcp__vault-rag__search_vault`として呼び出せる。

### なぜDuckDB/ChromaDBを選ばなかったか

- **DuckDB**: Google Driveとのファイルロック競合が発生
- **ChromaDB**: PersistentClientがマルチプロセス非推奨 + closeバグ
- **LanceDB**: 1,000ノート規模では過剰、Rust依存が重い

sqlite-vecはシングルファイルDBで、WALモードにすることでlaunchdとClaude Codeの同時アクセスを安全に扱える。

## AI-AGENT.md / CLAUDE.md: ベンダー非依存の2層設計

### 問題意識

CLAUDE.mdに全ルールを書くと、Cursorに移行するとき・別のAIエージェントを使うときに書き直しが発生する。

### 解決策: 中立層と adapter 層に分割

```
AI-AGENT.md  ← 中立正本（AIプラットフォーム非依存のルール）
    └── CLAUDE.md  ← Claude Code固有の差分のみ定義
    └── AGENTS.md  ← Codex固有の差分のみ定義（将来: .cursor/rules/）
```

**AI-AGENT.md** にはVaultのMap・哲学・検索戦略・PJ共通ルールを書く。
**CLAUDE.md** にはMCP具体名・Agent Team設定・Claude固有の動作差分のみ書く。

この設計により、**CLAUDE.mdはClaude固有の差分のみ**になり、他プラットフォームへの移植コストが最小化される。

## スキルシステム: 44本のClaude Codeスキル

### 設計思想

スキルはMarkdownファイルとして`.claude/skills/`に置く。Claude Codeが`/スキル名`で呼び出す。

```
.claude/skills/
├── morning-briefing.md   # 毎朝の状況確認
├── session-end.md        # セッション終了ログ
├── seo-outline.md        # SEO記事構成案
├── vault-rag-refresh.md  # RAGインデックス更新
└── ...（計44本）
```

### A/B/C分類で管理する

| 分類 | 説明 | Eval必須 |
|------|------|---------|
| A | 本番影響系（DB変更・投稿・デプロイ） | ✅必須 |
| B | 知識蓄積系（リサーチ・分析・要約） | Gotchasのみ |
| C | ワンショット系（一回限り） | 不要 |

A分類スキルはEvalチェック（成功/失敗/partial）を`skills-usage.json`に記録する。これにより「動いた気がする」で終わらず、実際の成功率が可視化される。

上限を50本に設定し、`/skill-rotate`で定期的に使用頻度の低いスキルをアーカイブする。

## scheduled-tasks: 36本の自律エージェント

### 仕組み

Claude Codeのscheduled-taskはcronベースでエージェントを定期実行する。各タスクはSKILL.mdとスケジュール定義を持つ。

```
.claude/scheduled-tasks/
├── morning-briefing/       # 毎朝7:00 ニュース収集・要約
│   └── SKILL.md
├── qiita-daily-writer/     # 毎朝7:11 Qiita記事生成・投稿
│   └── SKILL.md
├── pj-competitor-crawl/    # 週次 競合サイトクロール
│   └── SKILL.md
└── ...（計36タスク）
```

### 実際に動いているタスク例

| タスク | 頻度 | 内容 |
|--------|------|------|
| morning-briefing | 毎朝7:00 | AIニュース収集→日本語要約→Vault保存 |
| qiita-daily-writer | 毎朝7:11 | KWプランナー参照→記事生成→API投稿 |
| vault-evolution | 週次 | Claude Codeの新機能を検索してノート自動更新 |
| seo-improvement-planner | 週次 | GSCデータ取得→改善提案生成 |
| competitor-crawl | 週次 | 競合サイトのコンテンツ変化を検知 |

**人間がやることは「方針を決める」だけ**。実行・記録・フォローアップはエージェントが自律的に行う。

## 運用して気づいたこと

**1. Claudeに「ファイルを読ませる」より「検索させる」**
1,000ノートを超えたら、全読みは非現実的。vault-ragでセマンティック検索するほうがトークンも速度も1桁改善する。

**2. CLAUDE.mdは差分のみにする**
何でも書くと肥大化する。中立ルールはAI-AGENT.mdに逃がし、CLAUDE.mdはClaude固有の数十行に収める。

**3. スキルは上限を設けてローテーションする**
50本を超えたあたりから「どのスキルを呼べばいいか分からない」状態になる。A/B/C分類 + 定期ローテーションで管理する。

**4. scheduled-tasksはべき等に書く**
失敗して再実行したとき、重複投稿・重複コミットが起きないよう、各タスクの冒頭に「今日分が存在するかチェック」を入れる。

## まとめ

- **vault-rag**: sqlite-vec + bge-m3でセマンティック検索MCP化。Claudeがファイルを直読みしない設計
- **2層CLAUDE.md**: AI-AGENT.md（中立）+ CLAUDE.md（adapter差分）でベンダー非依存
- **スキルA/B/C分類**: 44本をEval記録付きで管理、上限50本でローテーション
- **scheduled-tasks 36本**: 朝刊・記事生成・競合クロール等を完全自律実行
- **規模感**: 1,172ノート / 22,813チャンク / 26PJ横断

「Claudeにフォルダを読ませる」段階を超えたら、この構成を参考にしてほしい。
