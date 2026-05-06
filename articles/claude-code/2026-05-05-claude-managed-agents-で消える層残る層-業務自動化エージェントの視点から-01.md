---
id: "2026-05-05-claude-managed-agents-で消える層残る層-業務自動化エージェントの視点から-01"
title: "Claude Managed Agents で消える層、残る層: 業務自動化エージェントの視点から"
url: "https://zenn.dev/genda_jp/articles/8038f227ba9bdf"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

2026年4月8日、AnthropicがClaude Managed Agentsを公開しました。公式は「meta-harness」と位置付けており、ブログでは「p50 TTFT 60%減・p95 90%減」というインフラレベルの改善が報告されています。TTFTはリクエストから最初の応答が返るまでの時間で、p50は中央値、p95は最も遅い5%を含む側の遅延を指します。中央値で6割短く、遅い側でも9割短くなった、ということです。マイナーな最適化では出ない、アーキテクチャ変更レベルの効果といえる数字です。Notion、Rakuten、Asana、Sentry、Vibecodeといった企業が早期採用済みです。

<https://www.anthropic.com/engineering/managed-agents>

日本語でもすでに、watany氏のハーネス用語整理、片山氏（paiza）のビルダー/ユーザーハーネス分類、kumamo\_tone氏やgalirage氏の試用記事など、複数の解説が出ています。

<https://zenn.dev/watany/articles/d8b692bbca65a3>

<https://note.com/rk611/n/n8424c56f4fa5>

<https://zenn.dev/kumamo_tone/articles/365845d65e6cf4>

<https://zenn.dev/galirage/articles/claude-managed-agents-quickstart>

ただし既存の議論は、ほぼコーディングエージェント前提で進んでいます。Notion（コーディング・スプレッドシート・スライド）、Sentry（バグ → PR自動化）、Vibecode（コード生成基盤）と、いずれもコーディング系の用途で揃っています。一方で、Markdown + MCPで業務自動化エージェント（毎朝のブリーフィング、月次の経理処理、QA運用、スタイルチェックなど）を組んでいる人にとって、Managed Agentsはどう位置付くのか。この視点での整理は、まだ広く出ていません。

私の運用するリポジトリは、`agents/` 配下に15個のロール別エージェント指示書、`knowledge/` 配下に40件以上のナレッジファイル、`prompts/` にタスクテンプレートを置いた構成です。Claude DesktopとMCPで日常の業務を回しています。前回のハーネス記事で書いた「Markdownだけで作るハーネスエンジニアリング」がこれです。

<https://zenn.dev/genda_jp/articles/e09cab2916c241>

Managed Agentsの登場で、この自前ハーネスはどうなるのか。全部置き換わるのか、一部だけか、それとも全く別の話なのか。

この記事で扱うのは、Managed Agentsが提供する層と、自前で持ち続ける層の境界です。技術的に乗せられる/乗せられないの話ではなく、「乗せられても、乗せない方が良い」根拠まで含めて、五つの観点に分けました。後半は、私が運用するリポジトリにある各エージェントを「乗る / 部分的に乗る / 乗らない」で実際に分類してみます。

## コーディングエージェントと業務自動化エージェント、ハーネスへの要求は違う

Managed Agentsを業務自動化視点で評価する前に、既存事例の前提を確認しておきます。

公式が紹介している早期採用事例は次のとおりです。

* Notion: コーディング・スプレッドシート・スライドのタスクを並列で委譲、Notion内で完結
* Rakuten: 部門ごとに専門エージェントを配置、各部門が1週間以内に立ち上げ
* Asana: AI Teammatesがプロジェクト内のタスクを引き受ける
* Sentry: 検知したバグから自律的にPRを作成
* Vibecode: コード生成基盤として10倍速のインフラ立ち上げ

コーディング寄りの事例（Notion・Sentry・Vibecode）から部門業務系（Rakuten・Asana）まで幅がありますが、いずれも長時間にわたって自律的に走り続けるタスクで、ファイルやリソースを連続的に操作する用途を含みます。Managed Agentsの「session実行時間 $0.08/hour」「長時間タスクのチェックポイント」「サンドボックス内コード実行」といった機能は、こうした用途に最適化されています。

一方で、Markdown + MCPで業務自動化エージェントを組んでいる例として、私の運用や構想を含めて、こういった使い方が挙げられます。

