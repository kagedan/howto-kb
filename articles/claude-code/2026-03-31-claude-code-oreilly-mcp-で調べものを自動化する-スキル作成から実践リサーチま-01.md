---
id: "2026-03-31-claude-code-oreilly-mcp-で調べものを自動化する-スキル作成から実践リサーチま-01"
title: "Claude Code + O'Reilly MCP で「調べもの」を自動化する ― スキル作成から実践リサーチまで"
url: "https://zenn.dev/wfukatsu/articles/00ea00a531197b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

技術書を調べるとき、O'Reilly Learning のサイトを開いて検索し、目次を眺め、レビューを読み、要点をメモする。このルーティンを Claude Code の MCP（Model Context Protocol）連携とスキル機能で自動化してみた。本記事では、セットアップから実際のリサーチ成果物を得るまでの一連の流れを紹介する。

---

## この記事で扱うこと

1. O'Reilly Learning MCP サーバーの導入と接続
2. Claude Code スキル（`.claude/skills/`）の設計と作成
3. 実際のリサーチワークフロー：書籍検索 → 深掘り → 知見の統合

---

## 1. O'Reilly MCP サーバーのセットアップ

### MCP とは

MCP（Model Context Protocol）は、Claude のような LLM が外部サービスのツールを呼び出すための標準プロトコルだ。MCP サーバーを接続すると、Claude Code から直接そのサービスの機能を「ツール」として使えるようになる。

O'Reilly は公式の MCP サーバーを提供しており、O'Reilly Learning プラットフォームのコンテンツ検索を Claude Code から実行できる。

### 接続方法

Claude Code の MCP 設定画面（`/mcp` コマンド）から O'Reilly の MCP サーバーを追加する。接続が完了すると、以下のようなツールが使えるようになる。

```
mcp__oreilly__search-oreilly-content
```

このツールは O'Reilly Learning プラットフォームに対するキーワード検索を実行し、書籍・動画・コース・ライブイベントなどのメタデータを返す。

### 利用できる検索パラメータ

| パラメータ | 説明 |
| --- | --- |
| `query` | 検索キーワード（質問形式ではなく、説明的なキーワードを使う） |
| `content_types` | コンテンツ種別のフィルタ（`books`, `videos`, `courses`, `articles`, `interactive`, `live-events` など） |
| `author_filter` | 著者名でフィルタ |
| `publisher_filter` | 出版社名でフィルタ |
| `languages` | 言語フィルタ（`en`, `ja` など。デフォルトは英語） |
| `order_by` | 並び順（`relevance`, `popularity`, `rating`, `date_added`, `date_published`） |
| `n_items` | 返却件数（デフォルト5） |

**注意点として**、著者や出版社を検索したいときは `query` に含めるのではなく、専用のフィルタパラメータを使う。また、クエリにブール演算子（AND, OR, NOT）は使えない。

---

## 2. Claude Code スキルの設計と作成

### スキルとは

Claude Code の「スキル」は、`.claude/skills/` ディレクトリに置く Markdown ファイルだ。特定のタスクに対する振る舞いの指示書として機能し、Claude Code がそのタスクに直面したときに参照するガイドラインとなる。

スキルには以下のような要素を記述する。

* **トリガー条件**: どんなリクエストでこのスキルが発動するか
* **ワークフロー**: 処理の流れ（フェーズごとに分割）
* **ベストプラクティス**: ツールの使い方のコツや注意事項
* **出力フォーマット**: 結果をどう整形して提示するか

### O'Reilly リサーチスキルの設計

今回作成したスキルは `.claude/skills/oreilly-research.md` に配置した。全体は5つのフェーズで構成している。

```
Phase 1: 検索意図の把握
  ↓
Phase 2: 検索実行（MCP ツール呼び出し）
  ↓
Phase 3: 結果の整理と提示
  ↓
Phase 4: 深掘り（オプション / WebFetch・Playwright 連携）
  ↓
Phase 5: リサーチまとめ（オプション）
```

#### Phase 1: 検索意図の把握

ユーザーのリクエストを分析し、以下の6つの軸に分解する。

