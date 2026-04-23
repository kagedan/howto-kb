---
id: "2026-04-02-claude-codeでai-rssリーダーを作ったらその日にinoreaderを解約した-01"
title: "Claude CodeでAI RSSリーダーを作ったら、その日にInoreaderを解約した"
url: "https://zenn.dev/caphtech/articles/feed-curator-ai-rss-with-claude-code"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

## TL;DR

Claude Code自身をAIキュレーターとして使うRSSツール「Feed Curator」を作った。APIキー不要。トピックを入力するだけでRSSフィードを検索・おすすめしてくれて、既読・スキップの履歴から嗜好を自動学習し、毎朝パーソナライズされた技術ブリーフィングを生成する。現在はBun + Tauri 2でデスクトップアプリ化し、アイコンを開くだけで使える。

<https://github.com/rizumita/feed-curator>

## なぜ作ったか

Inoreaderを使っていた。フィードは増える一方で、未読は13,000件を超えていた。「開いて、タイトルを見て、閉じる」の繰り返し。

思った。**Claude Codeをすでに使っているなら、それ使えばよくない？** 別途APIキーを取得する必要もなく、Claude Codeのサブプロセスとして呼び出せばいい。RSSの取得もスコアリングも要約も、作れそうだと思った。

思いついたその日に作り始めて、その日のうちに基本機能が動いた。生成されたブリーフィングを見た瞬間、Inoreaderを解約した。作り始めてから解約まで、同じ日のことだ。「未読を消化する」から「朝刊を読む」に体験が変わった。

## 設計判断：なぜClaude Codeサブプロセスなのか

Feed CuratorのAI統合は、Claude Code CLIの `-p`（パイプモード）+ `--output-format json` で実装している。

```
function callClaude(prompt: string): Promise<string | null> {
  return new Promise((resolve) => {
    const proc = spawn("claude", ["-p", "--output-format", "json", prompt]);
    let stdout = "";
    proc.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    proc.on("close", (code) => {
      if (code !== 0) { resolve(null); return; }
      const json = JSON.parse(stdout);
      resolve(json.is_error ? null : json.result?.trim() ?? null);
    });
  });
}
```

実はこの記事を書いている時点で気づいたのだが、最初のコードは `--output-format json` を使っていなかった。Claude Codeに「Claude CLIをサブプロセスで呼べるようにして」と指示したら、`-p` だけでプレーンテキストを受け取り、正規表現でJSONを抽出するコードが生成された。動くには動くが、エラー判定がexit codeだけに依存していた。

Claude Codeに詳細に指示しないと、こういう「動くけど最善ではない」コードが出てくる。AIに任せきりにせず、自分でCLIのオプションを確認して直した。この手の見直しは、AIと開発する上で常に必要になる。

**この設計の利点：**

1. **APIキー不要** — Claude Codeの認証をそのまま使う。ユーザーの追加設定ゼロ
2. **別途API契約が不要** — Claude Codeの利用料にすべて含まれる
3. **依存ゼロ** — AIライブラリ（LangChain等）が不要。`commander` + `sql.js` + `fast-xml-parser` の3つだけ
4. **プロンプトが全部見える** — ソースコード上のプロンプト文字列がそのまま使われる。ブラックボックスがない

## 3段階のパーソナライズ

Feed Curatorの核心は、使うほど精度が上がるパーソナライズの仕組みにある。

### 第1層：タグ統計プロファイル

キュレーション済み記事の既読率をタグごとに集計し、30日半減期の時間減衰を適用する。

```
Preferred tags (high read rate):
  agents: 85% read (17/20)
  security: 78% read (14/18)
Ignored tags (low read rate):
  enterprise: 12% read (2/17)
```

「最近よく読むトピック」と「一貫してスキップするトピック」が定量的に見える。

### 第2層：セマンティック嗜好メモ

