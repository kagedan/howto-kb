---
id: "2026-05-17-openai-vs-anthropicai競争の主戦場はモデル性能からハーネスへ移った-01"
title: "OpenAI vs Anthropic：AI競争の主戦場は「モデル性能」から「ハーネス」へ移った"
url: "https://zenn.dev/itdo/articles/e8695a0a51706c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "LLM"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

## 要旨

OpenAI と Anthropic の競争は、単純な「どちらのモデルが賢いか」という比較から、「どちらが実務で成果物を出せるか」という比較へ移っている。

初期の LLM 競争では、モデル単体の性能が主な評価軸だった。推論能力、コーディング能力、数学、長文コンテキスト、ハルシネーション率、API コストなどである。

しかし、現在の実務利用ではそれだけでは足りない。企業や開発者が求めているのは、チャット上で賢い返答をするモデルではなく、コードを読み、ファイルを編集し、コマンドを実行し、外部ツールと連携し、長時間のタスクを完了するシステムである。

このモデル周辺の実行環境を、本稿では「ハーネス」と呼ぶ。

Anthropic は Claude Code と MCP によって、このハーネス領域で先行した。一方、OpenAI は Codex、Responses API、Agents SDK、ChatGPT agent などを通じて急速に追撃している。

結論から言えば、総合プラットフォームとしては OpenAI が優勢である。ただし、Anthropic は単なるマーケティング勝ちではない。特に coding / enterprise workflow では実需があり、OpenAI に簡単に飲み込まれる立場でもない。

---

# 1. LLM 競争の評価軸が変わった

LLM の初期競争では、モデル性能がそのまま競争力だった。

たとえば、以下のような指標が重視されていた。

* ベンチマークスコア
* 推論能力
* コーディング能力
* 数学・科学タスク
* 長文コンテキスト
* ハルシネーション率
* API 単価
* レイテンシ

この段階では、「GPT が強いか」「Claude が強いか」「Gemini が強いか」というモデル単体の比較に意味があった。

しかし、実務導入が進むと問題は変わる。

企業や開発者が AI に期待するのは、単なる回答ではない。実際には以下のような処理が必要になる。

* リポジトリ全体を読む
* ファイルを編集する
* テストを実行する
* CI/CD と連携する
* GitHub issue や pull request を扱う
* Slack、Jira、Google Drive、社内 DB と接続する
* ブラウザを操作する
* コード実行環境を使う
* 権限管理や監査ログを維持する
* 長時間タスクを途中で止めずに完了する
* 組織固有のルールを守る

つまり、現在の AI 利用では「モデルの知能」だけでなく、「モデルが仕事を実行できる環境」が重要になる。

この実行環境がハーネスである。

---

# 2. ハーネスとは何か

ハーネスとは、モデルを実務に接続するための周辺システムである。

具体的には、以下のような要素を含む。

* CLI
* IDE 連携
* ファイル編集
* コマンド実行
* コード実行環境
* サンドボックス
* Git / GitHub 連携
* MCP などの外部ツール接続
* ブラウザ操作
* 権限管理
* ログ管理
* 長時間タスク管理
* メモリ、ルール、プロジェクト固有指示
* チーム単位の運用設計

重要なのは、ハーネスが単なる UI ではないという点である。

チャット UI が改善されても、それだけでは業務は完了しない。モデルが実際にファイルを編集し、テストを実行し、エラーを見て修正し、PR を作成できるようになって初めて、業務プロセスの一部になる。

モデル性能が多少劣っていても、ハーネスが優れていれば実務上の成果は高くなる。逆に、モデルが高性能でも、ハーネスが弱ければ人間の手戻りが増える。

この構造変化を早く捉えたのが Anthropic だった。

---

# 3. Anthropic は Claude Code でハーネス競争を先行した

Anthropic の強さは、Claude というモデル単体だけではない。むしろ Claude Code を中心とする開発者向けハーネスにある。

