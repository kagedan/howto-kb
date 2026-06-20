---
id: "2026-06-19-avantenvimでneovim上にclaudeのaiペアプロ環境を作る-01"
title: "avante.nvimでNeovim上にClaudeのAIペアプロ環境を作る"
url: "https://zenn.dev/kuroikotech/articles/nvim-avante-claude"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "OpenAI", "Gemini", "zenn"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

## はじめに

エディタ上でAIに質問したりコードを直してもらったりするのに、わざわざ別ウィンドウやブラウザを開きたくない。Neovimから出ずに完結させたくて入れたのが **avante.nvim**。Cursorのインライン編集・チャットUIをNeovimに持ち込むプラグインで、プロバイダにClaudeを指定して使っている。

---

## avante.nvimとは

* チャット形式でコードについて質問できる
* 提案された変更は**diff形式**で表示され、適用するかどうかを選べる
* プロジェクト内のファイルを参照させて、コードベース全体を踏まえた回答をさせられる
* プロバイダはClaude / OpenAI / Gemini など複数から選択可能

---

## 設定

lua/plugins/coding.lua（抜粋）

```
{
  "yetone/avante.nvim",
  event = "VeryLazy",
  version = false,
  build = "make",
  dependencies = {
    "nvim-treesitter/nvim-treesitter",
    "stevearc/dressing.nvim",
    "nvim-lua/plenary.nvim",
    "MunifTanjim/nui.nvim",
    "nvim-tree/nvim-web-devicons",
    "MeanderingProgrammer/render-markdown.nvim",
    {
      "HakonHarnes/img-clip.nvim",
      event = "VeryLazy",
      opts = {
        default = {
          embed_image_as_base64 = false,
          prompt_for_file_name = false,
          drag_and_drop = { insert_mode = true },
        },
      },
    },
  },
  opts = {
    provider = "claude",
  },
},
```

設定自体はシンプルで、`opts.provider = "claude"`を指定するだけ。あとはAPIキーを環境変数`ANTHROPIC_API_KEY`に入れておけば動く。

依存プラグインの役割は以下の通り：

| プラグイン | 役割 |
| --- | --- |
| `render-markdown.nvim` | チャット欄のMarkdown（コードブロック等）を整形表示 |
| `img-clip.nvim` | クリップボードの画像をプロンプトに貼り付け |
| `dressing.nvim` | 入力・選択UIをいい感じに差し替え |
| `nui.nvim` | チャットウィンドウ等のUIコンポーネント |

---

## 使い方

主なコマンド（avante.nvimのデフォルトキーマップ）:

* `<leader>aa` : チャットを開く / Ask
* `<leader>ae` : 選択範囲をEdit指示
* `<leader>ar` : チャット欄をリフレッシュ
* `<leader>at` : サイドバーのトグル

提案された変更はバッファ上にdiffとして表示され、`co`（accept）/ `cr`（reject）等で1つずつ判断できる。コードベース全体を踏まえた質問をしたいときは、ファイルをコンテキストに追加してから聞くと精度が上がる。

---

## まとめ

* `provider = "claude"`の1行で、Neovim上にClaude連携のAIペアプロ環境が手に入る
* 提案はdiffベースで適用判断できるので、まる投げにならず手綱を握ったまま使える
* ビルドに`cargo`が要る点と、`ANTHROPIC_API_KEY`の設定だけ忘れずに
