---
id: "2026-03-17-claude-codeの検索機能を分解してaiエージェントが利用する自作検索ツールのアーキテクチャを-01"
title: "Claude Codeの検索機能を分解して、AIエージェントが利用する自作検索ツールのアーキテクチャを考える"
url: "https://zenn.dev/toku7/articles/53753f3f001e9c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

Claude Code のようなAIエージェントは、当たり前のようにWeb検索をする。「この技術の最新動向を教えて」と聞けば勝手に検索して、ソース付きで答えてくれる。

便利に使っているが、気になる点もある。検索のたびにトークンを消費するし、特定の用途では深掘りの仕方が物足りないこともある。**自分のAIエージェントに検索機能を組み込んで、もっとカスタマイズしたい。** そう考えたとき、先行事例として実際のプロダクトがどう作られているかを知っておきたくなった。

そこで、Claude Code のWeb検索機能を「ユーザーの質問から回答が返るまで」のフロー全体を通して分解してみた。その上で、自分で検索機能を作る場合の実装パターンを整理する。

なお、この記事で扱うのは公開情報から分かることだけだ。非公開のままの部分は「ここから先は分からない」と明示する。

## AIエージェントはどうやって「検索しよう」と決めるのか

### ツール呼び出しの仕組み（前提知識）

AIエージェントの検索機能を理解するには、まず「ツール呼び出し（tool use）」の仕組みを知っておく必要がある。

AIエージェントは、LLM（大規模言語モデル）に対して「こういうツールが使えるよ」という定義を渡す。ツール定義はJSON Schemaのような構造化されたフォーマットで記述される。LLMはユーザーの質問を見て、「この質問に答えるには検索が必要だ」と自律的に判断し、構造化されたツール呼び出し（tool call）を生成する。エージェント側がそのツールを実行し、結果をLLMのコンテキストに戻す。LLMはその結果を踏まえて回答を生成する。

公開情報を見る限り、**検索専用の別のLLMがいるわけではない**。そのとき動いているLLM自身が「検索するかどうか」を判断し、検索クエリも生成しているように見える（内部で補助的な rewrite 等が全くないかは公開情報だけでは断定できないが、少なくとも公開 API 上はそう設計されている）。

### Claude Code ではどうなっているか

Claude Code が内部で使っている Anthropic API では、リクエストの `tools` 配列に以下のような server tool を登録する。

```
{
  "type": "web_search_20250305",
  "name": "web_search",
  "max_uses": 5
}
```

Claude がユーザーの質問を見て「検索が必要だ」と判断すると、`server_tool_use` というイベントが生成される。その中身はシンプルだ。

```
{
  "type": "server_tool_use",
  "name": "web_search",
  "input": { "query": "claude shannon birth date" }
}
```

つまり、Claude 自身が質問の意図を汲み取り、適切な検索クエリを1つの文字列として生成している。

さらに Claude Code には **hook** という仕組みがある。`PreToolUse` フックは「Claudeがツールのパラメータを作成した後」に実行され、検索クエリを検査・承認・差し替えできる。たとえば、会話コンテキストに含まれるセンシティブな情報が検索クエリに混入していないかをチェックする、といった使い方ができる。

## Claude Codeの検索を分解する

### 全体アーキテクチャ

Claude Code の検索機能には2つのレイヤーがある。

**CLI層（Claude Code 側）:**  
Claude Code の内部実装を公開した Claude Agent SDK（`@anthropic-ai/claude-agent-sdk`）では、`WebSearchInput` という型が定義されている。

```
interface WebSearchInput {
  query: string;
  allowed_domains?: string[];
  blocked_domains?: string[];
}
```

**API層（Anthropic 側）:**  
Anthropic API の server tool は `web_search_20250305`（基本版）と `web_search_20260209`（dynamic filtering 対応版）の2バージョンがある。API層の設定項目には `max_uses`（1リクエスト内での検索回数上限）や `user_location`（位置情報）がある。

この2つは別レイヤーだと考えられる。Agent SDK の `WebSearchInput` には `query` と `domain filters` があり、API層の server tool には `max_uses` と `user_location` がある。この非対称性から、CLI が `WebSearch(query)` というツールを持ち、その裏で Anthropic の server tool に橋渡ししている構造が推測できる（ただし、この bridging 実装自体は公式ドキュメントで直接説明されていない）。

