---
id: "2026-07-10-jetbrains-air-のエージェント複数作業とエージェントレビュー機能-01"
title: "JetBrains Air のエージェント複数作業と、エージェントレビュー機能"
url: "https://zenn.dev/nattosystem_jp/articles/c9a7d241a9fa31"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "Gemini", "GPT", "zenn"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

## はじめに

今回はJetBrains Air の Windows preview が出たので、実際に使ってみました。

<https://blog.jetbrains.com/air/2026/06/jetbrains-air-lands-on-windows/>

JetBrains Air は、AIエージェントにコーディングタスクを委任し、人間はワークフローの主導権を握ったまま結果を確認する、というコンセプトのAgentic Development Environmentです。  
Claude Agent・Codex・Gemini・Junieといった複数のエージェントをタスク単位で使い分ける、独立したアプリとして設計されています。  
2025年12月に発表され、2026年3月にmacOSでパブリックプレビューが始まりましたが、しばらくWindows非対応の状態が続いていました。  
それが2026年6月30日についにWindows版（x64/ARM64）がリリースされました。

現時点では Air 本体は無料で利用できます。  
エージェントを動かすには JetBrains AI のサブスクリプションを使えるほか、BYOK（Bring Your Own Key）で自分のAPIキーを設定して使うこともできます。  
すでに JetBrains AI を契約している人や、利用中のLLMプロバイダーのAPIキーを持っている人なら、そのまま試しやすいかなと思います。

普段AIエージェントに実装を任せるときは、ひとつのタスクが終わるまで待ってから、次のタスクを依頼したり、別のエージェントアプリで平行して作業することもありました。作業ディレクトリがひとつしかないので、片方が動いている間にもう片方をいじると、変更が混ざってどっちの差分かわからなくなる。

## Agentic Development Environment 「Air」 とは

Airは「IDEにAIチャットが付いたもの」ではありません。**AIエージェントに作業を任せて、その結果を確認するために画面全体が設計された、独立したアプリ**です。  
普段IntelliJ IDEAでJunieプラグインを使うのとは主従関係が逆で、「AIが実装し、人間はレビューする」ことが前提になっています。  
Claude Agent・Codex・Gemini・Junieを同じ画面で使い分けられます。

Airでの1タスクの流れ、

1. プロジェクトを開く（＝ワークスペース）
2. `Chat` ツールでやりたいことを書く
3. どのエージェント・**どこで**（実行環境）やるかを選ぶ
4. 送信して、`Task Changes` で差分を確認する
5. 気に入ればCommit/Pushなどで取り込む

* **エージェント**: Claude Agent / Codex / Gemini / Junie。得意分野やモデルが違うので使い分けることができます。
* **実行環境**（公式ドキュメント [Task run environments](https://www.jetbrains.com/help/air/execution-environments.html) によれば4種類）:
  + `Local Workspace` — 現在のワークスペースに直接書き込む。起動は最速だが**隔離はない**
  + `Git Worktree` — リポジトリの別ブランチ・別フォルダで作業させる。メインブランチとは隔離されるが、ホスト環境自体は共有する（依存関係の再インストールが必要になる場合がある）
  + `Docker` — 隔離コンテナの中で実行する。
  + `Cloud` — リモートのクラウド環境で実行する。完了後は別タスクブランチにコミット・pushされる

タスクが完了すると `Task Changes` でdiffが見られるほか、`Review with Agent` を使うと、実装とは別のセッションでエージェントにレビューさせることができます。今回はGit Worktreeでの並列実行と、Review with Agentを使ってみました。

## 実際に試したこと

### 1. ふたつの独立したタスクを、同時に実行

spring-petclinicのソースを見て、ふたつの“未実装のバリデーション”を実装しました。

* `PetController` / `Pet.java`: ペットの生年月日(`birthDate`)に、未来の日付を入力しても保存できてしまう
* `VisitController` / `Visit.java`: 同じペットに対して同じ日付の来院予約を、なんどでも重複登録できてしまう

このふたつはファイルもドメインも独立しているので、並列実行の検証にちょうどいい題材でした。

Chatツールで、タスクAを依頼しました。

```
PetController / Pet エンティティで、ペットの生年月日(birthDate)に未来の日付を入力しても保存できてしまいます。
今日以前の日付のみ許可するバリデーションを追加してください。既存のテストを確認し、必要なら新しいテストも追加してください。
```

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--mu1wB2z3--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/211f9a0d-46e3-4723-8c9b-f7209f63fb0f.png?_a=BACMTiAE)

実行環境は `Git Worktree` を選択。送信後、完了を待たずにタスクBも同じワークスペースから依頼。

```
VisitController / Visit エンティティで、同じペットに対して同じ日付の来院予約がすでに存在する場合、
新規の来院予約登録を拒否する重複チェックのバリデーションを追加してください。
既存のテストを確認し、必要なら新しいテストも追加してください。
```

こちらも実行環境は `Git Worktree`。

