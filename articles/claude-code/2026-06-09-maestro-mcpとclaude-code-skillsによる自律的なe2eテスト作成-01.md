---
id: "2026-06-09-maestro-mcpとclaude-code-skillsによる自律的なe2eテスト作成-01"
title: "Maestro MCPとClaude Code Skillsによる自律的なE2Eテスト作成"
url: "https://zenn.dev/flierinc/articles/fcf32bfa82524e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "zenn"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

モバイルアプリ開発におけるE2Eテストは、テストシナリオの作成やメンテナンスにコストがかかるため、十分な数のテストシナリオを整備・維持するのが難しいという課題があります。私自身も業務でMaestroを利用していますが、一部の主要なテストシナリオに絞った運用にとどまっていました。

そこで、Maestro MCPサーバとAIエージェントを組み合わせることでE2Eテストの作成・運用の一部を自動化できるのではないかと考え、公式のskill-creatorを使ってClaude Code Skillsを作成し、試してみました。

実際に試してみると、テストシナリオの生成だけでなく、テストの実行や失敗時の修正まで含めてなかなか良い体験だったため、汎用的に利用できる形へ整理してOSSとして公開しました。

<https://github.com/asmz/asmz-agent-plugins>

この記事では、MaestroおよびMaestro MCPの概要を説明した上で、今回公開したSkillの特徴や実際のワークフローを紹介します。

## Maestro MCPで何ができるのか

### Maestroとは

Maestroはモバイルアプリ向けのE2Eテストフレームワークです。

<https://maestro.dev/>

YAML形式で宣言的にテストシナリオを記述できるのが特徴で、Android・iOSの両方に対応しています。

例えば、ログイン画面でメールアドレスとパスワードを入力し、ログインボタンを押すような操作を以下のように記述できます。

```
appId: com.example.app
---
- launchApp
- tapOn: "メールアドレス"
- inputText: "test@example.com"
- tapOn: "パスワード"
- inputText: "password"
- tapOn: "ログイン"
```

### Maestro MCPとは

Maestro MCPは、Claude CodeなどのMCP対応AIエージェントからMaestroを操作するためのMCPサーバです。

<https://docs.maestro.dev/get-started/maestro-mcp>

これを利用することで、AIエージェントはアプリを操作しながら画面構造を調査し、テストシナリオの生成や実行を行えるようになります。例えば、以下のような操作をMCP経由で実行できます。

* 接続中デバイスの確認
* 画面のスクリーンショット取得
* 画面要素の取得
* Maestro Flowの実行

ただし、作成されるテストの品質や進め方はエージェントへの指示内容に大きく依存します。

そこで今回公開したSkillでは、Flutterアプリ向けのE2Eテスト作成に特化したワークフローやガイドラインを定義しています。

## 公開したSkillについて

本Skillは、Maestro Flowの作成を支援するClaude Code Skillです。

<https://github.com/asmz/asmz-agent-plugins>

単にMaestro Flowを生成するだけではなく、コード調査・テスト実行・失敗時の修正まで含めた一連の作業手順をSkillとして定義しています。

大まかな流れは以下のようになります。

```
シナリオ理解
    ↓
Flutterコード調査
    ↓
必要に応じて Semantics(identifier) を追加
    ↓
Maestro Flow生成
    ↓
テスト実行
    ↓
失敗した場合は調査・修正
    ↓
再実行
```

### このSkillで重視していること

本Skillでは、特に以下のような点を重視しています。

* Flutterコードを調査し、UI実装を踏まえてテストを作成する
* Maestro MCPで実際にテストを実行しながら検証する
* テスト失敗時は原因を調査し、修正後に再実行する
* テキストよりも `Semantics(identifier)` を優先して利用する
* `Semantics(identifier)` が不足している場合は追加を提案する

単純にMaestro Flowを生成して終わりではなく、実際に実行しながらテストを完成させることを前提としています。

文章だけではイメージしづらいと思うので、次の章から実際の動作を見ていきます。

## デモアプリでの実験

実際にこのSkillを使い、どのようにテストシナリオが生成されるのか確認するために、デモアプリのプロジェクトで実験してみました。

### 実験用デモアプリ

### シンプルなテストシナリオの作成

