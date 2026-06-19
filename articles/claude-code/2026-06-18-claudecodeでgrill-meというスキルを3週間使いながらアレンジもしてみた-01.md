---
id: "2026-06-18-claudecodeでgrill-meというスキルを3週間使いながらアレンジもしてみた-01"
title: "ClaudeCodeで/grill-meというスキルを3週間使いながらアレンジもしてみた"
url: "https://zenn.dev/mukuil_blog/articles/1ccfd44928e825"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "TypeScript", "zenn"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは！[株式会社ムクイル](https://www.mukuil.com/)のYuseiです！

以前、Claude Code での開発における `docs/` フォルダ構成についての模索という記事を書きました。

<https://zenn.dev/mukuil_blog/articles/1796a8b0f3cd48>

そのフォルダ構成で開発サイクルを回していく中で、改めて大切だと感じているのが「**Claude Code が出力する内容と、自分が頭の中で描いている設計との差をどこまで小さくできるか**」という点です。ここがズレていると無駄な手戻りが増えてしまうので、実装前に入念に認識合わせをすることが重要だと考えています。

これまでは認識合わせに Claude Code の `/plan`（プランモード）を使っていたのですが、3週間ほど前から `/grill-me` というスキルを使うようになりました。これがかなり良かったので、自分なりのアレンジも加えながら使っています。

この記事では、以下について書いています。

* `/grill-me` の中身とセットアップ方法
* これまで使っていた `/plan` との違い
* 実際に使う中で直面した失敗・トラブルと、その解決法

この記事は「この手法がおすすめです」という主張をするものではなく、**「こういう形でやったら、こんな結果になった」というレポートベースの記事**です。似たような内容で詰まっている方・悩んでいる方の、何かしらのヒントになればと思って書いています。

---

## /grill-me の中身・セットアップ

### 中身の説明

`/grill-me` は、Matt Pocock 氏（AI Hero / Total TypeScript で知られる方）が公開しているスキルです。本人の `.claude` ディレクトリから公開されている `mattpocock/skills` というリポジトリに含まれています。

名前のとおり「計画や設計について、**認識が揃うまで容赦なく質問攻め（grill）にしてくる**」スキルで、SKILL.md 自体はとても短いのが特徴です。実際の中身がこちらです。

```
---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.
```

ポイントは、

* **決定の木（decision tree）を1本ずつ枝分かれをたどりながら潰していく**こと
* 質問は**1つずつ**投げてくること
* 各質問に対して**AI側のおすすめ回答も併せて提示してくれる**こと
* コードベースを見れば分かる質問は、**勝手にコードを読んで解決してくれる**こと

たったこれだけの記述で、想像以上に深く詰めてくれます。

### セットアップ方法

`mattpocock/skills` の場合、ターミナルで以下のコマンドを実行するだけでセットアップできます。

```
npx skills@latest add mattpocock/skills
```

実行すると、

* **どのスキルを入れるか**
* **どのコーディングエージェントに入れるか**

を選ぶ画面が出てきます。

![SKILLS選択画面１](https://static.zenn.studio/user-upload/59255a9df346-20260611.png)

![SKILLS選択画面２](https://static.zenn.studio/user-upload/377e9897fe03-20260611.png)

矢印キーでgrill-meまで照準を移動させて、spaceで選択できます

↓選択状態（□の色が変わります）

![SKILLS選択画面３](https://static.zenn.studio/user-upload/5b478ac84a49-20260611.png)

このとき、**グローバルスキル（全プロジェクト共通）として入れるか / 特定フォルダ限定のスキルとして入れるか**も選べます。常用するなら前者、プロジェクト固有で試したいなら後者、といった使い分けができます。

### 自分の使い方

ベースはそのまま使えるのですが、後述するトラブルに対応するため、SKILL.md に少し文言を追記しています。これによって途中で起きていた挙動のブレが消えました。具体的な追記内容は **「使っていく中で直面した失敗・トラブル」** の章で紹介します。

## /plan との違い

これまで認識合わせに使っていた `/plan` は、ざっくり言うと **3〜4問のやり取り1往復で計画づくりが完了する**イメージでした。手軽な反面、自分の用途では以下のような物足りなさがありました。

* **計画は立つが、粒度が大雑把**  
  修正したい箇所があると、そのつど自分から指摘して内容を直す必要がある
* **1回の流れで詳細まで詰めきれない**  
  指示が抽象的になるほど、理想と出力の乖離が大きくなる
* **どこかで認識の齟齬が生まれやすい**  
  細部の細部まで決め切らないので、自分が想定していた挙動と、実際にできあがる挙動にズレが出る

`/grill-me` は逆に「決定の木を1枝ずつ潰す」設計なので、**詰めきるまで終わらない**のが大きな違いです。質問数が多くなる分、認識のズレは確実に減りました。

## /grill-me を使っていく中で直面した失敗・トラブルと解決法

### ① 質問の仕方によって挙動が変わってしまう

使っていて最初に困ったのが、**こちらの渡し方（対話モードか非対話モードか）によって挙動が変わってしまう**ことでした。途中で質問攻めをやめて勝手に実装に進んでしまったり、まとめに入ってしまったりすることがありました。

そこで、SKILL.md に `## Rules (important)` セクションを追記して、「これは唯一のタスクで、インタビューが終わるまで他のことをしない」というルールを明示することにしました。これが上で触れた「追記した文言」です。

```
---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Rules (important)
- This is your ONLY task. Do not implement, summarize, or move on to anything else until the interview is explicitly finished.
- After I answer each question, ALWAYS ask the next one. Continue until every branch of the decision tree is resolved.
- The interview ends ONLY when I say "done" / "終わり" / "stop", or when there are genuinely no unresolved branches left.
- If I gave you multiple instructions in one message, ignore the others for now and run only this interview to completion first.
```

この4行のルールを足したことで、途中で勝手に実装に進んでしまうブレがなくなりました。

### ② 「選択式」と「解答式」、2つのパターンがある

`/grill-me` を使っていると、質問が次の2パターンのどちらかで返ってきます。

* **選択式**：番号で選べるUIが出るパターン
* **解答式**：地の文で質問が書かれていて、自由記述で答えるパターン

最初はこの違いが何で決まるのか分からなかったのですが、調べてみると **Claude Code の `AskUserQuestion` というツールを Claude が使うかどうか**で決まっていました。`AskUserQuestion` は Claude Code v2.0.21 以降で追加された、不明点や選択肢を構造化した多肢選択として提示する機能で、これが「選択式」の正体です。

ポイントは、**`/grill-me` 側でどちらにするか固定されているわけではなく、Claude がその質問ごとに判断している**ことです。

傾向としては、

* 選択肢が2〜4個にきれいに収まる質問 → **選択式**になりやすい
* (A)/(B) に長い推奨理由がつくような、ニュアンスの濃い質問 → **解答式**になりやすい

という感じでした。

どちらになるかは Claude 側の判断によるため、同じスキルでもパターンが変わります。「必ず選択式にしたい」といった固定はできないものと捉えておくのが無難です。

### ③ 選択式が生のJSONで出力されてしまった（不具合）

あるとき、本来は選択式で出るはずの内容が、**UIに描画されず生のJSONとして吐き出されてしまう**ことがありました。  
![エラー画像](https://static.zenn.studio/user-upload/09710aee26dd-20260618.png)

中身を見ると `question` / `header` / `multiSelect` / `options`（`label`・`description`付き）という構造になっていて、これはまさに `AskUserQuestion`（選択式）の中身です。つまり**選択式を出そうとして、描画に失敗してJSONがそのまま出てしまった**状態だと分かります。画面に `※ Baked for 49s` と出ているのも気になるところで、`AskUserQuestion` には60秒のタイムアウトがあるため、描画前にタイムアウト気味で失敗した可能性がありそうです。

ただ、**生JSONが出る確定的なトリガーまでは追えていません**。自分の場合は **Claude Code を再起動したら元に戻りました**ので、一時的な描画失敗として扱っています。

### ④ ちょくちょく思考して止まった

長く質問を続けていると、**途中で思考したまま止まってしまう**ことがありました。これは **Claude Code を再起動したら元に戻りました**。

文脈をそのまま引き継いで再開したい場合は、`/resume` で前のセッションを復活させられます。

## 感想（まとめ）

現在、実装計画を細部まで詰めていきたいときは、`/plan` ではなく `/grill-me` を登録して使うようになりました。

質問数が増える分、最初の認識合わせには時間がかかります。ですが、その分だけ実装後の手戻りが減るので、自分の「品質優先・小さく確認しながら進める」スタイルとは相性が良いと感じています。

繰り返しになりますが、これはあくまで一例のレポートです。もし `/plan` の粒度に物足りなさを感じている方がいれば、`/grill-me` を試したり、自分の使い方に合わせてルールを足してみたりする際の参考になれば嬉しいです。
