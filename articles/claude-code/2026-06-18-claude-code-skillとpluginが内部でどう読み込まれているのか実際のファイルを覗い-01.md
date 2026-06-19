---
id: "2026-06-18-claude-code-skillとpluginが内部でどう読み込まれているのか実際のファイルを覗い-01"
title: "[Claude Code] SkillとPluginが内部でどう読み込まれているのか、実際のファイルを覗いてみた"
url: "https://zenn.dev/ncdc/articles/d39bf5c31e0fe8"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "LLM", "zenn"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## 最初に

Claude Codeを使っていると、SkillやPluginという言葉が頻繁に出てきます。

`/plugin install` でインストールすると何もしなくても動くし、`~/.claude/skills/` にファイルを置くだけで認識される。  
便利なんですが、「これ実際どういう仕組みになってるんだろう？」と気になって、実際のキャッシュディレクトリやPlugin配布リポジトリのファイル構造を直接確認しながら調べてみました。

では始めます。

---

## まず「Skill」って何なのか

公式ドキュメント（[Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)）には「Skills are folders of instructions, scripts, and resources that Claude loads dynamically」とあり、一言で言うと**Claudeへの指示書をファイルとして切り出したもの**です。

実体は `SKILL.md` というMarkdownファイルで、上部にYAMLフロントマター、その下に指示の本文が入ります。

```
~/.claude/skills/
└── commit-message/
    └── SKILL.md
```

```
---
name: commit-message
description: コミットメッセージを生成する。git addの後に使う。
---

## Instructions

変更内容を分析してConventional Commits形式のコミットメッセージを生成してください。
...
```

何も知らなかった頃の私は、「え、コードじゃないの？」と思ったんですが、そうではなく本当にただのMarkdownです。Skillを動かすのはあくまでClaude自身で、Skill側は「こうやって動いてください」という指示を書いておくだけ。スクリプトファイルを添付して実行させることもできますが、基本はテキストの指示書です。

