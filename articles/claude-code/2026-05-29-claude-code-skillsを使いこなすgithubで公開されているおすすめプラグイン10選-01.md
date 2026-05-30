---
id: "2026-05-29-claude-code-skillsを使いこなすgithubで公開されているおすすめプラグイン10選-01"
title: "Claude Code Skillsを使いこなす：GitHubで公開されているおすすめプラグイン10選と導入方法"
url: "https://qiita.com/satoshi_061/items/c8c097b0ff17ee5f437b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "TypeScript", "qiita"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

# Claude Code Skillsを使いこなす：GitHubで公開されているおすすめプラグイン10選と導入方法

Claude CodeにはGitHubで公開されている **Skills（スキル）** を追加することで、機能を大幅に拡張できます。この記事では、Skillsの仕組みから導入方法、おすすめのスキルまでをまとめて紹介します。

## Skillsとは？

Skillsは `SKILL.md` というファイルで定義された **再利用可能な指示セット** です。プロジェクトに追加しておくと、Claude Codeが関連するタスクを検出したときに自動的に読み込んで活用してくれます。

たとえば「記事を書いて」と指示するだけで、SEO最適化の知識を持ったスキルが自動発動し、高品質な記事を生成してくれます。

### Skillsの特徴
- **自動発動**：タスク内容からClaudeが適切なスキルを判断して適用
- **手動呼び出し**：`/skill-name` で明示的に呼び出すことも可能
- **プロジェクト単位**：フォルダごとに異なるスキルセットを管理できる
- **マルチエージェント対応**：Cursor・GitHub Copilot・Codex CLIなど他ツールにも対応

---

## インストール方法の種類

Skillsのインストール方法は主に2種類あります。

### 方法①：`npx skills add`（CLIから）

ターミナルでプロジェクトフォルダに移動して実行します。

```bash
cd your-project
npx skills add vercel-labs/agent-skills
```

