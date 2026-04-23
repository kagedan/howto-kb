---
id: "2026-04-17-ea開発を強固にすべくclaude-codeとcodexを合体させた-01"
title: "EA開発を強固にすべくClaude Codeとcodexを合体させた"
url: "https://note.com/mujofx/n/n0f1f629faee4"
source: "note"
category: "claude-code"
tags: ["claude-code", "OpenAI", "GPT", "note"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

自分で書いたコードを、同じAIにレビューさせていませんか。  
  
それは、自分で自分の答案を採点するようなものです。  
  
OpenAIが先日、Claude Code向けの公式プラグインをリリースしました。Claude（Anthropic）で書いて、Codex（OpenAI）でレビューする。アーキテクチャの異なるモデルを掛け合わせることで、単独では見落とすミスが浮かび上がってくる。ChatGPTサブスクがあれば、追加費用はかかりません。  
  
競合他社の製品向けに公式プラグインを出す。この動き自体が、AIツールが「囲い込み」から「相互運用」の時代に入ったことを示していると思います。  
  
諸行無常——ツールも固執せず、使えるものを使う。  
  
---  
  
■ なぜ組み合わせるのか  
  
同じモデルは、同じ内部仮定を共有しています。Claudeが「これでいい」と判断したコードをClaudeにレビューさせると、同じ理由で「これでいい」と返ってくる可能性がある。  
  
GPT系のCodexに見せると、その内部仮定が違うため、Claudeが気にしなかった部分に引っかかることがあります。これがクロスプロバイダーレビューの核心です。  
  
---  
  
■ 前提条件  
  
・Claude Code（動作確認済み）  
・ChatGPT サブスク（Free〜Pro いずれも可）  
・Node.js v18.18 以上  
  
Node.jsのバージョンは「node --version」で確認できます。  
  
---  
  
■ セットアップ（4ステップ）  
  
① Codex CLIをインストール  
  
npm install -g @openai/codex  
  
② ChatGPTアカウントでログイン  
  
codex login  
  
ブラウザが開きます。APIキーではなく、ChatGPTアカウントでのログインを選んでください。  
  
③ Claude Codeにプラグインを追加  
  
claude mcp add github.com/openai/codex-p…  
  
④ 動作確認  
  
Claude Code内で実行します。  
  
/codex:setup  
  
「Codex is ready」と表示されれば完了です。  
  
---  
  
■ 使うコマンドは3つだけ  
  
/codex:review  
基本のレビューです。これだけ覚えれば十分です。Claudeが書いたコードをCodexが第三者として確認してくれます。  
  
/codex:adversarial-review  
セキュリティ・競合状態・データ損失など、リスク領域を重点的にチェックしてもらいたいときに使います。  
  
/codex:rescue  
Claudeで詰まったタスクをCodexに引き継ぐコマンドです。異なるモデルが、まったく別のアプローチで解いてくることがあります。  
  
---  
  
■ 基本の流れ  
  
Claude で実装 → /codex:review → Claude で修正  
  
これを回すだけです。シングルモデルでは気づけなかった問題が、ループの中で浮かんでくるようになります。  
  
---  
  
■ ひとつ注意点  
  
/codex:setup --enable-review-gate というコマンドを使うと、Claudeが応答を返すたびに自動でCodexレビューを挟む設定ができます。ただし、Claude↔Codexのループが長くなり、両方の使用制限を消費しやすくなります。積極的に監視できるセッションでのみ使うことをおすすめします。  
  
---  
  
ツールは変わります。今日の最強が明日の標準になる。それでも、使えるものを組み合わせて、手を動かし続けることに変わりはない。  
  
いろいろ面倒だという方は、以上の内容をコピペしてClaude Codeに貼り付ければ簡単に実装できますよ。

毎日のトレードと気づきはXで発信しています。  
  
👉 https://x.com/mujo\_fx  
  
フォローしていただけると励みになります。