* 朝のブリーフィング（Calendar・Slackメンション・Gmail・ニュース要約を毎朝まとめる）
* 月次経理サポート（freeeから取引データ取得・Excelで集計・関係者に共有）
* QA運用（MagicPodの実行結果レビュー・問題のあるテストケースをConfluenceに記録・Slackで共有）
* スタイル監査（記事ドラフトを `writing-style-guide.md` に照らして検証）
* 1on1の準備（過去のメモを集約し論点を整理）

両者を並べると、ハーネスへの要求は次の4点に分類ができそうです。

| 観点 | コーディングエージェント | 業務自動化エージェント |
| --- | --- | --- |
| 主な操作対象 | ファイルシステム + リポジトリ | SaaS API（Slack、Calendar、Gmail、freee等） |
| 実行時間 | 数分〜数時間の長時間タスク | 短時間タスクの繰り返し |
| 状態の所在 | コンテナ内のファイル状態を持続 | SaaS側に状態が残る、ローカルは一時的 |
| トリガー | 人間が指示（チャットUI） | スケジュール、イベント、人間の指示が混在 |

Managed Agentsの設計は、ファイルシステムを持続させて長時間動かす用途に向いています。サンドボックス、checkpoint、session実行時間課金といった機能はその文脈で意味を持ちます。業務自動化のように「SaaS APIを呼ぶ短時間タスクを多数回す」用途では、これらの機能は使い切れないでしょう。

これは「業務自動化はManaged Agentsに合わない」と言いたいのではありません。用途が違うので、Managed Agentsから受け取れる価値の中身も違う、ということです。自前ハーネスとどう組み合わせるかを、次のセクション以降でまとめます。

公式記事「Scaling Managed Agents: Decoupling the brain from the hands」（2026年4月8日公開）を読むと、Managed Agentsの設計思想が明確に書かれています。

<https://www.anthropic.com/engineering/managed-agents>

冒頭の一文がすべてを表しています。

> Harnesses encode assumptions that go stale as models improve.  
> ハーネスはモデル進化で陳腐化する仮定を含む。

具体例として、Sonnet 4.5は「context limit直前にタスクを早く切り上げる」挙動（context anxiety）があり、ハーネス側でcontext resetsを実装していました。同じハーネスをOpus 4.5で動かすと、その挙動は消えており、resetsはdead weightになっていた。ハーネスに組み込んだ補正は、モデルが賢くなると不要になる、という観察です。

そこでAnthropicは、ハーネスそのものを抽象化することにしました。OSが `process` と `file` という抽象でハードウェアを仮想化したように、Managed Agentsはエージェントを次の三つに分離しています。

* Session: イベントの追記専用ログ。すべての出来事の真実
* Harness: Claudeを呼び出し、ツール呼び出しをルーティングするステートレスなループ
* Sandbox: コードやファイル操作の実行環境

そしてharnessはsandboxを `execute(name, input) → string` というシンプルなインターフェースで呼びます。コンテナだろうが、スマートフォンだろうが、Pokémonエミュレータだろうが、同じ抽象で扱える、というのが公式記事の表現です。

このdecoupleが効くのは、コンテナを「pet」から「cattle」に変えられる点です。petは名前を付けて個別に世話する固有の存在、cattleは番号管理で替えがきく群れの一頭、というインフラ運用の比喩です。コンテナが死んだら、harnessはツール呼び出しエラーとして受け取り、新しいコンテナをプロビジョニングする。harnessが死んでも、`wake(sessionId)` で再起動して `getSession(id)` でイベントログを取り直せば、最後のイベントから再開できる。セッションログだけが永続化されている、という設計です。

冒頭で触れたTTFTの改善（p50で約60%減、p95で90%以上減）は、このdecoupleから来ています。コンテナのプロビジョニングを待たずに推論を始められるためです。

Anthropicは自身のサービスを「meta-harness」と位置付けています。記事の結論部分を引用します。

> Managed Agents is a meta-harness in the same spirit, unopinionated about the specific harness that Claude will need in the future.  
> Managed Agentsは同じ思想に立つmeta-harnessであり、Claudeが将来必要とする個別のharnessについては何も決めつけない設計である。

つまりAnthropicが提供しているのは、「あらゆるharnessが乗る安定インターフェース」（session / harness / sandboxのvirtualization）であって、「これがあなたのharnessです」と決めつけるものではないのです。Claude Codeもtask-specific harnessもcustom harnessも、すべてその上で動かせるように設計されています。

これがManaged Agentsの位置付けです。

