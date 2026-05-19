---
id: "2026-05-18-claude-code-の作業完了を音で知らせるhooks-設定-01"
title: "Claude Code の作業完了を音で知らせる（Hooks 設定）"
url: "https://zenn.dev/westhouse_k/articles/6a6fb41ca9409a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code の作業完了・質問・権限要求を、**Hooks** で macOS の標準サウンドに鳴らし分ける設定をまとめます。

## Hooks とは

Hooks は Claude Code 側のイベントに対して、ユーザーが定義したコマンドをフックさせる仕組みです。代表的なイベントは以下のとおりです。

| イベント | 発火タイミング |
| --- | --- |
| `Stop` | アシスタントが応答を終え、ユーザー入力待ちになったとき |
| `PreToolUse` | ツールを実行する直前（matcher でツール名を絞れる） |
| `PostToolUse` | ツール実行が終わった直後 |
| `PermissionRequest` | 権限の許可を求めるダイアログが出るとき |
| `Notification` | 通知が発生したとき |

設定は `~/.claude/settings.json`（ユーザー全体）または `.claude/settings.json`（プロジェクト単位）に書きます。

## 設定方法

macOS の `afplay` コマンドで、`/System/Library/Sounds/` 配下の標準サウンドを鳴らします。`~/.claude/settings.json` に次のように追記します。

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Funk.aiff 2>/dev/null || true"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "AskUserQuestion",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true"
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Submarine.aiff 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

ポイントは以下のとおりです。

* **`Stop`**：作業が一区切りついたタイミング。一番よく鳴る音なので、自分にとって耳障りでないものを選ぶ
* **`PreToolUse` + `matcher: "AskUserQuestion"`**：`AskUserQuestion` ツールが発火する直前に鳴る。要するに「Claude が質問してきた」ときの通知
* **`PermissionRequest`**：許可ダイアログが出たとき。これを聞き逃すと作業が止まってしまうので、一番目立つ音にしておくと安全

末尾の `2>/dev/null || true` は、サウンドファイルが見つからない環境（例: Linux）でフックが失敗しても Claude Code 側に影響を出さないための保険です。

## 音の選び方

`/System/Library/Sounds/` には次のような `.aiff` ファイルが揃っています。

```
$ ls /System/Library/Sounds/
Basso.aiff     Frog.aiff      Hero.aiff      Pop.aiff       Submarine.aiff
Blow.aiff      Funk.aiff      Morse.aiff     Purr.aiff      Tink.aiff
Bottle.aiff    Glass.aiff     Ping.aiff      Sosumi.aiff
```

事前に試聴してから割り当てると失敗が少ないです。

```
afplay /System/Library/Sounds/Funk.aiff
afplay /System/Library/Sounds/Glass.aiff
afplay /System/Library/Sounds/Submarine.aiff
```

私の使い分けは次のような基準にしています。

| イベント | 音 | 理由 |
| --- | --- | --- |
| `Stop` | Funk | 短くて軽い。何度鳴っても疲れない |
| `AskUserQuestion` | Glass | 澄んだ音で「ちょっと聞きたいことがある」感が出る |
| `PermissionRequest` | Submarine | 低音で目立つ。聞き逃したくない通知に向く |

## 設定後の動作確認

設定を反映させるには Claude Code を再起動します。その後、適当なタスクを依頼して、

1. 応答が終わったタイミングで `Funk` が鳴る
2. `AskUserQuestion` を使った質問が来たタイミングで `Glass` が鳴る
3. ファイル編集など権限が必要な操作で `Submarine` が鳴る

の3つを確認できれば成功です。

うまく鳴らないときは、ターミナルから直接 `afplay` が動くか確認してみてください。OS のサウンド出力先（AirPods が別デバイスを掴んでいるなど）が原因のことも多いです。

## まとめ

* Claude Code の **Hooks** を使うと、ライフサイクルイベントに任意のコマンドをぶら下げられる
* `~/.claude/settings.json` に `Stop` / `PreToolUse(AskUserQuestion)` / `PermissionRequest` を仕込むと、作業完了・質問・許可要求を **音で鳴らし分け** できる
* macOS なら `afplay` + `/System/Library/Sounds/` の標準サウンドで十分

「Claude Code に任せた作業が終わるたびにターミナルを覗きに行く」習慣がなくなるだけで、体感の生産性はかなり上がります。ぜひお試しください。
