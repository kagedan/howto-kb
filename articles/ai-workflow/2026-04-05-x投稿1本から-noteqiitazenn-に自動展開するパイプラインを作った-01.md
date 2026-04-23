---
id: "2026-04-05-x投稿1本から-noteqiitazenn-に自動展開するパイプラインを作った-01"
title: "X投稿1本から note・Qiita・Zenn に自動展開するパイプラインを作った"
url: "https://zenn.dev/bentenweb_fumi/articles/8vt8cvkbbfxv"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## はじめに

フリーランスの情報発信、続けていますか？

X、ブログ、note、Qiita、Zenn。「全部やるべき」とわかっていても、1人で複数メディアを運用するのは現実的ではありません。1記事書くのに1〜2時間。それを各メディア用にフォーマット調整して投稿。週3本ペースでやると、発信だけで週10時間以上が消えます。

そこで「1つのX投稿から、AIが自動でリライトして複数メディアに展開する」仕組みを作りました。この記事では、その技術構成と実装方法を詳しく解説します。

## 全体アーキテクチャ

```
参考投稿（日常のインプット）
  ↓
AI生成（X投稿 500〜800文字）
  ↓
Firestore に保存（status: サニタイズ済）
  ↓
GAS → Discord #x-approval に通知
       Discord #content-hub にコピペ用テキスト
  ↓
ユーザーが承認 + 画像添付 + 日時指定
  ↓
GAS Cron → X に自動投稿
  ↓
ターゲット自動判別
  ↓
AIリライト（500文字 → 2000文字）
  ↓
  ├── 経営者向け → note（Playwright + CDP）
  ├── 技術実装系 → Qiita（公式API）
  └── AI関連 → Zenn（GitHub push）
```

## 技術スタック

| コンポーネント | 技術 | 役割 |
| --- | --- | --- |
| データストア | Firebase Firestore | 投稿データ・ステータス管理 |
| 承認フロー | GAS + Discord Webhook | 通知・承認・スケジュール予約 |
| X投稿 | GAS + X API v2 | 自動投稿・自己リプライ |
| メディア判別 | Node.js スクリプト | target フィールド + キーワード分析 |
| Qiita投稿 | Qiita API v2 | `POST /api/v2/items` |
| Zenn投稿 | Git + GitHub | マークダウンを push → 自動公開 |
| note投稿 | Playwright + CDP | ブラウザ自動操作 |
| リライト | Claude / GPT | 500文字 → 2000文字に拡張 |

## ターゲット自動判別ロジック

投稿データの `target` フィールドと本文のキーワードで送信先を決定しています。

```
function detectMedia(target, text) {
  const aiKeywords = ["AI", "Claude", "GPT", "生成AI", "LLM", "ChatGPT"];
  const isAI = aiKeywords.some((kw) => text.includes(kw));

  if (isAI) return "zenn";
  if (target.includes("エンジニア")) return "qiita";
  return "note"; // 経営者向け or デフォルト
}
```

## メディア別の投稿方式

### Qiita（API連携）

最もシンプル。公式APIにPOSTするだけです。

```
const res = await fetch("https://qiita.com/api/v2/items", {
  method: "POST",
  headers: {
    Authorization: "Bearer " + accessToken,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: title,
    body: bodyWithCta,
    tags: tags,      // キーワードから自動推定
    private: false,
  }),
});
```

タグは本文のキーワード（Python, GAS, Claude等）から自動推定しています。

### Zenn（GitHub連携）

ZennはGitHubリポジトリと連携しており、`articles/` ディレクトリにマークダウンを push するだけで記事が公開されます。

```
// フロントマターを生成
const zennArticle = `---
title: "${title}"
emoji: "💡"
type: "tech"
topics: ["claude", "automation", "ai"]
published: true
---

${bodyWithCta}
`;

// git commit & push
execSync("git add -A && git commit -m 'Add article' && git push origin main");
```

トピックも本文のキーワードから自動推定しています。

### note（Playwright + CDP）

noteは公式APIがないため、Playwrightでブラウザを自動操作します。既にCDPモードで起動しているChromeに接続し、ログイン済みのセッションを使います。

```
const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const page = await context.newPage();
await page.goto("https://note.com/new");

// タイトル入力
await titleInput.fill(title);

// 本文を段落ごとに入力
for (const para of paragraphs) {
  await page.keyboard.type(para, { delay: 5 });
  await page.keyboard.press("Enter");
}

// 下書き保存
await page.keyboard.press("Meta+s");
```

## リライトのルール

同じネタを複数メディアに出す際の重要なポイントは「水増しではなく深掘り」です。

| ルール | 理由 |
| --- | --- |
| 具体的な事例・データを追加 | 元の投稿にない情報を加えることで別コンテンツになる |
| コード例を追加（Qiita/Zenn） | 技術記事としての価値が上がる |
| メディアごとにトーンを変える | noteは経営者向け、Qiitaはエンジニア向け |
| 2000文字以上に拡張 | 元の3倍以上で重複コンテンツ判定を回避 |

## 被リンク効果

すべての記事末尾にbentenweb.comへのCTAを設置しています。メディアごとにトーンを変えて自然な導線にしています。

年間100本のX投稿 → 100本の外部記事 → 100本の被リンク。個人事業主のSEOとしては十分な量です。

## まとめ

* X投稿1本から note/Qiita/Zenn に自動展開するパイプラインを構築
* ターゲット（経営者/エンジニア/AI関連）で送信先を自動判別
* Qiita: API、Zenn: GitHub push、note: Playwright + CDP
* リライトは「水増し」ではなく「深掘り」で2000文字以上に
* すべての記事にbentenweb.comへのCTAを設置し、被リンク効果を狙う

「1つのコンテンツの価値を最大化する」という発想で、1人運営でも複数メディア同時展開は実現できます。

---

## この記事を書いた人

**BENTEN Web Works** — 業務自動化・AI活用・システム開発のフリーランスエンジニアです。

Claude Code / GAS / Python を活用した開発や、AI導入のご相談を承っています。

👉 **[BENTEN Web Works](https://bentenweb.com)** — お問い合わせはこちら  
🐦 **[X（旧Twitter）](https://x.com/Fumi_BENTENweb)** — 日々の知見を発信中