1. **検索キーワード** — 意図を的確にキーワード化
2. **コンテンツタイプ** — 書籍、動画、コースなど
3. **著者フィルタ** — 特定著者がいればフィルタで指定
4. **出版社フィルタ** — 特定出版社がいればフィルタで指定
5. **言語** — 日本語か英語か
6. **並び順** — 人気順、評価順、新着順など

ポイントは、著者名や出版社名を検索クエリに含めないこと。MCP ツールの仕様上、専用のフィルタパラメータを使うほうが精度が高い。

#### Phase 2: 検索実行

`mcp__oreilly__search-oreilly-content` を呼び出す。ここでのベストプラクティスをスキルに明記しておく。

```
**検索のベストプラクティス:**
- クエリにブール演算子（AND, OR, NOT）は使わない
- 著者・出版社は必ずフィルタパラメータで指定し、クエリには含めない
- 特に指定がなければ n_items: 5 で十分
- ライブイベントの publication_date はイベント日時ではない
```

こうした注意点をスキルに書いておくことで、Claude Code が毎回正しいパラメータの使い方をする。

#### Phase 3: 結果の整理と提示

検索結果を構造化して見やすく提示する。出力フォーマットをスキルに定義しておくと、毎回一貫した形式で結果が返ってくる。

#### Phase 4: 深掘り

特定の書籍をさらに調べたいとき、WebFetch や Playwright を使って O'Reilly のコンテンツページにアクセスし、目次や章構成を取得する。

実際にやってみると、WebFetch だけでは取得できない情報（目次の「Show More」ボタンの先にある章リストなど）があった。そこで Playwright MCP を併用してブラウザ操作を行い、完全な目次を取得した。このように、複数の MCP を組み合わせると対応範囲が広がる。

#### Phase 5: リサーチまとめ

複数の検索・深掘りを経て、テーマごとの推奨リソースリストや学習パスを提案する。

### スキルファイルの実体

スキルは通常の Markdown で書く。特別な構文やメタデータは不要で、Claude Code が自然言語として読み取れる形式であればよい。ファイルの配置場所は以下の通り。

```
プロジェクトルート/
└── .claude/
    └── skills/
        └── oreilly-research.md
```

---

## 3. 実践: エディトリアルデザインのリサーチ

スキルの動作検証を兼ねて、「プレゼンテーションスライドのデザイン原則」をテーマにリサーチを行った。

### Step 1: 書籍検索

まず「editorial design typography layout」で英語書籍を検索した。

```
検索条件:
  query: "editorial design typography layout"
  content_types: ["books"]
  n_items: 5
```

5冊がヒットし、その中に Caldwell & Zappaterra 著『Editorial Design』（Laurence King, 2014）を発見した。同時に日本語（`languages: ["ja"]`）でも検索したが、該当なし。O'Reilly プラットフォーム上では日本語のデザイン関連コンテンツは限られることがわかった。

### Step 2: 書籍の深掘り

『Editorial Design』の詳細ページから目次を取得した。

WebFetch でアクセスすると、リダイレクト（`learning.oreilly.com` → `www.oreilly.com`）が発生し、さらに目次は5章分までしか表示されなかった。Playwright で「Show More」ボタンをクリックし、全7章 + 付録の完全な構成を把握した。

```
Chapter 1. Editorial design
Chapter 2. Editorial formats
Chapter 3. Covers
Chapter 4. Inside the publication
Chapter 5. Creating layouts
Chapter 6. Editorial design skills
Chapter 7. Looking back, looking forward
+ The evolution of the printed page / Further reading / Index
```

### Step 3: テーマ展開 ― プレゼンスライドへの応用

エディトリアルデザインの知見を「プレゼンテーションスライド」に応用するため、追加でプレゼンデザインの定番書を検索した。

```
検索条件:
  query: "presentation zen slide design Nancy Duarte"
  content_types: ["books"]
  n_items: 10
```

Nancy Duarte『slide:ology』（O'Reilly, 2008）、Garr Reynolds『Presentation Zen』シリーズなど、プレゼンデザインの主要文献を網羅的に発見できた。

