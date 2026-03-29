---
id: "2026-03-27-claude-code-の便利機能-ctrlg-と-ctrls-を-zsh-でも使う-01"
title: "Claude Code の便利機能 Ctrl+G と Ctrl+S を zsh でも使う"
url: "https://zenn.dev/beef_and_rice/articles/482b09980fce23"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

何気に便利ですよね、Ctrl+G と Ctrl+S
Claude Code で Ctrl+G を打つと、エディタが起動して、プロンプトをエディタで編集できます。
また、 Ctrl+S を打つと、現在のプロンプトを一時保存してクリアします。何か別のプロンプトを送信すると、次にプロンプトを打つタイミングで一時保存したプロンプトが復元されます。
使っている人は共感してくれると思うのですが、普通に便利すぎて zsh でも使いたくなりますよね。

 zsh でもできます
どちらも zsh に機能として用意されています。
以下のように .zshrc を設定すると使えます。

 edit-comm...
