---
id: "2026-04-05-claude-codevoicevox音声通知ずんだもんが完了を教えてくれる設定術-01"
title: "Claude Code×VOICEVOX音声通知｜ずんだもんが完了を教えてくれる設定術"
url: "https://zenn.dev/kobarutosato/articles/938fd0df1d22aa"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

Claude Codeで長いタスクを投げて、別の作業をしている。

ふと気づくと、もう終わっていた。  
いつ終わったかわからない。

**この「気づかない問題」、音声通知で解決できます。**

Claude CodeのHooks機構を使えば、タスク完了のたびにVOICEVOXで音声を鳴らせます。  
ずんだもん、春日部つむぎ、ナースロボなど5キャラがランダムで「できました！」と教えてくれる。

この記事でわかること：

* Claude Code **Stop Hook** の仕組みと設定方法
* VOICEVOX APIの2段階呼び出し（audio\_query → synthesis）
* **ランダムキャラ選択**で毎回違う声を鳴らすシェルスクリプト
* VOICEVOX停止時でもClaude Codeに影響しない**グレースフルデグレード設計**

前提環境：macOS / Claude Code インストール済み / Python 3 / curl

## 全体像：たった1ファイルで完結する仕組み

![](https://static.zenn.studio/user-upload/bd4d9d1d8419-20260405.png)

構成はシンプルです。

```
Claude Code（応答完了）
  │
  │  Stop Hook（settings.json）
  ▼
~/.claude/scripts/speak.sh
  │
  ├─ 1. ランダムにキャラ選択（VOICEVOX speaker ID）
  ├─ 2. ランダムにセリフ選択（Python）
  ├─ 3. VOICEVOX API: /audio_query（テキスト→クエリ）
  ├─ 4. VOICEVOX API: /synthesis（クエリ→WAV）
  └─ 5. afplay で再生（macOS）
```

依存するのは **curl, python3, afplay** だけ。  
外部ライブラリもnpmパッケージも不要です。

## Step 1：VOICEVOXをインストールする

VOICEVOXはローカルで動くテキスト読み上げエンジンです。  
REST APIを公開していて、デフォルトで `http://localhost:50021` でリッスンします。

### 方法A：GUIアプリ（おすすめ）

[VOICEVOX公式サイト](https://voicevox.hiroshiba.jp/) からmacOS版をダウンロード。

初回起動時、macOSのGatekeeperにブロックされることがあります。

```
「"VOICEVOX"は、開発元を検証できないため開けません」
```

**「システム設定」→「プライバシーとセキュリティ」→「このまま開く」** で許可してください。

Apple Silicon Macの場合、Rosettaが未インストールだとエラーになります。

```
# Rosettaをインストール（Apple Silicon Macのみ）
softwareupdate --install-rosetta --agree-to-license
```

### 方法B：Docker（GUIが不要な場合）

```
# CPU版（macOS推奨）
docker pull voicevox/voicevox_engine:cpu-latest
docker run --rm -p '127.0.0.1:50021:50021' voicevox/voicevox_engine:cpu-latest
```

### 動作確認

VOICEVOXを起動した状態で、以下を実行。

```
# 疎通チェック
curl -s http://localhost:50021/version
# → "0.25.1" のようなバージョンが返ればOK
```

## Step 2：VOICEVOX APIの仕組みを理解する

VOICEVOXの音声合成は**2段階API**です。

**1段階目：/audio\_query**  
テキストとspeaker IDを受け取り、アクセント・イントネーション情報を含むクエリJSONを返す。

**2段階目：/synthesis**  
クエリJSONを受け取り、WAVバイナリを返す。

なぜ2段階なのか。  
間にアクセント調整を挟める設計だからです。  
今回は直結して使いますが、「ここを強調したい」といった微調整が将来的に可能になります。

```
# 実際に試してみる
# 1. クエリ生成（ずんだもん ノーマル = speaker 3）
curl -s -X POST \
  "http://localhost:50021/audio_query?text=できました&speaker=3" \
  -H "Content-Type: application/json" > /tmp/query.json

# 2. 音声合成
curl -s -X POST \
  "http://localhost:50021/synthesis?speaker=3" \
  -H "Content-Type: application/json" \
  -d @/tmp/query.json > /tmp/test.wav

# 3. 再生
afplay /tmp/test.wav
```

ずんだもんの声で「できました」が聞こえたら成功です。

### 主要なspeaker ID

| ID | キャラクター | スタイル |
| --- | --- | --- |
| 2 | 四国めたん | ノーマル |
| 3 | ずんだもん | ノーマル |
| 8 | 春日部つむぎ | ノーマル |
| 10 | 雨晴はう | ノーマル |
| 13 | 青山龍星 | ノーマル |
| 14 | 冥鳴ひまり | ノーマル |
| 20 | もち子さん | ノーマル |
| 22 | ずんだもん | ささやき |
| 43 | 四国めたん | ヒソヒソ |
| 47 | ナースロボ＿タイプＴ | ノーマル |

全スタイルは75以上。お気に入りのキャラで試してみてください。

## Step 3：speak.sh を作成する

ここが本記事の核心です。  
以下のスクリプトを `~/.claude/scripts/speak.sh` に保存します。

```
#!/bin/bash
# Claude Code Stop Hook → VOICEVOX 音声通知
# 依存: curl, python3, afplay (macOS)

VOICEVOX_URL="${VOICEVOX_URL:-http://localhost:50021}"

# --- 1. VOICEVOXの疎通チェック ---
# 起動していなければ静かに終了（Claude Codeに影響を与えない）
if ! curl -s --max-time 1 "${VOICEVOX_URL}/version" > /dev/null 2>&1; then
  exit 0
fi

# --- 2. ランダムにキャラ選択 ---
SPEAKERS=(3 8 14 47 20)
# 3=ずんだもん, 8=春日部つむぎ, 14=冥鳴ひまり, 47=ナースロボ, 20=もち子さん
SPEAKER=${SPEAKERS[$((RANDOM % ${#SPEAKERS[@]}))]}

# --- 3. ランダムにセリフ選択（Python） ---
LINE=$(python3 -c "
import random, urllib.parse
lines = [
    'できました！',
    '完了しました！',
    '終わりました！',
    'タスク完了です！',
    'お待たせしました！',
    '処理が終わりました！',
    '完了です！',
    '結果が出ました！',
    'チェックお願いします！',
    'お疲れさまです！',
    '準備できました！',
    '対応完了です！',
    '確認お願いします！',
    '作業終わりました！',
    'ばっちりです！',
]
chosen = random.choice(lines)
print(urllib.parse.quote(chosen))
")

# --- 4. VOICEVOX API 2段階呼び出し ---
QUERY=$(curl -s --max-time 5 -X POST \
  "${VOICEVOX_URL}/audio_query?text=${LINE}&speaker=${SPEAKER}" \
  -H "Content-Type: application/json")

# クエリ取得失敗時は終了
[ -z "$QUERY" ] && exit 0

WAV_FILE="/tmp/claude-voicevox-$$.wav"
curl -s --max-time 10 -X POST \
  "${VOICEVOX_URL}/synthesis?speaker=${SPEAKER}" \
  -H "Content-Type: application/json" \
  -d "$QUERY" \
  -o "$WAV_FILE"

# --- 5. 再生＋後処理 ---
[ ! -f "$WAV_FILE" ] && exit 0

afplay "$WAV_FILE" &
sleep 0.1
rm -f "$WAV_FILE"

exit 0
```

実行権限を付与します。

```
chmod +x ~/.claude/scripts/speak.sh
```

### 設計のポイントを深掘りする

**ランダム性の二重化**

キャラもセリフもランダムです。  
5キャラ × 15セリフ = **75パターン**。毎回違う体験になります。

飽きたらセリフを追加するだけで拡張できます。キャラもspeaker IDを足せばOK。

**グレースフルデグレード**

```
if ! curl -s --max-time 1 "${VOICEVOX_URL}/version" > /dev/null 2>&1; then
  exit 0
fi
```

この1行目が肝です。

VOICEVOXが起動していなければ、`curl` が1秒以内にタイムアウトして `exit 0` で静かに終了。  
クエリ取得失敗、WAVファイル未生成でも同様に `exit 0`。

**Claude Code本体には一切影響を与えません。**

Hookスクリプトが非ゼロで終了すると、Claude Codeのverboseモードでエラーが表示されます。`exit 0` で統一することで、通知が鳴らなくても邪魔にならない設計です。

**非同期再生**

```
afplay "$WAV_FILE" &
sleep 0.1
rm -f "$WAV_FILE"
```

`afplay` をバックグラウンドで起動し、`sleep 0.1` で再生開始を待ってからWAVを削除。  
再生が終わるまでスクリプトがブロックしない = Claude Codeの次の操作を止めません。

## Step 4：Claude Code Hooksを設定する

`~/.claude/settings.json` に以下を追加します。

```
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/scripts/speak.sh"
          }
        ]
      }
    ]
  }
}
```

既にsettings.jsonに他の設定がある場合は、`hooks` キーの中に `Stop` を追加してください。

### なぜStop Hookなのか

Claude Code Hooksには複数のイベントがあります。

| イベント | 発火タイミング | 通知用途 |
| --- | --- | --- |
| **Stop** | **Claudeの応答完了時** | **作業完了通知に最適** |
| Notification | 入力待ち・権限要求時 | 「確認してね」通知 |
| PreToolUse | ツール実行前 | コード検証向き |
| PostToolUse | ツール実行後 | フォーマッタ実行向き |

**Stopは「Claudeが返答を出し終わった瞬間」に発火します。**

つまり、長いタスクが完了した直後に音声が鳴る。  
これが「作業完了通知」として最適な理由です。

### matcherについて

空文字列はすべてのStop条件にマッチします。  
特定の条件でだけ鳴らしたい場合は、正規表現パターンを指定できます。

### 設定ファイルの配置場所

| ファイル | スコープ |
| --- | --- |
| `~/.claude/settings.json` | 全プロジェクト共通 |
| `.claude/settings.json` | プロジェクト単位 |
| `.claude/settings.local.json` | プロジェクト単位（gitignore推奨） |

チームで共有したくない個人設定は `~/.claude/settings.json` に書くのがベストです。

## Step 5：動作確認とトラブルシューティング

### 動作確認

```
# 1. VOICEVOXが起動していることを確認
curl -s http://localhost:50021/version

# 2. speak.shを単体テスト
~/.claude/scripts/speak.sh

# 3. Claude Codeで適当な質問をして、応答完了後に音声が鳴るか確認
claude "1+1は？"
```

### よくあるトラブルと解決策

**音が鳴らない：VOICEVOXが起動していない**

```
# 確認
curl -s http://localhost:50021/version
# → curl: (7) Failed to connect → VOICEVOXを起動してください
```

Docker版の場合：

```
docker run --rm -p '127.0.0.1:50021:50021' voicevox/voicevox_engine:cpu-latest
```

**音が鳴らない：スクリプトに実行権限がない**

```
ls -la ~/.claude/scripts/speak.sh
# → -rw-r--r-- なら権限なし
chmod +x ~/.claude/scripts/speak.sh
```

**音が鳴らない：settings.jsonの構文エラー**

```
# JSONの構文チェック
python3 -m json.tool ~/.claude/settings.json
```

カンマの過不足が最も多い原因です。設定変更後はClaude Codeを再起動してください。

**音が途切れる・無音になる**

`sleep 0.1` の値を `0.3` 〜 `0.5` に増やしてみてください。  
マシンの負荷が高いとafplayの読み込みが遅れることがあります。

## カスタマイズ例

### AskUserQuestionフックで「入力待ち」も通知する

Claude Codeがユーザーに質問を投げて入力待ちになる瞬間がある。  
ツール許可の確認、方針の確認、エラー時の判断。  
**この「待ち状態」に気づかないと、作業が止まったままになる。**

AskUserQuestion matcher を使えば、Claude Codeが質問した瞬間に音声で呼びかけてくれます。

```
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "~/.claude/scripts/speak.sh" }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "AskUserQuestion",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/scripts/speak-waiting.sh"
          }
        ]
      }
    ]
  }
}
```

**ポイント：matcherに `"AskUserQuestion"` を指定する**ことで、全ツール実行時ではなく「ユーザーへの質問」のときだけ発火します。

`speak-waiting.sh` は `speak.sh` と同じ構造ですが、セリフを「待ち系」に変えています：

```
#!/bin/bash
# Claude が入力待ち（質問・許可要求）のときにVOICEVOXで通知

VOICEVOX_URL="${VOICEVOX_URL:-http://localhost:50021}"

if ! curl -s --max-time 1 "${VOICEVOX_URL}/version" > /dev/null 2>&1; then
  exit 0
fi

SPEAKERS=(3 8 14 47 20)
SPEAKER=${SPEAKERS[$((RANDOM % ${#SPEAKERS[@]}))]}

LINE=$(python3 -c "
import random, urllib.parse
lines = [
    'おーい、まってるよ！',
    'おへんじまだかな？',
    'にゅうりょくまちなのだ！',
    'ゆるしてほしいのだ！',
    'ぽちっとおねがいなのだ！',
    'きょかまちだよ！',
    'ここでとまってるのだ！',
    'おねがいしまーす！',
    'おーい、みてみて！',
    'つぎにすすみたいのだ！',
]
chosen = random.choice(lines)
print(urllib.parse.quote(chosen))
")

QUERY=$(curl -s --max-time 5 -X POST \
  "${VOICEVOX_URL}/audio_query?text=${LINE}&speaker=${SPEAKER}" \
  -H "Content-Type: application/json")
[ -z "$QUERY" ] && exit 0

WAV_FILE="/tmp/claude-voicevox-waiting-$$.wav"
curl -s --max-time 10 -X POST \
  "${VOICEVOX_URL}/synthesis?speaker=${SPEAKER}" \
  -H "Content-Type: application/json" \
  -d "$QUERY" \
  -o "$WAV_FILE"

[ ! -f "$WAV_FILE" ] && exit 0
afplay "$WAV_FILE" &
sleep 0.1
rm -f "$WAV_FILE"
exit 0
```

`chmod +x ~/.claude/scripts/speak-waiting.sh` で実行権限を付与してください。

### Notificationフックも追加する

応答完了と入力待ちに加え、通知イベントでも音声を鳴らす場合：

```
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "~/.claude/scripts/speak.sh" }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "AskUserQuestion",
        "hooks": [
          { "type": "command", "command": "~/.claude/scripts/speak-waiting.sh" }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "~/.claude/scripts/speak.sh" }
        ]
      }
    ]
  }
}
```

### Linux対応

macOSの `afplay` を `aplay` に差し替えるだけです。

```
# speak.sh の再生部分を変更
# macOS:
# afplay "$WAV_FILE" &

# Linux:
aplay "$WAV_FILE" &
```

### キャラ・セリフの追加

```
# speak.sh のSPEAKERS配列にIDを追加
SPEAKERS=(3 8 14 47 20 2 13 22)
# 22=ずんだもん（ささやき）を追加
```

セリフもPythonの `lines` リストに追加するだけです。  
季節ネタを入れると楽しいですよ。

## まとめ

| 項目 | 内容 |
| --- | --- |
| 仕組み | Stop Hook + PreToolUse Hook → speak.sh / speak-waiting.sh → VOICEVOX API → afplay |
| 依存 | curl, python3, afplay（macOS標準搭載） |
| 通知パターン | 完了通知: 5キャラ × 15セリフ = 75パターン / 入力待ち: 5キャラ × 10セリフ = 50パターン |
| 耐障害性 | VOICEVOX停止時は静かに exit 0 |
| 設定時間 | 約5分（VOICEVOX導入済みなら） |

シェルスクリプト2枚、settings.jsonに数行。  
これだけでClaude Codeの作業体験が変わります。

ぜひ好きなキャラで試してみてください。
