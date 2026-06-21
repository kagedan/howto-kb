---
id: "2026-06-20-claude-code活用zenn記事をclaude-codeに書かせる-01"
title: "【Claude Code活用】Zenn記事をClaude Codeに書かせる"
url: "https://zenn.dev/pekopugu/articles/agent01-b8-zenn-article"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

## Claude Code で記事を書く発想

「コードを実装した Claude Code が、記事も書けるのでは？」

これが Series A・B 全16本の記事を Claude Code で生成することにした出発点です。

Claude Code は実装コードを直接読めるため、コードの引用が正確です。また PROGRESS.md に記録した「躓いた点・気づき」も参照できるため、体験談として具体性のある記事が生成できます。

## 記事生成指示書の設計

Claude.ai（claude.ai）で **記事生成指示書** を作成し、それを Claude Code に渡す形式を採用しました。

指示書には以下の要素を明記しています。

```
# Zenn記事生成指示書：Series B 全8本

## 共通ルール

- 全記事に以下の `:::message` ブロックを冒頭に追加する
- `published: false` のまま作成する
- コードブロックにはファイルパスを明記する
- 「です・ます」調で統一する
- 1500〜2500字を目安にする

## B2：ファイル読み書きを任せる

### フロントマター

```yaml
---
title: "【Claude Code活用】ファイル読み書きを任せる"
emoji: "📁"
...
```

### 構成

#### ## Claude Codeのファイル操作能力
- Read / Write / Edit の3つの基本操作
- ...
```

「参照ファイル・記事構成・文体ルール」を明記することで、Claude Code が記事のアウトラインを迷わず実装できます。

## 実際の生成フロー

Series B 全8本の生成フローは以下のとおりです。

```
Claude（claude.ai）
  ↓ 記事生成指示書を作成
  ↓ 参照すべきソースコードと PROGRESS.md を指定

Claude Code（zenn-contentsフォルダで起動）
  ↓ agent01 リポジトリのコードを読む
  ↓ PROGRESS.md の気づき・躓いた点を参照する
  ↓ 指示書に従って記事 md ファイルを生成
  ↓ git add → git commit → git push

人間
  ↓ 生成された記事をレビュー
  ↓ 修正指示 → Claude Code が修正
  ↓ published: true に変更して公開
```

Claude Code はコードを読みながら記事を生成するため、コードブロックの内容と本文の説明が一致しています。手書きで記事を書く場合に発生しがちな「コードを貼り忘れる」「説明とコードが食い違う」という問題が起きにくいです。

## 品質管理：人間のレビューが重要

生成された記事に対して、Claude.ai でレビューと修正指示を行いました。

確認のポイントは以下です。

* **技術的正確性**：コードの引用が正しいか、実際の動作と一致しているか
* **読みやすさ**：記事の流れが自然か、見出し構成が適切か
* **独自性**：「躓いた点・気づき」が体験談として具体的か
* **フォーマット**：フロントマター・シリーズリンク・`:::message` ブロックが揃っているか

`published: false` で作成してレビュー・修正後に `published: true` に変更することで、未完成の記事が公開される事故を防いでいます。

## 気づき

**実装コードを直接引用するため技術的な正確性が高い**：Claude Code は agent01 の `src/tools/file_tools.py` などを実際に読んでから記事を生成します。「このコードを書いた経験」を持つ Claude Code が記事を書くため、コード説明の正確性が高くなります。

**躓いた点の記録（PROGRESS.md）が記事の差別化ポイントになった**：「Windows の cp932 エンコーディング問題」「llama3.1:8b のツール呼び出しの安定性と日本語品質の課題」といった具体的な体験談は、PROGRESS.md に記録されていたものです。こうした一次情報を含む記事は、汎用的な解説記事との差別化になります。

**Series A 全8本もこのフローで作成できた**：AIエージェントの実装体験を Series A（コード解説）として、Claude Code の活用方法を Series B（ツール活用）として、同じフローで16本の記事を生成しました。開発とドキュメント生成を同時並行で進められる点が最大のメリットです。

**記事生成指示書は Claude.ai で設計する**：記事の構成・文体・引用するコード箇所を指示書に落とし込む作業は Claude.ai が担当します。Claude Code は指示書を忠実に実行する役割に専念させることで、品質が安定しました。

## まとめ

Claude Code を使った Zenn 記事生成フローは、「Claude.ai が設計した指示書を Claude Code が実行する」という分業体制で成り立っています。実装コードを直接引用できること、PROGRESS.md の体験談を素材にできることが、このフローの強みです。

Series B はこの記事で完結です。Series C では、SKILL.md や CLAUDE.md を使った AI 指示書の設計・管理手法を紹介する予定です。

## シリーズリンク（Series B）
