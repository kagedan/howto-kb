---
id: "2026-04-22-料金表もまた-ui-やった-claude-design-と-pro-消失事件-01"
title: "料金表もまた UI やった ― Claude Design と Pro 消失事件"
url: "https://zenn.dev/yokoi_ai/articles/cc-2026-04-22"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

## 値上げが炎上したんちゃう、告知が炎上したんや

2026年4月21日の夜、Claude Code が Pro プラン（$20）から消えた。  
いや、正確にはこう言うべきや。**「消えたように見えた」んや**。

Hacker News のスレッドは12時間で462ポイント／446コメント（2026-04-22 朝時点。その後も伸び続け500点超）。r/ClaudeAI も X も大炎上。翌朝にはあの Simon Willison がブログで取り上げて、The Register も Ed Zitron も書いた。Anthropic の Head of Growth、Amol Avasare は X でこう弁明した。「新規 prosumer サインアップの約2%に対する small test やで。既存の Pro と Max の購読者には影響ない」。

せやけど、問題は値段ちゃう。**Anthropic がその週ずっと掲げてた「progressive transparency」というデザイン原則と、料金表を誰にも告げず書き換えた行為が、真正面から衝突した**ことや。

この記事はそういう話やねん。Pro プラン消失は「4月のあの1週間」の最後のピースに過ぎん。先週 Anthropic は Desktop アプリを全面刷新して（4/14）、Anthropic Labs から Claude Design という新プロダクトを出した（4/17）。Jenny Wen や Joel Lewenstein っていう Head of Design が、ポッドキャストやインタビューで craft と透明性を語り続けた一週間や。その週の最後に、料金表を silent edit した。

**その1週間を並べてみると、Anthropic というプロダクト組織の「デザイン」がどこで噛み合って、どこで外れてるかが見えてくるんや。**

ラーメン屋で言うたらこんな感じや。麺は最高級、スープは2年かけて開発、盛り付けは職人が盛る。せやけど **看板だけは店主が気分で書き換える**——黙って「二郎系、今月から無し」って貼り紙1枚出して、客が怒鳴り込んだら「あ、あれは2%の客にだけ出すテストです」言うてる。**麺の craft は本物**や。**せやけど客が信用するのは、看板まで含めた店の craft 全体**なんや。この記事はそういう話や。

