---
id: "2026-05-20-claude-codeのskillsを育てる資産に変える設計指針と実装パターン-01"
title: "Claude Codeのskillsを「育てる資産」に変える設計指針と実装パターン"
url: "https://qiita.com/siromiya/items/5b1cfe443df9500c9e20"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "qiita"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeをチームや個人プロジェクトで使い続けていると、「同じ説明を毎回している」「CLAUDE.mdがどんどん肥大化してきた」「指示の質に人によってばらつきがある」といった悩みが出てきませんか。

そんな課題を解消する手段として注目されているのが、Claude Codeの **skills** という仕組みです。本記事では「アイデア20選を眺めて満足」で終わらせず、自分の作業文脈に合わせて skills を **継続的に育てる** ための設計指針と、実装で詰まりやすいポイントを整理します。アイデアの俯瞰には出典の[Claude Codeのskillsアイデア大全20選](https://qiita.com/kamome_susume/items/d8919d94f55d86e9881c)が便利なので、合わせて読むと運用論まで含めて理解が深まるはずです。

## この記事で分かること

- skillsとCLAUDE.mdをどう使い分けると無駄なく回るのか、その判断基準
- 育てやすいskillに必要な最小テンプレートとメタデータ設計
- チームで共有する際の命名規則と衝突回避のコツ
- 実運用でつまずきやすい3つの落とし穴と、その回避ポリシー
- 新規skillをレビューするときに使えるチェックリスト

## なぜCLAUDE.mdだけでは足りないのか

CLAUDE.mdは強力な道具ですが、すべての指示をここへ集約すると、ファイルが肥大化して「どの状況で効くルールなのか」が読み取りにくくなります。Claude Codeは起動のたびにこのファイルを読み込むため、適用範囲の狭いノウハウまで詰め込むのは経済的とは言えません。

一方で skills は description によるトリガー条件を持ち、必要な場面でだけ呼び出される構造です。つまり「常に効くルール」はCLAUDE.mdへ、「ある状況だけで効くワークフロー」は skills へ、と役割を分業させると、運用全体の見通しが一気に良くなります。

## 育てやすいskillの構造テンプレート

最初に作るときに迷わないよう、私は以下のような最小テンプレートから書き始めることをおすすめしています。このskillでは「いつ発動するか」をdescriptionに英語で具体的に記述している点がポイントです。

```markdown
---
name: api-spec-review
description: Use when reviewing OpenAPI specs or REST endpoint diffs — checks naming, status codes, and breaking-change risk for backend APIs.
---

# Role
You are reviewing an API spec on behalf of the platform team.

# Steps
1. List endpoints touched by the diff.
2. Verify each endpoint matches existing path / method conventions.
3. Flag breaking changes (param removal, type narrowing, status code shift).

# Output format
- Markdown table: endpoint | change | breaking? | suggestion
```

注目したいのは description の書き方です。Claude Codeはこの説明文を読んで適合度を判断するため、曖昧な記述だと意図しない場面で発火したり、必要な場面で呼ばれなかったりします。逆にここを丁寧に書けば、運用の体感品質はぐっと安定します。

## descriptionの書き方が運用の8割を決める

descriptionは「skillがどう動くか」ではなく「**いつ呼ぶか**」を書く欄だと割り切ると、命中率が劇的に上がります。

- NG例: 「APIをレビューします」 → 抽象的で発火条件が不明
- OK例: 「Use when reviewing OpenAPI specs, REST endpoint diffs, or breaking-change risk for backend APIs」

コツは "Use when 〜" の形で **入力条件・シチュエーション** を列挙することです。動詞中心ではなく場面中心に書くと、似た役割のskillが複数あっても判定が安定します。

## 命名規則とディレクトリ設計

チームで共有する場合は、skill名に階層的なプレフィックスを与えると衝突や検索の悩みが減ります。下表は私が普段使っている分類例です。

| プレフィックス | 用途の例 |
|---|---|
| `review-` | コードレビューや仕様レビュー |
| `gen-` | 雛形生成、コンポーネント生成 |
| `audit-` | セキュリティ・依存関係などの監査 |
| `migrate-` | マイグレーションやリプレース補助 |
| `debug-` | 障害調査、ログ解析 |

実際の名前は `review-api-spec`, `gen-react-component`, `audit-sql-injection` のようになります。接頭辞だけでもチーム内で早めに合意しておくと、後から増えても破綻しません。

## 実運用でハマった落とし穴3つ

### 1. descriptionに動作内容を詰め込みすぎる

「何を出力するか」をdescriptionへ書き込むと、似た役割のskill同士で評価が拮抗し、別物が呼ばれてしまう事故が起きます。descriptionは「いつ呼ぶか」、本文は「呼ばれたら何をするか」と役割を分けましょう。

### 2. skillの中に巨大なコード断片を埋め込む

skill本文が長くなるほど呼び出しごとに消費するトークンも増えます。テンプレが大きい場合は、リポジトリ内のパスを示して必要に応じて Read させる構造に切り替えると、軽量で再利用しやすくなります。

### 3. 評価フィードバックを回さない

作って終わりにするとskillsは静かに陳腐化します。「期待と違う発火をした」「呼んでほしいのに無視された」というケースを週次で1〜2行ずつメモし、descriptionを書き直すだけでも、命中率の体感は大きく変わります。

## チームで共有するときのチェックリスト

新規skillをマージする前のレビュー観点として、私は次の5点を確認しています。これだけ揃っていれば、後から読み返しても役割が一目で分かるskillになります。

- descriptionが "Use when 〜" 形式で具体的に書かれている
- CLAUDE.mdに書くべき「常時ルール」と役割が重複していない
- 既存skillと description の表現が紛らわしくない
- 期待する出力フォーマット(箇条書き・表など)が明示されている
- 例(few-shot)が1〜2件、本文中に含まれている

## まとめ

- skillsはCLAUDE.mdの「常時ルール」と棲み分け、**状況依存のノウハウ** を切り出す場所として使うのが基本方針
- descriptionは「Use when 〜」形式で発火条件を具体化すると、命中率が安定する
- 命名規則と接頭辞をチームで先に合意しておくと、衝突や検索の悩みを未然に防げる
- 作りっぱなしにせず、発火の成否を観測してdescriptionを継続改善する文化を育てる

次のステップとしては、まず自分が今週「同じ説明を2回以上した作業」を1つだけskill化してみてください。20選を眺めるよりも、自分の文脈にフィットした1つを丁寧に育てた方が、効果を実感しやすいはずです。アイデアを広げたいときは出典の[Claude Codeのskillsアイデア大全20選](https://qiita.com/kamome_susume/items/d8919d94f55d86e9881c)を起点に、自分の業務に置き換えながら読むのがおすすめです。
