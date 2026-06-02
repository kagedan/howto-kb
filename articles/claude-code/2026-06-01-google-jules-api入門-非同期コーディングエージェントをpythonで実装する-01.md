---
id: "2026-06-01-google-jules-api入門-非同期コーディングエージェントをpythonで実装する-01"
title: "Google Jules API入門 — 非同期コーディングエージェントをPythonで実装する"
url: "https://zenn.dev/kai_kou/articles/224-jules-api-coding-agent-python-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "Gemini"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

Google が提供する非同期 AI コーディングエージェント **Jules** の REST API が alpha 版として公開されています。Jules API を使うと、バグ修正・コードレビュー・PR 自動作成といった作業を、Slack・GitHub Actions・カスタムツールから直接トリガーできます。本記事では、Jules の概念から REST API の操作、Python SDK による実装、CI/CD への組み込みまでを解説します。

## はじめに

### この記事で学べること

* Jules（非同期 AI コーディングエージェント）の全体像
* Jules API のコアコンセプト（Sources / Sessions / Activities）
* REST API による操作（curl・Python）
* GitHub Actions との連携パターン
* Jules の最新機能（MCP 対応・CI 自動修正・メモリ機能）

### 対象読者

* AI コーディングエージェントを自社ツール・CI/CD に組み込みたいエンジニア
* Google Jules を実用的に活用したい開発者

### 前提条件

