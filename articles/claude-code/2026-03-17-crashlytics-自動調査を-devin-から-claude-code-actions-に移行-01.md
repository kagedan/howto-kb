---
id: "2026-03-17-crashlytics-自動調査を-devin-から-claude-code-actions-に移行-01"
title: "Crashlytics 自動調査を Devin から Claude Code Actions に移行できるか検証"
url: "https://qiita.com/mgre_tanabe/items/b9c2230c5cb343365876"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

> 注: 本記事の料金・モデル・機能の比較は 2026年3月時点 のものです。AIエージェントの進化は非常に速く、料金改定や新モデルのリリースで状況が変わる可能性があります。最新の情報は各サービスの公式ドキュメントをご確認ください。

[前回の記事](https://qiita.com/mgre_tanabe/items/74752d1ba32b54fad954)では、Devin + GitHub Actions で Crashlytics クラッシュ調査を自動化する仕組みを紹介しました。検知から調査・判定までを自動化し、エンジニアの一次調査工数をゼロにできた一方で、運用を続ける中で コストが課題になってきました。

前回記事では1件あたり約2ACU（数百円相当）と紹介しました。Devin の Billing ダッシュボードで実ACUを確認したところ、平均約2.5ACU/件（1.1〜3.4の幅あり）でした。前回記事の見積もりよりやや重く、PR作成を含むケースで特にACUが増える傾向があります。実作業時間は 10〜20分程度（スタックトレースN/Aの簡易調査で約10分、PR作成を含む詳細調査で約20分）です。

| 指標 | 前回記事時点 | Billing 実測値 |
| --- | --- | --- |
| Devin 実作業時間 | 10〜30分/件 | 10〜20分/件 |
| Devin ACU/件 | 約2 ACU | 約2.5 ACU（1.1〜3.4） |
| 1件あたりコスト | 数百円 | 約$5.6（約840円） |
| 月30件の場合 | — | 約$170/月 |

月額 $170 は「一次調査の自動化」としてはやや割高に感じます（エンジニアの手動調査30分〜1時間/件の工数削減と比較しての評価です）。一次調査として必要な品質を維持したまま、もっとコストを抑えられないか — そこで Claude Code Actionsへの移行を検証してみました。

## Claude Code Actions とは

[Claude Code GitHub Actions](https://code.claude.com/docs/ja/github-actions) は、GitHub Actions 上で Claude Code を実行できる仕組みです。Issue や PR への `@claude` コメントをトリガーに、コード調査や結果投稿を自動で行えます。

Devin との主な違いは以下の点です:

|  | Devin | Claude Code Actions |
| --- | --- | --- |
| 実行環境 | Devin 専用 VM | GitHub Actions ランナー |
| トリガー | Devin API (`POST /v1/sessions`) | `@claude` コメント |
| 完了検知 | ポーリング（60秒間隔） | 不要（自動でコメント投稿） |
| 課金 | ACU 従量（$2.25/ACU） | Claude Team などのサブスクリプション、または API トークン従量 |
| リポジトリアクセス | Devin ワークスペースに連携済み | `gh repo clone` で都度 clone |

セットアップは3ステップです:

1. [Claude GitHub App](https://github.com/apps/claude) をリポジトリにインストール
2. `ANTHROPIC_API_KEY`（API 従量課金の場合）または `CLAUDE_CODE_OAUTH_TOKEN`（Claude Team などのサブスクリプションの場合）をリポジトリシークレットに追加
3. `.github/workflows/claude.yml` を配置

## 移行の全体像

データ収集部分（第1〜2段階）はそのまま流用し、Devin API 呼び出し部分だけを `@claude` コメントに置き換えるのが移行の要点です。

### Before（Devin）

### After（Claude Code Actions）

変わる部分と変わらない部分を整理すると:

| 処理 | 変更 |
| --- | --- |
| GAS（アラート検知） | 変更なし |
| GitHub Actions（データ収集・緊急度判定） | 変更なし |
| プロンプトテンプレート | ほぼ変更なし（`{{ISSUE_URL}}` の除去程度） |
| AI エージェント呼び出し | Devin API → `@claude` コメント投稿 |
| 完了検知 + Slack 返信 | ポーリング廃止 → 不要に |

ポーリングが不要になったのは、実運用上大きな改善です。Devin では完了を検知するために GitHub Actions ランナーを最大2時間（$0.96 相当）待機させていましたが、Claude Code Actions は `@claude` コメントをトリガーに別のワークフローとして非同期実行されるため、データ収集ジョブは Issue 作成とコメント投稿で即座に終了します。

## 移行手順

### Step 1: claude.yml を追加

Claude Code Action のワークフローを追加します。`@claude` を含むコメントに反応して起動します:

```
name: Claude Code
on:
  issue_comment:
    types: [created]

jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          github_token: ${{ secrets.ORG_GITHUB_TOKEN }}
          claude_args: >-
            --model claude-opus-4-6
            --allowedTools "Bash(git:*)" "Bash(gh:*)" "Bash(grep:*)"
            "Bash(find:*)" "Bash(cat:*)" "Read" "Glob" "Grep" "Write"
```

ポイント:

* `--model claude-opus-4-6` で最高精度のモデルを指定（デフォルトは Sonnet）
* `--allowedTools` で git/gh CLI やファイル読み取りを許可。`actions/checkout@v4` でワークフロー実行リポジトリ自体を取得し、Claude が調査対象の別リポジトリを `gh repo clone` で追加取得する構成
* `ORG_GITHUB_TOKEN` は、組織内の別リポジトリへのアクセスや、`GITHUB_TOKEN` 利用時のイベント連鎖制約を避けるために使用。GitHub Actions では再帰防止の制限があり、後続ワークフロー起動を含む構成では PAT の方が扱いやすい場合があります

### Step 2: Devin API 呼び出しを `@claude` コメントに置換

なお、旧構成では Devin API の `v1/sessions` を利用していましたが、Devin は現在 v3 API が主系となっています。本記事では比較のため当時の構成をそのまま掲載しています。

`crashlytics-investigation.yml` の Devin セッション作成ステップを、`@claude` コメント投稿に置き換えます:

```
# Before: Devin API 呼び出し + ポーリング
- name: Trigger Devin Investigation
  run: |
    curl -X POST "https://api.devin.ai/v1/sessions" \
      -H "Authorization: Bearer $DEVIN_API_KEY" \
      -d "$(jq -n --arg prompt "$(cat prompt.md)" '{prompt: $prompt}')"
# ... 60秒間隔ポーリング（最大2時間）...

# After: @claude コメント投稿（これだけ）
- name: Trigger Claude investigation
  uses: actions/github-script@v7
  with:
    github-token: ${{ secrets.ORG_GITHUB_TOKEN }}
    script: |
      const prompt = require('fs').readFileSync('claude-prompt.md', 'utf8');
      await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: issueNumber,
        body: `@claude ${prompt}`
      });
```

ポーリングと Slack 返信のステップは削除できます。

### Step 3: プロンプトの微調整

プロンプトテンプレートはほぼそのまま流用できました。変更したのは:

* `{{ISSUE_URL}}` プレースホルダーの除去（Claude は自分が起動された Issue を自動認識する）
* リポジトリの clone 指示を `gh repo clone <org>/<repo>` 形式に明記
* Devin 固有の表現（「セッション」等）を一般的な表現に修正

前回記事で述べた「プロンプト1ファイルで調査を制御する」設計は、Claude Code Actions でもそのまま維持できています。

## 調査結果の比較

実運用で作成された同一の Crashlytics Issue 20件に対して、同じ Issue 本文・スタックトレース・トレンド情報を入力として、Devin と Claude の両方で調査を実行しました。なお、この比較は正解ラベル付きの厳密な評価ではなく、一次調査の置き換え先として実用上十分かを確認する目的で行ったものです。

### 判定傾向の比較

20件全件で両エージェントの判定が出揃った結果:

|  | Devin | Claude |
| --- | --- | --- |
| 🟡 経過観察 | 20件（100%） | 17件（85%） |
| 🟢 対応不要 | 0件 | 3件（15%） |
| 🔴 要エスカレーション | 0件 | 0件 |

Devin との一致率: 20件中17件一致（85%）。なお、この一致率は Devin を正解ラベルとみなした精度ではなく、判定傾向の差分を見るための参考値です。不一致の3件はいずれも、収束済みのクラッシュ（直近24時間の発生が0件）に対して Claude が追加の文脈を踏まえて 🟢対応不要と判断したケースでした。Devin は同じケースで慎重に 🟡経過観察としています。

### 調査品質の比較

| 評価項目 | Devin | Claude |
| --- | --- | --- |
| コード参照の具体性 | ◎ 行番号 + コミットハッシュ付き | ◎ 同等 |
| 処理速度 | 10〜20分 | **3〜9分** |
| 修正 PR の自動作成 | ◎（自律的に作成） | ○（条件付きで可能） |
| 既存の修正履歴の発見 | ○ | ◎（git log で追跡） |

Claude の方が処理が速い（3〜9分 vs 10〜20分）のは、GitHub Actions ランナー上で直接実行されるため、Devin のような VM 起動のオーバーヘッドがないためと思われます。

なお、Claude の処理時間は GitHub Actions のジョブ実行時間、Devin の処理時間は Devin のセッションログ上の開始〜完了メッセージの時間差です。厳密に同条件の比較ではない点にはご留意ください。

### コスト比較

Devin のコストは Billing ダッシュボードの実ACUです。Claude のコストは、[Anthropic の公開料金表](https://platform.claude.com/docs/ja/about-claude/pricing)をもとにした概算です。公開ページ間で表記が異なる箇所や、200Kトークンを超える長文入力時のプレミアム価格条件もあるため、実運用コストは入力サイズ・出力サイズ・契約形態に応じて変動します。最新の単価は公式ドキュメントをご確認ください。

今回は Claude Team サブスクリプション（`CLAUDE_CODE_OAUTH_TOKEN` で認証）で実行したため、API 従量課金での追加課金は発生していません。以下の表は API 従量課金で利用した場合のコスト目安です。

|  | Devin | Claude Code Actions |
| --- | --- | --- |
| 1件あたり | 約$5.6（2.5 ACU 実測） | 推定$1〜4（API公開単価からの概算。サブスク利用時は追加課金なし） |
| 月30件 | 約$170 | 推定$30〜120 |
| 備考 | 実測ACU | API従量課金時の概算 |

## やってみてわかったこと

### プロンプトとAPI呼び出しの分離が効いた

プロンプトの構造（二段階判定・確信度・出力フォーマット）はそのまま Claude に適用できました。移行作業の大半は API 呼び出し方式の変更（Devin API → [@claude](/claude "claude") コメント）で、調査ロジック自体の書き換えはほぼ不要でした。調査ロジックをプロンプト1ファイルに集約し、ツール固有の接続部分と分離していたことが効いています。

### ポーリングの廃止

Devin 版では完了検知のためにポーリングループ + タイムアウト + Slack 返信が必要でしたが、Claude Code Actions では `@claude` コメント投稿だけで完結します。ワークフローの見通しが良くなり、GHA の分数消費も減りました。

### Devin の強みが活きるケース

移行を検討している理由はコストであり、Devin の品質に不満があるわけではありません。現時点では以下の点で Devin が優れていると感じます:

* **修正 PR の自律的な作成**: Claude でも可能ですが、`allowedTools` の設定がやや複雑になります
* **ブラウザ操作**: 外部サイトの Issue ページや Release Notes を確認する調査は、GHA ランナー上で動く Claude では対応できません

### 移行判断の進め方

今回は同一の20件に対して両エージェントを実行し、判定の一致率とコスト差を数値で確認しました。精度だけでなく、TCO（ポーリング廃止による GHA 分数削減を含む）・保守性・ロックイン度を含めた評価が、移行の妥当性を判断するには必要だと感じています。

## おわりに

Crashlytics クラッシュ調査の自動化について、Devin から Claude Code Actions への移行を検証しました。コストを大きく抑えつつ、一次調査の置き換え先としては実用上十分な品質が得られており、移行は十分に現実的だと考えています。

|  | Devin | Claude Code Actions |
| --- | --- | --- |
| 1件あたりコスト | 約$5.6 | 推定$1〜4（サブスク利用時は追加課金なし） |
| 処理速度 | 10〜20分/件 | 3〜9分/件 |
| 判定一致率 | — | 85%（20件中17件一致） |
| PR 自動作成 | ◎ 自律的 | ○ 設定次第 |
| セットアップ | Devin ワークスペース連携 | GitHub App + Secret |

今回の検証で改めて感じたのは、プロンプト設計をツール非依存にしておくことの価値です。調査ロジックと API 接続を分離しておけば、ツールの乗り換えは接続部分の書き換えだけで済みました。AI エージェントの進化が速い以上、特定ツールへのロックインを避けて柔軟に切り替えられる設計にしておくことは、自動化を持続的に運用するための前提条件だと感じています。
