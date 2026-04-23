---
id: "2026-04-07-figma-url-を渡すだけでデザインシステム準拠の-compose-コードが生成される仕組みを作-01"
title: "Figma URL を渡すだけでデザインシステム準拠の Compose コードが生成される仕組みを作った"
url: "https://zenn.dev/dely_jp/articles/2cc6637e4d0aad"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## はじめに

クラシルで Android エンジニアをしている go です。

「Figma の URL を渡すだけで Compose UI を実装できたら最高だな」と思い、Figma MCP Server を使った PoC 検証を行いました。結果として Figma MCP は強力ですが、**そのままではプロジェクト固有のデザインシステム（以下 KurashiruTheme）に準拠したコードが生成されない**という課題に直面しました。

Figma MCP の出力と Android のデザインシステムをマッピングする Claude Code ルールを作成することで、**Figma → KurashiruTheme 準拠の Compose コードの自動生成**を実現した経緯を紹介します。

## 課題: Figma MCP の出力をそのまま使うとデザインシステムに従ったコードが生成されない

ここでいう「デザインシステムに従っていない」とは、**見た目が崩れるという意味ではありません**。生成されたコードは Figma のデザイン通りに表示されますが、`Color(0xFF2D2D2D)` のようなハードコードされた値が使われるため、プロジェクトのテーマ（`KurashiruTheme`）経由での一括管理・変更追従ができなくなるという問題です。

### Figma MCP はなぜ React+Tailwind を返すのか

Figma MCP Server の [`get_design_context`](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) は、指定した Figma ノードのコード・スクリーンショット・メタデータを返してくれるツールです。

