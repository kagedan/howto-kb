---
id: "2026-05-04-claude-codeを120使いこなす設定3選eccmemorymdobsidian連携-01"
title: "Claude Codeを120%使いこなす設定3選【ECC・Memory.md・Obsidian連携】"
url: "https://qiita.com/manchan/items/63745b9198f1989c2a15"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "qiita"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

Claude Codeを使い始めてしばらく経つと、こんな壁にぶつかりませんか？

- **「毎回同じ説明をしている」** — セッションが切れるたびにプロジェクトの背景を一から説明する
- **「コード生成はできるけど専門的なレビューが薄い」** — セキュリティや設計の観点が足りない
- **「調査した情報がどこかに消えていく」** — Claudeと一緒に調べた内容が次のセッションで使えない

私もまったく同じ悩みを持っていました。フリーランスのエンジニアとして、X投稿の自動化・録画→YouTube投稿パイプライン・情報収集の3本柱をClaude Codeで構築する中で、**3つの設定**を組み合わせることでこれらをすべて解決できました。

この記事ではその3つを実際のコードや設定ファイルとともに紹介します。

---

## 1. Everything Claude Code（ECC）— Claude Codeに"専門家チーム"を追加する

### ECCとは

**Everything Claude Code（ECC）** は、Claude Codeにエージェント・コマンド・スキル・ルールを一括インストールするプラグインです。

素のClaude Codeは万能ですが、専門的なタスク（セキュリティレビュー・テスト設計・アーキテクチャ設計など）では深みが出にくいことがあります。ECCを入れると**専門家エージェントが自動で呼び出される**ようになります。

インストールされるモジュール数の目安：

| 種別 | 数 |
|------|-----|
| エージェント | 48個 |
| コマンド | 79個 |
| スキル | 149個 |

### 導入方法

```bash
git clone https://github.com/GreatScotty44/EverythingClaudeCode
cd EverythingClaudeCode
./install.sh --profile full
```

`--profile full` で全モジュールをインストールします。インストール先は `~/.claude/` です。

### CLAUDE.mdに書くだけで自動呼び出しされる

ECCエージェントを活用するには、プロジェクトの `CLAUDE.md` に以下を追記するだけです。

```markdown
## ECC エージェントの活用ルール

| タイミング | 使うエージェント |
|-----------|----------------|
| スクリプト・コードを新規作成・修正したとき | code-reviewer |
| 認証情報・API・外部通信に関わるコードを触ったとき | security-reviewer |
| 複数ファイルにまたがる新機能を実装するとき（実装前） | planner |
| バグ修正・新機能追加のとき（実装前） | tdd-guide |
```

これだけで、コードを書いたら自動でレビューが走り、APIキーを扱うコードがあれば自動でセキュリティチェックが走るようになります。

実際に便利だと感じた使い方：

- **code-reviewer** → 関数の長さ・ネストの深さ・エラーハンドリングを自動指摘
- **security-reviewer** → X APIキー・YouTube OAuthトークンの扱いを自動チェック。`.env` への移動漏れを指摘してくれる
- **planner** → 「録画→エンコード→YouTube自動投稿」のような複数ファイルにまたがる実装の前に設計書を生成

### カスタムエージェントも作れる

ECCの標準エージェントだけでなく、**プロジェクト専用エージェントを自作**できます。

私が作った `x-post-drafter` エージェントの例：

```markdown
# X投稿下書き生成エージェント（~/.claude/agents/x-post-drafter.md）

## 役割
X（Twitter）投稿の下書きを3案生成する。動画告知と日常の2種類に対応。

## トリガー
ユーザーが「X投稿」「下書き」「告知」などと依頼したとき

## 出力形式
- タイプA（動画告知）: 140字以内 × 3案
- タイプB（日常）: 140字以内 × 3案
```

`~/.claude/agents/` に置くだけで、「X投稿の下書きを作って」と言うたびに自動で呼び出されます。SNS運用の手間が大幅に減りました。

---

## 2. CLAUDE.md + Memory.md — セッションをまたいで記憶させる

### 課題：Claude Codeはセッションが切れると忘れる

Claude Codeはセッションをまたぐと文脈がリセットされます。長期プロジェクトでは毎回「このプロジェクトは〜」と説明し直す手間が発生します。

### 解決策：2種類のファイルで記憶を管理する

| ファイル | 役割 | 更新タイミング |
|----------|------|---------------|
| `CLAUDE.md` | 作業ルール・操作制限・基本役割 | 方針が変わったとき（滅多に変えない） |
| `Memory.md` | プロジェクト状況・技術情報・完了タスク・残タスク | セッションごとに更新 |

### CLAUDE.md の全体像

