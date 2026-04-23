---
id: "2026-03-25-github-projectsを使ってる人全員に使ってほしいスキル-ghpm-の紹介-01"
title: "GitHub Projectsを使ってる人全員に使ってほしいスキル - ghpm - の紹介"
url: "https://zenn.dev/jackchuka/articles/ccdb11325f0ce6"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## ghpm — GitHub Projects をそのまま使える skill セット

**コードの変更理由がチームに伝わらない** — これはずっとある問題だと思う。diff だけでは意図が読み取れないので、レビュアーが推測で質問し、作業者が後から説明する。このやり取りが繰り返されている光景を何度も見てきた。

コーディングエージェントの普及でこの問題は加速した。作業者は coding agent とローカルで黙々と作業してお気持ち程度の説明文と一緒に PR を出してくる。判断の経緯が残らないまま、コードの生成速度だけが上がってきているというのを感じている人も多いんじゃないだろうか。

「設計判断を残そう」という話になると、仕様駆動開発の話題や ADR をコミットする、専用の記録ツール・オーケストレーションツールを導入する — などの解決策が出てくるけど、どれもすぐに導入するにはハードルが高い。特にツールを増やすのは、既存のワークフローに新しいツールを組み込むコストが大きい。結局「わかってはいるけど、まあいいか」となってしまう。

そこで原点に立ち返ってみた、**「今のワークフローを変えずに、設計判断をチームに見える形で残すにはどうすればいいか？」** という問いから ghpm が誕生した。

<https://github.com/jackchuka/ghpm>

## ghpm とは

ghpm は **GitHub Projects をそのまま活かす skill セット**。  
日頃から GitHub Projects をプロジェクト管理の中心に据えているチームが、使いやすいように設計されている。

今使っている Views、Fields、Status を解釈して、issue の着手から PR 作成までをガイドする。実装の設計判断は issue comment に直接残る。プロジェクトの構造を自動検出して設定もいらない。

```
npx skills add jackchuka/ghpm
/ghpm-init https://github.com/orgs/<org>/projects/<number>
```

`gh` CLI が認証済みであれば、これだけで始められる。プロジェクトの Fields、Views、リポジトリ一覧を自動検出して `.ghpm/config.json` に書き出される。

## ghpm-work: issue から PR まで

ghpm の中核をなすのが `ghpm-work` skill だ。issue に対する作業セッションをガイドしてくれる。

これで issue #42 に対する作業セッションが始まる。セッションは以下のフェーズで構成されている:

```
 1. Setup       → assign、ブランチ作成、Status を InProgress に
 2. Clarify     → issue の内容を評価、曖昧なら補足
 3. Plan        → コードベースを調査、アプローチを issue comment に投稿
 4. Impl Plan   → 具体的な実装ステップを issue comment に投稿
 5. Implement   → コードを書く、コミット、検証
 6. Draft PR    → issue をリンクした draft PR を作成
```

各フェーズで確認を取ってから進む。全部自動にしたければ `config.json` の `prompts` で `"auto"` にできるし、特定のアクションだけ確認を残すこともできる:

```
{
  "prompts": {
    "ghpm-work": {
      "default": "auto",
      "record_decision": "prompt",
      "draft_pr": "prompt"
    }
  }
}
```

`"prompt"` は確認する、`"auto"` は自動で進む、`"skip"` はスキップ。アクションは `status_sync`, `clarify_issue`, `post_plan`, `post_impl_plan`, `record_decision`, `draft_pr` の 6 つ。最初は全部確認ありで運用して、慣れたら徐々に `"auto"` にしていくのが現実的だと思う。

ghpm-work の一番の特徴は、**設計判断が issue comment として自動的に残る**こと。

Plan フェーズで「なぜこのアプローチにしたか」、実装中に「AとBで迷ってAを選んだ理由」— こういった判断が出てくると、issue comment に記録するか聞いてくる。skill の prompt が「代替案を比較した」「トレードオフを評価した」といった判断パターンを認識し、記録を促す仕組みになっている。自分から明示的に記録したい場合は `decide: GraphQL batch query を使う` のようにプレフィックスをつければよい。

