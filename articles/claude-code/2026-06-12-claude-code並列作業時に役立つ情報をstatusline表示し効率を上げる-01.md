---
id: "2026-06-12-claude-code並列作業時に役立つ情報をstatusline表示し効率を上げる-01"
title: "Claude Code並列作業時に役立つ情報をstatusline表示し効率を上げる"
url: "https://zenn.dev/secula/articles/997eb53f1e6a8d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

#### 並列作業している時に便利になるディレクトリやブランチ表示などを追加して作業効率をアップさせたいのでstasulineを導入してみました。

#### 見た目も自分好みにして気分Upして作業できそうです。

## 完成イメージ

![](https://static.zenn.studio/user-upload/0a64a573a550-20260612.png)

# Claude Code ステータスライン（Powerline風 / 2行表示）

Claude Code の画面下部に表示されるステータスラインを、Starship風の Powerline セグメント＋コンテキスト使用量グラデーションバーでカスタマイズする設定メモ。

参考: [Claude Code Docs — Status line](https://code.claude.com/docs/en/statusline#display-multiple-lines)

---

---

## 設定方法

### 1. スクリプトを配置

`~/.claude/statusline.sh` として保存し、実行権限を付与する。

```
chmod +x ~/.claude/statusline.sh
```

### 2. `~/.claude/settings.json` に登録

```
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 0
  }
}
```

* `type`: `command` を指定するとシェルコマンドの標準出力がそのまま表示される
* `command`: 実行するスクリプトのパス
* `padding`: `0` で左端まで使い切る（デフォルトは余白あり）

### 3. フォント要件（重要）

Powerlineの区切り三角（`）と gitアイコン（`）を表示するには、ターミナルに  
**Nerd Font / Powerline対応フォント**が必要。豆腐（□）になる場合はフォントを切り替える。

* 例: `Hack Nerd Font`, `JetBrainsMono Nerd Font`, `MesloLGS NF` など
* iTerm2 / Ghostty / VS Code いずれもフォント設定から指定可能

---

## 動作の仕組み

Claude Code はステータスライン用コマンドに、セッション情報を **JSON で標準入力に渡す**。  
スクリプトはそれを `jq` でパースして整形・出力する。

### 入力JSON（利用しているフィールド）

```
{
  "model":          { "display_name": "Opus" },
  "workspace":      { "current_dir": "/path/to/project" },
  "context_window": { "used_percentage": 41.2 },
  "rate_limits": {
    "five_hour":  { "used_percentage": 12 },
    "seven_day":  { "used_percentage": 20 }
  },
  "cost":       { "total_duration_ms": 423000 },
  "session_id": "xxxxxxxx"
}
```

> `jq` が未インストールの場合は `brew install jq` が必要。

### 主要な実装ポイント

| 項目 | 内容 |
| --- | --- |
| **bash 3.2 対応** | macOS標準の `/bin/bash` は 3.2。`$''` 形式のUnicodeエスケープが使えないため、Powerline記号は**UTF-8オクタルバイト列**（`printf '\356\202\260'`）で生成している |
| **gitキャッシュ** | ブランチ取得は重いので `/tmp/statusline-git-<session_id>` に**5秒キャッシュ**。大規模リポジトリでも描画が固まらない |
| **256色** | `\033[38;5;Nm`（文字色）/ `\033[48;5;Nm`（背景色）で指定。`fg()` / `bg()` ヘルパーにまとめている |
| **Powerlineの色繋ぎ** | 区切り三角は「前景＝現在セグメント色 / 背景＝次セグメント色」で描画すると境界が滑らかに繋がる |
| **グラデーションバー** | 10セルそれぞれを位置で色付け（左=緑→右=赤）。使用分は `█`、残りは同色の薄い `░`。**使用量が少なくても全体に色が出る** |
| **四捨五入** | 塗りつぶしセル数は `(PCT + 5) / 10`。切り捨て（`PCT / 10`）だと5%で0個になり色が消えるため |
| **レート制限の沈黙** | `RL_THRESHOLD`（既定50%）未満は非表示にして平常時はスッキリ。高負荷時だけ警告的に表示 |
| **経過時間** | `cost.total_duration_ms` を `Xh Ym / Xm Ys / Xs` に整形しストップウォッチ付きで表示。フィールドが無ければ自動で非表示 |

---

## カスタマイズ早見表

スクリプト冒頭付近の変数を書き換えるだけで調整できる。

### セグメント色（1行目）

```
C_MODEL=221    # モデル：薄い山吹色
C_GIT=218      # git：薄ピンク
C_DIR=153      # ディレクトリ：薄め水色
```

色番号は256色パレット。代替候補:

| パーツ | 現在 | 濃いめ | 淡いめ |
| --- | --- | --- | --- |
| モデル(山吹) | 221 | 220 | 222 |
| ブランチ(桃) | 218 | 211 | 224 |
| ディレクトリ(水) | 153 | 117 | 159 |

### バーのグラデーション（2行目）

```
# 左=緑 → 右=赤（パステル）
GRAD=(114 150 186 222 221 215 209 210 203 174)
```

* もっと派手にするなら: `GRAD=(82 118 154 190 226 220 214 208 202 196)`
* 残りセルをグレーに戻すなら、描画ループの `else` 側を `$(fg 240)` に変更

### レート制限のしきい値

```
RL_THRESHOLD=50   # これ未満は非表示。80 にするとより静かに
```

### 文字色

```
DARK=235       # 明るい背景セグメント用（濃い文字）
LIGHT=252      # 暗い背景セグメント用（明るい文字）
```

### 経過時間アイコン

ストップウォッチは Nerd Font の `(U+F2F2)。豆腐になる場合は時計` (`\357\200\227`) などに差し替える。

```
WATCH=$(printf '\357\213\262')   #  → 時計にするなら \357\200\227
```

---

## 動作確認（手動テスト）

スクリプトは標準入力からJSONを受け取るので、サンプルJSONを流し込めば単体で確認できる。

```
echo '{
  "model":{"display_name":"Opus"},
  "workspace":{"current_dir":"/Users/me/projects/api-migration"},
  "context_window":{"used_percentage":41},
  "rate_limits":{"five_hour":{"used_percentage":12},"seven_day":{"used_percentage":20}},
  "cost":{"total_duration_ms":423000},
  "session_id":"test"
}' | bash ~/.claude/statusline.sh
```

色番号を変えながら `for p in 5 41 87; do ...; done` のように使用率を振ると、グラデーションの見え方を一気に比較できる。

---

## スクリプト全文（`~/.claude/statusline.sh`）

```
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
FIVE_H=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
WEEK=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
SESSION_ID=$(echo "$input" | jq -r '.session_id')
DUR_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // empty')   # セッション稼働時間(ms)

# --- git情報は5秒キャッシュ（大規模リポジトリ対策） ---
CACHE="/tmp/statusline-git-$SESSION_ID"
if [ ! -f "$CACHE" ] || [ $(($(date +%s) - $(stat -f %m "$CACHE" 2>/dev/null || echo 0))) -gt 5 ]; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    echo "$BRANCH" > "$CACHE"
fi
BRANCH=$(cat "$CACHE")

# --- Powerline/ブロック文字（bash 3.2対応：UTF-8バイト列で生成） ---
ESC=$(printf '\033')                 # ANSIエスケープ
SEP=$(printf '\356\202\260')         #  U+E0B0 右向き三角（Nerd Font/Powerlineフォント必須）
GIT=$(printf '\356\202\240')         #  U+E0A0 ブランチアイコン
BLK=$(printf '\342\226\210')         # █ U+2588 フルブロック（バー使用分）
DOT=$(printf '\342\226\221')         # ░ U+2591 ライトシェード（バー残り）
WATCH=$(printf '\357\213\262')       #  U+F2F2 ストップウォッチ（Nerd Font）
RESET="${ESC}[0m"

fg() { printf '%s' "${ESC}[38;5;${1}m"; }   # 文字色（256色）
bg() { printf '%s' "${ESC}[48;5;${1}m"; }   # 背景色（256色）

# --- セグメント配色（明るい背景は濃い文字／暗い背景は明るい文字） ---
DARK=235       # 濃い文字色（明るい背景用）
LIGHT=252      # 明るい文字色（暗い背景用）
C_MODEL=221    # モデル：山吹色（薄め・黄寄り）
C_GIT=218      # git：薄ピンク
C_DIR=153      # ディレクトリ：薄め水色

# バー10セルのグラデーション配色（左=緑 → 右=赤、パステル）
# 各セルは「位置」で色が決まる＝使用量が少なくても全体に色が出る
GRAD=(114 150 186 222 221 215 209 210 203 174)

# 使用率→色（レート制限の値用）：低=緑 / 中=黄 / 高=赤
lvl() {
    v=$(printf '%.0f' "${1:-0}")
    if   [ "$v" -ge 90 ]; then printf 174   # 赤
    elif [ "$v" -ge 70 ]; then printf 185   # 黄
    else                       printf 149    # ライム緑
    fi
}

# レート制限の表示しきい値（これ未満は平常時として沈黙）
RL_THRESHOLD=50

# ============================================================
# 1行目：Powerlineセグメント（モデル → git → ディレクトリ）
# ============================================================
BGS=(); FGS=(); TXTS=()
BGS+=("$C_MODEL"); FGS+=("$DARK");  TXTS+=(" $MODEL ")
[ -n "$BRANCH" ] && { BGS+=("$C_GIT"); FGS+=("$DARK"); TXTS+=(" $GIT $BRANCH "); }
BGS+=("$C_DIR");   FGS+=("$DARK");  TXTS+=(" ${DIR##*/} ")

LINE1=""
for i in "${!BGS[@]}"; do
    cur=${BGS[$i]}
    LINE1+="$(bg "$cur")$(fg "${FGS[$i]}")${TXTS[$i]}"
    nxt=${BGS[$((i+1))]:-}
    if [ -n "$nxt" ]; then
        LINE1+="${RESET}$(fg "$cur")$(bg "$nxt")${SEP}"
    else
        LINE1+="${RESET}$(fg "$cur")${SEP}${RESET}"
    fi
done

# ============================================================
# 2行目：ブロックバー（使用分=色付き / 残り=ドット）＋ ％
#         レート制限は RL_THRESHOLD 以上のときだけ追記
# ============================================================
# 四捨五入：5%でも1セル点灯（切り捨てだと0個になり色が出ないため）
FILLED=$(( (PCT + 5) / 10 )); [ "$FILLED" -gt 10 ] && FILLED=10

# 全10セルをグラデーション色で描画：
#   使用分 = █（くっきり） / 残り = ░（同じ色の薄いドット）
BAR=""
for ((j=0; j<10; j++)); do
    if [ "$j" -lt "$FILLED" ]; then BAR+="$(fg "${GRAD[$j]}")${BLK}"
    else                            BAR+="$(fg "${GRAD[$j]}")${DOT}"
    fi
done
BAR+="${RESET}"

# ％の文字色＝現在位置のグラデーション色
idx=$((FILLED - 1)); [ "$idx" -lt 0 ] && idx=0
PCT_COLOR=${GRAD[$idx]}

# レート制限：平常時は沈黙、しきい値以上のみ表示
RL=""
if [ -n "$FIVE_H" ] && [ "$(printf '%.0f' "$FIVE_H")" -ge "$RL_THRESHOLD" ]; then
    RL="${RL} 5h:$(printf '%.0f' "$FIVE_H")/100"
fi
if [ -n "$WEEK" ] && [ "$(printf '%.0f' "$WEEK")" -ge "$RL_THRESHOLD" ]; then
    RL="${RL} 7d:$(printf '%.0f' "$WEEK")/100"
fi

# 経過時間：ms → 「Xh Ym / Xm Ys / Xs」に整形（ストップウォッチ付き）
TIMER=""
if [ -n "$DUR_MS" ]; then
    TOT=$((DUR_MS / 1000))
    H=$((TOT / 3600)); M=$(((TOT % 3600) / 60)); S=$((TOT % 60))
    if   [ "$H" -gt 0 ]; then T="${H}h ${M}m"
    elif [ "$M" -gt 0 ]; then T="${M}m ${S}s"
    else                     T="${S}s"
    fi
    TIMER=" $(fg 250)${WATCH} ${T}${RESET}"
fi

LINE2="${BAR} $(fg "$PCT_COLOR")${PCT}/100${RESET}"
[ -n "$RL" ] && LINE2="${LINE2}$(fg 246)${RL}${RESET}"
LINE2="${LINE2}${TIMER}"

printf '%s\n%s\n' "$LINE1" "$LINE2"
```

---

## トラブルシュート

| 症状 | 原因 / 対処 |
| --- | --- |
| 三角やアイコンが □（豆腐）になる | Nerd Font未設定。ターミナルのフォントを Nerd Font に変更 |
| 何も表示されない | `settings.json` の `statusLine.command` パス、スクリプトの実行権限（`chmod +x`）を確認 |
| `jq: command not found` | `brew install jq` |
| 色が出ない / 化ける | ターミナルが256色対応か確認（`echo $TERM` が `xterm-256color` 等） |
| バーが低使用率で真っ暗 | 旧版の切り捨て計算。本版は `(PCT+5)/10` の四捨五入＋全セル着色で解消済み |
| 経過時間が出ない | `cost.total_duration_ms` が渡らない環境（古いバージョン等）。フィールドが無いと自動で非表示になる仕様 |
| ストップウォッチが □ になる | Nerd Font未設定、または字形が無い。`WATCH` を時計 `\357\200\227` 等に差し替え |
