---
id: "2026-04-26-claude-code-routines-スケジュールapigithub-イベントで動く自律型クラウ-01"
title: "Claude Code Routines — スケジュール・API・GitHub イベントで動く自律型クラウド自動化"
url: "https://qiita.com/imk1t/items/e1ce3aa10626d8505855"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-04-26"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

開発チームの日常には、繰り返し発生する定型作業が山ほどあります。毎朝の Issue トリアージ、PR が開かれるたびのレビュー、デプロイ後のスモークテスト、週次のドキュメント更新チェック — どれも重要だけれど、人間が毎回手を動かすには退屈すぎる作業です。

これまでこうした自動化には GitHub Actions や cron ジョブを使うのが定番でしたが、「何をどう実行するか」をすべて事前にスクリプトとして書き下す必要がありました。Claude Code の **Routines** は、このアプローチを根本から変えます。自然言語のプロンプトで「何を達成したいか」を記述するだけで、Claude が自律的に判断・実行してくれるクラウドベースの自動化機能です。

2026 年 4 月 14 日にリサーチプレビューとして公開されたこの機能について、公式ドキュメントに基づいて解説します。

:::message
本記事の内容は 2026 年 4 月時点の情報です。Routines はリサーチプレビューとして提供されており、動作・制限・API サーフェスは今後変更される可能性があります。
:::

## Routines とは

Routines は、**プロンプト・リポジトリ・コネクタをパッケージ化し、トリガーに応じて自動実行する Claude Code の設定**です。Anthropic が管理するクラウドインフラ上で動作するため、ローカルマシンの電源を切っていても実行が継続します。

各 Routine には 1 つ以上のトリガーを設定できます。

| トリガー | 動作 |
|---|---|
| **Schedule** | 毎時・毎日・平日・毎週など定期的に実行 |
| **API** | HTTP POST で任意のタイミングから起動 |
| **GitHub** | PR・Push・Issue などのリポジトリイベントに反応して実行 |

1 つの Routine に複数のトリガーを組み合わせることも可能です。たとえば PR レビュー用の Routine に「毎晩のスケジュール実行」「デプロイスクリプトからの API 呼び出し」「新規 PR オープン時の GitHub トリガー」を同時に設定できます。

### 実行の仕組み

Routines の各実行はフルの Claude Code クラウドセッションとして動作します。通常のインタラクティブセッションと異なり、**パーミッション確認や承認プロンプトは表示されません**。完全に自律的に実行されます。

セッションが実行できる範囲は以下の 3 つで決まります。

1. **リポジトリ**: 選択したリポジトリがクローンされ、デフォルトブランチから開始。Claude は `claude/` プレフィックス付きブランチにのみプッシュ可能（制限解除オプションあり）
2. **環境**: ネットワークアクセスレベル、環境変数、セットアップスクリプトを制御
3. **コネクタ**: Slack・Linear・Google Drive など外部サービスへの MCP 接続

### アイデンティティと所有権

Routines は個人の claude.ai アカウントに紐づきます。チームメンバーとの共有はできず、アカウントの日次実行枠を消費します。Routine が行うすべてのアクション（Git コミット、PR 作成、Slack メッセージなど）は **あなた自身のアカウントとして実行** されます。

## Routine の作成方法

Routine は Web・CLI・Desktop アプリの 3 つから作成できます。いずれも同じクラウドアカウントに保存されるため、CLI で作った Routine が即座に Web に表示されます。

### Web から作成