タグ統計だけでは「なぜ読んだか」がわからない。そこで、直近90日の既読・スキップ履歴（最大100件）をClaudeに渡し、意味的なパターンを3-7行のメモに要約させる。

```
- 実装コード付きのハンズオンチュートリアルを好む（概念説明のみの記事はスキップ傾向）
- エッジデバイスでのローカルLLM推論に強い関心
- エンタープライズ向け導入事例や料金比較記事は一貫して読まない
- 最近、MCPプロトコル関連の記事を集中的に読んでいる
```

このメモはタグの羅列ではなく、「なぜその記事を読んだか」という意味レベルのパターンを捉える。

### 第3層：キュレーションへの注入

第1層と第2層の情報はキュレーションプロンプトに自動注入される。Claudeはスコアリング時に「この人はハンズオン記事を好み、エンタープライズ記事を読まない」という文脈を持った上で判断する。

**鮮度管理も自動：** メモは24時間経過かつ新規アクション20件以上で自動再生成される。趣味が変わっても追従する。

## トークン消費：何をどれだけ送っているか

「AIにRSS記事を送る」と聞くと、全文を丸ごと投げているように聞こえるかもしれない。実際には情報量をかなり絞っている。

### キュレーション（1日あたり最大5回呼び出し）

記事の全文は送らない。各記事から**先頭500文字＋末尾300文字**だけを切り出す。記事10件を1バッチとし、最大50件（5バッチ）を処理する。

```
1バッチあたりの入力:
  プロンプト本文     : ~200トークン
  ユーザープロファイル: ~100-300トークン（嗜好メモ含む）
  記事10件 × ~800文字: ~4,000-6,000トークン
  合計               : ~5,000-7,000トークン
```

出力はJSON配列（スコア・要約・タグ）で、1バッチあたり約1,000-2,000トークン。

### ブリーフィング生成（1日1回）

全文は送らない。キュレーション済みの**タイトル・スコア・要約・タグ**だけを送る。記事本文は含まれない。

```
入力:
  プロンプト本文     : ~200トークン
  ユーザープロファイル: ~100-300トークン
  記事メタデータ最大30件: ~2,000-3,000トークン
  合計               : ~3,000-4,000トークン
```

### 嗜好メモ生成（24時間ごと、条件付き）

直近90日の既読・スキップ履歴（最大100件）のタイトル・要約・タグ・スコア・アクションを送る。全文は含まない。

```
入力: ~3,000-5,000トークン
出力: ~200トークン（3-7行の箇条書き）
```

### 合計の目安

フィード8件・1日あたり新着30件の環境で、**1日の総トークン消費は約2万-4万トークン**程度。ただしClaude Code CLIの `-p` モードでも内部的なオーバーヘッドがあるため、実際の消費量はこれより多くなる。それでも記事の全文をそのまま送るアプローチと比較すると、桁が1つ少ない。

## 実際の使い方

### セットアップ（1分）

```
# インストール＆起動
npx feed-curator serve

# ブラウザで http://localhost:3000 を開く
# 言語を選択 → トピックでフィード検索 → Update
```

もっと手軽に始めるなら：

```
# 開発者向けフィード12件を一括登録
npx feed-curator init --starter

# 取得 → キュレーション → ブリーフィング → Web UI を一括起動
npx feed-curator start
```

RSSリーダーの最初のハードルは「どのフィードを登録すればいいかわからない」ことだ。Feed CuratorのWeb UIには、トピックベースのフィード検索機能がある。

「AI」「Rust」「セキュリティ」などキーワードを入力すると、Claudeがそのトピックに関連するRSSフィードを検索・推薦してくれる。OPMLのインポートやURLの手入力は不要で、興味のある分野を伝えるだけでフィードが揃う。

推薦されたフィードはチェックボックスで選んで一括登録できる。すでに登録済みのフィードは自動で除外されるので、重複を気にする必要もない。「何を読めばいいかわからないが、この分野には興味がある」という状態から始められるのが、従来のRSSリーダーとの大きな違いだ。

