---
id: "2026-06-30-claudeアーティファクトは-sonnet-と-opus-で質が変わるのか公式ドキュメントだけで仕-01"
title: "Claudeアーティファクトは Sonnet と Opus で質が変わるのか？──公式ドキュメントだけで「仕組み」から考える"
url: "https://qiita.com/yamapiiii/items/79a155f7c6b79e141343"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "cowork"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

# Claudeアーティファクトは Sonnet と Opus で質が変わるのか？──公式ドキュメントだけで「仕組み」から考える

> 「Claudeのアーティファクト、Sonnet と Opus で出来が変わるの？」
> ——よく聞かれる問いだが、ネットの体感談ではなく **Anthropic の公式ドキュメントだけ** を根拠に、しかも **"なぜ差が出るのか"の仕組み** まで掘り下げて答えてみる。
>
> 結論を先に言うと「**変わり得る。ただしその根拠は、世間で思われているほど"公式に明言"されていない**」。この記事は、その温度差を正確に書くことを目的にしている。

---

## TL;DR（結論）

- **アーティファクトの質はモデルで変わり得る。** ただし Anthropic は「Opus の方がアーティファクトの質が高い」と **Sonnet と直接比較して明言してはいない**。
- 差が出る理由は、体感ではなく **2つの公式事実から"仕組み"として説明できる**：
  1. **モデル層の位置づけ** — Opus 4.8 は「複雑な推論・長時間のエージェント的コーディング・高自律タスク向けの最も高性能な *Opus ティア* モデル」、Sonnet 4.6 は「速度と知性の最良の組み合わせ」。
  2. **アーティファクト特有の制約** — アーティファクトは厳格な **CSP（Content Security Policy）** のもとで動く **自己完結型の単一ページ**。外部リクエストが全面ブロックされるため、「制約を最後まで守る」「一発で破綻なく組む」難度が高く、ここでモデルの能力差が効きやすい。
- **実用結論**：凝ったデザイン・複雑なインタラクティブUI・一発勝負 → **Opus**。定番もの・とにかく速く回す → **Sonnet**。公式の推奨は「**まず速くて安いモデルから始め、足りなければ上げる**」。
- ⚠️ よくある誤解の訂正：Claude Code の `/fast`（Fast モード）は **Opus 4.8 / 4.7 のみ**対応で、**Opus 4.6 は対象外**。しかも 4.7 向けは2026/7/24に廃止予定。執筆時点（2026/6/30）で実質 **Opus 4.8 専用**。

> 📌 この記事の引用方針：**anthropic.com / claude.com / platform.claude.com / code.claude.com / support.claude.com の公式情報のみ**を出典とする。公式に書かれていない推論部分は「**これは推論です**」と明示する。数値・仕様は執筆時点（2026年6月30日）のもの。

---

## 1. そもそもアーティファクトとは何か（ここが"仕組み"の起点）

質の差を語る前に、アーティファクトが**技術的に何なのか**を押さえる。ここを理解すると「なぜモデル能力が効くのか」が腑に落ちる。

### 1-1. 「会話とは別ウィンドウの、自己完結したコンテンツ」

公式ヘルプセンターの定義：

> Claude can share substantial, standalone content with you in a dedicated window separate from the main conversation.
> （会話本体とは別の専用ウィンドウで、まとまった自己完結型コンテンツを共有できる）

生成のトリガーは「内容が **significant かつ self-contained**（おおむね15行超）で、追加の会話文脈なしに単体で成立するもの」とされている。
出典：[What are artifacts and how do I use them?（Claude Help Center）](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)

対応コンテンツは Markdown/プレーンテキスト、コードスニペット、**単一ページのHTMLサイト**、SVG、図・フローチャート、**インタラクティブな React コンポーネント**など（同上）。

### 1-2. 「厳格なCSPの下で動く、外部リクエスト全ブロックのサンドボックス」← 最重要

ここが核心。Claude Code のアーティファクト公式ドキュメントは、ランタイムの制約を**ほぼそのままの言葉で**書いている：

> Each artifact is one self-contained page. Claude Code wraps the file you publish in an HTML document shell and serves it under a strict Content Security Policy (CSP), which shapes what the page can do.
> （各アーティファクトは1つの自己完結ページ。公開するファイルをHTMLドキュメントの殻で包み、**厳格なCSP**のもとで配信する）

そして「No external requests（外部リクエスト不可）」の項：

