---
id: "2026-06-08-2-harness-starter-kitを実プロジェクトに入れて試してみ-01"
title: "2. harness-starter-kitを実プロジェクトに入れて試してみ"
url: "https://zenn.dev/yuuaan/articles/13da05c1ae5550"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/27cb22178d14-20260608.png)

# harness-starter-kitを実プロジェクトに入れて試してみた

こんにちは。韓国出身のジュニア開発者です。  
日本語はツールの助けも借りながら整えています。少し不自然な表現があればご容赦ください。

前回の記事では、なぜ私が `harness-starter-kit` を作ったのかを書きました。

理由はシンプルです。  
Cursor や Claude Code の新しいセッションを開くたびに、同じプロジェクトルールをエージェントへ説明し直したくなかったからです。

この記事は、きれいに整理されたチュートリアルではありません。  
実際のプロジェクトにこのスターターキットを入れてみたとき、何が起きたのかを記録したものです。

## 最初に心配していたこと

最初に不安だったのは、次のような点でした。

* エージェントがテンプレートを大量にコピーしてしまわないか
* 既存プロジェクトの構造を壊してしまわないか
* 誰もメンテナンスしない `docs/` ディレクトリが増えるだけにならないか

だからプロンプトでは、何度も次のことを強調しました。

* まず現在のプロジェクトを調べる
* テンプレートを盲目的にコピーしない
* 必要最小限のものだけを追加する
* 既存ファイルを勝手に上書きしない

## エージェントに渡したプロンプト

おおよそ、次のようなプロンプトを渡しました。

```
Use this kit to apply harness engineering to this repository:
https://github.com/baskduf/harness-starter-kit

Clone the kit into ./harness-starter-kit, read it as read-only reference,
inspect THIS repository first, then add only the minimum useful harness.

Do not blindly copy templates.
Do not overwrite files without explaining why.
Preserve the target repository's existing architecture, tools, docs, and conventions.
```

## 実際の結果

実際に動かしてみると、主に次のものが追加されました。

* `AGENTS.md`
* いくつかの小さな検査スクリプト
* `docs/decisions/`
* `docs/failures/`
* adoption report

私にとって重要だったのは、プロジェクトを特定の「標準構造」に無理やり変えなかったことです。

もともとチャットで何度も説明していたルールを、リポジトリの中に移しただけでした。

たとえば、次のようなルールです。

```
- 変更後は既存のテストを実行する
- 自動生成ファイルは変更しない
- 既存のディレクトリ構成に従う
- ユーザーに見える問題を修正した場合は `docs/failures/` に記録する
```

## Before / After

Before:

* ルールはチャットログの中にしかなかった
* 新しいセッションではコンテキストを忘れやすかった
* エージェントのミスは人間が見つけるしかなかった
* 失敗から得た知識が残りにくかった

After:

* ルールがリポジトリに入った
* エージェントが毎回 `AGENTS.md` を読めるようになった
* 一部のミスはスクリプトで早めに検出できるようになった
* 過去の失敗を `docs/failures/` に残せるようになった

## それでも、まだ「効果がある」とは言い切れない

正直に言うと、これで本当にエージェントが良くなったとは、まだ証明できません。

言えるのは、いくつかのルールがチャットログだけに閉じ込められなくなった、ということです。  
次のセッションを開いたとき、エージェントが少なくともそのルールを読む機会を持てるようになりました。

ただし、これが本当にエラーを減らすのかは、まだ別の問題です。

たとえば、次のようなことです。

* 間違ったファイルを変更する回数が減るのか
* テスト実行を忘れにくくなるのか
* 同じバグを繰り返しにくくなるのか
* reviewer の手戻りが減るのか

これらを言うには、もっと多くの実プロジェクトでのデータが必要です。

だから私は、Doctor のスコアが上がったからといって、エージェントの品質が上がったとは言いません。  
本当に大事なのは、実際の task outcome です。

## これから検証したいこと

今後は、もっと多くの実プロジェクトでの利用状況を集めたいと思っています。

もし Cursor や Claude Code をよく使っていて、似たような問題に困っている方がいれば、ぜひこのプロジェクトを見てみてください。

GitHub:

<https://github.com/baskduf/harness-starter-kit>

現在、貢献しやすい issue もいくつかあります。

* Go / Rust / iOS / Rails / Laravel profile を追加する
* monorepo adoption example を書く
* GitLab CI adoption note を補足する
* Harness Doctor のメッセージを改善する
* 実際の adoption report / effectiveness evidence を追加する

この考え方に問題があると思う場合も、ぜひ率直に指摘してください。

私はまだジュニア開発者なので、経験のある開発者からのフィードバックを特に聞きたいです。