しかし、出力は常に **React+Tailwind 形式**です。Figma 公式ドキュメントの「[The server keeps returning web/react code](https://developers.figma.com/docs/figma-mcp-server/server-returning-web-code/)」に記載されている通り、これは LLM が Web ベースのデータで広く訓練されているため、この形式が最も効果的に解釈されるという設計判断によるものです。

`clientLanguages` や `clientFrameworks` パラメータも存在しますが、[ツールスキーマの description](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) に「This is used for logging purposes to understand which frameworks are being used」と明記されており、出力形式の切り替えには使用されません。

つまり、Jetpack Compose プロジェクトで Figma MCP を使う場合、**Claude Code が React+Tailwind の中間出力をプロジェクト固有のデザインシステムにマッピングしながら Compose コードに変換する**必要があります。

### MCP 出力をそのまま使った場合 vs デザインシステムにマッピングした場合

ここが記事の核心です。同じ Figma URL から UI を実装しても、**マッピングの有無で生成コードの品質が大きく変わります**。

#### そのまま使った場合（マッピングなし）

```
// Figma MCP の CSS 変数・hex 値をそのまま Kotlin に転写
Text(
    text = "タイトル",
    color = Color(0xFF2D2D2D),        // hex 直書き
    fontSize = 14.sp,                  // 直値 → テーマ変更に追従しない
    lineHeight = 20.sp,
    fontWeight = FontWeight.Bold
)

Box(
    modifier = Modifier
        .background(
            Color(0xFFF7F7F7),         // hex 直書き
            RoundedCornerShape(8.dp)   // dp 直書き
        )
)
```

ビルドは通りますが、以下の問題があります:

* **デザインシステムと断絶**: トークン名がないため、デザイン変更時に grep で追えない
* **手戻りが大きい**: 1画面あたり 10〜20 箇所のトークン手動置き換えで 20〜60 分の修正

#### デザインシステムにマッピングした場合

```
// KurashiruTheme のトークンを使用
Text(
    text = "タイトル",
    color = KurashiruTheme.color.core.contentDefaultPrimary,
    style = KurashiruTheme.typography.label.small,
)

Box(
    modifier = Modifier
        .background(
            KurashiruTheme.color.core.backgroundDefaultSecondary,
            KurashiruTheme.shape.roundedCorner.xSmall,
        )
)
```

* **デザインシステム準拠**: 変更時にトークン名で一括管理可能
* **手戻りゼロ**: 最初から正しいトークンが使われる

**この差分を自動で埋めるのが、今回作成したマッピングルールとスキルの役割です。**

## PoC 検証: Figma のデザイントークンとテーマの対応関係

ルールを書く前に、Figma 側のデザイントークンと KurashiruTheme がどの程度一致しているかを検証しました。Figma MCP の `get_variable_defs` で実際の画面で使われている Variable を取得し、テーマのプロパティと突き合わせました。

### カラー: 検証した全色が完全一致

Figma Variable のパス階層がテーマのプロパティパスと 1:1 で対応していました。

| Figma Variable パス | テーマプロパティ |
| --- | --- |
| `color/core/content/contentDefaultPrimary` | `KurashiruTheme.color.core.contentDefaultPrimary` |
| `color/core/background/backgroundDefaultSecondary` | `KurashiruTheme.color.core.backgroundDefaultSecondary` |
| `color/core/border/borderOpaque` | `KurashiruTheme.color.core.borderOpaque` |
| `color/core extensions/content/contentCritical` | `KurashiruTheme.color.coreExtensions.contentCritical` |

変換ルールはシンプルです:

* `color/core/<category>/<name>` → `KurashiruTheme.color.core.<name>`
* `color/core extensions/<category>/<name>` → `KurashiruTheme.color.coreExtensions.<name>`

### タイポグラフィ・シェイプ: 概ね対応可能

タイポグラフィは Figma Text Style 名とテーマの typography プロパティが対応しており、シェイプも定義済みの角丸値（4/8/16/24/48dp）はテーマトークンにマッピング可能でした。

一致率が高かったことで、**マッピングルールを書けばほぼ自動変換できる**という確信が得られました。

## 解決策: `.claude/rules/` にマッピングルールを定義

### なぜ ui モジュール内にルールを置くのか

Figma の公式ドキュメント「[Add custom rules and instructions](https://developers.figma.com/docs/figma-mcp-server/add-custom-rules/)」でも、プロジェクト固有のルール（デザイントークンの使い方、コンポーネント配置規則など）を定義することが推奨されています。

デザイントークンのマッピングは UI 実装時にしか必要ありません。Claude Code はモジュール配下の `CLAUDE.md` をそのモジュールのコンテキストとして読み込むため、**ui モジュール内にルールを配置**することで、data 層やテスト編集時に不要なコンテキストが読み込まれることを防げます。

### ルールファイルの構造

`ui/` モジュール内にルールファイルを作成し、以下を定義しました:

```
ルールファイルの構成:
├── 1. ワークフロー
│     get_design_context → get_variable_defs → マッピング変換 → Compose コード生成
├── 2. カラーマッピング
│     Figma Variable パス → テーマカラープロパティの変換ルール
│     + Hex → ColorSpectrum の fallback 表（全25色）
├── 3. タイポグラフィマッピング
│     Figma Text Style → テーマ typography プロパティの対応表
├── 4. シェイプマッピング
│     Figma 角丸値 → テーマ shape プロパティの対応表
└── 5. テーマファイルの場所
      テーマ関連ソースファイルのパス一覧
```

ポイントは **ワークフローの先頭で `get_variable_defs` を明示的に呼ばせる**ことです。`get_design_context` だけでは CSS 変数名（`var(--color/core/...)`) しか取得できず、Variable のフルパスが得られないため、マッピング精度が下がります。

### Hex fallback

Variable が設定されていないコンポーネントのために、Hex → ColorSpectrum の対応表（全 25 色）も用意しました。ただし `#F7F7F7`(Gray0) と `#F0F0F0`(Gray50) のような近いグレー系は誤変換されることがあり、Variable 変換と比べると精度は落ちます。

## Figma 自動マッピングスキルの作成

ルールファイルだけでも効果はありますが、さらに**スキル化**することで、Figma URL を渡すだけの一発実行を実現しました。

スキルでは以下のワークフローを自動化しています:

```
1. Figma URL を受け取る
2. get_design_context でスクリーンショット・CSS変数を取得
3. get_variable_defs で Figma Variable（カラートークン）を取得
4. .claude/rules/figma-design-system.md のマッピング表に従いトークン変換
5. KurashiruTheme 準拠の Jetpack Compose コードを生成
```

ルールファイルがマッピング表（データ）を担い、スキルがワークフロー（手順）を担う、という役割分担です。

## 導入結果

| 観点 | MCP出力をそのまま使用 | デザインシステムにマッピング |
| --- | --- | --- |
| カラー | `Color(0xFF2D2D2D)` | `KurashiruTheme.color.core.contentDefaultPrimary` |
| タイポグラフィ | `fontSize = 14.sp` 直値 | `KurashiruTheme.typography.label.small` |
| シェイプ | `RoundedCornerShape(8.dp)` | `KurashiruTheme.shape.roundedCorner.xSmall` |
| デザイン変更への追従 | 全箇所手動修正 | トークン経由で自動追従 |

## 前提: この仕組みが機能するために必要なこと

自動マッピングの精度は、Figma と Android 双方のデザインシステム整備度に依存します。

### 1. Figma 側: コンポーネントに Variable を設定する

`get_variable_defs` は、Figma のインスペクトパネルで確認できる Variable（バリアブル）を取得するツールです。つまり、**デザイナーがコンポーネントのカラー等に Variable を適用していなければ、このツールは何も返しません**。

Variable が未設定の場合、マッピングは hex 値からの推測（fallback）に頼ることになり、`#F7F7F7` と `#F0F0F0` のような近似色の判別ができず精度が落ちます。**Figma 側で全カラーに Variable を設定しておくことが、マッピング精度を最も大きく左右する要素**です。

### 2. Android 側: Figma の Variable 体系と対応するテーマを実装する

Figma Variable のパス（例: `color/core/content/contentDefaultPrimary`）と Android テーマのプロパティ（例: `KurashiruTheme.color.core.contentDefaultPrimary`）が 1:1 で対応している必要があります。命名体系が揃っていればマッピングルールはシンプルになり、ずれていれば個別の変換テーブルが必要になります。

### デザイナーとエンジニアの連携が鍵

この仕組みは、デザイナーが Figma で Variable を整備し、エンジニアがそれと対応するテーマを Android に実装するという**両者の連携があって初めて成立**します。どちらか一方が欠けると hex fallback に頼ることになり、自動マッピングの恩恵が薄れます。

## まとめ

Figma MCP Server は[設計上の理由](https://developers.figma.com/docs/figma-mcp-server/server-returning-web-code/)で React+Tailwind 形式のコードを返します。Jetpack Compose プロジェクトでは、この出力を**そのまま使う**か**デザインシステムにマッピングする**かで、生成コードの品質に大きな差が出ます。

`.claude/rules/` にデザイントークンのマッピングルールを定義し、それを活用するスキルを作成することで、**Figma URL を渡すだけで KurashiruTheme 準拠の Compose コードが自動生成される仕組み**を実現しました。

同じアプローチを始める場合:

1. `get_variable_defs` で Figma のデザイントークンを取得し、自社テーマとの対応関係を洗い出す
2. `.claude/rules/` にマッピングルールを定義し、`paths` で UI ファイルのみに適用
3. スキル化してワークフローを自動化
4. 数画面で検証し、精度が安定したらチームに展開

**AI にデザインシステムの「翻訳辞書」を持たせることが、Figma → Compose 変換の精度を決めます。**
