---
id: "2026-04-11-agent-browser入門claude-codeからブラウザを自在に操る導入他ツール使い分けガイ-01"
title: "agent-browser入門：Claude Codeからブラウザを自在に操る！導入＆他ツール使い分けガイド"
url: "https://zenn.dev/shinyaa31/articles/082457e115885c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/53b8fd98248e-20260411.png)

生成AI全盛の昨今、『ブラウザ操作』に関しても生成AIを介して良い感じに効率化、高速化対応させてしまおう！という動きが非常に活発化しています。私も最近色々触っている状況ではあります。(先日以下のブログでも取り上げたりしていました)

<https://zenn.dev/shinyaa31/articles/dd315ea4868eb1>

そんな中、上記エントリで言及・紹介したPlaywright、Browser Useに負けず劣らず(いやそれ以上？)な使い勝手、機能の豊富さを兼ね備えるツールがあることを知りました。それがこちらのagent-browserです。

<https://github.com/vercel-labs/agent-browser>

そこで当エントリでは、このagent-browserについて基本概念、CLI導入手順、サンプルユースケースの実行、及び既存他ツールとの『比較、使い分け基準』について紹介していきます。

## agent-browserとは

agent-browserは、Vercel Labsが開発した、AIエージェント向けのヘッドレスブラウザ自動化CLIツールです。

Rustで実装された高速なネイティブバイナリで動作し、ページへのナビゲート・要素のクリックやフォーム入力・スクリーンショット撮影・ネットワーク監視・マルチタブ操作など幅広いブラウザ操作をシンプルなコマンドで実行できます。Claude CodeをはじめとするAIエージェントからCLI経由で直接呼び出すことを前提に設計されており、アクセシビリティツリーを使ったスナップショット＆ref操作ワークフローがAIとの親和性を高めています。

### 実際、どういうことが出来るのか？

公式リポジトリの情報から内容を抜粋、まとめた『agent-browserでできること』は以下の通り。実に様々な用途をカバーしています。

| カテゴリ | 出来ること |
| --- | --- |
| ページナビゲーション | URLを開く・戻る・進む・リロード・ タブ／ウィンドウの新規作成と切り替え |
| 要素操作 | クリック・ダブルクリック・ホバー・ドラッグ＆ドロップ・ フォーム入力・チェックボックス・ドロップダウン選択 |
| スクリーンショット・PDF | ページ全体／指定範囲のスクリーンショット取得・PDF保存・ 注釈付きスクショ（`--annotate`） |
| スナップショット | アクセシビリティツリー取得・要素へのref付与（`@e1`等）による AIフレンドリーな操作ワークフロー |
| 情報取得 | テキスト・HTML・input値・属性・タイトル・URL・要素数・ バウンディングボックス・CSSスタイルの取得 |
| 待機処理 | 要素表示待ち・テキスト出現待ち・URL変化待ち・ ネットワーク完了待ち・JavaScript条件待ち |
| Cookie・ストレージ | Cookie・localStorage・sessionStorageの取得・設定・削除 |
| ネットワーク制御 | リクエストのインターセプト・ブロック・モックレスポンス・ HAR記録・リクエストフィルタリング |
| 認証・セッション管理 | ログイン状態の保存／復元・複数セッションの並列管理・ 認証情報の暗号化保管(Auth Vault) |
| バッチ実行 | 複数コマンドをJSON配列でまとめて実行 (プロセス起動コストの削減) |
| デバッグ・トレース | DevTools接続・トレース記録・プロファイリング・ コンソールログ・エラー取得・要素ハイライト |
| iOSシミュレーター | Appium経由でiOSシミュレーター／実機のMobile Safariを操作 |
| クラウドブラウザ連携 | Browserbase・Browserless・Browser Use・ Kernelなどをプロバイダー指定で切り替えて利用 |
| ライブストリーミング | WebSocket経由でブラウザ画面をリアルタイム配信 (AIの操作を人間が見守るペアブラウジング) |

### agent-browser、どういう形で実行できる(指示できる)のか？

#### 1. コマンドを1つずつ実行

基本形はこれです。まぁ用例とか覚えないといけないので面倒ではありますよね...

