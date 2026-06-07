---
id: "2026-06-06-cmux-で-ai-エージェントの待機時間を眺めるpixel-officeを作った-01"
title: "cmux で AI エージェントの待機時間を眺める「Pixel Office」を作った"
url: "https://zenn.dev/atani/articles/cmux-pixel-office"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

![Pixel Office](https://static.zenn.studio/user-upload/deployed-images/e0dc22ff9a471b417df227cc.png?sha=f9cdbb65b2c2a6bc62388fca182c6e1bcf3e8165)

## はじめに

[VS Code 拡張「Pixel Agents」](https://zenn.dev/and_dot/articles/d987d07720929430)という、Claude Code の待機時間（記事中の言葉を借りれば「祈りの時間」）をピクセルアートで楽しくしてくれる拡張があります。仮想オフィスにキャラクターが並んで、エージェントがコードを書いていれば「タイピング」、入力待ちなら吹き出し、という具合に作業状況をアニメーションで見せてくれる。

これを見て「自分の環境にも入れたい」と思ったのですが、私の手元は VS Code ではなく [cmux](https://cmux.com/)（コーディングエージェント向けのオープンソースターミナル）でした。Pixel Agents は VS Code 拡張なので、そのままでは載りません。

ないなら作るか、ということで **cmux 版を作りました**。

## できたもの

cmux で開いている各 workspace を「働くエージェントの席」として並べ、状態をリアルタイムに表示するサイドバーです。約 1 秒ごとに再描画され、作業中の席は吹き出しのドットがアニメーションします。

| 状態 | 中の人 | ドット | 吹き出し |
| --- | --- | --- | --- |
| 呼び出し待ち（応答待ち） | 🙋 | 🟠 | 💬 呼んでます |
| 作業中（直近 60 秒に活動） | 🧑‍💻 | 🟢 | ⌨️ 作業中…（アニメ） |
| ひと休み（直近 15 分以内） | ☕️ | ⚪️ | 直近メッセージ |
| 就寝（それ以上） | 😴 / 🪑 | ⚪️ | 💤 待機中 |

席をタップするとその workspace に移動します。フッターには「N 席 · 呼出 M」を出していて、いくつのエージェントが自分の返事を待っているか一目で分かります。

生産性が上がるツールではありません。ですが、複数セッションを並行で回していると「今どの子が手を止めて待っているか」がゆるく見えて、ちょっと和みます。

種を明かすと、これは cmux 本体に組み込まれた **Custom sidebars** というベータ機能を使っています。`~/.config/cmux/sidebars/` に SwiftUI 風のファイルを置くと、cmux が**実行時に解釈してネイティブ SwiftUI として描画**してくれる、という仕組みです。

* ビルド・署名・別プロセスは不要。保存すると hot-reload で即反映
* cmux のライブ状態（workspace 一覧・未読数・git ブランチ・直近メッセージなど）に直接バインドできる
* 行タップで `cmux(...)` コマンドを実行できる

つまり「プラグイン」というより**テーマ／設定ファイルに近い**立ち位置です。任意コード実行はできず、cmux が許可した DSL のサブセットだけが動きます。

元の Pixel Agents との一番の違いは**データ源**です。本家は Claude Code が吐く `~/.claude/projects/*.jsonl` を監視します。今回読んでいるのは cmux が把握している workspace の状態です。なので Claude Code 専用ではなく、cmux 上のセッションなら何でも席として並びます。

## コード

サイドバーの本体はこの 1 ファイルだけです。

<https://gist.github.com/atani/f7b828ac06f3769c3804a28053a4a763>

状態判定の核はこのあたりです。`unread`（応答待ち）を最優先で見て、なければ `latestAt`（直近活動の epoch）と現在時刻の差で作業中／休憩／就寝を切り替えています。

```
if w.unread > 0 {
    Text("🙋")
} else {
    if let t = w.latestAt {
        Text(clock.epoch - t < 60 ? "🧑‍💻" : (clock.epoch - t < 900 ? "☕️" : "😴"))
    } else {
        Text("🪑")
    }
}
```

`clock` は約 1 秒ごとに更新されるので、作業中の吹き出しを `clock.second % 3` でドットの数を変えると、それだけでタイピング風のアニメーションになります。

## ハマりどころ：トグルが GUI に無い

ドキュメント（`docs/custom-sidebars.md`）には「Settings → Beta features → Custom sidebars で有効化」と書いてあります。ところが最新版 v0.64.13 のベータ機能一覧には Feed / Dock / エクステンションの 3 つしか出ていません。**Custom sidebars のトグルが見当たらない**のです。

機能自体はバイナリに入っています。`customSidebars.beta.enabled` という文字列があり、`~/.config/cmux/sidebars` も参照しているので、トグルが露出していないだけのようです。段階的なロールアウト中なのか、ドキュメントが実装より先行しているのかは分かりません。

ひとまず手元では `defaults` で直接フラグを立てて有効化できました。

```
defaults write com.cmuxterm.app "customSidebars.beta.enabled" -bool true
cmux reload-config
```

これで左サイドバー切り替えボタンの右クリックメニューに、自作サイドバーの名前が追加されます。この食い違いは cmux 側にも issue で共有しました。

## まとめ

* Pixel Agents の「待機時間を眺めて楽しむ」コンセプトを、cmux の Custom sidebars で再現した
* 中身は SwiftUI 風の設定ファイル 1 枚。cmux 本体機能の上に乗るユーザーコンテンツ
* データ源は Claude ログではなく cmux の workspace 状態なので、cmux 上のセッションなら何でも対象になる

実用性で語るものではないのですが、ターミナルの端で小さなオフィスが動いていると、待ち時間が少しだけ楽しくなります。同じ気分の方はぜひ。

## 関連リンク