### 検索プロバイダ

Claude Code のWeb検索は、裏側で **Brave Search** を使っている可能性が非常に高い。

根拠はいくつかある。

* **Anthropic Trust Center** に Brave Search がサブプロセッサー（データ処理委託先）として掲載されている（Simon Willison と TechCrunch の報道によれば 2025年3月19日追加）
* **Profound の分析** で、Claude の検索結果と Brave Search の結果の一致率が86.7%（15件中13件一致）だったと報告されている。Simon Willison も別途、1クエリで10件の検索結果が完全一致したと観測している
* Claude の内部パラメータに **`BraveSearchParams`** という名前が存在する（Simon Willison による観測）
* **TechCrunch** が同件を報道している

ただし、Anthropic の公式 Web Search ドキュメントは下位プロバイダ名を明記していない。あくまで公開情報から「Brave Search と強く判断できる」という位置付けだ。

### 処理フロー — 二重構造を理解する

Claude Code が情報をインターネットから集めるとき、「複数回検索する」が**2つのレベル**で起きている。ここが全体像を理解する鍵だ。

#### レベル1: 1回のツール呼び出しの中での繰り返し（バックエンド内部）

Claude Code が WebSearch を1回呼ぶと、その裏で Anthropic のバックエンドが自律的に複数回の検索・取得を行う。

**処理の流れ:**

1. Claude がプロンプトを見て検索の必要性を判断
2. `server_tool_use` で検索クエリを生成（クエリ生成は Claude 自身が行う）
3. Anthropic バックエンドが検索を実行（公開情報から Brave Search が使われていると強く推測される）
4. 検索結果のページから full HTML を取得（fetch）
5. 「まだ情報が足りない」とバックエンドが判断 → 追加で検索・fetch を繰り返す
6. この繰り返しの仕組みが **server-side sampling loop**（ループの上限は10イテレーション）
7. 最終的に検索結果がまとめられ、Claude に返される

なお、`max_uses` は sampling loop のイテレーション上限とは別の概念で、1リクエスト内で Web Search ツールが呼ばれる回数の上限を指定するパラメータだ。

ポイントは、1回の Web Search ツール呼び出し = 返ってくる結果件数に関係なく **1 use** としてカウントされることだ。つまりバックエンド内部で複数回の検索が走っても、エージェントから見れば「1回の検索」に見える。

**検索結果のフォーマット:**

検索結果は `web_search_tool_result` として返り、各結果は `url`、`title`、`page_age`、`encrypted_content` を持つ。最終回答には `web_search_result_location` 形式の citation（引用元情報）が付与される。なお、citation の `cited_text`、`url`、`title` はトークン使用量にカウントされない。

#### Dynamic Filtering（web\_search\_20260209）

新しいバージョン `web_search_20260209` では、**dynamic filtering** という後処理が加わる。

通常の basic web search では、取得した full HTML をそのまま LLM のコンテキストに投入して推論する。一方、dynamic filtering では Claude がフィルタリング用のコードを生成し、Anthropic のサンドボックス環境（secure sandboxed container）で実行する。これにより、full HTML から関連部分だけを残し、不要部分を落とす。

Anthropic が公表している効果:

* **トークン24%削減**
* **精度11%向上**（BrowseComp / DeepsearchQA ベンチマーク）

この機能は内部で code execution を利用するため、`web_search_20260209` は ZDR（Zero Data Retention）非対応となっている。なお、Sonnet 4.6 / Opus 4.6 では dynamic filtering がデフォルトで有効になっている。

なお、生成されるコードの具体的な中身（使用ライブラリ、抽出アルゴリズム等）は、主要な公開ドキュメントでは確認できなかった。公開情報で言えるのは「Anthropic のサンドボックス上で生成コードが後処理を行う」というところまでだ。

#### レベル2: Claude Code のLLMが複数のツールを組み合わせる（会話レベル）

レベル1は1回のツール呼び出しの内部の話だ。それとは別に、Claude Code のLLM自身が会話の流れの中で **WebSearch** や **WebFetch** を何度も呼び分ける。

典型的なフロー:

