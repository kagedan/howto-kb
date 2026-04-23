---
id: "2026-04-12-claudeとgeminiの全チャット履歴をnotebooklmに食わせたら自分のai使い分けが丸裸-01"
title: "ClaudeとGeminiの全チャット履歴をNotebookLMに食わせたら、自分のAI使い分けが丸裸になった話"
url: "https://zenn.dev/minipoisson/articles/claude-gemini-notebooklm"
source: "zenn"
category: "ai-workflow"
tags: ["Gemini", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## はじめに：「自作したら、公式が追いついてきた」というループ

[第1弾の記事](https://zenn.dev/minipoisson/articles/d8b307f8eedc5f)でGeminiの全チャット履歴をNotebookLMに取り込むツールを作り、程なくGeminiとNotebookLMの公式連携が強化されて、チャット履歴をNotebookLMのノートブックでそのままソースとして扱えるようになりました。

<https://zenn.dev/minipoisson/articles/d8b307f8eedc5f>

振り返ってみると、Googleの各種機能を使っていて不足を感じるたびにツールを作ったり手法を考案したりすると、その直後に公式機能の向上が発表されてそれらが不要になる——ということをこれまで何度か繰り返してきた気がします。

ですが、今回取り組んだ「**ClaudeのチャットをGeminiのチャットと合わせてNotebookLMで活用する**」ことは、さすがにGoogle公式ツールの機能では今後も実現できないでしょう。

## 1. 【背景】Claudeの利用開始当初からやりたかったこと

Claude を使い始めた当初から、Geminiで実施しているのと同様に、Claudeのチャット履歴もNotebookLMで活用したいと思っていました。

Geminiの履歴は Google Takeout でエクスポートできますが、ClaudeでもGDPR対応のPrivacy Portalを通じてデータエクスポートをリクエストできることをClaudeでのチャットで知り、早速試してみることにしました。

## 2. 【手順①】ClaudeのチャットをエクスポートするPrivacy Portal

### エクスポートのリクエスト

[claude.ai/settings/privacy](https://claude.ai/settings/privacy) にアクセスし、「Export Data」からリクエストを送信します。

### 届くまでの時間

一般的には数日かかると言われていますが、筆者の場合はリクエストから**ほぼ即時**にダウンロードリンクのメールが届きました。

```
Created at: Thu, Apr 9, 2026 at 7:02 AM
Delivered after 1 second
From: Anthropic <no-reply-...@mail.anthropic.com>
Subject: Your data is ready for download
```

もちろんタイミングによって変わる可能性はありますが、想定より大幅に早く入手できる場合もあるようです。

### ZIPの中身

ダウンロードしたZIPを展開すると、`conversations.json` が含まれています。これが全チャット履歴の本体です。

## 3. 【手順②】conversations.json の構造とGemini版との違い

Gemini版の `MyActivity.json` と比較したときの `conversations.json` の主な違いは以下の通りです。

| 項目 | Gemini（MyActivity.json） | Claude（conversations.json） |
| --- | --- | --- |
| エクスポート手段 | [Google Takeout](https://takeout.google.com/) | [Privacy Portal](https://claude.ai/settings/privacy) |
| トップレベル | オブジェクトの配列 | 会話オブジェクトの配列 |
| 話者の識別 | モデル/ユーザー区分 | `"human"` / `"assistant"` |
| メッセージ本文 | `text` フィールド | `chat_messages[].text` |
| HTMLの混入 | あり | あり（要クリーニング） |

JSONの構造を手早く確認したい場合は以下のコマンドが便利です。

```
python -c "import json; d=json.load(open('conversations.json')); print(list(d[0].keys())); print(list(d[0]['chat_messages'][0].keys()))"
```

> ※ Windows（CMD・PowerShell）でも動作確認済みです。

## 4. 【手順③】変換スクリプトの紹介

Gemini版の `convert_history.py` の設計思想をそのまま踏襲し、Claude Code を使ってClaude向けに書き替えました。スクリプトはGitHubで公開しています。

<https://github.com/minipoisson/Claude_Json2md4NotebookLM>

### Gemini版との主な差分

設計はほぼ同じですが、以下の点が異なります。

* 入力ファイルのデフォルト名が `conversations.json`（Gemini版は `MyActivity.json`）
* 話者の識別を `"human"` / `"assistant"` で行う
* **デフォルトの分割サイズを1,500,000バイトから1,000,000バイトに変更**

最後の点については、1.5MBのまま運用していたところNotebookLMへの取り込みに失敗することが稀にあったため、安定性を優先して1MBに引き下げました。明示的に指定することも可能です。

```
python convert_claude_history.py --input_file conversations.json --output_file Claude_History.md --limit 1000000
```

### 主な機能

Gemini版と同じく、Python標準ライブラリのみで動作します。

1. **HTMLタグ除去 & Markdown整形** — 会話ログを可読性の高いMarkdown形式に変換します
2. **自動ファイル分割** — 指定サイズを超えると自動で連番ファイルに分割します（`Claude_History-01.md`, `-02.md`...）
3. **差分更新への対応** — `last_entry_time.txt` に最終処理日時を記録し、次回以降は新しい会話分のみ処理します

### 動作確認

試行錯誤して作り上げたGemini向けのスクリプトの設計を踏襲しているので、出力されたMarkdown形式のファイルをNotebookLMのノートブックのソースに追加するとエラーなく登録され、これまでの全てのチャットの内容が認識されました。

## 5. 【発見】「Geminiで出したアイデアをClaudeで磨く」ワークフローの可視化

GeminiとClaudeの両チャット履歴を同一のNotebookLMノートブックに登録した状態で、NotebookLMに「同時期のGeminiとClaudeのチャットには、扱う内容ややり取りの仕方の傾向にどのような違いがありますか？」と質問してみました。

### NotebookLMの分析結果

返ってきた回答を要約すると、以下の通りです。

**Claude：客観的で厳格な「シニアアーキテクト・編集者」**

* 複雑なプログラミングとアーキテクチャ設計（レガシーC#/.NETのモダン化、PythonコードのGAS移植など）
* 高品質な翻訳・執筆推敲（論文の構成、Zenn/note記事の批判的推敲、i18n/l10nパイプライン）
* 事実の整理と厳密な分析（API仕様の裏取り、システム構造の比較など）
* ハルシネーションを犯した場合は「存在しません」と即座に看破し、その構造まで冷静に分析する

**Gemini：熱狂的で共感性の高い「アイデアパートナー・チアリーダー」**

* Googleエコシステムの自動化（Gmail、GAS、NotebookLMの連携やAPI制限の回避など）
* クリエイティブ・マーケティング（記事タイトル案、X投稿戦略、アイコン画像生成など）
* 幅広い文脈の壁打ち（歴史・文化・AIの倫理・ユーモアなど、技術に限らない議論）
* ただし「もっともらしい嘘」をポジティブな言葉で返してしまう傾向がある

**結論として、NotebookLMはこう評しました：**

> 「GeminiをアイデアのDB・壁打ち相手として使い、そこで出た情報をClaudeで論理的に磨き上げたり厳格なコードに落とし込む、という高度なワークフローが、この時期のチャット履歴から明確に読み取れます」

自分でも何となく使い分けているという自覚はありましたが、こうして第三者的に言語化されると、改めて「確かにそうだ」と腑に落ちるものがありました。

### 両方の履歴があって初めて全貌が見えた事例

この分析で特に印象的だったのが、[**Geminiのハルシネーション事件**](https://zenn.dev/minipoisson/articles/gemini-hallucination-google-services)の追跡です。

<https://zenn.dev/minipoisson/articles/gemini-hallucination-google-services>

Google Cloud Translation APIの調査の際、GeminiはAI Mode含め一貫して架空のメソッド `translate_image` を自信満々に提示し続けました。それを検証・看破したのがClaudeとのやり取りでした。

この一連の流れは、GeminiとのチャットだけでもClaudeとのチャットだけでも全貌が把握できません。**両方の履歴を同一のNotebookに入れてこそ、「何を誰に聞いて、どのように解決したか」という一連のストーリーが初めて追跡可能になります。**

このAI横断のユースケースは、Google公式機能では永遠に実現できない領域です。

## まとめ

| ステップ | 内容 |
| --- | --- |
| エクスポート | [claude.ai/settings/privacy](https://claude.ai/settings/privacy) からリクエスト（今回は即時で届いた） |
| 変換 | `convert_claude_history.py` で `conversations.json` → Markdown |
| 取り込み | 生成された `Claude_History-xx.md` をNotebookLMへアップロード |
| 活用 | GeminiとClaudeの履歴を同一Notebookに統合してAI横断分析 |

スクリプトはMITライセンスで公開しています。

<https://github.com/minipoisson/Claude_Json2md4NotebookLM>

「自作したら公式が追いついてきた」というループを繰り返しながらも、今回のようにどんな公式機能でも代替できないユースケースに辿り着いたとき、やはり自分で作ることの意味を再確認できます。ぜひ試してみてください。