**特徴：**
- コマンド一発で完結
- [agentskills.io](https://agentskills.io) オープン標準に準拠
- Claude Code以外のエージェントにも横断的にインストール

### 方法②：`/plugin marketplace add`（Claude Code内から）

Claude Codeのチャット内で実行します。

```
/plugin marketplace add muratcankoylan/Agent-Skills-for-Context-Engineering
```

その後、個別スキルをインストール：

```
/plugin install context-engineering@context-engineering-marketplace
```

**特徴：**
- Claude Code専用のプラグイン管理UI
- マーケットプレイスとして登録後、複数スキルをブラウズして選べる
- コミュニティ製スキルに多い形式

### どちらを使えばいい？

| | `npx skills add` | `/plugin marketplace add` |
|---|---|---|
| 実行場所 | ターミナル | Claude Codeチャット内 |
| 対象 | 複数エージェント対応 | Claude Code専用 |
| 向いてる場面 | 手早く入れたいとき | 複数スキルをブラウズしたいとき |

最終的にやること（SKILL.mdをプロジェクトに配置）は同じで、インストール後の使い方も変わりません。

---

## 自動適用の仕組み

Skillsはプロジェクトの `.agents/skills/` ディレクトリに配置されます。

```
your-project/
└── .agents/
    └── skills/
        ├── blog-write/
        │   └── SKILL.md
        └── keyword-research/
            └── SKILL.md
```

**重要：スキルはそのフォルダでClaude Codeを起動したときのみ有効です。**

各スキルの `SKILL.md` には `description` フィールドがあり、トリガーワードが定義されています。

```yaml
---
name: blog-write
description: >
  Write new blog articles from scratch...
  Use when user says "write blog", "new blog post", "create article".
user-invokable: true
---
```

「記事を書いて」「ブログを作成して」などの指示を出すと、descriptionのトリガーワードにマッチして自動発動します。

---

## おすすめSkills 10選

### 開発系

#### 1. Vercel React Best Practices
React/Next.jsのパフォーマンス最適化ガイド。Vercel公式エンジニアの知見が詰まった70ルールを収録。

```bash
npx skills add vercel-labs/agent-skills
```

コンポーネント生成時にメモ化・アクセシビリティ・バンドルサイズ最適化などが自動反映されます。

#### 2. Mastering TypeScript
企業レベルのTypeScript型安全パターン。React・NestJS対応。

```bash
npx skills add SpillwaveSolutions/mastering-typescript-skill
```

#### 3. React Claude Skill Package
React 18/19向け24スキル。Hooks・Server Components・テスト・パフォーマンス最適化を網羅。

```bash
npx skills add OpenAEC-Foundation/React-Claude-Skill-Package
```

#### 4. Frontend Design（Anthropic公式）
React + Tailwind CSS + shadcn/uiを使ったUI実装スキル。Anthropic公式提供。

```bash
npx skills add anthropics/claude-code
```

---

### コンテンツ・ブログ執筆系

#### 5. Claude Blog
ブログ執筆特化の30スキルセット。SEO・AI引用最適化・多言語対応まで対応。

```bash
npx skills add AgriciDaniel/claude-blog
```

主なスキル：
- `blog-write` — 記事執筆（SEO最適化済み）
- `blog-outline` — 構成作成
- `blog-strategy` — コンテンツ戦略
- `blog-repurpose` — 記事の二次利用
- `blog-calendar` — 投稿カレンダー作成
- `blog-factcheck` — ファクトチェック

#### 6. SEO & GEO Claude Skills
キーワードリサーチからコンテンツ執筆まで20スキル収録。

```bash
npx skills add aaron-he-zhu/seo-geo-claude-skills
```

主なスキル：
- `keyword-research` — キーワードリサーチ
- `seo-content-writer` — SEOコンテンツ執筆
- `competitor-analysis` — 競合分析
- `content-gap-analysis` — コンテンツギャップ分析
- `content-refresher` — 既存記事の更新最適化

---

### エージェント・コンテキスト管理系

#### 7. Agent Skills for Context Engineering
コンテキストウィンドウ管理・マルチエージェントアーキテクチャ向け15スキル。

```
/plugin marketplace add muratcankoylan/Agent-Skills-for-Context-Engineering
```

#### 8. Context Engineering Kit
エージェントの結果品質向上に特化。トークン効率を重視した設計。

```bash
npx skills add NeoLabHQ/context-engineering-kit
```

---

### 総合・大規模コレクション

#### 9. Awesome Agent Skills（VoltAgent）
Vercel・Stripe・Cloudflare・Netlify・Figma・Sentry・Hugging Faceなど有名企業公式スキルを1000件以上収録。

```bash
npx skills add VoltAgent/awesome-agent-skills
```

#### 10. Claude Skills（alirezarezvani）
329スキル収録。エンジニアリング・マーケ・セキュリティ・財務など幅広いカテゴリ。

```bash
npx skills add alirezarezvani/claude-skills
```

---

## 用途別おすすめ組み合わせ

### Reactアプリ開発

```bash
npx skills add vercel-labs/agent-skills
npx skills add OpenAEC-Foundation/React-Claude-Skill-Package
```

### 技術ブログ・Qiita記事執筆

```bash
npx skills add AgriciDaniel/claude-blog
npx skills add aaron-he-zhu/seo-geo-claude-skills
```

### AIエージェント開発

```bash
npx skills add NeoLabHQ/context-engineering-kit
/plugin marketplace add muratcankoylan/Agent-Skills-for-Context-Engineering
```

---

## セキュリティについて

インストール時にセキュリティリスク評価が表示されます。

```
blog        Safe    1 alert    Critical Risk
seo-writer  Safe    0 alerts   Med Risk
```

- **Gen / Socket**：コード解析ベースのリスク評価
- **Snyk**：依存関係の脆弱性チェック

`Critical Risk` のスキルは使用前に `SKILL.md` の内容を一読することを推奨します。インストール後のスキルは **フルエージェント権限** で動作するため、信頼できるソースのものを選びましょう。

---

## まとめ

| 用途 | おすすめSkill |
|---|---|
| React開発品質向上 | `vercel-labs/agent-skills` |
| TypeScript型安全 | `SpillwaveSolutions/mastering-typescript-skill` |
| 記事執筆・SEO | `AgriciDaniel/claude-blog` |
| キーワード・競合分析 | `aaron-he-zhu/seo-geo-claude-skills` |
| コンテキスト管理 | `NeoLabHQ/context-engineering-kit` |
| 全部入り | `VoltAgent/awesome-agent-skills` |

2025年中頃は約50スキルだったのが、2026年には1000件以上に急増しています。エコシステムはまだ成長中なので、定期的にチェックしてみてください。

---

## 参考リンク

- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [agentskills.io - オープン標準](https://agentskills.io)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- [AgriciDaniel/claude-blog](https://github.com/AgriciDaniel/claude-blog)
- [aaron-he-zhu/seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