1. Claude が「この質問に答えるには検索が必要」と判断 → **WebSearch** を呼ぶ（例: 「Brave Search API 仕様」で検索）
2. 検索結果を見て「この URL のドキュメントを詳しく読みたい」→ **WebFetch** を呼ぶ → ページ本文を取得
3. 「別の角度からも調べたい」→ **WebSearch** をもう1回呼ぶ（別のクエリで）
4. 全ての情報をまとめて回答を生成

**WebSearch と WebFetch の使い分け:**

| ツール | 役割 | 入力 |
| --- | --- | --- |
| WebSearch | 発見 + 横断比較。内部で複数サイトの HTML fetch も含む | `query`（検索クエリ） |
| WebFetch | 特定URLを明示的に深く読む | `url` + `prompt` |

WebFetch で取得できる URL は「ユーザーが明示した URL」または「前の WebSearch / WebFetch の結果に出てきた URL」に限定されている。

つまり、**レベル1（バックエンド内部の繰り返し）× レベル2（LLMによるツール組み合わせ）の二重構造** で、Claude Code は情報を集めている。

### LLMが担う役割 vs コードが担う役割

Claude Code の検索フローでは、LLMとコード（確定的処理）が役割を分担している。

**LLM（Claude）が担うこと:**

* 検索するかどうかの判断
* 検索クエリの生成
* 検索結果の解釈
* WebSearch / WebFetch の使い分け判断
* dynamic filtering のコード生成
* 最終回答の生成

**コード（確定的処理）が担うこと:**

* permission / hook の実行
* sampling loop の制御（上限回数の管理）
* domain validation（allowed / blocked domains の適用）
* max\_uses 制限の適用

### 公開情報の境界線

最後に、何が見えていて何が見えていないかを整理しておく。

**公開されている（control plane）:**

* ツール定義（WebSearchInput、WebFetchInput）
* 設定パラメータ（max\_uses、domain filters、user\_location）
* 呼び出しフロー（server\_tool\_use → web\_search\_tool\_result → citation）
* hook 層の仕組み
* dynamic filtering の仕組みと効果

**非公開（retrieval / extraction core）:**

* ranking アルゴリズム（検索結果の順位付け）
* HTML 抽出手法（boilerplate 除去の具体的方法）
* 取得件数（上位何件のページを fetch するか）
* JavaScript レンダリングの有無
* tool schema がモデル内部でどう hidden prompt に変換されるか
* server 側での query rewrite の有無

自分で検索機能を作る場合、**この非公開部分こそ自前で実装が必要な箇所** ということになる。

## 自分で検索機能を作るときの選択肢

ここからは、AIエージェントに検索機能を組み込む場合の実装パターンを整理する。

### 本質的な違いは「API側にLLMがいるかどうか」

AIエージェント向けの検索機能を選ぶとき、最も重要な判断軸は **呼び出す検索API/ツールの内部にLLMが介在しているかどうか** だ。

### パターン1: 純粋検索API型（API内部にLLMなし）

検索APIを叩いて生の検索結果を返すだけのツール。API側にLLMは介在しない。

**代表例:** Brave Search API、Google Custom Search JSON API

**返ってくるもの:** 典型的にはタイトル、URL、スニペット（短い抜粋）程度。ページ本文は返ってこないことが多い。

エージェントのLLMがクエリ生成・結果の解釈・回答生成を全て担当する。

* **メリット:** シンプル、制御しやすい、デバッグしやすい、監査性が高い
* **デメリット:** スニペットだけでは情報量が不十分なことが多い

**実態として、スニペットだけで完結するプロダクトはほぼない。** 多くの成熟したプロダクトは「検索 + 本文取得」の2段階構成を採用している。

* **Claude Code:** WebSearch（内部で multi-site fetch を含む discovery）→ 必要に応じて WebFetch（特定URLの深掘り）
* **Open WebUI（Agentic Mode）:** search\_web（snippets取得）→ 必要に応じて fetch\_url（ページ全文取得）。RAG-free で動く構成
* **LangChain:** TavilySearchResults（検索）+ TavilyExtract（本文取得）を別ツールとして提供

### パターン2: 自作AI検索ツール型（純粋検索API + ツール内LLMオーケストレーション）

純粋検索APIを部品として使いつつ、ツール内部にエージェントのメインLLMとは別のLLMを置き、そのLLMが検索プロセスを自律的にオーケストレーションするパターン。パターン3（AI検索API型）を自分で組み立てるイメージだ。

