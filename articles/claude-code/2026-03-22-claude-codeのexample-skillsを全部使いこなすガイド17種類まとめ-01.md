---
id: "2026-03-22-claude-codeのexample-skillsを全部使いこなすガイド17種類まとめ-01"
title: "Claude Codeのexample-skillsを全部使いこなすガイド【17種類まとめ】"
url: "https://qiita.com/souichirou/items/26f3c6fe731e710f62e3"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

# Claude Codeのexample-skillsを全部使いこなすガイド【17種類まとめ】

## はじめに

Claude Codeには `example-skills` という便利なスキル群が用意されています。しかし「どんなスキルがあるか」「いつ使うのか」がわかりにくく、存在を忘れてしまいがち。

この記事では、**example-skillsとは何か・インストール方法**から、全17種類のスキルを\*\*「こんなときに使う」という具体例つき\*\*で紹介します。

---

## スキル一覧（全17種）

| スキル名 | 用途 |
| --- | --- |
| `/doc-coauthoring` | ドキュメント・仕様書・提案書の共同執筆ワークフロー |
| `/theme-factory` | アーティファクト（スライド・HTML等）へのテーマ適用（10種プリセット） |
| `/webapp-testing` | Playwrightを使ったローカルWebアプリのテスト・UI検証 |
| `/claude-api` | Claude API / Anthropic SDKを使ったアプリ構築 |
| `/docx` | Wordファイル（.docx）の作成・編集・操作 |
| `/skill-creator` | 新スキルの作成・既存スキルの改善・evalによる評価 |
| `/algorithmic-art` | p5.jsを使ったアルゴリズミックアート・ジェネラティブアート生成 |
| `/pdf` | PDFの読み取り・結合・分割・作成・OCR等 |
| `/xlsx` | Excelファイル（.xlsx/.csv等）の作成・編集・変換 |
| `/mcp-builder` | MCPサーバーの構築ガイド（Python/Node対応） |
| `/frontend-design` | 高品質なフロントエンドUI・Webコンポーネントの作成 |
| `/brand-guidelines` | Anthropicブランドカラー・タイポグラフィの適用 |
| `/slack-gif-creator` | Slack用アニメーションGIFの作成 |
| `/pptx` | PowerPointファイル（.pptx）の作成・編集・読み取り |
| `/canvas-design` | PNG/PDFでポスター・アート・デザイン作成 |
| `/internal-comms` | 社内コミュニケーション文書（ステータスレポート等）の作成 |
| `/web-artifacts-builder` | React + Tailwind + shadcn/uiを使った複雑なHTMLアーティファクト作成 |

詳細は後述します。

---

## example-skillsとは？

Claude Codeには「スキル」という仕組みがあります。特定のタスクに特化した指示セット（SKILL.mdファイル）で、`/スキル名` または自然言語でトリガーすると、そのタスクに最適化された動作をしてくれます。

スキルには2種類あります：

| 種類 | 説明 | 保存先 |
| --- | --- | --- |
| **カスタムスキル** | 自分で作るスキル | `~/.claude/skills/` |
| **example-skills** | Anthropic公式が提供するスキル集 | プラグインとして管理 |

`example-skills` はAnthropicが `anthropics/skills` リポジトリで管理している公式スキル集で、Claude Codeの**プラグイン機能**を通じてインストールします。

---

## インストール方法

### 1. プラグインとしてインストール

```
claude plugins install example-skills@anthropic-agent-skills
```

### 2. インストール確認

### 3. settings.jsonで有効化されているか確認

`~/.claude/settings.json` に以下が追加されていればOKです：

```
{
  "enabledPlugins": {
    "example-skills@anthropic-agent-skills": true
  }
}
```

### 無効化・削除

```
# 一時的に無効化
claude plugins disable example-skills

# 完全に削除
claude plugins uninstall example-skills
```

### インストール先

プラグインは以下にキャッシュされます：

```
~/.claude/plugins/cache/anthropic-agent-skills/example-skills/
```

---

## スキルの使い方

インストール後は2つの方法で呼び出せます。

**① 自然言語でトリガー**（Claudeが自動判断）

```
「このPDFを結合して」 → pdf スキルが自動起動
「WordファイルをExcelに変換して」 → xlsx スキルが自動起動
```

**② スラッシュコマンドで明示的に呼び出す**

スキル名だけをスラッシュコマンドとして入力します（`example-skills:` のプレフィックスは不要）：

