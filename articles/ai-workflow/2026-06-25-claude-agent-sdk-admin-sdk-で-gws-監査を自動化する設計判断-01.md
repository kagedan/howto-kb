---
id: "2026-06-25-claude-agent-sdk-admin-sdk-で-gws-監査を自動化する設計判断-01"
title: "Claude Agent SDK × Admin SDK で GWS 監査を自動化する設計判断"
url: "https://qiita.com/drasenas/items/f3f370309926796d8191"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "Python", "TypeScript"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

Anthropic が提供する Claude Agent SDK を使うと、Python や TypeScript からエージェントをプログラム的に起動し、外部 API をエージェントの「ツール」として組み込める。本記事では、Google Workspace（以下 GWS）の Admin SDK Reports API をそのツールとして設計し、月次コンプライアンス監査の自動化ワークフローを構築する際の設計判断を整理する。

## この記事を読んだほうが良い人

- Claude Agent SDK の概要は把握しているが、GWS 管理系 API との組み合わせ方がイメージできていない情シス担当者
- Google Apps Script（以下 GAS）で書いた月次 GWS 監査スクリプトをより柔軟な仕組みに切り替えたいと考えている人
- Admin SDK Reports API を使った監査自動化を検討しているが、GAS / Claude Agent SDK / Batch API の使い分け判断に迷っている人

## GAS・Claude Agent SDK・Batch API の使い分け判断

月次 GWS 監査を自動化する手段は複数ある。GAS・Claude Agent SDK・Claude Batch API の 3 つを比較すると、それぞれの役割の違いが明確になる。

| 観点 | GAS | Claude Agent SDK | Claude Batch API |
|---|---|---|---|
| 主な役割 | 定型集計・Sheets 出力 | 自然言語指示によるオンデマンド調査 | 大量ログの非同期一括処理 |
| 実行形式 | 時間ベーストリガ | プロンプト起動（随時） | 非同期ジョブキュー |
| Claude 推論 | なし（別途連携が必要） | 組み込み | 組み込み（遅延あり） |
| 向くケース | 毎月同じ形式で集計を回す | 「今月は特権操作の変更に絞って確認して」 | 180 日分を月 1 回まとめて分析 |

GAS は「決まった集計を決まった形式で出力する」ことに特化している。ロジックが固定されている限りはメンテナンスコストも低く、情シスの現場で広く使われてきた実績がある。

Agent SDK が選択肢に入るのは、「調査観点が毎月変わる」場面だ。先月は外部共有の異常を確認したい、今月は二段階認証未設定ユーザーの増減を確認したい、というように問いが変わる場合、GAS ではロジックを書き直す手間が出てくる。Agent SDK を使えば、プロンプトを変えるだけで調査観点を切り替えられる。

Batch API はコスト最適化の観点から有効で、大量のログを非同期でまとめて処理したい場合に選ぶ。リアルタイム性や対話的な調査には向かない。

## Admin SDK Reports API を監査ツールとして設計する

Admin SDK Reports API（以下 Reports API）の `activities.list` は、GWS 上で発生した操作ログを取得するエンドポイントだ（Admin SDK: Reports API 公式ドキュメントより）。ログの種別はアプリケーション名で指定する。月次コンプライアンス監査でよく確認するカテゴリは次の 3 つだ。

- **管理者操作ログ（admin）**: スーパー管理者の付与・剥奪、ドメイン設定変更、外部転送設定の変更
- **ログインログ（login）**: 不審なログイン試行、通常とは異なる地点からのアクセス
- **OAuth トークンログ（token）**: 未承認アプリへのアクセス許可、広いスコープの付与状況

取得できる期間は最大 180 日分だ（Admin SDK Reports API 公式リファレンスより）。

### Bash ツール経由 vs カスタムツール定義

Agent SDK で Reports API を使う設計パターンには大きく 2 通りある。

**Bash ツール経由**では、エージェントが内蔵の Bash ツールを使い、Reports API を呼ぶ Python スクリプトをその場で実行する。起動コストが低くシンプルな一方、エージェントが Bash を通じて広範な操作を行える状態になるため、実行環境の権限設計を慎重にする必要がある。

**インプロセス型カスタムツール定義**では、Claude Agent SDK が持つインプロセス MCP サーバー機能を使い、Reports API の呼び出しを単一のツールとして登録する。「どのログカテゴリを、何日分取得するか」だけを受け付ける設計にすることで、エージェントが呼べる操作をピンポイントに絞れる。外部 MCP サーバーを別プロセスで立ち上げる必要がない点も、小規模な情シス組織では実装コストの面で利点になる。

