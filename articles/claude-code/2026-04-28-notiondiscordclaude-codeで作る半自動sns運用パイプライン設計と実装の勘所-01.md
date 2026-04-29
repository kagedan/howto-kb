---
id: "2026-04-28-notiondiscordclaude-codeで作る半自動sns運用パイプライン設計と実装の勘所-01"
title: "Notion×Discord×Claude Codeで作る「半自動SNS運用パイプライン」設計と実装の勘所"
url: "https://zenn.dev/bentenweb_fumi/articles/ucvoaiy8wi09"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-28"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

## はじめに：なぜ「完全自動化」ではなく「半自動化」なのか

SNS運用の自動化ツールは数多く存在しますが、エンジニアが個人や小規模事業で運用する場合、既製SaaSは「機密情報のサニタイズが甘い」「投稿フォーマットの自由度が低い」「月額コストが地味に効いてくる」といった課題があります。

本記事では、**Notion（記録）→ GAS（生成）→ Discord（承認）→ X API（投稿）** をパイプラインで繋ぎ、**月額0円・工数1/3** を実現したアーキテクチャを共有します。LLMをエージェント的に組み込みつつも、**最終承認は必ず人間に残す**という設計判断についても掘り下げます。

## 全体アーキテクチャ

```
[Notion 業務日記]
      │ 定期Pull (GAS Trigger)
      ▼
[Firestore: status=未処理]
      │ Claude Code CLI
      ▼
[サニタイズ → LLM生成 → NGワード検証]
      │
      ▼
[Firestore: status=サニタイズ済]
      │ Discord Webhook
      ▼
[#x-approval チャンネル]
      │ 👍リアクション
      ▼
[X API v2 予約投稿]
      │ 30分後
      ▼
[自己リプライ自動投稿（GAS Trigger）]
```

ポイントは**Firestoreをステートマシンの中心に据える**ことです。各ステップは疎結合で、どこで止まっても再開可能。GASの6分実行制限を回避するために、重い生成処理はローカルのClaude Code CLIに寄せています。

## 技術スタック比較：なぜこの組み合わせなのか

| レイヤ | 採用 | 比較対象 | 採用理由 |
| --- | --- | --- | --- |
| LLM | Claude Code（サブスク） | OpenAI API / Gemini API | 従量課金がなく、長文生成でコスト気にせず試行錯誤できる |
| DB | Firestore（Sparkプラン） | Supabase / PlanetScale | 無料枠で十分、GASとの相性が良い |
| ジョブ実行 | GAS Trigger | Cloud Functions / Cloud Run | 無料、デプロイ不要、トリガー設定がGUIで完結 |
| 通知・承認UI | Discord | Slack / LINE | Bot無料、リアクションAPIが扱いやすい、モバイルからも操作可 |
| 投稿先 | X API v2 Free | Buffer / Hootsuite | 月500投稿枠で個人運用には十分、有料SaaS不要 |

## 実装の核：サニタイズ層

業務日記をそのままLLMに食わせると、クライアント名・PV数・契約金額などが投稿に紛れ込むリスクがあります。**サニタイズはLLMに任せず、決定論的なルールベースで先に行う**のが鉄則です。

```
// scripts/sanitize.mjs（抜粋）
const SANITIZE_RULES = [
  { pattern: /株式会社[\u4e00-\u9fa5ァ-ヴー]+/g, replace: '某社' },
  { pattern: /[\d,]+万円/g, replace: '一定額' },
  { pattern: /\b\d{2,}人\b/g, replace: '複数名' },
  { pattern: /sk-[A-Za-z0-9]{20,}/g, replace: '[REDACTED]' },
];

export function sanitize(rawText) {
  return SANITIZE_RULES.reduce(
    (text, { pattern, replace }) => text.replace(pattern, replace),
    rawText
  );
}
```

その後、LLM生成結果に対して**NGワードリスト（`config/ng_words.json`）で二段階チェック**を行います。違反検出時は `exit 1` で止め、Discordへ「再生成が必要」と通知。

## ステップ詳細

### Step 1: Notion → Firestore取り込み

GASのトリガーで30分おきにNotion APIを叩き、`status: 未処理` でFirestoreに保存。重複は `notion_page_id` をキーに排除します。

