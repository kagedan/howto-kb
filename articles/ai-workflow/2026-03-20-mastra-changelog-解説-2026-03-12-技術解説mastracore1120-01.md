---
id: "2026-03-20-mastra-changelog-解説-2026-03-12-技術解説mastracore1120-01"
title: "[Mastra Changelog 解説] 2026-03-12 技術解説（@mastra/core@1.12.0）"
url: "https://zenn.dev/shiromizuj/articles/e0e6f4ae13f837"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-03-20"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Changelogs](https://mastra.ai/blog/category/changelogs)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

---

3月17日に、MastraのVer1.11、1.12、1.13のChangelogsがいっぺんにアップされました。ひとつずつ解説していきます。

2026-03-12 の Mastra リリース（`@mastra/core@1.12.0`）は、**Cloudflare ネイティブなストレージの選択肢追加**、**ファイルシステムのパス解決の正常化**、**MCP・プロセッサー・ワークフロー全体にわたるトレーシング強化**、そして**マルチステップ実行の信頼性向上**を中心としたアップデートです。

今回の焦点は大きく 5 つです。

1. **Cloudflare Durable Objects ストレージアダプター** — KV の次の選択肢として SQLite 永続化を Cloudflare ネイティブに
2. **LocalFilesystem のパス解決修正** — 「仮想ルート」という暗黙の慣習を廃止し、OS と同じセマンティクスへ
3. **MCP・プロセッサー・ワークフローのトレーシング強化** — 「なぜエージェントが止まったか」を見えるようにする
4. **エージェントループとトークン予算の信頼性向上** — 複数ステップ実行でコストが指数的に膨らむ問題を解消
5. **サンドボックス・ファイルシステムの拡張性向上** — プロバイダー固有のゲッターと文字列 PID で「抽象化の裏側」へのアクセスを整備

---

## ハイライト1: Cloudflare Durable Objects ストレージアダプター

### KV の限界と DO が解決すること

Cloudflare Workers で Mastra を動かすとき、従来のストレージ選択肢は KV（Key-Value Store）だけでした。KV は読み取り性能と地理的分散には優れていますが、一貫性の保証が「結果整合性」にとどまります。書き込みが即座に全リージョンに反映されるわけではなく、複数のリクエストが同じデータを同時に更新する状況では予想外の挙動になることがあります。

**Durable Objects**（DO）は Cloudflare が提供する別の永続化プリミティブです。KV と異なり DO は「単一のインスタンスが世界のどこか一か所で動く」という強整合性のモデルを持ちます。そして v1.12 で追加された `@mastra/cloudflare` の DO ストレージアダプターは、この DO の内部に **SQLite** を使ってデータを保存します。

```
KV:  書き込み → 非同期で世界中に伝播（結果整合性）
DO:  書き込み → 単一インスタンスの SQLite に即反映（強整合性）
```

### 追加された機能

* **SQL バックの永続化**: DO 内の SQLite ストレージを使うため、データの順序や関係を問い合わせやすい
* **バッチ操作**: 複数のレコードを一つのトランザクションにまとめて効率化
* **テーブル・カラムバリデーション**: スキーマの不整合を書き込み時に早期に検出

