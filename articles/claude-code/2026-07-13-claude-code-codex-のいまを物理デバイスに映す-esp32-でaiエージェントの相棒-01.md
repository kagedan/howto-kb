---
id: "2026-07-13-claude-code-codex-のいまを物理デバイスに映す-esp32-でaiエージェントの相棒-01"
title: "Claude Code / Codex の「いま」を物理デバイスに映す — ESP32 でAIエージェントの相棒を作った"
url: "https://qiita.com/kangyufei/items/0872df7ecd2be24d1c19"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "Python", "qiita"]
date_published: "2026-07-13"
date_collected: "2026-07-14"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- **Seeed SenseCAP Indicator D1**（ESP32-S3 + 4インチ 480×480 タッチスクリーン）を、Claude Code / Codex エージェントの**物理ステータスディスプレイ兼「相棒（コンパニオン）」**に改造しました。
- エージェントが「考え中」「ツール実行中」「入力待ち」「完了」といった状態を、机の上のデバイスがリアルタイムに表示してくれます。
- 最大4セッションを同時に表示。アイドル中はローカルLLMが気の利いた一言をつぶやき、放置するとスクリーンセーバーで瞬きする目が表示されます。
- ソースは MIT ライセンスで公開しています → https://github.com/yufeikang/indicator-ai-companion