```
% agent-browser open example.com
% agent-browser snapshot
% agent-browser click @e1
```

#### 2. `&&`でチェーン実行

1行にまとめて連続実行できます。バックグラウンドのデーモンがブラウザを保持し続けるので、毎回ブラウザを立ち上げ直すコストがかかりません。

```
agent-browser open example.com && agent-browser snapshot -i && agent-browser click @e1
```

#### 3. バッチ実行（JSONで一括）

複数コマンドをまとめて投げられます。

```
echo '[
  ["open", "https://example.com"],
  ["snapshot", "-i"],
  ["click", "@e1"],
  ["screenshot", "result.png"]
]' | agent-browser batch --json
```

#### 4. Claude Codeに自然言語で指示する

以下のように日本語で指示するだけで、Claude Codeが必要なagent-browserコマンドを自動で組み立てて実行してくれます。[README](https://github.com/vercel-labs/agent-browser?tab=readme-ov-file#usage-with-ai-agents)にも「エージェントに自然言語で頼むのが最もシンプル(The simplest approach -- just tell your agent to use it:)」と明記されています。

```
example.comを開いて、ログインフォームにメアドとパスワードを入力してログインし、
ダッシュボードのスクリーンショットを撮ってください。
```

## 導入

手元の環境はmacOS(Apple M4)。Claude Code及び(推奨とされている)npmをそれぞれ導入済み、利用可能な状態としておきます。

```
% sw_vers
ProductName:            macOS
ProductVersion:         26.3
BuildVersion:           25D125

% claude --version
2.1.97 (Claude Code)

% npm --version
11.6.0
```

導入そのものは上記の通り、推奨されている`npm install` & `agent-browser install`で行いました。`-g`のオプション指定でグローバルに導入しています。

```
## npmとagent-browserコマンドでインストール実施.
% npm install -g agent-browser
added 1 package in 19s

% agent-browser install
Installing Chrome...
  Downloading Chrome 147.0.7727.56 for mac-arm64
  https://storage.googleapis.com/chrome-for-testing-public/147.0.7727.56/mac-arm64/chrome-mac-arm64.zip
  165/165 MB (100%)
✓ Chrome 147.0.7727.56 installed successfully
  Location: /Users/xxxxxxxxxx/.agent-browser/browsers/chrome-147.0.7727.56

## 導入バージョンの確認.
% agent-browser --version
agent-browser 0.25.3
```

## agent-browser実践

### #1. 指定サイトのスクリーンキャプチャ取得

URLと補完場所を指定して、任意のサイトのスクリーンキャプチャを取得させてみました。  
![](https://static.zenn.studio/user-upload/ade86f260c86-20260411.png)

> agent-browserを使って、Hacker Newsのトップページをスクリーンショットしてデスクトップに保存してください。  
> URLはこちら。<https://news.ycombinator.com/>  
> 保存先はこちら。/Users/xxxxxxxxxx/agent-browser-demo/case1

結果は以下の通り。  
![](https://static.zenn.studio/user-upload/bbf3a8049287-20260411.png)

指定の場所にフォルダ及び結果が格納されています。  
![](https://static.zenn.studio/user-upload/d477c0c53845-20260411.png)

出力結果のスクリーンショットは以下の通り。  
![](https://static.zenn.studio/user-upload/99e0ed4751e1-20260411.png)

### #2. 指定ページから情報を取得

上述でも使ったページから、テキストを抜き出す処理をやってみました。  
![](https://static.zenn.studio/user-upload/d976141692bf-20260411.png)

> agent-browserを使って、Hacker Newsのトップページから記事タイトルを全件取得して、テキストファイルに保存してください。  
> URL: <https://news.ycombinator.com/>  
> 保存先: /Users/xxxxxxxxxx/agent-browser-demo/case2/hn\_titles.txt

実行結果は以下の通り。  
![](https://static.zenn.studio/user-upload/5f70c8abb6cd-20260411.png)

出力結果：

hn\_titles.txt

```
1. Filing the corners off my MacBooks
2. Artemis II safely splashes down
3. 1D Chess
4. Chimpanzees in Uganda locked in eight-year 'civil war', say researchers
5. Installing every* Firefox extension
6. Bevy game development tutorials and in-depth resources
7. WireGuard makes new Windows release following Microsoft signing resolution
8. Industrial design files for Keychron keyboards and mice
9. AI assistance when contributing to the Linux kernel
10. A practical guide for setting up Zettelkasten method in Obsidian
11. Investigating Split Locks on x86-64
12. JSON formatter Chrome plugin now closed and injecting adware
13. Italo Calvino: A traveller in a world of uncertainty
14. Helium is hard to replace
15. CPU-Z and HWMonitor compromised
16. Starfling: A one-tap endless orbital slingshot game in a single HTML file
17. What is RISC-V and why it matters to Canonical
18. Sam Altman's response to Molotov cocktail incident
19. The Bra-and-Girdle Maker That Fashioned the Impossible for NASA
20. Launch HN: Twill.ai (YC S25) – Delegate to cloud agents, get back PRs
21. Watgo – A WebAssembly Toolkit for Go
22. Quien – A better WHOIS lookup tool
23. PGLite Evangelism
24. A compelling title that is cryptic enough to get you to take action on it
25. Nowhere is safe
26. Intel 486 CPU announced April 10, 1989
27. OpenClaw's memory is unreliable, and you don't know when it will break
28. Show HN: FluidCAD – Parametric CAD with JavaScript
29. Bild AI (YC W25) Is Hiring a Founding Product Engineer
30. Clojure on Fennel Part One: Persistent Data Structures
```

### #3. 検索実行、結果を保存

任意の条件でブラウザ操作(今回の場合は検索)を行い、その結果を含めてファイルに保存してもらうという指示を出してみました。  
![](https://static.zenn.studio/user-upload/519e2ad3977a-20260411.png)

> agent-browserを使って、GitHubで「claude-code」を検索し、  
> 　検索結果の上位10件のリポジトリ名を取得してテキストファイルに保存してください。  
> 　URL: <https://github.com>  
> 　保存先: /Users/xxxxxxxxxx/agent-browser-demo/case3/search\_results.txt

処理中の実行ログ。agent-browserが適宜解析を行い、作業が進んでいきます。  
![](https://static.zenn.studio/user-upload/2977a07a0625-20260411.png)

出力結果は以下の通り。  
![](https://static.zenn.studio/user-upload/37ab13ac187e-20260411.png)

また、検索時の対象ページ(GitHub)の内容も保存しています。  
![](https://static.zenn.studio/user-upload/1e8cdc5cc756-20260411.png)

最終出力結果のテキストファイルは以下のような内容となりました。

search\_results.txt

```
GitHub検索結果: claude-code

1. anthropics/claude-code
2. affaan-m/everything-claude-code
3. claude-code-best/claude-code
4. shareAI-lab/learn-claude-code
5. ChinaSiro/claude-code-sourcemap
6. hesreallyhim/awesome-claude-code
7. jarmuine/claude-code
8. musistudio/claude-code-router
9. davila7/claude-code-templates
10. shanraisshan/claude-code-best-practice
```

### #4. セッション管理を踏まえたログイン状態の永続化フローを記録

セッション管理を踏まえた一連のデモを指示。保存→切断→再接続→復元確認という、ログイン状態の永続化フローを検証してみました。

![](https://static.zenn.studio/user-upload/d70c1dcbc656-20260411.png)

> agent-browserを使って、「github-demo」というセッション名でGitHubを開き、  
> 　セッションを保存してから再接続してください。  
> 　セッションが復元されていることをスクリーンショットで確認し、  
> 　/Users/xxxxxxxxxx/agent-browser-demo/case4/ に保存してください。  
> 　URL: <https://github.com>

実行結果は以下の通り。  
![](https://static.zenn.studio/user-upload/c0a87190353b-20260411.png)  
![](https://static.zenn.studio/user-upload/f80ee3607165-20260411.png)

### #5. 出力結果の差分を表示

2つの異なる情報をブラウザ経由で取得し、その差分を表示する指示を依頼してみました。  
![](https://static.zenn.studio/user-upload/3dcd84859ed4-20260411.png)

> agent-browserを使って、以下の2ページをビジュアル差分で比較してください。

出力結果は以下の通り。  
![](https://static.zenn.studio/user-upload/c5ee88857a2a-20260411.png)

差分に用いた結果は以下の通り。  
![](https://static.zenn.studio/user-upload/893de3595980-20260411.png)  
![](https://static.zenn.studio/user-upload/8ddf8a6670a0-20260411.png)

そして差分結果もテキストで取得。正直あまり参考にならないサンプルだったなぁ...w

diff\_report.txt

```
=== HN ページ差分レポート ===
ベースライン : https://news.ycombinator.com/
比較対象     : https://news.ycombinator.com/news?p=2
ビジュアル差分: 7.88%（58,219 / 738,560 px）

--- PAGE 1（1〜30位）---
1. Filing the corners off my MacBooks
2. Artemis II safely splashes down
3. 1D Chess
4. Chimpanzees in Uganda locked in eight-year 'civil war', say researchers
5. Installing every* Firefox extension
6. Bevy game development tutorials and in-depth resources
7. WireGuard makes new Windows release following Microsoft signing resolution
8. Industrial design files for Keychron keyboards and mice
9. AI assistance when contributing to the Linux kernel
10. A practical guide for setting up Zettelkasten method in Obsidian
11. Investigating Split Locks on x86-64
12. JSON formatter Chrome plugin now closed and injecting adware
13. Italo Calvino: A traveller in a world of uncertainty
14. Helium is hard to replace
15. CPU-Z and HWMonitor compromised
16. Starfling: A one-tap endless orbital slingshot game in a single HTML file
17. The Bra-and-Girdle Maker That Fashioned the Impossible for NASA
18. What is RISC-V and why it matters to Canonical
19. Sam Altman's response to Molotov cocktail incident
20. Launch HN: Twill.ai (YC S25) – Delegate to cloud agents, get back PRs
21. Watgo – A WebAssembly Toolkit for Go
22. PGLite Evangelism
23. A compelling title that is cryptic enough to get you to take action on it
24. Intel 486 CPU announced April 10, 1989
25. Nowhere is safe
26. OpenClaw's memory is unreliable, and you don't know when it will break
27. Quien – A better WHOIS lookup tool
28. Show HN: FluidCAD – Parametric CAD with JavaScript
29. Bild AI (YC W25) Is Hiring a Founding Product Engineer
30. Clojure on Fennel Part One: Persistent Data Structures

--- PAGE 2（31〜60位）---
31. Vinyl Cache and Varnish Cache
32. You can't trust macOS Privacy and Security settings
33. Show HN: Eve – Managed OpenClaw for work
34. Show HN: A WYSIWYG word processor in Python
35. Code is run more than read (2023)
36. The difficulty of making sure your website is broken
37. Penguin 'Toxicologists' Find PFAS Chemicals in Remote Patagonia
38. Molotov cocktail is hurled at home of Sam Altman
39. Simulating a 2D Quadcopter from Scratch
40. Mysteries of Dropbox: Testing of a Distributed Sync Service (2016) [pdf]
41. Team from ETH Zurich make high quality quantum swap gate using a geometric phase
42. FBI used iPhone notification data to retrieve deleted Signal messages
43. We've raised $17M to build what comes after Git
44. The best seat in town
45. A security scanner as fast as a linter – written in Rust
46. Bluesky April 2026 Outage Post-Mortem
47. RSoC 2026: A new CPU scheduler for Redox OS
48. How NASA built Artemis II's fault-tolerant computer
49. HBO Obtains DMCA Subpoena to Unmask 'Euphoria' Spoiler Account on X
50. Combining spicy foods with mint boosts anti-inflammatory effects 100x or more
51. Why do we tell ourselves scary stories about AI?
52. Show HN: Marimo pair – Reactive Python notebooks as environments for agents
53. C++: Freestanding Standard Library
54. Warez Scene
55. I still prefer MCP over skills
56. DOJ Top Antitrust Litigators Exit After Ticketmaster Accord
57. Google's Gmail Upgrade Decision: 2B Users Must Act Now
58. Instant 1.0, a backend for AI-coded apps
59. Two Japanese suppliers commit to keeping Blu-ray discs and drives in supply
60. Native Instant Space Switching on macOS

→ 全記事が異なる（同一構造・異なるコンテンツ）
```

## ブラウザ操作自動化系ツールの『使い分け』方針

さて、世の中的には所謂『ブラウザ操作自動化系』と呼ばれるツールやライブラリが今回紹介したagent-browser以外にも著名なものは幾つかあります。一旦ここで『どういう時にどれを使えば良いのか』を整理してみましょう。

| ツール | 開発元 | 操作主体 | 実装言語 | Claude連携方法 |
| --- | --- | --- | --- | --- |
| **[Playwright MCP](https://github.com/microsoft/playwright-mcp)** | Microsoft | 決定論的 | TypeScript | Claude Desktop / Code（MCP） |
| **[agent-browser](https://github.com/vercel-labs/agent-browser)** | Vercel Labs | AI判断 | Rust | Claude Code（CLI） |
| **[Browser Use](https://github.com/browser-use/browser-use)** | browser-use.com | AI判断 | Python | Claude Code（Python） |
| **[Stagehand](https://github.com/browserbase/stagehand)** | Browserbase | ハイブリッド | TypeScript | Claude Code（TS/JS） |
| **[Puppeteer](https://github.com/puppeteer/puppeteer)** | Google | 決定論的 | JavaScript | Claude Code（CLI/Node） |

### 各ツールの特徴詳細

上記で挙げたツール群の『強み』や『弱み』についてもまとめてみました。今回Claude CodeのみならずClaude.ai(Desktop)でも利用出来ないかなと思っていたのですが、この手のツールに関してはPlaywrightが最有力候補になりそうですね。

| ツール | 強み | 弱み | 向いているタスク | Claude Desktop |
| --- | --- | --- | --- | --- |
| **Playwright MCP** | 安定性・再現性が高い。手順が明確なタスクに最適 | 操作手順をコードで明示する必要があり、動的なページへの柔軟な対応は苦手 | フォーム入力・ボタンクリックなど手順が固定の自動化、E2Eテスト | ✅ MCP経由で直接使える |
| **agent-browser** | Rust製で高速・軽量。CLIなのでClaude CodeのBashツールから直接呼び出しやすい。スナップショット＆ref方式がAIとの相性抜群 | Claude Desktopからは使いにくい。複雑なロジックはClaude Code側が担う必要あり | スクレイピング・スクリーンショット・情報収集・サイト調査 | ❌ Claude Code推奨 |
| **Browser Use** | PythonエコシステムとのなじみがよくLangChainなどと組み合わせやすい。AIによる自律的な判断に強い | Python環境が必要。セットアップがやや重い | 複雑な判断を伴う多ステップタスク、Pythonベースのエージェント構築 | ❌ Claude Code推奨 |
| **Stagehand** | 「AIで要素を探してコードで操作」というハイブリッド設計。精度と柔軟性のバランスが良い | TypeScript/JS環境が必要。他ツールより情報が少ない | AIの判断と決定論的操作を組み合わせたガッツリしたエージェント開発 | ❌ Claude Code推奨 |
| **Puppeteer** | 情報量・事例が豊富。Node.jsエコシステムに馴染みがある人には敷居が低い | Playwrightやagent-browserと比べると速度・機能面でやや見劣りする。AI連携は自前実装が必要 | 既存のNode.jsプロジェクトへの組み込み、シンプルなスクレイピング | ❌ Claude Code推奨 |

上記内容を踏まえ、『どれを使えば良い？』のフローチャートも作ってみました。よろしければ参考にしてください。

## まとめ

という訳で、Vercel Labsが開発したAIエージェント向けのヘッドレスブラウザ自動化CLIツール『agent-browser』の紹介でした。実に広い範囲で『できること』をカバーしているこちらのツール、他ツールとの組み合わせを考えても主力級で頑張ってもらえそうな立ち位置になりそうです。一方Claude Desktop作業が入るようなケースではagent-browserは守備範囲外なので、他ツール(現状だとPlaywrightかな)との併用で良い感じに分担作業させていければと思います。