[claude.ai/code/routines](https://claude.ai/code/routines) にアクセスし、**New routine** をクリックします。

設定項目は以下の通りです。

**1. 名前とプロンプト**

Routine に説明的な名前を付け、Claude が毎回実行するプロンプトを記述します。プロンプトは Routine の最も重要な部分です。自律実行されるため、**何をすべきか・成功とは何かを自己完結的かつ明確に** 書く必要があります。モデルセレクターで使用するモデルも選択できます。

**2. リポジトリ**

Claude が作業する GitHub リポジトリを 1 つ以上追加します。各実行時にクローンされ、デフォルトブランチから開始します。

**3. 環境**

クラウド環境を選択します。環境はセッションのランタイムを制御します。

| 設定 | 内容 |
|---|---|
| ネットワークアクセス | セッション中のインターネットアクセスレベル |
| 環境変数 | API キー・トークンなどのシークレット |
| セットアップスクリプト | 依存関係のインストールなど、セッション開始前に実行するコマンド |

**4. トリガー**

Schedule・API・GitHub から選択します。複数のトリガーを組み合わせることも可能です。

**5. コネクタ**

接続済みの MCP コネクタがデフォルトで全て含まれます。不要なものは削除して、Routine がアクセスできるツールを最小限に絞ります。

### CLI から作成

セッション内で `/schedule` コマンドを実行します。

```bash
/schedule daily PR review at 9am
```

Claude が対話的に必要な情報を収集し、Routine を作成します。CLI ではスケジュールトリガーのみ作成可能で、API・GitHub トリガーは Web から追加します。

その他の管理コマンドもあります。

```bash
/schedule list    # 全 Routine の一覧表示
/schedule update  # Routine の更新
/schedule run     # 即時実行
```

### Desktop アプリから作成

Desktop アプリの **Schedule** ページから **New task** → **New remote task** を選択します。**New local task** を選ぶとローカルマシン上で実行されるスケジュールタスクになり、Routine（クラウド実行）とは異なるので注意してください。

## 3 つのトリガータイプ

### Schedule トリガー

定期的な繰り返し実行に使います。

- **プリセット**: hourly・daily・weekdays・weekly から選択
- **タイムゾーン**: ローカル時刻で入力し、自動変換される
- **カスタム cron**: CLI の `/schedule update` で任意の cron 式を設定可能（最小間隔は 1 時間）
- **stagger**: 実行開始は設定時刻から数分の誤差あり（Routine ごとに一定）

**ユースケース例: バックログメンテナンス**

毎晩 Issue トラッカーをスキャンし、ラベル付け・担当者アサイン・Slack へのサマリー投稿を自動実行。チームは翌朝グルーミング済みのキューから作業を開始できます。

### API トリガー

外部システムから HTTP リクエストで Routine を起動します。アラートシステム・デプロイパイプライン・社内ツールとの連携に適しています。

API トリガーを追加すると、Routine ごとに専用の URL とベアラートークンが発行されます。

```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/trig_01ABC.../fire \
  -H "Authorization: Bearer sk-ant-oat01-xxxxx" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sentry alert SEN-4521 fired in prod. Stack trace attached."}'
```

リクエストボディのオプション `text` フィールドで、アラート本文やログなどの実行時コンテキストを渡せます。成功すると新しいセッション ID と URL が返されます。

```json
{
  "type": "routine_fire",
  "claude_code_session_id": "session_01HJKLMNOPQRSTUVWXYZ",
  "claude_code_session_url": "https://claude.ai/code/session_01HJKLMNOPQRSTUVWXYZ"
}
```

セッション URL をブラウザで開くと、実行状況のリアルタイム監視・変更のレビュー・手動での会話の続行が可能です。

:::message
`/fire` エンドポイントはベータヘッダー `experimental-cc-routine-2026-04-01` が必須です。破壊的変更は新しい日付付きヘッダーバージョンで提供され、直前 2 バージョンは引き続き動作します。
:::

**ユースケース例: アラートトリアージ**

監視ツールがエラー閾値を超えた際に API エンドポイントを呼び出し、アラート本文を `text` で渡します。Routine はスタックトレースを解析し、最近のコミットと照合して修正 PR を自動作成。オンコールエンジニアは空のターミナルからではなく、PR のレビューから始められます。

### GitHub トリガー

リポジトリイベントに反応して自動的にセッションを開始します。Claude GitHub App のインストールが必要です。

対応イベントは多岐にわたります。

| イベント | トリガー条件 |
|---|---|
| Pull request | PR のオープン・クローズ・ラベル付けなど |
| Pull request review | レビューの提出・編集・却下 |
| Pull request review comment | PR diff へのコメント作成・編集・削除 |
| Push | ブランチへのコミットプッシュ |
| Release | リリースの作成・公開・編集・削除 |
| Issues | Issue のオープン・編集・クローズ・ラベル付けなど |
| Issue comment | Issue や PR へのコメント |
| Check run / Check suite | CI チェックの完了やリクエスト |
| Workflow run / Workflow job | GitHub Actions ワークフローの開始・完了 |
| Discussion / Discussion comment | ディスカッションの作成・コメント |
| Merge queue entry | PR のマージキュー出入り |
| その他 | Sub issues、Commit comment、Workflow dispatch、Repository dispatch |

#### PR フィルター

Pull request イベントでは、フィルターで対象を絞り込めます。すべての条件に一致した場合のみトリガーされます。

| フィルター | 対象 |
|---|---|
| Author | PR 作成者の GitHub ユーザー名 |
| Title / Body | PR タイトル・説明文のテキスト |
| Base branch / Head branch | マージ先・マージ元のブランチ |
| Labels | PR に付与されたラベル |
| Is draft / Is merged | ドラフト状態・マージ済みかどうか |
| From fork | フォークからの PR かどうか |

**フィルターの組み合わせ例:**

- **認証モジュール専用レビュー**: base branch が `main`、head branch に `auth-provider` を含む → 認証関連の PR に集中したレビューを実施
- **外部コントリビュータートリアージ**: From fork が `true` → フォーク経由の PR にセキュリティ・スタイルの追加レビューを適用
- **レビュー準備完了のみ**: Is draft が `false` → ドラフト PR をスキップ
- **ラベル駆動のバックポート**: Labels に `needs-backport` を含む → メンテナがタグ付けした場合のみバックポート Routine を実行

:::message
リサーチプレビュー期間中は GitHub webhook イベントに Routine ごと・アカウントごとの時間あたり上限があります。上限を超えたイベントはウィンドウがリセットされるまでドロップされます。
:::

**ユースケース例: カスタムコードレビュー**

`pull_request.opened` をトリガーに設定し、チーム独自のレビューチェックリストを適用。セキュリティ・パフォーマンス・スタイルの問題をインラインコメントで指摘し、サマリーコメントを残します。人間のレビュアーは設計判断に集中できます。

## ユースケース集

公式ドキュメントで紹介されているユースケースをまとめます。

| ユースケース | トリガー | 内容 |
|---|---|---|
| バックログメンテナンス | Schedule（毎晩） | Issue のラベル付け・担当者アサイン・Slack サマリー投稿 |
| アラートトリアージ | API | スタックトレース解析・最近のコミットとの照合・修正 PR 作成 |
| カスタムコードレビュー | GitHub（PR オープン） | チーム独自チェックリストによるインラインコメント |
| デプロイ検証 | API | スモークテスト・エラーログスキャン・go/no-go 判定 |
| ドキュメント乖離検出 | Schedule（毎週） | 変更された API に関連するドキュメントの更新 PR 作成 |
| ライブラリポート | GitHub（PR マージ） | 別言語 SDK への変更移植と対応 PR 作成 |

## 既存の自動化手段との比較

Claude Code エコシステム内にも、Routines 以外の自動化手段がいくつかあります。

| 機能 | 実行場所 | 前提条件 | 適したユースケース |
|---|---|---|---|
| `/loop` | ローカル（セッション内） | セッションが開いている必要あり | セッション中のクイックポーリング |
| Desktop Scheduled Tasks | ローカルマシン | マシンが起動している必要あり | ローカルファイルへのアクセスが必要な作業 |
| **Routines** | Anthropic クラウド | なし（ラップトップオフでも OK） | 自律的・反復的なクラウド作業 |
| GitHub Actions（claude-code-action） | GitHub インフラ | ワークフロー YAML | CI/CD パイプライン内でのタスク |

### GitHub Actions との根本的な違い

GitHub Actions は「ユーザーが書いたスクリプトを順番に実行する」仕組みです。何をどう実行するかは事前にすべて定義する必要があります。

一方 Routines は「プロンプトを受け取り、アウトカムに到達する方法を Claude が自分で判断する」仕組みです。シェルコマンドの実行、リポジトリの Skills の利用、コネクタ経由の外部サービスとの連携を、状況に応じて自律的に組み合わせます。

つまり、GitHub Actions が **手続き的な自動化** であるのに対し、Routines は **宣言的な自動化** と言えます。

## プランと利用制限

Routines は Claude Code on the Web が有効な Pro・Max・Team・Enterprise プランで利用可能です。

| プラン | 1 日あたりの Routine 実行上限 |
|---|---|
| Pro | 5 回 |
| Max | 15 回 |
| Team | 25 回 |
| Enterprise | 25 回 |

- Routine の実行はサブスクリプションの使用量と同様にカウントされます
- 日次上限またはサブスクリプション上限に達した場合、Extra usage が有効な組織は従量課金で実行を継続できます
- 現在の消費量と残り実行回数は [claude.ai/code/routines](https://claude.ai/code/routines) または [claude.ai/settings/usage](https://claude.ai/settings/usage) で確認可能

## ベストプラクティス

### プロンプト設計

Routine は完全自律実行されるため、プロンプトの品質がそのまま成果に直結します。

- **自己完結的に書く**: 対話的な確認はできないため、曖昧さを排除する
- **成功条件を明示する**: 「レビューする」ではなく「セキュリティ・パフォーマンス・スタイルの観点でインラインコメントを残し、サマリーコメントを投稿する」と具体的に書く
- **スコープを絞る**: 1 つの Routine に多すぎる責務を持たせない

### セキュリティ

- **ブランチ制限を活用する**: デフォルトの `claude/` プレフィックス制限を安易に解除しない
- **コネクタを最小限にする**: 不要な外部サービスへのアクセスを削除する
- **環境変数を適切に管理する**: 必要最小限のシークレットのみを設定する
- **実行結果を定期的にレビューする**: 各セッションを開いて Claude の行動を確認する

## まとめ

Claude Code Routines は、開発ワークフローの自動化を「スクリプトを書く」から「目的を伝える」に変える機能です。

- **Schedule トリガー** で毎日・毎週の定型作業を自動化
- **API トリガー** でアラートシステムやデプロイパイプラインと連携
- **GitHub トリガー** で PR レビュー・Issue トリアージをイベント駆動で実行

リサーチプレビューの段階ではありますが、日次のトリアージやコードレビューのような「重要だが繰り返しで退屈な作業」を Claude に任せることで、開発者はより創造的な仕事に集中できるようになります。

## 参考

- [Automate work with routines - Claude Code Docs](https://code.claude.com/docs/en/routines)
- [Introducing routines in Claude Code | Claude Blog](https://claude.com/blog/introducing-routines-in-claude-code)
- [Claude Code overview - Anthropic Docs](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Anthropic adds routines to redesigned Claude Code - 9to5Mac](https://9to5mac.com/2026/04/14/anthropic-adds-repeatable-routines-feature-to-claude-code-heres-how-it-works/)
- [Claude Code routines let AI fix bugs and review code on autopilot - The Decoder](https://the-decoder.com/claude-code-routines-let-ai-fix-bugs-and-review-code-on-autopilot/)
- [anthropics/claude-code - GitHub](https://github.com/anthropics/claude-code)
