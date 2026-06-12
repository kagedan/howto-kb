---
id: "2026-06-11-8-ようやく言えるharness-starter-kit-は-hidden-oracle-ab-テス-01"
title: "8. ようやく言える：harness-starter-kit は hidden-oracle A/B テストで成功した"
url: "https://zenn.dev/yuuaan/articles/55501dd45e2522"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/944d5fd7b0d3-20260611.png)

# 8. ようやく言える：harness-starter-kit は hidden-oracle A/B テストで成功した

こんにちは。韓国出身のジュニア開発者です。

日本語はまだ翻訳ツールの助けを借りながら書いているので、不自然な表現があれば大目に見ていただけると嬉しいです。

これは `harness-starter-kit` シリーズの第 8 回です。

これまでの記事では、かなり慎重に書いてきました。

あまり早い段階で、

> harness によって agent が強くなることを証明できた。

とは言いたくなかったからです。

当時は、まだ evidence が十分ではありませんでした。

言えたのは、せいぜい次のようなことでした。

* harness はルールを repo の中に残せる
* harness はエラーをより早く表面化させる
* harness は PR 内の agent work をレビューしやすくする
* benchmark runner によって、測定そのものが再現可能になり始めた

しかし今回は、少しだけ前に進めると思っています。

もちろん、

> harness によって、すべての coding agent がすべてのタスクで強くなる。

とはまだ言えません。

でも、今ならもう少し責任を持ってこう言えます。

> repository convention を守る必要があるタスクにおいて、harness-starter-kit には明確な効果がある。

今回、hidden-oracle A/B テストを行いました。

結果は次のとおりです。

| Target | Harness | Runs | Successes | Wrong-file edits | Timeouts |
| --- | --- | --- | --- | --- | --- |
| `flask-no-harness` | No | 12 | 0 | 11 | 3 |
| `flask-yes-harness` | Yes | 12 | 11 | 0 | 0 |

この結果を見て、初めてこう感じました。

> harness-starter-kit は、単に「なんとなく便利」なだけではない。  
> 実際に agent の行動に影響を与え始めている。

---

## なぜ今回のテストは、これまでのテストより重要なのか

以前は visible oracle のテストを行っていました。

visible oracle とは、

> 検証コードが target repo の中にあり、agent から見える状態である

という意味です。

この方法自体が間違っているわけではありません。

むしろ、次のようなことを確認するにはとても有効です。

* benchmark runner が正常に repo を clone できるか
* task spec が正しく書かれているか
* verification command が安定して動くか
* scoring logic にバグがないか
* file boundary violation を検出できるか

しかし、harness そのものの有効性を示したい場合、visible oracle には問題があります。

no-harness の agent でも oracle code を読むことができてしまうからです。

つまり、repo の中に convention がなくても、agent はテストコードから逆算して、

* endpoint はどういう名前であるべきか
* response shape はどうあるべきか
* error code は何であるべきか
* ドキュメントには何を書くべきか

といったことを推測できてしまいます。

そうなると、no-harness 側の成績が必要以上に高く出る可能性があります。

そこで今回は hidden oracle に切り替えました。

hidden oracle とは、

> 実際の検証コードを target repo の中には置かず、benchmark runner 側に置く

という方式です。

agent が Flask repo を編集している間、最終的な採点ロジックは見えません。

agent が頼れるのは、次のものだけです。

* prompt
* repo 内のコード
* repo 内のドキュメント
* AGENTS.md
* conventions
* check script

これは、私が本当に測りたかったことにより近いです。

> task が repo-local convention の理解を必要とする場合、harness は agent が正しく作業する助けになるのか？

---

## 今回の task はどう設計したのか

今回は 2 つの Flask repo を用意しました。

1 つは、

もう 1 つは、

です。

2 つの repo の基本的なアプリ構成は似ています。

ただし、`flask-yes-harness` には harness 情報が含まれています。

* AGENTS.md
* coding conventions
* domain glossary
* decision records
* check\_harness.py
* ドキュメントの配置ルール
* benchmark companion docs のルール
* sandbox で依存関係のインストールに失敗したとき、無限に再試行しないルール

今回用意した task は 4 つです。

1. stock risk report API
2. supplier readiness API
3. bundle quote API
4. reservation preview API

それぞれの task を、no-harness と yes-harness の両方で 3 回ずつ実行しました。

合計で 24 回の live Codex run です。

Codex の設定は次のとおりです。

```
CODEX_EXEC_ARGS='-c model_reasoning_effort=medium -c service_tier=priority'
```

つまり、reasoning effort は medium、service tier は priority です。

---

## 成功条件は「コードが動くこと」だけではない

今回の scoring は、pytest だけを見ているわけではありません。

1 回の run が成功と判定されるには、次の条件をすべて満たす必要があります。

1. agent が正常終了する
2. `git diff --check` に通る
3. pytest に通る
4. hidden oracle に通る
5. wrong-file edits がない
6. forbidden-file edits がない

ここはとても重要です。

最近、私はますますこう感じています。

> 実際のプロジェクトにおいて、「動く」ことは最低条件にすぎない。  
> それ以上に重要なのは、repo のやり方に従っているかどうかだ。

たとえば今回の task では、編集してよい場所は次の範囲でした。

しかし、次のようなファイルは編集すべきではありません。

```
README.md
requirements.txt
benchmarks/**
.env
runs/**
results/**
```

結果はかなり明確でした。

`flask-no-harness` は、単に機能を正しく実装できなかっただけではありません。  
かなりの頻度で、編集すべきではない場所も変更していました。

一方で `flask-yes-harness` は、機能を正しく実装しやすかっただけでなく、ファイル境界もよりよく守れていました。

---

## なぜ no-harness は失敗したのか

