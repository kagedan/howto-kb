---
id: "2026-06-07-iterm2-で-claude-code-を使うとき止まったら-macos-通知を受け取る方法-01"
title: "iTerm2 で Claude Code を使うとき、止まったら macOS 通知を受け取る方法"
url: "https://qiita.com/like-mountain/items/90f315e65ae99c36e622"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

# 問題

iTerm2 で Claude Code を使っていると、以下のタイミングに気づきにくい。

- Claude の応答が完了した
- コマンド実行の許可・拒否を求めている
- 質問待ちになっている

別の作業をしていると、Claude が止まったまま放置してしまう。

# 解決策

~/.claude/settings.json に hooks を設定することで、各タイミングで macOS 通知を受け取れる。

```
{
  "theme": "light",
  "permissions": {},
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"許可が必要です\" with title \"Claude
Code\"'"
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
            "command": "osascript -e 'display notification \"質問があります\" with title \"Claude Code\"'; echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PreToolUse\", \"permissionDecision\": \"deny\", \"permissionDecisionReason\": \"AskUserQuestion は禁止。テキストで質問して応答ターンを終えること（Stop フック通知のため）。\"}}'"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"完了\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

### 各フックの役割

| フック | タイミング | 動作 |
| --- | --- | --- |
| PermissionRequest | コマンド実行の許可プロンプトが出たとき | 「許可が必要です」と通知 |
| PreToolUse（AskUserQuestion） | Claude が質問ツールを使おうとしたとき | 「質問があります」と通知 + ツールをブロックしテキストで質問させる |
| Stop | Claude の応答ターンが終了したとき | 「完了」と通知 |


### PreToolUse で AskUserQuestion をブロックする理由

Claude が AskUserQuestion ツールを使うと、回答待ちの間は Stop フックが発火しない。
そのため AskUserQuestion を禁止し、代わりにテキストで質問して応答ターンを終わらせることで、Stop
フックの通知が確実に届くようにしている。

### 通知の様子

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3881019/6a2ac5aa-0a3e-4283-af6e-14fed34e29eb.png)


### デュアルディスプレイを使っている場合

2つのディスプレイを使っている場合、macOS の通知は主ディスプレイに表示される。
通知を受け取りたいディスプレイ側を主ディスプレイに設定しておく。

設定場所：システム設定 → ディスプレイ → 主ディスプレイにしたいモニターを選択

# まとめ

この設定により、Claude
の作業中に別のことをしていても、完了・許可待ちのタイミングで通知が来るようになる。
待ち時間を有効に使えるようになった。