<https://platform.claude.com/docs/en/managed-agents/overview>

次のセクションでは、その上に乗る「自前ハーネス」の中身を見ていきます。

## 自前ハーネスは2層構造: Managed Agentsで置き換わる層、自分で残す層

公式のmeta-harness設計が提供するのは、`session / harness / sandbox` の三つの抽象でした。これは言い換えると、エージェントを動かすためのOS層です。プロセス、ファイルシステム、メモリのような、上位アプリが乗る土台と言えるでしょう。

では、自前ハーネスはこの上に何を乗せているのか。私の運用するリポジトリの場合、こうなっています。

```
ikenyal-ai-agents/
├── agents/                  # ロール別エージェント指示書
│   ├── executive-assistant.md
│   └── ...                  # その他のロール定義
├── knowledge/               # ナレッジベース
│   ├── writing-style-guide.md
│   ├── article-strategy.md
│   └── ...                  # 各種コンテキスト
├── prompts/                 # タスクテンプレート
│   ├── morning-briefing.md
│   └── 1on1-prep.md
├── tasks/                   # タスク定義
├── scripts/                 # 分析・自動化スクリプト
├── docs/                    # 作業ログと運用ドキュメント
└── README.md                # ルート指示書
```

これらは、Managed Agentsが提供する「OS層」とは別のレイヤーにあります。エージェントが「何を知っているか」「どう振る舞うか」「何を禁止するか」を表現する、「ナレッジ層」と呼ぶべき領域です。

| 層 | 提供主体 | 内容 | 例 |
| --- | --- | --- | --- |
| **OS層** | Managed Agents（meta-harness） | エージェントループ、ツール実行、サンドボックス、セッション永続化 | `session / harness / sandbox` の三つの抽象 |
| **ナレッジ層** | 自前リポジトリ | エージェントの振る舞い指示、組織コンテキスト、専門知識、スタイル規約 | `agents/`、`knowledge/`、`prompts/`、`CLAUDE.md`、`AGENTS.md`、`SKILL.md` |

既存の日本語記事（watany氏のハーネス用語整理、片山氏のビルダー/ユーザーハーネス分類）は、ハーネス全体を一括して論じています。Managed Agentsの登場で何が変わるかを正確に読み取るには、この2層構造として見る必要があります。

Managed Agentsが置き換えるのは、OS層だけです。ナレッジ層はそのまま残ります。

ここまでは技術的な事実の確認でした。ここから先が本記事の本題です。Managed AgentsはSkills（`SKILL.md`）もagent定義も登録できるので、技術的にはナレッジ層の一部も乗せられます。にもかかわらず、なぜ自前で残した方が良いのか。次のセクションで五つの観点に分けてまとめます。

## なぜナレッジ層をAnthropicに渡さない方がいいか: 五つの観点

Managed Agentsの公式ドキュメントを読むと、`mcp_servers` の定義、`tools` の選定、`system` プロンプト、Skills（`SKILL.md`）はすべてagent定義として登録できます。技術的にはナレッジ層も乗せられます。

それでも自前で残した方が良い、というのが本記事の主張です。理由を五つ挙げます。

### 観点1: データの所在が変わる

業務自動化エージェントには、組織のコンテキストが含まれることが多くあります。私の場合、`agents/` 配下には所属組織の体制、運用知識、関係者情報、各種業務判断の基準などが書かれています。これらをManaged Agentsに登録すると、Anthropic側のリソースとして保存されます。明示的に削除するまで、Anthropic側に残り続けます。

ここで意識しておきたいのは、Managed Agentsのデータ保持の性格です。公式の「API and data retention」ドキュメントには、次のように明記されています。

<https://platform.claude.com/docs/en/build-with-claude/api-and-data-retention>

> Claude Managed Agents is a stateful resource. You can delete session transcripts, but there is no automatic deletion.  
> Claude Managed Agentsは状態を保持するリソースです。セッション記録は明示的に削除できますが、自動的には削除されません。

Skills（`SKILL.md`）にも同様の記述があります。

<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>

> Agent Skills is not covered by ZDR arrangements. Data is retained according to the feature's standard retention policy.  
> Agent SkillsはZDR契約の対象に含まれません。データは機能ごとに定められた標準の保持ポリシーに従って保管されます。

