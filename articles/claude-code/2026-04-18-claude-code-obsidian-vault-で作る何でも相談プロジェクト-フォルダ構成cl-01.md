---
id: "2026-04-18-claude-code-obsidian-vault-で作る何でも相談プロジェクト-フォルダ構成cl-01"
title: "Claude Code × Obsidian Vault で作る「何でも相談」プロジェクト ― フォルダ構成・CLAUDE.md・MCP設定まで全公開"
url: "https://qiita.com/htani0817/items/0cb5e8f91fa64fb9ba8c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "qiita"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code を使い始めて少し経つと、多くの人が同じ問題にぶつかります。

* Claude が生成した `.md` がプロジェクトルート直下に散乱する
* 「あの調査メモどこ行った？」が週1で起きる
* Mac と Windows を行き来するたびにパス問題でつまずく

この記事では、私が実際に運用している「何でも相談-pj」という Claude Code 専用プロジェクトの中身を、**フォルダ構成・`CLAUDE.md`・`.claude/settings.json`・`.mcp.json` まで全部公開**します。Obsidian の Vault をプロジェクトに内包することで、Claude Code の成果物を自動で整理し、さらに後から Obsidian のグラフビューで知識を俯瞰できる、という構成です。

対象読者：Claude Code を使い始めた〜中級者。Obsidian は未経験でも OK。

## プロジェクト全体像

まず設計の軸になっている3つの原則を先に書きます。この3つが全ての構成判断を支えています。

1. **成果物は全部 Obsidian Vault に入れる**（プロジェクトルートには散らかさない）
2. **置き場ルールは `CLAUDE.md` に書いて Claude 自身に守らせる**（人間が毎回指示しない）
3. **Mac と Windows を USB/ZIP で行き来できるポータブル設計**（Git 同期は使わない）

フォルダの全体像はこうなっています。

```
何でも相談-pj/
├── README.md                  # 初回セットアップ手順
├── CLAUDE.md                  # プロジェクト指針（Claude Code が自動読込）
├── .mcp.json                  # プロジェクト固有のMCPサーバ設定
├── .claude/
│   ├── settings.json          # model / effortLevel など
│   ├── settings.local.json    # 許可リスト（個人用）
│   └── skills/
│       └── note-article-writing/   # プロジェクト固有のカスタムスキル
└── obsidian-vault/            # Obsidian Vault ルート
    ├── .obsidian/             # Obsidian 設定ごと持ち運び可能
    ├── daily/                 # デイリーノート YYYY-MM-DD.md
    ├── coding/                # コーディング相談・サンプル
    ├── research/              # 技術調査・学習メモ
    ├── docs/                  # ドキュメント下書き・成果物
    ├── references/            # 参考資料・URL・PDF等
    └── archive/               # 終了した相談のアーカイブ
```

`CLAUDE.md` と `README.md` だけプロジェクトルートに残しています。これは Claude Code が起動時にこの2ファイルを自動で読むため、Vault の中に入れてしまうと参照されない、という理由です。

## フォルダ構成とサブフォルダの役割

`obsidian-vault/` をプロジェクトに内包しているのがこの構成の肝です。Claude Code の作業ディレクトリはプロジェクトルート（`何でも相談-pj/`）のままなので、`.claude/` や `.mcp.json` はちゃんと認識される。一方で、ノート・成果物はすべて Vault 配下に入る。

サブフォルダ6つの役割を表にまとめました。

| フォルダ | 用途 | 命名規則 |
| --- | --- | --- |
| `daily/` | デイリーノート・作業ログ | `YYYY-MM-DD.md` |
| `coding/` | コーディング相談・サンプル・レビュー対象 | `<トピック>/...` |
| `research/` | 技術調査・学習メモ | `YYYY-MM-DD-トピック.md` |
| `docs/` | ドキュメント下書き・成果物 | `<ドキュメント名>.md` |
| `references/` | 参考資料・URL集・PDF | `links.md` / `<資料名>.pdf` |
| `archive/` | 終了した相談のアーカイブ | `YYYY-MM/<元のパス>` |

ポイントは `archive/` の運用で、月単位フォルダ（`archive/2026-04/` など）に**元のフォルダ構造ごと**移動します。こうすると Vault ルートが常に最小化されつつ、過去の文脈を辿りたい時に元の階層のまま見つけられる。