### 日常の流れ

1. 朝、`feed-curator start` を実行（またはWeb UIの「Update」ボタン）
2. ブリーフィングビューでトピック別の要約を確認
3. 気になる記事を開いて読む / 興味がなければスキップ
4. その既読・スキップの履歴が次回のスコアリングに反映される

**使い続けるほど「自分向けの技術朝刊」になっていく。**

注意点として、キュレーションには時間がかかる。記事1バッチ（10件）あたりClaude CLIの呼び出しが1回走るので、新着30件なら3回の呼び出しで数分程度。フィードの取得自体もネットワーク越しに順次行うため、フィード数が多いほど待ち時間が増える。Web UIではSSEで進捗をリアルタイム表示するので、裏で動かしておいて完了を待つ運用になる。

### ダイジェストの公開

```
# 今日のブリーフィングをMarkdownで出力
feed-curator digest

# ファイルに保存
feed-curator digest --output output/digest-2026-04-02.md
```

実際に生成されたダイジェストの一部：

```
## ローカルモデル・量子化の最前線

Gemma 3nの2GB VRAMマルチモーダル対応、IntelのAutoRound高精度量子化、
1.58bit Falcon-Edgeなど、手元デバイスで動かせるモデルの実用性が急速に向上している。

- [Gemma 3n fully available in the open-source ecosystem!](...) — Score: 88
- [Falcon-Edge: A series of powerful, universal, fine-tunable 1.58bit...](...) — Score: 82
- [Introducing AutoRound: Intel's Advanced Quantization...](...) — Score: 85

---

*Generated by [Feed Curator](https://github.com/rizumita/feed-curator)*
```

ブログや社内Slackに貼れば、ツールの説明なしに価値が伝わる。

## Web UI

2カラムレイアウトのWeb UIで、ブリーフィング・記事一覧・フィード管理ができる。

