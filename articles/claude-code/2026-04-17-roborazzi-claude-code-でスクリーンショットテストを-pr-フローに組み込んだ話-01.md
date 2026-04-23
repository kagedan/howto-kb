---
id: "2026-04-17-roborazzi-claude-code-でスクリーンショットテストを-pr-フローに組み込んだ話-01"
title: "Roborazzi + Claude Code でスクリーンショットテストを PR フローに組み込んだ話"
url: "https://zenn.dev/dely_jp/articles/c1a02f1a9d6412"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

クラシル社で Android エンジニアをしている satoyu です。

前回の記事では、Claude Code のカスタムスキル `/create-pr` に事前チェック（コードレビュー・Lint・Build）を組み込み、並列自動化した取り組みを紹介しました。

<https://zenn.dev/dely_jp/articles/471c06e0296056>

その記事の中で「スクリーンショットテストの自動比較を事前チェックに組み込む取り組みを進めています」と記載していました。本記事ではその取り組みについて紹介します。

Roborazzi を導入してスクリーンショットテストを構築し、Claude Code の `/create-pr` スキルに統合するまでの流れを紹介します。結果として、**224枚のスクリーンショットテストが、手書きのテストファイル0で動いています。**

## 課題: UI の変更レビューで何が起きていたか

自分たちのチームでは、以下の課題を抱えていました。

* **PR 作成時のスクリーンショット撮影が手間になっていた。** UI に差分がある場合、PR 作成者が手動でスクリーンショットを撮影し、description に貼り付ける運用をしていました。この作業が地味に負担で、省略されることもありました。
* **Preview 関数の整備が統一されていなかった。** これまで Preview 関数の実装にルールがなく、用意されている画面もあればない画面もある状態でした。今後 Preview を追加していく際に、手動でスクリーンショットを撮る手間をなくしたいという思いがありました。
* **Material 2 から Material 3 への移行に備えたかった。** プロジェクトでは Material 2 と Material 3 が混在しており、将来的に Material 3 へ統一する方針です。その移行時に、意図しない UI の変化を簡単に検知できる仕組みが必要でした。

## 技術選定: なぜ Roborazzi か

Android のスクリーンショットテストには複数の選択肢があります。

| ライブラリ | 実行環境 | @Preview からのテスト自動生成 | 特徴 |
| --- | --- | --- | --- |
| **Roborazzi** | Robolectric（JVM） | :white\_check\_mark: | `generateComposePreviewRobolectricTests` で @Preview を自動スキャン |
| Compose Preview Screenshot Testing | Gradle Plugin（JVM） | :white\_check\_mark: | Google 公式。2024年リリース |
| Paparazzi | Layoutlib（JVM） | :x: | Square 製。手動でテスト記述が必要 |

決め手は **`generateComposePreviewRobolectricTests`** です。この機能を有効にすると、指定パッケージ配下の `@Preview` 関数を自動的にスキャンし、それぞれに対応するスクリーンショットテストを生成します。個別にテストファイルを記述する必要がありません。

自分たちのチームでは、Preview 関数の整備状況にばらつきがありましたが、今後 Preview を拡充していく方針を固めていました。Roborazzi であれば、Preview を追加するたびにスクリーンショットテストも自動的に増えるため、Preview 整備とテスト拡充を同時に進められる点が大きな決め手となりました。

## 設計: screenshot-testing モジュールの構成

Roborazzi と Robolectric の依存を本体から隔離するため、専用の `screenshot-testing` モジュールを設けました。

```
screenshot-testing/
├── build.gradle                # Roborazzi の設定
└── screenshot/
    └── outputs/
        ├── base/               # ベースライン画像（~224枚、Git 管理）
        └── compare/            # verify 時の差分画像出力先
```

`compare/` の差分画像は `.gitignore` に追加しており、PR には含めません。ベースライン画像が更新されれば GitHub 上の差分で変更前後を確認できるため、比較画像を別途管理する必要はありません。