ちなみにAnthropicのエンジニアによる解説記事（[Skills for Claude Code: The Ultimate Guide from an Anthropic Engineer](https://medium.com/@tort_mario/skills-for-claude-code-the-ultimate-guide-from-an-anthropic-engineer-bcd66faaa2d6)）には「A common misconception is that skills are 'just Markdown files.' In reality, the most powerful part is that they're folders」とあり、SKILL.md だけでなくフォルダ全体がコンテキストとして機能するようです。

---

## Skillの置き場所は2種類ある

Skillを置けるパスは大きく2つに分かれています。

| スコープ | パス | 用途 |
| --- | --- | --- |
| User（個人） | `~/.claude/skills/<name>/SKILL.md` | 全プロジェクトで使いたいもの |
| Project（プロジェクト） | `.claude/skills/<name>/SKILL.md` | そのリポジトリ専用・チームで共有したいもの |

同名のSkillが複数のスコープに存在する場合は Project > User > Enterprise の優先順位で上位が勝つようです。チーム固有の規約SkillをProjectスコープに置いておけば、個人設定を上書きすることなく共存できる設計になっています。

---

## セッション起動時に何が起きているか

「インストールしたらいきなり動く」のが不思議だったので、実際のセッションの挙動を追ってみました。

どうやらClaude Codeはセッション起動時に、読み込みパス上の `SKILL.md` を全部スキャンしているようです。ただし**最初に読み込むのはフロントマターの `name` と `description` だけ**で、本文は読みません。

収集した情報は `Skill` というメタツールの定義の中に `<available_skills>` ブロックとして埋め込まれます。こういう形になっているようです。

```
<available_skills>
  <skill>
    <name>commit-message</name>
    <description>コミットメッセージを生成する。git addの後に使う。</description>
    <location>user</location>
  </skill>
  ...
</available_skills>
```

そしてClaude自身がこのリストを見て「今のタスクにはこのSkillが関係しそう」と判断し、必要なタイミングで `SKILL.md` の本文を読み込む（コンテキストに注入する）という流れになっています。

```
セッション起動
  └─ 全Skillの name + description だけ収集 → <available_skills>に列挙

会話中（毎ターン）
  └─ Claudeがタスクに関連するSkillを判断
        ↓ Skillツール呼び出し
        ↓ SKILL.md 本文をコンテキストに注入（ここで初めて本文を読む）
        ↓ その指示に従って動作
```

全部のSkillの本文を最初から読まないのは、コンテキストウィンドウの節約のためだと思われます。この「最初は名前と説明だけ、必要になったら本文を読む」という段階的な読み込みはなかなか賢い設計だと感じました。

あと気になったのが「どのSkillを使うかはどうやって決めているのか」という点。

調べてみると、正規表現やキーワードマッチングのようなコードレベルのルーティングは行われておらず、**Claudeのモデル自身が description を読んで推論で判断している**ようです。  
なので description の書き方がそのまま発火しやすさに直結します。

前述のAnthropicエンジニアの記事でも description の重要性が強調されていました。

---

## Pluginは「Skillのまとめパッケージ」

手動でSkillを置く以外に、Plugin経由でインストールする方法があります。

Pluginの本質は、**Skill・Hook・Agent・MCP設定などをひとつのディレクトリにまとめて配布できるフォーマット**です。公式の [Create plugins ドキュメント](https://code.claude.com/docs/en/plugins) にも「Plugins let you extend Claude Code with custom functionality that can be shared across projects and teams」とあります。

Pluginかどうかの判定はシンプルで、**`.claude-plugin/plugin.json` が存在するかどうか**だけで決まるようです。

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json   ← これがある = Plugin
├── skills/
│   ├── feature-a/
│   │   └── SKILL.md
│   └── feature-b/
│       └── SKILL.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
└── agents/
```

実際に `plugin.json` の中身を確認してみたんですが、思ったよりかなりシンプルでした。

```
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "...",
  "author": { "name": "...", "email": "..." },
  "license": "MIT"
}
```

「どのディレクトリを読み込む」という設定は一切書かれていません。では何をもってSkillやHookを認識しているかというと、**ディレクトリ名の規約**です。  
`.claude-plugin/plugin.json` を見つけたら、そのディレクトリ配下の `skills/` `hooks/` `agents/` `commands/` といった名前のディレクトリを自動でスキャンする仕組みになっているようです。  
これは [公式GitHubリポジトリのREADME](https://github.com/anthropics/claude-plugins-official) にも記載されている構造と一致しています。

| ディレクトリ名 | 認識されるもの |
| --- | --- |
| `skills/` | Skills |
| `hooks/` | Hooks |
| `agents/` | Agents |
| `commands/` | Commands |
| `.mcp.json` | MCP設定 |

設定を書かなくても置く場所で決まる、といったいわゆる設定より規約の意味合いの方が強い設計だなと感じます。

---

## Marketplaceからのインストールとキャッシュの仕組み

`/plugin install` でインストールしたPluginは `~/.claude/skills/` には現れません。  
この事象に初めて気がついた時、「あれ、plugin経由でskillインストールしたよな。。どこに入ったんだろう」と思ったんですが、専用のキャッシュディレクトリに展開されているようです。

Marketplaceの実体は `marketplace.json` を持つGitリポジトリで、各Pluginのソース情報がこんな形で記録されています。

```
{
  "name": "my-plugin",
  "description": "...",
  "category": "development",
  "source": {
    "source": "url",
    "url": "https://github.com/example/my-plugin.git",
    "sha": "a1b2c3d4..."
  }
}
```

`source.sha` で特定のコミットが固定されているのがポイントで、再インストール時も必ず同じバージョンを取得できるようになっています。

インストールされると以下のようなパスに展開されます。

```
plugins/cache/<marketplace-name>/<plugin-name>/<version>/
  ├── .claude-plugin/
  │   └── plugin.json
  ├── skills/
  ├── hooks/
  └── ...
```

バージョンごとにディレクトリが分かれているので、アップデートしても古いバージョンと共存できますし、アンインストールもキャッシュディレクトリを消すだけでクリーンに終わります。  
Claude Codeはこのキャッシュパスをそのままマウントして読み込む形になっているようで、だから `~/.claude/skills/` には何も出てこないわけです。

---

## 「インストールしたら自動で動く」の正体はHook

Plugin経由でインストールすると何もしなくても動き始めるのはどうやら、**Hookの存在**によるものでした。

`hooks/hooks.json` にどのタイミングでどのコマンドを走らせるかが書いてあります。実際のファイルを確認するとこういう形でした。

```
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

`matcher` の `startup|clear|compact` が3つのタイミングに対応しています。

| トリガー | タイミング |
| --- | --- |
| `startup` | セッション初回起動 |
| `clear` | `/clear` で会話リセット |
| `compact` | `/compact` でコンテキスト圧縮 |

`startup` だけでなく `clear` と `compact` でも再発火するのが細かい工夫だと思いました。  
どちらもコンテキストがリセットされるタイミングなので、ここでフックが走らないと「さっきまで動いていたのに急に動かなくなった」という状況が起きてしまいます。

ちなみに、`async: false` は「このフックが完了するまでClaude側の処理を止める」という設定です。  
初期コンテキストの注入が終わる前にClaudeが動き始めないようにするためのものと思われます。

`${CLAUDE_PLUGIN_ROOT}` はClaude Codeがキャッシュパスを解決してくれる環境変数で、どの環境にインストールされてもパスがズレずに済む設計になっています。

---

## 全体の流れをまとめると

```
Marketplace登録
  └─ marketplace.json（GitリポジトリURL + SHA）を参照

/plugin install 実行
  └─ 指定SHAでGitリポジトリをfetch
        ↓
  plugins/cache/<marketplace>/<name>/<version>/ に展開
        ↓
  .claude-plugin/plugin.json の存在を確認（Plugin判定）
        ↓
  skills/ hooks/ agents/ を規約ベースで自動検知・認識

セッション起動
  └─ hooks.json の SessionStart フックが発火
        ↓ スクリプト実行（async: false で完了まで待機）
        ↓ 初期コンテキストを注入
  └─ 全Skillの name + description を収集
        ↓ <available_skills> としてSkillツールに埋め込む

会話中
  └─ ClaudeがLLM推論でSkillを選択
        ↓ Skillツール呼び出し
        ↓ SKILL.md 本文をオンデマンドでコンテキストに注入
        ↓ Claudeがその指示に従って動作
```

---

## 手動インストールとPlugin経由はどう違うか

最終的にどちらも「SKILL.md がスキャン対象のパスに存在する」状態になるので、Claudeから見た動作に違いはないようです。違いは管理の仕方の部分であると思われます。

|  | 手動インストール | Plugin経由 |
| --- | --- | --- |
| 配置先 | `~/.claude/skills/<name>/` | `plugins/cache/.../skills/<name>/` |
| バージョン管理 | 自前 | キャッシュディレクトリ構造で管理 |
| Hook | 別途手動設定が必要 | `hooks/hooks.json` で自動設定 |
| アンインストール | ディレクトリ削除 | `/plugin uninstall` でキャッシュごと削除 |

Pluginが便利なのは、Skill・Hook・Agentをまとめて配布できる点と、SHAでバージョンが固定されているため、どの環境においても再現性が高い点だと思います。逆に自分用のちょっとしたSkillを作るだけなら、手動で `~/.claude/skills/` に置くだけで十分だなと感じます。

---

## まとめ

調べてみて感じたのは、想像よりかは割とシンプルな仕組みだったということです。

* `SKILL.md` を決まったパスに置けばSkillとして認識される
* `.claude-plugin/plugin.json` があればPluginとして認識され、配下のディレクトリを規約ベースで自動認識する
* `hooks/hooks.json` の SessionStart フックがセッション起動時に自動でコンテキストを注入する

複雑なルーティングロジックがあるわけではなく、ファイル配置の規約とClaude自身の推論に委ねる設計になっているようでした。  
この仕組みを理解しておくと、「なぜ動かないのか」、「なぜskillが読み込まれていないか」が把握しやすくなりますし、Skill.mdの description の重要性も実感できると思います。

今回の記事がお役にたてたら幸いです。

---

## 参考
