---
id: "2026-04-19-cmux-上で-vim-から-claude-code-にファイル参照を渡すプラグイン-cmuxvim-01"
title: "cmux 上で Vim から Claude Code にファイル参照を渡すプラグイン cmux.vim を作った"
url: "https://zenn.dev/tanabee/articles/e9652e4dd2a11b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "antigravity", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

## 背景

最近は [Antigravity](https://antigravity.google/)（IDE）と [cmux](https://github.com/manaflow-ai/cmux)（Vim + Claude Code）を使い分けて開発しています。IDE 側では当たり前にできる「エディタからファイル参照を渡す」操作が、cmux 上の Vim からだと手間でした。これがネックで、ファイル参照を渡したい場面では IDE に切り替えていました。

```
> @src/components/UserProfile.tsx:L42-55 この部分のリファクタリングをお願い
```

このように `@filepath` でファイルや行範囲を明示的に指定するのは、AI に無駄なコンテキストを読ませず必要な箇所だけを渡せるという点で重要です。コンテキストサイズを抑えればレスポンスの精度もコストも良くなるので、個人的にこのようなプロンプトを書く頻度は高いです。

そこで Vim 側からショートカットでファイル参照を送れるプラグインを作りました。

## cmux.vim とは

[cmux.vim](https://github.com/tanabee/cmux.vim) は、Vim から Claude Code へファイル参照を `@filepath` 形式で送信するプラグインです。Gemini CLI にも対応しています。

* ファイルパス、行番号、Visual 選択範囲をそれぞれ送信可能
* `cmux tree` / `cmux read-screen` による Claude Code Surface の自動検出
* 送信後の自動フォーカス・自動 Enter 送信に対応

## インストール

cmux が動いている環境であれば、プラグインマネージャで入れるだけです。

```
# 手動の場合
git clone https://github.com/tanabee/cmux.vim.git ~/.vim/pack/plugins/start/cmux.vim
```

## 使い方

cmux でタブを2つ開き、片方で Vim、もう片方で Claude Code を起動します。デフォルトで `<C-\>` のキーで Claude Code にファイル参照 (@filepath) を渡します。

![cmux.vim - ファイル参照](https://static.zenn.studio/user-upload/cd2cf0da8894-20260419.gif)

Vim で範囲選択して `<C-\>` を押すと指定した範囲 (@filepath:L12-34) に限定することができます。

![cmux.vim - ファイルの範囲選択](https://static.zenn.studio/user-upload/1e737a5bd5bf-20260419.gif)

### キーマッピング

デフォルトのキーマッピングは以下の通りです。

| キー | モード | 送信内容 |
| --- | --- | --- |
| `<C-\>` | Normal | `@src/main.ts` |
| `<C-\>` | Visual | `@src/main.ts:L42-55` |

パスは Git リポジトリルートからの相対パスに自動変換されます。Claude Code の Surface は未設定時に自動検出され、以降はセッション中キャッシュされます。再検出したい場合は `:CmuxDetect` を使います。

### コマンド

| コマンド | 説明 |
| --- | --- |
| `:CmuxSendFile` | ファイルパスを送信 |
| `:CmuxSendPos` | ファイルパス＋行番号を送信 |
| `:'<,'>CmuxSendRange` | ファイルパス＋行範囲を送信 |
| `:CmuxDetect` | Claude Code Surface の再検出 |
| `:CmuxSetSurface` | Surface ID を手動設定 |

## 設定

`<C-\>` が競合する場合は `<Plug>` マッピングで変更できます。定義するとデフォルトのバインドは自動で無効化されます。

```
nmap <C-s> <Plug>(cmux-send-file)
nmap <C-g> <Plug>(cmux-send-pos)
vmap <C-s> <Plug>(cmux-send-range)
```

## まとめ

「Vim で見ているファイルを Claude Code に共有する」という、小さいけれど毎日使う機能をプラグインにしました。cmux 上で Vim + Claude Code の開発フローを回している方はぜひ試してみてください。

リポジトリ: [tanabee/cmux.vim](https://github.com/tanabee/cmux.vim)
