---
id: "2026-04-23-claude-codeでseo記事全自動生成エージェントを作ったgoogle-docs連携-01"
title: "Claude CodeでSEO記事全自動生成エージェントを作った【Google Docs連携】"
url: "https://zenn.dev/ai_strategy/articles/014ae83627a611"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "zenn"]
date_published: "2026-04-23"
date_collected: "2026-04-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

「記事書いて」と入力するだけで、キーワード選定→構成案作成→本文生成→Googleドキュメント保存→スプシへのログ記録まで全自動で動くエージェントを作った。

技術スタックはシンプルで、**Claude Code + Node.js + Google APIs**の組み合わせだ。サーバーもDockerも不要。ローカルで動く。

この記事では設計のポイントと実装の詳細を書く。

---

## システム全体像

```
ユーザー入力（「記事書いて」）
　↓
Claude Code（エージェント）
　├─ WebSearchでキーワードリサーチ
　├─ 構成案を生成・提示
　├─ 本文を生成（500〜10,000字）
　├─ Google Docs APIでドキュメント作成
　└─ Google Sheets APIで記事ログに追記
```

Claude Codeがオーケストレーターとして全体を制御し、必要に応じてNode.jsスクリプトを呼び出してGoogle APIと連携する設計だ。

---

## ディレクトリ構成

```
seo-article-agent/
├── CLAUDE.md                        ← エージェントの全スキル定義
├── package.json
├── .env.example
├── auth-google.mjs                  ← Google OAuth認証フロー
├── setup/
│   └── SETUP-FOR-CC.md             ← セットアップ手順書
├── tools/
│   ├── lib/
│   │   ├── sheets.mjs              ← Sheets APIヘルパー
│   │   └── docs.mjs               ← Docs APIヘルパー
│   ├── init-spreadsheet.mjs
│   ├── create-template-sheet.mjs
│   └── build-dist.mjs             ← 配布用ZIP生成
└── .claude/
    └── skills/
        └── write-article/
            └── SKILL.md            ← 記事作成スキル定義
```

---

## Claude Codeのスキル設計

このシステムの核心は**CLAUDE.mdとSKILL.mdの設計**だ。

Claude Codeはプロジェクトルートの`CLAUDE.md`を読んでコンテキストを把握する。ここにトリガーとスキルの対応表を書いておくことで、ユーザーの発話に応じて適切なスキルを呼び出せる。

### トリガー定義

```
## トリガー

| ユーザーの発話 | 発動するスキル |
|--------------|-------------|
| 「開始」「始める」「スタート」 | セットアップスキル |
| 「記事書いて」「SEO記事作って」 | 記事作成スキル |
| 「履歴見せて」「何書いた？」 | 履歴確認スキル |
```

### 記事作成スキルのワークフロー定義

`SKILL.md`に記事作成の全ステップを定義する。重要なのは**ステップ間の依存関係**を明示することだ。

```
### Step 4: 構成案の作成・提示

（構成案を提示）

ユーザーが修正指示を出したら、修正して再提示する。
「OK」「いいよ」「進めて」等の承認を受けてから Step 5 に進む。
```

「承認なしに次のステップに進まない」という制約をプロンプトレベルで書いておくことが重要だ。これがないと、ユーザーが確認する前にどんどん先に進んでしまう。

### 品質基準の定義

生成記事の品質は、`SKILL.md`に書く品質基準で大きく変わる。

```
#### 絶対やらないこと

- 「〜について解説します」等の冗長な前置き
- 同じ内容を言い方を変えて繰り返す（文字数稼ぎ）
- 根拠のない断定（「絶対に効果があります」等）
- AIっぽい定型表現（「〜という観点で」「非常に重要です」）
```

**「やること」よりも「やらないこと」の定義が効く**。禁止事項を明示するだけで、出力の品質が体感で1.5倍くらい上がる。

---

## Google API連携の実装

### 認証フロー

OAuth 2.0のデスクトップアプリフローを使う。初回認証でトークンを`credentials/tokens.json`に保存し、以降は自動でリフレッシュする。

```
// auth-google.mjs（抜粋）
import { google } from 'googleapis';
import { createServer } from 'http';
import open from 'open';

const SCOPES = [
  'https://www.googleapis.com/auth/documents',
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.file',
];

const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  'http://localhost:3000/callback'
);

const authUrl = oauth2Client.generateAuthUrl({
  access_type: 'offline',
  scope: SCOPES,
});

// ブラウザで認証URLを開く
await open(authUrl);
```

### Google Docsへの記事出力