Claude Code は、コードベースを読み取り、ファイルを編集し、コマンドを実行し、開発ツールと統合する agentic coding tool として提供されている。ターミナル、IDE、デスクトップアプリ、ブラウザで利用でき、コードベース全体を理解して複数ファイルとツールをまたいで作業できる。([Claude API Docs](https://docs.anthropic.com/ja/docs/claude-code/overview "Claude Code の概要 - Claude Code Docs"))

これは、従来型の「コードを書いてくれるチャット」とは違う。

開発者のワークフローに直接入り込み、実際のリポジトリ上で作業する。Claude Code は git と連携してコミットや pull request を作成でき、GitHub Actions や GitLab CI/CD と連携したコードレビューや issue triage も想定されている。([Claude API Docs](https://docs.anthropic.com/ja/docs/claude-code/overview "Claude Code の概要 - Claude Code Docs"))

さらに重要なのが、CLAUDE.md、スキル、フック、MCP などの仕組みである。CLAUDE.md によってプロジェクト固有のコーディング標準、アーキテクチャ判断、レビュー観点を与えられる。スキルによって反復可能なワークフローをパッケージ化できる。フックによって、ファイル編集後のフォーマットやコミット前の lint なども組み込める。([Claude API Docs](https://docs.anthropic.com/ja/docs/claude-code/overview "Claude Code の概要 - Claude Code Docs"))

これはモデル性能そのものではなく、開発組織に AI を定着させるための運用設計である。

Claude Code が強い理由は、モデルが賢いからだけではない。開発者が日々使う環境に入り込む設計になっているからである。

---

# 4. MCP は Anthropic の重要な先行施策だった

Anthropic が先行したもう一つの重要領域が MCP、Model Context Protocol である。

MCP は、AI アプリケーションが外部データソースやツールに接続するためのオープン標準として Anthropic が発表した。Anthropic は、個別のデータソースごとに専用コネクタを維持するのではなく、標準プロトコルに基づいて接続する構想を示した。([Anthropic](https://www.anthropic.com/news/model-context-protocol "Introducing the Model Context Protocol \ Anthropic"))

AI エージェントが実務で使われるには、社内文書、チケット管理、監視システム、CRM、データベース、クラウドサービスなどに接続する必要がある。MCP はその接続レイヤーを標準化する試みである。

Claude Code も MCP を通じて外部ツールやデータソースに接続できる。Anthropic のドキュメントでは、Google Drive の設計文書を読んだり、Jira のチケットを更新したり、Slack からデータを取得したりする例が示されている。([Claude API Docs](https://docs.anthropic.com/ja/docs/claude-code/overview "Claude Code の概要 - Claude Code Docs"))

この戦略は妥当だった。

AI エージェント時代に価値を持つのは、閉じたチャットボットではない。社内外のシステムに接続し、適切な権限で操作し、業務プロセスを進められるエージェントである。

Anthropic は、この点で市場のニーズを早く捉えた。

---

# 5. ただし MCP は Anthropic だけの moat ではなくなりつつある

MCP は Anthropic にとって強力な先行施策だったが、同時に Anthropic 固有の囲い込みにはなりにくい。

Anthropic は 2025 年 12 月、MCP を Linux Foundation 傘下の Agentic AI Foundation に寄付した。AAIF は Anthropic、Block、OpenAI が共同設立し、Google、Microsoft、AWS、Cloudflare、Bloomberg なども支援している。([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation "Donating the Model Context Protocol and establishing the Agentic AI Foundation \ Anthropic"))

Anthropic の発表によれば、MCP は ChatGPT、Cursor、Gemini、Microsoft Copilot、Visual Studio Code などにも採用されている。また、10,000 以上の active public MCP servers が存在するとしている。([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation "Donating the Model Context Protocol and establishing the Agentic AI Foundation \ Anthropic"))

これはエコシステムとしては望ましい。しかし、競争戦略として見ると、Anthropic の独占的優位は薄まりやすい。

標準を作った企業が、必ずしも標準化後の最大受益者になるとは限らない。標準が普及すると、次に重要になるのは配布網、資本力、モデル性能、プロダクト統合力である。

この点で OpenAI は強い。

---

# 6. OpenAI はハーネス領域に急速に寄せている

OpenAI はもともと、汎用モデル性能の向上に強くフォーカスしていた。しかし、Anthropic が Claude Code や MCP で実務性能を高めたことで、OpenAI も明確にハーネス領域へ寄せている。

その代表が Codex である。

OpenAI は Codex を cloud-based software engineering agent として発表した。Codex は、機能実装、コードベースに関する質問応答、バグ修正、pull request 提案を行い、それぞれのタスクをリポジトリが読み込まれた独立したクラウドサンドボックス環境で実行する。([OpenAI](https://openai.com/index/introducing-codex/ "Introducing Codex | OpenAI"))

Codex はファイルを読み書きし、テスト、linter、type checker などのコマンドも実行できる。これは Claude Code と同じく、単なるチャット補助ではなく、開発実行環境としての AI である。([OpenAI](https://openai.com/index/introducing-codex/ "Introducing Codex | OpenAI"))

OpenAI は AGENTS.md も導入している。Codex は作業開始前に AGENTS.md を読み、グローバルな指示とプロジェクト固有の指示を階層的に適用できる。これは Claude Code の CLAUDE.md と同種の発想であり、リポジトリごとのルールや作業方針を AI エージェントに伝えるための仕組みである。([OpenAI 開発者](https://developers.openai.com/codex/guides/agents-md "Custom instructions with AGENTS.md – Codex | OpenAI Developers"))

さらに OpenAI は Agents SDK も拡張している。更新された Agents SDK は、ファイルの検査、コマンド実行、コード編集、長時間タスクを controlled sandbox environments 内で扱えるようにするものだと説明されている。OpenAI 自身もこれを「model-native harness」と位置づけている。([OpenAI](https://openai.com/index/the-next-evolution-of-the-agents-sdk/ "The next evolution of the Agents SDK | OpenAI"))

つまり、OpenAI は明確に Anthropic が先行したハーネス競争へ参入している。

---

# 7. Responses API と ChatGPT agent も同じ方向を向いている

OpenAI のハーネス強化は、Codex だけではない。

Responses API では、remote MCP servers、Code Interpreter、file search、background mode、encrypted reasoning items などが導入されている。OpenAI は Responses API を agentic applications を構築するための中核 API primitive と説明している。([OpenAI](https://openai.com/index/new-tools-and-features-in-the-responses-api/ "New tools and features in the Responses API | OpenAI"))

特に remote MCP servers のサポートは重要である。OpenAI は、Responses API が任意の MCP server 上のツールに数行のコードで接続できると説明している。つまり、Anthropic 起点の MCP 標準を OpenAI 側も自社プラットフォームに取り込んでいる。([OpenAI](https://openai.com/index/new-tools-and-features-in-the-responses-api/ "New tools and features in the Responses API | OpenAI"))

ChatGPT agent も同じ流れにある。OpenAI は ChatGPT agent について、ChatGPT が自分のコンピュータを使い、複雑なタスクを start-to-finish で処理できるものとして説明している。Web サイトの操作、コード実行、分析、編集可能なスライドやスプレッドシートの作成などが想定されている。([OpenAI](https://openai.com/index/introducing-chatgpt-agent/ "Introducing ChatGPT agent: bridging research and action | OpenAI"))

この方向性は明確である。

OpenAI は、モデル単体の高性能化だけではなく、モデルがファイル、Web、コード、社内データ、外部ツールを扱うための実行環境を整備している。

Anthropic がハーネスで先行したが、OpenAI はその差を急速に埋めている。

---

# 8. モデル性能では OpenAI が総合的に強い

ハーネス競争が重要になったとはいえ、モデル性能が不要になったわけではない。むしろ、ハーネスが同等になれば、再びモデル性能、推論コスト、レイテンシ、安定性が効いてくる。

OpenAI はモデル性能で依然として強い。

GPT-5.5 は、OpenAI が「最も強い agentic coding model」と位置づけているモデルであり、Terminal-Bench 2.0 で 82.7%、SWE-Bench Pro で 58.6% を記録している。Terminal-Bench 2.0 は、計画、反復、ツール連携を伴う複雑なコマンドラインワークフローを評価するベンチマークである。([OpenAI](https://openai.com/index/introducing-gpt-5-5/ "Introducing GPT-5.5 | OpenAI"))

これは、単なる静的なコード生成ではなく、実行、検証、修正を含む agentic coding 能力が評価対象になっていることを意味する。

OpenAI の強みは、モデル単体の上限性能にある。推論能力、ツール利用、長時間タスク、コンピュータ操作などを総合すると、OpenAI は依然として非常に強い。

ただし、「OpenAI が全領域で Anthropic に勝っている」と単純化するのは危険である。

Anthropic は coding workflow、長時間の開発タスク、慎重な回答、企業内実務への接続で強い領域を持つ。Claude Code の普及は、単なるベンチマークでは説明しきれない。

---

# 9. Anthropic の成功はマーケティングだけではない

Anthropic の成功を「マーケティングがうまかっただけ」と見るのは誤りである。

Claude Code は、2025 年 5 月に一般提供され、2026 年 2 月時点で run-rate revenue が 25 億ドルを超えたと Anthropic は発表している。また、Claude Code の weekly active users は 2026 年初から倍増したとしている。([Anthropic](https://www.anthropic.com/news/anthropic-raises-30-billion-series-g-funding-380-billion-post-money-valuation?utm_source=chatgpt.com "Anthropic raises $30 billion in Series G funding at $380 ..."))

Anthropic 全体でも、2026 年 4 月時点で run-rate revenue が 300 億ドルを超え、2025 年末の約 90 億ドルから大きく伸びたと発表している。また、年 100 万ドル以上を使う business customer は 500 社超から 1,000 社超へ、2 か月未満で倍増したとしている。([Anthropic](https://www.anthropic.com/news/google-broadcom-partnership-compute "Anthropic expands partnership with Google and Broadcom for multiple gigawatts of next-generation compute \ Anthropic"))

Menlo Ventures の 2025 年 enterprise AI 調査では、Anthropic が enterprise LLM spend の 40% を占め、OpenAI は 27%、Google は 21% と推定されている。([Menlo Ventures](https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/ "2025: The State of Generative AI in the Enterprise | Menlo Ventures"))

これらの数字を見る限り、Anthropic は実際に企業から大きな支出を獲得している。

ただし、run-rate revenue は慎重に扱うべき指標である。Reuters Breakingviews は、Anthropic の lifetime sales と run-rate revenue の差を取り上げ、run-rate は直近の利用を年換算した指標であり、実際の GAAP revenue とは異なると指摘している。([Reuters](https://www.reuters.com/commentary/breakingviews/anthropic-gives-lesson-ai-revenue-hallucination-2026-03-10/?utm_source=chatgpt.com "Anthropic gives lesson in AI revenue hallucination"))

したがって、Anthropic の成長は本物だが、数字の見え方には割り引きが必要である。

重要なのは、Anthropic が「話題性」だけで伸びているわけではないという点である。Claude Code が開発者ワークフローに入り込み、企業利用で支出を生んでいることは事実である。

---

# 10. OpenAI の本当の強みはモデルだけではない

OpenAI の優位性は、モデル性能だけでは説明できない。

むしろ、以下の要素が一体化している点が強い。

* ChatGPT の巨大な消費者配布網
* API プラットフォーム
* Codex
* ChatGPT Enterprise
* Agents SDK
* Responses API
* ChatGPT agent
* Microsoft などとの連携
* 資本調達力
* compute 調達力
* 開発者エコシステム

OpenAI は 2026 年 3 月、1,220 億ドルの committed capital を調達し、post-money valuation は 8,520 億ドルと発表している。([OpenAI](https://openai.com/index/accelerating-the-next-phase-ai/ "OpenAI raises $122 billion to accelerate the next phase of AI | OpenAI"))

この規模の資本力は、モデル開発だけでなく、データセンター、推論基盤、企業販売、開発者向けプラットフォーム、消費者向けアプリのすべてに効く。

AI 競争は、もはや研究所同士のモデル性能競争ではない。

実態は、以下の総力戦である。

* モデル研究
* 推論基盤
* compute procurement
* 開発者体験
* エージェント基盤
* 企業販売
* 消費者配布網
* 資本市場
* 標準化戦略

この総合戦では、OpenAI は非常に強い。

Anthropic は企業実務と開発者体験で鋭いポジションを取っているが、OpenAI は consumer、developer、enterprise、API、agent、coding を横断する配布網を持つ。

---

# 11. Anthropic が OpenAI に押し切られるシナリオ

Anthropic が OpenAI に押し切られるシナリオは明確である。

## 11.1 ハーネスの差が標準化で消える

Claude Code、MCP、CLAUDE.md 的な運用は、Anthropic の強みだった。

しかし、MCP は標準化し、OpenAI も Responses API や Agents SDK に取り込んでいる。AGENTS.md のようなプロジェクト指示ファイルも Codex に組み込まれている。

ハーネスのベストプラクティスが業界標準になるほど、Anthropic 固有の優位は薄まる。

## 11.2 OpenAI のモデル性能が継続的に上回る

ハーネスが同等になると、最終的にはモデル性能が再び重要になる。

同じツール、同じコンテキスト、同じサンドボックス、同じコスト帯で使えるなら、より高性能なモデルを選ぶのが合理的である。

OpenAI が agentic coding、computer use、reasoning、long-horizon task で優位を維持すれば、Anthropic は差別化しにくくなる。

## 11.3 Codex が Claude Code を十分に代替する

開発者は、最高性能だけではなく、業務に十分な性能、既存環境との統合、導入しやすさ、価格、組織契約のしやすさで選ぶ。

Codex が Claude Code と同等の体験を提供できるようになれば、ChatGPT、OpenAI API、Enterprise 契約と統合できる OpenAI の方が購買上有利になる可能性がある。

## 11.4 OpenAI の配布網が効く

OpenAI は ChatGPT という巨大な入口を持つ。

個人利用から企業利用へ、ChatGPT から Codex へ、API から Enterprise へ、という導線を作れる。この配布網は Anthropic より強い。

Anthropic がいかに良いプロダクトを持っていても、OpenAI の配布力と資本力に押し切られる可能性はある。

---

# 12. Anthropic が残るシナリオ

一方で、Anthropic が簡単に負けるわけでもない。

## 12.1 開発者ワークフローは粘着性が高い

Claude Code がチームの開発プロセスに深く入ると、乗り換えコストが発生する。

たとえば、以下のような資産が蓄積される。

* CLAUDE.md
* チーム固有のプロンプト
* MCP サーバー
* CI/CD 連携
* コードレビュー手順
* Slack 連携
* 社内ルール
* セキュリティポリシー
* 自動化スクリプト
* 失敗時の運用手順

これらが実務に組み込まれると、単純なモデル性能差だけでは乗り換えない。

## 12.2 Anthropic は enterprise workflow に強い

Anthropic は、開発者向けだけでなく、企業ワークフロー全体にも入り込もうとしている。

特に金融、法務、調査、セキュリティ、データ分析などでは、単に速い回答よりも、慎重さ、説明可能性、欠損データに対する扱い、権限管理、監査性が重視される。

Claude はこの文脈で評価されやすい。

## 12.3 企業は単一モデルに全振りしない

企業は通常、単一ベンダーにすべてを依存しない。

今後は、以下のような multi-model / model router 構成が一般化する可能性が高い。

* コーディングは Claude
* 汎用業務は ChatGPT
* 低コスト大量処理は Gemini Flash など
* 機密性の高い処理は self-hosted / open weights
* 重要判断は複数モデルでクロスチェック

この構造では、OpenAI が総合首位を取っても、Anthropic が高単価領域で残る余地は十分にある。

---

# 13. 今後の競争構造

OpenAI と Anthropic の競争は、単純な winner-takes-all にはなりにくい。

今後の市場は、以下のように分化する可能性が高い。

| 領域 | 優位になりやすい要素 |
| --- | --- |
| 汎用チャット | 配布網、UI、コスト、速度 |
| 開発者向け coding agent | IDE/CLI 統合、コード理解、テスト実行、PR 生成 |
| 企業業務エージェント | 権限管理、監査、社内データ接続、ワークフロー統合 |
| API 利用 | 価格、レイテンシ、モデル性能、SDK、安定性 |
| 高リスク業務 | ハルシネーション耐性、説明可能性、ガバナンス |
| 大量処理 | 推論単価、スループット、キャッシュ、軽量モデル |
| 社内基盤 | ベンダー中立性、MCP、ルーティング、評価基盤 |

OpenAI は総合プラットフォームとして強い。  
Anthropic は coding / enterprise workflow に強い。  
Google は compute、価格、Workspace、巨大配布で強い。  
open weights はコスト、制御性、オンプレミス、規制対応で使われる。

したがって、「OpenAI か Anthropic か」という二択ではなく、用途ごとに最適モデルとハーネスを選ぶ構造になる。

---

# 14. 利用企業への示唆

日本企業がこの競争を見るとき、重要なのは「どのベンダーを選ぶべきか」ではない。

より重要なのは、AI を業務に接続するための自社ハーネスをどう設計するかである。

## 14.1 モデル名ではなく業務成果で評価する

ベンチマークだけで選定してはいけない。

見るべきなのは、自社業務での end-to-end 成果である。

* 要件定義が進むか
* 調査時間が減るか
* コードレビュー工数が減るか
* PR 作成速度が上がるか
* テスト作成が自動化されるか
* 社内文書の検索精度が上がるか
* 承認フローに組み込めるか
* 監査ログを残せるか
* 人間の確認コストが下がるか
* セキュリティ事故リスクが許容範囲か

AI 導入の評価軸は、モデル単体ではなく、業務単位の生産性で置くべきである。

## 14.2 ベンダーロックインを避ける

AI エージェントの接続仕様は、MCP のような標準へ寄っていく可能性が高い。

したがって、自社システムを特定モデル専用に作り込みすぎるのは危険である。

望ましい構成は以下である。

* モデルは差し替え可能にする
* ツール接続は標準仕様に寄せる
* 社内データ接続は抽象化する
* 業務別評価データセットを自社で持つ
* 重要業務では複数モデルで検証する
* プロンプトやルールをコード管理する
* 監査ログと権限管理を最初から設計する

モデルは外部ベンダーが提供する。しかし、自社業務に最適化されたハーネスは、自社側で設計する必要がある。

## 14.3 自社ハーネスこそ競争力になる

AI 活用の差は、最終的には「どのモデルを使っているか」ではなく、「モデルをどの業務プロセスにどう接続しているか」で決まる。

具体的には、以下が重要になる。

* 社内 DB との接続
* チケット管理との接続
* ドキュメント管理との接続
* コードベースとの接続
* 承認フロー
* 監査ログ
* セキュリティポリシー
* 評価データセット
* チームごとの運用ルール
* 失敗時のロールバック設計

OpenAI も Anthropic も強力なモデルとプロダクトを提供する。だが、それを自社業務の成果に変換する部分は、各企業の設計能力に依存する。

ここが今後の差別化ポイントになる。

---

# 15. 結論

OpenAI と Anthropic の競争は、モデル性能だけの競争ではなくなった。

Anthropic は Claude Code と MCP によって、モデルを実務に接続するハーネスの重要性を市場に示した。これは大きな成果である。

一方で、OpenAI は Codex、Responses API、Agents SDK、ChatGPT agent によって、同じ領域へ急速に踏み込んでいる。OpenAI はモデル性能、配布網、資本力、開発者基盤を持っており、総合プラットフォームとしての優位は大きい。

したがって、長期的には OpenAI が総合 AI プラットフォームとして優勢である可能性が高い。

ただし、Anthropic は単なるマーケティングで伸びているわけではない。Claude Code は開発者ワークフローに入り込み、企業支出を獲得している。coding / enterprise workflow では、Anthropic が今後も強いポジションを維持する余地がある。

今後の競争は、以下の構図になる。

> OpenAI は総合プラットフォームで強い。Anthropic は実務ワークフロー、特に coding / enterprise で強い。ハーネスの標準化が進むほど、最終的な差別化はモデル性能、配布網、コスト、ガバナンス、自社業務への統合力に戻る。

企業にとって重要なのは、OpenAI か Anthropic かを宗教的に選ぶことではない。

重要なのは、モデルを差し替え可能にし、自社データと業務プロセスに接続し、実務成果を測定できるハーネスを持つことである。

AI 競争の主戦場は、モデルそのものから、モデルを仕事に変換するハーネスへ移った。
