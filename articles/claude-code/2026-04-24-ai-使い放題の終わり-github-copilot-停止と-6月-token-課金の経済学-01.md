---
id: "2026-04-24-ai-使い放題の終わり-github-copilot-停止と-6月-token-課金の経済学-01"
title: "「AI 使い放題」の終わり ― GitHub Copilot 停止と 6月 Token 課金の経済学"
url: "https://zenn.dev/yokoi_ai/articles/ai-2026-04-24"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-04-24"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

## 4月20日、ビュッフェの店主がドアを閉めた

2026年4月20日、月曜の朝。GitHub が `Copilot Pro / Pro+ / Student` の新規受付を止めた。翌 21 日の夕方、Anthropic が `claude.com/pricing` から Claude Code の Pro 欄を silent に外した。翌 22 日、Anthropic が「新規 2% の A/B テストやねん」と弁明して復帰した。**3日間で、業界のトップ2社が同じ結論にたどり着いて、片方は慌てて戻した**。

あんた、これ偶然やと思うか？ おっちゃんはそうは思えん。**"AI 使い放題" という一時代が、この週に終わった**。今日はその話や。派手な新機能発表やのうて、**料金表の書き換え**という地味な動きの奥に、何が埋まっとるかを掘る。長うなるで。コーヒー淹れて読んでな。