このモジュールが各 UI モジュール（`ui:base`, `ui:top` など）に依存し、それらのモジュール内にある `@Preview` 関数をスキャンします。`@Preview` 自体は各 UI モジュールの `/preview/` ディレクトリに配置する規約にしています。

```
ui/base/src/main/java/.../component/shared/button/
├── PrimaryButton.kt
├── SecondaryButton.kt
└── preview/
    └── ButtonPreview.kt    # @Preview をまとめて定義
```

## 実装: Roborazzi のセットアップ

### Gradle 設定

`screenshot-testing/build.gradle` の主要部分です。

```
apply plugin: libs.plugins.roborazzi.get().pluginId

android {
    testOptions {
        unitTests {
            includeAndroidResources = true
            all {
                systemProperty "robolectric.pixelCopyRenderMode", "hardware"
                systemProperty "roborazzi.output.dir",
                    file("screenshot/outputs/base").absolutePath
            }
        }
    }
}

roborazzi {
    generateComposePreviewRobolectricTests.enable.set(true)
    generateComposePreviewRobolectricTests.packages.add("com.kurashiru.usapo.ui")
    outputDir.set(file("screenshot/outputs/base"))
}
```

ポイントは2点です。

* **`generateComposePreviewRobolectricTests`**: `com.kurashiru.usapo.ui` パッケージ配下の `@Preview` 関数を自動スキャンし、テストを生成します
* **`pixelCopyRenderMode = "hardware"`**: ハードウェアレンダリングモードにより、より正確なスクリーンショットを取得します（Robolectric のネイティブグラフィックスモード）

Roborazzi が自動生成するテストクラスでは、`@Config(sdk = [33], qualifiers = RobolectricDeviceQualifiers.Pixel4a)` が適用され、Pixel 4a（SDK 33）をシミュレーションします。

### 2つの Gradle タスク

| タスク | 用途 |
| --- | --- |
| `./gradlew :screenshot-testing:recordRoborazziDebug` | ベースラインの記録・更新 |
| `./gradlew :screenshot-testing:verifyRoborazziDebug` | ベースラインとの比較検証 |

`record` で現在の状態をベースラインとして保存し、`verify` でベースラインとの差分を検出します。差分が検出された場合は `screenshot/outputs/compare/` にビジュアル差分画像が出力されます。

## Claude Code 統合: スクリーンショットエージェント

ここまでで Roborazzi 単体としてのセットアップは完了です。`record` でベースラインを撮り、`verify` で差分を検出できる状態になりました。次はこれを `/create-pr` の事前チェックに組み込み、PR 作成フローの中で自動実行されるようにします。

### エージェント定義

`.claude/agents/screenshot.md` として、スクリーンショット比較専用のエージェントを定義しています。

```
---
name: screenshot
description: スクリーンショット比較を実行してUI変更を検証する
tools: Bash, Read
model: haiku
---

# Screenshot Agent

あなたはスクリーンショット比較を実行する専門エージェントです。

## 実行手順

### 1. 親ブランチの検出
（git reflog から親ブランチを特定）

### 2. UI関連ファイルの変更確認
UI_CHANGES=$(git diff --name-only "$PARENT_BRANCH"...HEAD | grep -E '^ui/.*\.(kt|xml)$')

### 3. スクリーンショット比較の実行（UI変更がある場合のみ）
./gradlew :screenshot-testing:verifyRoborazziDebug --rerun-tasks

### 4. 結果の解析
- 終了コード 0: 差分なし（PASSED）
- 終了コード 非0: 差分あり（FAILED）
```

設計のポイントは **「UI ファイルの変更がなければスキップする」** というガード条件です。バックエンドのロジック変更のみの PR でスクリーンショット比較を実行する意味はありません。`ui/**/*.kt` や `ui/**/*.xml` の変更有無を先に確認し、変更がなければ即座に `SKIPPED` を返す仕組みです。

また、モデルには `haiku` を指定しています。このエージェントの役割は Gradle タスクの実行と結果の解析のみであるため、高性能なモデルは不要です。コスト効率の観点から軽量モデルで十分に対応できます。