![4月のあの1週間タイムライン](https://static.zenn.studio/user-upload/deployed-images/38066df63d9c4929fbf46f27.png?sha=7bd45603d55030f281363902761848b0589f7ce5)

---

## 1. 4月のあの1週間 ― 4つの出来事

整理するで。

* **4/14（月）** Claude Code Desktop 全面刷新発表。並列エージェント前提の UI、複数セッションを見渡す "Mission Control" 的サイドバー（呼称は著者の比喩。公式は「並列エージェント向け新サイドバー」）、Side chat、drag-and-drop ペイン。同日 GitHub に Issue #48158「dark mode regression」が Critical priority で立つ。
* **4/17（木）** Anthropic Labs が **Claude Design** を公開。`claude.ai/design` で利用可能。チャット＋ canvas の dual-pane で、codebase やデザインファイルを読み込んで design system を自動構築。Canva の Melanie Perkins 曰く「seamless」。
* **4/21（月夜）** `claude.com/pricing` が静かに更新され、Pro ($20) の Claude Code 欄が赤 ✕ に。Max 5x／Max 20x のみ ✓ になる。Reddit／HN／X で炎上。Amol Avasare が X で弁明、同夜に pricing ページは元に戻る。**ただし実験は継続**（2% の新規ユーザーには invisible に見えてない設定）。
* **4/22（火朝）** Simon Willison「Is Claude Code going to cost $100/month? Probably not—it's all very confusing」。The Register、Ed Zitron が追撃。OpenAI Codex lead の Thibault Sottiaux が「Codex は Free と $20 Plus の両方で継続。透明性と信頼という原則は破らない」と即座にカウンター（Simon Willison の記事経由での言及）。

この4つが **偶然並んだ1週間ではない**、というのがこの記事の仮説や。

---

## 2. 4月14日：開発者が「指揮者」に昇格した日

Desktop redesign の公式ブログの趣旨はこうや。**「agentic な開発のかたちが変わった。ひとつの prompt を打って待つ時代やない。複数のリポジトリをまたいで複数のタスクを同時に扱う時代になった。だから orchestrator（指揮者）のためのツールが要る」**——こういう主旨で、Mac / Windows 版のデスクトップが並列エージェント前提に刷新された。

平たく言うと、\*\*「開発者は実行者やなくなった、オーケストレーターになった」\*\*ということや。

新 UI の目玉を並べるで。

* **Mission Control 的サイドバー**：複数の active／recent セッションを status／project／environment でフィルタ・グルーピング。PR をマージ or close したらセッションが自動アーカイブ。
* **Side chat**（⌘+; / Ctrl+;）：メインスレッドに文脈を汚染させずに中断質問できる。
* **drag-and-drop ペイン配置**：terminal / preview / diff / chat を自分で組む。
* **Verbose / Normal / Summary の3段階ビュー**：Claude のツール呼び出しをどこまで可視化するかの透明度コントロール。**この3段階ビューがあとで効いてくる。記事の後半で戻るで**。
* **rebuilt diff viewer**（ただし unified のみ。Codex の split view には劣る）、HTML/PDF preview、local server preview、in-app file editor、built-in terminal。
* SSH on Mac（従来は Linux のみ）、plugin parity、Usage ボタン。
* 対象プラン：Pro / Max / Team / Enterprise + API。

![Mission Control 概念図](https://static.zenn.studio/user-upload/deployed-images/7d82b39bbfde0f2b14ed0c3f.png?sha=6f5d2e932a37ba58b8794f90e3d4bd6f759c9c4e)

これな、tmux とか iTerm でゴリゴリやってた人間には「懐かしい感覚」や。せやけど一般開発者にも **「1人では使い切れへん設計」** が来たのが重要なんや。

### 反応は真っ二つに割れた

**The New Stack は辛口**やった。見出しが「burn through tokens even faster」。並列化するっちゅうことは **4セッション × 100K context = 400K tokens** 消費する、っちゅう算数や。diff viewer が unified のみで Codex の split に負けてる点も突かれた。

**VentureBeat はエンタープライズ視点で好意的**。「Desktop GUI が管理・レビューの標準、CLI は実行の道具」という役割分担が見えてきた、lead developer が "Review and Ship" を一アプリで完結できる、と評価した。

**X の反応は地獄絵図**や。@claudeai の告知ツイートは数時間で25,000 likes。せやけど同じ時間帯に：

* @GraemeVIP：5時間分のクォータを **8分で焼いた**
* @finkrishna：4分で焼いた
* 他にも「最初の prompt でフリーズした」「並列化したら context を食い切る」という声が続々

これが4月14日の話や。この日の夜、GitHub に Issue #48158 が立つ。**dark mode regression**。solid black 背景に飽和した青 bubble で「clash」する、長文スレッドが読みにくい、と。reporter は「previous version に戻すオプションか、old/new の theme 切替を」と要望。ラベルは `priority: Critical`。

> **転**：Mission Control 風 UI で「オーケストレーター」に昇格した（と Anthropic が言う）デスクトップ。実際にユーザーが最初に気づいたんは **「dark mode が読めへん」** やった。

---

## 3. 4月17日：Claude Design ― Anthropic Labs の華

デスクトップ刷新の3日後、Anthropic は別の玉も出した。**Claude Design**。`claude.ai/design`。これ Claude Code の中の機能ちゃうで、**別プロダクト**や。Anthropic Labs という実験ブランドでのリリースや。

### 何ができるのか

* **チャット（左）＋ canvas（右）の dual-pane**。Claude Opus 4.7 の vision model ベース。
* **onboarding で design system を自動構築**：codebase・デザインファイル・スライドを読み込んで、色／タイポ／コンポーネントを抽出。
* 入力：text / 画像 / DOCX, PPTX, XLSX / codebase / web capture。
* 反復：chat / inline comment / direct edit / **custom slider**（デザインパラメータを自分でスライダー化できる）。
* 出力：ZIP / PDF / PPTX / Canva / standalone HTML / **Claude Code へのハンドオフバンドル**。
* 協業：Canva CEO **Melanie Perkins**「seamless for people to bring ideas and drafts from Claude Design into Canva」。

### 顧客証言

* **Olivia Xu (Brilliant)**：他ツールで 20+ prompts かかったものが 2 prompts で済んだ
* **Aneesh Kethini (Datadog)**：会議中に rough idea から動くプロトタイプまで

### 既知の limitations

* comment の永続化不具合
* compact view の save error
* 大規模 codebase でのハンドリング
* chat の散発的エラー

### HN の反応は「resounding meh」

ここは面白い論点が3つ出た。

**1. 均質化**（ljm）：AI 生成 UI は「glass effect と drop-shadow が Web 2.0 を覆ったのと同じ経路を辿る」。つまり **安っぽい均質化**。

**2. Middle market 問題**（p\_stuart82）：「cheap commodity と premium authorship に分断されて、**真ん中のプロ**が潰される」。AI デザインツールは安い方を劇的に安くする、一方でトップの craft には届かない、中間のデザイナーが仕事を失う。

**3. 反復不能性**（rustystump、現役デザイナー）：「初期出力は動くが、要件変更で破綻する。デザインの fundamentals が欠けている」。

擁護側も一定いた。「内製ツールに artisanal weirdness は不要」「標準 UI の認知負荷低減は高齢者・障害者にとって恩恵」。**craft vs art** 議論（josefrichter）も再燃した：「デザインは craft や。不要な artistic flourish は害」。

> **喩**：Claude Design は、**印刷機が発明された直後の美術学校**みたいなもんや。量産される版画が安くなって、職人がパニックする。せやけど版画そのものの質を最も厳しく見てたんは、他ならぬ版画職人やった。

---

## 4. Anthropic のデザイン哲学 ― Jenny Wen と Joel Lewenstein

ここが記事の核や。Anthropic のデザインチームが何を掲げてきたか、**誰の言葉で**、**どんな原則で**デザインしてきたかを並べる。これが4/21の pricing サイレント書き換えと照らし合わせたときに、自己矛盾として浮かび上がるからや。

![Anthropic のデザイン基盤](https://static.zenn.studio/user-upload/deployed-images/67630c4fd1789d33473cdff9.png?sha=b7fb35f01403f6bd7d24a14e89543f7b767dfeb6)

### Jenny Wen — Head of Design, Claude

経歴：Shopify → Square → Dropbox (Paper) → **Figma**（Director of Design、FigJam / Slides / Buzz / Sites CMS / Community を統率）→ 2025 年 Anthropic 入社。

Anthropic での出荷物を時系列で並べると：

* 2025-03：**Claude.ai visual refresh**（入社後「最初の仕事」として主導）
* 2025 初頭：**Claude Cowork** の product vision 設定、実装までコード寄与
* 2026-01：Claude Cowork 出荷
* 2026-03：**Dispatch**（非同期タスク実行機能）出荷

Jenny の語る Anthropic の体制はこうや。

> 「機能ごとに **1人のデザイナー × 1人のエンジニア**。従来の5〜10人のチームモデルやない。Dispatch のような機能も2人で出荷した」

そしてこれが彼女のデザイン原則や（Double Diamond インタビュー、Lenny's Newsletter ポッドキャストより）。3つだけ、この記事で主役になるやつを引く。

**1. Progressive transparency**  
**信頼と能力が上がるにつれ、裏の詳細を徐々に隠す**。長時間タスクは plan-approval UI で可視性を残す。**この原則がこの記事全体の主役や**。

**2. Craft as differentiator**  
「誰でもコードを出せる時代、差は execution と craft のみ」。

**3. Don't trust the process**  
「標準化された design process を疑う。craft / judgment / shipping に戻る」。

他にも Non-deterministic design（結果ではなく変数を設計する）、Designing for model trajectory（未来のモデルに先回り）、Joy（software を less boring に）など4つ。興味ある方は Double Diamond インタビュー本体を。

### Joel Lewenstein — Head of Product Design, Anthropic

こっちは全社横断の Head。Config 2025 登壇、Fast Company 特集、By Design ポッドキャスト、Dive Club Ep.77。個人サイト `joellewenstein.com` には「Software as LEGO」(2021)、"Where is the Killer App in Politics?"(2018) 等の寄稿が並ぶ。子供向け絵本も書いとる。

彼の語彙：

> 「Claude は **sparring partner**。発話を verbatim で受け取るな、押し返せ」
>
> 「curious / transparent / open-minded / non-judgmental / non-simplistic / non-reductive」—— これを Claude の character として訓練する
>
> 「creative partner が immediately useful, meaningful, joyful であること」
>
> 「friction が creativity を育てる」
>
> 「you are not a slavish executor of my vision. We are coproducing this outcome together」
>
> 「volcano の上でプロダクトを作るような感覚」—— 基盤モデルが常に動く前提

Anthropic のブランドトーンを要約するとこうや：**warmth（温かさ）、human-centered mission、technical craft、helpful/harmless/honest**。

### Geist と書体と色

ブランドアイデンティティを2.5年かけて作ったのは **Geist** というエージェンシーや。共同創業者 Jack Clark はこう言うとる：「Geist were instrumental in helping us define our brand identity」。

* **ロゴ**：純粋なタイポグラフィック＋「スラッシュ」1点だけ。スラッシュは「AI の裏にあるコードと、これから来る未来」を指す。
* **書体**：**Styrene**（Commercial Type）の sans ＋ **Tiempos**（Klim Type Foundry）の serif。type.today や Dear Designer Substack で絶賛されとる。"technically refined and charmingly quirky"。
* **カラー**：温かい rust-orange（代表値 **#C15F3C**。Mobbin 等の第三者デザイン DB では "Crail" と命名されているが、Anthropic 公式のブランドガイドでこの名を使っているかは未確認）、周辺で #C4A584 や #AE5630。背景はクリーム／ベージュ／オフホワイト。
* **意図**：warmth を出して marketing と product UI の両立。ChatGPT のモノクロ hexagonal knot、Gemini の虹、Grok のエッジと対照的に「落ち着き・学術・信頼」。

> 「Claude」という名前自体が、情報理論の父 **Claude Shannon** へのオマージュ。モデル名 Opus / Sonnet / Haiku は文学的で優雅。ただし Medium の Dia Lohg は「pastel は unserious」「hand-drawn illustrations は juvenile」「**Duolingo と Notion の赤子**」「Anthropic の研究トーンと Claude の文学的トーンの命名ズレ」と辛辣に批評しとる。

---

## 5. Progressive Transparency の具体 ― 3段階ビュー

ここで Desktop redesign の話に戻るで。4/14 の Mission Control には **Verbose / Normal / Summary の3段階ビュー**があった、と書いた。これ Jenny Wen が言う **progressive transparency** の UI 実装や。

![progressive transparency の3段階](https://static.zenn.studio/user-upload/deployed-images/ec2e2eeb4e4b28f09c950a0f.png?sha=68e66e705b72707d04262b856e0a7f53fd746638)

* **Verbose**：Claude の全ツール呼び出しを表示。デバッグ向け。
* **Normal**：主要な判断だけ表示。daily use。
* **Summary**：結果だけ表示。信頼できる routine 用。

**信頼と能力が上がるにつれ、裏の詳細を徐々に隠していく**。言うてみれば、最初は車の下を覗きながら運転してた人間が、徐々にダッシュボードだけ見るようになり、最終的には窓の外だけ見て運転する、みたいな構造や。**これはエレガントな原則や**。車の信頼を段階的に積み上げる UI 設計。

せやけどな、**料金体系にはこの原則が適用されてへんかった**。それが4/21に噴火するんや。

---

## 6. 4月21日：Pro プラン消失事件 ― pricing ページもまた UI やった

時系列を分単位で追う。

* **04-21 朝〜昼** `claude.com/pricing` が静かに更新される。Pro ($20) の Claude Code 欄が **赤 ✕**。Max 5x（$100/月）と Max 20x のみ ✓。サポート記事タイトルも "Using Claude Code with your Pro or Max plan" から "...with your Max plan" に書き換え。
* **04-21 午後** Reddit r/ClaudeAI と HN で爆発。HN 本スレ（id=47854477）が12時間で 462ポイント／446コメント（2026-04-22 朝時点、その後も伸びて500点超）。重複スレ（id=47855565）が263ポイント。
* **04-21 夜** **Amol Avasare**（Anthropic Head of Growth）が X で反応。
  > 「For clarity, we're running a small test on ~2% of new prosumer signups. Existing Pro and Max subscribers aren't affected.」  
  > 「Will hear it from us, not a screenshot on X or Reddit.」
* **同時刻** **Thibault Sottiaux**（OpenAI Codex lead）が即マウント返し（Simon Willison 記事経由で報じられた趣旨）。
  > 「Codex は Free と $20 Plus の両方で提供を続ける。**透明性と信頼。この2つの原則はぼくらは破らない**」
* **04-21 夜〜22 未明** pricing ページは元に戻る。**ただし実験は継続**（対象 2% には invisible に異なる料金体系が見えてる）。
* **04-22 朝** Simon Willison がブログでタイムライン整理。「Is Claude Code going to cost $100/month? Probably not—it's all very confusing」。Internet Archive で差分を検証。The Register、Ed Zitron（wheresyoured.at）が追撃。

![pricing ページの差分](https://static.zenn.studio/user-upload/deployed-images/d5cbdf35d49d62dbf209f50d.png?sha=8470487c1962e2d02fdaae82aec535c5f20eb8dc)

### Amol の弁明の逐語分析

**「~2% of new prosumer signups」** という表現。これな、**被験者が知らずに参加する A/B テストの定義そのもの**や。せやけど：

**1. pricing ページは全員に見える**  
2% にしか適用されへん料金を、**公開 HTML で全員に見せた**。これは A/B テストやなくて、**公開発表を間違ってやった**のと同じ効果や。

**2. サポート記事のタイトルも書き換わった**  
pricing だけやなく、サポートのタイトルが "Using Claude Code with your Pro or Max plan" から "...with your Max plan" に変わってた。**これはドキュメントの変更**や。ドキュメントは被験者 2% にだけ表示するような仕組みがない。**つまり 100% の既存ユーザーが、自分の契約が変わったかのような表示を見た**。

**3. 既存 Pro 契約者への影響なし、と言うが**  
「既存は影響なし」と Amol は言うた。せやけど、**次の更新タイミング**は？**このテストの結論が出たら**？これが明示されてへん時点で、既存ユーザーも不安になる。progressive transparency なら、少なくとも「この実験は○日で終了、結論が出たら email 告知する」まで言語化すべきやった。

### Simon Willison の冷静な総括

Willison は Internet Archive を使って pricing ページの snapshot を撮り、差分をブログに貼った。彼の結論はこうや。

> 「教材として Codex の方が長期的に安全。学生や教育者にとって、料金プランが silent に変わるツールは授業に組み込めない」

**これが Anthropic のブランド原則「honest」と衝突する**。craft／warmth／transparent を掲げる会社が、料金ページを黙って書き換え、サポート記事も書き換え、炎上してから「テストやねん」と後出しした。

---

## 7. 自己矛盾の構造 ― 原則が守られんかった場所

ここが記事の肝や。整理するで。

![デザイン原則 vs 実行のズレ](https://static.zenn.studio/user-upload/deployed-images/defd48e1c20f872044f1b70a.png?sha=50ba403b1b4837d1b852bfcd4ef90c4ef91af9eb)

| 原則（デザインチームが掲げる） | 4/21 の実行 |
| --- | --- |
| Progressive transparency | pricing ページを silent edit |
| Honest（ブランド原則） | 弁明は HN 炎上後の X 投稿のみ |
| Don't trust the process | A/B テストの process だけは信じて、公開ページに出した |

**pricing ページそのものがデザイン成果物**や、というのがここでの主張や。

`claude.com/pricing` は **UI** や。書体は Styrene や。色は rust-orange や。チェックマーク ✓ と ✕ は視覚記号や。**この UI を edit するのは design の仕事**なんや。そして design チームは progressive transparency を掲げとる。

つまり、**Anthropic のデザインチームは原則を守ったが、pricing チームは守らんかった**——あるいは、**組織として「design principle は UI にだけ適用し、pricing UI は除外される」という暗黙の仕切りがあった**。どっちにしても、**progressive transparency は craft／warmth／honest と並ぶ横断原則として機能してへんかった**、ということや。

Ed Zitron（Where's Your Ed At）の論調を要約するとこうや。**Anthropic は借入頼みの "無限タダ券エコノミー" でユーザーを囲い込んできた、そして今、最初のハシゴを外した**——。トークン原価が売値の何倍にもなる Pro 層で Claude Code 並列実行されると赤字が爆発する、だから削るしかなかった、という **経済合理性**は分かる。せやけど、**デザイン原則と経済合理性が衝突したときに、経済合理性を silent に優先した**——それが progressive transparency との矛盾や。

### 重なりが示す、プロダクト組織の「三面鏡」

この1週間を並べると、見えてくる構造がある。

* **4/14 Desktop Redesign**（豪華化）— craft の強調、parallel agent 体験、dark mode regression は後に回る
* **4/17 Claude Design**（Labs の華）— design system 自動構築、Canva 連携、エコシステム拡張
* **4/21 Pro 抜き**（炎上）— pricing UI の silent edit、progressive transparency 原則との衝突
* **4/22 rollback** — 既存ユーザーに見える pricing は戻ったが、実験は継続

**この4つが同じ週に起きたのは偶然やない**と仮説してええと思う。プロダクト戦略の軸が「エンタープライズ／オーケストレーション」側に寄ってる。Desktop redesign は Mission Control UI でそれを表現した。Claude Design も Canva 連携で B2B を強化した。Pro ($20) で Claude Code を並列多重実行されると構造的にトークン赤字が爆発する、という経済合理性が、pricing の sneaky edit を引き起こした。**全部繋がっとる**。

繋がっとることそのものは悪やない。**組織として整合性を取るなら、progressive transparency は pricing ページにも適用されるべきやった**——つまり、段階的に「Pro で Claude Code は今後 Max にシフトする可能性があります。検討期間を設けます」と告知してから、実際の変更を行うべきやった。それが **principle を守る**ということや。

> **転**：Anthropic は「progressive transparency」をデザイン原則として語り続けた。その同じ週に、pricing ページは **regressive opacity（段階的不透明）** で動いた。

---

## 8. おっちゃんの見立て

整理したうえで、3つだけ言わしてくれ。

### 1. 値上げは「構造」やった、告知は「判断」やった

The Register と Ed Zitron が指摘した通り、Pro $20 のトークン原価は売値の 1/10 を切っとる、という分析は複数のソースが一致しとる。Desktop redesign の parallel session と Routines（4/14 同時発表）は **構造的にトークン消費を増やす**。Pro 層で Claude Code を野放しにしたら、Anthropic は赤字で潰れる。

**これは経営判断として完全に理解できる**。責められるべきは「値段を変えたこと」やない。**変え方を判断した人間**や。silent edit を「small test」と呼んで、公開 pricing ページと公開サポート記事まで書き換えた人間が、**progressive transparency を掲げる会社の価値観を、その瞬間に捨てた**。

### 2. craft は product team 全体のもんや

Jenny Wen は「craft が最後の差別化要因」と言うた。Joel Lewenstein は「sparring partner」と言うた。Geist は2.5年かけてブランドを作った。**全部正しい**。Styrene と Tiempos と rust-orange は美しい。Desktop redesign の Mission Control も、Claude Design の dual-pane も、職人の仕事や。

せやけど、**pricing ページの ✕ と ✓ も同じく職人の仕事**なんや。そこに craft がないということは、**design 原則を守る範囲が product UI に限られてる**、ということや。これは **組織設計の問題**や。デザインチームは powerful やけど、pricing チームまで届いてへんかった。

冒頭でラーメン屋の喩えを出したんを、もう一度呼び出しとく。麺は最高級、スープは2年開発、盛り付けは職人。**看板だけは店主が気分で書き換える**——これが今の Anthropic や。craft のある場所と、ない場所が、組織の中で線引きされとる。

### 3. transparency は原則ちゃう、筋肉や

progressive transparency は「言うて書いたらOK」やない、**毎日の判断で肉体化せなアカン**。4/21 の夜、Anthropic の中で「この pricing 変更、告知どうする？」っちゅう会話があったはずや。そこで誰かが「progressive transparency の原則どうする？」と言うべきやった。言わんかったんか、言うたけど却下されたんか、そもそもその会話が無かったんか。**どれかや**。

そして重要なんは、**Thibault Sottiaux がすかさず「透明性と信頼、この2つの原則をぼくらは破らない」と発信したこと**（Simon Willison 記事経由で報じられた趣旨）や。競合の OpenAI から、**同じ「transparency」という単語で打ち返された**。これは偶然やないで。**progressive transparency を掲げた会社に、transparency and trust で打ち返した**。Anthropic が掲げた原則が、**Anthropic を最も傷つける武器として外に飛んだ**瞬間や。

---

## 9. 読者への実践ガイド ― あんたは何をするか

Pro 契約中やなかったとしても、この事件は **AI コーディングツール選びに影響する**。整理しよう。

![選択フロー](https://static.zenn.studio/user-upload/deployed-images/ac6343080c1649c4b46e552e.png?sha=682d2f73972f908b1f8052cbbcb0819ee67cf873)

### あんたが Pro 契約者やったら

* **継続する場合**：当面影響なし。せやけど次の更新タイミング（年次 or 月次）で何が変わるかは読めない。**Anthropic の公式告知を Twitter ではなく email で待つ**ことを、まず自分に約束するんや。
* **Max 5x に昇格**：$100/月。Claude Code を並列運用・Routines を5本/日以上使うなら、経済合理性はある。Routines 単独で考えると dev machine 要らずが強い。
* **乗り換え候補**：
  + **OpenAI Codex**（Free / $20 Plus で継続、Sottiaux の言質あり）
  + **Cursor**（agent-first UI、月額 $20、ただし別の value proposition）
  + **Cline / Aider / local LLM**（ローカルモデル、初期コストは重いが継続コストゼロ）

### あんたが水曜公開の教材／チュートリアル作者やったら

Simon Willison の懸念がここに効く。「料金プランが silent に変わるツールは授業に組み込めない」。**長期教材**（1年以上使う前提）なら、**Codex か local LLM のほうが安全**や。Claude Code は **四半期 or 半年単位で内容を見直せる教材**に向いとる。

### あんたがチームで Claude Code を運用するなら

3つ考えるで。

1. **`/ultrareview` を重要 PR 限定で使う**：無料3回（2026-05-05 失効）の間に feel を掴む。1回 $5〜$20 なので月4〜8回で $20〜$160。「間違えたら巻き戻しコストが高い PR」（本番デプロイ前、DBスキーマ変更、認証系の書き換え等）限定で運用すると、費用対効果が読みやすい。
2. **Routines を日次メンテ系タスクに充てる**：Pro 5本/日、Max 15本/日の枠で、ナレッジDBの重複排除・インデックス更新・日次の品質チェックログ生成など、ルーチン化できる仕事を向こう側に移譲する。**ローカルで回してる `/loop` との棲み分け設計**が先に要る。
3. **pricing の silent edit を「組織のアンチパターン」として記録**：チームの wiki に「UI edit もコミュニケーションの一部」という原則を一行足しとくだけでええ。料金変更・権限変更・名称変更など、**視覚的な情報変更はすべて告知対象**、というルールを持つ。Anthropic の 4/21 が、他人事やなくて社内の参照事例になる瞬間や。

---

## 締め ― あんたなら、次の透明性を誰に預ける？

4月のあの1週間、Anthropic は「デザインの会社」になろうとしてた。Styrene の書体、rust-orange、progressive transparency、craft、Joy。全部美しい原則や。Jenny Wen も Joel Lewenstein も Geist も本物の craft を持っとる。**Desktop redesign も Claude Design も、その craft の結晶**や。

せやけど、pricing ページもまた UI なんや。**craft が pricing まで届かんかったことが、この週の最大の発見**や。

Thibault Sottiaux が Anthropic に向けて「transparency and trust」と打ち返した夜、**Anthropic は自分の原則が敵の武器になる瞬間を見た**。これを組織として学ぶか、それともそのまま流すかで、次の1年の Anthropic の信頼残高が決まる。

**信じとる原則は、それを掲げた会社に守らせるのが、最後はユーザーの仕事**なんや。炎上は、その意思表示のひとつや。

あんたは、次の透明性を、誰に預ける？

---

### 参考リンク

**一次情報**

**レビューと分析**

**デザイナー・チーム**

**ブランドとタイポ**

**コミュニティ反応**

---

*横井のAI日和 — AI の「今日のひとこと」をお届け。*
