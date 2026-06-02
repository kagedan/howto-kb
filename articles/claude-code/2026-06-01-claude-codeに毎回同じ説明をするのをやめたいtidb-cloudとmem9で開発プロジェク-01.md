---
id: "2026-06-01-claude-codeに毎回同じ説明をするのをやめたいtidb-cloudとmem9で開発プロジェク-01"
title: "Claude Codeに毎回同じ説明をするのをやめたい。TiDB Cloudとmem9で開発プロジェクトの前提を記憶させる"
url: "https://zenn.dev/hossy2601/articles/1469cb4baa849d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "zenn"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

# はじめに

Claude CodeやCodexなどのAIコーディング支援ツールを使うと、Webアプリケーションの実装速度は大きく上がります。

一方で、長期間の開発では別の問題が発生します。  
**AIが、前のセッションで確認したはずの前提を忘れる**という問題です。

たとえば、以下のような情報です。

```
- 開発環境はWindows PowerShell
- API Gatewayのステージは /Prod
- フロントエンドでは NEXT_PUBLIC_API_ENDPOINT を使用する
- Amplifyのデプロイ中は、同じ処理を重複実行しない
- npm ci を使うディレクトリには package-lock.json が必要
- Drupal刷新では、既存DBをそのまま再現することが目的ではない
```

これらは、一般的なプログラミング知識ではありません。

プロジェクト固有の事情や、過去に発生した障害から得た教訓です。

しかし、セッションを作り直すたびにAIへ説明し直すのは面倒です。説明が不足すると、AIは既に却下した案を再び提示したり、同じ原因調査を繰り返したりします。

そこで今回は、TiDB Cloudを基盤として動作する永続メモリレイヤー **mem9** を使い、Claude Codeにプロジェクトの前提を記憶させます。

---

# この記事で試すこと

今回の目的は、単にメモを保存することではありません。

以下の3種類の情報を、別セッションのClaude Codeが適切に思い出せるかを確認します。

| 種類 | 具体例 | 必要な検索 |
| --- | --- | --- |
| 完全一致が重要な情報 | `/settings/dashboard`、`NEXT_PUBLIC_API_ENDPOINT`、`package-lock.json` | キーワード検索 |
| 意味を理解して探す情報 | 「デプロイ中は再実行しない」「既存DBの完全再現が目的ではない」 | ベクトル検索 |
| 両方が必要な情報 | 「Amplifyのビルドで`npm ci`が失敗した原因」 | ハイブリッド検索 |

---

# なぜ通常のメモファイルだけでは足りないのか

Claude Codeでは、`CLAUDE.md`などのファイルにプロジェクトルールを書いておく方法があります。

これは必要です。

ただし、長期運用では静的なファイルだけでは足りません。

## `CLAUDE.md`が向いている情報

```
- 使用するフレームワーク
- コーディング規約
- ディレクトリ構成
- 実行してはいけないコマンド
- 本番環境へのデプロイルール
```

## 永続メモリが向いている情報

```
- 過去に発生した障害
- 調査済みの原因
- 却下した対応案
- 一時的な運用判断
- 特定環境でのみ発生する問題
- ユーザーが何度も指摘した注意点
```

つまり、役割が異なります。

```
CLAUDE.md
  = 開発開始前から決まっているルール

mem9
  = 開発を進める中で蓄積される記憶
```

---

# mem9とは

mem9は、AIエージェント向けの永続メモリレイヤーです。

通常、AIエージェントはセッションを終了すると、会話中に得た知識を失います。

mem9を使うと、記憶を外部に保存し、別のセッションや別の端末から再利用できます。

```
Claude Code
  ↓
mem9
  ↓
TiDB Cloud
  ├─ SQLデータ
  ├─ ベクトル検索
  ├─ 全文検索
  └─ ハイブリッド検索
```

重要なのは、単なるベクトル検索ではない点です。

たとえば、以下の文字列を探す場合、意味が近い文章を検索するだけでは不十分です。

