---
id: "2026-07-05-claude-code-スキルを-plugin-化してどのプロジェクトからでも読書メモを引く-01"
title: "Claude Code スキルを plugin 化してどのプロジェクトからでも読書メモを引く"
url: "https://qiita.com/narunaru-uhchan/items/3382c979b0239a8f3307"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "LLM", "qiita"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-rss"
query: ""
---

# Claude Code スキルを plugin 化してどのプロジェクトからでも読書メモを引く

## TL;DR

- 読書メモリポジトリ（LLM Wiki パターン）の運用スキル 6 つを `.claude/skills/` から Claude Code **plugin** に移行した
- あわせて新スキル `/wiki-recall` を追加し、**他のどのプロジェクトからでも**自分の読書メモ由来の知識ベースを引けるようにした（キャッシュクローン方式）
- marketplace は中央レジストリではなく「`marketplace.json` を置いた git リポジトリ」そのもの。private リポジトリなら参照権限がそのまま配布権限になる
- 一番ハマったのは **SKILL.md の frontmatter が YAML パースエラーで黙って空になる**問題。`argument-hint: [--fix] [--dry-run]` のようなブラケット表記が原因。`claude plugin validate` で検出できる

## 環境

| 項目        | バージョン                     |
| ----------- | ------------------------------ |
| OS          | Windows 11 Home（Build 26200） |
| Claude Code | 2.1.201                        |
| git         | 2.36.1.windows.1               |

## 前提: notes-wiki リポジトリと LLM Wiki パターン

読書メモを GitHub のprivateリポジトリで管理している。この記事ではリポジトリ名をnotes-wikiと表記する。構成は Karpathy の [LLM Wiki パターン](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) に寄せた二層構造:

- `raws/` — 人間が投入した読書メモ（Kindle ハイライトなど）。LLM は読むだけで書き換えない
- `wiki/` — LLM が raws/ から編纂する百科事典。concept / source / entity / query の 4 種のページを frontmatter 付き Markdown で持つ

この運用は 6 つの Claude Code スキルで回している:

| スキル         | 用途                                                        |
| -------------- | ----------------------------------------------------------- |
| `/add-book`    | Kindle HTML / My Clippings.txt から読書メモを作成し PR 作成 |
| `/add-article` | Web 記事を取得・要約して保存し PR 作成                      |
| `/update-wiki` | raws/ から wiki/ 層を生成・更新                             |
| `/lint-wiki`   | wiki/ 全体の健全性を静的検査                                |
| `/save-query`  | 質問・回答ペアを wiki/queries/ に保存                       |
| `/wiki-recall` | **（今回新設）** wiki を参照して質問に答える                |

もともと前者 5 つは `.claude/skills/`（プロジェクトスコープのスキル）と `.claude/commands/` に置いていた。

## 動機: なぜ plugin 化したか

プロジェクトスコープのスキル（`.claude/skills/`）には**そのリポジトリで Claude Code を開いているときしか使えない**という制約がある。公式ドキュメントもこの使い分けを「standalone（`.claude/` ディレクトリ）は単一プロジェクト向け、plugin は複数プロジェクト・チーム共有向け」と整理している。

