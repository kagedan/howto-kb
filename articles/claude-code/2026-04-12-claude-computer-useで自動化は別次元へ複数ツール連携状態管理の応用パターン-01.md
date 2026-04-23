---
id: "2026-04-12-claude-computer-useで自動化は別次元へ複数ツール連携状態管理の応用パターン-01"
title: "Claude Computer Useで自動化は別次元へ――複数ツール連携・状態管理の応用パターン"
url: "https://qiita.com/moha0918_/items/a140a8c2abb0eaf7ebcc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

Claude Code の `computer-use` MCP サーバーを有効化して「あとはよしなに」と投げてみると、思った以上のことをやってのけます。ただ、単純に「クリックしてくれる」だけなら使い道は限られます。真価が出るのは、**Bash・MCP・Computer Use の三つを組み合わせて、ループと状態管理を加えたとき**です。

この記事では、Computer Use の基本説明は最小限に留めて、実務で使える応用パターンに絞って解説します。

対象読者

* Claude Code をすでに使っており `/mcp` や Bash ツールに慣れている方
* macOS の Pro または Max プランを利用中
* Claude Code v2.1.85 以上を使用中

Computer Use 自体の有効化手順は[公式ドキュメント](https://docs.claude.ai/en/computer-use)を参照してください。

## ツール選択の優先順位を理解する

応用パターンに入る前に、Claude がどの順序でツールを選ぶかを把握しておくことが重要です。

| 優先度 | ツール | 使われる場面 |
| --- | --- | --- |
| 1 | MCP サーバー | 対象サービスに専用 MCP がある場合 |
| 2 | Bash | シェルコマンドで完結する場合 |
| 3 | Claude in Chrome | ブラウザ作業 |
| 4 | Computer Use | 上記で届かないもの全て |

Computer Use は最終手段です。精度・速度ともに最も低コストなのは Bash や MCP なので、**Computer Use が起動した時点で「ここは GUI にしか手が届かない」という意味**になります。

この優先順位を意識すると、プロンプト設計が変わります。「GUI を使わせたい」ときは、あえて MCP や API を排除した指示にする。逆に「なるべく Computer Use を避けたい」なら、利用可能な MCP を事前に整備しておく。

## パターン1: ビルド→起動→UIテスト→スクリーンショット保存のパイプライン

最もわかりやすい応用例から始めます。Swift アプリを書いて、その場でビルドし、GUI を操作して動作確認まで一気通貫でやらせるパターンです。

ポイントは**ステップを細かく分けずに一つの指示で投げる**こと。「ビルドして、起動して、テストして」と列挙するより、「こういう状態になっていることを確認して」と結果で指示する方が Claude が適切にツールを選択してくれます。

```
Build the MenuBarStats target with xcodebuild, launch the app,
open the preferences window, verify that the interval slider
updates the label in real time, and save a screenshot to
./test-results/prefs-$(date +%Y%m%d-%H%M%S).png when done.
If the build fails, show me the first 30 lines of the error.
```

こう書くと Claude は：

1. `xcodebuild` を Bash で実行（MCP なし → Bash 優先）
2. ビルド成功後に Computer Use でアプリを起動
3. UI を操作して動作確認
4. `date` コマンドでファイル名を作って `screencapture` 保存

という流れを自律的に組み立てます。失敗時のフォールバックを指示に含めておくのが重要で、これがないと Claude がエラーに詰まって停止しがちです。

スクリーンショット保存のパスは事前に `mkdir -p ./test-results` しておくか、指示の中に「ディレクトリがなければ作ってから保存して」を含めるとトラブルが減ります。

## パターン2: 状態ループによる回帰テスト

単発の操作でなく、**複数の状態を順番に確認するループ**を組ませるパターンです。

「ウィンドウを複数サイズにリサイズして、各サイズでスクリーンショットを撮って、レイアウト崩れを報告する」という指示で、Computer Use が状態遷移を管理します。

```
Test the Settings modal at the following window widths:
1200px, 900px, 768px, 600px, 400px.

For each width:
1. Resize the app window to that width
2. Open the Settings modal
3. Take a screenshot named settings-{width}px.png
4. Check if the footer or any button is clipped or hidden

After all sizes, summarize which widths had layout issues.
```

この指示の重要な点が二つあります。

**ファイル名にパラメータを埋め込む**ことで、Claude が各ステップを「どこまでやったか」を把握しやすくなります。ループが途中で止まった際の再実行も楽になります。

**最後に要約を求める**こと。個々のスクリーンショットだけでなく、差分の言語化まで Claude にやらせると、実際にレビューする手間が格段に減ります。

## パターン3: MCP × Computer Use のハイブリッド

正直、これが一番設計のうまい使い方だと感じます。

「API で取れるデータは MCP 経由で取得し、その結果を GUI に入力する」という組み合わせです。たとえば、ある SaaS の管理画面が API を持たず、データは別の API で管理されているケース。

```
1. Use the github MCP to get the list of open PRs in myorg/myrepo
   that have the label "ready-for-staging"
2. For each PR, open the internal deploy dashboard at
   http://localhost:3000 and trigger a staging deploy
   by clicking "Deploy" next to the matching PR name
3. After each deploy, wait 10 seconds and check the status
   indicator turns green before proceeding to the next
```

GitHub 側のデータ取得は MCP が担い、GUI 操作だけ Computer Use が担当する形です。処理速度・精度ともに Computer Use 単独でやるより大幅に上がります。

ポイントは**待機（wait 10 seconds）を明示的に指示に含める**こと。非同期な状態変化を Claude に監視させるには、ポーリング間隔を指示しないと無限に待ち続けることがあります。

## パターン4: iOS Simulator の自動操作

XCTest を書かずにオンボーディングフローを試したいとき、Computer Use は即戦力になります。

```
Open the iOS Simulator (iPhone 15 Pro, iOS 17),
launch the app from Xcode,
then go through the onboarding flow:
- Tap "Get Started"
- Grant notification permissions when prompted
- Enter username "testuser_auto" and tap "Continue"
- On the interests screen, select 3 items and tap "Done"

At each step, note the time it takes for the next screen
to appear. If any transition takes more than 2 seconds,
flag it in your summary.
```

パフォーマンス計測を「指示の中に組み込む」のがこのパターンの肝です。別途計測ツールを用意しなくても、Claude が主観的な遅延を報告します。精度は落ちますが、「明らかに遅い画面がある」程度の粗い検出には十分使えます。

## セッション管理とロックの扱い方

Computer Use は**マシン全体のロックを取得する**仕組みになっています。複数のプロジェクトを並行して開いているときに「Computer use is in use by another Claude session」というエラーに遭遇しやすいのがここです。

対処は単純で、ロックを持っているセッションを終了するか、そのセッションでの Computer Use タスクを先に完了させるしかありません。クラッシュしたセッションのロックは自動解放されますが、数分かかることがあります。

チームで使う場合は、**同じマシンで複数人が SSH してそれぞれ Claude Code を起動する構成ではロックが競合します**。Computer Use はローカルデスクトップ前提の機能なので、リモート開発環境とは相性がよくありません。

## スクリーンショット解像度の扱いと注意点

Retina ディスプレイ（16インチ MacBook Pro なら 3456×2234）でも Claude には自動ダウンスケール（約 1372×887）されて渡されます。これは設定で変えられません。

ここで詰まるケースとして、**フォントサイズが小さいアプリや、密度の高いダッシュボードで Claude がテキストを読み誤る**ことがあります。対処はアプリ側のフォントサイズを上げるか、対象エリアを絞った指示にすることです。

```
Zoom in on the error log panel (bottom-right quadrant of the window)
and read the last 5 error messages.
```

「画面全体を見て」より「このエリアだけ見て」の方が精度が上がります。

## 安全面で外せない設定

`computer-use` を有効化すると、承認した**アプリに対してはかなり広い操作権限**が渡ります。特に注意が必要なのが以下の三つです。

| アプリ種別 | 付与される権限 | 注意度 |
| --- | --- | --- |
| ターミナル・IDE | シェルアクセス相当 | 高 |
| Finder | 任意ファイルの読み書き | 高 |
| System Settings | システム設定の変更 | 中 |

これらは「警告が出るだけでブロックはされない」点に注意してください。承認ダイアログが出たとき、反射的に Allow を押す前に**今のタスクにそのアプリの操作が本当に必要か**を確認する習慣が重要です。

ターミナルを Computer Use に承認するのは、Bash ツールで Claude にシェルを渡すのと実質的に同じです。サンドボックス外での操作になるので、重要なデータのあるマシンでは慎重に使ってください。

## まとめ

Computer Use の価値は「クリックを代替する」ことより、**Bash・MCP・GUI 操作を一つの会話の中でシームレスにつなぐ**点にあります。ツール選択の優先順位を理解して、Computer Use が起動するタイミングを意識的に設計することで、精度と速度のバランスが取れた自動化フローが組めます。

まず試すなら、手元の iOS Simulator や macOS アプリで「ビルドから UI 確認まで一発でやらせる」パターンが一番手触りを掴みやすいです。