![図1: 2026-02〜06 業界タイムライン ― "AI 使い放題" 最期の3ヶ月](https://static.zenn.studio/user-upload/deployed-images/776170b30e5fe087ad390518.png?sha=2035b7160fc25cef985d63462f93b17512724e1b)

## 1. 何が起きたか ― 5日間の業界地殻変動

時系列で並べる。これだけ見ても「ただの偶然とちゃうな」と分かるはずや。

| 日付 | できごと | 誰が |
| --- | --- | --- |
| 2026-04-20（月） | GitHub Copilot Pro/Pro+/Student 新規受付停止 | Joe Binder（VP of Product, GitHub） |
| 2026-04-21（火 夕方） | Anthropic が `claude.com/pricing` から Claude Code の Pro 欄を silent 削除、docs も "Max-only" に書き換え | Anthropic（発表者なし） |
| 2026-04-22（水） | Anthropic が「新規 prosumer の 2% 向け A/B テスト」と弁明、Pro 欄復帰 | Amol Avasare（Head of Growth, Anthropic） |
| 2026-04-22（水） | Ed Zitron が Microsoft 内部文書リークを追加更新 ― **6月1日から全 Copilot 契約者を token-based billing へ移行** | Where's Your Ed At |
| 2026-04-23（木） | Neowin、Thurrott、BigGo が一斉追報。Business / Enterprise の pooled credits 額まで数字が出る | 複数メディア |
| 2026-04-24（金 発効） | GitHub Copilot の **interaction data 利用ポリシー改定**（Free/Pro/Pro+ は **デフォルト opt-in**、Business/Enterprise は対象外） | GitHub Blog |

5日や。たった5日の間に、**「使い放題モデルの終焉」と「token 課金への移行」と「データ学習ポリシーの改定」** という3つの地殻変動が、**同じ週に独立して発火した**。

これな、GitHub Copilot だけの話とちゃう。Anthropic もやった、Anthropic もやり返された、OpenAI Codex は既に token 連動に 4/2 で移行済み、Cursor は 2025-06 に先んじて同じ地雷を踏んでる（7月に公開謝罪）。**業界全体が、ほぼ同時に「定額制では支え切れん」と白旗を上げた**というのが、この5日間の正体や。

> ソース: [GitHub Community Discussion #192963](https://github.com/orgs/community/discussions/192963)、[The New Stack (2026-04-21)](https://thenewstack.io/github-copilot-signups-paused/)、[Where's Your Ed At (2026-04-23 更新)](https://www.wheresyoured.at/exclusive-microsoft-moving-all-github-copilot-subscribers-to-token-based-billing-in-june/)、[Neowin (2026-04-23)](https://www.neowin.net/news/report-github-copilot-is-moving-to-token-based-billing-from-june/)、[Simon Willison (2026-04-22)](https://simonwillison.net/2026/Apr/22/claude-code-confusion/)、[The Register (2026-04-22)](https://www.theregister.com/2026/04/22/anthropic_removes_claude_code_pro/)、[GitHub Blog: Interaction data policy update](https://github.blog/news-insights/company-news/updates-to-github-copilot-interaction-data-usage-policy/)

## 2. 6月1日から何が始まるのか ― 具体的な数字

Ed Zitron のリーク文書と Neowin / Thurrott / BigGo の追報で、**6月1日以降の料金体系**が数字付きで固まってきた。整理するで。

![図2: 6月1日以降の Copilot 料金体系 ― pooled credits から token へ](https://static.zenn.studio/user-upload/deployed-images/5d07c479b7b9b98b49d10c0f.png?sha=fbb9773d44b29bd02627f3a3452cc34b30bb101e)

### Business プラン（$19/月）

* **2026-06-01〜08-31**：プロモ期間。$19/月据え置き + **$30 分の pooled credits**（≒ $30 ぶん使える）
* **2026-09-01 以降**：$19/月据え置き + **$19 ぶんの tokens**（pooled credits から token 残高に切り替わる）

### Enterprise プラン（$39/月）

* **2026-06-01〜08-31**：プロモ期間。$39/月据え置き + **$70 分の pooled credits**
* **2026-09-01 以降**：$39/月据え置き + **$39 ぶんの tokens**

### 決定的な数字 ― **Copilot 側の request multiplier 7.5x（プロモ期間限定）**

ここ、読み違えやすいから丁寧にいくで。**7.5x というのは Copilot 側の request multiplier**や。具体的には、GitHub Copilot の premium request 制度で、**Claude Opus 4.7 を 1 リクエスト呼ぶと、Copilot の premium request 枠を 7.5 倍消費する**、という倍率設計になっとる。**2026-04-30 までの期間限定プロモ値**で、それ以降の扱いは未定や。

つまり、Pro プランの人が Opus 4.7 を重め（エージェント並列、長文 codebase 読み込み、Routines 系）で使うと、**Copilot 側の premium request 枠が 7.5 倍速で減る**。プラン上限の premium request 数が有限やから、**枠の消尽が早い**という話や。token 消費そのものが 7.5 倍になるわけではない——**あくまで Copilot の枠カウンタが 7.5 倍速**で回る、という意味。ここを混同せんでほしい。

4月22日に Anthropic が pricing ページで silent に抜こうとした動機も、同じ方向を向いとる。**Pro ($20) で Claude Code を並列多重実行されると、トークン原価が売値の何倍にもなる**。Microsoft（Copilot 側）と Anthropic（モデル側）が、同じ週に、同じ結論に独立到達した理由はここにある。片や **request multiplier** で枠消尽を早め、片や **tokenizer 更新** で実効単価を上げる。手口は違うが、狙いは同じ「**定額制のヘビーユーザーが垂れ流す赤字**」の抑制や。

> ソース: [Where's Your Ed At (2026-04-23 更新)](https://www.wheresyoured.at/exclusive-microsoft-moving-all-github-copilot-subscribers-to-token-based-billing-in-june/)、[Thurrott (2026-04-24)](https://www.thurrott.com/a-i/github-copilot/335125/report-microsoft-to-bring-token-based-billing-to-github-copilot)、[BigGo JP (2026-04-24)](https://biggo.jp/news/202604240351_GitHub_Copilot_Token_Billing_June_2026)

### 喩 ― ビュッフェの値段据え置きで「皿の枚数」に課金し始めた

平たく言うたらこうや。**月会費 $19 は据え置き、でも "食える皿数" に上限を付けた**。8月まではサービスで多めに皿を積む（pooled credits）。9月以降は月会費ぶんの皿しか出えへん。そのうえで、**Opus 4.7 を注文すると「チケット 7.5 枚ぶん」を一気に取られる**——これが Copilot の premium request multiplier 7.5x のイメージや（2026-04-30 までの期間限定プロモ）。寿司屋で言うたら、普通寿司 1 皿が 1 チケットで食えるとこ、特上ネタ（Opus 4.7）は **チケット 7.5 枚渡さんと出てこん**、みたいな話や。

客は気づく。「これ、実質値上げやんけ」。そのとおりや。**名目の月会費は変えず、中身を token 建てに置き換えた**ことで、**ヘビーユーザーから順に月額が跳ね上がる**構造が仕込まれとる。

## 3. なぜ起きたか ― 2023年の赤字試算が今も続いとる

「AI 使い放題は経済的に無理や」という事実、実は**2023年の時点で WSJ が書いとった**。3年前から分かっとる話が、今ようやく表面化してきただけや。

![図3: Agentic Workflow のコスト構造 ― ユーザー側 vs プロバイダ側](https://static.zenn.studio/user-upload/deployed-images/4d1963af64461b8d1530a3fb.png?sha=1bcf3869ab01a962a126b48b36c8cbb471836f93)

### 2023年10月、WSJ 記事の衝撃数字

当時、Microsoft は GitHub Copilot Individual を $10/月で売ってた。ところが **1 ユーザーあたりの原価は平均 $30/月**。つまり **1 人契約されるたびに $20 の赤字を垂れ流しとった**。重課金ユーザーは月 $80 の赤字、という試算まで出とる。

その後、Copilot は段階的に値上げして $19/月 になった。せやけど Ed Zitron の内部文書解説によると、**2026-01 以降、agentic workflow の普及で週次コストがほぼ倍増**。今の原価は **$60+/月**。売値 $19 に対して原価 $60、**1 人あたり月 $40 の赤字**や。

契約者が増えれば増えるほど赤字が膨らむ——**ビュッフェに客が来れば来るほど店主が泣く**というのが、ここ2年のクラウド AI 業界の実態や。

### 構造的に価格が上がる4つの要因

なぜ原価がここまで上がるか。4つ理由がある。

**1. agentic workflow（複数エージェント並列）の普及**  
4月14日に Anthropic が Claude Code Desktop の Mission Control を出した。Cursor 3 も並列エージェント前提の UI に切り替えた。Codex computer use も並列エージェント対応。**1 人のユーザーが同時に 4〜10 個のエージェントを走らせる**のが標準になった。これは「1人の客がビュッフェで同時に4皿並行摂取する」のと同じ話や。

**2. context の膨張**  
コードベースを丸ごと読ませる運用が普通になった。1 セッション 100K tokens が当たり前、重めなら 400K tokens。Claude の 1M tokens context も実用化しつつある。読み込むだけでもトークンは消費される。

**3. Opus 4.7 の「隠れ値上げ」（tokenizer 実効値上げ 1.0〜1.35x）**  
表示価格は Opus 4.6 から据え置き（$5/M input、$25/M output）。**ところが tokenizer が更新されて、同じ入力が 1.0〜1.35 倍の tokens として計算される**（最大 35% 増）。一次ソースは [Finout のブログ分析](https://www.finout.io/blog/claude-opus-4.7-pricing-the-real-cost-story-behind-the-unchanged-price-tag)で、名目単価を維持したまま tokenizer 側で実効単価を上げる、という手法が指摘されとる。ここで念押ししとくが、これは **前章で触れた Copilot の request multiplier 7.5x とは別軸の話**や。Copilot 側は「リクエスト 1 発で枠を 7.5 倍消費」、Anthropic 側は「同じ入力でトークン数が最大 35% 増」。**どちらもコスト増要因やけど、効き方は別物**。混ぜたらあかん。

**4. Cloudflare が指摘する container 限界**  
4月中旬の Cloudflare Agents Week で出た数字がエグい。「米国の知識労働者 1 億人 × 同時稼働率 15% = 2,400 万同時セッション。container ベースで回すと CPU が 50〜100 万個必要」。**今の container アーキテクチャでは agentic AI は経済的に成立しない**、というのが Cloudflare の主張や。Isolate（Cloudflare Workers の実行単位）なら 100 倍速・10〜100 倍メモリ効率、と。

4つ束ねると、**定額モデルが物理的に破綻する**のが見える。ビュッフェの食材原価が上がって、客が 4 皿並行で食って、レジでは月定額、という構造は、どこかで店じまいするしかない。

> ソース: [Cloudflare Blog: Agents Week in Review](https://blog.cloudflare.com/agents-week-in-review/)、[Finout: Claude Opus 4.7 Pricing — the real cost story](https://www.finout.io/blog/claude-opus-4.7-pricing-the-real-cost-story-behind-the-unchanged-price-tag)、[Where's Your Ed At: Four Horsemen](https://www.wheresyoured.at/four-horsemen-of-the-aipocalypse/)

### 転 ― 「AI の値段は下がり続ける」は、ここで止まった

ここで1つひっくり返すで。ずっと言われとった「AI の推論コストはムーアの法則で下がり続ける」「1 トークンの単価は毎年半減する」——**この楽観論は、2026年4月でいったん止まった**。

tokenizer 更新で体感値上げ、agentic 並列で消費量激増、context 膨張で 1 セッションあたりトークン量が 10 倍、規制（EU AI Act、データ保持）で原価上乗せ。**下げ圧よりも上げ圧のほうが強い**時期に入ったんや。

「値段下がるから、使い放題の定額プランで儲かる」というビジネスモデルは、もう成り立たん。だから 6月1日から token 課金に切り替える。**これは Microsoft の失敗やのうて、業界全体の前提が変わった**ということや。

## 4. 業界全体の地図 ― 誰がどの道を選んだか

Microsoft と Anthropic だけの話ちゃう。**2026年2月以降、AI コーディングツールの主要プレイヤー全員が、同じ方向に動いた**。

![図4: AI コーディングツール 料金マトリクス (2026-06 想定)](https://static.zenn.studio/user-upload/deployed-images/6b00897d5a579d398cbc1abb.png?sha=a6604405598fa14937b556b3a4be86afc4cb4d04)

### 先行事例：Cursor は 2025年6月に「謝罪」まで行った

Cursor は 2025年6月、`fixed requests` モデルから `usage credits` モデルに切り替えた。**案内が不十分やった**ため、**週 $350（≒月 $1,400）** の請求例が Hacker News で拡散。CEO **Michael Truell** が 2025年7月4日、公式ブログで公開謝罪し、遡及返金を実施した。

「料金変更は silent にやるな」という教訓を、Cursor が先に踏み抜いてくれた。**にもかかわらず**、2026年4月の Anthropic は同じことをやって炎上した。**1年前の他社の失敗を、自社は繰り返す**——業界の常や。

### 既に token 連動：OpenAI Codex（2026-04-02）

Codex は 2026年4月2日、per-message 課金から **API token 連動**に切り替え済み。Plus ($20)・Business・Enterprise はそれぞれ rate limit と burst 枠を持つが、重課金層は API 従量の形に寄せた。Codex lead の **Thibault Sottiaux** は 4月22日、Anthropic 炎上の夜に「Codex は Free と $20 Plus の両方で継続。**透明性と信頼という原則はぼくらは破らない**」と発信した。

### 最初から pure token：Cline / Aider

OSS 勢は元から pure token。Bring Your Own API Key（BYOAK）で、ユーザーが Anthropic / OpenAI / Google の API キーを貼り付けて、消費した分だけ払う。**Claude Sonnet 4.6 を Cline で重めに回すと $3〜8/時間**、Opus なら 5〜10 倍。1日8時間使えば $100〜$200、月 $2,000〜$4,000 のペースや。

これ、定額 $20/月の世界から見ると**眩暈がする数字**やけど、原価ベースではむしろこっちが「正しい値段」や。Microsoft も Anthropic も、**この原価を定額で吸収しようとして限界が来た**だけ。

### 3層マージン構造という罠

もう1つ、**SaaS 側が定額を維持できない構造的な理由**がある。Microsoft（Copilot 販売元）→ Anthropic / OpenAI（モデル提供）→ 推論インフラ（GPU / TPU）という**3層マージン構造**や。

Microsoft が $19/月で Copilot を売る。ユーザーが Claude Opus 4.7 を重めに呼ぶ。Microsoft は Anthropic に**原価ベースで token ごとに払う**。Anthropic は Google TPU / Broadcom / AWS に**さらに token ごとに払う**。**3層とも原価が token 連動**やのに、**一番上の売値だけ定額**——この構造が破綻するのは、時間の問題やった。

### Opus 4.7 の「名目据え置き・実効値上げ」

念押しで、Anthropic 側の値付けにも触れる。2025-12 リリースの Opus 4.7 は、**名目価格は 4.6 から据え置き**。$5/M input、$25/M output。

ところが、**tokenizer 更新で同じ入力が 1.0〜1.35 倍の tokens になる**（最大 35% 増、Finout 調べ）。数字を変えずに、実効値上げが実装された、ということや。これを相殺する救済として、Anthropic は **prompt caching（cache read $0.50/M、90% off）** と **Batch API（50% off）** を提供しとる。重課金ユーザーが「名目変わってないのにコストが上がっとる」と感じた理由は、ここにある。繰り返すが、これは **Copilot 側の 7.5x request multiplier とは別軸**の話や。混同して「Opus 4.7 は 7.5 倍値上げ」などと受け取らんでほしい。

> ソース: [OpenAI Codex rate card](https://help.openai.com/en/articles/20001106-codex-rate-card)、[TechCrunch (2025-07-07): Cursor apologizes for unclear pricing changes](https://techcrunch.com/2025/07/07/cursor-apologizes-for-unclear-pricing-changes-that-upset-users/)、[Finout: Claude Opus 4.7 Pricing](https://www.finout.io/blog/claude-opus-4.7-pricing-the-real-cost-story-behind-the-unchanged-price-tag)

## 5. 4/24 データ利用ポリシー改定 ― もう1つの伏線

token 課金の話に気を取られがちやけど、**同じ週に起きたもう1つの大事件**がある。2026年4月24日発効の、GitHub Copilot の **interaction data 利用ポリシー改定**や。

* **Free / Pro / Pro+**：**デフォルト opt-in**（設定 > Privacy で停止可）
* **Business / Enterprise**：**対象外**（明示除外）

収集される対象はこうや。

* 入出力
* コードスニペット
* カーソル周辺コンテキスト
* コメント
* ファイル名
* リポジトリ構造
* 操作ログ
* フィードバック

個人開発者・Pro 契約者は、**何も設定しなければ自動的にコードや操作ログがモデル学習に使われる**。この改定を、**料金体系の地殻変動と同じ週に**出してきた。

### 転 ― 「無料」の定義が変わった

ここで1つひっくり返す。「GitHub Copilot Free は無料やから安心」と思うやろ。**これ、もう成り立たん**。

Free ユーザーは、**月額ゼロ円**の代わりに、**自分のコードをモデルの教師データとして提供する**契約に、デフォルトで署名することになった。opt-out は設定画面の深いところにある（タブ3階層下）。**コードが通貨になった**んや。

これは何も GitHub だけやない。**AI 業界全体のデフォルト設計**がこっちに寄っとる。「無料で便利なツール」は、**「あんたのコードが訓練データ」という形で対価を取っとる**。Business / Enterprise が対象外なのは、**企業契約では法務が許さんから**や。逆に言えば、個人ユーザーには**法務のガードが無い**から、Opt-in default が通る。

あんた、自分のコードがモデルに吸われることに抵抗ある？ 抵抗あるなら、**4/24 以降、真っ先に Settings > Privacy を開く**んや。

> ソース: [GitHub Blog: Updates to GitHub Copilot Interaction Data Usage Policy](https://github.blog/news-insights/company-news/updates-to-github-copilot-interaction-data-usage-policy/)

## 6. 日本の現場はどう動くか ― 円安と仮想試算

ここからは日本の実務家目線や。おっちゃんが**日本の 40代社内SE**として、現場で何が起きるかを並べる。

![図5: 1,000人規模 SIer の Copilot 予算シナリオ (仮想試算)](https://static.zenn.studio/user-upload/deployed-images/b8a06373a28d5a966eccdf54.png?sha=0a6e8671f3029058609e57f3cd29ba20da18478b)

### 円安リスクが直撃する

これまでの **$20/月 定額プラン**は、**円安に対するヘッジ**として機能しとった。$20 が 2,200円でも 3,300円でも、「月額固定」という心理的ハードルが低かった。

ところが、**token 課金**になると話が変わる。「今月の請求は円建てで 8,700円」「重めに使ったら 23,000円」——**為替がそのまま月額に効く**ようになる。為替 150円から 165円に振れただけで、月額が 10% 上がる計算や。

**日本の会社で「AI コーディングツール予算」を組むとき、為替リスクの勘定が必須**になった。これまで財務は「月 $20 × 人数」で年予算を立ててた。これからは「月の平均 token 消費量 × 為替変動幅」を織り込む必要がある。

ITmedia AI+ が 2026年4月21日（執筆: 高橋史郎）に報じたのは、「Opus 全面削除で Pro ユーザーは **Claude Pro（¥3,178/月、≒$20）** への乗換が現実的」という日本の実務家目線の提案や。Anthropic の**日本向け定額サブスクリプション**は、**円建てで 3,178円/月**に設定されとる。ドル建て $20 と比較して、**為替変動を Anthropic 側で吸収する設計**や。

これ、実は業界にとって興味深い動きや。「定額崩壊」の流れの中で、**Anthropic が日本向けには円建て定額を維持**しとる。為替リスクを自社で吸収してでも、日本市場の個人ユーザー（Pro+ 利用量は Pro の 5倍という内部データあり）を確保したい、という戦略が見える。

### 1,000人規模 SIer の試算（仮想）

個別の日本企業名は出さへん。仮想の 1,000人規模 SIer を想定して試算するで。**これはあくまで "桁感" の議論**や。

**現行（2026年5月まで）**

* Copilot Business $19/月 × 1,000人 × 12ヶ月 = **年 $228K（≒ 年 3,420万円）**

**6月以降（token 連動）3シナリオ**

* **軽め**（補完中心、エージェント並列なし）：年 $240K（3,600万円）
* **中程度**（補完＋レビュー、Opus は控えめ）：年 $360K（5,400万円）
* **重め**（Opus 4.7 を日常的にエージェント並列）：年 $600K（9,000万円）

**中程度〜重めで、現行の 1.6〜2.6 倍**になる。為替が振れたらさらに上ぶれする。\*\*「これまで通りの運用を続けると、年予算が 1.5〜3 倍」\*\*が日本企業の現実や。

### 実務家が今週やるべき3つ

1. **token 消費量を測定する仕組みを作る**：いきなり「予算削減」と言う前に、**今誰が何にどれだけ token を使っとるか**を可視化する。GitHub Copilot なら organization の usage dashboard、Claude Code なら `/usage` コマンド。OpenAI は組織ダッシュボード。**データ無しで判断するな**。
2. **BYOAK（Bring Your Own API Key）運用を試す**：Cline / Aider / Continue.dev を社内で試験導入。API キーは会社で一元管理。ヘビーユーザー向けには pure token、ライトユーザー向けには定額、という **二層体制**が 2026 後半の現実解になる可能性が高い。
3. **情シス・法務と "データ利用ポリシー" を整理する**：4/24 発効の GitHub interaction data policy と同じ構造の改定が、他社でも来る。**どのプランが opt-in default で、どのプランが対象外か**を表にして、開発者に渡す。「気付いたらコードが学習に流れとった」事故を、法務に持ち込まれる前に防ぐ。

> ソース: [ITmedia AI+ (2026-04-21、執筆: 高橋史郎)](https://www.itmedia.co.jp/aiplus/articles/2604/21/news103.html)、[富士キメラ総研: 生成AI 国内市場予測](https://www.fuji-keizai.co.jp/press/detail.html?cid=24114)、[IDC Japan: AI インフラ支出 2026年 $5.5B](https://www.idc.com/resource-center/blog/7x-growth-in-just-three-years-japans-ai-infrastructure-will-surge-past-5-5-billion-in-2026-idc-reveals/)

### 市場の前提数字

参考までに、日本市場の周辺数字も置いとく。

* **富士キメラ総研**：生成AI 国内市場は **2028年度 1兆7,397億円（23年度比 12.3倍）** に成長予測
* **IDC Japan**：AI インフラ支出は **2026年 $5.5B（YoY +18%）**
* **Gartner**：2026年世界 AI 支出 **$2.5T**

**市場は伸びる、単価も上がる、為替も効く**。これが日本の 2026 後半の景色や。

## 7. おっちゃんの見立て ― 使い放題は楽しかったな

[再掲用なし／本文に続く]

ここから、おっちゃんの見立てや。3つだけ言わしてくれ。

### 1. 「値上げ」ではなく「料金設計の相転移」

「AI 開発が終わる」みたいな終末論は要らん。**終わってへん**。むしろ、**今まで異常に安かったものが、正しい値段に収斂しとる**というだけや。

水道と一緒や。水道が敷かれた直後は「基本料金だけで飲み放題」やった時代がある。使う人が増えて、水源が枯れかけて、**メーター課金**に移行した。今はそれが普通や。AI コーディングも同じフェーズに入った。**料金設計の相転移**——状態が根本から変わる瞬間や。

RPG で言うたら、これまで「経験値バー」だけ見とったのが、これからは **「MP 消費量」** も見ながら戦う必要が出た、みたいな UI 変化や。呪文一発打つたびに MP がゴリゴリ減る。強い呪文ほど MP が重い。Copilot の世界では、Opus 4.7 を唱えるとプラン側の **premium request チケットが 1 発で 7.5 枚**飛ぶ（プロモ期間中の設定）。**考えて打つ**時代になった、ということや。

### 2. 「日本だけが不利」やない ― 構造は全球共通

日本の円安リスクに触れたけど、「日本だけが AI 時代に取り残される」みたいなナショナル論調は避けたい。**円安は確かに効く、けど構造問題は全球共通**や。

ヨーロッパの開発者も、同じ token 課金で同じ悩みを抱える。ユーロも弱い局面がある。南米も東南アジアも、為替は振れる。**ドル建て token 課金は、全ての非ドル圏に同じ重力をかける**。

日本に有利な点もある。**品質重視の文化**や。「安いから雑に使う」より、**「必要なときに選んで使う」** 文化が、token 課金時代には相性がええ。ビュッフェで元を取ろうと 10 皿食うより、寿司屋でネタを選ぶ、みたいな節度。これは日本の開発現場が元々持っとる美徳や。

### 3. 使い放題は楽しかった、けど店が潰れたらビュッフェ自体が無くなる

最後に、これだけ言わせてくれ。

**AI コーディングの「定額使い放題」は、楽しかった**。月 $20 で GPT-4o も Claude Opus も Gemini も呼び放題。エージェントを 10 個並列で走らせて、コードベースをまるごと読ませて、1日数百回リクエストを投げる——これが $20 で収まってた 2025 年は、歴史に残る**狂った時代**や。

けどな、**店が赤字で潰れたら、ビュッフェ自体が無くなる**。Microsoft が赤字を吸収できんようになって、Anthropic が silent edit を試みて、Cursor が謝罪に追い込まれて、OpenAI が Codex を token 連動に戻した。**全員が「このまま続けたら店がもたん」と気づいた**。

6月1日から始まる token 課金は、**延命策**や。ユーザーにとっては実質値上げ、会社にとっては赤字縮小。どちらにも痛いけど、**「店を残す」ために必要な選択**や。

ビュッフェが恋しかったら、**ローカルLLM（Gemma 4、Llama、DeepSeek V4 系）** という選択肢もある。初期投資（GPU 付きマシン、モデル調整の学習コスト）は重いが、**継続コストはゼロに近い**。使い放題を続けたい人は、自分で店を開くしかない時代が来た、ということや。

### 問 ― あんたの会社の AI 予算、来月どうする？

あんたに問いを置いとく。

**あんたの会社の AI 予算、来月どうする？**

* 「従来通り Copilot Business $19/月 × 人数」で予算を立てたまま、6月1日を迎えるか？
* **token 消費量を可視化**して、中程度シナリオで予算を 1.6倍 に増やすか？
* BYOAK 運用に切り替えて、**個別の重課金ユーザー** を可視化するか？
* ローカル LLM への部分移行を検討するか？

決めるのは会長でも CTO でも経理でもない。**現場のあんた**や。5月のうちに試算を出して、6月1日以降の相転移に備える——これが、定額ビュッフェが終わった後の、**プロの作法**やで。

使い放題は楽しかったな。けどな、**値上げは延命策や**。延命された店で、何を注文するか、どう組み合わせるか——それを考える仕事が、これからは**実務家の腕の見せどころ**になる。

---

### 📎 編集後記 — おっちゃんの現場から

おっちゃんが普段回しとる日次の品質監査パイプラインは、Claude Code Opus 4.7 を使っとる。1 回の実行で context 込み **300K〜500K tokens** を読む。Opus 4.7 の tokenizer 実効値上げ（最大 1.35 倍、Finout 調べ）と、名目単価 $5/M input・$25/M output を素直に当てると、1 回あたりの原価は **素の Sonnet 比で 4〜5 倍のオーダー**になる計算や（なお、この数字は tokenizer 側の話であって、Copilot の request multiplier 7.5x とは別軸やで）。**Prompt caching を effective に使えば 90% off**、Batch API を組み合わせれば**さらに 50% off**——この2つを組み合わせんと、6月以降の token 課金時代は回らんな、というのが現場の手触りや。"使い放題感覚" で書いてたプロンプトを、cache-friendly に書き直す作業が、今月の宿題や。

---

*横井のAI日和 — AI の「今日のひとこと」をお届け。*
