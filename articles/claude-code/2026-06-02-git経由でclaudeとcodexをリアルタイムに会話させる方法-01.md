---
id: "2026-06-02-git経由でclaudeとcodexをリアルタイムに会話させる方法-01"
title: "Git経由で、ClaudeとCodexをリアルタイムに会話させる方法"
url: "https://qiita.com/Koukyosyumei/items/92112f2e783cec2e036e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "qiita"]
date_published: "2026-06-02"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

Claude CodeやCodexのようなコーディングエージェントは、ソフトウェア開発の自動化を大きく前進させました。一方で、単一エージェントのコンテキストウィンドウには限界があり、大規模なリポジトリでは複数のエージェントに並列で作業させたい場面も増えています。

そこで新たに課題になるのが、**複数のAIエージェントが、コンテキストを失わずにどのように協調するか**です。

この記事では、次世代のAI-aware Gitツールである [h5i](https://github.com/h5i-dev/h5i) のバージョン `0.1.5` で実装されたマルチエージェント向けメッセージング機能、**Agent Radio（`h5i msg`）** を紹介します。

Agent Radioを使うと、Claude CodeやCodexのようなコーディングエージェントが、まるでリアルタイムに会話しているかのように、実装方針を相談したり、作業内容を共有したりできます。さらに、やり取りはすべてGit上で自動的に記録・バージョン管理されるため、エージェント同士のコミュニケーション履歴をあとから監査できます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2959953/555c572d-dfb1-4933-96fb-b632c59c3725.png)

## インストールとセットアップ

`h5i` のインストールは簡単です。

```bash
curl -fsSL https://raw.githubusercontent.com/Koukyosyumei/h5i/main/install.sh | sh
```

次に、既存のGitリポジトリに移動して、`h5i` を初期化します。

```bash
h5i init
h5i msg setup
```

これで、Claude CodeとCodexをリアルタイムに会話させる準備ができました。

別々のターミナルを2つ開き、それぞれでClaude CodeとCodexを起動します。

例えばClaude側には、次のように依頼します。

> h5iを使い、てCodexと一緒に、次世代の深層学習フレームワークのより良い設計を考えてください。

Codex側には、次のように依頼します。

> h5iを使い、Claudeと一緒に、次世代の深層学習フレームワークのより良い設計を考えてください。

これにより、ClaudeとCodexが `h5i msg` を介して互いにメッセージを送り合いながら、設計について議論できます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2959953/4bfac583-4f09-48f2-b0bb-760b97243bf5.png)

また、別のターミナルから次のコマンドを実行すると、エージェント同士の会話をリアルタイムに監視できます。

```bash
h5i msg watch
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2959953/1fdc5852-2d4d-45df-a1a4-268e7ecf86c1.png)

さらに、会話内容のサマリーをGitHub Pull Requestに投稿することもできます。

```bash
h5i share pr post
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2959953/45c57952-96e4-4d22-8e33-f8dd9b5b4ad8.png)


## 仕組み

`h5i msg` は内部的に **i5h protocol** を利用しています。i5hは **Inter-Agent Information & Interaction Handshake** の略で、コーディングエージェントや人間の開発者が、Gitリポジトリを共有基盤として、型付きの作業引き継ぎメッセージを交換するための小さなプロトコルです。

特徴はシンプルで、外部サーバーも、ソケット通信も、スキーマレジストリも必要ありません。メッセージは1行1JSONの形式で、Git refである `refs/h5i/msg` 内の `messages.jsonl` に追記されます。各メッセージには、人間にも読みやすい7つの必須フィールドがあります。返信する場合は、`reply_to` で元のメッセージを指す新しい行を追加するだけです。会話を共有も簡単で、Git refをpush/pullだけで他の人と会話履歴をシェアできます。

また、各メッセージは immutable であり、`id` によって一意に識別されます。そのため、2つのクローンで会話履歴が分岐しても、単純な集合和としてマージできます。つまり、競合の起きにくい grow-only log として扱えます。

## まとめ

Agent Radioは、Gitを通じてコーディングエージェント同士のリアルタイム協調を可能にする仕組みです。

Claude Code、Codex、その他のエージェントは、外部サーバーや複雑なインフラを必要とせず、共有されたGitリポジトリ上でタスク、コンテキスト、フィードバックをやり取りできます。

さらに、すべてのメッセージはGit上で自動的にバージョン管理されるため、エージェントのやり取りをコード変更と同じように、透明で再現可能な履歴として残せます。

リポジトリはこちらです。https://github.com/h5i-dev/h5i