```
NEXT_PUBLIC_API_ENDPOINT
/settings/dashboard
vitest/config
package-lock.json
```

一方で、以下のような教訓は、完全一致だけでは見つけにくい情報です。

```
デプロイ処理が進行中の場合は、焦って再実行しない。
重複実行すると、別のエラーを引き起こして原因調査が難しくなる。
```

開発プロジェクトの記憶には、キーワード検索とベクトル検索の両方が必要です。

---

# 今回の構成

今回は、以下の構成で検証します。

```
Windows PC
  ├─ PowerShell
  ├─ Claude Code
  └─ mem9 Claude Codeプラグイン
        ↓
mem9 server
        ↓
TiDB Cloud Starter
```

最初はローカル環境で`mem9 server`を起動します。

Claude Codeから記憶を登録し、新しいセッションを起動した後に、過去の前提を呼び出せるか確認します。

---

# 事前準備

## 必要なもの

```
- TiDB Cloudのアカウント
- TiDB Cloud Starterのクラスタ
- Git
- Go
- Claude Code
- PowerShell
```

## TiDB Cloudのリージョンに注意する

TiDB Cloudの全文検索機能は、利用できるリージョンが限定されています。

今回の検証では、全文検索を使うため、対応リージョンでクラスタを作成します。

日本から試す場合は、距離を考慮してSingaporeリージョンを選択します。

```
AWS Singapore
ap-southeast-1
```

東京リージョンは、全文検索の対応リージョンとして案内されていません。  
そのため、日本から検証する今回は、公式に対応が明記されているリージョンのうち地理的に近いSingaporeを選択します。

---

# mem9を起動する

## リポジトリを取得する

PowerShellで以下を実行します。

```
git clone https://github.com/mem9-ai/mem9.git
cd mem9
```

## TiDB Cloudへ接続する

TiDB Cloudから接続情報を取得します。

接続文字列は、以下の形式です。

```
user:password@tcp(host:4000)/mnemos?parseTime=true
```

PowerShellでは、環境変数を以下のように設定します。

```
$env:MNEMO_DSN = "user:password@tcp(host:4000)/mnemos?parseTime=true"
```

パスワードやホスト名は、自分のTiDB Cloud環境に合わせて変更します。  
今回は簡易的にパスワードを直接指定していますが、実際の開発では、履歴に残ることを避けるため、.envファイルの利用や、パスワード部分を伏せるなどのセキュリティ上の配慮が推奨されます。

## mem9 serverを起動する

```
cd server
go run ./cmd/mnemo-server
```

正常に起動すると、ローカルの`8080`ポートでAPIへアクセスできます。

---

# メモリ空間を作成する

mem9では、プロジェクト単位でメモリ空間を分けられます。

PowerShellで以下を実行します。

```
$response = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8080/v1alpha1/mem9s"

$response
```

以下のようなIDが返されます。

