---
id: "2026-06-29-ローカルai-gateway-anthropic-tool-use-を試してみました-01"
title: "ローカルAI Gateway - Anthropic Tool Use を試してみました"
url: "https://zenn.dev/hisa_tech_2973/articles/a7d7d43db6011a"
source: "zenn"
category: "ai-workflow"
tags: ["API", "OpenAI", "zenn"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

前回の記事では、ローカルAI Gatewayに**Provider Adapter**を実装しました。

<https://zenn.dev/hisa_tech_2973/articles/cada005f5e26fe>

今回は実装の話ではなく、

**次の実装に向けた動作確認**

の内容を紹介します。

## 次に実装したいこと

これまでのローカルAI Gatewayでは、

* **機密情報の検出**（APIキー・メールアドレスなどを検知）
* **監査ログ**（全リクエストを記録）
* **Policy Engine**（検出結果をYAMLで制御）
* **Provider Adapter**（OpenAI・Anthropicへの統一インターフェース）

を実装してきました。

次に取り組みたいのは、

**AIが外部ツールに対して実行できる操作を制御すること**

です。

例えばGitHubなどの操作を、AIに好き勝手にさせるのではなく、

**Policy Engineのように、ポリシーで制御できるようにしたい**

と考えています。

## そのために理解が必要だったこと

ただ、その実装に入る前に確認しておきたいことがありました。

**Anthropic API はツールをどのように扱うのか**

ということです。

「AIが操作を実行する」と言うと、AIが直接APIを叩いているように聞こえます。

しかし実際のしくみは異なります。

その点を理解するために、今回は**Anthropic Tool Use**の動作確認を行いました。

## 確認したかった流れ

今回確認したかったのは、次の一連の流れです。

## 試した構成

Docker で動かせるシンプルな検証用のサンプルを作りました。

実際のGitHub APIは叩かず、**ダミーデータを返す** `github_list_issues` というツールを定義して動作を確認しました。

## ツール定義

ツールはAPIリクエストの `tools` フィールドに含めます。

```
{
  "name": "github_list_issues",
  "description": "List GitHub issues for a repository.",
  "input_schema": {
    "type": "object",
    "properties": {
      "owner": { "type": "string" },
      "repo":  { "type": "string" }
    },
    "required": ["owner", "repo"]
  }
}
```

ClaudeはこのJSON Schema定義を見て、

**「このツールが使えるなら使いたい」**

と判断したときに `tool_use` を返します。

## 1回目のリクエスト

ユーザーメッセージとツール定義を一緒に送ります。

```
st-hisatoshi-2973/startup-security-kit のIssue一覧を確認してください
```

Claudeは `github_list_issues` が必要と判断し、次のような `tool_use` を返しました。

```
{
  "type": "tool_use",
  "id": "toolu_01XXXXXXXXXXXXXXX",
  "name": "github_list_issues",
  "input": {
    "owner": "st-hisatoshi-2973",
    "repo": "startup-security-kit"
  }
}
```

Claudeはツールを実行していません。

**「このツールをこの引数で呼んでほしい」と返しているだけです。**

## アプリ側でツールを呼び出す

`tool_use` を受け取ったアプリ側が、実際の処理を行います。

今回はダミーデータを返しました。

```
func dummyIssues() string {
    issues := []Issue{
        {Number: 1, Title: "Add AI Gateway policy document", State: "open"},
        {Number: 2, Title: "Improve secret detection examples", State: "open"},
    }
    b, _ := json.Marshal(issues)
    return string(b)
}
```

## 2回目のリクエスト

1回目の会話履歴に `tool_result` を加えて再度送ります。

```
メッセージ構造:
  {user}      → 最初のユーザーメッセージ
  {assistant} → tool_use を含む1回目のレスポンス
  {user}      → tool_result（ツールの実行結果）
```

`tool_result` の `tool_use_id` には、`tool_use` の `id` を一致させます。

```
{
  "type": "tool_result",
  "tool_use_id": "toolu_01XXXXXXXXXXXXX",
  "content": "[{\"number\":1,...},{\"number\":2,...}]"
}
```

## Claudeの最終回答

ダミーデータを受け取ったClaudeは、自然文で最終回答を返しました。

```
「st-hisatoshi-2973/startup-security-kit」リポジトリのIssue一覧を確認しました。

## Issue一覧

現在、以下の2件のIssueがあります（両方ともOpen状態）：

| Issue# | タイトル | 状態 |
|--------|---------|------|
| 1 | Add AI Gateway policy document | Open |
| 2 | Improve secret detection examples | Open |
```

## 今回の検証で分かったこと

動作を確認して、いくつか重要な点が明確になりました。

### ツール定義はリクエストのたびに送る

ツールは **APIリクエストのたびに `tools` フィールドに含めて渡します。**

Claudeはそのリクエスト内の定義だけを参照してツールを判断します。

### Claudeはツールを実行しない

Claudeが行うのは `tool_use` を返すことだけです。

**実際にツールを実行するのはアプリケーション側**です。

```
Claude → tool_use（呼んでほしいという意思表示）
アプリ → ツールを実行
アプリ → tool_result（実行結果を返す）
Claude → 結果をもとに最終回答
```

### アプリ側がツールの実行を制御できる

Claudeが `tool_use` を返してきたとき、アプリ側には次の選択肢があります。

* **実行する**（ツールを呼んで結果を返す）
* **拒否する**（実行せずにエラーを返す）
* **実行前に検証する**（ポリシーで評価してから判断する）

ここが今回の核心です。

**ツールの実行可否をアプリ側で制御できる**ということは、

Policy Engineのような仕組みを挟む余地があるということです。

## Local AI Gatewayへの応用

今回の確認で、次の実装のイメージが固まりました。

Claudeが `tool_use` を返したとき、

**そのまま実行するのではなく、ポリシーで評価してから実行するかどうかを決める**

という流れです。

**リスクの高い操作をAIが自律的に実行しようとしたとき、ポリシーで止められるようにしたい**

と考えています。

今回の検証によって、その実装に必要な「ツールの実行はアプリ側の責任」という前提が確認できました。

## まとめ

* Anthropic Tool Use の動作確認として、ダミーツールを使ったサンプルを実装した
* Claudeはツールを実行するのではなく、`tool_use` という「呼んでほしい」という意思表示を返す
* 実際のツール実行はアプリ側の責務であり、実行前にポリシーで評価する余地がある

次は、この仕組みを活かして

**AIが外部ツールに対して実行できる操作をポリシーで制御する「Execution Control」**

を実装していく予定です。