> The CSP blocks scripts, stylesheets, fonts, and images loaded from any other host, along with `fetch`, XHR, and WebSocket calls. Claude inlines CSS and JavaScript and embeds images as data URIs so the page renders without any external request.
> （CSPは**他ホストからのスクリプト・スタイルシート・フォント・画像**の読み込みを、**`fetch`・XHR・WebSocket** ともどもブロックする。そのため Claude は **CSS/JS をインライン化**し、**画像を data URI として埋め込む**ことで、外部リクエストゼロで描画されるようにする）

出典：[Share session output as artifacts（Claude Code Docs）](https://code.claude.com/docs/en/artifacts)

さらに：
- **バックエンドなし**：「静的ページであり、フォーム送信データの保存・閲覧者の認証・閲覧時のAPI呼び出しはできない」
- **単一ページ**：「相対リンクは解決されない。複数セクションはページ内アンカーで表現する」
- ビューアは **`*.claudeusercontent.com`** という **claude.ai とは別のサンドボックスオリジン**から読み込まれる
- 公開ファイルは `.html` / `.htm` / `.md`、描画後サイズは **16 MiB 以下**

（すべて同上の Claude Code Docs より）

> 🔎 **例外が1つだけある**：claude.ai の「会話アーティファクト」は、**Claude 自身の補完API**だけは呼べる（＝AIを内蔵したアプリ化）。閲覧者は自分のClaudeアカウントで認証され、APIキー管理が不要。ただし現状の制約として「外部API呼び出し不可・永続ストレージなし・テキストベースの補完APIに限定」と公式に明記されている。
> 出典：[Build and share AI-powered apps with Claude](https://claude.com/blog/claude-powered-artifacts)

> ⚠️ 出典の精度について：この **詳細なCSPの記述は Claude Code のアーティファクト（Team/Enterprise 向けベータ）ドキュメント**のもの。claude.ai の会話アーティファクトも「外部リクエスト不可」という挙動は同じだが、消費者向けページに同等の技術仕様は公開されていない。記事で引用する際はこの点を添えると正確。

### 1-3. この制約が「モデル能力が効く理由」を作る

ここまでで重要なのは、アーティファクトが **「外部依存を一切使えない、自己完結の単一HTMLを、一発で破綻なく組む」** という制約ゲームだということ。つまり：

- **CDN や外部CSS/JS/フォント/画像が使えない** → 全部インライン化・data URI化して破綻させない実装力が要る
- **単一ページ・バックエンドなし** → 状態管理やレイアウトをページ内で完結させる設計力が要る
- **`var(--surface-1)` のような"外側の環境に依存した変数"はアウト** → アーティファクト単体で色が崩れる

つまり **「長くて細かい制約を最後まで守り切る能力」「複雑なものを一発でバグなく組む能力」「崩れに気づいて直す能力」** が、そのまま出来栄えに直結する。次章以降は、これらの能力についてモデル間で**公式に何が言えるのか**を検証する。

> 💡 筆者の実体験（※これは公式情報ではなく体験談）：あるアーティファクトを作った際、初版が `var(--surface-1)` など **claude.ai 側のCSS変数に依存**していて、アーティファクト単体だと色が崩れた。作り直しで自己完結に修正できた——これは1-2の「自己完結でなければ破綻する」という仕組みの具体例。ただし「モデルを変えたから直った」と断定はできない（2回目は文脈が増えていた効果もある）。**1回の体感を一般則にしないこと**自体が、この記事の主題でもある。

---

## 2. モデルの公式な位置づけ（Opus vs Sonnet）

「どちらが上か」を語る前に、**公式がどう位置づけているか**を確認する。

### 2-1. ラインナップと位置づけ（公式の文言）

[Models overview（Claude Platform Docs）](https://platform.claude.com/docs/en/about-claude/models/overview) の説明文（原文ママ）：

| モデル | API ID | 公式の位置づけ（原文の要旨） |
|---|---|---|
| **Claude Fable 5** | `claude-fable-5` | "Anthropic's most capable widely released model"（**一般提供で最も高性能**、最も難度の高い推論・長時間エージェント向け） |
| **Claude Opus 4.8** | `claude-opus-4-8` | "Anthropic's most capable **Opus-tier** model for complex reasoning and agentic coding"（**Opusティアで最も高性能**） |
| **Claude Sonnet 4.6** | `claude-sonnet-4-6` | "The best combination of **speed and intelligence**"（速度と知性の最良の組み合わせ） |
| **Claude Haiku 4.5** | `claude-haiku-4-5-20251001`<br>（alias: `claude-haiku-4-5`） | "The fastest model with near-frontier intelligence"（フロンティアに迫る知性を持つ最速モデル） |

> ⚠️ **"最も高性能（most capable）"は Opus ではなく Fable 5。** ここをよく誤解する。Opus 4.8 はあくまで **「Opus ティアの中で」** 最高性能であり、その上位に Fable 5（上位ティア、$10/$50）が別枠で存在する。`choosing-a-model` も「最高の能力が必要なワークロードは Fable 5 を見よ」と明記している。
> （このほか、安全性分類器を外し限定提供される `claude-mythos-5` も存在する）

### 2-2. 価格とコンテキスト（公式）

[Pricing](https://platform.claude.com/docs/en/about-claude/pricing) より（per MTok = 100万トークンあたり）：

| モデル | 入力 | 出力 | コンテキスト | 備考 |
|---|---|---|---|---|
| Fable 5 | $10 | $50 | 1M | 上位ティア |
| Opus 4.8 | **$5** | **$25** | **1M** | 1Mは標準価格（長文脈の追加料金なし） |
| Sonnet 4.6 | **$3** | **$15** | **1M** | Opusより安い |
| Haiku 4.5 | $1 | $5 | 200K | 最安・最速 |

- Opus 4.8 と Sonnet 4.6 はいずれも **1Mトークンのコンテキストを標準価格で**利用できる（長文脈プレミアムなし）。
- バッチAPI（50%引き）：Opus 4.8 = $2.50/$12.50、Sonnet 4.6 = $1.50/$7.50。
- 出力上限は執筆時点のモデル比較表で Opus 4.8 / Sonnet 4.6 ともに最大128Kトークン、Haiku 4.5 は64K（[Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)。仕様は変わり得るので利用時に最新値の確認を推奨）。

**つまり Sonnet は Opus より約4割安く、位置づけは"速度と知性のバランス"。** ここが「定番ものは Sonnet で十分かつ快適」の公式な根拠になる。

---

## 3. なぜ"上位モデル"が効くのか──公式記述と推論を分けて検証

ここが本題。冒頭の「Opusが効く4つの軸」を、**公式に明言されているか／推論にとどまるか**で1つずつ判定する。実は、世間で言われるほどには **Opus vs Sonnet を直接比較した公式記述は存在しない**。

> 📋 判定ラベル：**【公式明言】**＝ほぼ原文どおり / **【部分的】**＝一部は公式・一部は推論 / **【推論】**＝公式の位置づけ等からの妥当な推測

### 軸① 制約遵守（長く細かい指示を守り切る）→【部分的・むしろ注意】

- Opus 4.8 のプロンプトガイドは「指示を**文字どおり・明示的に**解釈する。勝手に一般化せず、頼まれていないことを推測しない。**精度・予測可能性が高く、構造化抽出やパイプライン向き**」と述べる。
  出典：[Prompting Claude Opus 4.8](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8)
  → ただしこれは **対 Sonnet ではなく、対・前世代 Opus** の話。
- **反証（重要）**：Sonnet 4.6 の発表は「ユーザーは Sonnet 4.6 を**指示遵守の点で意味のある差で優れている（"meaningfully better at instruction following"）と評価**し、旧フロンティアの **Opus 4.5 より59%の割合で好んだ**」と書いている（"meaningfully" を「有意に」＝統計的有意差と読まないよう注意）。
  出典：[Introducing Claude Sonnet 4.6](https://www.anthropic.com/news/claude-sonnet-4-6)

> ✅ 正しい書き方：「Opus 4.8 は指示を**文字どおり厳密に**解釈する設計で、複数制約のパイプラインなど**予測可能性が要る用途**に向く」。**「Opusの方がSonnetより指示遵守が上」とは書かない**（公式はむしろ逆の評価も出している）。

### 軸② 一発で複雑・破綻なく組む → 【推論】

- Opus 4.8 は「自分が書いたコードの欠陥を見逃す確率が**前世代（Opus 4.7）比で約1/4**」。
  出典：[Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8)
  → これも **対 Sonnet ではなく対前世代**。
- 「one-shot（一発）」という言葉が出てくる公式箇所は、Opus 4.7 に関する **Vercel の顧客コメント**（「ワンショットのコーディングで素晴らしい。Opus 4.6より正確で完全」）であって、Anthropic自身の対Sonnet比較ではない。
- Opus 4.8 発表の数値は強力だが、**Super-Agent ベンチで全ケース完走した唯一のモデル**／**Online-Mind2Web で84%**といずれも対競合・対前世代の話。

> ✅ 正しい書き方：「複雑なUIを一発で組む難度の高い仕事は、**最上位ティアのOpusを選ぶ公式根拠がある**（複雑な推論・高自律向けと位置づけ）」。ただし「**バグなし**」「**Sonnetより信頼性が高い**」と断定する公式表現は無い。

### 軸③ デザインの判断力（題材に合った配色・タイポ・レイアウト）→【推論】

- Opus 4.7 発表に **Anthropic自身の言葉**で「より洗練され創造的になり、**より高品質なインターフェース・スライド・ドキュメント**を生成する」とある。
  出典：[Introducing Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7)
  → ただし **対前世代の世代間比較**で、対Sonnet比較ではない。
- 一方で公式のフロントエンド・デザイン記事は、いわゆる "AI slop"（量産型のダサさ）を **プロンプト/Skillsの問題** として扱い、デザイン品質の改善を**モデル層ではなくプロンプト・Skills**に帰している。Opus vs Sonnet の区別はしていない。
  出典：[Improving frontend design through skills](https://claude.com/blog/improving-frontend-design-through-skills)

> ✅ 正しい書き方：「Opusティアは公式自身が"より高品質なインターフェース・スライド・ドキュメントを生成する"（Opus 4.7発表、対前世代）と表現している。**ただしOpus vs Sonnetを"デザインの質"で直接比較した公式記述は無い**。デザインの良し悪しはモデル層だけでなく**プロンプトとSkills**にも大きく依存する、というのが公式の立場」。

### 軸④ デバッグ・自己修正（崩れに気づいて直す）→【推論】

- Sonnet 4.6 発表自身が認めている：「**最も深い推論を要するタスク**（大規模リファクタリング、複数エージェントの協調、"正確さが最重要"な問題）では **Opus 4.6 が依然として最良**（"Opus 4.6 remains the strongest option…"）」。
  出典：[Introducing Claude Sonnet 4.6](https://www.anthropic.com/news/claude-sonnet-4-6)
  → ⚠️ この発表は2025年秋時点のもので、引用が指すのは**当時の最上位 Opus 4.6**。現行の Opus 4.8 の優位性を語るなら[Opus 4.8 発表](https://www.anthropic.com/news/claude-opus-4-8)を根拠にすること。
- 同時に同発表は「**Sonnet 4.6 はバグ検出で Opus との差を大きく縮めた**」「複雑なアプリ構築やバグ修正でフロンティア級」とも述べる。
- Opus 4.8 の「コード欠陥を見逃しにくい（前世代比約1/4）」は **対前世代** の比較。

> ✅ 正しい書き方：「**最も深い推論を要するデバッグはOpusが最良**（Sonnet発表自身が認める）。ただし**一般的なバグ修正ではSonnetも差を縮めており十分強力**」。

### 🧠 補足：「大きいモデルだから優れている」は公式の主張ではない

ここは重要な注意。「Opusの方が**パラメータが大きいから**質が高い」というスケーリング則的な因果は、**Anthropicが公式に主張しているものではない**。公式の説明はあくまで **能力・ベンチマーク・機能単位**（effort パラメータ、adaptive thinking、メモリファイル、長文脈処理など）であって、「規模→能力」の因果論ではない。

参考になる公式の「仕組み」記述：
- **適応的思考（adaptive thinking）**：「Opus 4.8 は**ターンが必要とするときだけ推論を起動**する。単純な参照には即答し、複雑な多段問題では答える前に推論する」（[What's new in Opus 4.8](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8)）
- **拡張思考（extended thinking）**：「複雑なタスク向けに強化された推論。内部の段階的推論ブロックを出力し、それを踏まえて最終回答を作る。**予算を増やすと複雑問題で品質が上がり得る**」（[Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)）
- **長文脈の劣化**：「**コンテキストが埋まるとLLMの性能は劣化**し、初期の指示を"忘れ"、ミスが増える」（[Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)）→ Opusの大きなコンテキスト＆長文脈処理改善が大きな仕事で効く根拠。

> 記事に「規模が大きいから〜」と書くなら、**それは一般的なML的推論であって公式の主張ではない**と明示する。

### 🎯 数少ない"直接的"な公式推奨：可視化はOpus

ほとんどが推論にとどまる中で、**比較的はっきりした公式推奨**が1つある。Claude のサポート記事（カスタムビジュアル）は「**Smarter is better. Opus performs the best at visualization tasks**（賢いほど良い。Opusが可視化タスクで最も優れる）。複雑なものを作るなら、より賢いモデルを選べ」と述べている。チャートやデータ可視化のアーティファクトでOpusを推す根拠としては、これが最も直接的。
（出典：[Custom visuals in chat and Cowork — Claude Help Center](https://support.claude.com/en/articles/13979539-custom-visuals-in-chat-and-cowork)）

---

## 4. 実用ガイド（公式の使い分け）

### 4-1. 公式の「モデルの選び方」：まず安く、足りなければ上げる

[Choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) の指針：
- 「**高頻度・単純なタスクは、まず高速・低コストのモデルから始め**、特定の能力不足があれば必要に応じて上げる」
- 「最も複雑なタスクは Opus 4.8 から検討。**正確さがコストに勝るとき** に向く」
- 「最高の能力が要るなら Fable 5」

### 4-2. Claude Code の `opusplan`：計画はOpus、実装はSonnet

これは公式の中で最も実務的な「Opus×Sonnet 役割分担」のガイド：

> opusplan: プランモードでは **opus**（複雑な推論・アーキテクチャ判断）を使い、実行モードでは自動的に **sonnet**（コード生成・実装）に切り替える。**Opusの推論力とSonnetの効率を組み合わせる**。

出典：[Model configuration（Claude Code Docs）](https://code.claude.com/docs/en/model-config)

→ 「**Opusで骨格を作り、細かい実装はSonnetで回す**」という使い分けには公式の裏付けがある。

### 4-3. `/fast`（Fast モード）の正しい理解 ← 要訂正ポイント

**仕組み（公式明言・原文ママ）**：

> Fast mode is **not a different model**. It uses Claude Opus with a different API configuration that prioritizes speed over cost efficiency. **You get identical quality and capabilities with faster responses.**
> （Fastモードは**別モデルではない**。Claude Opus を速度優先のAPI構成で動かすもので、**品質・能力は同一のまま、応答が速くなる**。最大約2.5倍速、ただし高コスト）

出典：[Speed up responses with fast mode（Claude Code Docs）](https://code.claude.com/docs/en/fast-mode)

つまり「**小さいモデルに格下げするのではなく、同じOpusを速くする**」は**公式に正しい**。一方で：

- ❌ **「4.6〜4.8で使える」は誤り。** 公式：「Fast mode is supported on **Opus 4.8 and Opus 4.7**. It is not available on Sonnet, Haiku, or other models.」 → **Opus 4.6 は対象外**。
- ⏳ **Opus 4.7 向けは2026/6/25に非推奨化、2026/7/24に廃止予定**（廃止後はエラーになり標準Opus 4.7にフォールバックもしない）。→ **執筆時点（2026/6/30）で実質 Opus 4.8 専用**。
- 🔬 research preview 機能。Claude Code **v2.1.36以降**が必要、**VS Code拡張では非対応**、Bedrock/Vertex/Azure Foundry/Claude Platform on AWS では利用不可。
- Fast モード料金は Opus 4.8 が $10/$50、Opus 4.7 が $30/$150（per MTok）。
- `effort`（思考量）とは別物：Fast = 同品質で低遅延・高コスト／effort低下 = 思考時間を削って速くする（品質低下の可能性）。併用も可能。

### 4-4. プラン別デフォルト（実務上の"そもそも何が動いているか"）

- **Max / Team Premium / Enterprise pay-as-you-go / Anthropic API**：既定 **Opus 4.8**
- **Pro / Team Standard / Enterprise サブスク席**：既定 **Sonnet 4.6**

出典：[Model configuration](https://code.claude.com/docs/en/model-config)

→ 「自分の環境で実際どちらが動いているか」はプランで変わる。質の体感差を語る前に、まず `/model` で確認するのが正しい。

---

## 5. まとめ：使い分けと「公式が言っていること／いないこと」

### 使い分けの目安

| 用途 | おすすめ | 公式の根拠の強さ |
|---|---|---|
| 凝ったデザイン・複雑なインタラクティブUI・一発勝負 | **Opus** | 推論（最上位ティアの位置づけ＋"より高品質なインターフェース"の世代間記述） |
| データ可視化・チャート | **Opus** | 比較的直接的（サポート記事「Opusが可視化で最良」） |
| 最も深い推論を要するデバッグ・大規模リファクタ | **Opus** | 公式（Sonnet 4.6発表が「Opus 4.6が依然最良」と認める／現行Opus 4.8の根拠は別途4.8発表を参照） |
| 定番ダッシュボード・シンプルなUI・高速反復 | **Sonnet** | 公式（「まず高速・低コストから」＋速度/価格優位） |
| 計画はOpus・実装はSonnet | **opusplan** | 公式明言 |
| Opusの質のまま速度も欲しい | **Opus 4.8 + /fast** | 公式明言（同モデル高速化） |

### 公式が「言っていること」と「言っていないこと」

**✅ 公式が明言**：
- アーティファクト＝厳格CSP下の自己完結ページ／外部リクエスト全ブロック
- Opus 4.8 ＝ Opusティア最高性能／Sonnet 4.6 ＝ 速度と知性の最良バランス
- "最も高性能"は **Fable 5**（Opus 4.8 ではない）
- `/fast` は別モデルへの格下げではなく同Opusの高速化、対応は **4.8/4.7のみ**
- 最も深い推論を要するタスクでは（当時の最上位）Opus 4.6 が最良（Sonnet 4.6発表自身が認める）
- 可視化タスクは Opus が最良（サポート記事）

**❌ 公式は言っていない（＝記事で断定すると不正確）**：
- 「Opusの方がアーティファクトの**デザイン品質**が高い」（対Sonnetの直接比較は無い）
- 「Opusは**Sonnetより指示遵守が上**」（むしろSonnetがOpus 4.5を上回ったという公式記述あり）
- 「Opusは**一発でバグなく**組める」「Sonnetより**信頼性が高い**」（"bug-free"も対Sonnetの信頼性比較も無い）
- 「**パラメータが大きいから**質が高い」（規模→能力の因果は公式の主張ではない）

> **結局のところ：** 「凝ったもの・複雑なもの・一発勝負はOpus、定番・高速はSonnet」という体感的な使い分けは**実務的に妥当**で、Opusの最上位ティア位置づけという**公式の裏付けもある**。ただし「アーティファクトの質でOpus>Sonnet」を**Anthropicが直接比較で明言しているわけではない**——この一線を守って書くのが、公式準拠の技術記事として誠実。

---

## 参考（すべて公式ソース）

- [Models overview — Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Choosing a model — Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
- [What's new in Claude Opus 4.8 — Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8)
- [Pricing — Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/pricing)
- [Extended thinking — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
- [Prompting Claude Opus 4.8 — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8)
- [Share session output as artifacts — Claude Code Docs](https://code.claude.com/docs/en/artifacts)
- [Speed up responses with fast mode — Claude Code Docs](https://code.claude.com/docs/en/fast-mode)
- [Model configuration — Claude Code Docs](https://code.claude.com/docs/en/model-config)
- [Best practices for Claude Code — Claude Code Docs](https://code.claude.com/docs/en/best-practices)
- [What are artifacts and how do I use them? — Claude Help Center](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them)
- [Custom visuals in chat and Cowork — Claude Help Center](https://support.claude.com/en/articles/13979539-custom-visuals-in-chat-and-cowork)
- [Build and share AI-powered apps with Claude — claude.com blog](https://claude.com/blog/claude-powered-artifacts)
- [Improving frontend design through skills — claude.com blog](https://claude.com/blog/improving-frontend-design-through-skills)
- [Introducing Claude Opus 4.8 — anthropic.com](https://www.anthropic.com/news/claude-opus-4-8)
- [Introducing Claude Opus 4.7 — anthropic.com](https://www.anthropic.com/news/claude-opus-4-7)
- [Introducing Claude Opus 4.5 — anthropic.com](https://www.anthropic.com/news/claude-opus-4-5)
- [Introducing Claude Sonnet 4.6 — anthropic.com](https://www.anthropic.com/news/claude-sonnet-4-6)
- [Introducing Claude 4 — anthropic.com](https://www.anthropic.com/news/claude-4)

---

> _想定タグ：`Claude` `AI` `Anthropic` `生成AI` `アーティファクト`_
> _数値・仕様は2026年6月30日時点。Fast モードの対応モデルや価格はresearch preview ゆえ変動する可能性が高いので、公開前に公式ドキュメントの再確認を推奨。_