```markdown
## セッション開始時のルール
- 必ずMemory.mdを読み込み、プロジェクトの状況・ルール・手順を把握してから作業を開始する
- 手順・ルールに変更があった場合はその都度Memory.mdを更新する

## 作業ルール

### 確認不要（自動実行してよい操作）
- ファイル・フォルダの一覧表示（ls, find）
- 既存ファイルの読み取り
- 作業内容の調査・分析

### 確認必要（y/n を求める操作）
- 新規ファイルの作成
- 既存ファイルへの書き込み・上書き
- パッケージのインストール

## スクリプト実行時の注意
- Python スクリプトは必ず venv を使用: `venv/bin/python scripts/xxx.py`
- ffmpeg のフルパス: `/usr/local/bin/ffmpeg`（PATH未設定環境対応）

## ECC エージェントの活用ルール
（前述のテーブルを記載）
```

**「確認不要」と「確認必要」を明示する**のがポイントです。これを書くだけで作業のテンポが劇的に改善します。

また「スクリプト実行時の注意」も重要です。macOSのlaunchdからPythonを実行すると `PATH` が引き継がれないため、ffmpegなどの外部コマンドはフルパスで書く必要があります。これをあらかじめ書いておくことで、毎回指摘する手間がなくなります。

### Memory.md の構成（引き継ぎ書のイメージ）

```markdown
# Memory — プロジェクト引き継ぎドキュメント

最終更新: 2026-05-03

## ユーザープロフィール
- 職業・目標・技術スタック

## プロジェクト構成（現在）
（フォルダ構成のツリー）

## 構築済み自動化システム
（何が動いているか：launchd デーモン・Dockerコンテナなど）

## 重要な技術情報
- 環境変数の一覧
- よく使うコマンド
- 認証情報の場所

## 完了済み作業 / 残タスク
- ✅ 完了したもの
- 【低優先度】次回着手するもの
```

### なぜこれが機能するか

CLAUDE.mdに「セッション開始時に必ずMemory.mdを読み込む」と書いているので、新しいセッションを始めるたびにClaudeが自動でこのファイルを読みます。

その結果：
- プロジェクトの目的を毎回説明しなくていい
- フォルダ構成を聞かれなくなる
- 「.envファイルはどこですか？」と聞かれなくなる
- 前回決めたアーキテクチャを覚えている

セッション開始時は一言：

```
前回のセッションを再開して
```

これだけで前回の状態から再開できます。

### Memory.mdはgitで管理できる

Memory.mdはプロジェクトのルートに置くためgitで管理できます。別のマシンに環境を移しても `git clone` するだけでClaudeの記憶ごと再現できます。チームで開発する場合も共有できます。

**CLAUDE.mdは"採用条件"、Memory.mdは"日々の業務引き継ぎ"** と考えると管理しやすいです。

---

## 3. Obsidian連携 — 情報収集をナレッジ管理に繋げる

### なぜObsidianか

Claude Codeで調査した情報は、セッションが終わると消えます。外部のメモアプリに手動でコピーするのも手間です。

**ObsidianのVaultをプロジェクト内に置く**ことで、ClaudeがMarkdownファイルを直接読み書きできるようになります。

### フォルダ構成

```
docs/AI-DataBase/  ← Obsidian Vault のルート
├── news/                           ← 自動収集ニュース記事（10日で自動削除）
│   └── news_2026-05-03.md
├── raw-sources/                    ← Web Clipperで手動保存した記事
└── wiki/                           ← Claudeが構造化して整理
    ├── summaries/
    └── references/
```

**`news/` と `raw-sources/` を分けることで、自動収集と手動クリップの役割が明確になります。**

### 自動ニュース収集（collect_news.py + launchd）

毎朝8時にZenn・QiitaのClaude Codeタグ記事をソースごとに2件ずつ自動収集するスクリプトを組みました。

```python
import os
import re
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
NEWS_DIR = "docs/AI-DataBase/news"
NEWS_RETENTION_DAYS = 10  # 10日経過したファイルを自動削除

def truncate_summary(text: str, max_lines: int = 3) -> str:
    """feedのsummaryをHTMLタグ除去・最大3行に整形"""
    text = re.sub(r"<[^>]+>", "", text)
    sentences = re.split(r"[。\n]", text.strip())
    result = "。".join([s.strip() for s in sentences if s.strip()][:max_lines])
    return result[:150] + "…" if len(result) > 150 else result

def delete_old_news():
    """10日以上前のニュースファイルを削除"""
    threshold = datetime.now() - timedelta(days=NEWS_RETENTION_DAYS)
    for filename in os.listdir(NEWS_DIR):
        if filename.startswith("news_") and filename.endswith(".md"):
            filepath = os.path.join(NEWS_DIR, filename)
            if datetime.fromtimestamp(os.path.getmtime(filepath)) < threshold:
                os.remove(filepath)

def notify_slack_per_article(items):
    """記事1件ごとにURL＋要約をSlackに送信"""
    for item in items:
        summary_line = f"\n> {item['summary']}" if item.get("summary") else ""
        message = f"📰 *{item['source']}*\n*{item['title']}*\n{item['url']}{summary_line}"
        requests.post(WEBHOOK_URL, json={"text": message}, timeout=10)
```

