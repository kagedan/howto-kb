---
id: "2026-06-19-あ気づいたらauto-compactを防ぐclaude-codeのコンテキスト使用率をmacos通知-01"
title: "「あ、気づいたらauto-compact...」を防ぐ。Claude Codeのコンテキスト使用率をmacOS通知してみる"
url: "https://qiita.com/_kuma/items/39607de8bd7c950f3136"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

# うげっ！auto compact動き出した...！！

## はじめに

Claude Code を長時間使っていると、気づいたら突然 **auto-compact** が走っていた、という経験はないでしょうか。

ステータスラインにコンテキスト使用率を出しているのですが、常時表示されていると逆に目に入らなくなってくるんですよね。気づいたら auto-compactが走り出している...なんてことが頻発しており困った困った。
ということでこの記事では、Claude Code の `statusLine` スクリプトに **コンテキスト使用率の閾値通知** を追加する方法を紹介します。

元々出していたstatusLineの基本的な設定は、以下の記事を参考にさせていただきました！

https://qiita.com/dai_chi/items/d72ec42444d66e88a044

---

## やること

- 使用率が 60 / 70 / 80 / 90% を超えたタイミングで **macOS 通知を1回だけ**送る
- セッション終了時に state ファイルをクリーンアップする

---

## 実装

### 1. statusLine スクリプトに通知ロジックを追加

既存の statusLine スクリプトに以下のブロックを追加します。`context_window.used_percentage` と `session_id` は statusLine に渡ってくる JSON から取得できます。

```sh
# コンテキスト使用率と session_id を取得
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
session_id=$(echo "$input" | jq -r '.session_id // "default"')

if [ -n "$used" ]; then
  used_int=$(printf '%.0f' "$used")

  # 閾値を超えたタイミングで macOS 通知（セッションごとに1回のみ）
  state_file="/tmp/.claude-ctx-warn-${session_id}"
  last=$(cat "$state_file" 2>/dev/null || echo "0")
  new=0
  [ "$used_int" -ge 90 ] && new=90
  [ "$new" -eq 0 ] && [ "$used_int" -ge 80 ] && new=80
  [ "$new" -eq 0 ] && [ "$used_int" -ge 70 ] && new=70
  [ "$new" -eq 0 ] && [ "$used_int" -ge 60 ] && new=60
  if [ "$new" -gt "$last" ]; then
    echo "$new" > "$state_file"
    case "$new" in
      60) osascript -e 'display notification "あ、60%超えた。まあまだ全然いける" with title "Claude Code" subtitle "コンテキスト通知" sound name "Glass"' & ;;
      70) osascript -e 'display notification "70%ね〜 なんとなく意識しといて" with title "Claude Code" subtitle "コンテキスト通知" sound name "Glass"' & ;;
      80) osascript -e 'display notification "80%きたよ。そろそろかもね" with title "Claude Code" subtitle "コンテキスト通知" sound name "Glass"' & ;;
      90) osascript -e 'display notification "90%！もうすぐ auto-compact 来るっぽい" with title "Claude Code" subtitle "コンテキスト通知" sound name "Glass"' & ;;
    esac
  fi
fi
```

`display notification` のパラメータは以下のとおりです。

| パラメータ | 説明 |
|-----------|------|
| 第1引数（文字列） | 通知本文 |
| `with title` | 通知のタイトル |
| `subtitle` | タイトル下のサブタイトル |
| `sound name` | 通知音。`"Glass"` の他に `"Basso"` `"Blow"` `"Funk"` など macOS 標準のサウンド名が使える |

ちなみに、通知音はいくつか選べますが、私は "Glass" がお気に入りです。

ポイントは2つです。

- state ファイルを `session_id` ベースのパス（`/tmp/.claude-ctx-warn-${session_id}`）にすることで、複数セッションが干渉しない
- `osascript` をバックグラウンド（`&`）で実行することで、statusLine の応答を遅らせない

---

### 2. クリーンアップスクリプトを作成

`~/.claude/ctx-warn-cleanup.sh` を作成します。`SessionEnd` フックでも JSON から `session_id` が取得できるため、そのセッションのファイルだけを削除できます。

```sh
#!/bin/sh
input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id // "default"')
rm -f "/tmp/.claude-ctx-warn-${session_id}"
```

```bash
chmod +x ~/.claude/ctx-warn-cleanup.sh
```

---

### 3. settings.json に SessionEnd を登録

```json
"hooks": {
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "bash ~/.claude/ctx-warn-cleanup.sh"
        }
      ]
    }
  ]
}
```

---

## 動作イメージ

60% を超えた最初のターンで macOS 通知が1回だけ届きます。

![スクリーンショット 2026-06-19 10.53.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3952436/b003122a-b91f-4aca-8549-d12e41c097fc.png)


以降、70%・80%・90% と閾値を超えるたびに通知が来ます。同じ閾値が繰り返されることはありません。

---

## 警告メッセージ一覧

| 使用率 | 通知メッセージ |
|--------|--------------|
| 60% 超 | あ、60%超えた。まあまだ全然いける |
| 70% 超 | 70%ね〜 なんとなく意識しといて |
| 80% 超 | 80%きたよ。そろそろかもね |
| 90% 超 | 90%！もうすぐ auto-compact 来るっぽい |

メッセージは好みで変えてください。
なんかゆる〜い感じにしてってお願いしたらこんなメッセージになりました。

---

## まとめ

| ファイル | 変更内容 |
|---------|---------|
| `~/.claude/statusline-command.sh` | 通知ロジックを追記 |
| `~/.claude/ctx-warn-cleanup.sh` | SessionEnd クリーンアップスクリプトを新規作成 |
| `~/.claude/settings.json` | `SessionEnd` に登録 |

ターミナルから目を離していても通知で気づけるのが利点です。ぜひ試してみてください。
