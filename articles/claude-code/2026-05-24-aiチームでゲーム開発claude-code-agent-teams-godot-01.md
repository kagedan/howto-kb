---
id: "2026-05-24-aiチームでゲーム開発claude-code-agent-teams-godot-01"
title: "AIチームでゲーム開発（Claude Code Agent Teams + Godot）"
url: "https://zenn.dev/yurinchi/articles/537a7640b59ee8"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "zenn"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回の記事ではAI活用して画像作成とゲーム開発をしました。  
今回の記事では`Claude Code Agent Teams`を利用して画像作成、ゲーム開発をそれぞれ別のClaude Codeで処理をさせていきます。

### 関連の記事

`MCP`の概要や他のMCPの設定方法については前回の記事を確認してください。  
<https://zenn.dev/yurinchi/articles/879883dc91c3d6>

## Claude Code Agent Teamsとは

公式では以下のように説明されています。

> 複数の Claude Code インスタンスがチームとして連携して動作するように調整し、  
> 共有タスク、エージェント間メッセージング、および一元管理を実現します。

エージェントチームを使用すると、複数の Claude Code インスタンスが連携して動作するようになり、  
実社会の開発チームのように作業を進めることが出来ます。  
1つのセッションがチームリーダーとして機能し、作業を調整し、タスクを割り当て、進捗や状況を管理。  
チームメンバーはそれぞれ独自のコンテキストウィンドウで動作し、互いに情報を連携します

## チーム構成

今回はゲーム開発のために、チームリーダ、デザイナー、プログラマーのチーム構成でゲーム開発を進めます。

* チームリーダ: 進捗の管理、各メンバーへの指示だし
* デザイナー: `PixelLab` を利用してゲームに必要な画像を生成
* プログラマー: `Godot MCP` を利用してゲームを開発

## Claude Codeの設定

### Team Agentの設定

エージェントチームはまだ実験的な機能のため、デフォルトでは無効になっています。  
そのため、settings.json または環境に CLAUDE\_CODE\_EXPERIMENTAL\_AGENT\_TEAMS を追加して有効にする必要があります。

.claude/settings.json

```
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### PixelLab MCPの設定

前回はClaude Desktopでの設定をしましたが、今回はCLIで実施するためClaude Code用の設定をします。

`PixelLab`については下記の記事を参考にしてください。  
<https://zenn.dev/yurinchi/articles/d47c3ca7a573bd>

#### 設定ファイルの修正

.mcp.json

```
{
  "mcpServers": {
    "pixellab": {
      "command": "npx",
      "args": ["pixellab-mcp"],
      "env": {
        "PATH": "${PATH}",
        "PIXELLAB_SECRET": "${PIXELLAB_TOKEN}"
      }
    },
  }
}
```

### Godot MCPの設定

Godotエディタの操作には`tugcantopaloglu/godot-mcp`を使います。  
前回利用したMCPとは違い、Godotエディタ側でプラグインの設定は不要です。

#### インストール

```
git clone https://github.com/tugcantopaloglu/godot-mcp.git
cd godot-mcp
npm install
npm run build
```

#### 設定ファイルの修正

.mcp.json

```
{
  "mcpServers": {
    "godot": {
      "command": "node",
      "args": [
        "tugcantopaloglu-godot-mcpのパス"
      ],
      "env": {
        "GODOT_PATH": "Godotエディタの実行パス",
        "DEBUG": "true"
      }
    }
  }
}
```

最終的にはpixellabと合わせて下記の内容を設定しています。

```
{
  "mcpServers": {
    "pixellab": {
      "command": "npx",
      "args": ["pixellab-mcp"],
      "env": {
        "PATH": "${PATH}",
        "PIXELLAB_SECRET": "${PIXELLAB_TOKEN}"
      }
    },

    "godot": {
      "command": "node",
      "args": [
        "/Users/yurinchi/workspace/claude/MCP/tugcantopaloglu-godot-mcp/build/index.js"
      ],
      "env": {
        "GODOT_PATH": "/Applications/Godot.app/Contents/MacOS/Godot",
        "DEBUG": "true"
      }
    }
  }
}
```

## 指示ファイル(CLAUDE.md)の作成

環境の準備が整ったら大まかな指示を`CLAUDE.md`に記載します。

CLAUDE.md

```
# Claude Code Instructions

- すべてのやり取り、質問、確認事項は日本語で行ってください。
- 技術的な解説も日本語でお願いします。
- ツール（ファイル操作やコマンド実行）を使用する前の確認も、日本語で意図を説明してください。

# 作成するもの

スイカゲーム風パズルゲーム

# 環境

* Godotゲーム開発
* GodotはMCPを利用する
* 利用する画像はPixelLabで生成する
* agent teamsでゲーム開発者とデザイナーのエージェントで分担して作業をする
* ゲームプロジェクトはカレントディレクトリにsuika-gameディレクトリを作成してその中に作成してください

# 注意点

* PixelLabはサブスクリプション契約の為、残高0でも画像生成出来ます。
* ゲーム開発者とデザイナーは並行して作業を進めて後で画像を組み込んでください。
* 最初に必要な画像をチームリーダが考えてからゲーム開発者とデザイナーに依頼をしてください。
* 画像の枚数が多い場合は２人のデザイナーで並行して画像を作成してください。
```

## Claude Codeでゲーム開発の指示

準備が整ったのでClaude Codeを起動しましょう。

起動するとMCPの許可について確認が出るので承認しましょう。

`/mcp list` で`pixellab`と`godot-mcp`が認識でいていることが確認できます。

そうしたらコンソールに指示を出していきましょう。

```
あなたはゲーム開発チームのリーダーです。
agent teams を利用して並列処理してください。
CLAUDE.mdに従い、ゲーム開発者とデザイナーのエージェントチームでスイカゲーム風のパズルゲームを新規に作成して。
また、今回はAgent Teamsのデモ動画として作成してるので利用して並行作業していることを視覚的にわかりやすいように作業を進めてください。
```

実践した内容は動画でも公開しているので良かった参考にしてください。

<https://youtu.be/ZerfdOyz01E>

PixelLabの割引コードも記載しておきます。

* Tier1: DDIATQ\_MONTHLY\_TIER\_1
* Tier2: DDIATQ\_MONTHLY\_TIER\_2
