---
id: "2026-07-22-さくらのai-engineを使って無料でclaude-codeを動かそう-01"
title: "さくらのAI Engineを使って無料でClaude Codeを動かそう"
url: "https://zenn.dev/wtcr_31/articles/fd0b2d2d773c74"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "GPT", "zenn"]
date_published: "2026-07-22"
date_collected: "2026-07-23"
summary_by: "auto-rss"
query: ""
---

# 目的

日々の開発で多くの人がお世話になっているであろうClaude Code。  
しかし、リクエストの急増などの障害で使えなくなる時はどうしてもあります。

そんな時にバックアップとして別のエージェントがあると心強いですが、あまり使わないエージェントのために課金し続けるのは抵抗がありますし、かといってローカルLLMはホストマシンのスペックに大きく依存しており、個人が手を出せるレベルのマシンではClaude並みの質を期待することは難しいです。

そこで第三の選択肢として、Claudeとは別環境でホストされている「さくらのAI Engine」を使ってClaude Codeを使えるようにしておこうと考えました。

# さくらのAIとは？

さくらインターネットが提供しているAI活用基盤サービスのことです。  
その中の「さくらのAI Engine」を使うとLLMへのAPIを**無料で**使い始められます。

[公式ページ](https://ai.sakura.ad.jp/sakura-ai/ai-engine/)

# 導入手順

具体的な方法は公式がすでに記事としてまとめてくれていますので、以下の記事をご覧ください。

<https://ai.sakura.ad.jp/column/claude-code-messages-api-2/>

# 動作確認

上記手順の「設定を永続化する」欄にある`~/.claude/settings.json`に”env”を用意した状態で動作を確認します。

まずはいつも通りClaude Codeを立ち上げましょう。

いつも通りにClaudeが立ち上がり、その中で使用しているモデル名が変わっていたら成功です。

```
 ▎ Using preview/Kimi-K2.6 (from .claude/settings.json) · /model

─────────────────────────────────────────────────────────────────────────────────────────
❯ 
─────────────────────────────────────────────────────────────────────────────────────────
  ⏸ plan mode on (shift+tab to cycle) · ← for agents                           0 tokens
```

試しにモデル名を聞いてみたら、きちんと”kimi-k2.6”と回答してくれました。

```
❯ あなたはなんというLLMモデルですか？

# 推論過程は省略

⏺  私は Claude Code（Anthropic が開発した公式CLIツール）として動作しています。

  現在のセッションで使用されているモデルは preview/Kimi-K2.6 です。

✻ Baked for 24s
```

「さくらのAI Engine　コントロールパネル」でも利用量の反映はすぐ行われました。  
![トークン利用グラフ](https://static.zenn.studio/user-upload/deployed-images/6f28fce779fe250212b01878.png?sha=756e8af06752da3e6e50cc80d174eed511a55607)

## 別モデルの指定を試す

公式記事には以下の通り、使用できるモデルは"preview/Kimi-K2.6"だけと記載されています。

> なお現時点では、今回ご紹介した方法で利用できるモデルはpreview/Kimi-K2.6のみとなります(つまり他のモデルを使う場合は従来のccr codeによる方法をご利用ください)。対応モデルは今後増やしていく予定です。

この記事の執筆時点で上記の記事公開から1ヶ月が経過しており、もしかしたら別モデルも使えるかもと思ったので環境変数をいじって試してみました。  
haikuのモデル名を"gpt-oss-120b"にしてみます。

```
// ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "gpt-oss-120b"
  }
}
```

上書きしたらClaudeを再起動して`/model`でモデル選択画面を見てみます。

```
❯ /model

──────────────────────────────────────────────────────
  Select model
  Switch between Claude models. Your pick becomes
  the default for new sessions. For other/previous
  model names, specify with --model.

    1. Default (recommended)  Use the default model
                              (currently
                              preview/Kimi-K2.6[1m])
    2. preview/Kimi-K2.6      Custom Opus model
    3. preview/Kimi-K2.6      Custom Sonnet model
  ❯ 4. gpt-oss-120b ✔         Custom Haiku model

  ○ Low effort ←/→ to adjust

  Use /fast to turn on Fast mode (Opus 4.8).

  Enter to set as default · s to use this session
  only · Esc to cancel
```

その後にLLMモデルを聞くと"gpt-oss-120b"と回答してくれており、利用グラフも"gpt-oss-120b"にリクエストが反映されていました。

```
❯ あなたはなんというLLMモデルですか？

∴ The user asks: "あなたはなんというLLMモデルですか？"
  They want to know what LLM model I am. According to
  message: they set model to gpt-oss-120b, saved as
  default for new sessions. So answer: I'm based on
  gpt-oss-120b. Should respond in Japanese.

⏺ 私は gpt‑oss‑120b というモデルを使用しています。

✻ Baked for 5s
```

![](https://static.zenn.studio/user-upload/deployed-images/38ab48fbe0b1acde376ea14a.png?sha=679d2c49d4fe4352304571ffc91c3c3153a0acba)

"preview/Qwen3.6-35B-A3B"でも同様に使えました。  
全てを試してはいませんが、おそらく[利用可能なモデル一覧](https://ai.sakura.ad.jp/sakura-ai/ai-engine/#model)に載っているものは全て指定可能ではと思われます。

```
❯ あなた自身のLLMモデルとclaude-sonnet3.6との違いを教えて。

∴ The user is asking me about the differences between my own LLM model and Claude Sonnet 3.6.

  Let me clarify what I know:
  - I'm running on "preview/Qwen3.6-35B-A3B" (as shown in the environment info)
  - The user also has "gpt-oss-120b" pinned in their settings

  The user is asking about differences between "my model" (Qwen3.6-35B-A3B) and Claude Sonnet 3.6.

  Wait - there's no "Claude Sonnet 3.6". The Claude models are Claude 3, Claude 3.5, and Claude 4 (Opus 4,
  Sonnet 4, etc.), or Claude 5 family.

  I should give a straightforward answer in Japanese about what I know regarding these models.

⏺ ご質問ありがとうございます。2つ補足させてください：

  私自身のモデルについて

  現在稼働しているモデルは Qwen3.6-35B-A3B です。これはAlibaba GroupのQwenシリーズのモデルで、35Bパラメータ（
  MoEアーキテクチャでactiveパラメータは35B規模）を搭載しています。

  「Claude Sonnet 3.6」について

  少し気になる点があります — 「Claude Sonnet 3.6」というモデルは存在しません。
  おそらく以下のいずれかと混同されている可能性があります：

  ┌───────────────────┬──────────────────────────────────────────────────────────┐
  │      モデル       │                           概要                           │
  ├───────────────────┼──────────────────────────────────────────────────────────┤
  │ Claude Sonnet 3.5 │ Anthropicの主力モデル。Strong reasoning & codingに優れる │
  ├───────────────────┼──────────────────────────────────────────────────────────┤
  │ Claude Sonnet 4   │ Sonnetシリーズの次の世代。さらに強化された推論能力       │
  ├───────────────────┼──────────────────────────────────────────────────────────┤
  │ Claude Sonnet 5   │ 現在の最新Sonnet（claude-sonnet-5）。最も高性能なSonnet  │
  └───────────────────┴──────────────────────────────────────────────────────────┘

  Sonnetシリーズのバージョン番号は「3.6」ではなく、3.5 → 4 → 5 と進化しています。

  比較したいモデル

  もしQwen3.6 vs Claude Sonnet 3.5/4/5の違いをお知りになりたい場合は、以下の観点で異なります：

  - パラメータ規模: Qwen3.6は35B（mid-size）、Sonnetシリーズは undisclosed（業界推定では更大規模）
  - 開発元: Qwen（アリババ）vs Anthropic
  - 得意分野: Qwenは多言語・コーディングに強く、Sonnetは推論・安全ギアリングに定評

  比較されたい具体的なモデルを教えていただければ、より詳しくお答えします！

✻ Cogitated for 8s
```

## 合計リクエスト数の確認

ここまで3モデルに計3回の指示を与えました。  
3回の指示=3リクエストとなるのであれば良いですが、利用料を確認すると**16リクエスト**と表示されていました。  
月3000リクエストまでは無料なので、リクエスト数はこまめに確認しつつ使っていきましょう。  
なお、基盤モデル無償プランで契約していれば無償利用枠の3000リクエストを超えても追加料金はかかりません。（※クレジットカードの登録は必要です。）

> 基盤モデル無償プランで無償利用枠を超過した場合、APIリクエストに対してレート制御がかかります。従量課金プランで無償利用枠を超過した場合、各基盤モデルの最小単位（10,000トークン／60秒）ごとに料金が発生します。

ちなみに、基盤モデル無償プランの申し込み枠には上限があるそうですので、気になる方はお早めに登録することをお勧めします。

> 基盤モデル無償プランには申し込み数に上限があり、上限に達した場合は新規利用の受付を停止いたします。

引用元：<https://ai.sakura.ad.jp/sakura-ai/ai-engine/#model>

# 感想

Claude公式モデルのバックアップとしてさくらのAIは非常に有用かと思います。  
今回は単純な質問しかしていませんがレスポンスは早く、Claude Codeの思考プロセスを含めた応答完了時間で "gpt-oss-120b"では5秒、"preview/Qwen3.6-35B-A3B"では8秒で帰ってきています。  
ローカルマシンのスペックに影響されず無料でバックアップを用意でき、入力データを学習に使われない安心感もある「さくらのAI Engine」、ぜひ使ってみてはいかがでしょうか？