## CLAUDE.md に置き場ルールを書く

ここがこの記事で一番伝えたいところです。

`CLAUDE.md` はプロジェクトごとの指示書として機能します。多くの人は「コーディング規約を書く場所」として使っていると思いますが、私は**ファイル配置の自動化装置**として使っています。

たとえば私の `CLAUDE.md` にはこんな表が書いてあります。

```
## フォルダ構成とデフォルト置き場ルール

新規ファイルを作る際は、内容に応じて以下のフォルダに配置してください
（絶対にプロジェクトルートや Vault ルートに散らさない）：

| フォルダ | 用途 | ファイル命名例 |
|----------|------|----------------|
| `obsidian-vault/daily/` | デイリーノート | `obsidian-vault/daily/YYYY-MM-DD.md` |
| `obsidian-vault/coding/` | コーディング相談 | `obsidian-vault/coding/<トピック>/...` |
| `obsidian-vault/research/` | 技術調査・学習メモ | `obsidian-vault/research/YYYY-MM-DD-トピック.md` |
| `obsidian-vault/docs/` | ドキュメント成果物 | `obsidian-vault/docs/<ドキュメント名>.md` |
| `obsidian-vault/references/` | 参考資料・URL集 | `obsidian-vault/references/links.md` |
| `obsidian-vault/archive/` | 終了した相談 | `obsidian-vault/archive/YYYY-MM/<元のパス>` |

会話の冒頭で `obsidian-vault/daily/<今日の日付>.md` が存在する場合、
Claude はそれを一度読んで当日の文脈を把握してから作業に入ってください。
```

この1枚の表を書いておくだけで、挙動が劇的に変わります。

**Before（`CLAUDE.md` なし）**：

> 私「API 設計のメモを書いて」  
> Claude「`api-design.md` を作りました」（プロジェクトルートに生える）

**After（`CLAUDE.md` に置き場ルールあり）**：

> 私「API 設計のメモを書いて」  
> Claude「`obsidian-vault/research/2026-04-18-API設計.md` を作りました」

毎回「Vault の research 配下に作ってね」と言わなくて良い。`CLAUDE.md` の最後の一文「会話の冒頭でデイリーノートを読む」も効いていて、セッション開始時に Claude が勝手に当日のデイリーノートを読み、前後の文脈を把握した上で返答してくれます。

## .claude/settings.json の工夫

プロジェクトの挙動を固めるために `.claude/settings.json` でいくつかのキーを明示しています。

```
{
  "model": "claude-opus-4-7",
  "enabledPlugins": {
    "everything-claude-code@everything-claude-code": true
  },
  "effortLevel": "xhigh",
  "env": {
    "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1"
  }
}
```

それぞれの狙いは次の通り。

* `model`: Opus 4.7 に固定。モデルが勝手に変わらないように。
* `enabledPlugins`: 後述の `everything-claude-code` をプロジェクトで明示的に有効化。
* `effortLevel: "xhigh"`: 推論の深さを最大寄り（`max` の一段下）に固定。コーディングや調査で妥協されないように。
* `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING`: 思考量の自動調整を止める。毎回同じ深さで考えてもらう方が実運用で安定するため。

加えて `.claude/settings.local.json` には**個人の許可リスト**を置いています。

```
{
  "permissions": {
    "allow": [
      "mcp__awslabs_aws-documentation-mcp-server__search_documentation",
      "mcp__awslabs_aws-documentation-mcp-server__read_documentation",
      "WebFetch(domain:qiita.com)",
      "WebFetch(domain:www.anthropic.com)",
      "WebFetch(domain:aws.amazon.com)",
      "WebSearch"
    ]
  }
}
```

`settings.json` は「プロジェクトとして共有したい設定」、`settings.local.json` は「自分の端末だけの許可」と使い分けるのがコツ。このファイルのおかげで、よく使う AWS 公式ドキュメント・Qiita・Anthropic 公式へのフェッチで**権限確認プロンプトが出なくなり**、作業のリズムが崩れません。

## .mcp.json と everything-claude-code プラグイン

MCP サーバはプロジェクト固有の `.mcp.json` で1つだけ有効化しています。

```
{
  "mcpServers": {
    "awslabs.aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_DOCUMENTATION_PARTITION": "aws"
      }
    }
  }
}
```