ここで出てくるZDR（Zero Data Retention）は、Anthropicの審査を経たEnterprise API顧客が個別契約で結ぶオプションで、APIに送ったデータをAnthropic側で保持しない、という保証です。社内データをAIに扱わせる際の前提条件としてよく参照されます。Managed AgentsとAgent Skillsは、その最も厳しい契約でも対象外、というのが現在の位置付けです。

ZDR契約の有無に関わらず、agent定義もsessionもskillsもAnthropic側に保持されます。明示的に削除しない限り、自動削除はありません。

これは「絶対にダメ」という話ではなく、データの置き場と取り回しの問題です。Git管理も結局はGitHubなどの外部サービスを使うことが多いので、置き場が外部にある点は同じです。違うのは、Git管理なら置き場（GitHub・GitLab・self-hosted・remoteを設定しないlocalのみ、など）を選べて、Markdownのまま別の場所にも移せる、という点です。Managed Agentsに登録した時点で、置き場はAnthropic、形式もAnthropic独自のJSON構造、という固定の構造になります。社内データを扱うエージェントを設計する際、この差は判断材料になります。

### 観点2: 編集・運用ワークフローの摩擦

自前ハーネスの場合、ナレッジ層の更新サイクルは次のようになります。エディタで `agents/executive-assistant.md` を編集して保存、Claude Desktopが次のセッションで再読み込み、即反映。所要時間は秒単位です。

Managed Agentsで同じことをする場合、ファイル編集後にAPI登録（`create / update agent`）を呼び、セッションを再起動する必要があります。即時反映とはいかず、API呼び出しのぶんワンクッション入ります。

このコストが効いてくるのは、編集が「使ってみて気付いた瞬間」に発生する場面です。エージェントを動かしている最中に「この指示文が冗長だった」「ここを足したい」と気付き、エディタで該当ファイルを直して保存、次のメッセージで反映、という流れが日常的に走ります。

大きな違いは、所要時間そのものよりも、思考の流れが切れるかどうかです。自前ハーネスは編集と反映が「使う」フローの中で完結します。Managed AgentsはそこにAPI登録のステップが入るので、思考の流れが一度途切れます。「Markdown → API同期スクリプト」を自前で書いて埋める選択肢はありますが、そのスクリプト自体がメンテ対象になります。

### 観点3: Git管理の利点を失う

ナレッジ層は試行錯誤の連続です。エージェントへの指示文を書き換え、結果を見て、また書き換える。`git diff` で変更点を見て、`git log` で歴史を辿り、`git blame` でなぜこうなったか確認する。気に入らなければbranchを切って実験する。

これらはManaged Agentsのagent定義APIでは使えません。Anthropic側にバージョン管理の仕組みはあるはずですが、`git` ツールチェーンのエコシステム（GitHub、PR、CI、code review、cherry-pick、rebase）は使えません。

ナレッジ層の進化は、git履歴で振り返ることに意味があります。「あのときなぜ `executive-assistant.md` にこの一文を足したのか」を、コミットのメッセージと一緒に追える。これは小さく見えて、運用の安心感を支える要素です。

### 観点4: オープン標準のポータビリティ

個人的に重視している観点です。

前回のDESIGN.md記事で書いたとおり、`AGENTS.md` と `SKILL.md` はオープン標準です。

<https://zenn.dev/genda_jp/articles/f71d3ed7d4d7e8>

`AGENTS.md` はOpenAI、Google、Sourcegraph、Cursor、Factoryらが共同推進し、2025年12月にLinux Foundationに寄贈されました。`SKILL.md` はagentskills.ioが標準化したAgent Skillsの中核です。

<https://agents.md/>

<https://agentskills.io/>

Codex、Claude Code、Cursor、GitHub Copilotといった複数のAIエージェントが、同じファイルを読みます。

一方、Managed Agentsのagent定義は、`name` `model` `system` `tools` `mcp_servers` `skills` などをまとめたAnthropic独自のJSON構造です。`SKILL.md` をManaged Agentsに登録すれば動きますが、それはAnthropicに閉じた登録であって、CodexやCursorからは見えません。

これは「ベンダーロックイン」というより、せっかく標準化されたものを特定実装に再ロックインする退行に近いとも言えるでしょう。`AGENTS.md` / `SKILL.md` がオープン標準として広がっていく流れに対して、自分のナレッジをAnthropic独自フォーマットに閉じ込める判断は、あえて選ぶメリットは見えにくくなります。

自前リポジトリで `AGENTS.md` / `SKILL.md` を持つ、という構成は、Managed Agents、Codex、Cursor、その他のAIエージェントから等しく参照できる「中立な置き場」を維持する選択でもあります。