### /create-pr への統合

前回の記事では「コードレビュー・Lint・Build」の3つだった並列チェックが、その後「設計原則レビュー（SOLID/DRY 等の観点）」を追加し、さらに今回の「スクリーンショット比較」を加えて5つに拡張されました。

![](https://static.zenn.studio/user-upload/b3899e6f5c1d-20260416.png)

エージェント定義としては `.claude/agents/screenshot.md` を1ファイル追加するのみですが、`/create-pr` スキル側では Agent の呼び出し追加に加えて、統合レポートへの Screenshot 行の追加も組み込んでいます。それでも、前回の記事で述べた「エージェント定義の Markdown 管理が容易」という利点はそのまま当てはまり、チェックの追加コストは低く抑えられました。

## 統合レポート: 5つのチェック結果

事前チェック完了後の統合レポートは、以下のような形式で出力されます。

```
# PR事前チェックレポート

## 実行サマリー

| チェック項目 | ステータス | 詳細 |
|-------------|-----------|------|
| 総合レビュー | ISSUES | must: 1, should: 2 |
| Detekt | PASSED | error: 0, warning: 0 |
| Android Lint | PASSED | error: 0, warning: 1 |
| Build | SUCCESS | - |
| Screenshot | FAILED | 差分: 3件 |

---

## スクリーンショット比較結果

### サマリー
- ステータス: FAILED
- 差分スクリーンショット: 3件

### 差分一覧
- ButtonPreview_PrimaryLightPreview.png
- ButtonPreview_PrimaryDarkPreview.png
- BadgePreview_SecondaryDarkPreview.png

### 確認方法
比較画像は `screenshot-testing/screenshot/outputs/compare/` に出力されています。
```

前回の記事のレポートに Screenshot の行が追加された形です。スクリーンショットエージェントは SKIPPED / PASSED / FAILED / TIMEOUT の4ステータスを返し、統合レポートに反映されます。

## 導入してみて

冒頭で挙げた3つの課題がどう変わったかを振り返ります。

**PR 作成時のスクリーンショット撮影の手間がなくなった。** `/create-pr` のフローにスクリーンショット比較が組み込まれたことで、PR 作成者が手動でスクリーンショットを撮影し description に貼り付ける作業が不要になりました。UI に差分があれば自動で検出され、ベースライン更新まで一連の流れで完結します。

**Preview 関数の整備が進むようになった。** 「Preview を追加すればスクリーンショットテストも自動的に増える」という仕組みがあることで、Preview を書くモチベーションが上がりました。これまでばらつきのあった Preview の整備状況が、徐々に改善されてきています。

**Material 3 移行の安全網が整った。** 224枚のスクリーンショットがベースラインとして管理されている状態になったため、Material 2 から Material 3 への移行時に意図しない UI の変化を検知できる体制が整いました。まだ移行作業自体はこれからですが、安心して着手できる状況です。

## まとめ

本記事では、Roborazzi を用いたスクリーンショットテストの導入から、Claude Code の `/create-pr` スキルへの統合までを紹介しました。

ポイントをまとめます。

* **Roborazzi の `generateComposePreviewRobolectricTests`** により、@Preview を記述するだけでスクリーンショットテストが自動生成される。現在224枚のスクリーンショットが手書きのテストファイル0で運用されている
* **Claude Code のエージェント**として `/create-pr` に統合し、他のチェックと並列実行される。UI ファイルの変更がない PR ではスキップされるため、不要なビルド時間を消費しない
* **UI ファイルの変更検知 → スクリーンショット比較 → ベースライン更新**まで、すべて `/create-pr` のフローの中で完結する。PR 作成者が手動でスクリーンショットを撮影する手間がなくなり、Material 3 移行時の安全網としても機能する

前回の記事で述べた「新しいチェックを追加するなら Markdown ファイル1つ追加するだけ」という設計方針を、今回の取り組みで実証できました。スクリーンショットテストの導入を検討されている方の参考になれば幸いです。
