---
id: "2026-03-28-engram-claude-codeの会話を自動記録し過去の記憶を検索注入するローカル長期記憶システ-01"
title: "Engram - Claude Codeの会話を自動記録し、過去の記憶を検索・注入するローカル長期記憶システム"
url: "https://zenn.dev/okamyuji/articles/engram-claude-code-local-memory"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

!

**謝辞とインスピレーションについて**

Kizamiは、noprogllamaさんの記事「[Claude Codeに長期記憶を持たせたら、壁打ちの質が変わった](https://zenn.dev/noprogllama/articles/7c24b2c2410213)」と、そこで公開されている[sui-memory](https://github.com/noprogllama/sui-memory)に深くインスパイアされて開発されました。

記事で提唱されている設計原則（外部依存の排除、保存時トークン消費ゼロ、自動保存、常時参照、編集と削除、最小依存）は、Kizamiの設計の柱としてそのまま採用させていただいています。特に「常時参照」というアイデア——ユーザーが明示的に検索しなくてもhookによって過去の記憶が自動注入される——は、Claude Codeの長期記憶に対する考え方を根本から変えてくれるものでした。

noprogllamaさんご本人からインスパイアされたアプリの公開については快く[ご許諾](https://zenn.dev/link/comments/a4f1ff92f81c98)いただいています。設計思想をオープンに共有し、コミュニティでの発展を歓迎してくださる姿勢に、重ねて感謝申し上げます。

## はじめに

Claude Codeを使って日常的に開発していると、「3日前のセッションで決めたアーキテクチャ方針、なんだったっけ」「先週このバグの原因を調べたはずだけど、どのセッションだったか覚えていない」といった場面に遭遇します。

Claude Codeにはauto memoryやCLAUDE.mdによる記憶の仕組みがありますが、セッション単位の会話はセッション終了とともにコンテキストから消えてしまいます。過去の議論や設計判断を後から振り返るには、トランスクリプトを手動で探すしかありません。

この課題は以前から気になっており、[MCP対応ツールで実現する会話自動記録システム](https://zenn.dev/okamyuji/articles/44a06d1061a9d7)や[そのv2.0](https://zenn.dev/okamyuji/articles/eed8e26ff86bc4)で、RedisとFastAPIを使ったMCPベースの会話記録システムを実装していました。これらの実装を通じて会話履歴の検索と知識管理の基盤は構築できたものの、明示的に記録保存の指示が必須な点や、MCP Serverの常時起動が必要な構成、Redisへの依存が気になっていました。

そんな中で出会ったのが、noprogllamaさんの記事「[Claude Codeに長期記憶を持たせたら、壁打ちの質が変わった](https://zenn.dev/noprogllama/articles/7c24b2c2410213)」と[sui-memory](https://github.com/noprogllama/sui-memory)です。この記事は自分にとって大きな転換点でした。sui-memoryは「セッション会話を自動で保存し、次のセッションで自動的に参照する」という明快なアプローチを提示しており、「常時参照」の考え方——ユーザーが明示的に検索しなくてもプロンプト送信時に関連する過去の記憶が自動で注入される設計——は、それまで自分が取り組んでいたMCP経由の明示的検索方式とは根本的に異なる発想でした。MCP Serverを起動しなくても、Claude Codeのhookだけで完結する軽量さも魅力的でした。

さらに、記事で整理されている6つの設計原則は、「Claude Codeの長期記憶システムに何が必要か」という問いに対する明確な回答になっていました。個別のテクニックではなく、設計原則として体系的に言語化されていたからこそ、他の実装に応用可能な知見として非常に価値があったと感じています。

Kizamiはこの設計思想をTypeScriptで再実装したツールです。sui-memoryの設計原則をそのまま柱として採用し、以前のMCPベースの実装で得た知見を活かしつつ、SQLite単一ファイルとhookだけで動作する構成に改めました。coreモードではPythonやモデルダウンロードなしで動作し、hybridモードではRuri v3日本語embeddingによるベクトル検索にも対応しています。

ソースコードは[GitHub](https://github.com/okamyuji/kizami)で公開しています。

## claude-memを使い続けて気づいた課題

Kizamiを開発する前は、claude-memプラグインを使っていました。claude-memはClaude Agent SDKを使ったAI圧縮でセッションの要約を生成してくれる高機能なツールです。しかし使い続ける中でいくつかの課題が見えてきました。

1つ目はディスク肥大化です。当時使用していたバージョンのclaude-memでは、内部で使用しているChromaDBのインデックスが420GBまで膨張し、macOSのストレージを圧迫していました。この問題については[別の記事](https://zenn.dev/okamyuji/articles/claude-mem-chromadb-disk-bloat-fix)で詳しく書いています。

注記：claude-mem v10.3.0以降での改善について

この問題はKizamiの開発動機となった当時（2025年末〜2026年初頭）のclaude-memで経験したものです。claude-memはその後も活発に開発が続けられており、[v10.3.0（2026-02-18）](https://github.com/thedotmack/claude-mem/blob/main/CHANGELOG.md)ではChromaDBへの接続方式がWASMベースのembeddingからchroma-mcp MCP接続へと大幅に刷新されました。v10.2.3ではONNXモデルキャッシュの破損問題も修正されています。現在のバージョンでは、筆者が経験した肥大化の問題は改善されている可能性があります。claude-memは多機能で完成度の高いツールであり、最新版の評価は別途行う必要があります。

2つ目は記憶参照の方式です。claude-memはMCP Server経由でツールとして検索する仕組みのため、Claudeが自発的に過去の記憶を参照するかどうかはモデルの判断に依存します。関連する記憶があっても、Claudeがツールを呼ばなければ注入されません。

3つ目は保存時のトークン消費です。claude-memはAI圧縮によって高品質な要約を生成しますが、そのためにAPIトークンを消費します。セッションごとの消費量は小さくても、長期的には積み重なります。

noprogllamaさんがsui-memoryで提唱した「常時参照」という設計は、2つ目の課題に対する回答でした。UserPromptSubmit hookを使えば、プロンプトを送信するたびに自動的に関連記憶が注入されます。モデルの判断を介在させない分、確実に過去の文脈が利用されます。

## 設計原則

Kizamiの設計原則は、noprogllamaさんがsui-memoryで提唱された6原則をそのまま継承し、DB肥大化対策を加えた7つです。

| # | 原則 | 説明 |
| --- | --- | --- |
| 1 | 外部依存の排除 | SQLite単一ファイルに全データを格納します。外部APIや大規模モデルのダウンロードは不要です |
| 2 | 保存時トークン消費ゼロ | LLMを使わずにチャンク化します。ルールベースの処理のみで動作します |
| 3 | 自動保存 | SessionEnd hookにより手動操作なしで保存が行われます |
| 4 | 常時参照 | UserPromptSubmit hookにより毎メッセージ送信時に自動的に関連記憶を注入します |
| 5 | 編集と削除 | CLIから履歴の検索、編集、削除ができます |
| 6 | 最小依存 | coreモードのランタイム依存はbetter-sqlite3のみです |
| 7 | DB肥大化対策 | セッション保存時に自動メンテナンスが実行されます。古いチャンクの削除とDBサイズ制限を24時間ごとにチェックします |

7番目の原則は、claude-memのChromaDB肥大化問題を経験したことから追加しました。

## アーキテクチャ

Kizamiは2つのClaude Code hookで動作します。

セッション終了時にトランスクリプトのJSONLファイルを読み込み、ターン単位でチャンク分割してSQLiteに保存します。プロンプト送信時にはFTS5 trigram検索を実行し、BM25スコアと時間減衰を適用したうえでリランカーが関連度を再スコアリングし、上位3件をClaude Codeのコンテキストに注入します。

## インストールとセットアップ

Node.js 20以上とpnpmが必要です。

```
git clone https://github.com/okamyuji/kizami.git
cd kizami
pnpm install
pnpm build
npm link
```

ビルドスクリプトが`dist/cli.js`に実行権限を自動付与します。miseやnvm等のバージョン管理ツールを使っている場合は、リンク後に`mise reshim`等でshimを更新してください。

セットアップコマンドを実行すると、データベースの初期化とClaude Codeのhook設定が自動で行われます。

次のClaude Codeセッションから自動記録が始まります。設定される内容は以下の3つです。

* データベースが`~/.local/share/kizami/memory.db`に作成されます
* 設定ファイルが`~/.config/kizami/config.json`に作成されます
* Claude Codeの`~/.claude/settings.json`にSessionEnd hookとUserPromptSubmit hookが追加されます

## 検索モード

Kizamiには2つの検索モードがあります。

| モード | 検索方式 | 追加依存 | モデルダウンロード |
| --- | --- | --- | --- |
| core(デフォルト) | FTS5 trigram + BM25 + 時間減衰 + リランカー | なし | 不要 |
| hybrid(オプション) | FTS5 + Ruri v3ベクトル検索 + RRF | sqlite-vec, @huggingface/transformers | 約37MB (int8) |

coreモードはFTS5のtrigramトークナイザを使った全文検索です。trigramは3文字単位でトークン化するため、日本語のような分かち書きのない言語でも外部辞書なしに機能します。検索結果にはBM25スコア、時間減衰（半減期30日）、キーワードベースのリランカーが順に適用されます。

hybridモードではcoreの検索に加えて、Ruri v3-30mによるベクトル類似検索の結果をRRF（Reciprocal Rank Fusion）で統合します。Ruri v3はcl-nagoyaが開発した日本語特化のembeddingモデルで、ONNX変換されたint8量子化版（約37MB）を使用しています。sui-memoryが使用するRuri v3-310m（約600MB）と比べて大幅に軽量です。

hybridモードを有効にするには、追加パッケージをインストールしてからセットアップを実行します。

```
pnpm add sqlite-vec @huggingface/transformers
pnpm build
npm link
kizami setup --hybrid
```

## 日本語検索の課題とCJK N-gram対応

開発中に発見した問題として、FTS5のキーワード抽出が日本語テキストに対して正しく動作しないケースがありました。

たとえば「過去の会話履歴をclaude-memを使わずにkizamiで検索しているかどうかを動作確認してください」というプロンプトに対して、キーワード抽出関数はスペースや句読点で分割を試みます。しかし日本語にはスペースがないため、文全体が1つのトークンとして扱われ、その長い文字列でFTS5 MATCH検索を行うとヒット0件になるという問題が起きていました。

対策として、日本語助詞（は、が、を、に、で等）をゼロ幅分割点として追加し、CJKを含む長いトークンをN-gram（3文字単位）に展開してFTS5 trigramに適合させる処理を実装しました。リランカー側には元々CJK N-gram対応が入っていたのですが、FTS検索の段階で0件になるとリランカーに到達しないため、検索の入り口にも同じ対応が必要でした。

## 自動メンテナンスによるDB肥大化防止

claude-memのChromaDB肥大化を経験したことから、Kizamiには初めから自動メンテナンス機能を組み込んでいます。

セッション保存時に以下の処理が実行されます。ただし前回の実行から24時間以上経過している場合のみ動作するため、通常のsaveのレイテンシには影響しません。

1. 90日を超えた古いチャンクを削除します
2. DBサイズが100MBを超えている場合は、古い順に10%ずつ削除してサイズを下げます
3. チャンクがなくなったセッションを削除します
4. WALチェックポイントを実行してディスク領域を回収します

これらの閾値はすべて設定ファイルで変更できます。

```
{
  "maintenance": {
    "enabled": true,
    "intervalHours": 24,
    "maxChunkAgeDays": 90,
    "maxDbSizeMB": 100
  }
}
```

## Token節約効果

Kizamiは全履歴をコンテキストに入れるのではなく、関連度の高いチャンクだけを注入するため、大幅なToken節約になります。以下は80セッション、5,400チャンクが蓄積された実環境での計測結果です。

| 指標 | 値 |
| --- | --- |
| DB内の総トークン数 | 1,676,514 |
| recall 1回あたりの注入量 | 最大375トークン (3件 x 125トークン) |
| Token節約率 | 99.98% |

1セッションで50回プロンプトを送信した場合、全履歴を毎回注入すると約8,380万トークンを消費しますが、Kizamiでは18,750トークンで済みます。そもそも167万トークンの履歴はコンテキストウィンドウに収まらないため全注入は現実的ではありませんが、Kizamiは関連度スコアによるフィルタリングで必要な記憶だけを375トークン以内に収めて注入します。

## 類似ツールとの比較

| 領域 | sui-memory | claude-mem | Kizami |
| --- | --- | --- | --- |
| 言語 | Python | Bun/Python/JS | TypeScript |
| ランタイム依存 | sentence-transformers, sqlite-vec | Chroma, Claude Agent SDK等 | better-sqlite3のみ(coreモード) |
| モデルダウンロード | Ruri v3-310m (約600MB) | 内部embedding | coreでは不要。hybridではRuri v3-30m (約37MB) |
| チャンク分割 | Q&A形式ルールベース | AI圧縮(APIトークン消費あり) | ルールベース(トークン消費ゼロ) |
| 検索 | RRF (FTS5 + ベクトル) | FTS5 + Chroma + 3層段階開示 | FTS5 + BM25 + 時間減衰 + リランカー(+ RRF hybrid) |
| 記憶注入 | 明示的検索のみ | MCP Server経由で明示的検索 | UserPromptSubmit hookで自動注入 |
| Web UI | なし | localhost:37777で可視化 | なし |
| DB肥大化対策 | なし | AI圧縮による暗黙的な削減 | 自動メンテナンス |

※この比較表は筆者が各ツールを使用した時点（2025年末〜2026年初頭）の情報に基づいています。特にclaude-memはv10系で活発にアーキテクチャが刷新されているため、最新版では状況が異なる場合があります。

claude-memにはWeb UIによるメモリストリームの可視化、`<private>`タグによる機密データの除外、observationの自動分類（bugfix, feature, discovery等）、v9.0.0で導入されたLive Context Systemによるフォルダレベルの活動コンテキスト自動生成など、Kizamiにはない豊富な機能があります。一方でKizamiは、hookベースの常時自動注入、保存時のトークン消費ゼロ、日本語特化embeddingによるhybrid検索、自動メンテナンスによるDB肥大化防止など、claude-memとは異なる方向の強みを持っています。

用途に応じた使い分けが可能です。claude-memからのデータインポート機能も用意しています。

## CLIコマンド

Kizamiは以下のCLIコマンドを提供しています。

```
# メモリの検索
kizami search "React Hook Form"

# セッション一覧の表示
kizami list
kizami list --all-projects

# 統計情報の表示
kizami stats

# チャンクの編集
kizami edit 42 --content "修正した内容"

# データの削除
kizami delete --session abc123
kizami delete --before 2024-01-01
kizami delete --chunk 42

# 古いメモリの一括削除
kizami prune --older-than 90d

# エクスポート
kizami export --format json > backup.json
kizami export --format markdown > backup.md

# 類似チャンクのマージ
kizami merge --dry-run --all-projects
kizami merge --threshold 0.7 --all-projects
```

## おわりに

Kizamiはnoprogllamaさんのsui-memoryの設計思想をTypeScriptで再実装し、coreモードでのゼロ依存動作、Ruri v3によるhybrid検索、自動メンテナンスを加えたツールです。

「常時参照」の仕組みにより、過去のセッションで議論した内容を意識しなくてもClaude Codeが自動的に思い出してくれます。DB肥大化対策を最初から組み込むことで、claude-memで経験したディスク圧迫の問題を回避しています。

改善の余地はまだ多くあります。MCP Server化、Web UIの実装、検索精度のさらなる向上など、まだまだ検討すべき課題があります。

最後に、改めてnoprogllamaさんに感謝を述べたいと思います。「[Claude Codeに長期記憶を持たせたら、壁打ちの質が変わった](https://zenn.dev/noprogllama/articles/7c24b2c2410213)」の記事がなければ、Kizamiは生まれていませんでした。設計原則を体系的に言語化し、実装とともにオープンに公開してくださったおかげで、同じ課題に取り組む開発者が自分なりのアプローチで発展させることができています。また、Engram（現Kizami）公開について快く許諾いただいたことにも深く感謝しています。こうした設計思想の共有と派生実装の歓迎が、コミュニティ全体の知見を高めていくのだと実感しています。

ソースコードは[GitHub](https://github.com/okamyuji/kizami)で公開しています。
