---
id: "2026-05-04-claude-codeセッション上限youve-hit-your-limit-resets-hmmに-01"
title: "【Claude Code】セッション上限（You've hit your limit · resets H:MM）に到達した時のための自動再開スクリプトを作った"
url: "https://qiita.com/nAotO01_03/items/604a51d7383da086cbcb"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

# はじめに
Claude CodeのProプランを利用していると、セッション上限に到達して一定期間使えなくなることをしばしば経験します。
特に、複雑な実装や大量ファイルの読み書きを行っていると、短時間の処理であっという間に上限に到達してしまいます。

上限到達すると `You've hit your limit · resets X:XX (Asia/Tokyo)` と表示される
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3846857/09d1fff9-2c2e-4a17-8e75-be2daaa2906f.png)

これまでは上限がリセットされた後に、`claude -c` でセッション再開していましたが、毎回手動でセッション再開するのが面倒なので自動スクリプトを作成してみました。
これで外出中や深夜でもリセットされた直後にセッション再開できます。
# スクリプト概要
指定した時刻になったら `claude -c` を実行するという、非常にシンプルなものです。
引数に時間と対象プロジェクトを指定するだけです。

# スクリプト詳細
**CLAUDE_BIN** にはclaudeをインストールしているパスを設定してください。
`e.g. /Users/ユーザ名/.npm-global/bin/claude`

``` shell
#!/bin/zsh
set -eu

CLAUDE_BIN="claudeをインストールしているパスを設定してください"

usage() {
  echo "usage:" >&2
  echo "  $0 <HH:MM> <PROJECT_PATH>" >&2
  echo "  $0 <YYYY-MM-DD> <HH:MM> <PROJECT_PATH>" >&2
  echo "  PROJECT_PATH must be an absolute path." >&2
  exit 1
}

# --- 引数解析 ---
case $# in
  2)
    TIME="$1"
    PROJECT_PATH="$2"
    NOW=$(date +%s)
    TARGET_TODAY=$(date -j -f "%Y-%m-%d %H:%M" "$(date +%Y-%m-%d) ${TIME}" +%s 2>/dev/null) \
      || { echo "invalid time: ${TIME}" >&2; exit 1; }
    if (( TARGET_TODAY <= NOW )); then
      DATE_STR=$(date -v+1d +%Y-%m-%d)
    else
      DATE_STR=$(date +%Y-%m-%d)
    fi
    ;;
  3)
    DATE_STR="$1"
    TIME="$2"
    PROJECT_PATH="$3"
    ;;
  *)
    usage
    ;;
esac

# --- プロジェクトパス検証 ---
if [[ "${PROJECT_PATH}" != /* ]]; then
  echo "error: PROJECT_PATH must be absolute (got: ${PROJECT_PATH})" >&2
  exit 1
fi
if [[ ! -d "${PROJECT_PATH}" ]]; then
  echo "error: PROJECT_PATH not found: ${PROJECT_PATH}" >&2
  exit 1
fi

# --- 目標時刻のエポック計算 ---
TARGET_EPOCH=$(date -j -f "%Y-%m-%d %H:%M" "${DATE_STR} ${TIME}" +%s 2>/dev/null) \
  || { echo "invalid datetime: ${DATE_STR} ${TIME}" >&2; exit 1; }

NOW=$(date +%s)
if (( TARGET_EPOCH <= NOW )); then
  echo "error: target time is in the past: ${DATE_STR} ${TIME}" >&2
  exit 1
fi

REMAIN=$((TARGET_EPOCH - NOW))
HH=$((REMAIN / 3600)); MM=$((REMAIN % 3600 / 60)); SS=$((REMAIN % 60))

echo "================================================================"
echo "Claude Code 自動再開"
echo "  target:  ${DATE_STR} ${TIME}"
echo "  project: ${PROJECT_PATH}"
echo "  now:     $(date '+%Y-%m-%d %H:%M:%S')"
echo "  remain:  ${HH}h ${MM}m ${SS}s"
echo "  ※ このターミナルを閉じると予約は失われます"
echo "  ※ Ctrl+C で予約をキャンセルできます"
echo "================================================================"

# --- 待機ループ（Mac スリープ復帰にも対応するため実時間で判定） ---
while :; do
  NOW=$(date +%s)
  if (( NOW >= TARGET_EPOCH )); then
    break
  fi
  REMAIN=$((TARGET_EPOCH - NOW))
  HH=$((REMAIN / 3600)); MM=$((REMAIN % 3600 / 60)); SS=$((REMAIN % 60))
  printf "\r[%s] 残り %02d:%02d:%02d  " "$(date '+%H:%M:%S')" "$HH" "$MM" "$SS"
  if   (( REMAIN > 600 )); then sleep 30
  elif (( REMAIN > 60  )); then sleep 5
  else                          sleep 1
  fi
done
echo
echo "================================================================"
echo "$(date '+%Y-%m-%d %H:%M:%S') → ${PROJECT_PATH} で claude -c を起動"
echo "================================================================"

cd "${PROJECT_PATH}"
exec "${CLAUDE_BIN}" -c "セッション再開して"
```

