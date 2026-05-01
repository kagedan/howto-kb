---
id: "2026-04-30-mastra-announce-ワークスペースが-lsp-対応-ソースコード解釈が大幅パワーアップ-01"
title: "[Mastra Announce] ワークスペースが LSP 対応！ ソースコード解釈が大幅パワーアップ"
url: "https://zenn.dev/shiromizuj/articles/2ee37b4e35b544"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "zenn"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。普段このシリーズでは「速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです」と書いているのですが、**今回も私の勝手解釈が多めです**。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## Mastra が「ワークスペースのLSP対応」を発表

2026年4月27日、Mastra は **LSP Inspection for Mastra Workspaces** を発表しました。

アナウンスの冒頭を直訳すると以下のようになります。

> Mastraワークスペースは、言語サーバープロトコル（LSP）の検査をサポートするようになりました。これにより、エージェントは生のテキスト分析に頼るのではなく、言語サーバーに型情報、定義、実装の詳細を照会できるようになります。

もう少し詳しくいうと、Mastra の Workspace に `lsp: true` を設定すると、エージェントは `lsp_inspect` ツールを使って言語サーバーへ問い合わせできるようになります。これにより、単なる文字列検索ではなく、**定義ジャンプ・型情報・実装参照**のような「言語意味ベース」の調査が可能になります。

重要なのは、これが既存の `read_file` や `grep` を置き換えるものではない点です。ファイル閲覧と検索はそのまま使い、必要なときだけ LSP を使って深掘りする、という位置づけです。

ちなみに、MastraのWorkspace機能について解説が必要な方はこちらをご覧ください。  
<https://zenn.dev/shiromizuj/articles/25f8de31d22ddf>

---

## そもそも LSP とは何か

LSP（Language Server Protocol）は、エディタと「言語解析エンジン」をつなぐ共通規格です。VS Code の「定義へ移動」「参照検索」「型エラー表示」もこの仕組みで動いています。

### LSP のプロセスモデル ― 「サーバー」はリモートではなくローカルのバイナリ

「言語サーバー」という名前から、どこかにサーバーが立っているイメージを持ちがちですが、実態は**開発者のマシンにインストールされた実行可能ファイル**です。ネットワークは関係ありません。

| 言語 | バイナリ名 | 代表的なインストール方法 |
| --- | --- | --- |
| TypeScript / JS | `typescript-language-server` | `npm install typescript-language-server typescript` |
| Python | `pyright` | `pip install pyright` |
| Go | `gopls` | `go install golang.org/x/tools/gopls@latest` |
| Rust | `rust-analyzer` | `rustup component add rust-analyzer` |

LSP の設計上の特徴は、この解析バイナリを**クライアントとは別プロセスとして起動**し、stdin/stdout 経由の JSON-RPC でやり取りする点にあります。

```
[クライアント（エディタ / Mastra Workspace など）]
           ↕  JSON-RPC（stdin/stdout ― ローカルプロセス間通信）
[言語サーバー ＝ ローカルにインストールされたバイナリ（tsserver / Pyright / gopls など）]
```

Mastra は `lsp_inspect` を初めて呼んだタイミングで、対象言語のバイナリを子プロセスとして起動します。クライアントが「このシンボルの型は？」と送ると、言語サーバーが「`string` 型、定義は `src/types.ts:42`」と返す往復です。AI エージェントに置き換えると、次の差が出ます。

たとえば `UserService` がどこで定義され、どこで参照され、実体はどのファイルの何行にあるかを、単純な grep より高精度でたどれます。

### インデックスはどこにあるか ― 言語サーバーが自前で持つ

「LSP がシンボルを追跡できる」のは、言語サーバーが**起動後に自分でプロジェクトをスキャンして意味モデルを構築する**からです。「どこかにインデックスファイルを置く」というより、言語サーバー自身がその作業をするイメージです。

実態は言語サーバーごとに異なります。

