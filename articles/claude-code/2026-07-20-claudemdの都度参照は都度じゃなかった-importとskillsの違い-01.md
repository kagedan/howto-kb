---
id: "2026-07-20-claudemdの都度参照は都度じゃなかった-importとskillsの違い-01"
title: "CLAUDE.mdの「都度参照」は都度じゃなかった — @importとSkillsの違い"
url: "https://zenn.dev/tamaki2026/articles/a000b6db8ab649"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-rss"
query: ""
---

前回は、[Claude Codeに `.htaccess` を触らせないHook設定](https://zenn.dev/tamaki2026/articles/0a925c2be0ad86)を書きました。今回は「余計なものを読ませない」側の話です。

結論から言うと、私が「都度参照」のつもりで書いていた設定は、**都度になっていませんでした**。`/context` で実測して気づいたので、その記録を残します。

## やっていた設定

Web制作の案件で、CLAUDE.mdにこう書いていました。

```
## Skills（常時参照）
@DESIGN.md
@CLIENT.md
@skills/impeccable.md

## Skills（都度参照）
- デザイン実装時 : @skills/frontend-design.md
- jQuery実装時   : @skills/jquery.md
- フォーム実装時 : @skills/form-builder.md + @skills/accessibility.md
- レビュー時     : @skills/design-reviewer.md + @skills/accessibility.md
```

意図は明確でした。常に必要なコーディング規約は常時読ませて、工程ごとのルールはその工程のときだけ読ませる。そうすれば文脈がすっきりするはずだ、と。

見出しに「都度参照」と書いてあるので、私はずっとそう動いていると思っていました。

## /context で見たら全部載っていた

Claude Codeには `/context` というコマンドがあり、いま何が文脈を占めているかを見られます。`/context all` にすると内訳まで展開されます。

実行した結果がこれです。

```
Memory files · /memory
├ CLAUDE.md: 1.1k tokens
├ DESIGN.md: 1.3k tokens
├ CLIENT.md: 538 tokens
├ skills/impeccable.md: 226 tokens
├ skills/frontend-design.md: 359 tokens
├ skills/jquery.md: 343 tokens
├ skills/form-builder.md: 299 tokens
├ skills/accessibility.md: 247 tokens
└ skills/design-reviewer.md: 367 tokens
```

「都度参照」と書いたはずの5ファイルが、全部載っています。セッションを開いた直後、まだ何の作業も指示していない段階でです。

理由はシンプルで、CLAUDE.md の `@ファイル名` は**import記法**だからです。Claude Codeはセッション開始時にCLAUDE.mdを読み、その中の `@` を展開して、参照先の中身をまるごと文脈に取り込みます。見出しに何と書いてあるかは、読み込みのタイミングに一切影響しません。

当たり前と言えば当たり前なのですが、「都度参照」という自分で書いた見出しを、自分で信じてしまっていました。

## 本物の遅延読み込みは同じ画面に写っていた

面白いのは、同じ `/context all` の出力の少し下です。

```
Skills · /skills

User
├ jquery-responsive: ~50 tokens
├ site-audit: ~40 tokens
├ contact-form: ~40 tokens
├ delivery-check: ~40 tokens
└ site-estimate: ~40 tokens
```

こちらは Claude Code の公式なSkills機能で登録したものです。1つあたり40〜50トークンしかありません。

これは本文が載っていないからです。Skillsは `SKILL.md` のフロントマターに書いた `name` と `description` だけを常駐させ、Claudeが「今回はこれが要る」と判断したときに初めて本文を読みに行きます。説明文だけを目次として持っておいて、必要になったらページを開く、というイメージです。

公式ドキュメントにも、起動時にフロントマターの `name` と `description` がシステムプロンプトへ読み込まれ、本文などのファイルは必要時に読まれると書かれています（[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)）。実測した数字は、そのままこの仕様どおりでした。

つまり同じ画面に、2つの方式が並んで写っていたことになります。

|  | 常駐するもの | 1件あたり |
| --- | --- | --- |
| `@` import | 本文まるごと | 226〜367 tokens |
| Skills | 説明文だけ | 40〜50 tokens |

## ただし、容量の話ではない

ここは正直に書いておきます。「都度参照」としていた5ファイルの合計は1,615トークンです。全体の文脈は100万トークンあるので、割合にすれば0.2%にもなりません。**節約効果としては、ほぼ誤差です。**

なので「トークンを削減しましょう」という話にはしません。効いてくるのは別のところです。

**常に載っているものは、常に効きます。** 私は「作る役」のルールと「見直す役」のチェックリストを別ファイルに分けています。レビュー用のチェックリストが実装中もずっと文脈にある状態は、分けた意味を薄めます。

そしてもう一つ、**古くなったファイルも確実に読まれ続けます**。ここは実際に事故りかけたので、次回まとめて書きます。

## Skills形式への移し方

本当に都度読ませたいなら、公式のSkills形式にします。ディレクトリを作って `SKILL.md` を置くだけです。

```
~/.claude/skills/
└ jquery-responsive/
   └ SKILL.md
```

`SKILL.md` の冒頭にフロントマターを書きます。必須は `name` と `description` の2つだけです。

```
---
name: jquery-responsive
description: jQueryでハンバーガーメニューやスムーススクロールを実装するときの記法ルール。data属性セレクタ、.on()の使用、プラグイン不使用の方針を含む。
---

（ここから下に本文。常駐しない）
```

`name` はディレクトリ名と一致させます。

**そして `description` が全てです。** ここに書いた内容だけを見てClaudeが起動を判断するので、「いつ使うものか」が読み取れる文にする必要があります。「jQueryのルール」だけだと、どの場面で要るのか判断できません。実装するとき・修正するとき、という状況まで書くのがコツでした。

移行後は必ず `/context` で確認してください。トークン数が40〜50程度になっていれば、説明文だけが載っている状態です。

## どちらを使い分けるか

全部Skillsにすればいいという話でもありません。私は今こう整理しています。

**`@` import が向いているもの**

* プロジェクトの前提そのもの（DESIGN.md、クライアント情報）
* 常に守ってほしいコーディング規約
* 読み込まれていないと事故になるもの

**Skills が向いているもの**

* 特定の工程でしか使わない手順（見積、検査、納品前チェック）
* 呼ばれなくても実害がないもの
* 説明文で用途を一文にできるもの

線引きは「読み込まれていなかったら困るか」です。困るなら `@`、困らないならSkills。常時参照の3ファイルはこの基準で残しました。

## まとめ

* CLAUDE.md の `@` はimport記法。セッション開始時に本文がまるごと載る
* 見出しに「都度参照」と書いても挙動は変わらない
* Skillsは `description` だけ常駐し、必要時に本文を読む。これが本物の遅延読み込み
* 実測は `/context all`。思い込みで運用しない
* 効いてくるのは容量ではなく、何が常に効いているかという点

前回のHookもそうでしたが、AIまわりの設定は**書いたつもりと実際の挙動がずれていても、エラーが出ないので気づけません**。動いているように見えてしまう。だから定期的に実測する習慣のほうが、正しい設定を覚えることより大事だと思っています。

次回は、この「全部載っている」状態が実際に引き起こした事故について書きます。古いルールと新しいルールが同時に生きていて、危うくバリデーションの抜けたフォームが出来上がるところでした。
