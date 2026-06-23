---
id: "2026-06-22-claude-code-github-actionsでレビュー工数を削減した話情シス開発リーダーのた-01"
title: "Claude Code GitHub Actionsでレビュー工数を削減した話〜情シス・開発リーダーのためのチーム導入とセキュアCI設計〜"
url: "https://zenn.dev/nocodesolutions/articles/74655ccf184937"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/89d296fdb099-20260622.png)

## はじめに：なぜ今、チームでのAIコードレビューなのか

「メンバーが各自バラバラに Claude Code を使い始めたが、レビュー基準が人によって違い、品質がばらつく」  
「Pull Request は増える一方で、人手のレビューが追いつかず、マージ待ちが慢性化している」  
「AI を CI（自動化パイプライン）に組み込みたいが、APIキーの漏洩やプロンプトインジェクションが心配で踏み切れない」

情シス担当者・DX推進リード・開発チームリーダーがいま向き合っているのは、「AIコーディングを個人の便利ツールから、**チームの仕組みとして安全に回す**段階」に特有のこうした課題です。個人の生産性は上がったのに、チーム全体ではレビューがボトルネックになり、統制も効かない。この状態を解消する有力な選択肢が **Claude Code GitHub Actions** です。

Claude Code GitHub Actions は、すでに多くの開発現場で標準になっている自動化基盤「GitHub Actions」の上で、Claude を**作業者**として動かす仕組みです。Issue や PR に `@claude` とメンションすれば、Claude が内容を読み取ってコードを実装し、PR を自動で作成します。また、PR が出されたときに自動で一次レビューを走らせることもできます。しかも、リポジトリの `CLAUDE.md` に書いたレビュー基準やコーディング規約に従って動くため、**誰の PR にも同じ基準を効かせられる**のが特徴です。

本記事では、Anthropic 公式ドキュメント（Claude Code GitHub Actions）を基に、情シス・開発リーダー視点での「導入・統制・セキュリティ」を、コピペ可能なワークフローファイル（YAML）付きで解説します。Claude Code 自体の概要は、別記事「AIコーディングエージェント×Claude Code」も参照してください。

**この記事を読むことで得られること:**

* Claude Code GitHub Actions が「個人利用」と何が違い、なぜ今チーム導入が進んでいるのか
* 最新の v1 構文（`prompt` / `claude_args`）でのセットアップと、PRレビュー自動化の作り方
* `CLAUDE.md` によるレビュー基準の標準化（属人化しないAIレビュー）
* CI で AI を動かすときのセキュリティ設計（権限最小化・Secrets・プロンプトインジェクション対策）
* 導入前に確認すべきチェックリストと、コストを暴走させない設定

---

## 1. 基礎知識：Claude Code GitHub Actions とは（個人利用との違い）

### 1.1 「個人のAI」から「チームの仕組み」へ

Claude Code は、もともとは開発者が自分のパソコン（ターミナル）で対話しながら使うツールです。これに対して Claude Code GitHub Actions は、**GitHub のクラウド上**で、決められたきっかけ（トリガー）に応じて Claude を自動で動かす仕組みです。両者は対立するものではなく、「使う場所」と「きっかけ」が違います。

| 観点 | 個人のClaude Code（ローカル） | Claude Code GitHub Actions |
| --- | --- | --- |
| 動く場所 | 開発者のパソコン | GitHub のランナー（クラウド） |
| きっかけ | 開発者が対話で指示 | Issue/PRのイベント（`@claude`等） |
| 主な使い手 | 開発者個人 | チーム全員 |
| 向く用途 | 試行錯誤・探索的な開発 | レビュー自動化・定型作業の標準化 |

> **補足:** ここで言う「ランナー」は、ワークフローを実行する GitHub 上の仮想マシンを指します。コードは GitHub のランナー上で処理され、外部に持ち出されません。

チームリーダーにとっての価値は、**「個人の便利」を「チームの標準」に引き上げられる**点にあります。具体的には、次の3つです。