まずはシンプルな例として、以下のようなテストシナリオの作成指示を与えてみます

> このアプリのボトムタブを全てタップし、各画面が正常に表示されることを確認するE2Eテストを作成して

![](https://static.zenn.studio/user-upload/8c8f193cd16d-20260608.png)  
*今回のSkillが使用されていることが確認できる*

するとSkillは、まず対象となるFlutterコードを調査し、画面内で利用されている `Semantics(identifier)` やテキスト情報など、テストに利用できる要素を収集します。

![](https://static.zenn.studio/user-upload/e355c75293cb-20260608.png)

その後、調査結果をもとに必要があればFlutterコードへ `Semantics(identifier)` の追加などを行い、最終的にMaestro Flowを生成します。

今回のケースでは、ボトムタブと各画面ルートに `Semantics(identifier)` が不足していたため、以下のような変更が提案されました。

```
@@ -26,10 +147,25 @@ class MainTabViewState extends State<MainTabView> {
         body: _pages.elementAt(_selectedIndex),
         bottomNavigationBar: BottomNavigationBar(
           items: [
-            BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
+            BottomNavigationBarItem(
+              icon: Semantics(
+                identifier: 'main_tab_profile',
+                child: Icon(Icons.person),
+              ),
+              label: 'Profile',
+            ),
             :
```

これにより、表示テキストではなく安定した `Semantics(identifier)` を利用したテストを作成できるようになります。

また、単純に指示されたタスクだけを実行するのではなく、画面録画の開始・終了や、操作後のアサーションなども自動的に入れてくれます。

[bottom\_tabs.yaml（抜粋）]

```
appId: ${APP_ID}
---
- startRecording:
    path: maestro/screenshots/${TIMESTAMP}_${PLATFORM}/bottom_tabs
# ボトムタブ(Profile / Blog / Slide)を全てタップし、各画面が正常に表示されることを確認する
- launchApp
- waitForAnimationToEnd

# 起動直後は Profile タブが表示される
- assertVisible:
    id: "profile_page"
:
```

実際に生成された `bottom\_tabs.yaml` 全文

```
appId: ${APP_ID}
---
- startRecording:
    path: maestro/screenshots/${TIMESTAMP}_${PLATFORM}/bottom_tabs
# ボトムタブ(Profile / Blog / Slide)を全てタップし、各画面が正常に表示されることを確認する
- launchApp
- waitForAnimationToEnd

# 起動直後は Profile タブが表示される
- assertVisible:
    id: "profile_page"

# Blog タブに切り替え
- tapOn:
    id: "main_tab_blog"
- waitForAnimationToEnd
- assertVisible:
    id: "blog_page"

# Slide タブに切り替え
- tapOn:
    id: "main_tab_slide"
- waitForAnimationToEnd
- assertVisible:
    id: "slide_page"

# Profile タブに戻り、Flow開始時と同じ状態で終了
- tapOn:
    id: "main_tab_profile"
- waitForAnimationToEnd
- assertVisible:
    id: "profile_page"

- stopRecording
```

生成後はそのままテストを実行し、結果を確認します。

![](https://static.zenn.studio/user-upload/96db47971e01-20260608.gif)  
*Maestroに同梱されているMaestro Viewerで、MCPのリアルタイムな動きを確認可能*

今回のケースでは追加の修正は発生せず、そのままテストが成功しました。

### 失敗したテストの自動修復

次に、以下のようにアプリ起動時にいくつかのモーダルを表示し、先ほどのテストが失敗するように仕込んでみます。

* お知らせダイアログ表示
* 利用規約確認ボトムシート表示
* アップデートお知らせモーダル表示

![](https://static.zenn.studio/user-upload/ee75d5590dc1-20260608.gif)

この状態で、先ほど生成したMaestro Flowを実行すると、起動直後にモーダルが表示されるため、期待していたプロフィール画面に到達できずテストは失敗します。

```
$ TIMESTAMP=$(date +%Y%m%d_%H%M%S)
maestro test maestro/flows/bottom_tabs.yaml \
   -e APP_ID=beer.asmz.portfolio.flutter \
   -e TIMESTAMP=$TIMESTAMP -e PLATFORM=ios
Running on iPhone Air - iOS 26.2 - 0CFCA50A-546F-4EAB-80F9-D61713B00719

 ║
 ║  > Flow: bottom_tabs
 ║
 ║    ✅   Start recording maestro/screenshots/20260608_123517_ios/bottom_tabs
 ║    ✅   Launch app "beer.asmz.portfolio.flutter"
 ║    ✅   Wait for animation to end
 ║    ❌   Assert that id: profile_page is visible
 ║    🔲   Tap on id: main_tab_blog
 ║    🔲   Wait for animation to end
 ║    🔲   Assert that id: blog_page is visible
 ║    🔲   Tap on id: main_tab_slide
 ║    🔲   Wait for animation to end
 ║    🔲   Assert that id: slide_page is visible
 ║    🔲   Tap on id: main_tab_profile
 ║    🔲   Wait for animation to end
 ║    🔲   Assert that id: profile_page is visible
 ║    🔲   Stop recording
 ║

Assertion is false: id: profile_page is visible

Assertion 'id: profile_page is visible' failed. Check the UI hierarchy in debug artifacts to verify the element state and properties.

Possible causes:
- Element selector may be incorrect - check if there are similar elements with slightly different names/properties.
- Element may be temporarily unavailable due to loading state
- This could be a real regression that needs to be addressed

==== Debug output (logs & screenshots) ====
:
```

今回のテストは、アプリ起動直後に `profile_page` が表示されることを前提としていました。

しかし、アプリ仕様の変更によってモーダルが表示されるようになったため、この前提が成立しなくなりテストが失敗しています。

ここで、以下のようなテストシナリオの修復指示を与えてみます。

> アプリの変更によりE2Eテストのbottom\_tabs.yamlが失敗するようになってしまったので、テストシナリオを修復して

この指示を受けて、エージェントはMaestro MCPを利用しながら以下のような手順で原因調査と修正を行いました。

* 既存のMaestro FlowとFlutterコードを確認
* Maestro MCPでテスト失敗を再現
* スクリーンショットと画面要素を取得して原因を調査
* モーダル表示が原因であることを特定
* モーダルを閉じる処理をFlowへ追加
* 修正後のFlowを再実行し、成功を確認

![](https://static.zenn.studio/user-upload/be2bbf58324f-20260608.gif)

動画内にも出てきますが、エージェントから提案された修正Flowは以下です。

```
@@ -6,6 +6,34 @@ appId: ${APP_ID}
 - launchApp
 - waitForAnimationToEnd
 
+# 起動時に順次表示される3つのダイアログを閉じる
+# 1) お知らせ AlertDialog
+- extendedWaitUntil:
+    visible:
+      text: "OK"
+    timeout: 20000
+- tapOn:
+    text: "OK"
+- waitForAnimationToEnd
+  :
```

起動直後に表示されるモーダルを順番に閉じる処理が追加されていることが分かります。

なお、動画の最後の方に少しエージェントの見解が出てきますが、今回はボタンラベルが十分安定した固定テキストであると判断され、 `Semantics(identifier)` の追加ではなく、`text:` でのマッチが選択されていました。Skill側でガイドラインを定義していても、エージェントは状況に応じて別の解決策を選択する場合がありますのでご注意ください。

この修正後に再度テストを実行し、全てのアサーションが成功することを確認できました。

このように、Maestro MCPを利用することで、テスト生成だけでなく失敗時の調査や修正まで含めたワークフローを構築できます。

## まとめ

今回は、Maestro MCPとAIエージェントを組み合わせたE2Eテスト作成ワークフローを紹介しました。

Maestro MCPによって、AIエージェントはアプリを操作しながらテストシナリオの生成・実行・修正を行えるようになります。

今回はFlutterの `Semantics(identifier)` を利用しましたが、React Nativeの `testID` のように安定したセレクタを持つ環境であれば、同様のアプローチを適用できます。

また、今回公開したSkillも、もともとは実際の業務で利用していたものから汎用的な部分を切り出したものです。チームごとのテスト方針や開発ルールに合わせてSkillを育てていくことで、それぞれの開発環境に合わせたワークフローへ発展させていくことができるかと思います。

E2Eテストの作成やメンテナンスに課題を感じている方の参考になれば幸いです。
