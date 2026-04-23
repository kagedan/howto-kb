---
id: "2026-04-11-claude-に-issue-のラベルを自動でつけさせたら-gitlab-のタスク管理が加速した話-01"
title: "Claude に issue のラベルを自動でつけさせたら GitLab のタスク管理が加速した話"
url: "https://qiita.com/autoaim-jp/items/0556b3514c5001b3a52d"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

自宅の Raspberry Pi で GitLab をセルフホストして、日常のタスク管理をすべて Issue で行っています。「〇〇を実装する」「マヨネーズを買う」「明日の出社準備」——こういった雑多な issue を 2,000 件以上ため込んできました。

その中で長年の課題だったのが **ラベル管理**です。「issue を作るときにラベルを設定するマイルールを決めよう」と何度か試みたのですが、面倒で続きませんでした。ラベルのない issue が溜まっていくと、「前にも同じこと書いた気がするな」と思っても探せない。同じラベルで絞り込んで俯瞰する、ということもできない。

この記事では、この問題を **Claude（Anthropic API）+ GitLab の Webhook + CI ジョブ**で解決した話を紹介します。

### テイクアウトメニュー

* GitLab のタスク管理でラベルが使えるようになる仕組み
* Webhook とジョブの使い分けの考え方
* GitLab に Claude を組み込む最小構成の試し方

---

## 以前の状況：ラベルをつけるのが面倒で続かなかった

自宅 GitLab で Issue を管理していると、issue の幅がとても広くなります。

* `〇〇機能を実装する`（開発タスク）
* `△△のドキュメントを更新する`（保守）
* `GitLab セルフホストのメリットを記事にする`（情報発信）
* `マヨネーズを買う`（雑務）

これらに手作業でラベルを付けるルールを作ろうとしましたが、**issue を起票するたびにラベルを選ぶ手間**がじわじわとストレスになり、気づけばラベルなし issue が増えていきました。

その結果：

* ラベルで絞り込めないので、同系統の issue がまとまって見えない
* 「前にも似たこと書いたかも？」というときに探しにくい
* issue をまとめたいとき（類似 issue の番号とタイトルをピックアップする作業）が非常に遅い

---

## 今の状況：issue を作るだけでラベルがつく

現在は、issue を新規作成すると **自動で `pj3::` から始まるラベルが付与されます**。

操作は「issue を書いて保存する」だけ。ラベルを選ぶ必要はありません。

> **`pj3::` ラベルとは？**  
> もともと `pj::` から始まるラベルを手動でつけていましたが、面倒で続きませんでした。次に、AI ラベル設定ジョブ ver1 として `pj2::` から始まるラベルを自動付与する仕組みを作りましたが、分類の粒度が合わなかったため見直しました。今回紹介する ver2 では分類を再設計し、`pj3::` から始まるラベルを使っています。

これによって：

* **ラベルをクリックするだけ**で同じカテゴリの issue を一覧できる
* 「前にも書いた気がする」というときに **即座に探せる**
* 類似 issue をまとめたいときの下調べが格段に速くなった

---

## 仕組みの全体像

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2710990%2Ff7a51510-8b4d-4d7e-9fce-2ecb3113dbec.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4db719171c9832c8becdcbf41b9b4050)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2710990%2Ff7a51510-8b4d-4d7e-9fce-2ecb3113dbec.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4db719171c9832c8becdcbf41b9b4050)

### 各ステップの役割

| ステップ | 役割 |
| --- | --- |
| GitLab Webhook | issue 作成イベントを Webhook サーバへ通知 |
| Webhook サーバ | イベントを受け取り、CI パイプラインをトリガー |
| ai\_label ジョブ | Claude にラベルを判定させ、GitLab API で付与 |

---

## 実装の詳細

### 1. Webhook サーバ（issue 作成を検知）

Node.js + Express の Webhook サーバを自宅 k3s 上で動かしています。GitLab の issue 作成イベントを受け取ると、CI パイプラインをトリガーします。

```
// issue 作成イベント: ai_label ジョブをトリガー
if (eventType === "Issue Hook" && action === "open") {
  await triggerPipeline({ projectId, labelIssueId: issueIid });
}
```

### 2. ai\_label ジョブ（Claude でラベルを判定）

GitLab CI の `ai_label` ジョブが動き、以下を実行します：

1. **issue タイトルを取得**（GitLab API）
2. **関連 issue を検索**（タイトルキーワードで検索し、文脈として渡す）
3. **Anthropic API（claude-haiku）を呼び出し**、最適な `pj3::` ラベルを判定
4. **ラベルを付与**（GitLab API で `PUT /issues/:iid`）
5. **判定理由をコメント投稿**（GitLab API で `POST /issues/:iid/notes`）