収集件数は `config/sources.json` の `limit` で各ソース2件に設定しています（合計最大8件/日）。
```

launchdで毎朝8時に自動実行：

```xml
<!-- ~/Library/LaunchAgents/com.claude.collect-news.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.claude.collect-news</string>
  <key>ProgramArguments</key>
  <array>
    <!-- PATHが引き継がれないのでvenvのフルパスを指定 -->
    <string>/Users/yourname/project/venv/bin/python</string>
    <string>/Users/yourname/project/scripts/collect_news.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>8</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/Users/yourname/project/scripts/logs/collect_news.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/yourname/project/scripts/logs/collect_news-error.log</string>
</dict>
</plist>
```

### Obsidian Web Clipperとの組み合わせ

- ブラウザで参考記事を見つけたら **Obsidian Web Clipper**（Chrome拡張）で1クリック保存
- 保存先を `raw-sources/` に設定しておくと、Claudeが「調べて」と言われたときに自動参照
- 「このVaultを参照して〇〇を調べて」と指示するだけで、蓄積した知識ベースをもとに回答してくれる

**収集→整理→活用** のサイクルが半自動化されました。

### obsidian-skillsでObsidian記法の精度を上げる

Obsidian CEO の Steph Ango（@kepano）が公開している **obsidian-skills** をインストールすると、ClaudeがWikilinksやCallouts・YAMLフロントマターをより正確に書けるようになります。

```bash
git clone https://github.com/kepano/obsidian-skills /tmp/obsidian-skills
cp -r /tmp/obsidian-skills/skills/obsidian-markdown ~/.claude/skills/
cp -r /tmp/obsidian-skills/skills/defuddle ~/.claude/skills/
# 全スキルをインストールする場合
cp -r /tmp/obsidian-skills/skills/json-canvas ~/.claude/skills/
cp -r /tmp/obsidian-skills/skills/obsidian-bases ~/.claude/skills/
cp -r /tmp/obsidian-skills/skills/obsidian-cli ~/.claude/skills/
```

特に便利な2つ:

| スキル | 効果 |
|--------|------|
| `obsidian-markdown` | Wikilinks（`[[]]`）・Callouts・Properties を自動で正確に記述 |
| `defuddle` | URLを渡すだけでクリーンなMarkdownに変換。Web Clipperの代替として使える |

これにより、raw-sourcesの記事を整理してwikiに格納するIngest作業でリンク切れや記法ミスが大幅に減ります。ECC + obsidian-skills を組み合わせることで、Claude Codeが**Obsidian記法をネイティブに扱える**環境が整います。

---

## まとめ：3つ合わせると何が変わるか

| 課題 | 解決策 |
|------|--------|
| 毎回文脈を説明し直す | CLAUDE.md + Memory.md |
| AIの専門性が足りない | ECC（専門エージェント48個） |
| 調査した情報が散逸する | Obsidian Vault連携 |

3つを組み合わせることで、Claude Codeが**プロジェクトの状況を記憶し・専門的に動き・情報を蓄積する**開発環境になりました。

特に「前回のセッションを再開して」の一言でプロジェクトの状態がすぐに戻ってくるのは、長期プロジェクトや複数プロジェクトを掛け持ちしているフリーランスには特に効いています。

### 設定コストは最初の1〜2時間だけ

- CLAUDE.md：30分で書ける
- Memory.md：プロジェクトの棚卸しをしながら1時間
- ECC：インストールコマンド1行

それ以降は毎回のセッションでその恩恵を受け続けられます。ぜひ試してみてください。

---

## 参考リンク

- [Everything Claude Code（ECC）](https://github.com/affaan-m/everything-claude-code)
- [Claude Code 公式ドキュメント](https://docs.anthropic.com/ja/docs/claude-code)
- [Obsidian](https://obsidian.md/)
- [Obsidian Web Clipper](https://obsidian.md/clipper)
- [Obsidian Vault構成の参考（@MakeAI_CEO）](https://x.com/MakeAI_CEO/status/2043674800888119512?s=20)
- [obsidian-skills（kepano）](https://github.com/kepano/obsidian-skills)
