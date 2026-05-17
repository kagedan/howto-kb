---
id: "2026-05-17-claude-for-small-business-と-claude-for-legal-を公式ソー-01"
title: "Claude for Small Business と Claude for Legal を公式ソース基準で分解する"
url: "https://qiita.com/daisuke-nagata/items/9284eac8ce590778bb1e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "GPT"]
date_published: "2026-05-17"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

<div style="background: #0a0a0a; color: #ffffff; padding: 24px; border-radius: 12px; margin: 24px 0;">
<div style="font-size: 13px; color: #8b949e; letter-spacing: 0.1em; margin-bottom: 6px;">VISUAL SUMMARY — 別ページ</div>
<div style="font-size: 22px; font-weight: bold; line-height: 1.4; margin-bottom: 12px;">先に「1ページサマリ」を読む</div>
<div style="font-size: 14px; color: #c9d1d9; line-height: 1.7; margin-bottom: 16px;">
本記事の内容を視覚的にまとめた1ページHTMLを用意した。Before/After比較・3つのすごい点・両製品スペック・公式未公開事項まで、スクロール1回で全部見える形に整理してある。<br/>
時間ない人はこっち先に開けば全体像がつかめる。
</div>
<a href="https://htmlpreview.github.io/?https://gist.githubusercontent.com/foolish1023/e0526128ca0426c17854420b394cbfd3/raw/535bea1c63a2f56efb8aaa608e000e7b49d5ffdb/index.html" style="display: inline-block; background: #ffffff; color: #0a0a0a; padding: 12px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 14px;">→ ビジュアル版を開く</a>
</div>

<div style="background: #0a0a0a; color: #ffffff; padding: 32px 24px; border-radius: 12px; margin: 24px 0;">
<div style="font-size: 13px; color: #8b949e; letter-spacing: 0.1em; margin-bottom: 8px;">2026-05-12 / 2026-05-13 ANTHROPIC ANNOUNCEMENT</div>
<div style="font-size: 28px; font-weight: bold; line-height: 1.4; margin-bottom: 12px;">AIが社内ツールに直接アクセスして<br/>業務の下書きまで自動で作る</div>
<div style="font-size: 16px; color: #c9d1d9; line-height: 1.7;">Claude for Legal（法務）と Claude for Small Business（中小企業）の2本。普通のChatGPT/Claudeが「賢いコメント役」止まりだったのに対し、QuickBooks・Ironclad・DocuSign等に直接繋がって動く。<br/><b style="color: #ffffff;">送信・支払い・署名の前は必ず人間が承認</b>する設計。</div>
</div>

<table style="width: 100%; border-collapse: separate; border-spacing: 12px 0; margin: 24px 0;">
<tr>
<td style="width: 50%; background: #fff6f6; border: 2px solid #cf222e; border-radius: 10px; padding: 20px; vertical-align: top;">
<div style="font-size: 12px; color: #cf222e; font-weight: bold; letter-spacing: 0.1em;">BEFORE</div>
<div style="font-size: 20px; font-weight: bold; color: #0a0a0a; margin: 6px 0 12px 0;">従来のAI</div>
<div style="font-size: 14px; color: #444; line-height: 1.7;">
人間が社内ツールからデータをコピー<br/>
→ AIに貼り付ける<br/>
→ AIが返したテキストを社内ツールに戻す<br/>
<b style="color: #cf222e;">前後工程は全部人間が担当</b>
</div>
</td>
<td style="width: 50%; background: #f0f9f0; border: 2px solid #1a7f37; border-radius: 10px; padding: 20px; vertical-align: top;">
<div style="font-size: 12px; color: #1a7f37; font-weight: bold; letter-spacing: 0.1em;">AFTER</div>
<div style="font-size: 20px; font-weight: bold; color: #0a0a0a; margin: 6px 0 12px 0;">Claude for Legal / Small Business</div>
<div style="font-size: 14px; color: #444; line-height: 1.7;">
人間: 業務を一言で依頼<br/>
→ AI: MCPコネクタでツールから取得・下書き作成<br/>
→ 人間: 承認するだけ<br/>
<b style="color: #1a7f37;">AIが業務を実行する側に回る</b>
</div>
</td>
</tr>
</table>