| 言語サーバー | インデックスの実態 |
| --- | --- |
| TypeScript (`tsserver`) | `tsconfig.json` を起点に参照ファイルをすべてメモリ上で解析 |
| Python (`Pyright`) | `pyrightconfig.json` / `pyproject.toml` を起点にメモリで解析 |
| Go (`gopls`) | ディスクキャッシュあり（`$XDG_CACHE_HOME/gopls`）。二回目以降は高速 |
| Rust (`rust-analyzer`) | ディスクキャッシュあり。初回は重いが再起動後は差分読み込み |

つまり Mastra 自身はコード解析ロジックを持たず、**ローカルにインストールされた各言語のバイナリに委ねる**設計です。逆に言えば、対応バイナリがマシンに入っていないと LSP は機能しません。

### 起動時のタイムラグ ― `initTimeout` が存在する理由

言語サーバーは起動直後からすぐに答えを返せるわけではありません。プロジェクトのファイルをスキャンして意味モデルが固まるまでは「ロード中」状態が続きます。

* 小さなプロジェクト（数十ファイル）: 数秒
* 中規模（数百ファイル）: 10〜30 秒程度
* 大規模モノレポ: それ以上になることもある

Mastra の設定オプションに `initTimeout`（デフォルト 8 秒）が存在するのは、まさにこのためです。

```
const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './workspace' }),
  lsp: {
    initTimeout: 15000,     // 大きなプロジェクトでは引き上げる
    diagnosticTimeout: 4000, // 編集後の診断を待つ最大時間
  },
});
```

また言語サーバーは**遅延起動**（**オンデマンド**）です。ワークスペースを作った瞬間ではなく、対象言語のファイルを最初に `lsp_inspect` で問い合わせたタイミングで起動します。

### ファイル変更への追従 ― 明示的な再インデクシングは不要

Mastra の workspace ツール（`edit_file`、`write_file`、`ast_edit`）がファイルを変更すると、内部で言語サーバーに `textDocument/didChange` 通知を送ります。言語サーバーはこれを受けて**差分更新**を行います。

新規ファイル追加の場合は `workspace/didChangeWatchedFiles` 通知が使われます。どちらも Mastra が自動で処理するため、**利用者が手動でインデックスを更新したり、再起動を指示したりする必要はありません**。

編集後すぐに診断結果を取れるのも、この連携があるからです（待ち時間は `diagnosticTimeout` で制御）。

### 余談：Serena も「LSP を使う MCP サーバー」