* **品質の標準化:** 全員の PR に同じレビュー基準を効かせられ、レビューが人によってブレない（属人化しない）
* **レビュー工数とマージ待ちの削減:** PRごとに自動で一次レビューが走るため、人手のレビュー負荷と待ち時間が減る
* **統制:** AIに与える権限やトリガーを設定で管理でき、誰が・どこで使っても同じルールで動く

各自がバラバラに AI を使う状態ではこれらが揃いませんが、GitHub Actions に組み込めば、チーム全体で一度に実現できます。

### 1.2 何ができるのか（3つの代表パターン）

公式ドキュメントが挙げる代表的な使い方は次の3つです。

| パターン | きっかけ | Claudeの動作 |
| --- | --- | --- |
| **Issueからの実装** | Issueに `@claude`で指示 | 内容を解釈し、変更を加えたPRを自動作成 |
| **PRの一次レビュー** | PRが作成・更新された | 差分を読み、規約違反やバグの指摘をコメント |
| **対話的な修正** | PRコメントで `@claude`に依頼 | 指摘に応じてコードを修正し、コミット |

たとえば PR コメントでは、`@claude` に続けて自然文で指示します（日本語でもかまいません）。各コマンドの上のコメントが対訳と意図です。

```
# Issueの説明に沿って、この機能を実装して（実装の依頼）
@claude implement this feature based on the issue description

# このエンドポイントのユーザー認証は、どう実装すべき？（実装方針の相談）
@claude how should I implement user authentication for this endpoint?

# ユーザーダッシュボード画面の TypeError を修正して（バグ修正の依頼）
@claude fix the TypeError in the user dashboard component
```

### 1.3 なぜ「今」なのか

GitHub Actions 自体は2019年から提供されている定番の自動化基盤で、いまさら流行というものではありません。流れが変わったのは、**この実績ある安定した基盤の上に AI エージェントを載せて「作業そのもの」を任せられるようになった**ことです。

* **2025年5月19日:** GitHub Copilot のコーディングエージェントがプレビュー公開
* **2025年5月22日:** Claude 4 の発表と同時に Claude Code が一般提供され、GitHub Actions 連携がベータ提供開始

つまり「AI×GitHub Actions」は、約1年前にほぼ同時に立ち上がった新しい波です。土台が安定していて信頼できるからこそ、企業も安心して試しやすく、急速に広がっています。

---

## 2. 実装のステップ：セットアップとPRレビュー自動化

ここからは、実際に動かす手順を解説します。本記事のコード例は、すべて Claude Code GitHub Actions 公式ドキュメント の v1 構文に準拠しています。

### 2.1 セットアップ（最短ルート）

最も簡単なのは、ターミナルで Claude Code を開いて次のコマンドを実行する方法です。GitHub App のインストールと必要なSecretsの登録を対話的に案内してくれます。

```
# Claude Code のターミナルで実行する
/install-github-app
```

> **補足:** このコマンドの実行にはリポジトリ管理者の権限が必要です。なお、ここで説明しているのは Claude API を直接使う場合の手順です。Amazon Bedrock や Google Vertex AI を経由して使いたい場合は、後述の「3.4 認証方式の選択」を参照してください。

手動でセットアップする場合は、次の3ステップです。