```
/doc-coauthoring
/pdf
/frontend-design
/xlsx
```

---

---

## 全スキル一覧

### 📝 ドキュメント・オフィス系

#### `/doc-coauthoring`

**ドキュメント・仕様書・提案書の共同執筆ワークフロー**

こんなときに使う：

* 技術仕様書を一緒に書きたい
* 提案書・設計ドキュメントをゼロから作りたい
* 「あとで読む人がわかるドキュメント」に仕上げたい

```
「認証機能のAPI仕様書を一緒に書いて」
「新機能の提案書を作りたい。要件をヒアリングして整理して」
```

---

#### `/docx`

**Wordファイル（.docx）の作成・編集・操作**

こんなときに使う：

* 報告書・議事録をWord形式で作りたい
* 既存の.docxファイルを編集・内容抽出したい
* 目次・見出し・ページ番号付きの本格的なWord文書を作りたい

```
「この内容をWordファイルにして」
「.docxから本文を抽出して」
```

---

#### `/pdf`

**PDFの読み取り・結合・分割・作成・OCR等**

こんなときに使う：

* 複数のPDFをまとめたい
* PDFからテキストを抽出したい
* スキャンされたPDFをOCRで検索可能にしたい

```
「3つのPDFを1つにまとめて」
「このPDFの内容を読んで要約して」
```

---

#### `/xlsx`

**Excelファイル（.xlsx/.csv等）の作成・編集・変換**

こんなときに使う：

* CSVデータをExcelに変換・整形したい
* スプレッドシートに計算式や書式を追加したい
* 汚いデータをきれいな表に整理したい

```
「このCSVをExcelにして、ヘッダーを太字にして」
「売上データを月別に集計したExcelを作って」
```

---

#### `/pptx`

**PowerPointファイル（.pptx）の作成・編集・読み取り**

こんなときに使う：

* スライドデッキをゼロから作りたい
* 既存のPPTXを編集・テキスト抽出したい
* 構成案からスライドを自動生成したい

```
「この設計内容をPowerPointのスライドにして」
「PPTXから議事録用のテキストを抽出して」
```

---

### 🎨 デザイン・ビジュアル系

#### `/frontend-design`

**高品質なフロントエンドUI・Webコンポーネントの作成**

こんなときに使う：

* 見栄えの良いWebページ・ランディングページを作りたい
* ダッシュボードUIのプロトタイプを素早く作りたい
* デザインクオリティの高いHTMLコンポーネントが欲しい

```
「GitHubの統計データを表示するダッシュボードUIを作って」
「おしゃれなログインページを作って」
```

---

#### `/web-artifacts-builder`

**React + Tailwind + shadcn/uiを使った複雑なHTMLアーティファクト作成**

こんなときに使う：

* 状態管理・ルーティングが必要な複雑なUI
* shadcn/uiコンポーネントを使いたい
* 複数ページ・タブ切り替えのあるインタラクティブなUI

`frontend-design`との違い：より複雑なSPA的なUIに特化。

```
「タブ切り替えで複数ページを持つダッシュボードを作って」
「フィルター・ソート機能付きのデータテーブルを作って」
```

---

#### `/canvas-design`

**PNG/PDFでポスター・アート・デザイン作成**

こんなときに使う：

* イベントポスターを作りたい
* インフォグラフィックを作りたい
* 静的なビジュアルデザインの成果物が欲しい

```
「技術勉強会のポスターを作って」
「アーキテクチャ図をきれいなデザインで作って」
```

---

#### `/algorithmic-art`

**p5.jsを使ったアルゴリズミックアート・ジェネラティブアート生成**

こんなときに使う：

* コードで生成するアートを作りたい
* フローフィールドやパーティクルシステムを試したい
* インタラクティブなビジュアライゼーションを作りたい

```
「フローフィールドを使ったジェネラティブアートを作って」
「シード値で再現可能なアルゴリズミックパターンを作って」
```

---

#### `/theme-factory`

**アーティファクト（スライド・HTML等）へのテーマ適用**

こんなときに使う：

* 作成したアーティファクトに統一感のあるデザインを適用したい
* 10種類のプリセットテーマから選びたい
* カスタムテーマを生成したい

```
「このスライドにダークテーマを適用して」
「このHTMLにミニマルなテーマを当てて」
```

---

#### `/brand-guidelines`

**Anthropicブランドカラー・タイポグラフィの適用**