<table style="width: 100%; border-collapse: separate; border-spacing: 10px 0; margin: 16px 0;">
<tr>
<td style="width: 33%; background: #ddf4ff; border: 1px solid #0969da; border-radius: 10px; padding: 18px; vertical-align: top;">
<div style="font-size: 36px; font-weight: bold; color: #0969da;">01</div>
<div style="font-size: 16px; font-weight: bold; color: #0a0a0a; margin: 4px 0 10px 0;">社内ツールに入り込む</div>
<div style="font-size: 13px; color: #444; line-height: 1.6;">MCP（Anthropic提案・Linux Foundation管理のオープン標準）で20以上のSaaSに繋がる</div>
</td>
<td style="width: 33%; background: #dafbe1; border: 1px solid #1a7f37; border-radius: 10px; padding: 18px; vertical-align: top;">
<div style="font-size: 36px; font-weight: bold; color: #1a7f37;">02</div>
<div style="font-size: 16px; font-weight: bold; color: #0a0a0a; margin: 4px 0 10px 0;">「うちの流儀」を覚える</div>
<div style="font-size: 13px; color: #444; line-height: 1.6;">初回 cold-start interview (10-20分) で playbook を聞き、CLAUDE.md に保存。全Skillが参照する</div>
</td>
<td style="width: 33%; background: #fbefff; border: 1px solid #8250df; border-radius: 10px; padding: 18px; vertical-align: top;">
<div style="font-size: 36px; font-weight: bold; color: #8250df;">03</div>
<div style="font-size: 16px; font-weight: bold; color: #0a0a0a; margin: 4px 0 10px 0;">業務単位のAIが大量に</div>
<div style="font-size: 13px; color: #444; line-height: 1.6;">Legal: 86 Skill/Agent (GitHub公開リポで計数) / Small Business: 15ワークフロー</div>
</td>
</tr>
</table>

<table style="width: 100%; border-collapse: separate; border-spacing: 10px 0; margin: 16px 0;">
<tr>
<td style="width: 50%; background: #ffffff; border: 1px solid #0969da; border-radius: 10px; padding: 20px; vertical-align: top;">
<div style="font-size: 12px; color: #0969da; font-weight: bold; letter-spacing: 0.1em;">CLAUDE FOR LEGAL</div>
<div style="font-size: 18px; font-weight: bold; color: #0a0a0a; margin: 4px 0 12px 0;">法務・法律事務所向け</div>
<table style="width: 100%; font-size: 13px;">
<tr><td style="padding: 4px 0; color: #6e7681; width: 50%;">プラグイン</td><td style="padding: 4px 0; color: #0a0a0a;"><b>13個</b></td></tr>
<tr><td style="padding: 4px 0; color: #6e7681;">Skill/Agent</td><td style="padding: 4px 0; color: #0a0a0a;"><b>86個</b> (GitHub計数)</td></tr>
<tr><td style="padding: 4px 0; color: #6e7681;">MCPコネクタ</td><td style="padding: 4px 0; color: #0a0a0a;"><b>20以上</b></td></tr>
<tr><td style="padding: 4px 0; color: #6e7681;">採用先</td><td style="padding: 4px 0; color: #0a0a0a;">Freshfields, Holland &amp; Knight 等</td></tr>
<tr><td style="padding: 4px 0; color: #6e7681;">ライセンス</td><td style="padding: 4px 0; color: #0a0a0a;">Apache 2.0 (公開)</td></tr>
</table>
</td>
<td style="width: 50%; background: #ffffff; border: 1px solid #1a7f37; border-radius: 10px; padding: 20px; vertical-align: top;">
<div style="font-size: 12px; color: #1a7f37; font-weight: bold; letter-spacing: 0.1em;">CLAUDE FOR SMALL BUSINESS</div>
<div style="font-size: 18px; font-weight: bold; color: #0a0a0a; margin: 4px 0 12px 0;">中小企業向け</div>
<table style="width: 100%; font-size: 13px;">
<tr><td style="padding: 4px 0; color: #6e7681; width: 50%;">ワークフロー</td><td style="padding: 4px 0; color: #0a0a0a;"><b>15個</b></td></tr>
<tr><td style="padding: 4px 0; color: #6e7681;">主要接続SaaS</td><td style="padding: 4px 0; color: #0a0a0a;">QuickBooks, PayPal, HubSpot 他</td></tr>
<tr><td style="padding: 4px 0; color: #6e7681;">採用顧客</td><td style="padding: 4px 0; color: #0a0a0a;">Purity Coffee, Simple Modern 他</td></tr>
<tr><td style="padding: 4px 0; color: #6e7681;">同時提供</td><td style="padding: 4px 0; color: #0a0a0a;">無料講座 + 全米10都市ツアー</td></tr>
<tr><td style="padding: 4px 0; color: #6e7681;">開始</td><td style="padding: 4px 0; color: #0a0a0a;">2026-05-14 (Chicago)</td></tr>
</table>
</td>
</tr>
</table>

