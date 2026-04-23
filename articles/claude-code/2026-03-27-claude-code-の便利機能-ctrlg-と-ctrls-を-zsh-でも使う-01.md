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

## 何気に便利ですよね、Ctrl+G と Ctrl+S

Claude Code で Ctrl+G を打つと、エディタが起動して、プロンプトをエディタで編集できます。  
また、 Ctrl+S を打つと、現在のプロンプトを一時保存してクリアします。何か別のプロンプトを送信すると、次にプロンプトを打つタイミングで一時保存したプロンプトが復元されます。

使っている人は共感してくれると思うのですが、普通に便利すぎて zsh でも使いたくなりますよね。

## zsh でもできます

どちらも zsh に機能として用意されています。  
以下のように `.zshrc` を設定すると使えます。

### edit-command-line

以下のようにすると、 Ctrl+G でエディタが起動して、コマンドラインをエディタで編集できます。

edit-command-line

```
autoload -Uz edit-command-line
zle -N edit-command-line
bindkey '^G' edit-command-line
```

ここでは Claude Code に合わせて Ctrl+G キー (`^G`) を割り当てていますが、慣習的には Ctrl+X Ctrl+E キー (`^X^E`) を割り当てることが多いようです。お好きな方をどうぞ。

### push-line

コマンドラインを一時保存してクリアする機能は、通常は、 Esc q キー (`\eq`) が割り当てられています。  
Esc キーを押して、離してから、 q キーを押すことで利用できます。

Ctrl+S キーに割り当てる場合、元々 Ctrl+S / Ctrl+Q に割り当てられている、ターミナルの出力を一時停止 / 再開する機能を無効化してから割り当てます。  
(通常、これらはあんまり使わないはずなので、困らないかと思います)

push-line

```
stty -ixon
bindkey "^s" push-line
```

以上です！