以下は Agent SDK の `query()` を使って監査チェックを指示する概念例だ（概念例。`claude_agent_sdk` パッケージ準拠、パターンを簡略化）。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_audit_check():
    async for message in query(
        prompt=(
            "Admin SDK Reports API の管理者操作ログ（admin）から"
            "先月 1 か月分を取得し、スーパー管理者権限の変更と"
            "外部転送設定の変更をリストアップしてください。"
            "異常と判断した操作があれば理由とともにレポートしてください。"
        ),
        options=ClaudeAgentOptions(
            allowed_tools=["Bash"],
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(run_audit_check())
```

プロンプトを書き換えるだけで調査観点を切り替えられるのが GAS との大きな違いだ。GAS で同じ柔軟性を実現しようとすると、条件分岐のロジックが次第に複雑になっていく。

## OAuth スコープを最小権限に絞る設計判断

Reports API の用途別 OAuth スコープは次の 2 種類が用意されている（Google Workspace Admin SDK 認可ドキュメントより）。

- `https://www.googleapis.com/auth/admin.reports.audit.readonly`：監査ログの読み取り（管理者操作・ログイン・OAuth トークン等）
- `https://www.googleapis.com/auth/admin.reports.usage.readonly`：利用状況データの読み取り（ストレージ使用量等）

コンプライアンス監査が目的であれば、**`admin.reports.audit.readonly` 1 つで足りるケースがほとんどだ**。

情シスが陥りがちな権限過大付与パターンを 3 つ挙げる。

**パターン 1：Directory API のスコープを同居させてしまう**。監査ログに表示名や部署情報を添えたいとき、Admin Directory API の読み取りスコープを同じサービスアカウントに追加してしまいやすい。この構成はサービスアカウントが漏洩した際のインパクトを大きくする。ユーザー情報の取得が必要なら、ログ取得処理と Directory 参照処理を別のサービスアカウントに分離する設計を検討したい。

**パターン 2：将来を見越して `usage.readonly` を先付けする**。「いつか利用状況も見たいかもしれない」という理由でスコープを先に追加すると、後の権限棚卸しで根拠の説明ができなくなる。スコープは「実際に使う時点で追加する」が原則だ。

**パターン 3：ドメイン全体の委任設定を広く渡す**。Reports API をサービスアカウントから呼ぶには、管理コンソールのセキュリティ設定からドメイン全体の委任（Domain-wide Delegation）でサービスアカウントに権限を委任する設定が必要になる。この委任スコープを「とりあえず広く」すると、サービスアカウントが実質的に広範な管理者権限を持つ状態になる。Reports API 専用のサービスアカウントを用意し、委任スコープを必要最小限に絞る設計を原則にしたい。

## 定期実行・エラー通知・GAS との組み合わせ

Agent SDK ベースの監査エージェントを月次で運用するには、Cloud Scheduler や cron でスクリプトを定期起動する構成が基本になる。

設計時に押さえておきたい点が 3 つある。

**エラーを必ず通知経路に乗せる**: エージェントが API 呼び出しに失敗したり Claude の応答がタイムアウトしたりした場合、無音で終了しないよう例外を捕捉して Slack や Google Chat に通知する処理を組み込む。「静かに失敗している」監査スクリプトは、本来検出すべき問題を見逃す原因になる。

**出力の保存先を最初に決める**: エージェントが生成した監査レポートは、Google Drive の特定フォルダや Cloud Storage に自動保存する設計にしておくと、後からの参照や監査証跡の管理が楽になる。

**GAS との分業を検討する**: GAS で Reports API を使った定型集計をすでに動かしている場合、すべてを Agent SDK に置き換える必要はない。「GAS で定型集計、Agent SDK で例外調査」という分業構成は実務でも機能する。毎月決まった形式のレポートは GAS が担い、異常値を深掘りする調査だけ Agent SDK のエージェントに指示するイメージだ。GAS ベースの Reports API 活用については、DRASENAS の既存記事「Admin SDK Reports API で GAS・AppSheet の利用実態を可視化する」も参照してほしい。

## 導入前に確認したい設計判断のポイント

Claude Agent SDK と Admin SDK Reports API の組み合わせは、手作業の月次監査から抜け出す有力な選択肢だ。ただし、導入前に整理しておくべき判断がある。

まず、調査観点が毎月変わるかどうかを確認する。観点が固定されているなら GAS で十分で、Agent SDK を持ち込む必要はない。Agent SDK が力を発揮するのは「今月はこれを中心に見てほしい」と指示の中身が変わるケースだ。

次に、OAuth スコープの設計を導入前に一度整理する。Reports API の監査用途であれば `admin.reports.audit.readonly` だけを付与する方針を原則にし、追加が必要になった時点でスコープを都度審査する運用にする。

最後に、エラー通知と出力保存先は「動いたら考える」ではなく最初から設計に含める。自動化の恩恵を受けながら「静かに失敗する」状態を防ぐためだ。

設計方針が固まれば、実装のハードルは想像よりずっと低い。

## コーポレートITのご相談はお気軽に

この記事で書いたような業務改善・自動化の設計から実装まで、DRASENASではコーポレートITの現場に寄り添った支援を行っています。
「まず相談だけ」でも大歓迎です。[DRASENAS 公式サイト](https://www.drasenas.com?utm_source=qiita&utm_medium=article_body&utm_campaign=claude-agent-sdk-admin-sdk-compliance-automation)からお気軽にどうぞ。

---
※ この記事は [DRASENAS Blog](https://www.drasenas.com/blog/claude-agent-sdk-admin-sdk-compliance-automation/?utm_source=qiita&utm_medium=article&utm_campaign=claude-agent-sdk-admin-sdk-compliance-automation) の転載です。オリジナルではコードや設定手順が随時アップデートされています。