### Step 2: サニタイズ＆LLM生成

ローカルでClaude Code CLIを起動し、`未処理` レコードをまとめて処理。プロンプトには以下を渡します。

* 過去の高ER投稿（フィードバックループ）
* ターゲット属性（経営者 / エンジニア）
* 切り口5パターンから1つ選択させる指示

### Step 3: Discord承認

```
// 承認待ちメッセージ送信
await fetch(WEBHOOK_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: `**[${target}] 承認待ち**\n\n${generatedText}\n\n---\n機密チェック: ${checklist}`,
  }),
});
```

メッセージに👍リアクションが付いたらBotがX API予約投稿を作成。👎なら破棄、💬なら再生成キューへ戻します。

### Step 4: 予約投稿 + 自己リプライ

X API v2 の予約投稿エンドポイントでテキストのみ予約。**画像はGeminiアプリで手動添付**する運用にしています（Imagen系のAPI課金を避けつつ品質を担保）。投稿30分後にGASトリガーが自己リプライを追加投稿します。

## なぜ「完全自動化」を避けたのか

エンジニア界隈では「全自動化こそ正義」という空気がありますが、SNS運用に関しては**人間の最終確認を残す方がROIが高い**と判断しました。

| 観点 | 完全自動化 | 半自動化（採用） |
| --- | --- | --- |
| 工数 | 0分/日 | 約10分/日 |
| 機密漏洩リスク | 高（事故時に拡散済み） | 低（承認時に検知可能） |
| トーンのブレ | 中〜高 | 低（人間が違和感をフィルタ） |
| 心理的安全性 | 低（無意識に投稿が拡散される恐怖） | 高 |

10分/日のコストで、事故の致命性を大幅に下げられるなら安いものです。

## FAQ

**Q. Claude Code以外でも組めますか？**  
A. はい。`OpenAI GPT-4o` や `Gemini 2.5 Pro` でも同等の構成は可能です。ただし生成回数が多くなる運用ではサブスク型LLMの方が予算予測が立てやすいです。

**Q. Notionじゃないとダメ？**  
A. Markdownを取得できればObsidian + Git, Logseq, Scrapbox なんでも代用可能です。要は**業務記録の正本がデジタルで存在する**ことが前提条件です。

**Q. Discordじゃなくても？**  
A. SlackのInteractive MessageやLINE Botでも実装可能です。Discordを選んだのは個人開発者にとってBot枠が無料・無制限で気軽だからです。

## 将来の展望：Agentic Workflowへの拡張

現在は「生成→承認→投稿」の一方向パイプラインですが、Claude Agent SDKやMCPを組み合わせれば以下の拡張が見えてきます。

* **投稿パフォーマンスを観測してプロンプトを自己更新するループ**（reflexion型）
* **複数SNS（X / Threads / Bluesky）への横展開とプラットフォーム最適化**
* **コメント返信の半自動化**（再びDiscord承認を挟む）

特にMCPサーバー化しておくと、Claude Codeから `@x-automation generate` のように呼び出せて、エージェント連携の幅が広がります。

## まとめ

* SNS運用の自動化は「完全」より「承認フロー付き半自動」がROI高い
* Firestoreをステートマシンの中心にすると各ステップが疎結合になり再開可能
* サニタイズはLLM任せにせず、ルールベース＋NGワードの二段構えが鉄則
* 月額0円構成でも、工数1/3 + 品質担保は十分に達成できる

LLM時代のコンテンツ運用は、「人間がどこまで関与を残すか」という設計判断こそが品質を決めます。フルオートに飛びつく前に、**自分のリスク許容度に合わせたパイプライン設計**を一度図に書き出してみることをおすすめします。

---

## この記事を書いた人

**BENTEN Web Works** — 業務自動化・AI活用・システム開発のフリーランスエンジニアです。

Claude Code / GAS / Python を活用した開発や、AI導入のご相談を承っています。

👉 **[業務自動化サービス](https://bentenweb.com/services/automation/)** — 詳細・お問い合わせはこちら  
🐦 **[X（旧Twitter）](https://x.com/Fumi_BENTENweb)** — 日々の知見を発信中
