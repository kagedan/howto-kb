---
id: "2026-04-19-bugsnagに通知されたエラーの調査をaiに任せる-claude-code-smartbear-m-01"
title: "BugSnagに通知されたエラーの調査をAIに任せる ─ Claude Code × SmartBear MCPの活用例"
url: "https://zenn.dev/tsukulink/articles/ffb7a8ab9899e1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

こんにちは、ツクリンクでソフトウェアエンジニアをしているHRT([@hrt\_sc](https://x.com/hrt_sc))です🙋

私の所属しているツクリンクでは[BugSnag](https://www.bugsnag.com/)を利用してエラー監視を行っています。  
エラー対応はどの業務よりも優先で行う必要がありますが、一方で開発タスクもあるため、エラーの調査や原因究明に十分な時間を割くのが難しい場面も多いのではないでしょうか。

そうしたエラー対応における課題に対して、Claude CodeとBugSnagを提供するSmartBear Software社のMCPを活用することによってAIにエラー分析を行ってもらい、エラー対応の手間を削減したので、その方法についてご紹介します。

## 弊社のアラート対応体制と課題

ツクリンクでは、毎日チームごとにローテーションでエラー対応を行っており、基本的に当番日に来たエラーに関しては当番チームが確認するようになっています。  
3チームで回しているため、一ヶ月で約10日ほどアラート対応を行う日があります。  
アラート対応を行う日が多いからこそ、このエラー対応を効率化できれば生産性の向上につながります。

対応手順は決まっているものの、エラーに対して「どこまで深ぼって調べるか」や「ログからどの程度原因を推測できるか」は、担当するエンジニアの経験値や裁量に大きく依存している部分があります。  
そのため、**AIを使ってエラーの分析をサポートさせることで、エンジニアの経験値に関わらず、調査の質を向上できるのではないかと考えました。**

## SmartBear MCPを使ってエラー分析を行う方法

弊社ではClaudeとBugSnagを利用しているため、BugSnagを提供しているSmartBear Software社「[SmartBear MCP Server](https://developer.smartbear.com/smartbear-mcp/docs/mcp-server)」を使用します。

### 動作環境

Claude Codeは記事執筆時点での最新版であるv2.1.92を利用しています。  
Node.jsに関しては、SmartBear MCP Serverの要件でNode.js 20以降が必要とされています。

<https://developer.smartbear.com/smartbear-mcp/docs/getting-started>

### 1. Claude Codeで行うSmartBear MCP Serverの設定

まずは、`.mcp.json`や`~/.claude.json` に下記を追加します。  
`YOUR_BUGSNAG_AUTH_TOKEN`は`Settings > My account > Personal auth tokens`から生成できます。

```
{
  "mcpServers": {
    "smartbear": {
      "command": "npx",
      "args": [
        "-y",
        "@smartbear/mcp@latest"
      ],
      "env": {
        "BUGSNAG_AUTH_TOKEN": "your_personal_auth_token"
      }
    }
  }
}
```

### 2. Claude Codeでエラー分析用スキルを用意

プロンプトで指示を与えるのも良いですが、期待する出力フォーマットや調査手順を効率的に指示できるようにスキルを用意しておくと便利です。  
Anthropic社公式の`skill-creator`コマンドを使って作成することをおすすめします！  
<https://github.com/anthropics/skills/tree/main/skills/skill-creator>

下記がskill-creatorコマンドを利用して作成したスキルになります

```
---
name: bugsnag-analysis
description: BugSnagのエラーをSmartBear MCPで取得し、ソースコードを分析して事象・原因・影響範囲・対策案を日本語でレポートします
allowed-tools: Bash, Read, Grep, Glob, mcp__smartbear__bugsnag_get_current_project, mcp__smartbear__bugsnag_list_projects, mcp__smartbear__bugsnag_get_error, mcp__smartbear__bugsnag_get_event, mcp__smartbear__bugsnag_get_event_details_from_dashboard_url, mcp__smartbear__bugsnag_list_project_errors
argument-hint: "<BugSnagエラーURL または errorId>"
---

# BugSnagエラー初期分析スキル

BugSnagのエラー情報をSmartBear MCPで取得し、ソースコードと照合して根本原因・影響範囲・対策案を含む初期分析レポートを生成します。

## Step 1: エラー情報の取得

`$ARGUMENTS` の形式に応じて適切なツールを選択してください。

**BugSnagダッシュボードURL（`https://app.bugsnag.com/...?event_id=...`）の場合**

`mcp__smartbear__bugsnag_get_event_details_from_dashboard_url` を使用します。URLにはエラーIDとイベントIDの両方が含まれるため、スタックトレース・ブレッドクラム・メタデータを一度に取得できます。

**errorId のみの場合**

`mcp__smartbear__bugsnag_get_error` でエラー集計情報を取得します。スタックトレースの詳細やブレッドクラムが必要な場合は、続けて `mcp__smartbear__bugsnag_get_event` で最新イベントの詳細も取得してください。

## Step 2: エラー詳細の整理

Step 1 で取得した情報から以下を把握します：

- エラークラス・メッセージ
- スタックトレース（プロジェクト内ファイルの特定が目的）
- 初回・最終発生日時 / 発生件数 / 影響ユーザー数
- リリースステージ・アプリバージョン
- BugSnagダッシュボードURL

ブレッドクラムや追加メタデータ（リクエストパラメータ、ユーザー情報など）がある場合は、エラー再現の手がかりとして活用してください。

## Step 3: ソースコード分析

スタックトレースのファイルパス・行番号をもとに、関連するソースコードを調査します。

### 調査手順

1. **エラー発生箇所を読む** — `Read` でスタックトレースの先頭付近のプロジェクトファイルを開き、エラー行の前後20行程度を確認する
2. **呼び出し元を追う** — コントローラ・モデル・サービスの呼び出し関係を `Grep` / `Glob` で辿る
3. **エラーの直接原因を特定する** — nilアクセス・型不一致・存在しないメソッド呼び出しなど、エラーが起きる具体的な理由を特定する

### 調査ツールの使い方

```
# クラス名でファイルを検索
Glob: app/models/**/*user*.rb

# メソッド名や変数名で定義・呼び出しを検索
Grep: pattern="def fetch_users" glob="**/*.rb"

# エラーメッセージのキーワードで関連コードを検索
Grep: pattern="user_id" glob="app/models/**/*.rb"
```

スタックトレースにgemや標準ライブラリのみが含まれる場合は、呼び出し元のプロジェクトコードまで遡って調査してください。

## Step 4: 分析レポートの出力

以下のフォーマットで分析レポートを日本語で出力してください。

---

## BugSnagエラー分析レポート

**エラーID**: `{error_id}`
**BugSnagリンク**: {bugsnag_url}

---

### 事象

- **エラークラス**: `{error_class}`
- **エラーメッセージ**: `{error_message}`
- **初回発生**: {first_seen}
- **最終発生**: {last_seen}
- **発生環境**: {release_stage}（バージョン: {app_version}）

{エラーの症状・発生状況を2〜3文で要約する}

---

### 原因

{スタックトレースとソースコード分析から推定される根本原因を記述する}

- **直接原因**: {エラーが発生している具体的なコードの問題}
- **背景要因**: {なぜその状態になったか、前提条件や設計上の問題など}

---

### 影響範囲

{影響を受ける機能・ユーザー層・業務フローを記述する}

---

### 対策案

{根本原因を解消するためのコード修正・設計改善の提案}

---

### 該当コード

```ruby
# {file_path}:{line_number}
{該当コードの抜粋（前後10行程度）}
```

---

**【注意事項】**
- 原因が確定できない場合は「推定」と明記すること
- 機密情報（APIキー、個人情報等）はレポートに含めないこと
```

## 実際の利用例と出力内容

Claude Codeで`/bugsnag-analysis "<BugSnagエラーURL または errorId>"`を実行します。  
そうすると、Ruby on Railsアプリケーションでバッチ処理中に発生した一般的なエラー（NoMethodError）を想定した架空のエラーに対してではありますが、下記のような出力結果が得られます。

```
BugSnagエラー分析レポート
エラーID: xxxxxxxxx
BugSnagリンク: https://app.bugsnag.com/my-org/my-app/errors/xxxxxxxxxx

事象
- エラークラス: `NoMethodError`
- エラーメッセージ: `undefined method 'upcase' for nil:NilClass`
- 初回発生: 2026-03-10 14:22:00 JST
- 最終発生: 2026-03-13 18:45:12 JST
- 発生環境: production（バージョン: v2.4.1）

管理画面からユーザーリストをCSVエクスポートするジョブの実行中にエラーが発生し、処理が中断しています。特定ユーザーのデータフォーマット変換時に、想定外の空データ（nil）を処理しようとしてクラッシュしている状況です。

原因
取得したスタックトレースおよびソースコード（`app/services/user_export_service.rb`）の調査から、以下の原因が推定されます。

- 直接原因: `UserExportService#format_user_row` メソッド内（42行目）で、ユーザーの `country_code` に対して .upcase メソッドを実行しています。しかし、処理対象のユーザーの `country_code` が nil であったため、`NoMethodError` が発生しています。

- 背景要因: 過去の仕様変更より前に登録された古いユーザーデータには、`country_code` が未設定（nil）のレコードが存在していると推定されます。エクスポート機能の実装時に、この欠損値（NULL）に対する考慮が漏れていたことが根本的な原因です。

影響範囲
CSVエクスポート機能を実行した管理者および運用スタッフ。
エクスポート処理が途中でフェイルするため、リストのダウンロードが完了できない状態となっています。
バックグラウンドジョブでのエラーのため、一般ユーザーのフロントエンド側でのサービス利用に影響はありません。

対策案
該当コードにおいて、nil アクセスを防ぐための修正を提案します。

コードの修正（即時対応）
セーフナビゲーション演算子（ぼっち演算子 `&.`）を使用するか、`to_s` を挟むことでエラーを回避します。

修正例1: user.country_code&.upcase （nilの場合はnilをCSVに出力する）

修正例2: user.country_code.to_s.upcase （nilの場合は空文字をCSVに出力する）

データの整備（恒久対応）
古いレコードの country_code に対し、デフォルト値（例: 'JP'）を設定するデータパッチ（マイグレーション）の実行を検討してください。

該当コード
```ruby
# app/services/user_export_service.rb:38
def format_user_row(user)
  [
    user.id,
    user.full_name,
    user.email,
    user.country_code.upcase, # 42行目: ここでエラーが発生しています
    user.created_at.strftime("%Y-%m-%d")
  ]
end
```
```

## まとめ

これまでは、エラー内容とソースコードを参照して、何が原因なのか、どう対応すべきなのかを確認していたため、見慣れないエラーの場合だと時間がかかってしまいがちでした。  
今回作成したスキルで生成されたような内容をAIに出力させるためにプロンプトで指示を出すにしても、プロンプトを入力する手間がかかりますし、毎回同じフォーマットで出力させるための指示を再現するのも難しいため、Claudeのスキルとして定義しておくことで**コマンド一つで一貫性のある分析レポートを得られるのが大きなメリット**だと感じています。

GitHub Actions等を利用して人間の手を介さずに分析レポートをSlackへ通知するような仕組みを作って自動化することも可能ですが、とは言え最終的に人間がエラーを確認するというフローは変わらないことを考えると、現時点では自動化するメリットは大きくないと考えています。

今後も引き続きエラー分析の効率化については取り組んでいきたいと思います！