# スクリプト実行方法
スクリプト（`claude-schedule-resume.sh`）の引数に以下を指定して実行するだけです。時間になったら自動でセッション再開してくれます。
* 時刻（`<HH:MM>` or `<YYYY-MM-DD> <HH:MM>`）
* 対象プロジェクトパス（**絶対パス**）

| 形式 | 引数構成 | 例 |
|------|----------|----|
| 時刻のみ | `<HH:MM> <PROJECT_PATH>` | `claude-schedule-resume.sh 23:00 /Users/XXXX/YYYY/MyApp` |
| 日付指定 | `<YYYY-MM-DD> <HH:MM> <PROJECT_PATH>` | `claude-schedule-resume.sh 2026-04-30 02:00 /Users/XXXX/YYYY/MyApp` |

問題なくスクリプトが起動すれば以下キャプチャのような表示になります。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3846857/19287576-7922-4a2d-b440-6ef621a19d2a.png)

# 【おまけ】 ステータスラインの活用
地味だけど便利なステータスラインの機能を紹介します。
Claude Codeを使用しているとコンテキストウィンドウをどれくらい消費しているのか、セッション上限まであとどれくらいか、といった情報を把握しておきたいと感じることがあります。
※ `/context`で確認できますが、毎回コマンドを打つのも面倒です。

その際に役に立つのがClaude Codeのカスタマイズ機能の **ステータスライン** です。
ステータスラインを設定するとターミナル下部に任意の情報を表示させることができます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3846857/2584b579-1023-4bd6-b7db-ca453a89a170.png)

**設定手順**
1. スクリプト作成　※Claudeに依頼すればサクッと作ってくれます
1. Claude Codeのsettings.jsonに1で作成したスクリプトを設定

筆者はステータスラインにセッション使用率とコンテキストウィンドウ使用率を表示させています。
``` shell
#!/bin/bash
input=$(cat)

CONTEXT_PCT=$(echo "$input" | jq -r '.context_window.used_percentage // empty' | cut -d. -f1)
RATE_PCT=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty' | cut -d. -f1)

if [ -n "$RATE_PCT" ] && [ -n "$CONTEXT_PCT" ]; then
    echo "Session: ${RATE_PCT}% | Context: ${CONTEXT_PCT}%"
elif [ -n "$CONTEXT_PCT" ]; then
    echo "Context: ${CONTEXT_PCT}%"
else
    echo "Context: -"
fi
```

settings.jsonに以下の設定を追加します。
``` json
"statusLine": {
    "type": "command",
    "command": "作成したスクリプトのパス" 
  }
```
| 設定する箇所 | settings.jsonのパス |
|:-|:-|
| プロジェクト直下  | `.claude/settings.local.json`  |
| グローバル  | `~/.claude/settings.json` |
# 参考

https://zenn.dev/long910/articles/2026-02-21-claude-code-usage-limit

https://dev.classmethod.jp/articles/claude-code-statusline-context-usage-display/
