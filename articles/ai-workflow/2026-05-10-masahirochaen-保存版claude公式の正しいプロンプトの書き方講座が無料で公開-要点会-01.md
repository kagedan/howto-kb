---
id: "2026-05-10-masahirochaen-保存版claude公式の正しいプロンプトの書き方講座が無料で公開-要点会-01"
title: "@masahirochaen: 【保存版】Claude公式の「正しいプロンプトの書き方」講座が無料で公開 要点：会話風に書くのはNGで段階的に作るべし"
url: "https://x.com/masahirochaen/status/2053313212377096527"
source: "x"
category: "ai-workflow"
tags: ["prompt-engineering", "x"]
date_published: "2026-05-10"
date_collected: "2026-05-12"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

【保存版】Claude公式の「正しいプロンプトの書き方」講座が無料で公開

要点：会話風に書くのはNGで段階的に作るべし

①推奨される10要素の組立順
②V1→V5でプロンプトが進化する実演
③Examples・Pre-fill・Extended thinkingの神テク

一通り見るだけで勉強になるので是非

スレッドで詳細解説↓ https://t.co/Zg7O4zbazN

(2/n)
動画はAnthropic Applied AIチームのHannah & Christianによる "Prompting 101"。

題材は実顧客ベース、スウェーデン保険会社の車事故クレーム解析。事故報告書（17項目チェックボックス）と手描きスケッチをClaude 4 Sonnetに読ませて「過失はどっちか」を判定させる。

V1の初期プロンプトをV5まで段階的に強化していくハンズオン形式。

(3/n)
Anthropic推奨のプロンプト構造は10要素を順番に積む。

①Task context（役割と任務）
②Tone context（口調・原則）
③Background data（不変情報）
④Examples（Few-shot）
⑤Conversation history
⑥Detailed instructions
⑦Final reminder（重要事項の再確認）
⑧Output formatting
⑨Pre-fill
⑩Extended thinking

会話風に書くと、力のほんの一部しか出ない。

(4/n)
V1: 「事故報告書を分析して」だけ → Claudeはなんと「スキー事故」と推測。コンテキスト不足で全く違う方向に走る。

V2の追加: 役割「車保険会社のClaim adjusterを補助するAI」＋ トーン「自信がない時は推測しない、factualに保つ」。

これだけで車事故と認識しはじめる。コンテキストとトーンは必須要素。

(5/n)
V3でフォーム構造そのもの（17項目の意味、2列＝車両A/B、Swedish言語）をsystem promptに移す。

ポイントは「不変な情報」と「動的な情報」を分けること。不変部はprompt cachingにも最適。

ClaudeはXMLタグでfine-tuningされているので、`<form_structure>`...のような構造化が効く。Markdownも有効。

(6/n)
Examples（Few-shot）はClaudeを誘導する最強テク。

グレーゾーンの過去事例＋人間がつけた正解ラベルをsystem promptに丸ごと入れる。画像例もbase64で渡せる。

「prompt engineeringはempirical scienceだ」とHannah。Claudeが間違えた場面を例として追加するフィードバックループを回し続ける。これが本気の運用。

(7/n)
V4で「分析の順序」を明示的に指示。

「まずフォームを箱単位で確認 → 結果をリスト化 → 次にスケッチを見る → フォームの理解と照らし合わせる」。

人間が同じ事故を判定する時の思考順を、そのままClaudeに渡す。

ハルシネーション抑制策も重ねる：「fact主張は必ず box X が checked、と根拠を示せ」「不明なら不明と答えろ」。

(8/n)
V5の仕上げ3点。

①Output formatting: 結論を `<final_verdict>` タグでwrap。DBに直接突っ込めるJSONや構造化フォーマットを指定。

②Pre-fill: Claudeの返答冒頭を「[」や「<final_verdict>」から始めさせる。前置き不要。

③Extended thinking (Claude 3.7/4): scratchpadの思考過程を読んで、足りないコンテキストを system prompt に追加する。

(9/n)
24分の講義から得る3つの結論。

①Claudeに会話風で投げると性能の一部しか出ない。Task→Tone→Background→Instructions→Examples→Reminder→Format の順で積む。
②不変情報はsystem promptへ、動的情報はuser promptへ分離。
③Examples＋Extended thinkingでフィードバックループを回す。

公式ワークショップ動画はこちら↓
https://t.co/X6kSg8Obil
