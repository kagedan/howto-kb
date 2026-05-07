---
id: "2026-05-06-全部入りかつ軽量skill-creatorを作りました-01"
title: "全部入りかつ軽量skill-creatorを作りました"
url: "https://qiita.com/artie/items/8e21bc0adff39369ffd7"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "GPT", "qiita"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

最近skillが一般普及し始めていることに伴って、以下のような問題が発生しています。

- 似たようなスキルが増える
- どのスキルをいつ使うべきか曖昧になる
- 運用するうちに品質が落ちる
- 評価基準がなく、雰囲気で改善してしまう
- 依存関係が放置される
- 肥大化したスキルの分割タイミングが分からない

少数の skill なら人間の記憶と気合いで回せます。

でも 10 個、20 個、50 個と増えると破綻しやすいです。

そこで必要になってくるのは、「必要な skill をその都度書くこと」ではなく、

**良い skill を継続的に作り、評価し、改善し、整理し続ける仕組み**です。

`skill-builder` は、そのためのメタスキルとして作りました。

https://chatgpt.com/share/69f6cae6-c864-83e8-b612-4337888a2231

https://github.com/artieax/artie-dev-skills/tree/main/skills/skill-builder

https://deepwiki.com/search/skillbuilder_ac901ff4-2bcc-4698-89ae-40e922259b4a?mode=deep


## この記事の要約

- `skill-builder` は、単なる `skill-creator` ではなく、**スキルの設計・生成・評価・改善・分割・依存管理**まで扱うメタスキル
- `atomic-builder` により、スキルをテンプレートではなく **`Atom` の合成**として構築可能
- `eval`、optimizer、しきい値設計によって、**スキル本文だけでなく生成プロンプト自体**も改善対象に
- `stdout-delegate`、`Deno Sandbox`、`sklock`、`AUTO-SPLIT`、`practice-drift-scan` により、**作成後の運用と保守**までをカバー
- 公式の `skill-creator` が「1つのスキルを良くする」方向に強いなら、`skill-builder` は「**スキル群を育てる**」方向に強い
- ただし常に重いわけではなく、`minimal` preset から始めて必要な機能だけを段階的に作成


## まず結論から、何が違うのか

| 観点 | 従来のスキル作成 | `skill-builder` |
|---|---|---|
| 作り方 | 思いついたら個別に書く | パイプラインとして生成する |
| 構造 | テンプレート頼み | `Atom` / `Preset` / `Archetype` の合成 |
| 改善 | 手動で雰囲気改善 | `eval` による継続改善 |
| 判断 | 人間の勘に依存 | スコア・しきい値・停止条件を持つ |
| 依存関係 | だいたい放置 | `sklock` で管理 |
| 肥大化対策 | 手で分割する | `AUTO-SPLIT` で候補を出す |
| 運用 | 作って終わりがち | 月次で自己改善する |
| 初期導入 | 軽いが再利用しにくい | `minimal` から始めて拡張できる |

要するに、`skill-builder` がやっているのは、skill を「1ファイルの成果物」から「継続的に育てる開発対象」へ移すことです。

## `skill-builder` が扱う範囲

`skill-builder` は `SKILL.md` を 1 枚生成して終わる skill ではありません。

扱うのは、skill のライフサイクル全体です。

- 既存 skill との重複確認
- 新規 skill にする範囲の決定
- 必要な `Atom` の選定
- scaffold の生成
- 複数案の比較
- `eval` による品質確認
- しきい値調整
- 依存関係の登録
- 分割候補の検出
- 月次改善ループの運用

phase map も `CREATE → SCAFFOLD → ITERATE → EVALS → AUTO-DEPS → AUTO-SPLIT → SCHEDULE` という流れで整理されています。

つまり、最初のドラフト生成は入口にすぎません。

狙っているのは、**良い skill を継続的に量産できる仕組み**です。

## 何をしないのか

`skill-builder` は強いですが、万能薬を目指しているわけではありません。

- すべての skill 設計を完全自動にしない
- 人間のレビューを不要にしない
- 判断をブラックボックス化しない
- 外部ソース由来の提案を無条件で自動適用しない

あくまで、**skill 開発のボトルネックを機械化するための基盤**です。

## 全部入りだけど、常に重いわけではない

ここは誤解されやすいポイントですが、`skill-builder` は全部入りでも、最初からフル装備を強制するわけではありません。

`minimal` preset は **6 要素**、つまり `frontmatter + trigger + workflow + redflag + output + requirements` だけで始められます。

- workflow 3 step 以下の小さな skill
- supplementary docs が不要な skill
- eval tracking をあと回しにしたい skill

なら、この最小構成で十分です。

必要になった段階で、

- `Atom` を追加する
- `eval` を足す
- `sklock` を入れる
- `AUTO-SPLIT` を使う

というように段階的に拡張できます。

つまり `skill-builder` は、固定的な巨大テンプレートではなく、**必要なぶんだけ展開できる progressive disclosure 型の全部入り**です。

全部入りだからといって、contextを圧迫するわけではありません。

## `atomic-builder`：テンプレートではなく `Atom` の合成で作る

`skill-builder` の中核の 1 つが `atomic-builder` です。

普通にやると skill 作成はテンプレートベースになりがちです。

しかしテンプレート方式は、用途が少しズレるたびにテンプレートが増殖し、管理コストが上がります。

そこで `skill-builder` では、skill を完成済みテンプレートではなく、**必要な部品の組み合わせ**として扱います。

たとえば、

- 軽量な skill なら最小限の `Atom` だけを使う
- script 実行が必要なら `scripts/` 系 `Atom` を足す
- 検証が必要なら `sandbox/` 系 `Atom` を足す
- 長期改善したいなら `eval` 系や `projects/` 系 `Atom` を足す

