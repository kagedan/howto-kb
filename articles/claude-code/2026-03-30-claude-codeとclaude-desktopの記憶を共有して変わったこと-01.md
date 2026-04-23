---
id: "2026-03-30-claude-codeとclaude-desktopの記憶を共有して変わったこと-01"
title: "Claude CodeとClaude Desktopの記憶を共有して変わったこと"
url: "https://zenn.dev/cloto/articles/claude-memory-changed-dev-experience"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## 2つの Claude が別人だった

Claude Code で設計方針を詰めた翌日、出先のスマホから Claude に関連する相談をしたくなった。しかし昨日の議論は Claude Code のセッション内にしかない。結局、前提を一から説明し直すか、帰宅まで待つかの二択だった。

Claude Code には CLAUDE.md や MEMORY.md があるが、これはローカルのテキストファイルで、Claude Desktop からは見えない。逆に Claude Desktop のセッション履歴は Claude Code から参照できない。

さらに、セッション横断での文脈維持には構造的な限界がある。長い設計議論の内容を別のセッションから引き出そうとしても、全てが取得できるとは限らない。

## 「Claude Code に統一すればいい」は正ではない

「なら Claude Code だけ使えばいいのでは？」と思うかもしれない。自分も一時期そう考えた。

しかし実際にはそうならなかった。

* Claude Code の公式リモート機能はまだ不安定な場面がある
* Claude Desktop / web にはブラウザとしての利点がある: マルチモーダル入力、UI の手軽さ、スマホからのアクセス
* スマホで移動中に思いついたことを Claude に伝えておき、帰宅後に Claude Code で実装を続けたい

使い分けること自体は合理的だ。問題は「使い分けると記憶が分断される」ことにある。

## cpersona で記憶を共有する

この問題を解決するために、MCP Memory Server「cpersona」を開発した。

仕組みはシンプルだ。cpersona を Streamable HTTP サーバーとして起動し、Claude Code・Claude Desktop・スマホの Claude、全てが**同じ記憶 DB に HTTP 経由でアクセスする**。

### 完全無料で構築できる

「サーバーを公開する」と聞くとクラウドの月額費用を想像するかもしれないが、**自宅の PC をそのまま使える**。

この組み合わせで、自宅 PC 上の cpersona を安全に公開できる。ランニングコストはゼロだ。ここでは割愛するが、実際に可能なので是非調べてみてほしい。

詳しいセットアップ手順は[書籍の Ch.2](https://zenn.dev/cloto/books/claude-memory-mcp-server/viewer/ch02-quickstart) で解説している。

## 何が変わったか

### 朝の説明が消えた

以前は毎朝「このプロジェクトは Rust + Tauri で、DB は SQLite で…」と説明していた。

cpersona を導入してからは、セッション開始時に `recall` が走り、前回の作業文脈が自動的に復元される。Claude Desktop で会話しても、Claude Code で作業しても、どちらから始めても前回の続きから始まる。

### 長いセッションの情報消失がなくなった

これが一番大きかった。

Claude Desktop で 3 時間の設計議論をしたとする。重要な決定事項を含む長いセッションだ。従来なら、そのセッションが長くなるほど後から検索しにくくなる。

cpersona では、重要な決定を `store` で即座に保存する。セッション終了時には `archive_episode` で会話全体を要約保存する。**記憶は SQLite に永続化されているので、セッションの長さに関係なく、いつでも正確に取り出せる。**

### スマホの会話を Code に引き継げるようになった

移動中にスマホの Claude で「この機能、こういうアプローチで実装しよう」と会話する。cpersona に記憶が保存される。

帰宅後、Claude Code を開くと、システムプロンプトの指示に従って Claude が自動的に前回の記憶を取得してくれる。スマホでの会話内容がそのまま引き継がれ、すぐに実装に入れる。もちろん明示的に「recall して」と指示することも可能だ。

デバイスやクライアントを跨いでも、記憶が一本の線で繋がっている。

### 設計判断が消えなくなった

「なぜこの設計にしたのか」を `store` で保存しておくと、数週間後に別のクライアントから聞いても、当時の判断理由まで含めて回答できる。

コードコメントには書ききれない「議論の経緯」や「却下した代替案」が、記憶として残る。

### エピソードが一本化された

Claude Code で 2 セッション、Desktop で 1 セッション。それぞれの終了時に `archive_episode` で要約を保存する。3 つのエピソードが同じ DB に蓄積される。

数ヶ月分のエピソードが溜まると、Claude は「3 月に検索アルゴリズムを改善した」「2 月にリネーム作業をした」といった長期的な文脈を持って応答するようになる。どのクライアントから聞いても、同じ作業履歴を参照できる。

## cpersona がやっていること

cpersona は単純な RAG（ベクトル検索）ではない。3 つの層を組み合わせた検索で記憶を取り出す。

| 層 | 役割 | 例 |
| --- | --- | --- |
| **Agent Tools** | 記憶の保存・検索・管理 | `store`, `recall`, `archive_episode` |
| **RAG** | ベクトル類似度検索 | 「プログラミング言語」→「Rust と Python を使う」 |
| **Filter** | FTS5 全文検索 + プロファイル + キーワード | 固有名詞の完全一致、ユーザー属性 |

RAG 単体ではキーワードの完全一致を見逃す。Filter 層がこの穴を埋める。

他にも、記憶の鮮度を表す Confidence Score（時間減衰）、会話の要約であるエピソード記憶、ユーザー属性を蓄積するプロファイル記憶などを備えている。

## まとめ

Claude Code と Claude Desktop を使い分けるのは合理的だ。問題は記憶の分断にある。

cpersona を導入して、記憶を一箇所に集約するだけで：

* **朝の説明が不要に** — どちらのクライアントからでも前回の続き
* **長いセッションの情報消失を解消** — 重要な記憶は DB に永続化
* **デバイスを跨いだ引き継ぎ** — スマホの会話を Code に持ち込める
* **設計判断の蓄積** — 数週間後でも「なぜこうしたか」が残る
* **作業履歴の一本化** — 全クライアントのエピソードが一箇所に

## もっと深く知りたい方へ

cpersona の設計思想と実装の詳細を解説した書籍を Zenn で公開している。embedding モデルの選択肢や検索精度の改善方法も扱っている。

📘 **[『Claude は明日もあなたを忘れる — MCP Memory Server cpersona 設計と実践』](https://zenn.dev/cloto/books/claude-memory-mcp-server)**

Part 1（Ch.1〜4）は無料で読める。[Ch.2](https://zenn.dev/cloto/books/claude-memory-mcp-server/viewer/ch02-quickstart) にはインストールから動作確認までのクイックスタートガイドがある。

**GitHub**: [github.com/Cloto-dev/cloto-mcp-servers](https://github.com/Cloto-dev/cloto-mcp-servers)
