---
id: "2026-04-23-claude-の使用率をメニューバーで常時確認する-swiftbar-oauth-api-で作る1フ-01"
title: "Claude の使用率をメニューバーで常時確認する ── SwiftBar + OAuth API で作る1ファイル実装"
url: "https://zenn.dev/yktsnet/articles/202604-claude-usage-swiftbar"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "Python", "zenn"]
date_published: "2026-04-23"
date_collected: "2026-04-24"
summary_by: "auto-rss"
query: ""
---

Claude Pro/Max を使っていると、5時間セッションと週次の使用率が気になる場面があります。確認するたびに claude.ai を開くのは手間なので、メニューバーに常時表示させました。

最近 [Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs) の週次枠が追加されたので、5時間・週次・Design の3つをまとめて1行に出すことにしました。

```
5h:21% (4h14m) 7d:74% (9h24m) De:7% (Mon)
```

### Claude Design について

2026年4月にリサーチプレビューとして公開された Anthropic のビジュアル制作ツールです。スライド、UI プロトタイプ、ワンページャーなどを Claude との会話で作れます。Claude Opus 4.7 を基盤にしており、Pro/Max/Team/Enterprise プランで利用できます。

### 制限の構造

claude.ai の使用制限は独立した3つの枠で管理されています。

| 枠 | リセット | 対象 |
| --- | --- | --- |
| 5時間セッション | 最初のメッセージから5時間後（ローリング） | 通常の会話 |
| 週次（全モデル） | 7日ごと | claude.ai・Claude Code の合算 |
| 週次（Claude Design） | 7日ごと | Design の利用のみ |

週次の全モデル枠は claude.ai の会話・IDE プラグイン・Claude Code をまたいで合算されます。Design の枠は独立しているため、Design を使っても通常の週次枠には影響しません。

※ 枠の定義や名称は Anthropic が予告なく変更することがあり

## 仕組み

Claude Code はログイン時に OAuth トークンを macOS キーチェーンに保存しています。このトークンで Anthropic の内部エンドポイント `api.anthropic.com/api/oauth/usage` を叩くと、claude.ai の UI が表示しているのと同じ使用率データが取れます。このエンドポイントは、Claude Code の通信をネットワークツールで確認しているコミュニティによって発見されたものです。

レスポンスはこういう形です。Design の枠は `seven_day_omelette` というキーで返ってきます。

```
{
  "five_hour":          { "utilization": 21.0, "resets_at": "..." },
  "seven_day":          { "utilization": 74.0, "resets_at": "..." },
  "seven_day_omelette": { "utilization":  7.0, "resets_at": "..." }
}
```

※ seven\_day\_omelette は Claude Design の内部キー名で公式ドキュメントには記載なし

**前提条件**

