---
id: "2026-07-08-claude-codeをもっと使いこなす⑦自作skillskillmdの作り方-01"
title: "Claude Codeをもっと使いこなす⑦｜自作Skill（SKILL.md）の作り方"
url: "https://zenn.dev/kaihatsu_biyori/articles/claude-code-custom-skill"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "zenn"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

# Claude Codeをもっと使いこなす⑦｜自作Skill（SKILL.md）の作り方

こんにちは、開発日和です。

[Part6](https://zenn.dev/kaihatsu_biyori/articles/claude-code-skill-basics)でビルトインSkillを紹介しました。今回は「自分で作るSkill（カスタムSkill）」の話です。

毎回同じ長いプロンプトを打っていて、「これ登録できたらいいのに」と思ったことはありませんか。カスタムSkillはまさにそれを解決してくれます。中身はMarkdownファイルを書くだけ……なのですが、**実は私はファイルの置き方で最初につまずきました**。その話も含めて、実際に動いた形式だけを紹介します。

---

## この記事で紹介する内容

| 内容 | ひとことメモ |
| --- | --- |
| カスタムSkillの正しい作り方 | `.claude/skills/<スキル名>/SKILL.md` が正解 |
| 実践例2つ | デプロイ前チェック／Laravel専用レビュー |
| descriptionによる自動起動 | 自然言語の依頼からSkillが勝手に動く |
| グローバルとプロジェクトの違い | 候補一覧の `(user)` と `(project)` |
| `.claude/commands/` との違い | 単一.mdで動くのはこっち。混同注意 |
| 最初のSkillの作り方 | Claudeに作らせるのが早い |

---

## カスタムSkillの仕組み ― SKILL.md形式で作る

### ①何をするか

カスタムSkillは、**スキル名のディレクトリを作り、その中に `SKILL.md` を置く**ことで定義します。

```
プロジェクトルート/
└── .claude/
    └── skills/
        ├── deploy-check/
        │   └── SKILL.md    ← これがカスタムSkill
        └── laravel-review/
            └── SKILL.md    ← 複数作れる
```

ここが重要なのですが、`.claude/skills/deploy-check.md` のような**単一のMarkdownファイルを置く形式では認識されません**。実際に試したところ、エラーが出るわけでもなく、ただ `/` の候補に出てこないだけでした（詳しくは後述のつまずいたポイントで）。

### ②実際の挙動

`SKILL.md` の基本構造はこうです。frontmatter（ファイル冒頭の `---` で囲む部分）に `name` と `description` を書きます。

```
---
name: deploy-check
description: このSkillが何をするかの説明（Claudeが使いどころを判断する材料になる）
---

ここにClaudeへの指示を自然言語で書く。
どんな作業をするか、どんな順序で進めるか、
何に注意するかなどを書けばOK。
```

このファイルを置くと、`/deploy-check` として `/` の候補に表示されて呼び出せるようになります。ディレクトリ名と `name` は揃えておくのが分かりやすいです。

そして地味に嬉しいのが、**再起動が不要**なこと。セッションの途中で新しいSkillを追加しても、すぐに `/` の候補に出てきました。作って→試して→直すのサイクルが速く回せます。

### ③活用方法・つまずいたポイント

* **「候補に出ない＝形式が間違っている」のサイン**。エラーが出ないぶん気づきにくい
* frontmatterの `description` は省略せずに書く。あとで紹介する「自動起動」に効いてきます
* 最初から完璧を目指さず、**いつも打っている長いプロンプトをそのまま本文に貼る**だけでも十分効果があります

---

## 実践例① Laravelデプロイ前チェック（/deploy-check）

実践例は2つともLaravel（PHPのフレームワーク）の例ですが、Laravelを知らない方は「**中身のチェックリストを自分の業務の手順に差し替えれば同じことができる**」とだけ掴んでもらえればOKです。

`.claude/skills/deploy-check/SKILL.md` として作ります。

```
---
name: deploy-check
description: Laravelプロジェクトをデプロイする前に必要なチェックを一括で行う
---

以下のチェックを順番に行い、問題があれば報告してください：

1. `php artisan config:cache` が通るか確認（設定ファイルにエラーがないか）
2. `php artisan route:list` でルート定義にエラーがないか確認
3. .env.example と .env のキーが一致しているか確認（.envにあって.env.exampleにないキーを報告）
4. composer.json の "require" に開発用パッケージが混入していないか確認
5. git diff で未コミットの変更がないか確認

問題がなければ「デプロイ準備OK」と報告してください。
問題があれば優先度順にリストアップしてください。
```

本文にこう書いておけば、`/deploy-check` の一言で一連のチェックを頼める、という書き方の例です。デプロイのたびに確認していたことが一言になるのは地味に大きいです。

---

## 実践例② Laravel専用コードレビュー（/laravel-review）

`.claude/skills/laravel-review/SKILL.md` として作ります。

```
---
name: laravel-review
description: LaravelとPHPのベストプラクティスに特化したコードレビューを行う
---

現在のブランチの変更をレビューしてください。
以下の観点で確認し、問題点を優先度（高・中・低）付きでリストアップしてください：

**セキュリティ**
- SQLインジェクション（生クエリの使用、バインドパラメータ漏れ）
- マスアサインメントの脆弱性（$fillable/$guarded の設定漏れ）
- 認証・認可の抜け（middleware未設定のルート）

**Laravelの作法**
- コントローラーにビジネスロジックが書かれていないか
- N+1問題（with() のないリレーション取得）
- バリデーションがFormRequestではなくコントローラーに書かれていないか

**コード品質**
- 同じ処理の重複
- マジックナンバーの定数化漏れ
- 長すぎるメソッド（20行を超えるものは要検討）
```

こちらは、汎用の `/code-review` より自分のプロジェクトに特化した観点でレビューさせる想定の例です。観点リストを自分のチームの規約に差し替えれば、そのままレビューSkillの叩き台になります。

---

## descriptionを書いておくと、自然言語から自動で動く

これは試してみて「おっ」となった挙動です。

`/deploy-check` が認識された状態で、スラッシュコマンドを使わずに「**デプロイ前の確認をして**」と普通にお願いしてみました。すると、Claudeが「デプロイ前チェック用のスキル deploy-check を実行します。」と言って、自動でSkillを使ってくれました。画面には `Skill(deploy-check)` と `Successfully loaded skill` が表示されます。

![](https://static.zenn.studio/user-upload/76379e4c20a7-20260707.png)

つまり、**コマンド名を覚えていなくても、descriptionに合う依頼をすればClaudeが勝手にSkillを引っ張ってきてくれる**ということです。descriptionを「なんとなく」で書かずに、「いつ使うSkillか」が伝わるように書いておく価値はここにあります。

白状すると、実はこのとき私のSKILL.mdはfrontmatter（nameとdescription）だけで、**本文の指示を書き忘れていました**。それでもClaudeはdescriptionから意図を汲んでSkillを起動して動いてくれました。とはいえ、狙い通りの手順で確実に動かすには本文の指示が必要なので、書き忘れはおすすめしません。

---

## グローバルSkillとプロジェクトSkillの違い

置き場所によって有効範囲が変わります。

| 場所 | 有効範囲 | 候補一覧の表示 |
| --- | --- | --- |
| `~/.claude/skills/` | すべてのプロジェクトで使える | `(user)` |
| `.claude/skills/` | そのプロジェクト内だけ | `(project)` |

`~/.claude/skills/` に同じ形式で置いたSkillは、別のプロジェクトを開いても `/` の候補に出てきました。候補一覧では末尾のラベルで区別できます。

![](https://static.zenn.studio/user-upload/ee7f38fe4220-20260707.png)

ちなみに、**同じ名前のSkillをuser側とproject側の両方に置くと、候補に2つ並んで表示されました**。どちらが動いているのか分からなくなるので、名前はかぶらせないほうが無難です。

![](https://static.zenn.studio/user-upload/10987a5dc715-20260707.png)

「どのプロジェクトでも使いたい」汎用的なSkillはグローバルに、「このプロジェクト専用」はプロジェクト内に、という使い分けが自然です。

---

## 似てるけど別物：カスタムスラッシュコマンド（.claude/commands/）

ここ、混同しやすいポイントなので1セクション取って整理します。

実は「**単一のMarkdownファイルを置くとファイル名がコマンド名になる**」という仕組み自体は存在します。ただしそれはSkillではなく、**カスタムスラッシュコマンド**という別機能で、置き場所は `.claude/commands/` です。

```
.claude/
├── skills/
│   └── deploy-check/
│       └── SKILL.md          ← Skill（ディレクトリ＋SKILL.md）
└── commands/
    └── deploy-check2.md      ← カスタムスラッシュコマンド（単一.mdでOK）
```

実際に `.claude/commands/deploy-check2.md` を置いてみたところ、`/deploy-check2` が `(project)` ラベル付きで候補に表示されました。しかも候補一覧上では**Skillもcommandsのコマンドも同じように並ぶ**ので、見た目では区別がつきにくいです。

![](https://static.zenn.studio/user-upload/fc27baef0955-20260707.png)

解説記事によってはこの2つが混ざっていることがあるので、「単一.mdで作る」と書いてあったらcommandsの話、「SKILL.md」と書いてあったらSkillの話、と読み分けてください。

---

## つまずいたポイント

**単一.mdで作ったら、候補に出なかった**

カスタムSkillは今回が初挑戦だったのですが、最初に `.claude/skills/deploy-check.md` という単一ファイルで作りました。結果は、再起動しても `/` の候補に出てこない。エラーも出ないので「そんなパターンもあるんだなあ」と首をかしげることに。

解決方法はシンプルで、**Claude Code本人に「Skillの正しい作り方を教えて」と聞きました**。すると `.claude/skills/<スキル名>/SKILL.md` の形式を教えてくれて、その通りに作り直したら一発で認識されました。ドキュメントを漁る前に、まずClaudeに聞くのが早いです。

**「再起動すれば認識される」は不要だった**

認識されないとき、反射的に再起動を試しがちですが、正しい形式で置けば**セッション中でも即座に候補に反映されます**。候補に出ないなら、再起動ではなくファイル形式を疑ってください。

**Skill化の粒度が難しい**

これは現在進行形で悩んでいます。いつも打つ長いプロンプトの中で、同じ項目名や概念名を毎回入力しているのをどうにかしたいのですが、「どこからどこまでを1つのSkillにするか」はまだ手探りです。最初のうちは「よく打つプロンプトを1本＝1 Skill」くらいの雑な粒度でいいと思います。

---

## 最初のSkillはClaudeに作らせるのが早い

「で、何から作ればいいの？」という人へ。**Skill自体をClaudeに作らせる**のがおすすめです。ただし丸投げではなく、目的と役割を自分の言葉で渡すのがコツです。

私が最初に作ったのは `/article-team` という、記事制作のクオリティを上げるための「制作チーム」Skillです。ディレクター・インタビュアー・ライター・読み手（ターゲットペルソナ）・校閲・戦略担当という複数のサブエージェント（[Part4](https://zenn.dev/kaihatsu_biyori/articles/claude-code-subagent-basics)で解説した仕組みです）を束ねるワークフローになっています。

作り方は、Claudeに**目的・背景・目標を伝えた上で、エージェントごとのポジションと、やってもらいたい内容・役割を具体的に示す**というもの。各エージェント200〜300文字くらいで、「マークダウン形式とまではいかないけど、言葉で伝えたいことをぎゅっと詰め込んだ」感じです。

そして初めて実行したのが、まさにこの記事の制作でした。感想は「**期待以上**」です。

実務のLaravel案件でも、関連資料を読み解いて要約文書を作るSkillを作りました。次は管理画面のCRUDページ一式（model・controller・DB構成ファイルなどの生成）や、MTG議事録からタスクの要件定義とissue作成までを流すSkillを作りたいと思っています。

---

## CLAUDE.mdとSkillの使い分け

[Part3](https://zenn.dev/kaihatsu_biyori/articles/claude-code-claudemd-md)で紹介したCLAUDE.mdと役割がかぶりそうですが、私の中の整理はこうです。

**絶対的なルールや条件はCLAUDE.md、単体で使いたい「魔法」のようなものはSkill。**

CLAUDE.mdは毎回のセッションで常に効いてほしい前提。Skillは唱えたいときに唱える呪文。この分け方でだいたい迷わなくなりました。

---

## まとめ

| ポイント | 内容 |
| --- | --- |
| 正しい形式 | `.claude/skills/<スキル名>/SKILL.md`（単一.mdは認識されない） |
| frontmatter | `name` と `description` を書く |
| 反映タイミング | 再起動不要。置けばセッション中でも即候補に出る |
| 自動起動 | descriptionが書けていれば自然言語の依頼からClaudeが自動で使う |
| 置き場所 | グローバル `~/.claude/skills/`（user）とプロジェクト `.claude/skills/`（project） |
| 混同注意 | 単一.mdで動くのはカスタムスラッシュコマンド（`.claude/commands/`） |

毎回同じプロンプトを打っていると気づいたら、それはSkillにするサインです。まずは1個、Claudeに相談しながら作ってみてください。

次回のPart8では、外部ツールとの連携を可能にするMCPサーバーの基礎を解説します。

---

*開発日和では、Claude Codeの使い方を実体験ベースで発信しています。*  
*質問・感想はコメントやXの [@webpull](https://twitter.com/webpull) までどうぞ。*