起動は `uvx` 経由。uv/uvx を先に入れておけば、初回起動時に自動でパッケージをダウンロードしてくれます。なぜ AWS Docs を入れたかというと、Claude に AWS の話を聞くと**古い情報**で答えられがちなので、一次情報を直接引けるようにするためです。

大事なのは「**MCP を増やしすぎない**」こと。everything-claude-code の README にも「すべての MCP を有効にすると 200k のコンテキストが 70k まで縮む可能性」と書いてあります。私は AWS Docs だけをプロジェクトスコープで常時有効、他の MCP（`context7` `exa` `github` `memory` `playwright` `sequential-thinking`）は everything-claude-code プラグイン経由で必要時だけ使う、という運用です。

そのプラグイン側でよく使っているスラッシュコマンドを表にしておきます。

| コマンド | 使いどころ |
| --- | --- |
| `/plan` | 実装計画を立てるとき |
| `/tdd` | TDD でコードを書き始めるとき |
| `/code-review` | 書いたコードの品質レビュー |
| `/security` | セキュリティ観点のレビュー |
| `/build-fix` | ビルドエラーの原因特定・修正 |
| `/refactor-clean` | デッドコード削除・整理 |
| `/verify` | 実装後の検証ループ |
| `/checkpoint` | 検証通過時の状態保存 |

さらに `.claude/skills/note-article-writing/` に**プロジェクト固有のカスタムスキル**を置いています。note.com 向け記事を書くためのチェックリストやテンプレを `SKILL.md` に記述し、Claude が自動トリガーで呼び出してくれる。プロジェクトスコープで独自スキルを配置できるのが `.claude/skills/` の強みで、ワークフローに合わせたミニエージェントを自作できます。

## Mac/Windows 手動コピー移行のルール

このプロジェクトは Git もクラウド同期も使わず、USB/ZIP で手動コピーする前提です。Git を使わない理由は、Obsidian のグラフ・設定ファイル・PDF などバイナリ類まで含めた「丸ごと」を雑に持ち運びたいから。その代わり、**ファイル作成時のルール6つ**を守る必要があります。

| # | ルール | 理由 |
| --- | --- | --- |
| 1 | 絶対パスを書かない | OS をまたぐと即死 |
| 2 | ホームディレクトリ直接参照（`C:\Users\...` や `/Users/...`）を埋め込まない | 同上 |
| 3 | パス区切りは `/` で統一 | Windows でも `/` は動く |
| 4 | BOM 無し UTF-8 で保存 | 文字化け対策 |
| 5 | 改行は LF（CRLF 混在は避ける） | Git を使わないのでエディタ側で揃える |
| 6 | `obsidian-vault/.obsidian/` も一緒にコピー | Obsidian の設定・プラグイン有効化状態を引き継ぐため |

別 PC に移した後は、プラグインだけ再導入します。これは `~/.claude/plugins/` が OS ごとにバイナリダウンロードされるため、フォルダごと持ち運べないからです。

```
/plugin marketplace add https://github.com/affaan-m/everything-claude-code
/plugin install everything-claude-code
```

この2行を叩けば、2回目以降の同じ PC では `~/.claude/settings.json` に記録されるので不要。Obsidian 側は、新 PC で Obsidian を起動して `obsidian-vault/` を Vault として開き直すだけで、デイリーノート設定やプラグイン有効化状態がそのまま引き継がれます。

## まとめ：今日からマネできる最小セット

長くなったので、マネするときに最低限やることを5ステップにまとめておきます。

1. プロジェクトフォルダを作り、ルートに `CLAUDE.md` と `README.md` を置く
2. `obsidian-vault/` を作り、`daily/` `coding/` `research/` `docs/` `references/` `archive/` の6フォルダを切る
3. `CLAUDE.md` に「どこに何を置くか」の表を書く（これだけで Claude の振る舞いが変わる）
4. `.claude/settings.json` で model / effortLevel を固定、`.mcp.json` で必要な MCP だけ有効化
5. Obsidian で `obsidian-vault/` を Vault として開き、Daily notes プラグインを有効化

記事中で紹介したものは全部コピペで動きます。慣れてきたら `.claude/skills/` に自分用のスキルを置いたり、MCP を増減させたりして、自分の作業にフィットさせていくのがおすすめです。

### 参考リンク