### 観点5: テスト・試行錯誤のスピード

エージェントを「育てる」フェーズでは、サイクルの速さが質を決めます。指示書の一行を書き換える、試す、結果を見る、また書き換える。このループが速ければ速いほど、エージェントの精度はどんどん上がっていきます。

自前ハーネス（Claude Desktop + Markdown）の場合、書き換えて保存、次のメッセージで反映、所要時間は秒単位です。

Managed Agentsだと、agent更新APIを呼び、environmentを再構築し、sessionを起動し直して、テストします。1サイクルごとにAPI経由のステップが挟まる構造です。「育てる」フェーズには不利になりやすい局面とも言えます。

本番運用に入った長時間タスク（セッション数時間〜）では、Managed Agentsの安定性とスケーラビリティが価値を発揮します。しかし業務自動化エージェントは、毎日少しずつ手を入れて育てるフェーズが長いものが多いです。私の `executive-assistant.md` も、数ヶ月以上にわたって毎週何かしら手を入れています。

### 五つの観点を束ねて見えること

「乗せられる」と「乗せた方が良い」は別の問題です。Managed Agentsの公式設計が `meta-harness` を志向しているように、その上のナレッジ層も「meta-harnessの外側」に置いた方が、上記の観点で合理的に見えます。

公式が三層分離（session / harness / sandbox）で「上に乗るharnessは何でも良い」と形を決めつけない設計を選んだのと対称的に、ユーザー側も「ナレッジ層は自前で持つ」という形を決めつけない選択ができる。これが2層構造で見たときの自然な帰結だと思います。

## 自前のエージェント群を「乗る / 部分的に乗る / 乗らない」で分類してみる

ここまでの整理を、自前のエージェント群に当てはめてみます。Managed Agentsに「乗る / 部分的に乗る / 乗らない」の三段階で分類すると、大きく次のパターンが見えてきます。

| 用途のタイプ | 主なツール | 判定 | 判定の根拠 |
| --- | --- | --- | --- |
| 個人秘書系（カレンダー・メール・チャット・ローカルファイル横断） | カレンダー・メール・チャット・チケット管理・Web検索・ローカルファイル操作 | 部分的に乗る | 主要MCPはリモート対応で乗るが、ローカルファイル操作系MCPはリモート版が無く、その範囲は乗らない |
| インフラ運用支援系 | クラウドAPI・チャット・ドキュメント | 乗る | 主要ツールがすべてリモートMCPで完結し、長時間タスクの想定とも相性が良い |
| プロジェクト・組織運用支援系 | チャット・チケット管理 | 乗る | 主要ツールがすべてリモートMCPで完結し、ローカル依存も無い |
| テスト品質運用系 | テスト自動化ツールのMCP・チャット・ドキュメント | 乗らない | テスト自動化ツールのMCPがローカルstdio型のみで、リモート前提のManaged Agentsから呼べない |
| 部門業務系（経理・法務など） | SaaS API・チャット・ローカルExcelやドキュメント参照 | 部分的に乗る | SaaS API側はリモートMCPで乗るが、ローカルExcelやドキュメント参照は乗らず、社内データの扱いには組織のガバナンス判断も要る |
| 対話による思考整理系（朝のブリーフィング・1on1準備など） | カレンダー・チャット・Web検索 | 乗らない | Claude Desktopで対話しながら深掘りすることを前提に設計しており、自律実行のManaged Agentsとは用途が合わない |

ここで気付くのは、ナレッジ層はどのパターンでも自前のまま、という点です。「乗る」と判定したエージェントについても、ロール定義、組織コンテキスト、スタイル規約は自前リポジトリに置き続けます。Managed Agents側に置くのは、エージェントを動かすOS層の機能（サンドボックス、ハーネスループ、セッション永続化、認証vault）だけです。

これが前述した2層構造の具体例です。OS層はAnthropicに任せる選択肢があり、ナレッジ層は手元に残す。エージェント単位で「OS層を任せるか / 任せないか」を判断する、という形になります。

自身のエージェント群を当てはめるときの判断軸は、次の四つです。

* 主要ツールがリモートMCPで完結するか、ローカルツールに依存するか
* 扱うデータが社内データを含むか、含まないか
* 長時間タスクか、短時間タスクの繰り返しか
* 「育てる」フェーズか、「運用する」フェーズか

