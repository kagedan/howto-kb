---
id: "2026-04-27-蔵人と言えばclaudeが起動する環境を作った話windows-voiceattack-01"
title: "「蔵人」と言えばClaudeが起動する環境を作った話（Windows + VoiceAttack）"
url: "https://zenn.dev/rhu/articles/claude_voice_launch"
source: "zenn"
category: "ai-workflow"
tags: ["GPT", "zenn"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

「Claudeを使いたいけど、毎回アプリを開くのが地味に面倒」

そう感じていたので、声をかけるだけでClaudeが起動する環境を作りました。使ったのは**VoiceAttack**というツール。無料トライアル版で十分実現できます。

---

## 必要なもの

* Windows PC
* Claudeデスクトップアプリ（インストール済み）
* VoiceAttack（無料トライアル版でOK）

---

## 手順1：Claudeをログイン時に自動起動する

まずPC起動時にClaudeが自動で立ち上がるようにします。

1. Windowsの「設定」→「アプリ」→「インストールされているアプリ」→「Claude」を開く
2. 「ログイン時に実行する」のトグルを**オン**にする

これだけで、PC起動後にClaudeが自動で開くようになります。

---

## 手順2：VoiceAttackをインストールする

1. <https://voiceattack.com> からダウンロード・インストール
2. 起動時の案内画面は「Go」→「Close」→「OK」と進む

---

## 手順3：音声コマンドを作る

1. VoiceAttackのメイン画面で、鉛筆アイコン（プロフィール編集）をクリック
2. 「New Command」をクリック
3. 「When I say:」欄に起動ワードを入力
4. 「Other >」→「Windows」→「Run an Application」をクリック
5. アプリのパス欄に以下を入力：

6. 「OK」をクリックして保存

---

## 手順4：VoiceAttackをPC起動時に自動起動する

VoiceAttackの設定画面で「Start VoiceAttack when Windows starts」をオンにする。

これで、PC起動 → Claude自動起動 → VoiceAttack自動起動、の環境が整います。

---

## 起動ワードの選び方

「Claude」と話しかけると\*\*「蔵人」\*\*と誤認識されます。

なので逆に「蔵人」をコマンドワードに登録しました。誤認識されやすい言葉は、そのまま登録してしまうのが一番手軽です。

---

## 登録しているコマンド一覧

| 話しかける言葉 | 動作 |
| --- | --- |
| 蔵人 | Claudeを起動（`claude:`） |
| コーデックス | Codexを起動 |
| チャッピー | ChatGPTを起動 |
| マイク | Windows + H（音声入力）を起動 |
| メモ帳 | メモ帳（notepad.exe）を起動 |

認識されにくい言葉は、似た音の別の言葉に置き換えるのがポイントです。

---

## Tips

* 音声認識の精度が低い場合は、VoiceAttackの「Let's train the speech engine」でトレーニングを行うと改善します
* VoiceAttackのマイクアイコンが赤くなっている状態がリスニング中です
* 設定完了後は声をかけるだけなので、キーボードに手を伸ばす必要がなくなります