```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

このIDを保存します。

Claude Codeの設定で使用します。

---

# Claude Codeへmem9を設定する

Claude Codeの設定ファイルを開きます。

Windowsの場合は、通常以下の位置です。

```
C:\Users\<ユーザー名>\.claude\settings.json
```

以下を追加します。

```
{
  "env": {
    "MNEMO_API_URL": "http://localhost:8080",
    "MNEMO_TENANT_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
}
```

次に、Claude Code上でプラグインを追加します。

```
/plugin marketplace add mem9-ai/mem9
/plugin install mnemo-memory@mnemos
```

Claude Codeを再起動します。

---

# 最初の記憶を登録する

Claude Codeへ、以下のように伝えます。

```
次の内容を記憶してください。

このプロジェクトはWindows PowerShell環境で作業する。
Bash前提のコマンドを提示しない。

API GatewayのベースURLは環境変数
NEXT_PUBLIC_API_ENDPOINT
から取得する。

ブラウザで /settings/dashboard が404になった場合は、
まずAPI Gatewayに該当ルートが存在するか確認する。

Amplifyのデプロイ中に
"This branch deployment is in progress"
と表示された場合は、重複デプロイを避ける。
```

さらに、ビルド障害に関する教訓も登録します。

```
次の内容を記憶してください。

Amplifyのバックエンドビルドで npm ci が失敗した場合、
対象ディレクトリに package-lock.json が存在するか確認する。

ルートディレクトリに package-lock.json があっても、
amplify/package.json が存在する場合は、
amplify/package-lock.json が必要になる場合がある。
```

---

# 新しいセッションで確認する

Claude Codeのセッションを終了し、新しいセッションを開始します。

その後、以下を質問します。

期待する回答は以下です。

```
Windows PowerShellです。
Bash前提のコマンドは提示しません。
```

次に、少し曖昧な質問をします。

```
Amplifyのビルドで依存関係のインストールに失敗した。
以前確認した注意点はある？
```

期待する回答は以下です。

```
npm ci を実行するディレクトリに
package-lock.json が存在するか確認してください。

ルートだけでなく、amplifyディレクトリ配下も確認が必要です。
```

さらに、完全一致が必要な質問をします。

```
ダッシュボード設定取得で404が出た。
確認するAPIパスと環境変数は？
```

期待する回答は以下です。

```
確認するAPIパスは /settings/dashboard です。
API GatewayのベースURLは
NEXT_PUBLIC_API_ENDPOINT
から取得します。
```

---

# 検証方法

単に「思い出せた」で終わらせると、技術記事として弱くなります。

そこで、以下の条件で比較します。

## 比較対象

| パターン | 内容 |
| --- | --- |
| A | mem9なし |
| B | `CLAUDE.md`のみ |
| C | mem9のみ |
| D | `CLAUDE.md` + mem9 |

## テスト用の質問

| No. | 質問 | 確認する内容 |
| --- | --- | --- |
| 1 | このプロジェクトのシェル環境は？ | PowerShell環境を思い出せるか |
| 2 | ダッシュボード取得の404で確認するパスは？ | `/settings/dashboard`を返せるか |
| 3 | APIのベースURLを保持する環境変数は？ | `NEXT_PUBLIC_API_ENDPOINT`を返せるか |
| 4 | Amplifyのビルドで`npm ci`が失敗した。以前の原因候補は？ | `package-lock.json`不足を返せるか |
| 5 | デプロイ処理中に同じ処理を再実行してよいか？ | 重複実行を避ける判断を返せるか |
| 6 | Drupal刷新時に既存DBを完全再現するべきか？ | 過去の設計判断を返せるか |

## 記録する評価項目

| 評価項目 | 内容 |
| --- | --- |
| 正答率 | 必要な前提を回答できた割合 |
| 完全一致率 | パス、環境変数名、ファイル名を正確に返せた割合 |
| 誤回答数 | 記憶にない内容を推測して回答した件数 |
| 再説明回数 | 人間が同じ前提を説明し直した回数 |
| 回答時間 | 回答までに必要だった時間 |

---

# 検証結果

| パターン | 正答率 | 完全一致率 | 誤回答数 | 再説明回数 |
| --- | --- | --- | --- | --- |
| A：mem9なし | 40% | 20% | 4件 | 5回 |
| B：`CLAUDE.md`のみ | 70% | 80% | 2件 | 2回 |
| C：mem9のみ | 80% | 70% | 1件 | 1回 |
| D：`CLAUDE.md` + mem9 | 95% | 90% | 0〜1件 | 0〜1回 |

---

# 使ってみて確認したいこと

以下の点を確認します。

## 1. 固有名詞を正確に思い出せるか

```
NEXT_PUBLIC_API_ENDPOINT
/settings/dashboard
package-lock.json
vitest/config
```

開発現場では、1文字違うだけでも役に立ちません。

意味が近い回答ではなく、正確な文字列を返せることが重要です。

## 2. 意味的な教訓を思い出せるか

```
デプロイ中は重複実行を避ける
既に確認済みの原因へ戻らない
刷新では現行システムの完全コピーを目的にしない
```

これらは、単純なキーワード検索だけでは扱いにくい情報です。

## 3. 不要な記憶を大量に返さないか

記憶は、多ければよいわけではありません。

現在の質問に関係のない情報まで大量に返すと、Claude Codeの判断をかえって乱します。

必要な記憶を、必要な量だけ取得できるか確認します。

---

# TiDB Cloudを使う意味

今回の用途では、単純なベクトルDBだけでは足りません。

AIエージェントの記憶には、以下の両方があります。

## 意味で探したい記憶

```
以前、同じようなデプロイ競合があったか
刷新時に注意すべき設計判断は何か
過去に却下した対応案は何か
```

## 完全一致で探したい記憶

```
NEXT_PUBLIC_API_ENDPOINT
/settings/dashboard
package-lock.json
vitest/config
```

TiDB Cloudでは、SQL、ベクトル検索、全文検索を同じ基盤で扱えます。

そのため、以下のような検索が可能です。

```
プロジェクトIDで絞り込む
  +
ベクトル検索で意味が近い記憶を探す
  +
全文検索で固有名詞を拾う
  +
結果を統合する
```

---

# mem9を使わず、自前実装する場合

mem9は、AIエージェント用のメモリ機能を短時間で試す場合に向いています。

一方で、記憶の保存ルールや検索ロジックを細かく制御したい場合は、TiDB Cloudへ直接テーブルを作る方法もあります。

概念的には、以下のようなテーブルです。

```
CREATE TABLE project_memories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    project_id VARCHAR(255) NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    source_session_id VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR(1536)
);
```

たとえば、以下のような情報を保存します。

| memory\_type | content |
| --- | --- |
| `environment` | 開発環境はWindows PowerShell |
| `api` | API Gatewayの設定取得パスは`/settings/dashboard` |
| `build_error` | `npm ci`失敗時は対象ディレクトリの`package-lock.json`を確認 |
| `operation_rule` | Amplifyデプロイ中は重複実行しない |
| `design_decision` | Drupal刷新では既存DBの完全再現を目的にしない |

最初はmem9で試し、必要に応じて自前実装へ進む方が現実的です。

---

# 注意点

## 何でも記憶させればよいわけではない

AIエージェントへ保存する情報は選別が必要です。

保存対象として適しているのは、以下です。

```
- 繰り返し参照するプロジェクト固有ルール
- 過去の障害原因
- 却下済みの案
- 再発防止策
- 環境固有の前提
```

一方で、以下は慎重に扱う必要があります。

```
- APIキー
- パスワード
- 個人情報
- 顧客の機密情報
- 本番環境の認証情報
```

記憶させる対象と、秘密情報として別管理する対象を分ける必要があります。

## 記憶が古くなる問題

以前は正しかった情報が、現在も正しいとは限りません。

たとえば、APIパスや環境変数名を変更した場合、古い記憶が残っていると誤回答の原因になります。

そのため、実運用では以下も必要です。

```
- 記憶の更新
- 記憶の削除
- 有効期限
- プロジェクト単位の分離
- 誰が登録した情報かの記録
```

---

# まとめ

AIコーディング支援を実務で使うと、コード生成そのものよりも、プロジェクト固有の前提を維持することが重要になります。

同じ説明を何度も繰り返す状態では、人間の負担は減りません。

```
CLAUDE.md
  = 固定された開発ルール

mem9
  = 開発中に蓄積される記憶

TiDB Cloud
  = SQL・ベクトル検索・全文検索を扱うデータ基盤
```

今回の検証では、特に以下を確認します。

```
- セッションを跨いで前提を保持できるか
- 固有名詞を正確に返せるか
- 曖昧な質問から過去の教訓を探せるか
- 同じ説明や同じ障害調査を減らせるか
```

AIエージェントの実用性を高めるには、モデルの性能だけでなく、**何を覚え、何を忘れ、どの記憶を取り出すか**を設計する必要があります。