### 2. 並列実行を確認

同じワークスペースの中で、独立したタスクが同時に動いていました。  
![image.png](https://res.cloudinary.com/zenn/image/fetch/s--g8xetiSE--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/101d5ab7-3079-4864-b7cf-bc7b8af894c0.png?_a=BACMTiAE)

### 3. Review with Agent を押したら、レビューが始まった

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--hgU6o-Oa--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/f2895e42-7fc8-442a-b717-2b4b0ebfaa54.png?_a=BACMTiAE)

タスク完了後の画面には `Review with Agent` と `Changes` というボタンが並んでいました。  
`Review with Agent` を押してみたところ、そのままレビューが自動で始まり、サイドバーのタスクの下に「Agent Review」という子タスクが生成されました。

レビューが残したコメントには "codex" という表示があり、実装に使ったのと同じCodex(GPT 5.5)がレビューも担当していたようです。  
![image.png](https://res.cloudinary.com/zenn/image/fetch/s--bYgeMOat--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/90bbf37c-c965-4e6e-a46a-f910e3120080.png?_a=BACMTiAE)

そして、そのレビューコメントがタスクBの重複チェック実装について、こう指摘しました。

> This duplicate check only inspects the in-memory visits loaded before `owners.save(owner)`, so two concurrent POSTs for the same pet/date can both pass validation and persist duplicates. If the requirement is to prevent duplicates reliably, enforce uniqueness at the persistence layer as well (for example a unique constraint on `visits(pet_id, visit_date)` or a transactional repository/service check that handles a unique-constraint violation).

つまり「メモリ上のチェックだけでは、同時に2件POSTが来た場合に両方バリデーションを通過してしまい、結局重複が保存されうる」という、実装したときには気づいていなかったことでした。

### 4. コメントをそのままSendして、修正させる

このコメントには `Send` `Delete` `Edit` の操作が付いていたので、そのまま `Send` してメインタスクに送り返しました。

結果は、

* `Visit.java`: `uk_visits_pet_date` という `@UniqueConstraint` を追加
* `schema.sql`: MySQL・PostgreSQL向けのスキーマに `UNIQUE(pet_id, visit_date)` を追加
* `VisitController.java`: `DataIntegrityViolationException` を捕捉し、`duplicate.visitDate` のフォームエラーに変換
* `VisitControllerTests.java`: 既存visitによる事前拒否と、DB制約違反が起きたときのエラー変換の両方をテスト追加

エージェントは実装後、Javaのformatterとcheckstyleを自走で実行し、フォーマット崩れを検知して自動修正した上で、`.\mvnw.cmd -Dtest=VisitControllerTests test` を実行して6件のテストがすべて通ることまで確認していました。

修正が終わると、再び `Review with Agent` と `Changes` ボタンが表示され、いつでも次のレビューサイクルに入れる状態に戻っていました。

## 結果

* ふたつの独立した依頼を、待ち時間なく並行して進められた
* メモリ上のロジックだけを見て「重複チェックできた」と思っていたコードに、実際の本番運用で起きうる競合バグ（同時アクセスでの二重登録）が潜んでいることを、レビューAgentが指摘してくれた
* 指摘を送り返すだけで、DB制約・例外処理・テストまで含めた一貫性のある修正が返ってきた

「並列で作業できる」だけでなく、レビューのところまで確認できました。

## 不便だった点

* タスク完了直後は「レビュー担当エージェントを選ぶ画面」が出ず、そのまま自動でレビューが始まりました。後で公式ドキュメント（[Review with agent](https://www.jetbrains.com/help/air/agentic-review.html)）を確認したところ、レビューに使うモデルは `Settings | Global | AI | Review | Agent review model` で事前に設定しておく仕組みで、タスクのその場で選ぶUIではないとわかりました。「別のエージェントにレビューさせて客観的な意見をもらう」を試したい場合、事前にSettingsを見ておく必要があります。

## まとめ

JetBrains Air の Git Worktree 実行環境を使うと、独立したAIタスクを同時に進めても差分が混ざりません。  
「ひとつ終わるまで待つ」だった作業を、タスクごとにわけて進められます。

もうひとつは、Review with Agent のレビュー能力、今回のケースでは、メモリ上の重複チェックだけでは防げない並行処理のバグを指摘し、DB制約・例外処理・テストまで含めた修正につながりました。  
`Review with Agent` で別のエージェントに依頼したい場合は`Settings | Global | AI | Review | Agent review model` でレビュー用モデルをご確認ください。

## ナットウシステムからのお知らせ

弊社は JetBrains 製品に関するご質問、ご相談等を受け付けております。弊社の[X](https://x.com/nattosystem?s=20)または[メール](mailto:sales@nattosystem.com)でご連絡ください。

## 参考資料

<https://blog.jetbrains.com/air/2026/06/jetbrains-air-lands-on-windows/>

<https://www.jetbrains.com/help/air/getting-started.html>
