---
id: "2026-03-26-marionette-mcp-の-call-custom-extension-でstore-画像撮影-01"
title: "Marionette MCP の call_custom_extension で、Store 画像撮影や UI 検証を自動化しよう"
url: "https://zenn.dev/yumemi_inc/articles/20260326_marionette_mcp_call_custom_extension"
source: "zenn"
category: "claude-code"
tags: ["MCP", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

## はじめに

Flutter エンジニアの皆さん、普段の開発でどんな MCP を使っていますか？  
今回は僕イチ推しの Marionette MCP と、最近追加された `call_custom_extension` について紹介します！

## Marionette MCP とは

[LeanCode](https://leancode.co/) が開発している Flutter に特化した MCP です。

<https://pub.dev/packages/marionette_mcp>

Flutter 専用の MCP としては公式が出している [Dart and Flutter MCP server](https://docs.flutter.dev/ai/mcp-server) がありますが、あちらはエラーの取得やコードの分析など開発時の利用を想定しています。一方、Marionette MCP はボタンのタップやテキスト入力などランタイムでの操作に特化したものです。

どちらを選択するかではなく、併用するのがおすすめです。

---

以前 Flutter で使えるランタイムの操作に特化した MCP を比較したスライドがあるので、興味があればどうぞ

<https://k9i-0.github.io/flutter_deck_template/fluttergakkai_9/#/title>

実はこのスライドを flutter\_deck で作った時に、Marionette MCP で狙ったスライドへ遷移させるのが面倒だったのが `call_custom_extension` を [提案するきっかけ](https://github.com/leancodepl/marionette_mcp/issues/27)になりました。Issue を立ててプロトタイプを実装したところ、ベースに採用してもらえて[正式リリース](https://github.com/leancodepl/marionette_mcp/pull/30)に至っています。

## これまでのつらみ

まずは `call_custom_extension` 登場以前に大変だったシナリオを紹介します。

### 深い階層へのナビゲーション

こんな体験はありませんか？

Claude Code 等に実装させた画面の検証も AI に投げて優雅にランチをして帰宅。いざ PC を開いたらそもそも検証させたい画面に辿り着けてない🤪

人間にとっては直感的にたどり着ける画面でも、AI にとっては何度もツールの呼び出しをして初めてたどり着けるようなことがあります。  
ツールを呼び出しまくれば、当然トークン代も嵩みますね…

### スクショを撮らせようとしたら言語設定やテーマが間違ってた

似た問題ですが、ライトテーマ x 日本語でスクショを撮って欲しいのに間違ってたみたいなこともあるあるだと思います。  
あと、そういう設定ってちょっと導線が深くなりがちなので、AI が苦労します。

## `call_custom_extension` の紹介

`call_custom_extension` は先ほど挙げた課題を解決するものです！

ひとことで言うと、**Flutter アプリに独自の操作を定義して、AI エージェントから呼び出せるようにする仕組み**です。

Flutter の VM Service Extension を MCP 経由で公開する「エスケープハッチ」のようなもので、Marionette MCP のツールセットを小さく保ちつつ、アプリ固有の操作を柔軟に追加できます。

### 仕組み

`call_custom_extension` は 2 つの MCP ツールで構成されています。

| ツール | 役割 |
| --- | --- |
| `list_custom_extensions` | アプリが登録しているエクステンションの一覧を取得（ディスカバリー用） |
| `call_custom_extension` | 発見したエクステンションを実際に呼び出す |

AI エージェントはまず `list_custom_extensions` で何ができるかを把握し、必要に応じて `call_custom_extension` で実行する、という流れです。

### Flutter 側の実装

Flutter アプリ側では `registerMarionetteExtension()` を呼ぶだけでエクステンションを登録できます。

```
import 'package:marionette_flutter/marionette_flutter.dart';

registerMarionetteExtension(
  name: 'myApp.goToPage',
  description: 'Navigate to a specific page by name.',
  callback: (params) async {
    final page = params['page'];
    if (page == null) {
      return MarionetteExtensionResult.invalidParams(
        'Missing required parameter: page',
      );
    }

    // アプリ固有のナビゲーション処理
    navigateTo(page);

    return MarionetteExtensionResult.success({
      'page': page,
      'status': 'navigated',
    });
  },
);
```

ポイントは以下の通りです。

* `name`: エクステンション名。AI が呼び出す際の識別子になる
* `description`: エクステンションの説明。AI はこれを読んで使い方を判断する
* `callback`: 実際の処理。引数は `Map<String, String>` で受け取り、`MarionetteExtensionResult` を返す

戻り値には `success`, `error`, `invalidParams` の 3 種類があり、AI に結果をわかりやすく伝えられます。

### 初期化

`main()` で Marionette の初期化と一緒にエクステンションを登録します。

```
void main() {
  if (kDebugMode && !kIsWeb) {
    MarionetteBinding.ensureInitialized();
    registerMyExtensions(); // カスタムエクステンションの登録
  } else {
    WidgetsFlutterBinding.ensureInitialized();
  }
  // ...
}
```

`kDebugMode` でガードしているので、リリースビルドには一切影響しません。

## 活用事例：CC Pocket での Store スクショ自動撮影

ここからは、僕が個人開発している [CC Pocket](https://github.com/K9i-0/ccpocket) での活用事例を紹介します。

CC Pocket は mac 上の Claude Code / Codex をスマホから操作できるアプリです。

AI駆動開発を効率的に行うための検証も兼ねているので、MCP などを積極的に活用しています。

### 登録しているエクステンション

CC Pocket では以下の 5 つのエクステンションを [登録しています](https://github.com/K9i-0/ccpocket/blob/main/apps/mobile/lib/services/store_screenshot_extension.dart)。

| エクステンション名 | 説明 |
| --- | --- |
| `ccpocket.navigateToStoreScenario` | 指定した Store スクショ用シナリオへ直接遷移 |
| `ccpocket.popToRoot` | すべてのルートをポップしてホーム画面に戻る |
| `ccpocket.setTheme` | テーマ切替（light / dark / system） |
| `ccpocket.setLocale` | 言語切替（en / ja / zh） |
| `ccpocket.navigateToMockScenario` | モックシナリオの chat 画面へ直接遷移 |

実装例として `ccpocket.setTheme` を見てみましょう。

```
registerMarionetteExtension(
  name: 'ccpocket.setTheme',
  description:
      'Switch the app theme. '
      'Values: "light", "dark", "system".',
  callback: (params) async {
    final theme = params['theme'];
    if (theme == null || theme.isEmpty) {
      return MarionetteExtensionResult.invalidParams(
        'Missing required parameter: theme (light/dark/system)',
      );
    }

    final ctx = StoreScreenshotState.navigatorKey?.currentContext;
    if (ctx == null) {
      return MarionetteExtensionResult.error(1, 'Context not available.');
    }

    final mode = switch (theme.toLowerCase()) {
      'light' => ThemeMode.light,
      'dark' => ThemeMode.dark,
      'system' => ThemeMode.system,
      _ => null,
    };
    if (mode == null) {
      return MarionetteExtensionResult.invalidParams(
        'Invalid theme: $theme. Use light, dark, or system.',
      );
    }

    ctx.read<SettingsCubit>().setThemeMode(mode);
    return MarionetteExtensionResult.success({'theme': theme});
  },
);
```

設定画面を開く → テーマの項目を探す → タップする、という複数ステップが `call_custom_extension` 一発で済むようになります。

### Store スクショ撮影の自動化フロー

これらのエクステンションを組み合わせて、Claude Code の [スキル（`/update-store`）](https://github.com/K9i-0/ccpocket/blob/main/.claude/skills/update-store/SKILL.md)から Store スクショの撮影を完全に自動化しています。

流れはこんな感じです。

1. `ccpocket.setTheme` でライトテーマに設定
2. `ccpocket.setLocale` で言語を設定
3. `ccpocket.navigateToStoreScenario` でシナリオに遷移
4. 描画完了を待って `xcrun simctl io booted screenshot` でスクショ撮影
5. `ccpocket.popToRoot` でホーム画面に戻す
6. 3-5 を全シナリオ分繰り返す

以前は手動で各画面に遷移してスクショを撮っていましたが、今はコマンド一発で全シナリオ分のスクショが自動生成されます。

## LLM にうまく使ってもらうための Tips

`call_custom_extension` は登録するだけでは不十分で、AI が適切に使えるように工夫する必要があります。

### エクステンション名は明確に

`goToPage` のような汎用的な名前よりも、`ccpocket.navigateToStoreScenario` のようにアプリ名をプレフィックスにつけると、AI が何のエクステンションなのか迷わなくなります。

### スキルのプロンプトにエクステンションを明記する

`description` をしっかり書くことも大事ですが、それ以上に効果的なのは Claude Code のスキル等のプロンプトに「このタスクではこのエクステンションを使え」と明記することです。

ちなみに `description` 自体は AI にコードを書かせればいい感じに書いてくれるので、人間が頑張るポイントはそこではなかったりします。

## まとめ

試してみてね☝️