### Step 4: 複数文献の統合

O'Reilly MCP での検索に加え、Tavily（Web 検索 MCP）を併用して書評やサマリー記事も収集。複数の文献から得た知見を統合し、「プレゼンテーションスライドデザインの原則」として体系化した。

最終的な成果物には、以下のような観点を含めた（各書籍の内容を筆者の言葉で要約・再構成したもの）。

* **根本思想**: Duarte のプレゼンテーション哲学と Reynolds の禅的アプローチ
* **スライド設計の基本原則**: 1スライド1メッセージ、ビジュアルヒエラルキー、グリッドシステム
* **タイポグラフィ**: フォント選定、テキスト配置のルール
* **色彩**: カラーパレットの制限、コントラストの活用
* **画像・データ**: 三分割法、装飾的要素の排除
* **構成**: エディトリアルデザインの原則をスライドに応用する方法

---

## 4. 著作権への配慮

本記事および成果物の作成にあたっては、以下の点に配慮した。

* **書籍の内容をそのまま転載しない**: 各書籍から得た知見は、筆者自身の言葉で要約・再構成している
* **引用は最小限に**: 直接引用を行う場合は、出典を明記し、引用の範囲を必要最小限に留めた
* **出典の明示**: 参考にした書籍は著者名・書名・出版社・出版年を明記し、O'Reilly Learning 上のリンクを併記した
* **独自の体系化**: 複数の文献から得た知見を独自の視点で統合・再構成しており、特定の書籍の構成をそのまま再現するものではない

なお、O'Reilly Learning のコンテンツは有料サブスクリプションが必要です。

---

## 5. まとめ: MCP + スキルがもたらすリサーチ体験

### 従来のリサーチフロー

```
ブラウザで O'Reilly を開く
  → 検索キーワードを入力
  → 結果を目視で確認
  → 書籍ページを開いて目次を読む
  → 別タブでレビューを検索
  → メモアプリに手動で転記
  → 複数書籍の情報を自力で統合
```

### MCP + スキル活用後のフロー

```
Claude Code に「○○を調べて」と指示
  → スキルが検索意図を分解
  → MCP 経由で O'Reilly を検索（並列実行可能）
  → Playwright で目次を完全取得
  → Tavily で Web 上のレビュー・サマリーを補足収集
  → 複数文献の知見を統合して構造化された成果物を生成
```

手作業で数時間かかっていたリサーチが、対話を通じて段階的に深掘りしながら進められるようになった。特に「複数の文献を横断して知見を統合する」部分は、人手でやると最も時間がかかるところだが、ここが大幅に効率化される。

### 今後の展開

* **スキルの汎用化**: O'Reilly 以外の学術データベースや論文検索の MCP が登場すれば、同様のスキルパターンで横展開できる
* **ワークフローの連鎖**: リサーチ結果をそのままスライド生成スキルに渡し、プレゼン資料まで一気通貫で作る流れも実現可能
* **チーム共有**: `.claude/skills/` はリポジトリに含められるため、チームメンバー全員が同じリサーチスキルを使える

MCP はツールの接続口、スキルはその使い方の知恵。この2つを組み合わせることで、Claude Code は「指示を待つアシスタント」から「リサーチのやり方を知っているパートナー」に変わる。

---

## 参考文献

* Duarte, N. (2008). *slide:ology: The Art and Science of Creating Great Presentations*. O'Reilly Media.
* Reynolds, G. (2019). *Presentation Zen: Simple Ideas on Presentation Design and Delivery* (3rd ed.). New Riders.
* Reynolds, G. (2013). *Presentation Zen Design: Simple Design Principles and Techniques to Enhance Your Presentations* (2nd ed.). New Riders.
* Duarte, N. (2010). *Resonate: Present Visual Stories that Transform Audiences*. Wiley.
* Nussbaumer Knaflic, C. (2019). *Storytelling with Data: Let's Practice!* Wiley.
* Caldwell, C., & Zappaterra, Y. (2014). *Editorial Design: Digital and Print*. Laurence King.
