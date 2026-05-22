---
id: "2026-05-21-aiエージェントをハブにする設計-claude-mcp-bashで複数サービス連携の複雑さを預ける-01"
title: "AIエージェントをハブにする設計 ── Claude + MCP + Bashで複数サービス連携の複雑さを預ける"
url: "https://zenn.dev/h_moto/articles/h_motohiro_article9990002"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "Gemini", "antigravity"]
date_published: "2026-05-21"
date_collected: "2026-05-22"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* 複数サービス連携（iCloud → 画像解析 → 栄養DB → 食事管理アプリ → LINE）を、**ビジネスロジックを書かずに**作った
* ポイントは「**AIエージェントをハブに据える**」設計。サービス間の判断・変換は全部AIに預け、自分が書くのはBashの入出力配線だけ
* 副作用として、**AIモデルを差し替え可能**な構造になる。実際 Claude → Gemini → Antigravity と乗り換えても、ロジックは無変更で済んだ

## 1. 動機：「自動化したいけど、自動化に力尽きたくない」

仲間内で「食事写真とカロリー・PFCをLINEで報告しあう」相互監視ムーブメントが起こった。が、毎食ごとに栄養素を手で調べて入力するのは正直しんどい。

理想はこうだ。

* 食事の写真をiCloudに置く
* 自動で栄養素が推定される
* 食事管理アプリ（MacroFactor）に登録される
* LINEグループに「今日◯◯kcal」と通知される

普通に作ろうとすると、画像認識API・栄養データベース・MacroFactor API・LINE Messaging APIを繋ぐビジネスロジックの塊になる。趣味のために何日もかけたくない。

## 2. 設計思想：複雑さをAIエージェントに預ける

そこで発想を変えた。

**サービス間の「判断」と「変換」を、ぜんぶAIエージェントに丸投げする。**

従来のアーキテクチャと比べるとこうなる。

|  | 従来のグルーコード | AIエージェント・ハブ |
| --- | --- | --- |
| サービス連携ロジック | 自分でコードを書く | 自然言語の指示で済ませる |
| 形式変換（画像→JSON等） | パーサ・スキーマを書く | AIに「JSONで返して」と頼む |
| エラー処理の分岐 | if文で網羅 | AIが文脈で判断 |
| API/モデルの差し替え | 各所書き換え | CLIコマンド名の置換だけ |

要するに、**「サービスの間にAIエージェントを挟むだけ」のアーキテクチャ**にする。自分が書くのは、AIを起動するBashスクリプトと、入出力のファイルパスだけ。

これが効くのは、繋ぐ先のサービスがそれぞれ「曖昧さ」を持っているケースだ。

* 画像 → これは食事？領収書？
* 食材名 → カロリーいくら？
* 栄養情報 → MacroFactorのどの食品マスタにマッチする？

こういう「人間がやるとちょっと考える」部分は、コードで書くと急に重くなる。AIに預ければ一行で済む。

## 3. 実例：食べ物アナライザーの構成

実際に作った「食べ物アナライザー」の全体像はこうだ。

登場人物は多いが、**自分が書いたのは中央の `analyze-food.sh` だけ**。あとはAIへの指示文（プロンプト）と、繋ぎ先のCLIコマンドを並べている。