こんなときに使う：

* Anthropicのブランドに準拠したデザインを作りたい
* 公式カラーパレット・フォントを使いたい

```
「Anthropicのブランドガイドラインに従ってこのUIを作って」
```

---

#### `/slack-gif-creator`

**Slack用アニメーションGIFの作成**

こんなときに使う：

* Slackで使えるアニメーションGIFを作りたい
* Slackの制約（ファイルサイズ・解像度）に最適化したGIFを作りたい

```
「ローディングアニメーションのGIFをSlack用に作って」
```

---

### 🔧 開発・テクニカル系

#### `/claude-api`

**Claude API / Anthropic SDKを使ったアプリ構築**

こんなときに使う：

* コードに `import anthropic` や `@anthropic-ai/sdk` がある
* Claude APIを使ったアプリを作りたい
* Agent SDKでエージェントを構築したい

```
「Claude APIを使ってチャットボットを作って」
「Anthropic SDKでストリーミングレスポンスを実装して」
```

⚠️ `openai` など他のAI SDKには使わない

---

#### `/mcp-builder`

**MCPサーバーの構築ガイド（Python/Node対応）**

こんなときに使う：

* 外部APIをClaudeから使えるMCPサーバーを作りたい
* FastMCP（Python）またはMCP SDK（TypeScript）でツールを実装したい
* Claude Codeに新しい能力を追加したい

```
「SlackのAPIをMCPサーバーとして作って」
「社内DBに接続するMCPサーバーを構築して」
```

---

#### `/webapp-testing`

**Playwrightを使ったローカルWebアプリのテスト・UI検証**

こんなときに使う：

* ブラウザでUIの動作確認をしたい
* フロントエンドのバグをスクリーンショットで確認したい
* ブラウザログを見ながらデバッグしたい

```
「localhost:3000のログインフォームが動くか確認して」
「このページのUIをPlaywrightで検証して」
```

---

#### `/skill-creator`

**新スキルの作成・既存スキルの改善・evalによる評価**

こんなときに使う：

* 自分専用のカスタムスキルを作りたい
* 既存スキルの動作を改善・最適化したい
* スキルの性能をevalで測定したい

```
「毎週のKPIレポートを自動作成するスキルを作って」
「このスキルのトリガー精度を改善して」
```

---

### 💬 コミュニケーション系

#### `/internal-comms`

**社内コミュニケーション文書の作成**

こんなときに使う：

* ステータスレポート・進捗報告を書きたい
* リーダーシップ向けのアップデートを作りたい
* インシデントレポート・FAQを作りたい

```
「今週の開発進捗レポートを書いて」
「障害報告書のドラフトを作って」
```

---

## 迷ったときの選び方

```
何を作りたい？
│
├─ 文書・資料
│   ├─ Word → docx
│   ├─ Excel → xlsx
│   ├─ PowerPoint → pptx
│   ├─ PDF → pdf
│   └─ 社内文書 → internal-comms
│
├─ UI・ビジュアル
│   ├─ Webページ・ダッシュボード（シンプル） → frontend-design
│   ├─ Webページ・ダッシュボード（複雑/SPA） → web-artifacts-builder
│   ├─ ポスター・インフォグラフィック → canvas-design
│   ├─ ジェネラティブアート → algorithmic-art
│   ├─ テーマ適用 → theme-factory
│   └─ Slack用GIF → slack-gif-creator
│
└─ 開発・技術
    ├─ Claude API連携 → claude-api
    ├─ MCPサーバー構築 → mcp-builder
    ├─ WebアプリのUIテスト → webapp-testing
    └─ カスタムスキル作成 → skill-creator
```

---

## まとめ

| カテゴリ | スキル数 | 代表的なユースケース |
| --- | --- | --- |
| ドキュメント・オフィス | 5 | Word/Excel/PDF/PPT作成 |
| デザイン・ビジュアル | 7 | UI・アート・テーマ・GIF |
| 開発・テクニカル | 4 | API・MCP・テスト・スキル作成 |
| コミュニケーション | 1 | 社内文書 |
| ドキュメント共同執筆 | 1 | 仕様書・提案書 |

Claude Codeを使いこなすうえで、これらのスキルを知っておくだけで日常の作業効率が大きく上がります。特に `frontend-design` と `web-artifacts-builder` はプロトタイプ作成に非常に強力です。ぜひ活用してみてください。
