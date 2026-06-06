---
id: "2026-06-06-claude-codeでthe-models-tool-call-could-not-be-pars-01"
title: "Claude Codeで「The model's tool call could not be parsed」エラーを回避する方法"
url: "https://qiita.com/natume_nat/items/76fe608d570caebb4f4c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-06-06"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

# はじめに

Claude Code（特にOpus 4.8）を日本語環境で使用していると、以下のパースエラーが発生してツール実行が失敗し、セッションが中断される不具合があります。

```text
The model's tool call could not be parsed (retry also failed).
```

セッションを切り替えても数ターン後にはゾンビのように蘇るこのエラーメッセージ、何度も見てうんざりしていませんか？
僕は何とか解決しようと試行錯誤していたのですが、中々上手くいきませんでした。
社内チャットで愚痴っていたところ、社員の1人が信じられない発言をしました。
> 「1回もclaude codeエラーでたことないけど」

深掘ってみたところ、彼は [issue](https://github.com/anthropics/claude-code/issues/63875) にあがっている内容に関連する設定をしていました。
この記事では、その**エラー回避に繋がる設定**と、**エラー発生時の即時リカバリー方法**を紹介します。

## 1. 解決方法 - `CLAUDE.md` に1行追加する

プロジェクトのルートディレクトリにある **`CLAUDE.md`** に、以下の指示を1行追加します。

```markdown
Think in English, interact with the user in Japanese.
```

これだけで、ユーザーとの対話（出力）は日本語のまま、エラーの発生を防ぐことができます。
この設定で上手くいかない方は、セッション開始時のプロンプトに「Think in English, interact with the user in Japanese.」と添えてみてください。

## 2. 原因と「思考の英語化」が有効な理由

### 根本原因
このエラーの本質は、クライアント側のバグではなく「マルチバイト文字（日本語・中国語など）の密度が高くなると、モデル側の出力デコーダーがバグを起こし、ツール呼び出し用のXMLタグ（`antml:invoke`）の構造を崩してしまう」というモデル応答側のストリーミングバグです。
タグが崩れるため、クライアント側がツールを認識できずにクラッシュします。

### 「/effort」を下げるだけでは防げない理由
これまでは暫定対策として「`/effort medium` や `low` に下げて思考を抑える」方法で試していました。しかし検証の結果、単にeffortを下げるだけでは日本語で思考している限り、直前の文脈や特殊文字の組み合わせ次第で依然として高頻度でエラーが発生することが分かりました。

### なぜ「思考の英語化」で治るのか
思考の「量」ではなく、思考の「言語（バイト密度）」を変えるのがこの対策です。

* **対話やコードの読み書き：** 日本語（従来通り）
* **内部の思考（Thinking）：** **英語（1バイト文字）に強制固定**

思考プロセスをすべて1バイト文字（ASCII）に縛ることで、出力全体のバイト密度が劇的に下がり、デコーダーのバグを完全に回避できます。結果として、どれだけ深く考えさせても（xhigh effortでも）、ツール呼び出しタグが正確に出力されるようになります。

## 3. リカバリー方法 - エラーが出たら「Esc 2回」

`CLAUDE.md` を設定後もエラーが発生してしまった場合、以下の方法で簡単にロールバックできます。

1. `Esc` キーを2回連続で押す
2. 直前の会話を選択して Enter を押す
3. Rstore conversation を選択して Enter を押す

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/488226/ff1f0f2f-ed26-487f-b468-3ecdbcf69290.png)

これだけで、**エラーが発生する直前のユーザーメッセージ（最後に送信したプロンプト）が入力欄に残った状態まで自動的にロールバック**されます。セッションを `/clear` したり、`/rewind` コマンドを入力したりすることなく、そのまま再送して正常な応答を引き直すことが可能です。（元の文章のままだとガチャになりがちですが）


## 4. まとめ

1. `CLAUDE.md` に「thinkingは英語でしてください。」と書く
2. エラーが出たら「Esc 2回」でロールバックして再送

この運用により、Opusのフルパワー（xhigh effort / 1M context）を維持したまま、ストレスなく開発を継続できます。

## 参考リンク
- [Claude Codeで「The model's tool call could not be parsed」エラーが発生する場合の調査と対策 - Qualitegブログ](https://blog.qualiteg.com/claude-code-tool-call-could-not-be-parsed/)
- [Recurring error: "The model's tool call could not be parsed (retry also failed)" interrupts sessions #63875](https://github.com/anthropics/claude-code/issues/63875)