これらに照らして、エージェントごとに判断してみてください。

## 想定される反論と回答

ここまでの整理に対して、想定される反論を三つ取り上げます。

### 反論1: 主要MCPがリモート対応しているなら、全部乗せれば？

> 主要MCP（Slack・Atlassian・Calendar・Gmail・freee）はリモート対応してるから、業務自動化も全部Managed Agentsに乗せれば良いのでは？

確かに2026年5月時点で、業務自動化に必要な主要MCPの多くはリモート対応しています。Atlassian Rovo、Slack、Google Calendar/Gmail、freeeなどです。「乗せられるエージェント」は増えています。

<https://platform.claude.com/docs/en/managed-agents/mcp-connector>

<https://platform.claude.com/docs/en/agents-and-tools/remote-mcp-servers>

ただし、本記事の主張は「乗せられないから乗せない」ではなく「乗せられても、乗せた方が良いとは限らない」です。OS層は乗せる候補になりますが、ナレッジ層を乗せるかどうかは、五つの観点（データの所在、編集ワークフロー、git管理、オープン標準、試行速度）で個別判断する必要があります。

### 反論2: $0.08/hour は許容できるのでは？

> $0.08/hour は許容できるのでは？

短時間タスクなら問題ありません。朝のブリーフィングが10分で終わるなら、月20営業日 × 10分。つまり、約3.3時間 × $0.08 = $0.26、加えてトークン課金。これだけなら許容範囲です。

問題になるのは、Claude Desktopで日常的に使っているエージェントを移すかどうかです。業務時間中に常時開いて使うような使い方をそのままManaged Agentsに置き換えると、セッション課金とトークン課金が稼働時間にそのまま比例します。同じ使い方をすれば、コストは上がる可能性が高くなります。

「Managed Agentsに乗せる / Claude Desktopで使う / 併用する」は、用途とコスト構造でエージェントごとに判断する話です。

### 反論3: 既存事例があるなら、業務自動化も乗せれば？

> Notion / Sentry / Vibecodeのような事例があるんだから、業務自動化も乗せれば良いのでは？

これらの事例はすべてコーディング系（コード生成、バグ修正、スプレッドシート操作）です。業務自動化エージェントの典型（SaaS連携、月次レポート、QA運用）とはハーネスへの要求が違うことは、前段で整理しました。

そして実は、これらの事例も全部Managed Agents内に閉じているわけではありません。NotionはNotion内で、SentryはSentryのインフラで、VibecodeはVibecodeのプラットフォームで、それぞれ独自のナレッジとUXを持っています。Managed Agentsはその下で動くOS層として機能する。これは本記事の2層構造の主張と整合します。

## 一手目をどこに置くか

実際に手をつけるなら、このような流れになるでしょう。

1. **自前のエージェント群の中で、SaaS連携が中心のものを抽出する**: ローカルファイル操作やデスクトップ連携のないエージェントが候補
2. **そのエージェントが扱うMCPがリモート対応しているか確認する**: Slack、Atlassian、Calendar、Gmail、freeeあたりは対応済み。それ以外は個別確認
3. **一つだけManaged Agentsに乗せて運用してみる**: いきなり全部移行しない。一つで運用感をつかむ
4. **ナレッジ層は自前リポジトリで継続管理する**: agent定義はAPIに登録するが、`agents/` `knowledge/` `prompts/` はgitで管理し続ける。Markdownを正、API登録はミラーと位置付ける
5. **段階的に乗せる範囲を広げる、または広げない**: 一つ運用してみて、コスト・速度・編集ワークフローの観点で問題なければ次へ。問題があれば自前のままで残す

「全部書き換え」も「全部自前」も極端です。エージェント単位で判断する、というのが現実的な落とし所だと思います。

ハーネスはモデル進化で陳腐化する仮定を含む。公式の言葉です。OS層の自前実装は、Managed Agentsの登場で確かに陳腐化します。Sandbox、エージェントループ、セッション永続化を自前で書く必要はもうありません。

しかし、その上のナレッジ層は、組織と個人の文脈を表現する場所であり続けます。`AGENTS.md` も `SKILL.md` も、オープン標準として複数のAIエージェントから参照される。gitで管理され、エディタで秒単位に編集される。`writing-style-guide.md` のような自分が育てたルールは、Anthropic側のリソースではなく、自分のリポジトリで進化していく。

ハーネスエンジニアリングの次の一歩は、層を分けて考えるところから始まります。
