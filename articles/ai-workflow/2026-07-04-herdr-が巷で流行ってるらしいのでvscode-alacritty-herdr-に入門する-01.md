---
id: "2026-07-04-herdr-が巷で流行ってるらしいのでvscode-alacritty-herdr-に入門する-01"
title: "Herdr が巷で流行ってるらしいので、VSCode + Alacritty + Herdr に入門する"
url: "https://zenn.dev/arx8/articles/2f29a85828e8ef"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "GPT", "VSCode", "zenn"]
date_published: "2026-07-04"
date_collected: "2026-07-05"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/af7c397c3a2f-20260704.png)  
*by ChatGPT。 VSScode...?*

## TL;DR

* Alacritty, Herdr どちらも Rust 製なので速い。とにかく速い。マジ爆速。VSCode が止まって見えるレベル。
* (少なくとも macOS では) ショートカットキーの設定が癖強だったので、Agent Skills なり書いて LLM にやらせるとよい。
* VSCode 連携には AppleScript 書くとよいっぽい。

## 読者プレゼント

豪華3大特典！なんと全部無料！！

* macOS + Alacritty + herdr で、 CMD + 文字キー等のショートカットキーを割り当てる方法（kitty CSI-u 方式）をまとめたスキル。
* VSCode の `Open New External Terminal` から Alacritty + herdr を起動する AppleScript についてまとめたスキル。
* 上記で書いてもらった AppleScript

Skills の動作確認は Claude のみ。  
この 2 つ読ませた Claude に聞けば VSCode + Alacritty + Herdr の連携とショートカットは何とかなると思う。

おわり🌴

...だと技術記事として侘びしいので Tips とか書く。

## 各ツールの関係性

こんな感じ

```
VSCode
├── Integrated Terminal
│   └── zsh
└── Open New External Terminal
    └── Alacritty
        └── Herdr
            └── zsh
```

雑に Alacritty ≒ iTerm, Herdr ≒ tmux と理解

## Why Alacritty?

* 軽量、高速だから
* tab や split は Herdr に任せるので、terminal の機能は最低限でいい

## Why Herdr?

* tmux と違い、AI Agent の状態表示や完了通知をデフォルトでやってくれるから
* AI Agent 多頭飼い時代のダッシュボード的な

## Tips とか

前提として、環境は macOS。

### `~/.config` を丸ごと git 管理する

* `~/.config` を project root と見なして、 `.claude/` 配置して Skills やら整備すると安全かつ簡単に設定変更できるのでよい。
* log とか credentials ある場合もあるので、適宜 .gitignore を忘れずに。

### herdr config 変更後の再起動

```
herdr server reload-config
```

### herdr/config.toml

以下おすすめ。日本語入力化でも ctrl + b のショートカットをうまく効かせるようにするためのもの。

```
[experimental]
switch_ascii_input_source_in_prefix = true
```

違いを感じるための操作は以下。

1. Herdr を開く
2. macOS の入力ソースを ひらがな にする
3. Herdr で ctrl+b を押す
4. 続けて c を押す
5. default なら prefix+c は新しい tab 作成のはず

このとき、c が Herdr の command として処理されず、IME 側に吸われる/変な入力になる/何も起きないなら、この設定の対象。

* **Alacritty**: `アラクリティ`
  + 英単語 `alacrity` 由来なので、英語発音はだいたい「アラク リティ」寄り。
  + 日本語では `アラクリティ` が自然。
* **Herdr**: `ハーダー`
  + おそらく `herder`、つまり「群れをまとめる人」っぽい命名。
  + `ヘルダー` と読むのはドイツ語っぽく見た場合で、terminal tool 名としてはたぶん外す。
  + 無難に言うなら `ハーダー`。

(by ChatGPT)

## 換装した感想

* 呼吸レベルに染み付いた VSCode しぐさが抜けず、気づいたら VSCode terminal で作業してる。難しい。
* ただ VSCode だけでたくさん terminal 使うのがツラかったのはそうなので、慣れていきたい。

## Appendix

### Official

### References

Special thanks
