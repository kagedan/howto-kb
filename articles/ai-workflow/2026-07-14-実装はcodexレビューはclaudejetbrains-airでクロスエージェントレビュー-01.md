---
id: "2026-07-14-実装はcodexレビューはclaudejetbrains-airでクロスエージェントレビュー-01"
title: "実装はCodex、レビューはClaude、JetBrains Airでクロスエージェントレビュー"
url: "https://zenn.dev/nattosystem_jp/articles/584eb689033cfa"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "Gemini", "zenn"]
date_published: "2026-07-14"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回は JetBrains Air の[Git Worktreeで並列タスクを試した記事](https://qiita.com/nattogohan123/items/b03635608fbcea85172e)を書きましたが、その中で `Review with Agent`（エージェントによる自動レビュー）を使ったところ、実装したのと同じエージェントがレビューも担当する設定になっていることがわかりました。  
今回は、設定から**別のエージェントをレビュー担当に指定**してみました。

実装したエージェント自身がレビューもすると、自分が採用した前提や設計判断を疑わずにそのまま良しとしてしまう。人間のセルフレビューでも起きることですが、AIでも同じことが起きるはずです。

JetBrains Air は、AIエージェントにコーディングタスクを委任し、人間はワークフローの主導権を握ったまま結果を確認する、というコンセプトのAgentic Development Environmentです。  
Claude Agent・Codex・Gemini・Junieといった複数のエージェントをタスク単位で使い分ける、独立したアプリとして設計されています。  
2025年12月に発表され、2026年3月にmacOSでパブリックプレビューが始まり、2026年6月30日についにWindows版（x64/ARM64）がリリースされました。

現時点では Air 本体は無料で利用できます。  
エージェントを動かすには JetBrains AI のサブスクリプションを使えるほか、BYOK（Bring Your Own Key）で自分のAPIキーを設定して使うこともできます。  
すでに JetBrains AI を契約している人や、利用中のLLMプロバイダーのAPIキーを持っている人なら、そのまま試しやすいかと思います。

## 試した手順

### 1. Codexで郵便番号バリデーションを実装

`spring-petclinic` の `Owner` エンティティには `address`・`city`・`telephone` はあるものの、郵便番号のフィールドがありません。これを実装対象にしました。

実行環境は `Git Worktree` を選択し、Codexにこう依頼しました。

```
Owner エンティティに日本の郵便番号フォーマット（XXX-XXXX）のフィールドpostalCodeを追加し、
OwnerControllerのフォームでバリデーションが効くようにしてください。
既存のテストを確認し、必要なら新しいテストも追加してください。
```

Codexの実装内容は以下の通りでした。

* `Owner.java` に `postalCode` フィールドを追加し、`@NotBlank` と `@Pattern(regexp = "\\d{3}-\\d{4}")` で `XXX-XXXX` 形式を検証
* `createOrUpdateOwnerForm.html` に入力欄を追加
* 所有者詳細画面にも表示を追加
* DB初期化SQL、各localeのメッセージキー、既存テストデータを更新
* テスト実行結果: `Tests run: 26, Failures: 0, Errors: 0`

一見、フィールド追加からテストデータ更新まで一貫していて、抜けがないように見えました。

### 2. Codexでの Review with Agent

`Review with Agent` を押すと、前回の記事と同じく、自動でレビューが始まりました。レビューも実装と同じCodexが担当することになります。

残されたコメントは2件でした。

> `CREATE TABLE IF NOT EXISTS` does not add `postal_code` when an existing MySQL PetClinic database already has the `owners` table. With `spring.sql.init.mode=always`, the updated `data.sql` and JPA mapping will then reference a missing column and startup/save operations can fail. Add an idempotent migration step such as `ALTER TABLE owners ADD COLUMN IF NOT EXISTS postal_code VARCHAR(8)` or otherwise document/drop-and-recreate this schema for existing MySQL databases.

> `CREATE TABLE IF NOT EXISTS` leaves existing PostgreSQL `owners` tables unchanged, so databases created before this change will still lack `postal_code`. Because this profile always runs SQL init and the entity/data script now require that column, startup or owner persistence can fail against an existing database. Add an idempotent `ALTER TABLE owners ADD COLUMN IF NOT EXISTS postal_code TEXT` (or an equivalent migration/reset path) before the data inserts.

要約すると、「`CREATE TABLE IF NOT EXISTS` は既存のMySQL/PostgreSQLの `owners` テーブルには効かないので、すでに稼働中のDBには `postal_code` カラムが追加されない。起動時やowner保存時に失敗しうる」という、DBスキーマの移行手順に関する指摘です。実装時には気づいていなかった、インフラ寄りの指摘でした。  
![image.png](https://res.cloudinary.com/zenn/image/fetch/s--Rx-HS3y8--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/dc9d377e-30f1-4f33-9d00-5785738b9f70.png?_a=BACMTiAE)

### 3. Claude Agentに切り替えてレビュー再実行

`Settings` → `Global` タブ → `AI | Review` → `Agent review model` を **Claude Agent** に変更し、同じタスクに対してもう一度 `Review with Agent` を実行しました。  
![image.png](https://res.cloudinary.com/zenn/image/fetch/s--CCq2jZI6--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/47bd3b5e-8ced-474a-ad53-4c2656129664.png?_a=BACMTiAE)

今度は、Codexとは異なる種類の指摘が返ってきました。

> 正規表現 `\d{3}-\d{4}` は日本の郵便番号形式に固定されている。シードデータの所有者は Madison, WI や London など米国・英国の住所であり、実際の米国 ZIP（5桁、または+4形式で10桁）や他国の郵便番号はすべてこの検証で拒否される。PetClinic が特定地域限定でない前提なら、フォーマットをより汎用的にする（例: 英数字・可変長を許容する、または国別バリデーションを分離する）べき。少なくとも意図的な仕様なのかコメントで明示した方が良い。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--rtcwLtD3--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/4b8e50df-115b-4042-b6a6-9c6f68741e4d.png?_a=BACMTiAE)  
こちらはDBスキーマの話ではなく、そもそもこの要件自体がプロジェクトの実データと矛盾しているという、ドメイン・要件レベルの指摘です。  
`spring-petclinic` のシードデータには Madison, WI（アメリカ）や London（イギリス）の所有者が含まれており、日本の郵便番号形式に固定したバリデーションでは、既存データの多くがそもそも保存できません。

## 結果

同じ実装物に対して、2つのエージェントが指摘した内容の違いがはっきりします。

| レビュー担当 | 指摘の種類 | 指摘内容 |
| --- | --- | --- |
| Codex（自己レビュー） | インフラ・スキーマの正しさ | 既存DBへの非冪等なカラム追加、起動・保存失敗のリスク |
| Claude Agent（別エージェント） | ドメイン・要件の妥当性 | 郵便番号フォーマットが実際のシードデータ（米英住所）と矛盾 |

* 「実装者とは別の視点」を意図的に持ち込むことで、指摘の"種類"そのものが増えることを実感した

## 他エージェントツールとのちがい

単体のコーディングエージェントツール（実装もレビューもひとつのツールで完結するもの）で「別のAIにレビューさせる」をやろうとすると、diffを手動でコピーして別のチャットツールに貼り付ける、といった手間が発生します。  
JetBrains Airでは、設定を変更するだけで、同じUI・同じタスクの文脈のまま、レビュー担当だけを差し替えられます。

## 不便だった点・制限

* デフォルトでは実装エージェントと同じものがレビューも担当する設定になっているため、意識してSettingsを開かないと「別のエージェントに見せた」つもりが実は自己レビューだった、ということが起こり得ます
* レビュー担当の切り替えはグローバル設定（`Settings | Global`）なので、タスクごとに毎回変える運用には向いていません。プロジェクト単位で固定したい場合は別途確認が必要そうです

## まとめ

AIに実装させたコードのレビューを、同じAIに任せにしている人は、一度JetBrains Air で`Agent review model` を別のエージェントに変えてタスクをレビューすることをおすすめします。  
今回のケースでは、インフラ視点の指摘と、ドメイン・要件視点の指摘という、片方だけでは出てこなかった2種類の問題が見つかりました。  
「どのAIにレビューさせるか」まで意識する価値があると感じました。

## ナットウシステムからのお知らせ

弊社は JetBrains 製品に関するご質問、ご相談等を受け付けております。弊社の[X](https://x.com/nattosystem?s=20)または[メール](mailto:sales@nattosystem.com)でご連絡ください。

## 参考資料

<https://blog.jetbrains.com/air/2026/06/jetbrains-air-lands-on-windows/>

<https://www.jetbrains.com/help/air/getting-started.html>
