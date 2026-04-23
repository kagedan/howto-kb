---
id: "2026-04-18-gas-claude-api-search-console-で作るseo週次レポート自動生成システム-01"
title: "GAS + Claude API + Search Console で作る、SEO週次レポート自動生成システム"
url: "https://zenn.dev/bentenweb_fumi/articles/seo-weekly-20260418"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

「SEOをやっているけど、毎週どのキーワードを狙って記事を書くかの判断材料がない」

これは中小規模のオウンドメディアを運用していると必ず突き当たる壁です。Search Console を毎週開いてエクセルに転記して、競合と比較して、改善案を考えて……というのを手作業でやっていると、本業を圧迫します。

そこで、**毎週土曜の朝にレポートが自動でDiscordに届く**仕組みを Google Apps Script + Claude API で構築しました。レポートを朝コーヒーを飲みながら見て、その週に書く記事のキーワードを判断するだけで済みます。

本記事では、その構成と実装のポイント、運用してわかった「LLMにレポートを書かせるコツ」を共有します。

## 技術構成

### 全体像

### 技術スタック

| レイヤー | 採用技術 | 役割 |
| --- | --- | --- |
| 実行環境 | Google Apps Script | 既存の blog\_auto プロジェクトに追加、サーバー不要 |
| データソース1 | Search Console API v3 | クエリ別の表示回数・クリック・順位 |
| データソース2 | WordPress REST API | 公開記事のタイトル・カテゴリ・公開日 |
| データソース3 | スプレッドシート | GMOキーワード（メインKW + サブKW）の順位履歴 |
| AI分析 | Claude API (sonnet) | 統合データから示唆を抽出、提案KWを生成 |
| 通知 | Discord Webhook | `#task-report` チャンネルに本文 + サマリ |

### 「APIから取る」だけでは足りない

最初は Search Console と WordPress のデータを単純にレポート化していました。が、これだけだと \*\*「で、今週何の記事を書けばいいの？」\*\*が見えてきません。

そこで以下の3要素を組み合わせる構成にしました。

1. **実績データ**: SCのクエリ・順位・CTR
2. **コンテンツ資産**: WPの公開済み記事一覧
3. **戦略レイヤー**: GMOキーワードシート（狙うべきメイン3KW + サブ15KW）

この3つを Claude に渡して「ギャップ分析 + 来週書くべきキーワード提案」をさせると、毎週「次にやるべきこと」が明確に出てきます。

## 実装のポイント

### 1. Search Console API は OAuth Token 直叩きが安定

GAS の Advanced Services にも Search Console は無く、UrlFetchApp + OAuth Token で叩きます。`ScriptApp.getOAuthToken()` を使うと、スクリプトに紐づいた認証で実行できます。

```
function fetchSearchConsoleData(siteUrl, startDate, endDate) {
  const url = `https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/searchAnalytics/query`;
  const payload = {
    startDate: startDate,
    endDate: endDate,
    dimensions: ['query', 'page'],
    rowLimit: 500,
  };
  const response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: `Bearer ${ScriptApp.getOAuthToken()}` },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });
  if (response.getResponseCode() !== 200) {
    throw new Error(`SC API error: ${response.getResponseCode()}`);
  }
  return JSON.parse(response.getContentText()).rows || [];
}
```

`appsscript.json` に Search Console の OAuth scope を追加するのを忘れると認証が通りません。

```
{
  "oauthScopes": [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/script.external_request"
  ]
}
```

### 2. WordPress REST API のフォールバックURL

クライアント環境によっては `https://example.com/wp-json/wp/v2/posts` が 404 を返すことがあります（パーマリンク設定や、サーバー側のリダイレクト設定の影響）。その場合は以下の代替URLを使います。

```
https://example.com/blog/index.php?rest_route=/wp/v2/posts
```

実装側では先に通常URLを試し、404なら代替URLにフォールバックする処理を入れています。

### 3. Claude へのプロンプト設計

Claude にレポートを書かせるプロンプトの肝は、**「役割」「データ」「出力形式」を明確に分離する**ことです。

```
function buildPrompt(scData, wpPosts, gmoKeywords) {
  return `
あなたはSEOアナリストです。以下のデータから、来週の記事制作の意思決定に使えるレポートを作成してください。

## データ1: Search Console（過去7日 vs 前週）
${formatScDiff(scData)}

## データ2: 公開済み記事一覧
${wpPosts.map((p) => `- ${p.title}（${p.date}）`).join('\n')}