![Agent HUD デモ](https://github.com/yufeikang/indicator-ai-companion/raw/main/docs/media/demo-full-poster.jpg)

---

## 作ったもの

複数のターミナルで Claude Code や Codex を走らせていると、「あのセッション、今どうなってるんだっけ？」と画面を行き来することがよくあります。ビルドが終わったのか、こちらの入力を待っているのか、まだ延々と考えているのか — それを確認するためだけに Alt+Tab を連打する日々でした。

そこで、**エージェントの状態を机の上の小さな物理デバイスに常時表示する**プロジェクトを作りました。ターゲットにしたのは Seeed の [SenseCAP Indicator D1](https://www.seeedstudio.com/) という ESP32-S3 ベースのタッチディスプレイ端末です。

エージェントが動き出すとデバイス上のアイコンが「呼吸する」ように脈動し、完了すれば色が変わって知らせてくれる。手が空いているときはローカルLLMが生成した一言をしゃべり、しばらく放置すると瞬きする目のスクリーンセーバーになる — そんな「AIエージェントの相棒」です。

---

## デモ

| Agent HUD | スクリーンセーバー |
|:---:|:---:|
| ![HUD](https://github.com/yufeikang/indicator-ai-companion/raw/main/docs/media/demo-full-poster.jpg) | ![Eyes](https://github.com/yufeikang/indicator-ai-companion/raw/main/docs/media/demo-eyes-poster.jpg) |

動画版はリポジトリの `docs/media/demo-full.mp4` / `docs/media/demo-eyes.mp4` に置いてあります。

---

## 主な機能

### 🖥️ Agent HUD
エージェントのセッション状態をリアルタイムに可視化します。`thinking`（考え中）/ `tool execution`（ツール実行中）/ `awaiting input`（入力待ち）/ `completion`（完了）を、色とアニメーションで表現。プロバイダごとにアイコンが異なり（Claude のスパーク、Codex のコードマーク）、作業中はアイコンが「呼吸」します。

### 🔀 マルチセッション・アイコンバー
最大4セッションを同時に扱えます。画面下部のアイコンをタップするとセッションを切り替えられ、プロジェクト名がステータスに応じて色分けされます。タップしたセッションは約45秒フォーカスされ、その後は最後にアクティブだったセッションへ自動的に戻ります。

### 💬 AIコンパニオンカード
アイドル時、ローカル / LAN 上のLLMが「気の利いた一言」を生成します。物理ボタンから呼び出すこともできます。

### 😴 スクリーンセーバー
300秒間操作がないと、全画面で瞬きする目とLLM生成のウィットに富んだセリフが表示されます。緊急のアラートが保留中のときは起動しません。

### 🌐 多言語対応
`BRIDGE_LANG` 環境変数（`zh` / `en`）で UI とコンパニオンのテキストを切り替えられます。

---

## アーキテクチャ

このプロジェクトの肝は、**「映像フレームを送らず、意味的なステータスだけを送る」**という設計です。

```
Claude Code / Codex
      │  webhook (HTTP POST)
      ▼
  Bridge デーモン (Python)
   ・session_id / thread_id でメッセージを束ねる
   ・セッションレジストリを管理
   ・意味的なステータス更新のみを送出
      │  暗号化された ESPHome API
      ▼
  SenseCAP Indicator D1 (ESP32-S3 + LVGL)
   ・run / think / wait / done / ready / online
     という言語非依存のステータスで
     アニメーションと色を駆動
```

Claude Code / Codex は webhook（HTTP POST）で bridge デーモンにイベントを送ります。bridge は `session_id` / `thread_id` ごとにメッセージを束ね、セッションレジストリを保持し、**動画フレームではなく意味的なステータス更新だけ**を暗号化 ESPHome API 経由でデバイスに push します。

`run` / `think` / `wait` / `done` / `ready` / `online` という**言語非依存のステータス値**がデバイス側のアニメーションと色を駆動し、ローカライズされたテキストは UI ラベルとして描画されます。アイコンのタップはデバイス⇔bridge のローカルループで完結し、エージェント側には戻りません。

この分離のおかげで、通信量は極小に抑えられ、UIの言語やアニメーションはデバイス/bridge 側だけで完結して差し替えできます。

---

## ハードウェア

- **MCU:** ESP32-S3（WiFi/BLE）、ESPHome + LVGL で駆動
- **ディスプレイ:** 4インチ 480×480 IPS 静電容量式タッチ（ST7701S + FT5x06）
- **コプロセッサ:** RP2040（現状は未使用）

埋め込みCJKフォントは GB2312 のおよそ 3,800 文字 + ASCII をカバーしています。それ以外の文字体系を使う場合はフォントの拡張が必要です。

---

## セットアップ

大まかな流れは以下の通りです（正確なコマンドは [README](https://github.com/yufeikang/indicator-ai-companion) を参照してください）。

1. **アセットのビルド**（初回のみ）: Python ユーティリティでフォント・背景・セッションアイコンを生成します。
2. **ファームウェアの書き込み**: 初回は USB 経由（約30秒）、以降は WiFi OTA で更新できます。
3. **Bridge デーモンの起動**: Docker（`docker compose up`）または直接 Python で起動。デバイスIP・暗号化キー・言語などを環境変数で渡します。
4. **エージェントのフック接続**: 用意された JSON スニペットを Claude Code / Codex の設定ファイルにマージします。
5. **デモモードで動作確認**: 実際のエージェントを走らせなくても、スクリプト化されたイベントストリームで表示を確認できます。

Docker を使う場合はおおむねこんなイメージです：

```bash
# .env にデバイスIP・暗号化キー・言語などを設定してから
docker compose up -d
```

> **注意:** `.env` の `INDICATOR_NOISE_PSK` は、ファームウェア側の `api_key` と一致している必要があります。

---

## 技術的なこだわり

- **映像ではなくセマンティックなステータスを送る**: 端末は「状態」を受け取ってから自前でアニメーションを生成するので、帯域を食わず、UIの改修がホスト側に依存しません。
- **暗号化された ESPHome API**: bridge ↔ デバイス間は ESPHome の Noise 暗号化 API で通信します。
- **セッションの束ね方**: 連続する webhook イベントを `session_id` / `thread_id` でまとめ、チラつかない状態遷移を実現しています。
- **ローカルLLMでコンパニオン生成**: 相棒のセリフはローカル / LAN のLLMで生成するため、外部に会話内容を出しません。

---

## まとめ

「AIエージェントの状態を、机の上の物理デバイスで一目で分かるようにする」という小さなアイデアから始めたプロジェクトですが、実際に置いてみるとエージェントの"気配"が感じられて思いのほか楽しいです。ESP32 + ESPHome + LVGL の題材としても、Claude Code / Codex のフック連携の実例としても参考になれば幸いです。

- **リポジトリ:** https://github.com/yufeikang/indicator-ai-companion
- **ライセンス:** MIT © 2026 Yufei Kang

スター・Issue・PR、お待ちしています！ 🌟