![](https://static.zenn.studio/user-upload/53a03d024d47-20260621.png)

### 2.2 基本のワークフロー（v1構文）

最小構成のワークフローファイルは次のとおりです。`issue_comment` と `pull_request_review_comment` をトリガーにし、コメント内の `@claude` メンションに反応します。

```
name: Claude Code # ワークフローの名前（任意）
on: # 起動するきっかけ（トリガー）
  issue_comment: # Issueにコメントが付いたとき
    types: [created]
  pull_request_review_comment: # PRのレビューコメントが付いたとき
    types: [created]
jobs:
  claude: # ジョブ名（任意）
    runs-on: ubuntu-latest # 実行環境（GitHubのクラウド上のLinux）
    steps:
      - uses: anthropics/claude-code-action@v1 # Claudeを動かす公式アクション（v1）
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }} # Secretsに登録したAPIキーを参照
          # prompt を書かなければ、コメント内の @claude メンションに自動で応答する
```

v1 では、モードの指定（`mode`）が不要になり、設定から**自動判定**されるようになりました。`@claude` メンションに応答する「対話モード」か、`prompt` を渡して即時実行する「自動モード」かを、ワークフローの内容から判断します。

なお、設定は `prompt` と `claude_args` の2つに集約されています。**`prompt` は Claude への指示文**、**`claude_args` は Claude Code に渡す細かい設定（使うモデル、対話の往復回数の上限、許可するツールなど）をまとめて指定する欄**です。以降のコード例に出てくる `--max-turns` や `--allowedTools` は、すべてこの `claude_args` の中身です。

> **ベータ版からの移行に関する注意:** v1 は破壊的変更（＝古い書き方がそのままでは動かなくなる変更）を含みます。ベータ版を使っている場合は、`@beta`→`@v1`、`mode` の削除、`direct_prompt`→`prompt`、`max_turns`・`model`・`custom_instructions` 等を `claude_args` へ移すといった修正が必要です。公式の移行例を引用します。

以下は旧→新の設定の対応関係を示す例です（`steps:` 内の**1ステップだけ**を抜き出しています）。ベータ版を使っていない場合は読み飛ばして構いません。

```
# ベータ版（旧）
- uses: anthropics/claude-code-action@beta
  with:
    mode: "tag" # 旧：動作モードの指定（v1では廃止＝自動判定）
    direct_prompt: "Review this PR for security issues" # 旧：指示の渡し方（v1では prompt に）
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }} # APIキー（新旧で共通）
    custom_instructions: "Follow our coding standards" # 旧：追加指示（v1では claude_args に統合）
    max_turns: "10" # 旧：往復回数の上限（v1では claude_args に統合）
    model: "claude-sonnet-4-6" # 旧：使うモデル（v1では claude_args に統合）

# v1（新）：prompt と claude_args の2つに集約される
- uses: anthropics/claude-code-action@v1
  with:
    prompt: "Review this PR for security issues" # 指示はすべて prompt にまとめる
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }} # APIキー（新旧で共通）
    # CLIオプションはすべて claude_args にまとめる
    claude_args: |
      --system-prompt "Follow our coding standards"
      --max-turns 10
      --model claude-sonnet-4-6
```

> **補足:** v1側の `--system-prompt` / `--max-turns` / `--model` は、それぞれ旧 `custom_instructions` / `max_turns` / `model` に対応します。

### 2.3 PRレビューの自動化

レビュー工数の削減に直結するのが、PR が作成・更新されるたびに Claude が自動でレビューする構成です。次の例は、公式の実例（examples/pr-review-comprehensive.yml）に沿って、PR が開かれた（`opened`）・更新された（`synchronize`）ときにレビューを実行します。

```
name: PR Review # ワークフローの名前（任意）
on: # 起動するきっかけ（トリガー）
  pull_request: # PRに対して起動する
    types: [opened, synchronize] # PRが「作成」または「更新」されたとき
jobs:
  review:
    runs-on: ubuntu-latest # 実行環境（GitHubのクラウド）
    permissions: # このワークフローに与えるGitHub側の権限（最小限に）
      contents: read # コードの読み取りのみ
      pull-requests: write # レビューコメントの投稿に必要
      id-token: write # 認証トークンの発行に必要
    steps:
      - uses: actions/checkout@v6 # リポジトリのコードを取得
      - uses: anthropics/claude-code-action@v1 # Claudeを動かす公式アクション
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }} # Secretsのキーを参照
          prompt: | # Claudeへの指示（レビュー内容）
            REPO: ${{ github.repository }}
            PR NUMBER: ${{ github.event.pull_request.number }}
            このPRの差分をレビューし、CLAUDE.md のレビュー基準に沿って
            規約違反・バグ・抜け漏れを指摘してください。
          # 差分の読み取りとレビューコメント投稿に必要なツールだけを許可する
          claude_args: |
            --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*)"
```

`--allowedTools` で許可している4つのツールの役割は、次のとおりです。これ以外の操作（任意のシェル実行・ファイル変更・push など）はできません。

| ツール | 役割 |
| --- | --- |
| `create_inline_comment` | 該当行へインラインのレビューコメントを付ける |
| `gh pr comment` | PRへ総評コメントを投稿する |
| `gh pr diff` | PRの差分（変更内容）を読む |
| `gh pr view` | PRの情報（タイトル・説明など）を読む |

この構成により、**人間がレビューに着手する前に、規約違反・明らかなバグ・抜け漏れの一次チェックが終わっている**状態を作れます。人間のレビュアーは、AI が拾った指摘を確認したうえで、設計判断など人にしかできない部分に集中できます。

![](https://static.zenn.studio/user-upload/25cac69aacfe-20260621.png)

### 2.4 工数削減の考え方（定量イメージ）

効果は、チームの PR 件数とレビュー時間に比例し、実際の削減率はチームによって異なります。

規模感の参考として、外部の実証研究を挙げます。エンジニア300名が1年間にわたり、AIによるコード生成・自動レビューを実務で利用した研究では、**PRレビューのサイクルタイムが31.8%短縮**したと報告されています（Kumar et al., "Intuition to Evidence: Measuring AI's True Impact on Developer Productivity", 2025）。これは Claude Code 固有の数値ではなく、AIによるレビュー支援全般を対象とした事例ですが、効果の規模感の参考になります。

ポイントは、AI が人間のレビューを**置き換える**のではなく、**一次フィルターとして前段に入る**ことで、人間のレビューの負荷とマージ待ち時間を下げる点です。最終的なマージ判断は必ず人が行う前提は変わりません。

---

## 3. 応用・発展：チーム統制とセキュアなCI設計

ここが、入門記事の多くが踏み込まない、リーダー視点の核心です。「AI に任せたあと、どう統制し、どうリスクを抑えるか」を設計します。

### 3.1 CLAUDE.md でレビュー基準を標準化する

`CLAUDE.md` は、リポジトリのルートに置く設定ファイルで、コーディング規約・レビュー基準・プロジェクト固有のルールを記述します。Claude は PR の作成・レビュー時にこの内容に従うため、**レビュー基準をファイルとして一元管理し、全員の PR に同じ基準を効かせる**ことができます。これが「属人化しないAIレビュー」の正体です。

```
# CLAUDE.md（レビュー基準の例・抜粋）

## レビュー時に必ず指摘すること
- 例外を握りつぶしている箇所（空のcatch、握り潰しのexcept）
- 入力値の検証漏れ（外部入力をそのままSQL・コマンドに渡していないか）
- ハードコードされた認証情報・APIキー
- テストが追加されていない新規ロジック

## コーディング規約
- 関数は1つの責務に絞る。50行を超える関数は分割を提案する
- 命名は既存コードの慣習に合わせる
```

`CLAUDE.md` の設計・書き方そのものは、別記事「CLAUDE.md 完全実装ガイド」で詳しく解説しています。本記事の「レビュー基準の標準化」と合わせて読むと、AIへの指示設計からチームのレビュー体制までを一貫して整えられます。

### 3.2 権限を最小限に絞る（claude\_args）

CI で AI に過剰な権限を与えないことは、統制の基本です。v1 では、許可するツールを `claude_args` の `--allowedTools` で限定できます。考え方は「**そのワークフローに必要なツールだけを許可し、それ以外（特に任意のシェルコマンド実行）は与えない**」ことです。

```
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }} # Secretsのキーを参照
    # 往復回数の上限を設け、必要なツールだけを許可する
    claude_args: |
      --max-turns 5
      --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr diff:*),Bash(gh pr view:*)"
```

> **補足:** `--allowedTools` は許可リスト、`--disallowedTools` は禁止リストです。`gh` コマンドも `Bash(gh pr diff:*)` のように用途を限定して許可し、`Bash` の無制限許可は避けます。**注意点として、`Read`・`Grep` などの読み取り専用ツールだけに絞ると、レビューコメントを投稿できなくなります**。レビュー用途では、上記のように差分確認とコメント投稿に必要なツールを許可したうえで、それ以外を与えないのが安全です。`--max-turns` は対話の往復回数の上限で、コストと暴走の抑制に効きます。

さらに、ワークフローの `permissions` で GitHub 側の権限も最小化します。`permissions` は、**ファイルのトップレベル（`on:` や `jobs:` と同じ階層）に書くと全ジョブに適用**され、**ジョブの中（`jobs:` 配下）に書くとそのジョブだけに適用**されます（2.3 の例ではレビュー用ジョブに絞って書いています）。トリガーも `if:` 条件で `@claude` を含むイベントだけに限定し、無関係なイベントで起動しないようにします。

```
permissions: # GitHub側の権限を必要な範囲だけに絞る
  contents: write # コードの読み書き（write は read を含む。PR作成・修正に必要）
  pull-requests: write # PRへのコメント・更新に必要
  issues: write # Issueへの応答に必要
jobs:
  claude:
    # コメント本文に @claude が含まれるときだけ起動する（無関係なイベントで動かさない）
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
```

### 3.3 CI特有のセキュリティ：プロンプトインジェクションとSecrets

CI で AI を動かすと、ローカル利用にはない固有のリスクが生まれます。リーダーが特に押さえるべきは次の3点です。

| リスク | 何が起きるか | 対策 |
| --- | --- | --- |
| **プロンプトインジェクション** | Issue/PR本文やコメントに紛れ込ませた指示でAIを誘導し、意図しない操作をさせる | トリガーを信頼できる相手に限定、許可ツールを最小化、提案は必ず人がレビューしてからマージ |
| **Secrets漏洩** | APIキーやトークンがログや生成コードに露出する | キーは必ず Secrets 経由で参照（`${{ secrets.* }}`）、コードへの直書き禁止 |
| **過剰な自動実行** | AIが大量のターンを回し、コストや変更が暴走する | `--max-turns`・ジョブのtimeout・concurrency制御で上限を設ける |

> **補足:** プロンプトインジェクションは、外部からの入力（Issue本文など）を AI が「指示」として受け取ってしまうことで起きます。CI では Issue/PR が外部の不特定多数から投稿され得るため、ローカル利用より注意が必要です。多層防御の考え方そのものは、LLM全般のセキュリティとして体系立てて対策する必要があります。

公式も、APIキーは必ず GitHub Secrets を使う、`permissions` は必要最小限にする、**Claude の提案はマージ前に必ず人がレビューする**、という原則を明記しています。AI はあくまで提案者であり、最終承認者は人間である、という前提を崩さないことが重要です。

### 3.4 認証方式の選択（API / Bedrock / Vertex）

データの保管場所（データレジデンシー）や課金を自社でコントロールしたい場合、Claude API の直接利用に加えて、Amazon Bedrock や Google Vertex AI 経由でも利用できます。

| 方式 | 認証 | 向くケース |
| --- | --- | --- |
| Claude API（直接） | `ANTHROPIC_API_KEY`（Secrets） | まず試したい・最短で始めたい |
| Amazon Bedrock | OIDC＋IAMロール（`use_bedrock`） | AWS中心・データ管理を自社で握りたい |
| Google Vertex AI | Workload Identity Federation（`use_vertex`） | GCP中心・静的キーを持ちたくない |

> **補足:** Bedrock / Vertex はいずれも、ダウンロード型の静的な資格情報を使わず、一時的な認証トークンを発行する方式（OIDC / Workload Identity Federation）が推奨されています。静的キーを保管しなくて済むぶん、セキュリティ面で有利です。

なお、MCP（Model Context Protocol）サーバーを `claude_args` の `--mcp-config` で読み込めば、社内ツールや外部サービスと連携した自動化も可能です。MCP の活用は「Claude MCP サーバーおすすめ7選」も参考にしてください。

### 3.5 コストを暴走させない

Claude Code GitHub Actions のコストは、①GitHub Actions の実行時間（GitHub-hosted ランナーの分数を消費）と、②Claude API のトークン使用量の2つから発生します。リーダーとして押さえるべき抑制策は次のとおりです。

> **補足（2026年6月の課金変更）:** 本記事が前提とする `ANTHROPIC_API_KEY`（API従量課金）での利用は、**この課金変更の対象外**です（コストは上記①②のとおり）。影響を受けるのは、Claude のサブスクリプション（Pro / Max）経由で Claude Code GitHub Actions を動かす場合です。2026年6月15日以降、こうしたプログラム経由の利用は、チャットとは別枠の月次クレジットで課金されます（使い切ると既定では停止し、超過分は別途 API 従量課金）。サブスクで運用する場合は、この枠を前提に見積もってください。

---

## 4. まとめと運用チェックリスト

Claude Code GitHub Actions は、「個人の便利なAI」を「チームの安全な仕組み」へ引き上げるための仕組みです。情シス・開発リーダーの視点で要点を整理します。

### 要点の整理

* **レビュー工数の削減と品質の標準化:** PRの一次レビューを自動化し、`CLAUDE.md` でレビュー基準を全員に効かせることで、レビュー待ちの解消と属人化の防止を同時に狙えます。
* **最新の v1 構文で書く:** 設定は `prompt` と `claude_args` の2つに集約されました。旧 `mode` / `direct_prompt` は不要です。
* **統制は「権限最小化」が基本:** `--allowedTools` でツールを絞り、`permissions` と `if:` 条件でGitHub側の権限とトリガーを最小化します。
* **CI特有のリスクに備える:** プロンプトインジェクション・Secrets漏洩・自動実行の暴走に対し、Secrets経由の参照・上限設定・「マージ前に人がレビュー」の原則で多層的に防ぎます。

AI を「勝手に動く不安なもの」から「基準どおりに働く、統制されたチームの一員」へ変えること――それが、Claude Code GitHub Actions をチームに導入する本当の価値です。

### 情シス・開発リーダー向け 導入前チェックリスト

> **使用環境:** 本記事は Claude Code Action v1（2026年6月時点）を前提に記述しています。ワークフローの構文（`prompt` / `claude_args` 等）や操作画面は、今後のアップデートで変わる可能性があります。導入前に公式ドキュメントとリリースページで最新版をご確認ください。

---

## 最後に

私たちは、単にシステムを組むだけの開発会社ではありません。低コストで高品質なAIツールの構築から、ROI（投資対効果）を最大化する導入ロードマップの策定、社内スタッフが自らAIを運用・改善できる体制の構築まで、AI導入の成功に必要なすべてを最初から最後まで丸ごと支援いたします。  
[無料オンライン相談で、最適な導入プランを相談する](https://hjpwym75crze.jp.larksuite.com/scheduler/1ac87ad4828f1fde)

---

## 参考文献

1. Anthropic.「Claude Code GitHub Actions - Claude Code Docs」（v1構文・YAML例・認証・セキュリティの出典。2026年6月15日参照）
2. Anthropic. "Claude Code Action." GitHub.（`docs/security.md`〔許可ツール・セキュリティ〕、および `docs/migration-guide.md`・`docs/usage.md`〔ベータ→v1 の移行、`custom_instructions` → `--system-prompt` の対応〕の出典。2026年6月15日参照）
3. Anthropic. "Introducing Claude 4."（2025年5月22日のClaude Code一般提供・GitHub Actions連携ベータ提供の根拠。2026年6月15日参照）
4. GitHub. "GitHub Copilot coding agent in public preview." GitHub Changelog, 2025年5月19日.（AI×GitHub Actionsの立ち上がり時期の根拠。2026年6月15日参照）
5. Kumar, Anand, et al.「Intuition to Evidence: Measuring AI's True Impact on Developer Productivity」arXiv:2509.19708, 2025年9月.（PRレビューのサイクルタイム31.8%短縮の出典。AIレビュー支援全般の実証研究。2026年6月15日参照）
6. Anthropic.「Use the Claude Agent SDK with your Claude plan」Claude Help Center.（2026年6月15日からのAgent SDK・Claude Code GitHub Actions 等の別建てクレジット課金への移行の根拠。2026年6月15日参照）