```
Decision detected. Record to #42?
  > "GraphQL batch query を使う。REST だと N+1 になるため"
(y/n)
```

これが ADR のような別ファイルではなく、**その issue のタイムラインに直接残る**。後からチームメンバーが issue を見れば、なぜこの実装になったのか追える。

### セッションは中断・再開できる

Claude Code を閉じても、次に同じブランチで再開すれば前回の続きから:

```
GHPM session #42 "Add batch query support" [implement]. Use /ghpm-work 42 to resume.
```

セッション情報は `.ghpm/sessions/42.json` に保存されていて、フェーズごとに更新される。`ghpm-init` で Claude Code の hooks を自動インストールすると、現在のブランチからセッションを自動検出して再開を促してくれる。24時間以上放置すると stale 警告が出るので、途中で放置してしまった作業も忘れずに拾えるなどの工夫も入れている。

### 次に何をやるか迷ったら

```
/ghpm-suggest 2時間くらいで終わるやつ
```

今いるリポジトリとの関連度、最近のコミットからの momentum、issue の Priority や Status、そして「2時間」のような時間制約 — これらを総合して「次はこれがいいんじゃない？」と提案してくれる、なんて機能もある。

## 他の skill

ghpm は名前の通り、GitHub Projects Management のための skill セットなので、ghpm-work 以外にもプロジェクト管理に役立つスキルがいくつかある。  
現時点で全部で 6 つの skill で構成されている。それぞれの説明は割愛するけど、一覧はこんな感じ:

| Skill | やること |
| --- | --- |
| `ghpm-init` | プロジェクト設定の自動生成 |
| `ghpm-status` | プロジェクト全体の健康状態 |
| `ghpm-view` | Views やフィルタでアイテム一覧 |
| `ghpm-suggest` | 次に何をやるべきか提案 |
| `ghpm-work` | issue → PR のフルライフサイクル |
| `ghpm-issue` | issue 作成 + ボードに追加 |

`ghpm-status` はワークフロー分布、コンポーネントごとの状況、チーム負荷を一覧で出す。`ghpm-view` は GitHub Projects の View をそのまま CLI から引ける。`ghpm-issue` は issue を作ると同時にボードに追加して Status や Fields をセットする。

## 設計思想

冒頭の問題提起からわかるように、ghpm を作るときに意識したのは「今の運用を変えずに使えること」だった。

### 設定は自動検出する

`/ghpm-init` を実行すると、プロジェクトの構造を自動で読み取るようになっている。GitHub API を叩いて、以下の情報を取得する:

* Fields とその型（Status, Priority, Sprint...）
* Views の名前、レイアウト、フィルタ、ソート順
* 紐づいているリポジトリ一覧
* Status フィールドの選択肢（Planned, InProgress, Done...）

手動で YAML を書いたり、フィールド ID を調べて貼り付けたりする必要がない。誰のどんな Projects でも動くようにするために、プロジェクトの形をある種の中間表現に落とし、どんなプロジェクト構成でも動くようにしている。

### Convention は自然言語で書く

`config.json` の `conventions` ブロックはこうなっている:

```
{
  "conventions": {
    "branch": "{type}/{issue-number}/{slug}. Detect type from issue labels...",
    "status_sync": "On start, set to InProgress if currently Planned or ReadyForDev...",
    "decisions": "When a design decision is detected, nudge before recording..."
  }
}
```

柔軟に様々な運用ルールに対応できるよう、ここは自然言語で書くことが想定されている。これを読んで agent がルールとして解釈する。  
例えばブランチ名のルールを変えたければ、conventions の `branch` の value を書き換えるだけでいい。

自然言語ならではの曖昧さが入り込む余地はあるけど、実際に使ってみると解釈精度は十分実用的だったりする。

## まとめ

GitHub Projects でプロジェクト管理をしている人は、ぜひ一度 ghpm を使ってみてほしい。  
設計判断は issue comment に直接残す。運用ルールはそのまま、既存のワークフローを変えずに skill 一つで始められる！

```
npx skills add jackchuka/ghpm
```

面白いと感じたら、いいねや GitHub の Star をもらえると励みになります！

<https://github.com/jackchuka/ghpm>

それでは、また 👋