というように、目的に応じて構造を合成できます。

この発想の良いところは、柔軟なだけではありません。**最初から全部を載せなくていい**ことです。

progressive disclosure(走りながら、必要な情報だけを開示すること)

のアーキテクチャを体現しています。

## `Preset` / `Archetype` / `Exemplar mode`

`Atom` だけだと柔軟すぎるので、再利用レイヤーとして `Preset` と `Archetype` を用意しています。

### `Preset`

よく使う `Atom` の組み合わせをまとめたものです。まず標準的な `Preset` を選び、足りない部分だけを `Atom` で補うことで、毎回ゼロから考えなくて済みます。

### `Archetype`

ドメイン特化の設計パターンです。

- 最小構成で作りたい
- script 付きで作りたい
- 比較評価しやすくしたい
- バージョン管理しながら改善したい
- sandbox 付きで安全に検証したい

といった違いを、毎回手作業で設計しなくてよくなります。

### `Exemplar mode`

高スコアな既存 skill から `Atom pool` を作り、次の生成に再利用する仕組みです。

うまくいった構造を次の初期値として持ち込めるので、単なるテンプレート再利用より使いやすいです。

## `eval` と optimizer：雰囲気で改善しない

skill 作成で難しいのは、「良い skill とは何か」を感覚で決めがちなことです。

だから `skill-builder` では、`eval` を中心に置きます。

見るのはたとえば次のような観点です。

- 期待したタイミングで発火するか
- 出力品質が安定しているか
- 手順が無駄に増えていないか
- 既存 skill より改善しているか
- 回帰していないか

さらに最近は optimizer も実務寄りになっていて、stale artifact の掃除、複数回 scoring の中央値採用、false positive / false negative 要約などにより、**前回の残骸で誤って良く見える問題**を潰しやすくなっています。

加えて、Optuna 的な発想で停止条件や品質しきい値も設計対象にしています。

- 何点以上なら十分良いか
- どれくらい改善しなくなったら止めるか
- どの指標をどれくらい重く見るか

このあたりを人間の気分で決めず、探索可能な対象として扱うわけです。

## その他の実行と運用を支える仕組み

### `stdout-delegate`

script 自身が API や CLI を直接叩く代わりに、stdout に directive を出して host 側に LLM 呼び出しを委譲する方式です。

これにより、script 側で API key や特定 CLI を前提にしなくてよくなり、skill の portability が上がります。

### `Deno Sandbox`

自然言語ベースの skill でも変更による回帰は起きます。そこで sandbox により、入力・期待出力・境界条件を持った検証をマージ前に回せるようにします。

### `sklock`

https://zenn.dev/einperience/articles/340854da492ca1

skill 群の依存関係を整理する軽量な依存管理レイヤーです。

agent 全体の package manager ではなく、**skill グラフを壊れにくく保つための仕組み**として位置づけています。

こちらはoptinalになってますので、使用しない場合は簡易にmermeid記法で依存グラフを管理するという選択もできます。

### `AUTO-SPLIT`

skill が太って複数責務を抱え始めたときに、分割候補を出すための仕組みです。巨大関数や神クラスを放置しないのと同じ発想です。

### `practice-drift-scan`

外部の実践や公式更新を見て、現在の skill inventory と比較しながら改善候補を提案する open-loop の discovery です。自動適用ではなく、**proposal を出すところまで**に留めているのが重要です。

### `定期改善ループ`

skill は作った瞬間がピークではありません。使われるほど `eval` log、失敗例、重複、依存関係のズレ、分割候補が見えてきます。

だから `skill-builder` は、定期で見直して育てる前提で設計しています。


## すぐ試せます

ご使用のAI agent に次のように頼めば、そのまま使い始められます。

```txt
https://github.com/artieax/artie-dev-skills の skill-builder を使って、
以下の skill を作りたいです
```

plugin として使い始めるなら、次のコマンドです。

```bash
/plugin marketplace add artieax/artie-marketplace
/plugin install artie-dev-skills@artie-marketplace
```

まずはskill-creatorと並行して使用みるのもおすすめです。

## まとめ

- `skill-builder` は、skill の生成から継続改善までを扱うメタスキル
- `atomic-builder` により、skill をテンプレートではなく `Atom` の合成で構築できる
- `Preset` / `Archetype` / `Exemplar mode` により、構造そのものを再利用できる
- `eval`、optimizer、しきい値設計により、本文だけでなく生成プロンプトも改善対象にできる
- `stdout-delegate`、`sandbox`、`sklock`、`AUTO-SPLIT`、`practice-drift-scan` により、運用フェーズまで含めて設計されている
- `minimal` から始めて必要な機能だけを足せるので、全部入りでも常に重いわけではない
- 公式 `skill-creator` が「1つの skill を良くする」方向に強いなら、`skill-builder` は「skill 群を育てる」方向に強い

## さいごに

スキルは、これからのエージェント開発における重要な再利用単位になるはずです。

そして `skill-builder` は、その単位を 1 個ずつ良くするだけでなく、**群として持続的に育てるための基盤**として作っています。

新しい skill を作り、次に `eval` 前提で改善し、
その後で依存関係・分割・月次改善まで含めて「自動で育つ設計」にしていく。

さらに気に入った機能があればatomに足していったり、presetも増やすことができるので、拡張しやすいです。

ぜひコンセプトなどが気にいった人は使用してみてください。

https://chatgpt.com/share/69f6cae6-c864-83e8-b612-4337888a2231

https://github.com/artieax/artie-dev-skills/tree/main/skills/skill-builder

https://deepwiki.com/search/skillbuilder_ac901ff4-2bcc-4698-89ae-40e922259b4a?mode=deep