`flask-no-harness` が失敗した理由は、Codex が Flask を書けないからではありません。

より正確に言うと、この repo が何を求めているのか分からなかったからです。

その結果、agent は推測します。

たとえば、

* endpoint 名を間違える
* response shape を間違える
* supplier map を間違える
* safety stock のルールを間違える
* ドキュメントの配置場所を間違える
* README をついでに変更してしまう

といった失敗が起きました。

これらは、実際のプロジェクトでよく起きる agent の問題にかなり似ています。

agent は、コードをまったく書けないわけではありません。

ただ、repo-local context が足りないのです。

そして、その context が人間の頭の中にしか存在しない場合、agent は推測するしかありません。

---

## なぜ yes-harness は成功したのか

`flask-yes-harness` が成功した理由も明確です。

harness がモデルを突然賢くしたわけではありません。

人間の習慣の中に散らばっていた情報を、agent が読めて、check もできる repo 内の情報に変えたことが大きいです。

たとえば、

* API 命名規則はどこにあるのか
* domain term はどう解釈すべきか
* companion docs はどこに書くべきか
* どのファイルを不用意に変更してはいけないのか
* check command はどう実行すべきか
* sandbox 内で依存関係のインストールに失敗したとき、無限に再試行しないこと

こうしたものは、一見すると特別な魔法には見えません。

しかし coding agent にとっては非常に重要です。

なぜなら、agent は新しい task を始めるたびに、ほとんど「今プロジェクトに入ったばかりの人」のような状態だからです。

repo が何も教えてくれなければ、agent は一般的な経験だけで作業するしかありません。

しかし実際のプロジェクトで最も失敗しやすい部分は、一般論ではありません。

そのプロジェクト固有の convention です。

---

## 今回のテスト後に感じた harness-starter-kit の強み

今回のテストを通じて、harness-starter-kit の強みをより具体的に理解できました。

第一に、繰り返し説明する手間を減らせます。

以前は新しい session を始めるたびに、agent に毎回こう伝える必要がありました。

> README は変更しないで。  
> 先にテストを実行して。  
> ドキュメントは docs/decisions に置いて。  
> requirements.txt は勝手に変更しないで。  
> このプロジェクトの API response はこう書いて。

今は、こうした情報を repo の中に残せます。

第二に、agent の推測を減らせます。

convention がなければ、agent は一般的な経験に頼って推測します。

convention があれば、少なくとも agent は先にプロジェクトのルールを読むことができます。

第三に、エラーを見つけやすくなります。

wrong-file edits、forbidden-file edits、verification failure、timeout などを記録できます。

これにより、「今回の agent はなんとなく微妙だった」と感覚で言う必要がなくなります。

代わりに、こう言えます。

> 変更してはいけないファイルを編集した。  
> hidden oracle に通らなかった。  
> timeout した。  
> pytest は通ったが、repo contract には合っていなかった。

第四に、改善を feedback loop にできます。

1 回の失敗は、単なる失敗で終わりません。

それは次のような形に変えられます。

* failure memory
* convention update
* check script update
* benchmark task update
* 次回 run の比較データ

これこそが、私が最初に harness を作りたかった理由です。

---

## それでも、過大評価はしたくない

今回の結果は良いものでした。

しかし、それでも私はこうは言いたくありません。

> harness-starter-kit を使えば、すべての coding task が良くなる。

それは厳密ではありません。

今回のより正確な結論は次のとおりです。

> repo-local convention を守る必要があるタスクにおいて、harness-starter-kit は明確に役立つ。

つまり、harness の最も大きな価値は、「一般的なコーディング能力」を上げることではありません。

むしろ、次のような能力を高めることです。

* contract discovery
* file-boundary discipline
* documentation placement
* validation discipline
* project-specific consistency

これらは実際のプロジェクトではとても重要です。

実際のプロジェクトは LeetCode ではありません。

コードは正しい場所に置かれる必要があります。

API は既存の約束に従う必要があります。

ドキュメントはチームが見つけられる場所に書く必要があります。

依存関係は勝手に追加してはいけません。

失敗理由は後からレビューできる必要があります。

これが harness の価値です。

---

## 今なら責任を持って言えること

第 8 回まで書いてきて、ようやくこう言えます。

> harness-starter-kit は、hidden-oracle A/B テストで成功した。

その成功の意味は、

> agent が魔法のように強化された

ということではありません。

そうではなく、

> repo が agent に対して、より明確な operating environment を提供できた

ということです。

今回、no-harness は 0/12 でした。

yes-harness は 11/12 でした。

wrong-file edits は 11 から 0 に減りました。

timeouts は 3 から 0 に減りました。

私にとって、これはもう「なんとなく便利」という段階ではありません。

レビュー可能な evidence です。

もちろん、次のステップとして、さらにサンプルを広げる必要があります。

* より多くの task
* より多くの repo
* より多くの framework
* より多くの agent
* より多くの repetition

それでも少なくとも今は、以前よりも harness-starter-kit に対する信頼が強くなりました。

これは万能ツールではありません。

むしろ、repo を agent が作業しやすい環境に変えるための starter kit に近いものです。

もしあなたも Cursor、Claude Code、Codex、あるいは他の coding agent をよく使っているなら、まずはとても小さなところから始めてみるのがよいと思います。

> agent に何度も繰り返し伝えているルールを repo に書く。  
> 間違って編集されやすいファイル境界を明確にする。  
> 検証コマンドを実行可能な check にする。  
> 失敗を記録する。  
> そして、実際の task outcome を使って改善しているかを見る。

今回、私はようやく少し明確な答えを見ることができました。

convention-dependent work において、

> harness は有効です。

git: <https://github.com/harnessworks/harness-starter-kit>