**処理フローの例:**

1. ツールがユーザーの質問を受け取る
2. ツール内LLMが検索クエリを生成 → 純粋検索API（Brave等）を叩く
3. 結果を見て「情報が足りない」と判断 → 追加クエリを生成 → 再検索
4. 必要なURLをfetch → HTMLからテキスト抽出 → ツール内LLMで要約・フィルタリング
5. 最終的に縮約済みの結果をエージェントに返す

**実例:**

* **Claude Code の dynamic filtering:** Claude がフィルタリング用コードを生成 → サンドボックスで実行して HTML を後処理
* **Perplexity Pro Search の内部構造:** multi-step で search → fetch\_url\_content を繰り返す
* **自作する場合:** 軽量LLM（Haiku等）をツール内オーケストレーターに使い、検索・fetch・要約を自動化

**メリット:**

* 検索方針・後処理ロジックを完全にコントロールできる
* 使う検索APIやLLMを自由に選べる（ベンダーロックインなし）
* エージェントのメインLLMに渡すトークンを大幅に削減できる（縮約済みで返すため）

**デメリット:**

* 実装が最も複雑（検索ロジック + fetch + 後処理 + LLM呼び出しを全て自前構築）
* LLMコストが2重（メインLLM + ツール内LLM）
* レイテンシが大きくなりやすい（multi-step処理）

### パターン3: AI検索API型（API内部にLLMあり、独立型）

API自体が内部でLLMを使って検索結果を処理し、整理された情報や回答を返す。特定のLLMプロバイダに縛られず、どのエージェントからでも呼べる独立型だ。

**Tavily:**

* AI エージェント向けの検索 API
* `include_raw_content=true` でクリーニング済みページ全文を返せる（Markdown または plain text を選択可能）— API側がHTML取得 + 前処理まで担当
* `include_answer=true` で LLM生成の回答も同梱可能（純粋検索〜回答付きまで切り替え可能）
* 制御点が豊富: `max_results`（最大20）、`search_depth`、`include_domains` / `exclude_domains`、`chunks_per_source`
* 料金: credit制、$0.008/credit
* LangChain、LlamaIndex 等の主要フレームワーク向けの integration がある

**Perplexity Sonar:**

* 検索と回答が一体で返る answer-first API
* `citations`（URL配列）+ `search_results`（title, url, snippet等）をトップレベルで返す
* 制御点: `search_mode`（web / academic / sec）、domain filter、date filter、language filter、`search_context_size`（low / medium / high）
* `enable_search_classifier` で検索要否のAI判断も可能
* OpenAI Chat Completions 互換（`base_url` 差し替えだけで使える）
* Pro Search: multi-step reasoning + `fetch_url_content` を含む上位モード
* 料金: Sonar $1/$1M in/out + request fee $5〜$12/1K、Sonar Pro $3/$1M in・$15/$1M out + $6〜$14/1K

**You.com Research API:**

* research workflow を丸ごとAPI化。"multiple searches, reads through the sources, synthesizes citation-backed answer"
* `research_effort`: lite / standard / deep / exhaustive（深いほど時間もコストもかかる）
* Markdown回答 + inline citations + sources配列
* 料金: lite $6.50〜exhaustive $300/1K calls

**このパターンの特徴:**

* **メリット:** 検索 + 本文取得 + 後処理をAPI側が担当するため、エージェント側の実装がシンプル。トークン効率も良い
* **デメリット:** API側の検索方針・後処理ロジックはブラックボックス。APIコストが別途かかる
* **適した場面:** エージェントから検索を「葉ノードの専門家ツール」として外注したいとき

### パターン4: プロバイダ組み込み型（LLM APIに検索が統合）

LLMプロバイダのAPI自体に検索機能が組み込まれている。`tools` 配列に type を指定するだけで、そのLLMが検索付きで動く。業界の標準パターンになりつつある。Claude Code はこのパターンだ。

**対応プロバイダ:**