<div style="background: #fff8c5; border-left: 6px solid #bf8700; padding: 16px 20px; margin: 24px 0; border-radius: 4px;">
<div style="font-size: 14px; font-weight: bold; color: #6f4e00; margin-bottom: 6px;">公式が言っていないこと（2026-05-17時点）</div>
<div style="font-size: 13px; color: #0a0a0a; line-height: 1.7;">
価格・課金体系（Cowork内包かどうかも未明示） / 日本リージョン提供・日本語UI / 業務削減時間の具体数値 / cold-start interview で聞かれる項目の詳細<br/>
<span style="color: #6e7681;">本記事は推測で埋めず、これらは「未公開」と明記している</span>
</div>
</div>

<details>
<summary><b>本記事の検証方針（クリックで展開）</b></summary>

本記事の数値・名称はすべて以下の一次ソースで裏取りしている。

- Anthropic公式blog (`claude-for-small-business`, `claude-for-the-legal-industry`)
- GitHub公開リポ `anthropics/claude-for-legal` (Apache 2.0)
- Claude製品ページ `claude.com/solutions/small-business`

業務時間削減量・価格・playbook内容など、**公式が言っていないものは「未公開」と明記**している。

</details>

**Anthropicが2026-05に出した「Claude for Legal」「Claude for Small Business」を、Anthropic公式blogとGitHub公開リポ (`anthropics/claude-for-legal`, Apache 2.0) のみを一次ソースに分解する。**

**結論を先に: これは「ChatGPTみたいなAIチャット」ではない。社内ツール（QuickBooks・Ironclad・DocuSign等）にAIが直接アクセスして、契約レビューや月次決算のような業務を「下書きまで自動 → 人間が承認」までやるパッケージ**。

**価格・日本対応・業務時間の削減量は2026-05-17時点で公式に明示されていない。本記事の数字や名称は全て公式blogとGitHub公開リポに直接当たって裏取りしている。**

## この記事でわかること

- Claude for Small Business / Claude for Legal が**公式に何を提供すると言っているか**（推測ではなく一次ソースで）
- 普通のChatGPT/Claudeと比べて**何が違うのか**
- AI初心者でも理解できるレベルでの**仕組みの説明**（MCP / Plugin / CLAUDE.md）
- 試したい人向けの**確認できる事実と未確定事項の切り分け**

## 対象読者