* GitHub アカウント（Jules の GitHub App をインストールするため）
* Python 3.10 以上
* Jules アカウント（[jules.google](https://jules.google/)）

---

## TL;DR

* Jules API は `https://jules.googleapis.com/v1alpha/` で提供される REST API（alpha 版）
* 認証は `X-Goog-Api-Key` ヘッダー。Jules 設定画面で最大 3 個まで発行可能
* **Source → Session → Activity** の 3 層モデルで非同期コーディングを管理
* `automationMode: AUTO_CREATE_PR` を指定すれば Jules が自動で PR を作成
* Gemini 3 Flash（無料〜）/ Gemini 3.1 Pro（Pro プラン）がバックエンドモデル

---

## Jules とは何か

Jules は Google Labs が開発した **非同期 AI コーディングエージェント**です。GitHub Copilot のようなインライン補完ツールとは異なり、Jules はバックグラウンドでコーディングタスクをこなし、完了したら PR を作成して報告します。

### 従来ツールとの違い

| ツール | 形式 | 動作タイミング |
| --- | --- | --- |
| GitHub Copilot | インライン補完 | リアルタイム（開発者が入力中） |
| Cursor Agent | セミインタラクティブ | 対話しながら作業 |
| **Jules** | **非同期エージェント** | **バックグラウンドで完結** |

Jules に「認証バグを直して」と指示すると、Jules は独立した仮想環境でコードを読み込み、解析し、修正し、PR を作成します。開発者が別の作業をしている間に、Jules が問題を片付けてくれるのが最大の特徴です。

### バックエンドモデル

| プラン | モデル | 特徴 |
| --- | --- | --- |
| 無料・有料全般 | Gemini 3 Flash | 高速・省コスト |
| Google AI Pro プラン | Gemini 3.1 Pro | 高度な推論・複雑タスク対応 |

---

## Jules API の全体像

Jules API は 3 つのリソースを中心に設計されています。

### 1. Source（ソース）

コーディング作業の対象となるリポジトリです。Jules の GitHub App をリポジトリにインストールすると、API から参照できるようになります。

```
形式: sources/github/{owner}/{repo}
例:   sources/github/myorg/my-backend
```

### 2. Session（セッション）

1 つのコーディングタスクに対応する作業単位です。`prompt`（指示内容）と `sourceContext`（対象リポジトリ）を指定して作成します。Session の状態をポーリングすることで、Jules の進捗を確認できます。

### 3. Activity（アクティビティ）

Session 内の個々のステップです。Jules がプランを立案する、コードを修正する、ユーザーがメッセージを送る、などの各アクションが Activity として記録されます。

---

## 事前準備

### Step 1: Jules GitHub App のインストール

Jules API を使う前に、Jules の GitHub App を対象リポジトリにインストールしてください。

1. [jules.google](https://jules.google/) にアクセスしてログイン
2. 「Connect GitHub」から GitHub App をインストール
3. 対象リポジトリへのアクセスを許可

### Step 2: API キーの発行

1. Jules Web アプリの [Settings](https://jules.google.com/settings) にアクセス
2. 「Create API Key」をクリック
3. 生成されたキーをコピー（最大 3 個まで作成可能）

---

## REST API で操作する

ベース URL: `https://jules.googleapis.com/`

すべてのリクエストに `X-Goog-Api-Key: YOUR_API_KEY` ヘッダーを付与します。

### リポジトリ一覧を取得する

```
curl 'https://jules.googleapis.com/v1alpha/sources' \
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
```

レスポンス例:

```
{
  "sources": [
    {
      "name": "sources/github/myorg/my-backend",
      "displayName": "myorg/my-backend"
    }
  ]
}
```

### セッション（タスク）を作成する

```
curl 'https://jules.googleapis.com/v1alpha/sessions' \
    -X POST \
    -H 'Content-Type: application/json' \
    -H 'X-Goog-Api-Key: YOUR_API_KEY' \
    -d '{
      "title": "認証バグを修正する",
      "prompt": "src/auth/login.py の JWT 検証ロジックに、トークン有効期限チェックが抜けています。公式ドキュメントに沿って修正してください。",
      "sourceContext": {
        "source": "sources/github/myorg/my-backend",
        "githubRepoContext": {
          "startingBranch": "main"
        }
      },
      "automationMode": "AUTO_CREATE_PR"
    }'
```

**主要パラメータ:**

| パラメータ | 説明 |
| --- | --- |
| `title` | セッションの名前 |
| `prompt` | Jules への指示内容 |
| `sourceContext.source` | 対象リポジトリのリソース名 |
| `githubRepoContext.startingBranch` | 作業ベースブランチ |
| `automationMode` | `AUTO_CREATE_PR`（自動 PR）または省略（手動承認） |
| `requirePlanApproval` | `true` にするとプラン確認後に作業開始 |

### セッションのアクティビティを確認する

```
curl 'https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities' \
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
```

### エージェントにメッセージを送る

Jules が作業中または完了後に、追加指示を送ることもできます。

```
curl 'https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:sendMessage' \
    -X POST \
    -H 'Content-Type: application/json' \
    -H 'X-Goog-Api-Key: YOUR_API_KEY' \
    -d '{"prompt": "テストコードも追加してください"}'
```

---

## Python で実装する

REST API を直接叩くことも可能ですが、サードパーティの Python SDK を使うと実装が簡潔になります。

### SDK のインストール

```
pip install jules-agent-sdk
```

### 基本的な使い方

```
from jules_agent_sdk import JulesClient
import time

JULES_API_KEY = "your-api-key"
REPO = "sources/github/myorg/my-backend"

def run_coding_task(prompt: str, branch: str = "main") -> str:
    """Jules にコーディングタスクを依頼して PR URL を返す"""
    with JulesClient(api_key=JULES_API_KEY) as client:
        # セッション作成
        session = client.sessions.create(
            prompt=prompt,
            source=REPO,
            starting_branch=branch,
            automation_mode="AUTO_CREATE_PR",
        )
        print(f"Session created: {session.name}")

        # 完了するまでポーリング（最大10分）
        for _ in range(60):
            time.sleep(10)
            session = client.sessions.get(session.name)
            print(f"Status: {session.state}")
            if session.state in ("COMPLETED", "FAILED"):
                break

        if session.state == "COMPLETED":
            return session.pull_request_url
        else:
            raise RuntimeError(f"Task failed: {session.state}")

if __name__ == "__main__":
    pr_url = run_coding_task(
        prompt="docs/ ディレクトリの README.md を最新の API エンドポイントに合わせて更新してください"
    )
    print(f"PR 作成完了: {pr_url}")
```

### プラン承認ありのフロー

`requirePlanApproval: true` を使うと、Jules がコーディング前に作業計画を提示します。内容を確認してから承認することで、意図しない変更を防ぐことができます。

```
from jules_agent_sdk import JulesClient

def run_with_plan_approval(prompt: str) -> None:
    with JulesClient(api_key="your-api-key") as client:
        # プラン承認モードでセッション作成
        session = client.sessions.create(
            prompt=prompt,
            source="sources/github/myorg/my-backend",
            starting_branch="main",
            require_plan_approval=True,
        )

        # プランが来るまで待機
        import time
        for _ in range(30):
            time.sleep(5)
            activities = list(client.sessions.activities.list(session.name))
            plans = [a for a in activities if a.type == "PLAN"]
            if plans:
                print("Jules のプラン:")
                print(plans[-1].content)
                break

        # 承認
        confirm = input("このプランで進めますか？ (y/n): ")
        if confirm.lower() == "y":
            client.sessions.approve_plan(session.name)
            print("承認しました。Jules が作業を開始します。")
        else:
            print("キャンセルしました。")
```

---

Jules API は Web ブラウザだけでなく、ターミナルから操作できる CLI ツール（Jules Tools）も提供しています。

### インストール

```
npm install -g @google/jules
```

### 基本操作

```
# API キーの設定
jules config set api-key YOUR_API_KEY

# リポジトリ一覧
jules sources list

# タスクを作成
jules session create \
  --source "sources/github/myorg/my-backend" \
  --prompt "認証バグを修正して PR を作成してください" \
  --branch main \
  --auto-pr

# セッション一覧と状態確認
jules session list

# 特定セッションのアクティビティを表示
jules session activities SESSION_ID
```

CLI はスクリプトに組み込むことも可能で、`--json` フラグを付けると機械処理しやすい JSON 形式で出力されます。

---

## GitHub Actions に組み込む

Jules API を GitHub Actions と組み合わせることで、イシューのラベルをトリガーとして自動コーディングを走らせることができます。

### ワークフロー例: `jules-label` ラベルで自動修正

```
# .github/workflows/jules-autofix.yml
name: Jules Auto-fix

on:
  issues:
    types: [labeled]

jobs:
  autofix:
    if: github.event.label.name == 'jules-label'
    runs-on: ubuntu-latest
    steps:
      - name: Jules にコーディングを依頼
        env:
          JULES_API_KEY: ${{ secrets.JULES_API_KEY }}
        run: |
          ISSUE_TITLE="${{ github.event.issue.title }}"
          ISSUE_BODY="${{ github.event.issue.body }}"

          PROMPT="GitHub Issue: ${ISSUE_TITLE}\n\n${ISSUE_BODY}\n\n上記の問題を修正する PR を作成してください。"

          curl -s 'https://jules.googleapis.com/v1alpha/sessions' \
            -X POST \
            -H 'Content-Type: application/json' \
            -H "X-Goog-Api-Key: ${JULES_API_KEY}" \
            -d "{
              \"title\": \"Fix: ${ISSUE_TITLE}\",
              \"prompt\": \"${PROMPT}\",
              \"sourceContext\": {
                \"source\": \"sources/github/${{ github.repository }}\",
                \"githubRepoContext\": {\"startingBranch\": \"main\"}
              },
              \"automationMode\": \"AUTO_CREATE_PR\"
            }"

      - name: イシューにコメントを追加
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🤖 Jules がこのイシューの対応を開始しました。完了次第 PR を作成します。'
            })
```

---

## Jules の主要機能一覧

### MCP サポート（2026年2月〜）

Jules は Model Context Protocol（MCP）をサポートしており、以下のサービスと連携できます。API キー認証で接続します。

| MCP サーバー | 用途 |
| --- | --- |
| Linear | タスク管理 |
| Neon | PostgreSQL データベース |
| Supabase | BaaS 操作 |
| Context7 | コードドキュメント参照 |
| Tinybird | データ分析 |
| Stitch | ETL パイプライン |

### CI 自動修正（2026年2月〜）

Jules が作成した PR で CI が失敗した場合、Jules が自動でログを解析して修正コミットを追加します。手動でのデバッグ作業が不要になります。

### メモリ機能

Jules はリポジトリごとの設定を記憶します。「このリポジトリでは必ず TypeScript strict モードを守る」「テストは必ず Jest で書く」といった設定を一度入力すると、以降のタスクに自動で適用されます。

### ファイルセレクター

Jules に特定のファイルだけを対象として作業させることができます。大規模なリポジトリで範囲を絞って作業させたい場合に有効です。

### コミット著作権の制御

Jules が作成したコミットの著作権表記を 3 パターンから選択できます。

| モード | コミット表記 |
| --- | --- |
| Jules のみ（デフォルト） | `Jules <noreply@jules.google>` |
| 共著 | `Co-authored-by: Jules <noreply@jules.google>` |
| ユーザーのみ | 自分のアカウント名のみ |

---

## API のステータスと注意点

Jules API は **alpha 版**であり、以下の点に注意が必要です。

* エンドポイントの仕様・API キーのフォーマットが将来変更される可能性がある
* 本番環境への組み込みは段階的に行い、エラーハンドリングを十分に実装すること
* API キーは環境変数や Secret Manager で管理し、コードへの直接埋め込みは避けること

---

## まとめ

Google Jules API を使うと、バグ修正・ドキュメント更新・コードレビューといった定型作業を非同期で自動化できます。

* **Sources → Sessions → Activities** の 3 層モデルを理解すれば、REST API は直感的に扱える
* `AUTO_CREATE_PR` モードでエンドツーエンドの自動化が可能
* GitHub Actions と組み合わせることで、イシューのラベルから PR 作成まで全自動化できる
* Gemini 3 Flash（全ユーザー）/ Gemini 3.1 Pro（Pro プラン）という強力なバックエンドで精度が向上

Claude Code や Codex など多くの AI コーディングエージェントが登場している中、Jules の「非同期で PR を作って報告する」というアプローチは、開発フローへの組み込みやすさが際立ちます。まずは alpha API を触って、自チームのワークフローに合ったユースケースを探してみてください。

---

## 参考リンク