* Claude Code がインストール済みでログイン済みであること
* [SwiftBar](https://swiftbar.app) がインストール済みであること

## スクリプト

SwiftBar の設定で指定したプラグインディレクトリに `claude-usage.5m.sh` として保存して `chmod +x` とします。

```
#!/bin/bash
# <bitbar.title>Claude Usage</bitbar.title>
# <bitbar.version>v1.2</bitbar.version>
# <bitbar.refreshInterval>300</bitbar.refreshInterval>

CACHE_FILE="$HOME/.cache/claude-usage.json"
mkdir -p "$(dirname "$CACHE_FILE")"

CREDS=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null)
if [ -z "$CREDS" ]; then
  echo "Claude: N/A"
  exit 0
fi

TOKEN=$(echo "$CREDS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('claudeAiOauth', {}).get('accessToken', ''))
" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Claude: auth error"
  exit 0
fi

RESPONSE=$(curl -s "https://api.anthropic.com/api/oauth/usage" \
  -H "Authorization: Bearer $TOKEN" \
  -H "anthropic-beta: oauth-2025-04-20" \
  -H "Accept: application/json")

IS_OK=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    sys.exit(0 if 'error' not in d else 1)
except Exception:
    sys.exit(1)
" 2>/dev/null; echo $?)

if [ "$IS_OK" -eq 0 ]; then
  echo "$RESPONSE" > "$CACHE_FILE"
elif [ -f "$CACHE_FILE" ]; then
  RESPONSE=$(cat "$CACHE_FILE")
else
  echo "Claude: rate limited"
  exit 0
fi

echo "$RESPONSE" | python3 -c "
import sys, json, datetime

try:
    d = json.load(sys.stdin)
except Exception:
    print('Claude: error')
    sys.exit(0)

def pct(key):
    v = d.get(key)
    if v and v.get('utilization') is not None:
        return int(round(v['utilization']))
    return None

def remaining(key):
    v = d.get(key)
    if not v or not v.get('resets_at'):
        return None
    t = datetime.datetime.fromisoformat(v['resets_at'])
    now = datetime.datetime.now(datetime.timezone.utc)
    secs = int((t - now).total_seconds())
    if secs <= 0:
        return 'reset'
    h, rem = divmod(secs, 3600)
    m = rem // 60
    days, h2 = h // 24, h % 24
    if days:
        return f'{days}d{h2}h'
    elif h:
        return f'{h}h{m:02d}m'
    else:
        return f'{m}m'

def reset_day(key):
    v = d.get(key)
    if not v or not v.get('resets_at'):
        return None
    t = datetime.datetime.fromisoformat(v['resets_at'])
    return t.astimezone().strftime('%a')

fh_pct = pct('five_hour')
sd_pct = pct('seven_day')
de_pct = pct('seven_day_omelette')  # Claude Design の週次枠。不要なら以降の de_ 変数と出力行を削除

fh_rem = remaining('five_hour')
sd_rem = remaining('seven_day')
de_day = reset_day('seven_day_omelette')

fh_str = f'{fh_pct}%' if fh_pct is not None else 'N/A'
sd_str = f'{sd_pct}%' if sd_pct is not None else 'N/A'
de_str = f'{de_pct}%' if de_pct is not None else 'N/A'

fh_rem_str = f' ({fh_rem})' if fh_rem else ''
sd_rem_str = f' ({sd_rem})' if sd_rem else ''
de_day_str = f' ({de_day})' if de_day else ''

print(f'5h:{fh_str}{fh_rem_str} 7d:{sd_str}{sd_rem_str} De:{de_str}{de_day_str}')
print('---')
print(f'5h session:  {fh_str}{fh_rem_str}')
print(f'Weekly:      {sd_str}{sd_rem_str}')
print(f'Design:      {de_str}{de_day_str}')  # 不要なら削除
"
```

ファイル名の `.5m.` が更新間隔で、5分ごとに API を叩いて表示を更新します。API がレートリミットを返した場合は直前のキャッシュを表示します。

![SwiftBar Claude使用率](https://static.zenn.studio/user-upload/deployed-images/1be6ffae644ff6a8a815d81b.png?sha=9c0b9aaa27a92d9f6ede4e3924a30fec7d06d92e)

## レートリミットについて

実際に動かしてみると、`/api/oauth/usage` はレートリミット（HTTP 429）が非常にアグレッシブで、一度引っかかると30分以上回復しないことがあります。GitHub にも同様の報告が複数上がっており、既知の問題です。

上記スクリプトでは、API が失敗した場合に `~/.cache/claude-usage.json` のキャッシュにフォールバックする方式で対処しています。

## 注意点

### Anthropic の OAuth ポリシーについて

2026年2月、Anthropic は Free/Pro/Max プランの OAuth トークンを Claude Code・claude.ai 以外のツールで使用することを利用規約違反と明記しました。4月にはサードパーティツール（OpenClaw 等）への技術的な遮断も実施されています。

このスクリプトが呼んでいるのは使用率の取得のみで、Claude モデルへの推論リクエストは一切行いません。禁止の背景にあるサブスクリプションのタダ乗り（トークンアービトラージ）とは用途が異なりますが、規約の文言上はグレーゾーンです。自己責任での利用となります。

### その他

`/api/oauth/usage` は公式ドキュメントに記載のない内部エンドポイントです。Anthropic 側の変更で動かなくなる可能性があります。公式の使用率 API を求める Issue は [GitHub](https://github.com/anthropics/claude-code/issues/19880) にも上がっており、いずれ正式な手段が提供されるかもしれません。

スクリプトを初めて実行したとき、macOS がキーチェーンへのアクセス許可を求めるダイアログを表示することがあります。「許可」を選択すれば以降は表示されません。

スクリプト内では `python3` コマンドを使用しています。macOS 標準の Python 3 で動作しますが、Homebrew 等で複数バージョンを管理している場合は `/usr/bin/python3` と明示してもかまいません。