| プロバイダ | ツール定義 | 特徴 |
| --- | --- | --- |
| Anthropic (Claude) | `{"type": "web_search_20250305"}` / `web_search_20260209` | server tool として実行。本記事で詳しく解剖した方式 |
| OpenAI | `{"type": "web_search"}` | Responses API built-in。Codex CLI では cached / live / disabled の実行モードあり |
| Gemini (Google) | `{ google_search: {} }` | groundingMetadata で回答セグメントと根拠の対応を返す。retrieved context は input token 課金なし |
| Mistral | `{"type": "web_search"}` | Agents API 限定。premium版もあり |
| xAI (Grok) | `{"type": "web_search"}` + `{"type": "x_search"}` | X/Twitter検索も可能 |

**このパターンの特徴:**

* **メリット:** 導入が最も簡単。ツール定義を渡すだけで、citation・複数回検索・後処理までプロバイダが面倒を見る
* **デメリット:** 中身がブラックボックス、ベンダーロックイン。検索方針のカスタマイズは限定的
* **パターン3との違い:** パターン3は独立したAPIなのでどのLLMからでも呼べるが、パターン4はそのプロバイダのLLMでしか使えない

### パターン比較表

| 観点 | 1. 純粋検索API型 | 2. 自作AI検索ツール型 | 3. AI検索API型 | 4. プロバイダ組み込み型 |
| --- | --- | --- | --- | --- |
| API内部のLLM | なし | 自分で用意 | あり | あり |
| プロバイダ依存 | なし | なし | なし | あり |
| 制御性 | 高 | 最高 | 中〜高 | 低 |
| 導入コスト | 中（fetch併用が必要） | 高（全て自前構築） | 低 | 低 |
| 後処理品質 | エージェントLLM次第 | 自分次第（最適化可能） | 高（retrieval+処理が密結合） | プロバイダ次第 |
| トークン効率 | 低（生結果を全投入） | 高（縮約して返す） | 高（処理済み結果を返す） | プロバイダ次第 |
| 透明性 | 高 | 高 | 中 | 低 |
| 適した場面 | 検索方針を完全に握りたい | 後処理を自前で最適化したい | 検索を葉ツールとして外注したい | とにかく手軽に使いたい |

### Claude Code から学べること

この記事で Claude Code の内部を調べて見えてきたのは、以下のポイントだ。

* **クエリ生成はLLMに任せるのが主流。** 別の query builder は不要で、LLM自身が適切な検索クエリを生成する
* **検索結果の後処理が品質を分ける。** dynamic filtering のように内部でLLMがコードを生成して後処理を行うアプローチは効果が大きい（トークン24%削減、精度11%向上）
* **Claude Code の内部は単純なパターン4だけではない。** 表向きはプロバイダ組み込み型（パターン4）だが、公開情報からは裏側で検索プロバイダ（Brave Search と推測）、fetch、code-execution-based filtering を組み合わせているように見える
* **自作するなら:** まず Tavily 等のAI検索API（パターン3）をツールとして使い、制御性や品質が足りなければ自作AI検索ツール（パターン2）に進化させるのが現実的

## まとめ

Claude Code のWeb検索は、**バックエンド内部の繰り返し（レベル1）× LLMによるツール組み合わせ（レベル2）の二重構造**で動いている。

公開情報で見えるのは control plane（ツール定義、設定、呼び出しフロー）だ。retrieval / extraction core（ranking、HTML処理のアルゴリズム）は非公開のままで、自分で検索機能を作るなら、この非公開部分こそ自前で設計・実装が必要になる。

実装パターンは4つ。判断軸は「API側にLLMがいるか」「プロバイダに縛られるか」「後処理を自前で最適化したいか」だ。

### 筆者の考え → 実際に作るなら大体パターン2に行き着くのでは

実際に検索ツールを自作する必要性が出てくるのは、コストの問題だったり、特定サイトの深掘りやその他特定データの重点的な検索など、通常のWeb検索では対応できないケースだったりするはずだ。

そういった場面では、既成のAI検索API（パターン3・4）では要件を満たせず、結局 **パターン2（自作AI検索ツール型）に行き着く** ことになるのではないかと思う。

そのとき参考になるのが、Claude Code の「レベル2」の動き方だ。WebSearch と WebFetch を自在に組み合わせて、検索 → 発見 → 深掘り → 別角度で再検索、と情報を集めていくあのフロー。

つまり、**LLMにツールとして検索APIとfetch機能を渡し、LLM自身に検索戦略を組み立てさせるアプローチ**が、自分で検索機能を作る際の有力なヒントになると考えている。

---