Cloudflare Workers で Mastra を本番運用しているチームにとって、これまで「KV では不安だが外部 DB を用意するほどでもない」という中間の需要を満たすアダプターになります。（[PR #12366](https://github.com/mastra-ai/mastra/pull/12366)）

---

## ハイライト2: LocalFilesystem のパス解決が OS のセマンティクスと一致するように

### 「仮想ルート」という暗黙の慣習が招いていた問題

Mastra の `LocalFilesystem` はエージェントがファイルを読み書きするときの抽象レイヤーです。サンドボックスを構成するとき、`basePath` という「ワークスペースのルートディレクトリ」を設定します。

v1.11 以前、contained モードで絶対パスを渡したとき、`/file.txt` は `basePath/file.txt` として解釈されていました。「`/` はワークスペースのルートを指す」という仮想ルート慣習です。一見便利に見えますが、これが厄介なバグを生んでいました。

```
basePath = /home/agent/workspace
渡したパス = /home/user/.config/settings.json

v1.11 まで → basePath/home/user/.config/settings.json（意図しない場所）
v1.12 から →  /home/user/.config/settings.json（実際のファイルシステム、containment チェックあり）
```

`/home/user/.config` のような「絶対パスに見えるが実は相対として扱われていた」ケースで、予期しない場所にファイルが読み書きされていたわけです。

### 新しいパス解決の規則

v1.12 からは OS の一般的なルールと一致します。

| パスの形式 | 解決先 |
| --- | --- |
| `/foo/bar.txt`（`/` 始まり） | 実際のファイルシステムの `/foo/bar.txt`（containment チェックあり） |
| `src/index.ts`（相対パス） | `basePath/src/index.ts` |
| `~/Documents/file.txt`（`~/` 始まり） | ホームディレクトリ配下 |

### マイグレーション

ワークスペース内のファイルを指定するつもりで絶対パスを使っていたコードは、相対パスに書き直す必要があります。

```
// Before: 絶対パスでワークスペース内を指定していた（仮想ルート慣習）
await filesystem.readFile('/src/index.ts');

// After: 相対パスで指定する
await filesystem.readFile('src/index.ts');
```

あわせて、いくつかの関連バグも修正されています。

* `allowedPaths` が `basePath` ではなく作業ディレクトリ（cwd）を基準に解決されていた問題を修正。`basePath ≠ cwd` の環境で予期しない権限エラーが出ていた原因の一つです。
* まだ存在しないディレクトリを `allowedPaths` に指定していたとき（スキルの自動発見フェーズなどで起こりうる）にエラーが出ていた問題を修正。
* 権限エラーが HTTP 500 ではなく正しく **403** を返すように修正。クライアント側が不要なリトライを繰り返さなくなります。

（[PR #13804](https://github.com/mastra-ai/mastra/pull/13804)）

---

## ハイライト3: MCP・プロセッサー・ワークフローのトレーシング強化

### 「なぜ止まったか」が分からない問題

AIエージェントをプロダクションで動かしていると、「エージェントが途中で止まった、でもログを見ても何が起きたか分からない」という状況はよくあります。今回のリリースでは、この「見えなかった部分」を三か所で改善しています。

### MCP ツール呼び出しに専用のスパン種別

これまで MCP サーバー経由で呼ばれたツールは、通常のツール実行と同じ `TOOL_CALL` スパンとしてトレースに記録されていました。どのスパンが MCP 由来なのかを区別するには、アトリビュートを一件ずつ確認するしかありませんでした。

v1.12 からは MCP 経由のツール呼び出しは **`MCP_TOOL_CALL`** という専用スパン種別で記録されます。スパンには MCP サーバーの名前・バージョン・ツールの説明が自動で付加されます。`@mastra/mcp` の MCP クライアントがツール生成時に `mcpMetadata` を自動付与するため、ユーザー側にコード変更は不要です。

Studio の Trace タイムラインにもMCP専用のアイコンと色が追加されたので、複数のツールが混在するトレースを目視でスキャンするときに一目で MCP ツールを識別できます。

（[PR #13274](https://github.com/mastra-ai/mastra/pull/13274)）

### プロセッサーによるアボートがトレースに表示される

ガードレールやプロセッサーがエージェントの実行を中断（アボート）したとき、これまではトレースにその事実が残りませんでした。「エージェントが動いたはずなのに出力がない」という状況で原因を追うのが困難でした。

v1.12 からは、プロセッサースパンにアボートの詳細（理由・リトライフラグ・メタデータ）が記録されます。エージェントレベルのスパンにも同じ情報が伝播するため、「ガードレールに引っかかったのか」「プロセッサーが止めたのか」がトレース画面で即座に分かります。（[PR #14038](https://github.com/mastra-ai/mastra/pull/14038)）

### ワークフローの suspend/resume でトレースの連続性を保持

長時間動作するワークフローは「中断（suspend）→再開（resume）」を繰り返すことがあります。従来は再開後の処理が別のトレースに切り離され、一連の作業がバラバラのスパンとして見えていました。

v1.12 からはデフォルトエンジンで動くワークフローが suspend/resume をまたいでもトレースの継続性が保たれます。再開後の処理が元のスパンの子として表示されるため、長期実行ワークフローの全体像を一つのトレースツリーで確認できます。（[PR #12276](https://github.com/mastra-ai/mastra/pull/12276)）

---

## ハイライト4: エージェントループとトークン予算の信頼性向上

### 複数ステップ実行の「地雷」二つ

マルチステップのエージェント実行（ツールを呼び出して結果を受け取りまた判断する、を繰り返す）では、小さな制御フローのバグが大きなコスト問題や予期しない停止につながります。今回、特に厄介だったバグが二つ修正されました。

### ループが継続しない問題

`onIterationComplete` フックで `continue: true` を返すと、エージェントが次のイテレーションに進む——はずでしたが、実際にはここでループが止まっていました。ループ継続の条件判定にバグがあり、`continue: true` が無視されていたためです。

このフックを使っていたコードは、実質「一回しか動かない」状態で動作していたことになります。v1.12 で修正され、意図通りに動くようになりました。（[PR #14170](https://github.com/mastra-ai/mastra/pull/14170)）

### トークンが指数的に増える問題

エージェントがツールを呼び出しながら複数ステップを繰り返すとき、`TokenLimiterProcessor`（トークン数を上限以下に保つプロセッサー）によるメッセージ刈り込みが **最初のステップでしか動いていませんでした**。ツールの呼び出し結果が会話履歴に積み上がっていく後続ステップでは刈り込みが走らず、コンテキストウィンドウに送られるトークン数がステップを重ねるごとに膨らんでいました。

```
ステップ1: 刈り込み ✓
ステップ2（ツール結果受け取り後）: 刈り込み ✗ ← ここが問題
ステップ3: 刈り込み ✗
...
```

修正後は `processInputStep` が追加され、ツールコール継続を含む**すべてのステップの直前**でトークン予算超過チェックが走ります。また、Tiktoken エンコーダーの初期化もプロセッサーごとに新規インスタンスを作る非効率な実装から、グローバルシングルトン（`getTiktoken()`）の共有に変わり、CPU・メモリ負荷も下がりました。（[PR #13929](https://github.com/mastra-ai/mastra/pull/13929)）

---

## ハイライト5: サンドボックス・ファイルシステムの拡張性向上

### 抽象化の「裏側」へのアクセスを整える

Mastra のサンドボックス（Daytona・Blaxel・E2B など）やワークスペースファイルシステム（S3・GCS など）は、プロバイダーの違いを吸収する統一インターフェースを提供しています。しかし「プロバイダー固有の高度な機能（S3 の presigned URL、GCS のバケット直接操作）を使いたい」という場面で、これまでは内部の SDK インスタンスにアクセスする標準的な方法がなく、実装の詳細に依存する必要がありました。

### プロバイダー固有のゲッター

v1.12 からは、各プロバイダーが明示的なゲッターを公開します。

```
// サンドボックスのゲッター
const daytonaSandbox = sandbox.daytona;  // 直接 Daytona SDK の Sandbox インスタンス
const blaxelSandbox  = sandbox.blaxel;   // 直接 Blaxel SDK の SandboxInstance

// ファイルシステムのゲッター
const s3Client  = filesystem.client;     // AWS S3Client インスタンス（presigned URL など）
const gcsStorage = filesystem.storage;   // Google Cloud Storage インスタンス
const gcsBucket  = filesystem.bucket;    // GCS バケットインスタンス
```

これにより「Mastra の抽象化で 80% のことを済ませ、残り 20% はプロバイダー SDK で直接やる」という設計が、ハックなしで実現できます。なお、従来の汎用 `sandbox.instance` ゲッターはこの変更により非推奨になります。IDE の補完でプロバイダー名のゲッターが見えるので、どのゲッターを使えばいいかも一目瞭然です。（[PR #14166](https://github.com/mastra-ai/mastra/pull/14166)）

### プロセス ID が文字列に統一

`ProcessHandle.pid` の型が `number` から `string` になりました。

これは Daytona のように「プロセスをセッション ID で管理する」プロバイダーに対応するためです。従来は数値 PID を前提とした設計だったため、Daytona や Blaxel では `parseInt()` で ID を強制変換するワークアラウンドが必要でした。文字列に統一することで、どのプロバイダーでもネイティブな ID をそのまま使えます。

```
// Before: number 型
const handle = await sandbox.processes.spawn('node server.js');
handle.pid;  // number (例: 1234)
await sandbox.processes.get(42);

// After: string 型
const handle = await sandbox.processes.spawn('node server.js');
handle.pid;  // string (例: '1234' ローカル、'session-abc' Daytona)
await sandbox.processes.get('1234');
```

（[PR #13591](https://github.com/mastra-ai/mastra/pull/13591)）

---

## その他の注目アップデート

### User-Agent ヘッダーの付与

OpenAI・Anthropic・Google・Mistral・Groq・xAI・DeepSeek などすべてのプロバイダー API リクエストに `mastra/<version>` の User-Agent ヘッダーが自動付与されるようになりました。Mastra 経由のトラフィックをゲートウェイやプロバイダーのダッシュボードで識別・集計できます。（[PR #13087](https://github.com/mastra-ai/mastra/pull/13087)）

### プロセッサー一覧取得のバグ修正

`listConfiguredInputProcessors()` と `listConfiguredOutputProcessors()` が、個別のプロセッサーの配列ではなく「結合されたワークフロー」を返していたバグが修正されました。ID でプロセッサーを検索・取得する操作が正しく動くようになります。（[PR #14158](https://github.com/mastra-ai/mastra/pull/14158)）

### リトライのバックオフ調整

`fetchWithRetry` のバックオフが `2s → 4s → 8s` と指数的に増加し、以降は 10s にキャップされるようになりました。以前は固定間隔だったため、一時的な過負荷状態で大量のリトライが集中してしまうことがありました。（[PR #14159](https://github.com/mastra-ai/mastra/pull/14159)）

### サブエージェントのメモリ設定上書きバグ修正

`defaultOptions.memory` を持つサブエージェントが、親エージェントのツールとして呼ばれたとき、親の memory 設定（新しく生成されたスレッド ID・リソース ID）で上書きされてしまう問題が修正されました。サブエージェントに独自のメモリ設定がある場合はそれが優先されます。コード変更は不要です。（[PR #11561](https://github.com/mastra-ai/mastra/pull/11561)）

### MCP stdio サーバーに `stderr` と `cwd` オプション

MCP の stdio サーバー設定で `stderr`（エラー出力の扱い）と `cwd`（作業ディレクトリ）が指定できるようになりました。

```
const mcp = new MCPClient({
  servers: {
    myServer: {
      command: 'node',
      args: ['server.js'],
      stderr: 'pipe',   // エラー出力をパイプで取得
      cwd: '/path/to/server',  // サーバーの作業ディレクトリ
    },
  },
});
```

（[PR #13959](https://github.com/mastra-ai/mastra/pull/13959)）

### Observational Memory のスレッショルド処理の軽量化

Observational Memory がローカルでのスレッショルドチェックをより低い CPU・メモリ負荷で行うように最適化されました。画像対応のマルチモーダルなスレッショルド動作は引き続きサポートされており、既存の OM 設定に変更は不要です。（[PR #14178](https://github.com/mastra-ai/mastra/pull/14178)）

### Studio の読み込み高速化

Studio の静的アセットが圧縮配信されるようになりました。開発環境（dev）・本番デプロイ（deploy）の両方でバンドルのダウンロードが速くなります。ただし最初の実装では圧縮が全 API ルートに適用されてしまい JSON レスポンスが読み取れなくなる問題が発生したため、圧縮を静的アセットのみに限定する修正もあわせてすぐに入りました。（[PR #13945](https://github.com/mastra-ai/mastra/pull/13945), [PR #14190](https://github.com/mastra-ai/mastra/pull/14190)）

---

## 破壊的変更

v1.12 の破壊的変更は 2 点です。どちらも自動コードモッドが用意されています。

```
npx @mastra/codemod@latest v1
```

### 1. LocalFilesystem の絶対パス解決の変更

絶対パス（`/` 始まり）を渡していた箇所で、ワークスペース相対として動いていたコードは相対パスへの書き換えが必要です。

```
// Before
await filesystem.readFile('/src/index.ts');

// After
await filesystem.readFile('src/index.ts');
```

### 2. ProcessHandle.pid が string に変更

数値 PID を前提としたコード（数値演算や `processes.get(42)` のような呼び出し）は文字列ベースに変更する必要があります。

```
// Before
handle.pid;  // number
await sandbox.processes.get(42);

// After
handle.pid;  // string
await sandbox.processes.get('1234');
```

---

## バージョン要件

```
{
  "dependencies": {
    "@mastra/core": "^1.12.0",
    "@mastra/memory": "^1.7.0",
    "mastra": "^1.12.0"
  }
}
```

---

今回のリリースは「見えていなかったものを見えるようにする」「動いていなかったものを動くようにする」という地道な仕上げが多いリリースです。特にトレーシング強化（MCP 専用スパン・プロセッサーアボート可視化・ワークフロー継続性）は、プロダクションで「なぜこうなったか」を調査するコストを大きく下げます。トークン指数増大のバグ修正も、長いエージェント実行を本番で使っているチームには即アップデートを勧めたい内容です。

詳細は[公式 Changelog](https://mastra.ai/blog/changelog-2026-03-12) と [GitHub Release](https://github.com/mastra-ai/mastra/releases/tag/%40mastra%2Fcore%401.12.0) をあわせてご覧ください。
