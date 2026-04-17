---
id: "2026-04-17-radineere10-anthropicの社員がclaude-codeのセッション管理を体系的に解-01"
title: "@RadineerE10: Anthropicの社員が、Claude Codeのセッション管理を体系的に解説している記事がガチで有益。。。"
url: "https://x.com/RadineerE10/status/2045097440051699834"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "x"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

Anthropicの社員が、Claude Codeのセッション管理を体系的に解説している記事がガチで有益。。。　　　　　　　　　　　　　　　　　　　　　　　　　

1Mコンテキストは諸刃の剣。
長く使えるが、管理しないとコンテキスト汚染で出力品質が落ちる。
この問題の解決策がここに👇

【核心：各ターン完了後の5分岐】
Claudeが作業を終えたとき、「次のメッセージを送る」以外に4つの選択肢がある。
ほとんどの人がこれを知らない。

> 「While the most natural is just to continue, the other four options exist to help manage your context.」

1. Continue — そのまま続ける（自然だがコンテキストが蓄積）
2. Rewind (Esc Esc) — 任意の地点まで巻き戻して再プロンプト
3. Clear — 新セッション開始。自分で重要事項を書き出す
4. Compact — Claudeに要約させて圧縮継続
5. Subagent — 独立コンテキストに委譲し結論だけ受け取る

「なんとなくContinue」の連続がコンテキスト腐敗を引き起こす。 
毎ターンこの5択を意識するだけで出力品質が変わる。

【最も重要な習慣：Rewind】
> 「If I had to pick one habit that signals good context management, it's rewind.」
Claudeが5ファイル読んでアプローチAを試して失敗。「それダメだった、Bを試して」と打ちたくなる。でも最適解は違う。

ファイル読み込み直後まで巻き戻して、学びを含めた再プロンプトを送る。
「アプローチAは使うな、fooモジュールはそのAPIを公開してない。直接Bで行け。」

失敗のコンテキスト（ツール呼び出し、エラー出力）がまるごとドロップされ、ファイル読み込みの結果だけ残る。
修正メッセージより圧倒的にクリーン。

【Compactの正しい使い方】
「compact使うな」という声をよく見るが、この記事は別の視点を示している。
> 悪いcompactが起きるのは、モデルが次の作業方向を予測できないとき。
方向指示を渡せば品質を制御できる：

`/compact focus on the auth refactor, drop the test debugging`
「何を残し、何を捨てるか」を人間が指定する。
Claude任せにしないのがポイント。

さらに、1Mコンテキストでは腐敗が進む前に積極的にcompactする時間的余裕がある。 
追い込まれてからではなく、早めに方向指示付きで実行する。

【サブエージェントの判断基準】
> 「The mental test we use: will I need this tool output again, or just the conclusion?」
中間出力がもう一度必要 → 親セッションで実行
結論だけ必要 → サブエージェントに委譲

典型例
・「サブエージェントで別のコードベースを読んでauth flowを要約して」
・「サブエージェントでgit changesからドキュメントを書いて」

中間出力が親コンテキストに入らないので、汚染を防げる。

【1Mコンテキストの腐敗タイミング】
> 「We see some level of context rot happen around ~300-400k tokens, but it is highly dependent on the task — not a fast rule.」
300-400K（30-40%）で腐敗が始まる。
ただしタスク依存、固定ルールではない。

原則：新タスクには新セッション。 
ただしドキュメント作成など「知能感度が低い関連タスク」は、ファイル再読み込みのコストを避けて同一セッション継続もあり。

Claude Codeの使い方を一段上げたい人は、この5分岐フレームワークを今日から試してみてください。
特にRewindは即効性がある。


--- 引用元 @trq212 ---
https://t.co/Ljzw0lmvao
