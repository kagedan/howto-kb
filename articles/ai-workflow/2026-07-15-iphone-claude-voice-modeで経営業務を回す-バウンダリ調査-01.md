---
id: "2026-07-15-iphone-claude-voice-modeで経営業務を回す-バウンダリ調査-01"
title: "iPhone + Claude Voice Modeで経営業務を回す ── バウンダリ調査"
url: "https://qiita.com/dave-kiara-inc/items/d13f8b2b5809b4bf13c3"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "Python", "qiita"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-rss"
query: ""
---

## 背景

Claude Voice Modeが速い。自然に話せて、割り込みにも強く、タイピングより口頭の方が速いと感じる場面が増えた。

経営の仕事(メール、Slack、スケジュール調整、契約レビュー、資料フィードバック)を「iPhone + 音声だけ」で回せないか検証した。PCなし、タイピングなし、移動中でも音声だけで完結する働き方が目標。

まず現状の仕様を調べ、境界線を明確にした。

## 結論(先出し)

**Voice Modeは「会話専用」。「実行」は別モードが必要。**

| モード | できること | できないこと |
|---|---|---|
| Voice Mode(音声会話) | 壁打ち、要約、意思決定支援、Web検索 | Reminders/Calendar/Messages/Maps/Health操作 |
| テキストチャット(タイプ or ディクテーション) | 上記 + Reminders作成・カレンダー登録・メール下書き | Apple純正以外のアプリ操作(Todoist、Slack等) |

公式ヘルプに明記あり:

> Most functionality described below is not compatible with our voice mode beta feature at this time.
> (アプリ連携機能は、現時点でvoice modeと互換性がない)

## なぜ紛らわしいか

「マイクボタンでの音声入力」と「Voice Mode」は別機能。

- **マイクボタン(ディクテーション)**: 音声→テキスト変換だけ。送信後はただのテキストチャット。ツール呼び出しが使える。
- **Voice Mode(会話モード)**: 双方向の音声会話そのもの。ツール呼び出しは使えない。

「Voice Modeで話しかけたらカレンダーに予定を入れてくれる」体験は、現状存在しない。

## 補足の境界: Remindersしか繋がらない

テキストチャット経由でも、ネイティブ連携はApple純正アプリ(Reminders/Calendar/Mail/Messages/Maps/Health)限定。Todoist、Things、Notion、Slackへの直接操作は非対応。

## 自分で埋める3つの方法

| アプローチ | 工数 | Voice Mode内で完結 | 使う言語 |
|---|---|---|---|
| ① Shortcuts + Siri | 小 | × (別入口) | Shortcuts DSL |
| ② 自作MCPサーバー | 中 | × (テキストのみ) | Python/TS |
| ③ フルスクラッチiOSアプリ | 大 | ○ | Swift |

### ① Shortcuts + Siri(最速)

Voice Modeを経由せず、Siri発話 or Action ButtonからClaude APIを直接叩く。

```
POST https://api.anthropic.com/v1/messages
Headers:
  x-api-key: YOUR_API_KEY
  anthropic-version: 2023-06-01
  content-type: application/json

Body:
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 500,
  "messages": [
    {"role": "user", "content": "音声入力からタスク名と期限を抽出しJSONのみ返答: '明日15時までに資料をまとめる'"}
  ]
}
```

レスポンスをパースして対象アプリを呼ぶ。

```
things:///add?title=資料をまとめる&when=tomorrow&deadline=15:00
```

Todoist/Slack/Notionは各REST APIを直接叩けばよい。

- **メリット**: 今日から動く。追加スキル不要。
- **制約**: 単発コマンド向き。Voice Modeとは別入口(相談はVoice Mode、実行はShortcuts、の2段構え)。

### ② 自作MCPサーバー(中規模)

対象アプリのAPIをラップし、Claudeのテキストチャットから呼ぶ。Voice Modeからは呼べない。「壁打ちはVoice Mode、実行はテキストに切り替えてMCP経由」という運用になる。

### ③ フルスクラッチiOSアプリ(本命だが工数大)

`SFSpeechRecognizer`で音声認識 → Claude APIで意図解析 → 対象アプリのAPI実行。会話と実行を1つの音声体験に統合できる唯一の方法。Swift実装が必要。

## 現実的な着地

- **今すぐ始める**: Voice Modeで相談・決定 → 実行だけShortcuts経由でAPIを叩く。2段構えで最速のMVP。
- **会話中にシームレスに実行まで行きたい**: 現状はフルスクラッチのSwiftアプリのみ。Anthropic側のVoice Mode拡張(ツール対応の広がり)を待つのも選択肢。
