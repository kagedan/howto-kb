---
id: "2026-04-03-claude-code-v2189のfullscreen-renderingモードno-flicke-01"
title: "Claude Code v2.1.89のFullscreen renderingモード（NO_FLICKER）"
url: "https://zenn.dev/firstloop_tech/articles/6c6cb8d4e77bd6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

こんにちは、ファーストループテクノロジーの彦坂です。

2026年4月1日リリースのClaude Code **v2.1.89**で、ターミナルのちらつきを抑える**Fullscreen rendering**モードが追加されました。環境変数 `CLAUDE_CODE_NO_FLICKER=1` で有効になります。現時点ではResearch previewの扱いです。

## 背景

筆者の環境では、SSH経由やスマホからTermiusで接続し、tmux上でClaude Codeを使用しています。この構成では、長時間のセッションでログが蓄積してくるとターミナル描画のちらつきが顕著になっていました。

対策として、DEC 2026（Synchronized Output）に対応したGhosttyターミナルを導入しました。Synchronized Outputは、アプリケーションの描画をバッファリングしてから一括で画面に反映する仕組みで、ちらつき対策としては正攻法です。しかし、Claude Codeのちらつきはスクロールバックバッファへの繰り返し再描画が根本原因であり、tmux経由ではSynchronized Outputの伝搬にも制約があるため、完全な解消には至りませんでした。

今回追加されたFullscreen renderingは、描画先自体を代替スクリーンバッファに切り替えるため、より根本的な対策になります。

## 概要

通常、Claude Codeはターミナルのスクロールバックバッファに直接描画します。Fullscreen renderingでは、`vim`や`htop`と同様の**代替スクリーンバッファ（alt-screen）** を使用します。画面全体を一括更新するため、ストリーミング出力時のちらつきが軽減されます。

## 設定方法

3通りの方法があります。

### 1. 起動時に環境変数を指定

ターミナルからClaude Codeを起動する際に、環境変数を付けて実行します。この起動時のみ有効です。

```
CLAUDE_CODE_NO_FLICKER=1 claude
```

### 2. シェルプロファイルに追記

`~/.zshrc` や `~/.bashrc` に追加すると、以降のすべてのセッションで有効になります。

```
export CLAUDE_CODE_NO_FLICKER=1
```

### 3. Claude Codeの設定ファイル

`~/.claude/settings.json` に記述する方法です。

```
{
  "env": {
    "CLAUDE_CODE_NO_FLICKER": "1"
  }
}
```

## 通常モードとの比較

| 項目 | 通常モード | Fullscreen rendering |
| --- | --- | --- |
| スクリーンバッファ | スクロールバック | 代替スクリーンバッファ |
| 入力欄の位置 | 出力に追従して移動 | 画面下部に固定 |
| メモリ使用量 | 会話履歴全体を保持 | 表示部分のみ保持 |
| テキスト検索 | `Cmd+F`で直接検索 | `Ctrl+O` → `/`で検索 |
| マウス操作 | ターミナル依存 | Claude Code側でクリック・スクロール対応 |

入力欄が画面下部に固定されるため、長い出力のストリーミング中に画面が流れません。メモリ使用量も表示部分のみに抑えられるため、長時間セッションでの安定性が向上します。

## 関連する環境変数

Fullscreen renderingモードで併用できる環境変数です。

```
# マウス機能を無効化（SSHやtmux内で有用）
export CLAUDE_CODE_DISABLE_MOUSE=1

# マウスホイールのスクロール速度（1〜20、デフォルト: 3）
export CLAUDE_CODE_SCROLL_SPEED=3
```

## 注意点

* Research previewのため、今後のアップデートで挙動が変わる可能性があります
* Claude Code **v2.1.89以降**が必要です
* テキスト検索の操作方法が通常のターミナルと異なります（`Ctrl+O` → `/`）
* tmux内で使用する場合、マウス関連の設定が競合する場合があります
