---
id: "2026-06-06-ai駆動開発はここまで来たclaudefigmamcpで1日アプリ制作-01"
title: "AI駆動開発はここまで来た！Claude×FigmaMCPで1日アプリ制作"
url: "https://zenn.dev/sun_asterisk/articles/claude-figma-mcp-app"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "zenn"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

今週末、Figma MCP サーバーを Claude Code から使って、デザインから実装までをつなぐ小さなアプリ開発を試してみました。  
想像以上に開発体験がよかったので、この記事では実際に行ったセットアップ手順をまとめます。

## 完成イメージ

Figma でデザインした画面を、MCP 経由で Claude に渡してコード化した最終成果物です。  
今回はペットと一緒に行ける場所を探せる **PetSpot** という Web アプリを作りました。

![PetSpot アプリの完成イメージ](https://i.gyazo.com/df8d6bd2c96c195270f6a24fbb70202c.gif)

検索バー、カテゴリタブ（Restaurants / Facilities / Hotels）、ブログ記事、おすすめスポット一覧など、Figma 上のデザインをそのまま Web アプリとして動かせています。

## 前提

このチュートリアルでは、次の環境がすでに整っていることを前提にしています。

* macOS を利用している
* **Claude CLI / Claude Code がインストール済み**（`claude` コマンドがターミナルから実行できる）
* **Figma の Pro プラン以上**を利用していて、ファイルで **Dev Mode（開発モード）が有効にできる**
* Figma Desktop アプリ、もしくはブラウザ版 Figma にログイン済み

## Figma MCP（リモート版）のセットアップ手順

公式ドキュメントは [Claude Code and Figma: Set up the MCP server](https://help.figma.com/hc/en-us/articles/39888612464151-Claude-Code-and-Figma-Set-up-the-MCP-server) を参照しています。

### 1. Figma プラグイン（MCP サーバー）をインストール

1. ターミナルを開く
2. 次のコマンドを実行して Figma プラグインをインストール

```
claude plugin install figma@claude-plugins-official
```

3. インストール完了後、Claude Code（CLI）を再起動

### 2. Figma MCP サーバーを有効化

1. ターミナルで `/plugin` と入力して Plugin marketplace を開く
2. `Installed` タブに移動
3. 一覧から `figma` サーバーを選択して Enter
4. もう一度 Enter を押して認証フローを開始
5. ブラウザで開いた Figma のページで「Allow access」をクリック
6. 認証が完了したらターミナルに戻り、再度 `/plugin` を実行して `figma` が「connected」になっていることを確認

### 3. Claude から Figma MCP を使う

ここまで設定できれば、Claude Code から Figma に対して次のようなことができるようになります。

* Figma ファイルのコンポーネントやレイアウト情報を読む
* Code Connect を使って、実際のコンポーネントコードと同期する(認証に問題が発生した場合　TROUBLESHOOTING をご覧ください)
* Claude 側から Figma のキャンバスにレイヤーを生成・更新する

ここからは、実際に「デザインを作る → コード化する」流れに進みます。

## Claude から Figma にデザインを作ってもらうプロンプト例

まずは Claude に、Figma MCP 経由でアプリの画面デザインを作ってもらいました。  
自分が使ったプロンプトのイメージはこんな感じです。

```
Create a Figma design for a pet-friendly spot search web app called "PetSpot".

The app should help users find restaurants, cafes, facilities, and hotels where they can go with their pets.

Design a desktop landing page with:
- A friendly header with the PetSpot logo
- Navigation links: TOP, Blog, Spots, Map
- A hero search area
- Category tabs for Restaurants, Facilities, and Hotels
- A search input
- A "Browse All Places" button
- A blog card section with pet-related articles
- A featured places ranking list
- A simple footer with social links

Use a warm, friendly, pet-themed visual style.
Make the layout clean and realistic so it can be implemented as a web app.
```

このプロンプトを Claude に渡すと、Claude が Figma MCP を使って Figma 上に画面デザインを作ってくれます。  
最初から完璧なデザインを狙うよりも、まずは全体の構成を作ってもらって、そのあと色・余白・文言を少しずつ調整する方が進めやすかったです。

## Figma 側の MCP セクションからコード実装までの流れ

Figma でデザインができあがったあと、Dev Mode の MCP セクションから「Claude に渡す用のプロンプト」をコピーして、そのまま Claude に貼るだけでコード実装に進めます。

ざっくりした流れは次のとおりです（UI の細かい文言は将来変わる可能性があります）。

1. Figma で対象フレーム（もしくはコンポーネント）を選択する
2. 右サイドバーで **Dev Mode** に切り替える
3. MCP / Claude 関連のセクションから、「コード生成用のプロンプト」を表示する
4. 提示されるプロンプト（例: 「このフレームをベースに React/Next.js のコンポーネントを実装して」など）を **そのままコピー**
5. ターミナルの Claude Code もしくは Claude の UI に貼り付けて実行

実際には、Figma の右サイドバーにある MCP セクションから `Copy example prompt` を押します。

![Figma MCP セクションの Copy example prompt](https://i.gyazo.com/004802e1e8d3069e738faf8e6b0e307a.png)

こうしておくと、「Figma 上のデザイン意図」と「実際のコード実装への指示」がズレにくくなり、デザイン変更が入っても、再度 MCP セクションからプロンプトをコピーし直すだけで実装側を追従させやすくなります。

## 実際に使って感じたメリット

実際に触ってみて特に便利だったのは、デザインと実装の往復コストがかなり減ったことでした。

これまでは、

1. Figmaで画面を作る
2. 実装する
3. デザインとの差分を直す
4. また実装を修正する

という流れになりがちでした。

一方、Figma MCP を使うと、Claude が Figma 上の構造を直接参照できるため、  
「余白」「コンポーネント構造」「レイアウト意図」を維持したままコード生成しやすくなります。

特にプロトタイピング段階ではかなり高速に UI を試せる感覚がありました。

## まとめ

今回、Claude Code と Figma MCP を使って、  
「デザインを作る → 実装する」という流れを実際に試してみました。

もちろん細かい調整や設計はまだ人間側で必要ですが、  
UI プロトタイピングや初期開発のスピードはかなり変わる感覚がありました。

特に、

* Figma 上のデザインをそのまま参照できる
* プロンプトをコピーするだけで実装に進める
* デザイン変更への追従がしやすい

という点は、これまでの「デザイン → 実装」の分断をかなり減らせそうです。

まだ発展途上な部分もありますが、  
今後の AI 駆動開発のワークフローとしてかなり面白い体験だったので、  
気になる方はぜひ試してみてください。

## Troubleshooting（認証直後の接続エラー）

認証後に Claude 側で次のような案内が出たあと、

`Please open this URL in your browser to authorize Figma access:`

案内に従ってブラウザで `Click here to authorize Figma` を開くと、Figma のページ後にブラウザ側で「接続エラー」になることがありました。

このときの解決方法として、Claude 側の指示どおり、ブラウザのアドレスバーに出ている `http://localhost:64438/callback?code=...` から始まる **フル URL** をコピーして、Claude に貼り直します。

自分のケースでは、そのあと Claude がエラー URL を受け取って処理が進み、`figma` が `connected` になりました（「Claude に再度ペーストする」がポイントでした）。

認証画面のイメージはこんな感じです。

![Claude と Figma の認証画面](https://i.gyazo.com/c71051fc18dca528ea0526682d55daeb.png)