![ブリーフィングビュー](https://raw.githubusercontent.com/rizumita/feed-curator/main/docs/screenshots/briefing-view.png)

**特徴：**

* ティア別グルーピング（Must Read / Recommended / Worth a Look / Low Priority）
* スコアリング（円形プログレス表示）
* カテゴリ・タグ・既読状態のフィルタ
* ダーク/ライト/自動テーマ
* SSEベースのリアルタイム進捗表示

## 技術スタック

意図的にシンプルに保っている。

| 役割 | 技術 |
| --- | --- |
| ランタイム | Node.js 20+ / Bun |
| 言語 | TypeScript (ESM) |
| DB | SQLite (sql.js / Bunでは `bun:sqlite`) |
| CLI | Commander.js |
| RSS解析 | fast-xml-parser |
| AI | Claude Code CLI サブプロセス |
| テスト | Vitest + fast-check (PBT) |
| ビルド | tsup (npm) / `bun build --compile` (スタンドアロンバイナリ) |
| デスクトップ | Tauri 2 (Rust) |

**フロントエンドフレームワークなし。** HTMLはサーバーサイドで文字列として生成し、クライアント側はVanilla JSのみ。デスクトップアプリでもこの構成はそのままで、TauriのWebViewがlocalhostに接続する形をとっている。

## Claude Codeとの開発プロセス

Feed Curatorはほぼ全てのコードをClaude Codeで生成した。ただし「生成して終わり」ではない。機能を1つ追加するたびに、以下のサイクルを回している。

### 1. 生成 → リファクタリング

Claude Codeが生成するコードはそのまま動くことが多いが、冗長だったり、既存コードとスタイルが揃っていなかったりする。機能が動いた直後にリファクタリングをかけ、コードの一貫性を保つ。

### 2. テスト設計

手書きのユニットテストに加え、Property-Based Testing（fast-check）で境界条件を網羅する。PBTはClaude Codeが見落としがちな入力パターンを自動生成してくれるので相性がいい。

```
test("formatProfile never produces NaN or Infinity", () => {
  fc.assert(
    fc.property(
      fc.record({
        totalCurated: fc.nat(),
        totalRead: fc.nat(),
        overallReadRate: fc.float({ min: 0, max: 1, noNaN: true }),
        preferredTags: fc.array(/* ... */),
        // ...全フィールドをランダム生成
      }),
      (profile) => {
        const formatted = formatProfile(profile);
        const prompt = profileForPrompt(profile);
        expect(formatted).not.toContain("NaN");
        expect(prompt).not.toContain("NaN");
      }
    )
  );
});
```

実際にPBTから発見されたバグ：既読率の計算でゼロ除算が発生し、NaNがプロファイルプロンプトに混入するケースがあった。キュレーション時にClaudeが「スコア: NaN」という壊れた文脈を受け取ることになる。手書きのテストでは見つけにくいエッジケースだった。

### 3. コードレビュー

最後に、変更差分に対してClaude Codeでクリティカルレビューを実行する。依存グラフの分析、テストカバレッジの確認、セキュリティ観点のチェックを含む構造化されたレビューだ。

例えば今回の `digest` コマンド追加時、レビューで以下が見つかった：

* **Markdownインジェクション** — RSS記事のタイトルに `[` `]` が含まれるとリンク構文が壊れる → エスケープ処理を追加
* **エラーハンドリング不足** — `loadStarterFeeds` がファイル不在時にスタックトレースを出す → try/catchとバリデーションを追加
* **変数参照バグ** — リファクタリング時に `feeds` → `json.feeds` の変更漏れ → テストで即発覚

レビューなしで出していたら、ユーザーが `init --file` に壊れたJSONを渡した時点でクラッシュしていた。

### このサイクルの効果

v0.4.1時点でテストは561件。生成コードの品質を人間が担保するのではなく、**生成 → リファクタリング → テスト設計 → レビュー**のパイプラインで構造的に担保している。Claude Codeは書くのは速いが、自分が書いたコードの問題を自分で見つけるのは苦手だ。だからこそ、生成と検証を分離することに意味がある。

ただし、これは全部Claude Codeのプロンプトで手動実行している。CI/CDパイプラインに組み込んだり、カスタムハーネスでAI生成コードを自動検証するような仕組みは作っていない。小さいプロダクトにはそこまで要らない。「機能を足したらレビューとテストを回す」を愚直にやるだけで、十分品質は保てている。

## 設計の小ネタ

### 先頭500文字＋末尾300文字

キュレーション時、記事の全文は送らない。各記事から先頭500文字と末尾300文字だけを切り出してClaudeに渡す。

なぜ先頭800文字ではないのか。技術記事は冒頭に「何の話か」、末尾に「結論・まとめ」がある。中間は詳細な説明や手順で、スコアリングの判断材料としては冒頭と末尾で十分だ。これでトークン消費を抑えつつ、記事の要旨を捉えられる。

```
const head = content.slice(0, 500);
const tail = content.length > 800 ? content.slice(-300) : "";
```

800文字以下の短い記事ではtailを切り出さない。短い記事のheadとtailが重複するのを防ぐためだ。

### ブリーフィング選定：スコア×鮮度のブレンド

ブリーフィングに載せる記事は、キュレーションスコアだけでは選ばない。`0.7×スコア + 0.3×鮮度` のブレンドスコアで選定する。

```
const freshness = Math.max(0, 1 - age / (14 * 24 * 60 * 60 * 1000));
const blended = 0.7 * score + 0.3 * freshness;
```

14日で鮮度がゼロになる設計。これがないと、高スコアだが1週間前の記事がブリーフィングを占有してしまう。逆にスコアが低くても昨日出たばかりの記事が拾われる余地が生まれる。

### その他の設計判断

* **sql.js（Wasm版SQLite）** — ネイティブバインディング不要で `npx` 一発起動を実現
* **フレームワークなしのWeb UI** — HTMLはサーバーサイドで文字列生成、クライアントはVanilla JS。配布サイズと依存の少なさを優先
* **WebSocketではなくSSE** — キュレーション進捗は一方向通知だけなので、双方向通信は不要

## CLIからデスクトップアプリへ：SaaSが要らなくなる構造

記事の公開後、Feed CuratorはBunとTauriでデスクトップアプリ化した。

### アーキテクチャ

`bun build --compile` でCLIをシングルバイナリにし、Tauri 2のサイドカー（`externalBin`）として同梱する。起動するとTauriがバイナリを子プロセスで立ち上げ、WebViewがlocalhostに接続する。Web UIの書き直しはゼロだ。Bun環境では `bun:sqlite` をネイティブに使うため、sql.js（Wasm）も不要になった。

```
[Tauri (Rust)] → spawn → [feed-curator バイナリ (Bun)] → localhost:3200
                                                              ↑
                          [WebView] ─────── HTTP ────────────┘
```

Claudeの検出とセットアップもTauri側でハンドリングしている。Claude Code CLIが未インストールならインストール手順を案内し、未ログインならログインを促す。ユーザーがやることは「アプリを開く」だけだ。

### Inoreaderに払っていたものは何だったか

Inoreaderを解約した時点では、まだCLIだった。`npx feed-curator start` を毎朝ターミナルで打つ。動くには動くが、SaaSの「開くだけで使える」体験には届かない。

デスクトップアプリにしたことで、その差がなくなった。アイコンをクリックすれば朝刊が出る。データは全てローカルのSQLite。アカウント登録もサーバーもない。月額課金もない。

振り返ると、Inoreaderに月額を払っていたのは「フィードの取得・整理・表示」という機能に対してではない。**「自分で作るのが面倒」だから払っていた**のだ。フィードの取得はRSSパーサー、整理はSQLite、表示はHTML——どれも枯れた技術の組み合わせに過ぎない。AIキュレーションだけがClaude Codeに依存しているが、それもAPIキー不要で追加コストゼロだ。

AIがコードを書く時代に、「自分で作るのが面倒」というSaaSの存在意義は足元から崩れつつある。もちろんすべてのSaaSがそうではない。マルチデバイス同期、チームコラボレーション、大規模データ処理——サーバーサイドに本質的な価値があるサービスは残る。だが「ローカルで完結する個人ツール」のカテゴリにおいては、Claude Codeがコードを書いてくれる前提なら、SaaSを自前で置き換えるハードルは劇的に下がっている。Feed Curatorの本体は約3,000行のTypeScriptだが、すべてClaude Codeが生成したコードだ。

## 今後

ロードマップは[GitHub Issues](https://github.com/rizumita/feed-curator/issues)で公開している。

**近い将来：**

* 明示的フィードバック（like/dislike）の追加
* クロスフィード重複検出
* 2段階キュレーション（高速パス＋精密リランク）

**実現済み：**

* スタンドアロンバイナリ配布（Bun compile）
* デスクトップアプリ（Tauri 2）

**検討中：**

* MCPサーバー対応（Claude DesktopやClaude Codeから直接利用）
* Homebrew tap / パッケージマネージャ経由の配布

## まとめ

Feed Curatorは「Claude Codeを持っている開発者が、追加の契約なしで、自分専用の技術朝刊を手に入れる」ツールだ。

CLIなら `npx feed-curator serve` で即座に始められる。デスクトップアプリならアイコンを開くだけだ。APIキーの設定もAIライブラリのインストールもない。使い続けるほど、既読・スキップの履歴からあなたの関心を学習し、精度が上がっていく。

RSSリーダーに月額を払っていた理由が「自分で作るのが面倒だから」だったなら、その前提はもう変わった。

興味があればぜひ試してほしい。

<https://github.com/rizumita/feed-curator>

Star / Issue / PR 歓迎。