```
# issueタイトルを取得
issue_json=$(curl -sS -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$API_BASE/projects/$CI_PROJECT_ID/issues/$LABEL_ISSUE_ID")
issue_title=$(echo "$issue_json" | jq -r '.title // ""')

# Anthropic API でラベル判定
response=$(curl -sS -X POST "https://api.anthropic.com/v1/messages" \
  -H "x-api-key: ${ANTHROPIC_API_KEY}" \
  -d "$(jq -n --arg prompt "$prompt" \
    '{model: "claude-haiku-4-5-20251001", max_tokens: 512,
      messages: [{role: "user", content: $prompt}]}')")

# ラベルを付与
curl -sS -X PUT \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --data "$(jq -n --arg lbl "$best_label" '{add_labels: $lbl}')" \
  "$API_BASE/projects/$CI_PROJECT_ID/issues/$LABEL_ISSUE_ID"
```

### 3. ラベル定義（Claude へのプロンプトに含む）

Claude に渡すプロンプトには、ラベルの定義と判断基準を明記しています。

```
- pj3::publish（記事・デモ動画・情報発信）
  外向けに出すコンテンツの作成。主題が「外に見せる・伝える」ならこれ。

- pj3::develop（機能開発）
  既存の仕組みに対する機能追加・改善・修正のタスク。

- pj3::maintenance（環境保守）
  既存の開発環境・既存の仕組みを安定して使える状態に整えるタスク。

- pj3::task（雑務・一般タスク）
  連絡、申請、買い物、予約、支払いなどの用事。主題が「やるべき用事そのもの」ならこれ。

（…全 10 種類）
```

### 4. CI ジョブとして実装した理由

同じ処理を Webhook サーバ内で完結させることもできます。でも、あえて **GitLab CI ジョブとして切り出した**理由があります。

> **「動いていないかもしれない」と思ったとき、すぐに確認できる場所に置きたかった。**

Webhook サーバ内で処理していると、「止まっているかどうか」を確認するにはサーバに SSH して確認する必要があります。一方、CI ジョブなら **GitLab の UI でジョブの成否・ログを即座に確認できます**。運用上の視認性を重視したため、CI ジョブとして分離しました。

---

## 実際の動作例

issue を作成すると、数秒後に以下のようなコメントが自動で投稿されます：

```
[AI生成(webhook:label)]

**最適ラベル**: pj3::publish（記事・デモ動画・情報発信）
- 理由: 外向けに情報を発信するコンテンツ作成のタスクのため。

**他の候補**:
- pj3::develop（機能開発）：実装が伴う場合はこちらの可能性もある

**関連issue**:
- #2171 3つのスラッシュコマンドで開発するワークフローを記事にする
```

同時に issue に `pj3::publish（記事・デモ動画・情報発信）` ラベルが付与されます。

---

## やってみた感想

### よかったこと

**ラベルを意識しなくていい**のが想像以上に快適でした。issue を書くことだけに集中できます。

ラベル精度についても、日常的な使用では概ね正確です。「マヨネーズを買う」は `pj3::task（雑務）`、「CI の不具合を直す」は `pj3::maintenance（環境保守）`、「GitLab のセルフホストを記事にする」は `pj3::publish（記事・デモ動画・情報発信）` と判定されます。

### 工夫したポイント

まれに判定が微妙なケースがあります。「〇〇を調査してから実装する」のように複数の性質を持つ issue は、人間が見てもどちらか迷うことがあり、Claude も同様です。そういった場合はコメントを見て手動で上書きしています。

Claude がコメントに「他の候補」と「判定理由」を残してくれるおかげで、上書きが必要かどうかをすぐ判断できます。ラベルの精度を高めるより、**補正コストを下げる設計**にしたのがポイントです。

---

## まとめ

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2710990%2Fabfff1e5-a4ed-439d-a0e8-7e2cf9332e59.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f3f34c0e122755dbd58db1db8cbe4500)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2710990%2Fabfff1e5-a4ed-439d-a0e8-7e2cf9332e59.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f3f34c0e122755dbd58db1db8cbe4500)

**「ラベルをつけるのが面倒」という問題を、Claude に任せることで解決しました。** 重要なのは、Webhook → CI ジョブという構成にすることで、運用上の視認性（動いているかどうかがすぐわかる）も確保できている点です。

GitLab に Claude を組み込む最小構成として、参考になれば幸いです。