- AIをチャットでは使うけど、業務に組み込むイメージが湧かない人
- 法律事務所・経理・人事・営業の人で、AIに業務を任せたい人
- Claude / ChatGPT は知ってるけど、「Cowork」「MCP」と言われるとフワッとする人
- SaaSプロダクトを作っていて、自社製品がAIと繋がる未来を考えている人

## 目次

- [まず、いまのAIの限界の話](#まずいまのaiの限界の話)
- [Claude for Legal は具体的に何をやってくれるのか](#claude-for-legal-は具体的に何をやってくれるのか)
- [Claude for Small Business は具体的に何をやってくれるのか](#claude-for-small-business-は具体的に何をやってくれるのか)
- [何がすごいのか・3つのポイント](#何がすごいのか3つのポイント)
- [仕組みをやさしく解説](#仕組みをやさしく解説)
- [公式が言っていること / 言っていないことの切り分け](#公式が言っていること--言っていないことの切り分け)
- [日本で使うときの注意点](#日本で使うときの注意点)
- [今日から自分が動けること](#今日から自分が動けること)
- [まとめ](#まとめ)

---

## まず、いまのAIの限界の話

このセクションで得られること: 「なぜこれが必要だったか」がわかる。

ChatGPTでもClaudeでも、業務で使おうとすると毎回こうなる。

```
[人間]   この契約書レビューして（PDFを貼る）
[AI]     はい、こういう点が気になります...
[人間]   じゃあドラフト直して
[AI]     直しました
[人間]   （手元のWordにコピペして、上司に送って、DocuSignで署名依頼出して...）
```

つまり、**AIは「賢いコメント役」止まり**で、前工程（データ集め）と後工程（社内ツールへの反映）は全部人間がやる。

これを解決するのが今回の Claude for Legal / Small Business。**AIが社内ツールに直接アクセスして、データ取得から下書きまで自動でやる。送信前に人間が承認する**。

Anthropic公式の表現（Small Business blog）:

> "You approve the plan first or, when you're ready, let it run end-to-end."
> "You approve before anything sends, posts, or pays."

人間がやる仕事は**①依頼の一言、②AI生成物の承認**だけ。図にするとこうなる。

![普通のAIと Claude for X の関与の違い](https://files.catbox.moe/12up6c.png)

左が従来AI（人間が前後工程を全担当）、右が Claude for X（AIが両端まで動き、人間は承認役）。**業務削減時間の具体数値は公式に未公開**なので、図にも書いていない。

---

## Claude for Legal は具体的に何をやってくれるのか

このセクションで得られること: 公式GitHubリポに**実在する**Skill/Agentで、法務業務に何が引き取られるか。

法務向けにAnthropicが2026-05-12に出した、法律業務に特化したパッケージ。公式GitHubリポ [`anthropics/claude-for-legal`](https://github.com/anthropics/claude-for-legal)（Apache 2.0）で**全Skillが公開されている**ので、推測抜きで分解できる。

### 13プラグインの全リスト（GitHub公開リポで確認）

```
commercial-legal       — 商事契約全般
corporate-legal        — コーポレート / M&A
employment-legal       — 労務 / 雇用
privacy-legal          — プライバシー / GDPR
product-legal          — プロダクト法務
regulatory-legal       — 規制対応
ai-governance-legal    — AI ガバナンス
ip-legal               — 知的財産
litigation-legal       — 訴訟
legal-clinic           — リーガルクリニック
law-student            — 法学生向け
legal-builder-hub      — Skillインストール管理
cocounsel-legal        — Thomson Reuters CoCounsel連携
```

> **補足**: Anthropic公式blogは「12 plugins」と表現しているが、GitHubリポには13ディレクトリがある（うちcocounsel-legalは外部パートナー製）。

### 代表的なSkill / Agentの例

各プラグインにエージェント（Skill）が複数入っている。**全部GitHubリポで実在確認できる**ものを抜粋。

#### commercial-legal（商事契約）

- **Vendor Agreement Reviewer** — ベンダー契約のレビュー
- **NDA Triager** — NDA仕分け
- **Amendment Tracer** — 変更履歴トレース
- **Renewal Watcher** — 更新期日の監視
- **Playbook Monitor** — playbook違反の検知
- **Escalation Router** — エスカレーション判定

#### privacy-legal（プライバシー）

- **DSAR Responder** — GDPR個人情報開示請求対応
- **DPA Reviewer** — データ処理契約のレビュー
- **PIA Generator** — プライバシー影響評価生成
- **Privacy Reg Gap Checker** — 規制ギャップチェック

#### employment-legal（労務）

- **Termination Reviewer** — 解雇通知のレビュー
- **Hire Reviewer** — 採用関連書類レビュー
- **Worker Classification Screener** — 業務委託/雇用の判定
- **Policy Drafter** — 就業規則ドラフト
- **Wage & Hour Q&A** — 賃金・労働時間Q&A

#### litigation-legal（訴訟）

- **Claim Chart Builder** — 特許クレームチャート作成
- **Demand Letter Drafter** — 督促状ドラフト
- **Deposition Prep** — 証言準備
- **Brief Section Drafter** — 準備書面の章ドラフト

#### ai-governance-legal（AIガバナンス）

- **AI Use Case Triager** — AIユースケース分類
- **AI Impact Assessor** — AIインパクト評価
- **Vendor AI Reviewer** — ベンダーAIレビュー
- **AI Reg Gap Checker** — AI規制ギャップチェック

> **GitHub公開リポで数えた総数**: 全プラグイン合計で **86個のSkill/Agent** が定義されている（私が`anthropics/claude-for-legal`のREADMEテーブルから数えた）。

### 接続できる法務SaaS（20以上、GitHubで19個確認）

```
Ironclad          — 契約管理
DocuSign / CLM    — 電子契約・契約ライフサイクル管理
iManage           — ドキュメント管理
Box               — ファイル管理（VDR用途含む）
Everlaw           — eDiscovery
CourtListener     — 連邦判例DB（無料公開）
Trellis           — 州裁判所ドケット
Aurora            — 案件管理
Definely          — ドキュメント内ドラフト支援
Solve Intelligence — 特許ドラフト
Thomson Reuters CoCounsel — Westlaw連携
Slack / Google Drive — 全プラグイン共通
Linear / Atlassian / Asana — product-legal用
他
```

### 採用事務所（公式blogで明示）

公式blogの推薦文に登場するのは:

- **Freshfields**（Gerrit Beckhaus, Partner and Co-Head）
- **Holland & Knight**（Manfred Gabriel, Partner）

> **補足**: 他媒体（Artificial Lawyer / ABA Journal等）では **Quinn Emanuel** や **Crosby Legal** の名前も出ているが、本記事は公式blog記載分のみを採用先として扱う。

---

## Claude for Small Business は具体的に何をやってくれるのか

このセクションで得られること: 中小企業向けに公式が**実際に名指ししている**業務ワークフロー。

2026-05-13にAnthropicが出した、中小企業向けパッケージ。**経理・営業・販促・カスタマー対応を兼務している小規模事業者**を狙っている。

### 公式blogが明示している接続先SaaS（7つ）

```
Intuit QuickBooks   — 会計
PayPal              — 決済
HubSpot             — CRM
Canva               — デザイン
DocuSign            — 電子契約
Google Workspace    — メール・カレンダー・ドキュメント
Microsoft 365       — Outlook / Excel / Teams 等
```

> **補足**: 製品ページ [`claude.com/solutions/small-business`](https://claude.com/solutions/small-business) では追加で **Slack / Google Drive / Google Calendar** が個別にリストされている。

### 公式blogが明示している15ワークフローの抜粋

`15 ready-to-run agentic workflows` と公式blogが明言している。記事内で具体名が明かされているのは以下11個（全15個は公開されていない）:

```
Planning payroll                   — 給与計算プラン
Closing the month                  — 月次決算
Getting a pulse on your business   — 経営状況の把握
Running your next campaign         — キャンペーン運営
Invoice chaser                     — 請求書督促
Margin analyzer                    — マージン分析
Month-end prepper                  — 月次決算の準備
Tax-season organizer               — 税務シーズン整理
Contract reviewer                  — 契約レビュー
Lead triager                       — リード仕分け
Content strategist                 — コンテンツ戦略
```

### 採用顧客（公式blogで明示）

公式blogの推薦文に登場するのは:

- **Purity Coffee**（Brian Ludviksen, COO）
- **Simple Modern**（Mike Beckham, CEO）
- **MidCentral Energy**（Ryan Olson, Technology and Innovation Manager）

### 10都市ツアー（2026-05-14開始）

PayPal共同開発の無料講座 **"AI Fluency for Small Business"** を半日ハンズオンで提供。

```
Chicago, Tulsa, Dallas, Hamilton Township, Baton Rouge,
Birmingham, Salt Lake City, Baltimore, San Jose, Indianapolis
```

> **訂正**: 私が初稿で「New Jersey」と書いた都市は、正しくは **Hamilton Township**（ニュージャージー州内の都市名）です。

### Legal + Small Business の業務サマリ図

両方の代表ワークフローを1枚で並べた図。**業務削減時間は公式未開示なので、図にも入れていない**。

![Claude for Legal / Small Business 公式ワークフロー](https://files.catbox.moe/zhxzps.png)

上段がLegalの5プラグインに含まれる代表Skill、下段がSmall Businessの5ワークフロー。全名称はGitHub公開リポと公式blogから直接拾った。

---

## 何がすごいのか・3つのポイント

このセクションで得られること: 従来のAIと比べて何が新しいのかが整理される。

### すごいポイント1: AIが社内ツールに「入り込む」

普通のAIは、人間がコピペで情報を渡さないと何もできない。

| | **従来のChatGPT/Claude** | **Claude for Legal/Small Business** |
| --- | --- | --- |
| **データ取得** | 人間が貼り付け | AIがMCP経由でツールから直接取得 |
| **業務実行** | アドバイスのみ | 下書き作成 |
| **送信・反映** | 人間がコピペ | 人間承認後にAIが実行 |
| **人間の作業** | 全工程関与 | 依頼の一言 + 承認 |

これは技術的には **MCP（Model Context Protocol）** という仕組みで実現している（詳細は次のセクション）。

### すごいポイント2: AIが「うちのやり方」を覚える

普通のAIは毎回ゼロから対話を始める。今回のパッケージは、インストール時に **cold-start interview** をやる。GitHub公開リポから引用:

> "Run the cold-start interview first. Every other skill in a plugin reads from the practice profile it writes. Skipping setup is the single most common reason a skill produces generic output. The interview takes 10–20 minutes per plugin..."

10〜20分の初回インタビューで「うちの流儀」を聞き出し、`CLAUDE.md` として保存する。保存場所も公式に書かれている:

```
~/.claude/plugins/config/claude-for-legal/<plugin>/CLAUDE.md
```

以降、そのプラグイン内の全Skillはこのファイルを読みにいく。**事務所ごと・会社ごとに違う「うちの基準」を AIが覚える**。

### すごいポイント3: 業務単位のAIが「最初から大量に」入っている

普通は「AIに何を頼もう？」から考える必要がある。今回のパッケージは:

- **Claude for Legal**: GitHub公開リポで **86個** のSkill/Agent
- **Claude for Small Business**: **15** ワークフロー

業務名（Vendor Agreement Reviewer / Invoice chaser 等）で呼び出すと該当業務の専門AIが動く。

---

## 仕組みをやさしく解説

このセクションで得られること: MCP・コネクタ・CLAUDE.md・Plugin のフワッとした用語が、ようやく腹落ちする。

専門用語が3つだけ出てくるので、それぞれ最短で説明する。

### Claude Cowork（コウォーク）= 会社用Claude

普段使う `claude.ai` は個人版。**Cowork** は会社向けにスケールしたClaude。今回の Legal / Small Business は、**Cowork または Claude Code の上にインストールするPlugin** という位置づけ。

GitHubリポから引用:

> "Everything here is available two ways from one source: install it as a Claude Cowork or Claude Code plugin, or deploy it through the Claude Managed Agents API behind your own workflow engine."

### MCP（Model Context Protocol）= AI業界のUSB規格

AIが外部サービス（QuickBooks、DocuSign、Gmail等）と話すための共通規格。Anthropic が 2024年末に提案し、Linux Foundation 管理のオープン標準。

**何がすごいか**: 昔は「ClaudeとQuickBooks繋ぐ専用コネクタ」「ChatGPTとQuickBooks繋ぐ別の専用コネクタ」と全部別物だった。**MCPに対応していれば、どのAIからも同じ接続口で使える**。USB-C化と同じ発想。

### Plugin / Skill = AIに渡す業務マニュアル

Pluginは「業務カテゴリ単位」。Legalなら commercial-legal / privacy-legal 等の13個。各Pluginには複数のSkill（業務エージェント）が入っている。

### 全体構造を1枚で

![Cowork × MCP × CLAUDE.md × Plugin の4階層とMCP=USB アナロジー](https://files.catbox.moe/752vhv.png)

左が4階層の仕組み、右上がMCP=USB規格のアナロジー、右下が承認フローの説明。各階層の説明は左の図に書いてある通り。

---

## 公式が言っていること / 言っていないことの切り分け

このセクションで得られること: 「裏取りした事実」と「未確定事項」を明確に区別。

検証可能なソースに当たった結果、こうなった。

### 公式blogが明示している（一次ソース確認済）

- Legal: 12〜13プラグイン / 20以上のMCPコネクタ / 採用先（Freshfields, Holland & Knight）
- Small Business: 15ワークフロー / 7つの主要接続先 / 採用顧客（Purity Coffee, Simple Modern, MidCentral Energy）
- 10都市ツアー全都市名 / 開始日 2026-05-14
- PayPal共同講座名 "AI Fluency for Small Business"
- 「人間承認」の仕組み（"You approve before anything sends, posts, or pays."）
- MCP の出自（Anthropic提案・Linux Foundation管理）
- GitHub anthropics/claude-for-legal の86 Skill/Agent / Apache 2.0 ライセンス

### 公式blogに記載なし（未確定）

- **価格・課金体系**（Cowork既存ライセンス内包かどうかも不明）
- **業務時間の削減量**（"Hours of looking at stuff that doesn't matter are gone." の定性表現のみ）
- **日本語対応・日本リージョン提供**
- **「Named Agent」「80体」の正式呼称**（公式は "skills" / "agent template" 表記）
- **「4D Framework」の詳細**（公式blog本文に記載なし）
- **「契約金額3倍まで」等のplaybook具体例**（cold-start interviewで何を聞かれるかの詳細は公式に未公開）

### 他媒体ソースに依存（公式blog以外で確認）

- Quinn Emanuel / Crosby Legal の採用（Artificial Lawyer / ABA Journal等）
- ウェビナー登録者20,000名超（Artificial Lawyer）

---

## 日本で使うときの注意点

このセクションで得られること: 「飛びついて損する」前のチェック。

### 価格がまだ表に出ていない

2026-05-17時点で、月額・シート単価の明示が無い。既存のCowork（Pro / Team / Enterprise）に内包される可能性はあるが要確認。

### 日本リージョン・日本語UIは未明示

公式発表は英語圏向け。10都市ツアーも全米のみ。日本展開ロードマップは公開されていない。

### 接続できるSaaSが米国寄り

中小企業向けのコネクタは **QuickBooks / PayPal / HubSpot** など、日本でのシェアが低いものが中心。

| **米国側（公式接続先）** | **日本での主流** |
| --- | --- |
| QuickBooks | freee / マネーフォワード |
| PayPal | クレジットカード決済 / 銀行振込 |
| HubSpot | Salesforce日本 / kintone |

つまり、**日本の中小企業が日常使っているSaaSにそのまま繋がらない**可能性が高い。

### 法務プラグインは英米法ベース

採用事例（Freshfields, Holland & Knight）はすべて英米系。日本の民法・商法・労働基準法への適合は未保証。

### 完全自動化はしない設計

公式blog: "You approve before anything sends, posts, or pays."

送信・支払い・契約署名の前には**必ず人間承認**が必要。end-to-end実行も選択肢としては提示されているが、誤爆防止のため承認モードがデフォルト。

---

## 今日から自分が動けること

このセクションで得られること: 立場別の次アクション。

### 法務・経理・営業の人

1. **今日**: 自社で使っているSaaSが、公式blog/GitHubリポのコネクタ一覧に入っているか確認する
2. **今週**: 普段の業務を1つ書き出して、「うちはこういうルールでやる」というメモを作る（後でCLAUDE.md相当に転用できる）
3. **今月**: 自社の Cowork 契約状況を IT 部門に確認、価格情報を取りに行く

### Claude / ChatGPT を使っているエンジニア

1. **今日**: [MCP公式ドキュメント](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) を1ページだけ読む
2. **今週**: 自分が普段使っているSaaSが MCP対応しているか調べる
3. **今月**: 対応していないSaaSがあれば、簡易MCPサーバを書いて GitHub に置く

### SaaSプロダクト担当

1. **今日**: 自社プロダクトのカテゴリ（会計・CRM・契約等）が、Anthropicのコネクタ一覧に入っているか確認
2. **今週**: 入っていなければ「空席」。MCP対応の優先度を見積もる
3. **今月**: 入っていてもいなくても「人間承認フロー前提のUI」を1画面プロトタイプしておく

---

## まとめ

Claude for Small Business / Claude for Legal は、**「賢いコメント役」止まりだったAIを、社内ツールに入り込んで業務の下書きまでやらせるパッケージ**。送信・支払い・署名の直前は必ず人間承認を挟む。

公式が明示している事実だけを抜き出すと:

- Legal: 13プラグイン / 86 Skill (GitHub公開リポ) / 20以上の法務SaaSコネクタ
- Small Business: 15ワークフロー / 7つの主要SaaS接続 / 10都市無料ツアー

すごいポイントは3つ。

1. **AIが社内ツールに入り込む**（MCPという規格のおかげ）
2. **AIが「うちの流儀」を覚える**（cold-start interview + CLAUDE.md）
3. **業務単位のAIが大量に入っている**（Legalで86 Skill、SMBで15ワークフロー）

**未確定なのは価格・業務削減数値・日本対応の3つ**。公式blogに具体記載がない以上、「ここは公式が言っていないので不明」と切り分けて使うのが安全。

### 今日からやること

1. **今日**: 自社で使ってるSaaSが、公式blog/GitHubリポのコネクタ一覧に入ってるか見る
2. **今週**: 一番面倒な業務を1つ書き出して、「うちのルール」をメモにする
3. **今月**: MCP公式ドキュメントを読む or Cowork契約状況を確認する

---

**参考ソース（一次・公式優先）:**

- [Introducing Claude for Small Business — Anthropic公式blog](https://www.anthropic.com/news/claude-for-small-business)
- [Claude for the legal industry — Claude公式blog](https://claude.com/blog/claude-for-the-legal-industry)
- [anthropics/claude-for-legal — GitHub公開リポ (Apache 2.0)](https://github.com/anthropics/claude-for-legal)
- [Claude for Small Business — 製品ページ](https://claude.com/solutions/small-business)
- [Get started with custom conn