## データ3: 戦略キーワード（メイン3 + サブ15）
${gmoKeywords.map((k) => `- ${k.keyword}: 現在${k.rank}位（先週${k.prevRank}位）`).join('\n')}

## 出力形式（厳守）
### サマリ（3行以内）
### 上昇/下落クエリ Top3
### 提案キーワード（来週書くべき記事 3本、根拠付き）
### 推奨アクション
`;
}
```

ポイントは \*\*「出力形式を厳守させる」「根拠を付けさせる」\*\*こと。これをやらないと、毎週フォーマットが揺れて読みにくくなります。

### 4. 6分制限への対応

GAS は1実行あたり6分の上限がありますが、本処理は実測で約44秒。十分余裕があります。

ただし将来的にサイト数が増えた場合に備えて、サイト単位で別関数に分離してトリガーを並べる設計にしました。

```
function seo_generateWeeklyReport() {
  const startTime = Date.now();
  const sites = getMonitoredSites();

  for (const site of sites) {
    if (Date.now() - startTime > 5 * 60 * 1000) {
      // 5分超えたら次回トリガーに譲る
      saveResumeState(site.id);
      return;
    }
    processOneSite(site);
  }
}
```

### 5. Discord Webhook の文字数制限対策

Discord の1メッセージは 2000 文字制限があります。Claude が長文レポートを返すと超えるので、以下の対策を入れています。

* サマリ部分のみを Discord 本文に出す
* レポート全文はスプレッドシートに保存し、リンクを Discord に貼る
* 提案KW Top3 だけは本文に含める（即判断したいので）

```
function postToDiscord(report, sheetUrl) {
  const summary = extractSummary(report);
  const proposedKw = extractProposedKeywords(report);
  const message = `
**SEO週次レポート (${formatDate(new Date())})**

${summary}

**今週書くべきキーワード（Top3）**
${proposedKw.slice(0, 3).map((k, i) => `${i + 1}. ${k.keyword} — ${k.reason}`).join('\n')}

詳細: ${sheetUrl}
`.trim().substring(0, 1900);

  UrlFetchApp.fetch(DISCORD_WEBHOOK_URL, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ content: message }),
  });
}
```

## 運用してわかったこと

### 「土曜朝に届く」が判断速度を変える

平日に届くと、本業の合間に流し読みして対応が遅れがちでした。**土曜朝に届く運用**にしたら、コーヒーを飲みながら落ち着いて読めて、その日のうちに来週分のキーワードが決まるようになりました。

スケジュール設計はLLMの精度より、**いつ届けるか**のほうが運用に効くケースが多いです。

### LLMの提案を100%信用しない

Claude が出す提案KWは7〜8割は妥当ですが、残り2〜3割は「狙う意味がないKW」「すでに書いた記事と被るKW」が混ざります。

なので運用上は「Top3提案を見て、自分でフィルタしてから記事制作に渡す」フローにしています。LLMは判断材料の整理係であって、最終判断は人間が握る、という分担です。

### データソースを増やすたびに精度が上がる

最初は SC データだけでしたが、WP記事一覧 + GMOキーワードシートを追加するごとに、提案の質が上がりました。

特に **「すでに公開している記事一覧」を渡すこと**で、「既存記事と被らないKW」「既存記事のリライト候補」のような、より実用的な提案が出るようになりました。

LLMにレポートを書かせるとき、データの質と量は精度に直結します。

## まとめ

SEOレポートの自動化で実用的になったのは、以下の3点を意識してからでした。

1. **データソースを複数組み合わせる（実績 + 資産 + 戦略）**
2. **プロンプトで出力形式を厳格に固定し、根拠を必ず添えさせる**
3. **届けるタイミングを「判断したい時間」に合わせる**

次の一手としては、Looker Studio との連携（ビジュアル化）と、競合サイトの公開記事を自動収集して比較に組み込む、を検討しています。

SEO の意思決定を「気合と根性」から「データと提案」に変えるだけで、コンテンツ運用の負荷が大きく下がります。同じ悩みを持つ方の参考になれば幸いです。

---

## この記事を書いた人

**BENTEN Web Works** — 業務自動化・AI活用・システム開発のフリーランスエンジニアです。

Claude Code / GAS / Python を活用した開発や、AI導入のご相談を承っています。

👉 **[業務自動化サービス](https://bentenweb.com/services/automation/)** — 詳細・お問い合わせはこちら  
🐦 **[X（旧Twitter）](https://x.com/Fumi_BENTENweb)** — 日々の知見を発信中
