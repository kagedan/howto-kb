---
id: "2026-07-08-claudechatgpt-desktopmacで日本語入力の誤送信を止める-enterで改行cmd-01"
title: "Claude(ChatGPT) Desktop（Mac）で日本語入力の誤送信を止める — Enterで改行、Cmd+Enterで送信にする"
url: "https://qiita.com/Nono3/items/4be1c8ae483ee1151a4c"
source: "qiita"
category: "ai-workflow"
tags: ["Gemini", "GPT", "qiita"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- Claude Desktop / claude.ai は「Enter＝送信」「Shift+Enter＝改行」が標準仕様
- 日本語入力で変換を確定する Enter がそのまま送信として扱われ、書きかけのプロンプトが誤送信される
- Mac なら Karabiner-Elements で「Enter＝改行 / Cmd+Enter＝送信」に付け替えるのが一番手軽
- 変換確定の Enter まで巻き込まれるのが気になるなら、IME 由来の Enter だけ素通しする常駐ツール（CGEventTap）を使うと厳密に解決できる
- ブラウザ版だけなら Chrome 拡張で対応できる

## なぜ誤送信が起きるのか

原因は大きく2つあります。

1つ目は、指の慣れの問題です。Slack・Discord・メールクライアントは「Enter＝改行、Ctrl+Enter＝送信」の流儀ですが、Claude をはじめ ChatGPT や Gemini など AI チャット系はほぼ業界標準で「Enter＝送信」です。長年の指の動きと噛み合わず、書いている途中で送ってしまいます。

2つ目が日本語ユーザー特有の、より厄介な原因です。日本語入力では変換候補を選んで Enter で確定する操作が頻繁に発生します。この「確定のための Enter」が、そのまま Claude 側に「送信の Enter」として伝わってしまい、未完成のプロンプトで回答が始まってしまいます。メッセージ上限も無駄に消費されるので、地味にダメージが大きい問題です。

なお claude.ai（ブラウザ版）を Chrome で使う場合は対策が施されていることもありますが、デスクトップアプリや Safari では顕著に発生します。

## 大前提：Karabiner にできること・できないこと

具体策に入る前に、ここを押さえておくと設定でハマりません。

Karabiner-Elements ができるのは「アプリに届くキー入力を差し替える」ことだけで、アプリ側がそのキーをどう解釈するかは変えられません。Claude Desktop は「Enter＝送信」と解釈するアプリなので、Enter を改行として機能させたければ、Karabiner が物理 Enter を Shift+Enter に変換してアプリに渡すしかありません。

ここを勘違いして「Enter を Enter に変換（＝素通し）」としてしまうと、アプリは相変わらずそれを送信と解釈するため、誤送信問題はまったく解決しません。「Enter を改行にする」の実体は「Enter を Shift+Enter としてアプリに渡す」だと理解しておくのがポイントです。

## 解決法1：Karabiner-Elements（デスクトップアプリ向け）

Claude Desktop がアクティブなときだけ、単独の Enter を改行（Shift+Enter）として渡し、Cmd+Enter を送信（Enter）に変換します。`frontmost_application_if` で Claude Desktop に限定するので、他のアプリ（Emacs や Windows App など）の挙動には一切影響しません。

以下の JSON をそのままインポートできます。

```json
{
  "title": "Claude Desktop: Enter=改行 / Cmd+Enter=送信",
  "rules": [
    {
      "description": "Claude Desktop: 単独Enterを改行(Shift+Enter)に、Cmd+Enterを送信(Enter)に",
      "manipulators": [
        {
          "type": "basic",
          "from": {
            "key_code": "return_or_enter",
            "modifiers": { "mandatory": ["command"] }
          },
          "to": [ { "key_code": "return_or_enter" } ],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": ["^com\\.anthropic\\.claudefordesktop$"]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "return_or_enter" },
          "to": [ { "key_code": "return_or_enter", "modifiers": ["shift"] } ],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": ["^com\\.anthropic\\.claudefordesktop$"]
            }
          ]
        }
      ]
    }
  ]
}
```

順序に注意してください。Cmd+Enter のルールを先に置くのがコツです。Karabiner はマニピュレータを上から評価するため、この順で並べておくと Cmd+Enter が確実に「送信」として処理されます。

### 導入手順

1. Karabiner-Elements を開き、Complex Modifications タブを選択
2. Add rule → Add your own rule
3. 表示されたダイアログに上記 JSON を貼り付けて Save
4. 追加されたルールを Enable にする

macOS Sequoia 以降では、Karabiner のドライバ機能拡張を「システム設定 → 一般 → ログイン項目と機能拡張」で有効化する必要があります。インストール直後に動かないときは、まずここを確認してください。grabber と observer の片方しか表示されない場合は、Karabiner-Elements を再起動すると両方出るようになります。

設定が有効になると、Claude Desktop 内では次のようになります。変換確定は通常どおり Enter、改行だけ入れたいときも Enter、送信は Cmd+Enter。LINE や Slack に近い操作感になります。

### この方式の注意点

物理 Enter を一律 Shift+Enter に変換するため、変換確定の Enter も Shift+Enter として扱われます。実用上はほぼ問題ないという報告が多いものの、環境によっては「変換確定と同時に改行が1つ入る」といった挙動が出ることがあります。これが気になる場合は、次の解決法2が向いています。

## 解決法2：IME 由来の Enter だけ通す（より厳密）

変換確定の Enter まで巻き込みたくない、という場合は、キーイベントを直接監視して IME 由来のものだけ素通しする方法があります。

macOS には CGEventTap という仕組みがあり、アクセシビリティ権限を付与すればシステム全体のキーイベントを捕捉・変換・破棄できます。ポイントは、物理キー押下と IME が内部生成したイベントを `eventSourceStateID` で判別できることです。ユーザーが物理的にキーを押したイベントは `sourceStateID = 1`（hidSystemState）になるのに対し、IME が変換確定のために内部生成したイベントは異なる値になります。

これを利用すると、次のような振り分けが実現できます。

- 物理 Enter → Shift+Enter に変換（改行）
- Cmd+Enter → Enter に変換（送信）
- IME 由来の Enter（変換確定）→ そのまま素通し

常駐方法にも一つ落とし穴があります。launchd での常駐は GUI セッション外から起動されるためアクセシビリティ権限が正しく継承されず、CGEventTap の作成に失敗します。macOS の「ログイン項目」として登録すれば GUI セッション内で起動され、権限が正常に効きます。

この考え方を Swift で実装した `ClaudeRemap` という作例が公開されています。監視対象アプリを表す定数を差し替えるだけで他アプリにも応用できます。実装コードと詳しい解説はこちらを参照してください。

- Claude デスクトップアプリで「Enter で改行、Command+Enter で送信」を実現する（Qiita）: https://qiita.com/nate3870/items/51b196de9a07717d3952

## 解決法3：ブラウザ版（claude.ai）の場合

ブラウザ版に Karabiner を使うとブラウザの bundle ID 全体、つまり他サイトまで巻き込んでしまうため、こちらは拡張機能のほうが素直です。

「ChatGPT Ctrl+Enter Sender」という Chrome 拡張は、送信キーを Ctrl+Enter（Mac では Cmd+Enter）に割り当て、本来の Enter を改行用に変更してくれます。名前に ChatGPT と付いていますが、v1.4.0 以降で claude.ai にも正式対応しています。

Safari 派で拡張が使いにくい場合は、変換中および変換確定直後の一定時間（例：300ms）だけ Enter による送信をブロックする UserScript を Tampermonkey で動かす方法もあります。`compositionstart` / `compositionend` を監視し、キャプチャフェーズで Enter イベントを止めるのが定石です。

## どれを選ぶか

| 状況 | おすすめ |
| --- | --- |
| デスクトップアプリ中心、とにかく手軽に | 解決法1（Karabiner） |
| 変換確定の余計な改行まで避けたい | 解決法2（CGEventTap 常駐ツール） |
| ブラウザ版（claude.ai）中心 | 解決法3（Chrome 拡張 / UserScript） |

Karabiner をすでに使っているなら、まずは解決法1を入れてみて、変換確定まわりの挙動が気になったら解決法2へ、という流れが現実的です。

## まとめ

Claude Desktop の誤送信は、日本語ユーザーならほぼ全員が一度は踏む問題です。原因は「AI チャット標準の Enter＝送信」と「日本語 IME の変換確定 Enter」の二重苦にあります。

Mac であれば Karabiner-Elements で「Enter＝改行 / Cmd+Enter＝送信」に付け替えるのが手軽で、アプリ限定条件を付ければ副作用もありません。変換確定 Enter まで厳密に扱い分けたいなら CGEventTap を使った常駐ツール、ブラウザ版中心なら Chrome 拡張、と使い分けられます。

現状 Claude 側に Enter 動作を入れ替える公式設定はありません。誤送信された回答にサムズダウンを付けて「IME の変換確定 Enter で送信されてしまう」旨をフィードバックしておくと、将来的な公式対応の後押しになるかもしれません。

## 参考リンク

- Claude Desktop IME Fix for Karabiner-Elements（GitHub Gist）: https://gist.github.com/azu/10268f35f5c7c286e72398d2e3262796
- Claude デスクトップアプリで「Enter で改行、Command+Enter で送信」を実現する（Qiita）: https://qiita.com/nate3870/items/51b196de9a07717d3952
- MacのSafariでClaude.aiを快適に使う：日本語入力時のEnterキー問題を解決するUserScript（Zenn）: https://zenn.dev/ryoushin/articles/cb6bfff2aea37e