> 📖 参考: [プラグインとスタンドアロン設定を使い分ける – プラグインを作成する](https://code.claude.com/docs/ja/plugins#when-to-use-plugins-vs-standalone-configuration)

読書メモの価値は「別の仕事をしているときに引けること」にある。たとえば別プロジェクトで SQL を書いているときに「『SQL実践入門』で実行計画についてどう整理してたっけ」と引きたい。しかし wiki はプロジェクトスコープのスキルからは見えないし、そもそもスキル自体が存在しない。

そこで:

1. スキル一式を **Claude Code plugin** にして、ユーザー単位でインストールできるようにする
2. 新スキル `/wiki-recall` を追加し、GitHub 上のリポジトリを **ローカルキャッシュに shallow clone して読む**（キャッシュクローン方式）ことで、どのディレクトリからでも wiki を参照できるようにする

plugin 化はフェーズを切って進めた:

- **Phase 1**: `plugin/` ディレクトリ新設、既存 5 スキル + テンプレート同梱、marketplace.json 追加
- **Phase 2**: 新スキル `/wiki-recall` 作成（→ PR その1）
- **Phase 3**: Phase 1–2 の検証（インストール・スキル認識・他プロジェクトからの実行）
- **Phase 4**: 旧 `.claude/skills/` `.claude/commands/` `templates/` を削除して plugin に一本化（→ PR その2）

## Claude Code plugin の仕組み（最低限の理解）

作業前に押さえておくべきだったのは次の 3 点。

### 1. marketplace は「ただの git リポジトリ」

Claude Code の plugin marketplace には npm レジストリのような中央サーバーは存在しない。実体は **`.claude-plugin/marketplace.json` を含む git リポジトリ（またはローカルディレクトリ）** そのもの。公式の配布手順も「リポジトリを作る → `.claude-plugin/marketplace.json` を置く → ユーザーに `/plugin marketplace add owner/repo` してもらう」の 3 ステップだけである。

```
/plugin marketplace add <owner>/<repo>     # GitHub リポジトリを marketplace として登録
/plugin marketplace add /path/to/dir       # ローカルディレクトリでも可
/plugin install <plugin名>@<marketplace名>
```

> 📖 参考: [マーケットプレイスをホストして配布する – プラグインマーケットプレイスの作成と配布](https://code.claude.com/docs/ja/plugin-marketplaces#host-and-distribute-marketplaces) / [マーケットプレイスファイルを作成する](https://code.claude.com/docs/ja/plugin-marketplaces#create-the-marketplace-file)

`marketplace add` の実行時、Claude Code は **実行者自身の git / gh 認証情報で** リポジトリを clone し、中の `marketplace.json` を読む。どこかに公開・登録される工程は一切ない。公式ドキュメントにも「手動のインストール・更新には既存の git credential helper（`gh auth login`、macOS Keychain、`git-credential-store` など）をそのまま使う」と明記されている。

つまり private リポジトリの場合、**リポジトリの read 権限がない人は marketplace 登録の時点で clone に失敗する**。追加のアクセス制御は不要で、「GitHub 上でリポジトリへの read 権限を渡すこと」がそのまま plugin の配布権限になる。社内限定の plugin 配布はこれだけで成立する。

1 点だけ注意があり、起動時のバックグラウンド自動更新は credential helper を使わない（対話プロンプトが起動をブロックするため）。private marketplace の自動更新まで効かせたい場合は `GITHUB_TOKEN` などのトークンを環境変数で渡す必要がある。

> 📖 参考: [プライベートリポジトリ – プラグインマーケットプレイスの作成と配布](https://code.claude.com/docs/ja/plugin-marketplaces#private-repositories) / [マーケットプレイスが読み込まれない – プラグインマーケットプレイスの作成と配布](https://code.claude.com/docs/ja/plugin-marketplaces#marketplace-not-loading)

### 2. plugin が認識するのは「plugin ルート直下の skills/」だけ

plugin のスキルの置き場所は、plugin ルート（= `.claude-plugin/plugin.json` がある階層）直下の `skills/`（旧形式は `commands/`）と決まっている。`.claude/skills/` はプロジェクトスコープ用の**別機構**であり、plugin システムからは見えない。だからファイル移動が必須だった。

公式ドキュメントには「よくある間違い」として「`skills/` や `commands/` を `.claude-plugin/` の中に入れてはいけない（`.claude-plugin/` に入るのは `plugin.json` だけ。他のディレクトリはすべて plugin ルート直下）」という警告まで書かれている。

> 📖 参考: [プラグイン構造の概要 – プラグインを作成する](https://code.claude.com/docs/ja/plugins#plugin-structure-overview) / [プラグインコンポーネント（Skills） – プラグインリファレンス](https://code.claude.com/docs/ja/plugins-reference)

### 3. plugin ルートをリポジトリルートにしない方がよい場合がある

marketplace.json の各 plugin エントリの `source` には、marketplace リポジトリ内の相対パス（`./` 始まり必須、marketplace ルート基準で解決）を指定できる。そして重要な仕様として、**marketplace 経由でインストールされた plugin は、plugin ルート以下がまるごとローカルの plugin キャッシュ（`~/.claude/plugins/cache`）へコピーされる**（in-place 参照ではない）。

> 📖 参考: [相対パス – プラグインマーケットプレイスの作成と配布](https://code.claude.com/docs/ja/plugin-marketplaces#relative-paths) / [プラグインのキャッシュとファイル解決 – プラグインリファレンス](https://code.claude.com/docs/ja/plugins-reference#plugin-caching-and-file-resolution)

つまりリポジトリルートを plugin ルートにすると、**インストール時に raws/ や wiki/ などデータ全体が plugin キャッシュへコピーされてしまう**。

そこで「仕組み（plugin/）」と「データ（raws/ wiki/）」を分離し、`plugin/` サブディレクトリを plugin ルートにした:

```
notes-wiki/
├── .claude-plugin/
│   └── marketplace.json         # marketplace 定義（リポジトリルート）
├── plugin/                      # ← plugin ルート
│   ├── .claude-plugin/
│   │   └── plugin.json          # plugin マニフェスト
│   ├── skills/                  # 6 スキル（各ディレクトリに SKILL.md）
│   ├── templates/               # スキルが使うテンプレート
│   └── README.md
├── raws/                        # 読書メモ原本（plugin には含めない）
└── wiki/                        # LLM 編纂の知識ベース（plugin には含めない）
```

marketplace.json はこう:

```json
{
  "name": "notes-wiki",
  "owner": { "name": "<owner>" },
  "plugins": [
    {
      "name": "notes-wiki",
      "source": "./plugin",
      "description": "notes-wiki の運用スキル一式（add-book / add-article / update-wiki / lint-wiki / save-query）と、他プロジェクトから wiki の知識を引用する wiki-recall スキル"
    }
  ]
}
```

plugin.json はこう:

```json
{
  "name": "notes-wiki",
  "version": "0.1.0",
  "description": "notes-wiki（LLM Wiki パターンの読書メモリポジトリ）の運用スキル一式と、他プロジェクトから wiki の知識を引用する wiki-recall スキル",
  "author": { "name": "<owner>" }
}
```

## /wiki-recall の設計（キャッシュクローン方式）

plugin 化の主目的である「他プロジェクトから読書メモを引く」スキル。設計のポイント:

- **source of truth は GitHub 上のリポジトリ**。ローカルの checkout に依存しない
- 初回実行時に `git clone --depth 1` で `$HOME/.cache/notes-wiki` へ shallow clone。2 回目以降は `git pull --ff-only` で最新化
- **pull 失敗時（ネットワーク断など）はキャッシュで続行**し、最終コミット日付きで「古い可能性がある」と必ず注記する（黙って古い情報を出さない）
- リポジトリ URL は環境変数 `WIKI_REPO` で差し替え可能（フォークや移転に備える）
- **完全に読み取り専用**。キャッシュ内への書き込み・コミット・プッシュは一切しない。キャッシュは使い捨て（`--refresh` で作り直せる）
- カレントディレクトリが notes-wiki 自身のときはキャッシュを使わず手元の wiki/ を直接読む
- 回答には**必ず出典（concept slug / source slug）を付ける**。wiki に情報がなければ「まだ蓄積されていない」と正直に言い、一般知識で補う場合は wiki 由来でないことを区別する
- wiki ページの frontmatter `status`（active / draft / stale / contradicted / archived）に応じて扱いを変える。`archived` は参照しない

「設定ゼロで動く」ことを重視した。パス設定もデータ配置も不要で、git の認証さえ通っていれば `/wiki-recall <質問>` だけで動く。

## テンプレートの参照と `${CLAUDE_PLUGIN_ROOT}`

スキルが使うテンプレート（読書メモ・wiki ページの雛形）は plugin に同梱し、SKILL.md 内からは:

```
${CLAUDE_PLUGIN_ROOT}/templates/book-template.md
```

のように参照する。`${CLAUDE_PLUGIN_ROOT}` は **Claude Code 本体が plugin 実行時に自動で設定する変数**で、plugin のインストール先ディレクトリの絶対パスに展開される。リポジトリ側で定義する必要はない。公式リファレンスによれば、スキル本文・agent 本文・hook コマンドなどの中に書けばインラインで置換され、hook や MCP サーバーのサブプロセスには環境変数としても渡される。

実はこれ、最初は「どこで設定される変数なのか」が分からなくて不安だった。

> 📖 参考: [環境変数 – プラグインリファレンス](https://code.claude.com/docs/ja/plugins-reference#environment-variables)

## 時系列の作業ログ

### 1. フェーズ分割

いきなり移行せず、フェーズを切って進めた。特に「旧スキルの削除（Phase 4）」を plugin 追加（Phase 1–2）と**別 PR に分離**したのが効いた。plugin 追加の PR は「増えるだけ」なので安全にマージでき、削除はマージ後に plugin 側の動作を確認してから行える。

### 2. Phase 1–2: plugin/ ディレクトリの構築と `/wiki-recall` スキルの作成（PR その1）

- `plugin/skills/` に 6 スキルの SKILL.md を移植
  - 移植時に「実行環境の前提」セクションを各スキルに追加（notes-wiki リポジトリ内でしか意味がないスキルは `raws/` と `wiki/` の存在を確認し、なければ中断する。plugin はどこからでも呼べてしまうため）
  - テンプレート参照を相対パスから `${CLAUDE_PLUGIN_ROOT}/templates/` に変更
- `/wiki-recall` の SKILL.md を新規作成
- `plugin/templates/` にテンプレート一式をコピー
- `plugin/.claude-plugin/plugin.json` と、リポジトリルートの `.claude-plugin/marketplace.json` を作成
- PR 作成。この時点では旧 `.claude/skills/` はそのまま残す（併存期間）

なお、後から知ったが「既存の `.claude/` 構成を plugin に変換する」手順は公式ドキュメントにそのまま載っている（移行後に旧ファイルを消さないと重複する、という注意書きも含めて）。移行方法だけ知りたい人は以下の公式ドキュメントを読めば必要なことがわかると思う。

> 📖 参考: [既存の設定をプラグインに変換する – プラグインを作成する](https://code.claude.com/docs/ja/plugins#convert-existing-configurations-to-plugins)

### 3. Phase 3: マージ前検証

ここでは何点か詰まったポイントがあった（詳細は次章）。実施した検証は 3 つ:

1. **ローカルパス形式で marketplace add + install**

   ```
   /plugin marketplace add c:/Users/<you>/notes-wiki
   /plugin install notes-wiki@notes-wiki
   ```

   ローカルパス形式は**チェックアウト中のブランチの作業ツリー**を読むので、PR ブランチのまま検証できる（GitHub 形式が使えない理由は詰まったポイント②参照）。「配布前にローカルパスでテストする」手順は公式ドキュメントでも推奨されている

   > 📖 参考: [配布前にローカルでテストする – プラグインマーケットプレイスの作成と配布](https://code.claude.com/docs/ja/plugin-marketplaces#test-locally-before-distribution)

2. **6 スキルが正しい説明文つきで認識されるか確認**
   セッション再起動後、`/` を打つとスキルが `notes-wiki:add-book` のように **plugin 名の namespace 付き**で列挙される。これが plugin 経由で認識されている証拠（旧 `.claude/skills/` 版は「(project)」表記で併存して見えるので区別できる）。plugin のスキルが常に namespace 付きになるのは、plugin 間の名前衝突を防ぐための公式仕様

   > 📖 参考: [最初のプラグインを作成する（名前空間に関する Note）– プラグインを作成する](https://code.claude.com/docs/ja/plugins#quickstart)

3. **別プロジェクトから `/wiki-recall` を実行**
   全く関係ないプロジェクトのディレクトリで
   ```
   /notes-wiki:wiki-recall sqlの設計におけるポイントを教えて
   ```
   を実行。`~/.cache/notes-wiki` への shallow clone が走り、『SQL実践入門』由来の concept 5 つ（実行計画・インデックス・結合アルゴリズムなど）を出典 slug 付きで合成回答し、wiki に蓄積のない領域（正規化・命名規約など）は「まだ蓄積されていない」と正直に区別した。期待どおりの動作

このほか、検証中に `claude plugin validate ./plugin` という CLI を知り、frontmatter の致命的バグを 2 件検出できた（後述）。**plugin を作ったらまず validate を回すべき**だった。validate は公式ドキュメントで marketplace / plugin の検証手順として案内されているコマンドで、セッション内から `/plugin validate` でも実行できる。

> 📖 参考: [検証とテスト – プラグインマーケットプレイスの作成と配布](https://code.claude.com/docs/ja/plugin-marketplaces#validation-and-testing) / [デバッグと開発ツール – プラグインリファレンス](https://code.claude.com/docs/ja/plugins-reference#debugging-and-development-tools)

### 4. PR その1 をマージ

検証で見つかった修正コミット（frontmatter クォート修正）を積んでマージ。

### 5. Phase 4: 旧スキル削除への切り替え（PR その2）

- `.claude/skills/`（5 スキル）、`.claude/commands/`、リポジトリルートの `templates/` を削除
- CLAUDE.md / README / WORKFLOW を「スキルは plugin が提供する」前提に書き換え
- マージ前に、このブランチ上で plugin 版 `/add-article` → `/update-wiki` → `/lint-wiki` の一巡テストを実施（旧スキルが消えた状態で plugin 版だけで運用が回ることの確認）

### 6. マージ後の切り替え

マージ後は marketplace をローカルパス版から GitHub 版に登録し直す:

```
/plugin marketplace remove notes-wiki
/plugin marketplace add <owner>/notes-wiki
/plugin install notes-wiki@notes-wiki
```

以後の plugin 更新は GitHub の main を pull する形になり、他のマシンでも同じ 2 コマンドでセットアップできる。

## 詰まったポイント集

### ① SKILL.md の frontmatter が YAML パースエラーで「黙って」空になる

スキルの frontmatter にこう書いていた:

```yaml
---
name: lint-wiki
description: wiki/ 全体の健全性を静的検査する
argument-hint: [--fix] [--dry-run] [--scope <namespace>] [--severity <level>] | --help
---
```

`argument-hint` の値が `[` で始まっているため、YAML の**フローシーケンス（インライン配列）**として解釈が始まり、2 つ目のブラケット以降で `Unexpected token` になる（YAML 仕様上、`[` はフローシーケンスの開始記号）。問題はエラーの出方で、**Claude Code はこの場合 frontmatter 全体を黙って空として読み込む**。例外も警告も出ない。

ちなみに `argument-hint` 自体は公式の Frontmatter reference に載っている正規のフィールドで、記載例は `[issue-number]` — **公式の例からしてブラケット形式**である。ブラケットが 1 組だけなら valid な YAML（ただし文字列でなく配列）として通ってしまうため、複数組を書いたときだけ突然壊れる、という気づきにくい罠になっている。

> 📖 参考: [フロントマターリファレンス – スキルで Claude を拡張する](https://code.claude.com/docs/ja/skills#frontmatter-reference) / [Flow sequences – YAML 仕様 1.2.2](https://yaml.org/spec/1.2.2/#flow-sequences)

症状は一見無関係に見える:

- スキル一覧での説明文が、`description` ではなく**本文の最初の見出し（「概要」など）にフォールバック**する
- `name` も落ちるので、スキルとしての認識自体が不安定になる

スキル一覧に「概要」とだけ表示されているのを見て「なんか変だな」と思いつつ、原因が frontmatter の YAML パースエラーだとは最初は結びつかなかった。

検出できたのは `claude plugin validate` のおかげ:

```
claude plugin validate ./plugin
```

これがスキルごとの frontmatter パース結果を報告してくれて、2 スキル（lint-wiki / save-query、ブラケットが複数あるもの）が致命的エラー、他も配列として解釈されていることが分かった。

修正はダブルクォートで文字列化するだけ:

```yaml
argument-hint: "[--fix] [--dry-run] [--scope <namespace>] [--severity <level>] | --help"
```

なおこのバグは旧 `.claude/skills/` 時代から存在していた（プロジェクトスコープでも同じ問題は起きる）。plugin 化のついでの validate で初めて顕在化した形。

**教訓: SKILL.md を書いたら `claude plugin validate` を必ず通す。`argument-hint` のようなブラケットを含む値はクォート必須。**

### ② GitHub 形式の marketplace add はマージ前だと失敗する

PR がまだマージされていない状態で

```
/plugin marketplace add <owner>/notes-wiki
```

を実行したら `Error: Marketplace file not found`。GitHub 形式は **リポジトリのデフォルトブランチ（通常 main）** を clone して `marketplace.json` を探すため、marketplace.json がまだ PR ブランチにしかない段階では見つからない。当然といえば当然だが、エラーメッセージからは理由が読み取りにくい。

マージ前検証は**ローカルパス形式**（チェックアウト中の作業ツリーを読む）で行う:

```
/plugin marketplace add c:/Users/<you>/notes-wiki
```

なお、後で公式ドキュメントを読むと `owner/repo@ブランチ名` の形式でブランチやタグを指定して add することもできるようだ（私は未検証。マージ前の PR ブランチを直接指す手もあったかもしれない）。

> 📖 参考: [plugin marketplace add – プラグインマーケットプレイスの作成と配布](https://code.claude.com/docs/ja/plugin-marketplaces#plugin-marketplace-add)（`@ref` でブランチ・タグをピンできる旨の記載あり）

### ③ install してもスキルが認識されない → 再起動か `/reload-plugins` が必要

install 直後に `/wiki-recall` を打ったら `No commands match "/wiki-recall"`。**plugin のインストールや設定変更は、実行中のセッションには自動反映されない**。Claude Code を再起動したら認識された。

なお、再起動せずに plugin・スキル・hook などを再読み込みする `/reload-plugins` コマンドも公式ドキュメントに載っている。後日こちらも試したところ、install 直後に実行すれば**同じセッション内でそのままスキルが使えるようになる**ことを確認した（当時は知らず再起動で解決した）。

> 📖 参考: [プラグインをローカルでテストする – プラグインを作成する](https://code.claude.com/docs/ja/plugins#test-your-plugins-locally)（`/reload-plugins` の説明）

このとき同時に `Auto-update failed: claude.exe in use` という警告も出ていた。複数の Claude Code セッションを開いたまま作業していたのが原因（Windows では実行中の exe を置き換えられない）。**検証時は他のセッションを全部閉じてから再起動**するのが確実。

### ④ 併存期間中はスキルが二重に見える

Phase 1–2 マージ後 Phase 4 マージ前は、同名スキルが

- `add-book (project)` — 旧 `.claude/skills/` 版
- `notes-wiki:add-book` — plugin 版

の 2 つ見える。検証時は namespace 付きで明示的に呼べば plugin 版を確実にテストできる。この紛らわしさを解消するのが Phase 4（旧スキル削除）で、削除 PR を分離しておいたことで「plugin 版の動作確認が取れてから消す」手順が守れた。

公式の移行ガイドにも「移行後は重複を避けるため元の `.claude/` のファイルを削除すること」という注意書きがある。

> 📖 参考: [既存の設定をプラグインに変換する – プラグインを作成する](https://code.claude.com/docs/ja/plugins#convert-existing-configurations-to-plugins)

## まとめ

- Claude Code plugin は「`plugin.json` を置いたディレクトリ + `marketplace.json` を置いた git リポジトリ」だけで成立する。private リポジトリの参照権限がそのまま配布権限になるので、個人・社内用途に向いている
- プロジェクトスコープのスキルを plugin 化する価値は「どこからでも呼べる」こと。データ本体をリポジトリに残し、スキルが実行時に clone/pull して読む**キャッシュクローン方式**にすれば、知識ベースをどのプロジェクトからでも引ける
- ハマりどころは frontmatter の YAML（ブラケットはクォート）、マージ前検証はローカルパス形式、install 後の反映は再起動か `/reload-plugins`
- `claude plugin validate` は最初に回す。移行のような「増やしてから消す」変更は PR を分けると安全に進められる

## 参考リンク

本文中で参照した公式ドキュメントの一覧:

- [プラグインを作成する（plugin の作り方・standalone との使い分け・移行手順）](https://code.claude.com/docs/ja/plugins)
- [プラグインリファレンス（マニフェストスキーマ・環境変数・キャッシュの仕様）](https://code.claude.com/docs/ja/plugins-reference)
- [プラグインマーケットプレイスの作成と配布（marketplace.json・plugin source・private リポジトリ）](https://code.claude.com/docs/ja/plugin-marketplaces)
- [プラグインの発見とインストール（利用者向けのインストール手順）](https://code.claude.com/docs/ja/discover-plugins)
- [スキルで Claude を拡張する（SKILL.md のフロントマターリファレンス）](https://code.claude.com/docs/ja/skills#frontmatter-reference)
- [Karpathy の LLM Wiki パターン（着想元の gist）](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