最近注目されている **[Serena](https://github.com/oraios/serena)**（23,000 以上 ⭐、GitHub: oraios/serena）も、内部構造は同じ LSP が軸です。Serena は「エージェント向けの IDE」を標榜する MCP サーバーで、40 以上の言語をカバーするために各種 LSP 実装を抽象化して束ねています（JetBrains プラグインをバックエンドにする有償モードもあり）。

![](https://static.zenn.studio/user-upload/003e6dd578ac-20260428.png)

```
Serena:          [AI クライアント] ← MCP → [Serena サーバー] ← LSP → [各言語サーバー]
Mastra Workspace: [Mastra エージェント] ← Workspace ツール → [LSP クライアント内蔵] ← LSP → [各言語サーバー]
```

外側の接続方式が「MCP」か「Workspace ツール」かという違いはありますが、コード解析の実体はどちらも LSP 実装に委ねています。「LSP を AI に使わせる」というアプローチ自体はすでに複数のツールが採用しており、Mastra はそれをフレームワーク内に統合した形です。

---

## 改めて今回の発表内容の確認

公式アナウンスの中核は次の3点です。

1. Mastra Workspace が LSP inspection をサポート
2. 有効化すると `lsp_inspect` ツールが追加される
3. 読み取り・検索系ツールの挙動は変えず、深掘り用の追加能力として提供される

最小構成イメージは以下です。

```
import { Agent } from "@mastra/core/agent";
import { Workspace, LocalFilesystem, LocalSandbox } from "@mastra/core/workspace";

const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: "./workspace" }),
  sandbox: new LocalSandbox({ workingDirectory: "./workspace" }),
  lsp: true,
});

export const lspAgent = new Agent({
  id: "lsp-agent",
  name: "LSP Agent",
  model: "anthropic/claude-opus-4-6",
  instructions: "Use workspace tools and lsp_inspect for code understanding.",
  workspace,
});
```

デフォルト対応言語は TypeScript / JavaScript / Python / Go / Rust（および ESLint 診断連携）です。

---

## 「v1.8で作られた機能」なのに「v1.28のタイミングでアナウンス」する理由

LSP 連携の初出は `@mastra/core@1.8.0`（2026-02-26）です。今回の 4/27 記事は「新機能の初公開」というより、**機能の再訴求と導線整理**に近い Announcement です。

実務ではこのパターンはよくあります。

* 機能自体は先に出る（ChangeLog 主体）
* ユースケースが固まってからブログで再整理される
* その時点の周辺機能と合わせて「使い方の型」を示す

つまり「古い」ではなく、**早く出た機能が、今のエコシステムで使いやすくなった段階**と見るのが自然です。

---

## v1.8 以降、LSPまわりで何が改善されたか

リリースノートを追うと、LSP 検査は少しずつ実用性が上がっています。特に効くのは次の2点です。

### 1) v1.9: LSP バイナリ解決の柔軟化

`@mastra/core@1.9.0` では `LSPConfig` に以下が追加されました。

* `binaryOverrides`
* `searchPaths`
* `packageRunner`

これで「プロジェクト直下の node\_modules/.bin にないと動かない」問題が緩和され、モノレポやグローバル導入環境でも LSP が使いやすくなりました。実運用で詰まりやすいのはまさにこの部分なので、体感差が大きい更新です。

### 2) v1.28: カスタム言語サーバー登録

`@mastra/core@1.28.0` では `lsp.servers` が追加され、組み込み以外の言語サーバーを登録可能になりました。PHP / Ruby / Java / Kotlin / Swift / Elixir などへ横展開しやすくなります。

```
const workspace = new Workspace({
  lsp: {
    servers: {
      phpactor: {
        id: "phpactor",
        name: "Phpactor Language Server",
        languageIds: ["php"],
        extensions: [".php"],
        markers: ["composer.json"],
        command: "phpactor language-server",
      },
    },
  },
});
```

この更新により、「LSP inspection は TS/Python 専用っぽい」という初期印象から、**多言語ワークスペース向けの共通基盤**へ進化したと言えます。

---

## どんな場面で効くか

### コードレビュー支援

エージェントが `grep` だけで判断すると、同名関数や再エクスポートで誤認しやすいです。`lsp_inspect` を併用すると、定義元を正確に突き止めやすくなります。

### リファクタリング前の影響調査

「この型を変えたらどこに波及するか」を参照ベースで追えるので、修正範囲見積もりが現実的になります。

### マルチ言語モノレポ探索

言語ごとの解析器を切り替えながら、エージェントの探索品質を保てる点が大きいです。v1.28 のカスタムサーバー登録がここで効きます。

---

## 導入時の注意点

要するに、LSP は万能置換ではなく **高精度モード** です。通常探索と意味解析を使い分けると、コストと精度のバランスがよくなります。

---

## まとめ

4/27 のブログは、2/26 に入った LSP 機能の「再発見記事」です。ただし中身は単なる再掲ではなく、v1.9 以降の運用改善（バイナリ解決）や v1.28 の拡張（カスタム言語サーバー）を踏まえると、今のほうが実用価値は高いです。

Mastra Workspace は、

* `read_file` / `grep` で広く探す
* `lsp_inspect` で意味的に確定する

という二段構えが取りやすくなってきました。エージェントに「コードを読ませる」から「コードを理解させる」へ進む、地味ですが重要な一歩だと思います。

---

## 参考リンク
