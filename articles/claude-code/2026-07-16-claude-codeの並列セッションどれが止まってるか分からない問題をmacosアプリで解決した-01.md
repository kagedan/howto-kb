---
id: "2026-07-16-claude-codeの並列セッションどれが止まってるか分からない問題をmacosアプリで解決した-01"
title: "Claude Codeの並列セッション、どれが止まってるか分からない問題をmacOSアプリで解決した"
url: "https://zenn.dev/hatoya/articles/62255987ec50e7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## Claude Codeを並列で走らせると起きる問題

Claude Codeが十分に賢くなった結果、最近の開発スタイルはこうなりました。

* ターミナルでセッションA: 機能実装
* 別タブでセッションB: バグ修正
* さらに別プロジェクトでセッションC: ドキュメント整備

すると今度は\*\*「どのセッションが許可待ちで止まっているか分からない」\*\*という問題が発生します。Claude Codeは危険な操作の前に人間の許可を求めて停止しますが、別の作業をしていると気づけない。気づいたら10分間ずっと `rm` の確認待ちだった、ということが日常的に起きます。

メニューバー常駐型のツール（[claude-status-bar](https://github.com/m1ckc3s/claude-status-bar) など）もありますが、メニューバーは1セッション分の表示が限界で、並列セッションには向きません。

そこで、\*\*全セッションの状態を常時最前面の小さなフローティングパネルに表示するmacOSアプリ「ccglance」\*\*を作りました。

![](https://static.zenn.studio/user-upload/b7b2601b8ae0-20260716.gif)

<https://github.com/hatoya/ccglance>

## できること

* 走っているClaude Codeセッションを**プロジェクトごとにまとめて一覧表示**
* 状態が一目で分かる: 作業中（経過時間つき）/ **許可待ちは黄色くパルス** / 完了・アイドル
* サブエージェント（Agentツール）の動きもインデント表示
* アイドル中のセッションはPRのCI/レビュー状態をアイコン表示
* クリックしても**作業中のアプリからフォーカスを奪わない**
* GitHub Releases経由の自動アップデート

インストールはHomebrewで一発です（Apple Silicon / macOS 12+）。

```
brew install --cask hatoya/tap/ccglance
```

初回起動時にClaude Codeのhooksを自動セットアップするので、あとは新しいセッションを始めるだけでパネルに現れます。既存のhooks設定には手を加えず、バックアップも作ります。

## 仕組み: hooksとJSONファイルだけ

構成は意図的に単純にしています。サーバーもIPCもありません。

![](https://static.zenn.studio/user-upload/f349344e1628-20260715.png)

Claude Codeには [hooks](https://code.claude.com/docs/ja/hooks) という仕組みがあり、`SessionStart` / `UserPromptSubmit` / `PreToolUse` / `PostToolUse` / `Notification` / `Stop` / `SessionEnd` といったライフサイクルイベントで任意のコマンドを実行できます。

ccglanceはここに小さなNode.jsスクリプトを登録し、イベントをstdinで受け取ってセッション状態のJSONを1ファイル書くだけ。アプリ側はそのディレクトリを0.5秒ごとに読んで描画するだけです。

この構成の良いところ:

* **疎結合**: アプリが落ちてもClaude Codeに影響ゼロ。逆も同じ
* **デバッグが楽**: `cat ~/.claude/ccglance/sessions/*.json` で全状態が見える
* **hooksスクリプトはnpm依存ゼロ**: インストールでnode\_modulesが生えない

クラッシュしたセッションのファイルが残る問題は、「12時間更新がないファイルは自動削除」という雑だが確実なルールで処理しています。

## こだわり1: フォーカスを奪わないパネル

ステータス表示ツールがフォーカスを奪って作業を中断させたら本末転倒なので、ここは一番気を使いました。AppKitの `NSPanel` を `.nonactivatingPanel` で作り、レベルを `.statusBar` に、全SpaceとフルスクリーンにもついてくるようにcollectionBehaviorを設定しています。

```
let panel = StatusPanel(
    contentRect: rect,
    styleMask: [.borderless, .nonactivatingPanel, .resizable],
    ...
)
panel.level = .statusBar
panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
```

これで「常に見えるが、決して邪魔しない」パネルになります。ドラッグでの移動・リサイズはできるので、サブディスプレイの隅に置いておくのが推奨の使い方です。

## こだわり2: 依存ゼロでビルドする

このアプリにはXcodeプロジェクトがありません。ビルドは `swiftc -O` を直接叩くシェルスクリプト1枚で、Xcode Command Line Toolsだけで完結します。外部Swiftパッケージもゼロです。

常時起動するユーティリティなので、Electronのような重いランタイムは選択肢に入れませんでした。ネイティブAppKitなら、常駐させてもCPU・メモリのフットプリントはごくわずかです。

リリースはGitHub ActionsでDeveloper ID署名 + notarize + stapleまで自動化してあり、Gatekeeperの警告なしでそのまま起動できます。

## このアプリ自体、ほぼClaude Codeで作った

「Claude Codeを監視するアプリをClaude Codeで作る」というセルフホスト的な開発でした。実装・CI整備・Homebrew tap対応・notarize対応まで、ほぼ全部Claude Codeとの共同作業です。

開発中は当然ccglance自身が画面の隅で動いているので、「許可待ちの黄色パルスに気づいて即答→開発が止まらない」というドッグフーディングの効果を一番実感したのは自分でした。

## まとめ

* Claude Codeの並列セッション運用には「状態の可視化」が効く
* hooks + JSONファイル + ポーリングという枯れた構成で十分実用になる
* macOSの常駐ツールはネイティブ（Swift/AppKit）で書くと軽い

同じ悩みを持っている方はぜひ試してみてください。フィードバック・issue歓迎です！

```
brew install --cask hatoya/tap/ccglance
```

<https://github.com/hatoya/ccglance>
