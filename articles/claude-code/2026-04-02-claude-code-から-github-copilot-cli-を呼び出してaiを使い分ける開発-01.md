---
id: "2026-04-02-claude-code-から-github-copilot-cli-を呼び出してaiを使い分ける開発-01"
title: "Claude Code から GitHub Copilot CLI を呼び出して、AIを使い分ける開発フロー"
url: "https://zenn.dev/geeknees/articles/829542e8b243b4"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "Gemini", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

## はじめに

Claude Code でコーディングしていて、「この判断は GitHub Copilot にも聞いてみたい」「Copilot のコードサジェストを今すぐ使いたい」と感じたことはありませんか?

`claude-plugin-opinionated` は、Claude Code のセッション内から `/delegate-copilot` コマンドで **GitHub Copilot CLI を直接呼び出せる**ようにするプラグインです。Claude を起点に、GitHub Copilot・Gemini・Codex へタスクを委譲できます。

<https://github.com/geeknees/claude-plugin-opinionated>

## 何ができるのか

このプラグインを使うと、Claude Code から以下のコマンドで各AIエージェントへ委譲できます:

* `/delegate-copilot` - **GitHub Copilot CLI** に委譲 ← 今回やったこと！
* `/delegate-claude` - Claude CLIに委譲
* `/delegate-codex` - OpenAI Codex CLIに委譲
* `/delegate-gemini` - Google Gemini CLIに委譲

### ユースケース

1. **Copilot のセカンドオピニオン**: Claude が提案した実装を Copilot にもレビューしてもらう
2. **Copilot の強みを活かす**: GitHub リポジトリ知識やコード補完の精度で Copilot が得意な場面に切り替える
3. **負荷分散**: レート制限やトークン消費を複数のAIサービスに分散
4. **多角的なコードレビュー**: Claude + Copilot + Gemini の3者それぞれの意見を集める

## 動作の仕組み

各スキルは非常にシンプルで、対応するローカルCLIコマンドを実行するだけです:

| スキル | 実行コマンド |
| --- | --- |
| `delegate-copilot` | `copilot -p "$ARGUMENTS" --allow-all-tools` |
| `delegate-claude` | `claude -p "$ARGUMENTS"` |
| `delegate-codex` | `codex exec "$ARGUMENTS"` |
| `delegate-gemini` | `gemini -p "$ARGUMENTS"` |

`/delegate-copilot` は `--allow-all-tools` フラグ付きで呼び出すため、Copilot CLI がファイル操作や検索などのツールを使いながら回答を構築できます。

## インストール方法

### 前提条件

各CLIツールがローカルにインストールされ、認証済みである必要があります。

### Claude Codeでプラグインとしてインストール

GitHubにリポジトリをプッシュ後:

```
/plugin marketplace add geeknees/claude-plugin-opinionated
/plugin install delegate-claude@claude-plugin-opinionated
/plugin install delegate-codex@claude-plugin-opinionated
/plugin install delegate-gemini@claude-plugin-opinionated
/plugin install delegate-copilot@claude-plugin-opinionated
```

### skills.shでスキルとしてインストール

```
npx skills add geeknees/claude-plugin-opinionated --skill delegate-claude
npx skills add geeknees/claude-plugin-opinionated --skill delegate-codex
npx skills add geeknees/claude-plugin-opinionated --skill delegate-gemini
npx skills add geeknees/claude-plugin-opinionated --skill delegate-copilot
```

## 使い方

インストール後、`/delegate-*` コマンドで具体的なリクエストを送ります。差分、コード、エラー出力、設計コンテキストなどの関連情報を含めると効果的です。

### 基本的な使用例

```
# Claude Codeのセッション内で Copilot に委譲
/delegate-copilot このアプローチとキューベースの設計を比較して

/delegate-copilot この実装をレビューして。特にパフォーマンスとセキュリティの観点で

/delegate-copilot このdiffの正しさ、エッジケース、保守性をレビューして
```

### 実践的な活用シナリオ

#### シナリオ1: Claude で実装 → Copilot でレビュー

Claude Code で実装を進め、仕上げに Copilot の目でレビューしてもらいます:

```
# Claude Codeで実装完了後
/delegate-copilot この実装をレビューして。特にパフォーマンスとセキュリティの観点で

# Copilotの指摘を受けてさらにGeminiにも
/delegate-gemini このコードの改善点を教えて。特にエラーハンドリングについて
```

#### シナリオ2: レート制限の回避

Claude がレート制限に達したとき、Copilot に引き継ぎます:

```
/delegate-copilot 残りのテストケースを実装して
```

#### シナリオ3: 得意分野の使い分け

```
# アーキテクチャ設計はClaude
/delegate-claude このマイクロサービスアーキテクチャの設計を評価して

# 実装の最適化はCopilot
/delegate-copilot この処理を並列化する実装を提案して
```

#### シナリオ4: 💥 この記事自体の執筆 (実践例) 💥

実はこの記事のベースも、Claude Code から Copilot CLI に委譲して生成しています。Claude がリポジトリを解析し、`/delegate-copilot` で Copilot に記事執筆を依頼しました。AIがAIを呼んで記事を書く、というユースケースです。

## 注意点

### Geminiの制約

Geminiは多くのヘッドレス環境でワークスペースを自由に検査できないため、コードレビューやデバッグに使う際は、関連する差分、ファイル内容、エラー出力を事前に提供する必要があります。

### カスタマイズ

インストールされているコマンド名が `claude`、`codex`、`gemini`、`copilot` でない場合は、各スキルのコマンドを調整してください。

## リポジトリ構成

```
.
├── .claude-plugin/
│   └── marketplace.json
└── skills/
    ├── delegate-claude/
    │   └── SKILL.md
    ├── delegate-codex/
    │   └── SKILL.md
    ├── delegate-gemini/
    │   └── SKILL.md
    └── delegate-copilot/
        └── SKILL.md
```

各スキルは意図的に最小限に保たれており、対応するローカルCLIに委譲するだけのシンプルな設計になっています。

## まとめ

`claude-plugin-opinionated` を使うことで:

✅ Claude Code から `/delegate-copilot` で GitHub Copilot CLI をワンコマンド呼び出しできる  
✅ Claude + Copilot の長所を組み合わせたレビューフローが作れる  
✅ トークン使用量とレート制限を複数AIに分散できる  
✅ タスクの性質に応じて最適なAIを選択できる

「Claude だけ」「Copilot だけ」の時代から、**AIを使い分けるチーム開発**へ。ぜひ試してみてください。

## （おまけ）実際のトークン使用量

この記事の執筆フロー（Claude Code が `/delegate-copilot` を呼び出し、Copilot CLI がサブエージェントとして記事を生成）で実際に消費されたトークンは以下のとおりです。最後にClaudeに聞いて集計してもらいました。

### 親エージェント: Claude Code

| モデル | Input tokens | Output tokens | Cache read | Cache creation |
| --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | 78 | 13,160 | 2,093,447 | 287,131 |

Cache read が約200万トークンと突出しています。Claude Code がシステムプロンプトやコンテキストをキャッシュしながら動作しているためです。

### サブエージェント: GitHub Copilot CLI

Copilot CLI は内部でさらに複数のモデルを呼び出しています:

| モデル | Input tokens | Output tokens | Cached tokens | 推定コスト |
| --- | --- | --- | --- | --- |
| claude-sonnet-4.5 | 75,600 | 1,400 | 25,600 | Est. 1 Premium request |
| claude-opus-4.5 | 141,900 | 1,700 | 105,000 | Est. 0 Premium requests |

**Copilot CLI セッション合計**

| 指標 | 値 |
| --- | --- |
| 合計推定コスト | Premium request × 1 |
| API 処理時間 | 1m 8s |
| セッション合計時間 | 1m 13s |

委譲先の Copilot CLI 内部でもサブエージェントが動くため、コンテキストが積み上がります。キャッシュが効いている部分（`cached tokens`）が多いほどコスト効率が上がります。Copilot CLI 側だけで **約22万トークン**が処理されており、AIのネスト呼び出しにはそれなりのトークン消費が伴うことがわかります。

## リンク