MacroFactorへの登録は、[@sjawhar](https://github.com/sjawhar) 製の [macrofactor-mcp](https://github.com/sjawhar/macrofactor-mcp) を使っている。MCPサーバーを差すだけで、Claude/GeminiからMacroFactorの食事登録が叩けるようになる。

実装の詳細を見る

### メインスクリプト（analyze-food.sh）

```
#!/bin/bash
# 食事写真解析 + MacroFactor登録 + LINE通知

TARGET_DATE=""
USE_CLAUDE=false
SKIP_MF=false
SKIP_LINE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d) TARGET_DATE="$2"; shift 2 ;;
    -c) USE_CLAUDE=true; shift ;;
    -s|--skip-mf) SKIP_MF=true; shift ;;
    --skip-line) SKIP_LINE=true; shift ;;
    *) shift ;;
  esac
done

ICLOUD_FOODS_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/daily-foods"
WORK_DIR="$HOME/Projects/food-analyzer"
TODAY="${TARGET_DATE:-$(date +%Y-%m-%d)}"
LOG_FILE="$WORK_DIR/logs/${TODAY}.log"

source "$WORK_DIR/.env"
source "$WORK_DIR/lib/common.sh"

mkdir -p "$WORK_DIR/logs" "$WORK_DIR/input" "$WORK_DIR/temp"
log "===== 食事解析開始 ====="

# 写真を探してコピー
PHOTOS=$(find "$ICLOUD_FOODS_DIR" -name "food-${TODAY}*" -type f 2>/dev/null)
MEMO_FILE="$ICLOUD_FOODS_DIR/food-memo.txt"
MEMO_ENTRIES=$(grep "^${TODAY}-" "$MEMO_FILE" 2>/dev/null || true)

if [ -z "$PHOTOS" ] && [ -z "$MEMO_ENTRIES" ]; then
  log "今日の写真・メモがありません"
  exit 0
fi

rm -f "$WORK_DIR/input/food-"*
[ -n "$PHOTOS" ] && echo "$PHOTOS" | while read p; do cp "$p" "$WORK_DIR/input/"; done

# Session 1: 画像・メモ解析
SESSION1_MEMO="$MEMO_ENTRIES" bash "$WORK_DIR/lib/session1.sh" -d "$TODAY" \
  ${USE_CLAUDE:+-c}

if [ $? -ne 0 ] || [ ! -f "$WORK_DIR/temp/meals.json" ]; then
  log "Session 1 失敗。終了。"
  exit 1
fi

MEALS_JSON=$(cat "$WORK_DIR/temp/meals.json")

# Session 2: MacroFactor登録
if [ "$SKIP_MF" = false ]; then
  bash "$WORK_DIR/lib/session2.sh" -d "$TODAY" -i "$WORK_DIR/temp/meals.json"
  if [ $? -eq 0 ] && [ -f "$WORK_DIR/logs/${TODAY}-final.json" ]; then
    FINAL_JSON=$(cat "$WORK_DIR/logs/${TODAY}-final.json")
  else
    log "Session 2 失敗。Session 1 の結果で継続..."
    FINAL_JSON="$MEALS_JSON"
  fi
else
  FINAL_JSON="$MEALS_JSON"
fi

# LINE送信
JSON="${FINAL_JSON:-$MEALS_JSON}"
if [ "$SKIP_LINE" = false ]; then
  TOTAL_KCAL=$(echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['total']['kcal'])" 2>/dev/null)
  curl -s -X POST https://api.line.me/v2/bot/message/push \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${LINE_CHANNEL_ACCESS_TOKEN}" \
    -d "{\"to\": \"${LINE_GROUP_ID}\", \"messages\": [{\"type\": \"text\", \"text\": \"📊 本日: ${TOTAL_KCAL}kcal\"}]}"
fi

log "===== 食事解析完了 ====="
```

### Session 1: 画像・メモ解析（lib/session1.sh）

```
#!/usr/bin/env bash
# Session 1: 食事写真・メモ解析（MacroFactor登録なし）
# Output: temp/meals.json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/common.sh"

USE_CLAUDE=false
TODAY=""
MEMO_ENTRIES="${SESSION1_MEMO:-}"

while getopts "d:c" opt; do
  case $opt in
    d) TODAY="$OPTARG" ;;
    c) USE_CLAUDE=true ;;
  esac
done

mkdir -p "$WORK_DIR/temp"

PHOTO_SECTION=""
PHOTOS=$(find "$WORK_DIR/input" -name "food-${TODAY}*" -type f 2>/dev/null)
if [ -n "$PHOTOS" ]; then
  PHOTO_SECTION="## 写真の解析
- input/ フォルダにある ${TODAY} の食事写真をすべて解析する
- ファイル名の _HH-MM 部分を食事時刻として使用する
- 食事の写真またはレシート・領収書かを判定する
- Web検索で栄養情報を調べてカロリー・PFCを推定する"
fi

MEMO_SECTION=""
if [ -n "$MEMO_ENTRIES" ]; then
  MEMO_SECTION="## メモからの解析
以下のメモエントリを解析する（形式: YYYY-MM-DD-HH-MM 食べたもの [量]）:

${MEMO_ENTRIES}

Web検索で栄養情報を調べてカロリー・PFCを推定する"
fi

TEMPLATE=$(cat "$WORK_DIR/prompts/session1-base.txt")
PROMPT="${TEMPLATE//\{\{PHOTO_SECTION\}\}/$PHOTO_SECTION}"
PROMPT="${PROMPT//\{\{MEMO_SECTION\}\}/$MEMO_SECTION}"

# AIエージェント呼び出し（Claude or Antigravity）
if [ "$USE_CLAUDE" = true ]; then
  RESULT=$(echo "$PROMPT" | claude --print --model claude-sonnet-4-6 \
    --allowedTools "WebSearch,WebFetch" 2>>"$LOG_FILE")
else
  RESULT=$(agy -p "$PROMPT" 2>>"$LOG_FILE")
fi

JSON=$(echo "$RESULT" | extract_json)
if [ -z "$JSON" ]; then
  exit 1
fi

echo "$JSON" > "$WORK_DIR/temp/meals.json"
exit 0
```

### Session 2: MacroFactor登録（lib/session2.sh）

```
#!/usr/bin/env bash
# Session 2: MacroFactor登録
# Usage: bash lib/session2.sh -d DATE -i MEALS_JSON_FILE

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/common.sh"

TODAY=""
INPUT_FILE=""

while getopts "d:i:" opt; do
  case $opt in
    d) TODAY="$OPTARG" ;;
    i) INPUT_FILE="$OPTARG" ;;
  esac
done

[ ! -f "$INPUT_FILE" ] && exit 1

MEALS_JSON=$(cat "$INPUT_FILE")

TEMPLATE=$(cat "$WORK_DIR/prompts/session2-base.txt")
PROMPT="${TEMPLATE//\{\{TODAY\}\}/$TODAY}"
PROMPT="${PROMPT//\{\{MEALS_JSON\}\}/$MEALS_JSON}"

log "Session 2: Claude で MacroFactor 登録中..."
RESULT=$(echo "$PROMPT" | claude --print --model claude-sonnet-4-6 \
  --allowedTools "mcp__macrofactor__*,Bash,WebSearch,WebFetch" 2>>"$LOG_FILE")

JSON=$(echo "$RESULT" | extract_json)
[ -z "$JSON" ] && exit 1

echo "$JSON" > "$WORK_DIR/logs/${TODAY}-final.json"
exit 0
```

### 共通ユーティリティ（lib/common.sh）

```
#!/usr/bin/env bash
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

LOG_FILE="${LOG_FILE:-/dev/stderr}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

extract_json() {
  python3 -c "
import sys, re, json
text = sys.stdin.read()
match = re.search(r'\{.*\}', text, re.DOTALL)
if match:
    try:
        print(json.dumps(json.loads(match.group()), ensure_ascii=False))
    except:
        pass
"
}
```

注目してほしいのは、スクリプトに**栄養計算ロジックも、画像判定ロジックも、食品マスタへのマッチングロジックも書かれていない**こと。Bashがやっているのは「ファイルを見つけてAIに渡し、返ってきたJSONを次のサービスに渡す」だけだ。

## 4. 副産物：AIモデルを差し替え可能な構造になる

このアーキテクチャを動かして1週間ほどで、**もう一つの恩恵**に気づいた。

### 4-1. 最初の壁：Claude の使用量制限

開発中、デバッグで何度も実行していたら、ある日LINEに「解析に失敗しました」が飛んできた。Claudeの使用量制限だ。

それ以上に効いたのは「**食べ物アナライザーのために、Claude Codeの本業の枠を食うのはもったいない**」という感覚。趣味プロジェクトに本業の開発リソースを取られるのは本末転倒。

### 4-2. 切り替えコストがほぼゼロだった

ここで効いてきたのが「AIをハブにする」設計だ。栄養分析の処理を Gemini に振ってみることにした。

```
# Before
claude "この食事の栄養情報を分析してください" < photo.jpg

# After
gemini "この食事の栄養情報を分析してください" < photo.jpg
```

**コマンド名を変えるだけ**。プロンプト（=ビジネスロジック）は完全に同じ。スクリプトの構造もそのまま。

ロジックを「コード」ではなく「自然言語の指示」に外出ししているおかげで、AIモデルが交換可能なコンポーネントになっている。

結果：

* Claude（Sonnet）：栄養分析に約1分
* Gemini（3.1-pro-preview）：同じ処理が数十秒

体感の応答制限もGeminiの方が緩く、毎日のワークフローが安定して回るようになった。その後 gemini-cli が Antigravity（`agy`）に統合された際も、同じ要領で `agy` に置換するだけで移行完了。

### 4-3. 設計上の含意

ここから読み取れるのはこういうことだ。

* **ロジックを自然言語に追い出すと、実装が「モデル非依存」になる**
* 各AIの「得意な処理」「制限」「コスト」に合わせて、処理単位ごとにモデルを差し替えられる
* 画像認識は Gemini、MCP呼び出しは Claude、要約は Haiku、みたいな最適化が現実的になる

ちなみに途中で Gemini-3.5-Flash に変えてみたら、なぜか遅くなったので 3.1-pro-preview に戻した。モデル選択も試行錯誤の対象になる、という意味でもこの設計は柔らかい。

## 5. まとめ：このパターンが効く場面

「AIエージェントをハブにする」アーキテクチャは、こういう特性を持つ案件と相性が良い。

* 繋ぎ先の各サービスに「曖昧な判断」が要る
* 個人開発・社内ツールで、ビジネスロジックを書く時間がない
* 完全な精度より、毎日確実に回ることのほうが大事
* 後から要件・サービス・モデルが入れ替わりそう

逆に、**ミリ秒単位のレイテンシが必要**だったり、**100%決定的な出力が必要**な処理には向かない。そこは普通にコードを書いた方がいい。

要するに、「コードを書くべきかAIに預けるべきか」という**新しい設計の選択肢**が増えたと捉えるといい。複数サービス連携で詰まったとき、選択肢に入れてみてほしい。