```
// tools/lib/docs.mjs（抜粋）
import { google } from 'googleapis';

export async function createArticleDoc(title, markdownBody) {
  const auth = await getAuth();
  const docs = google.docs({ version: 'v1', auth });
  const drive = google.drive({ version: 'v3', auth });

  // ドキュメント作成
  const doc = await docs.documents.create({
    requestBody: { title },
  });
  const docId = doc.data.documentId;

  // 本文を挿入
  await docs.documents.batchUpdate({
    documentId: docId,
    requestBody: {
      requests: [
        {
          insertText: {
            location: { index: 1 },
            text: markdownBody,
          },
        },
      ],
    },
  });

  const url = `https://docs.google.com/document/d/${docId}/edit`;
  return { docId, url };
}
```

Markdown形式で渡すと、Googleドキュメントにプレーンテキストとして挿入される。見出しのスタイリングまでやろうとするとbatchUpdateが複雑になるので、今は本文挿入だけに留めている。

### Sheetsへのログ記録

```
// tools/lib/sheets.mjs（抜粋）
export async function appendArticleLog({ keyword, title, articleUrl, charCount }) {
  const auth = await getAuth();
  const sheets = google.sheets({ version: 'v4', auth });

  const today = new Date().toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });

  await sheets.spreadsheets.values.append({
    spreadsheetId: process.env.SPREADSHEET_ID,
    range: '記事ログ!A:E',
    valueInputOption: 'USER_ENTERED',
    requestBody: {
      values: [[keyword, title, articleUrl, charCount, today]],
    },
  });
}
```

Claude Codeからこの関数を呼び出すときは、インラインでNode.jsを実行する。

```
node --input-type=module -e "
import { appendArticleLog } from './tools/lib/sheets.mjs';
await appendArticleLog({
  keyword: 'SEO対策 やり方',
  title: '【2026年最新】SEO対策のやり方完全ガイド',
  articleUrl: 'https://docs.google.com/document/d/xxxx/edit',
  charCount: 5200,
});
console.log('✓ スプシに記録完了');
"
```

---

## 配布用ZIPの生成

`.env`や`credentials/`などの個人データを除外して配布用ZIPを作るスクリプトも用意した。

Windowsでは`zip`コマンドが使えないため、PowerShellの`Compress-Archive`を使う分岐を入れた。

```
// tools/build-dist.mjs（抜粋）
const isWindows = process.platform === 'win32';

if (isWindows) {
  // ファイルをtempDirにコピーしてからCompress-Archive
  const psCmd = `Compress-Archive -Path "${tempDir}\\*" -DestinationPath "${outPath}" -Force`;
  execSync(`powershell -Command "${psCmd}"`, { stdio: 'inherit' });
} else {
  // macOS / Linux
  const excludeArgs = EXCLUDE_PATTERNS
    .map((p) => `-x './${p}' -x './${p}/*'`)
    .join(' ');
  execSync(`cd "${PROJECT_ROOT}" && zip -r "${outPath}" . ${excludeArgs}`, {
    stdio: 'inherit',
  });
}
```

---

## 設計上のポイント

### 1. Claude Codeをオーケストレーターにする

AIに全部考えさせるのではなく、**「何をすべきか」はMarkdownで定義し、「どう実行するか」はClaude Codeに任せる**設計にした。

スキル定義が明確なほど、Claude Codeの動作が安定する。曖昧な指示は曖昧な挙動を生む。

### 2. ユーザーの操作回数を最小化する

ユーザーが操作するのは3回だけになるように設計した。

1. 「記事書いて」と入力
2. キーワードを番号で選ぶ
3. 構成案に「OK」と返す

それ以外は全部自動。この「操作回数の最小化」が使い続けてもらえるかどうかの分岐点だと思っている。

### 3. 環境変数はエージェントが設定する

ユーザーにファイルを直接編集させない設計にした。

```
クライアントIDとクライアントシークレットの両方を、
このチャットにそのまま貼り付けてください。
こちらで自動的に設定ファイルを作成します。
```

チャットに値を貼り付けてもらえば、Claude Codeが`.env`を自動生成する。「.envって何？」「どこを編集すればいい？」という質問が来ない設計にすると、非エンジニアでも詰まらない。

### 4. エラーハンドリングをセットアップガイドに書く

よくあるエラーとその対処法をセットアップガイドに網羅しておく。

```
| エラーメッセージ | 原因 | 対応 |
|---------------|------|------|
| `Token file not found` | Google認証未完了 | auth-google.mjsを再実行 |
| `アクセスがブロックされました` | テストユーザー未登録 | GCPでユーザーを追加 |
| `SPREADSHEET_ID not set` | スプシ未設定 | テンプレートをコピー |
```

エラーが起きたときに「何が起きたか」「次に何をすればいいか」がわかるだけで、サポートコストが大幅に減る。

---

## 詰まったところ

### Windowsでzipコマンドが使えない

macOSやLinuxには標準で`zip`があるが、Windowsにはない。最初はNode.jsの`archiver`パッケージを使おうと思ったが、追加の依存を増やしたくなかった。

結局、PowerShellの`Compress-Archive`を使うことにした。ただしPowerShellへのパス渡しで日本語が文字化けするケースがあったため、一旦tempディレクトリにファイルをコピーしてからZIPを作る方式にした。

### Google Docs APIのMarkdown非対応

Google Docs APIはMarkdownをそのまま受け付けない。`insertText`で挿入するとプレーンテキストになる。

見出しスタイルを適用するには`updateParagraphStyle`リクエストを使う必要があり、行ごとにH2/H3を判定してbatchUpdateのrequestsを組み立てる実装が必要になる。

今は本文をプレーンテキストで挿入するだけにしている。Googleドキュメントで開いてからスタイルを当てる運用で妥協した。次のバージョンでちゃんと実装したい。

---

## まとめ

* **Claude Codeのスキル設計が全て**。CLAUDE.mdとSKILL.mdを丁寧に書くほど動作が安定する
* **「やらないこと」の定義が生成品質を上げる**
* **Windowsのzip問題はPowerShellで回避**できる
* **Google Docs APIはMarkdown非対応**なので、スタイリングは手動か別途実装が必要

---

## ツールとして公開しています

このシステムを**Kijiru**という名前でGumroadに公開した。プログラミング不要で、Claude CodeとGoogleアカウントがあれば動く。セットアップガイド付き。

エンジニアが買うものというよりは、「AIを使いたいけどコードは書けない」という人向けに設計した。

自分でゼロから作りたい人はこの記事を参考にどうぞ。

👉 [Kijiru — SEO記事全自動生成ツール](https://6132829596308.gumroad.com/l/wnpjzk)
