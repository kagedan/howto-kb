---
id: "2026-05-08-claude-codecursorcodex-cli3つ全部使って気づいたこと-01"
title: "Claude Code・Cursor・Codex CLI——3つ全部使って気づいたこと"
url: "https://zenn.dev/kenworkflow/articles/dfffcc275ad49f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "OpenAI", "Gemini"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

![](https://res.cloudinary.com/zenn/image/fetch/s--4DGEuWaD--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://hcniahdryda7.feishu.cn/space/api/box/stream/download/asynccode/%3Fcode%3DMThjNzQ4Njg1OTk1NWI0NjIzMmVhZDI0MWZhZDdjYTFfcHhhTkFWTUVPY05GYkg0RnZTcjJMM0tzQWt2TUpVZFpfVG9rZW46THhkRmJxc0Z6b0hhNkd4WXJwZGNZbkI0blRlXzE3NzgyMzI3NDE6MTc3ODIzNjM0MV9WNA)

実はずっと悩んでたんですが、AI編程ツールの選び方についてちゃんと書こうと思います。

2026年に入ってから「Claude CodeとCursorどっちがいい？」と聞かれることが増えました。そこにOpenAIのCodex CLIも加わって、正直に言うと——もう「どれが一番」という問い自体がズレてきています。

3つとも毎日使っています。結論から言うと、それぞれ得意な場面がまったく違う。1本で全部済ませようとすると、どれを選んでも不満が残ります。

## そもそも何が違うのか

3つのツールは、設計思想のレイヤーから違います。

**Claude Code**はターミナルに住んでいるAIエージェント。ファイルの読み書き、シェルコマンドの実行、gitの操作まで全部ターミナルの中で完結します。200Kトークンのコンテキストウィンドウ（[Opus 4.6では100万トークンのベータ](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)も始まっています）で、大きなコードベースを丸ごと読み込んで推論できるのが強みです。[Pragmatic Engineerの調査](https://newsletter.pragmaticengineer.com/)では、開発者の46%が「最も気に入っているAIコーディングツール」として挙げています。

![](https://res.cloudinary.com/zenn/image/fetch/s--AgCsWsvJ--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://hcniahdryda7.feishu.cn/space/api/box/stream/download/asynccode/%3Fcode%3DMTk3ODQxOWFlZDRjMzU4NTA5M2U2ZjU2NGMzMDQyZTRfcHU4TlhEaUFnbEVZQWJnTnFPaTc1VldnRU5EdU9uQzFfVG9rZW46TUQ5dmJ3Y0hDbzBtZzF4Ukt0UGM4QjVMbmFiXzE3NzgyMzI3NDE6MTc3ODIzNjM0MV9WNA)

**Cursor**はVS Codeをフォークして、AIを内側から組み込んだIDE。見た目も操作感もVS Codeそのまま。Tabキーで出てくる補完の応答が100ms以下で、書いているそばからコードが先読みされる感覚は、他の2つにはない体験です。Claude、GPT-5、Geminiなど複数モデルを切り替えられるのも特徴。

**Codex ​CLI**はOpenAIのターミナルエージェント。Claude Codeと似た位置づけですが、ChatGPTのサブスクリプションに含まれていて、クラウドのサンドボックスで非同期に動きます。タスクを投げて放っておくと、終わったらPRが上がってくる。自分が手を離している間に仕事が進む、というのが設計上の狙いです。

![](https://res.cloudinary.com/zenn/image/fetch/s--CSlCmS0q--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://hcniahdryda7.feishu.cn/space/api/box/stream/download/asynccode/%3Fcode%3DMTQxNGM0N2M2Y2NiNDgwODI1Mjk5ZTI5M2M2MzUyZTlfd3B3R2UwdWtFQWJ1NzNBekNxUFBxNVJlU3hIT3JSOVFfVG9rZW46TU5BTGJPTno2b0g4R1Z4Q3lIZGNHM3FXbnVmXzE3NzgyMzI3NDE6MTc3ODIzNjM0MV9WNA)

## 場面ごとに使い分けてみた結果

ここからが本題で——実際にどう使い分けているか書きます。

### 複数ファイルにまたがるリファクタリング

Claude Codeの独壇場です。十数ファイル、複数モジュールにまたがる変更を一発で通せるのはこれだけでした。SWE-bench Verifiedでの解決率が公開オープンソースモデルの中で最高水準というベンチマークもありますが、体感としても、一回の指示で「テストまで含めて動くコード」が返ってくる確率が明らかに高いです。

Cursorでも小規模なリファクタリングはできます。でも、10ファイル以上になると漏れが出やすい。手動で確認する箇所が増えて、結局時間がかかります。

### 日常のコーディング——機能追加、CRUD、UI実装

ここはCursorが圧倒的です。Tabで出てくる補完の精度と速度、Cmd+Kで自然言語からコード変更を指示できる体験、ファイルの差分をその場で視覚的に確認できること。「書きながら考える」タイプの作業では、IDEと一体化しているCursorの快適さに代わるものがありません。

### バックグラウンドで回す自動化タスク

Codex CLIの出番です。テスト生成、ドキュメント作成、定型的な機能実装など、「仕様が明確で、自分が見ていなくても進む」タイプのタスクに向いています。複数のタスクを同時に投げられるのも強みで、フロントエンド・テスト・ドキュメントを別々のエージェントに並行処理させるような使い方ができます。

### 大きなコードベースの全体把握

Claude Codeです。100万トークンのコンテキストが使えるようになってからは、レポジトリ全体を読み込んでアーキテクチャの把握や影響範囲の分析ができるようになりました。CursorのRAGもプロジェクト全体をインデックスしてくれますが、実効的なコンテキスト長ではClaude Codeの方が余裕があります。

## コストの話——見た目の価格と実際の出費は違う

よかった点と気になった点、両方書きます。

**Cursor**はPro $20/月から。無料枠もあるので始めやすいですが、クレジット制になっていて、使うモデルや操作量で消費速度が大きく変わります。Opusを多用すると想定以上に減りが早い。

**Claude Code**はAPI従量課金。1回のタスクで消費するトークンは多め（[独立テストで同一タスクをCursorの5.5分の1のトークンで完了](https://www.builder.io/blog/cursor-vs-claude-code)したデータもありますが、タスクの性質に依存します）。首次通過率が高いので、「何度もやり直す」コストが減る分、複雑なタスクでは結果的に安くなることもあります。

**Codex ​CLI**はChatGPT Plus（$20/月）に含まれていて、トークン効率が最も高い。コスト重視なら一番手軽です。ただし、複雑な推論タスクでは一発で通らないことが多く、やり取りの回数で間接コストが増えることがあります。

## 「1本に絞る」より「組み合わせる」時代

でも、ここからが本題で——2026年の時点では、3つは競合というより補完関係になってきています。

[The New Stackの報道](https://thenewstack.io/ai-coding-tool-stack/)で指摘されている通り、Cursorは複数モデルを横断してエージェントを統合するオーケストレーション層、Claude CodeとCodex CLIはコードを実際に書いて実行するエージェント層として、ツール同士が「レイヤーとして重なる」構造が見えてきています。実際、OpenAIはClaude Codeの中からCodex CLIを呼び出せる公式プラグインまでリリースしています。

![](https://res.cloudinary.com/zenn/image/fetch/s--h_OeFvnV--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://hcniahdryda7.feishu.cn/space/api/box/stream/download/asynccode/%3Fcode%3DNTRmYWY2NGQ5YzFhNDg2ZmJhNDBkODM5MGM4YzE5ODRfcHo0b1JJR0Zab1RTUHVISXp4ZWJrR0Z3dFBHMkhVT3ZfVG9rZW46SkFCWmIzWmVIbzREQ0R4MkQ3T2NneFltbnFlXzE3NzgyMzI3NDE6MTc3ODIzNjM0MV9WNA)

個人的には、こう使い分けています。

朝の機能実装 → **Cursor**で書きながら考える。Tabの補完とComposerの複数ファイル編集を使って手を動かす。

午後のリファクタリング → **Claude Code**に投げる。CLAUDE.mdにプロジェクトのルールを書いておけば、セッションをまたいでも方針がブレない。

並行タスク・CI連携 → **Codex ​CLI**にバックグラウンドで回させる。テスト生成やドキュメント更新など、自分が見ていなくていい仕事。

## どれから始めるか

向き不向きがあるので、全員に同じものは勧めません。

**VS Codeで毎日コードを書いている人** → まずCursor。学習コストがほぼゼロで、今日から使える。

**ターミナル派で、複雑なタスクを丸投げしたい人** → Claude Code。学習曲線はあるけど、慣れたときの生産性の跳ね方が大きい。

**コスト重視で、定型タスクを自動化したい人** → Codex CLI。ChatGPT Plusに含まれているので追加費用なしで始められる。

**余裕があれば** → Cursor + Claude Codeの組み合わせが、今のところ一番カバー範囲が広いです。日常のコーディングはCursor、重い仕事はClaude Code。この2つで大半の場面は回ります。

長くなりましたが、要点だけ言うと。「どれが一番か」ではなく「何をやるときにどれを開くか」で選ぶ——これが今のAIコーディングツールとの付き合い方だと思っています。

ちなみに、複数ツールを行き来していると「このスキルやルール、ツールをまたいで使い回せないのか」という壁にぶつかります。CLAUDE.mdに書いたプロジェクトルールはClaude Codeでしか効かないし、Cursorの設定はCursorの中で閉じている。

この「ツール間でエージェントの知見が共有されない」問題、個人的にけっこう気になっていて、最近[EvoMap](https://evomap.ai/)を触り始めました。AIエージェントのスキルや判断ルールを「Gene」という単位で構造化して、ツールやモデルをまたいで再利用できるようにするプロトコルです。Skill Storeでコミュニティが公開しているスキルも覗けるので、エージェント活用を本格的に広げたい人は一度見てみてください。

#AIコーディング #ClaudeCode #Cursor #AIエージェント #開発者ツール
