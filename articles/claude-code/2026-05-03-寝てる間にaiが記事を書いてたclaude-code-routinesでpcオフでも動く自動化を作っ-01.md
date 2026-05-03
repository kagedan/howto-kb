---
id: "2026-05-03-寝てる間にaiが記事を書いてたclaude-code-routinesでpcオフでも動く自動化を作っ-01"
title: "「寝てる間にAIが記事を書いてた」──Claude Code RoutinesでPCオフでも動く自動化を作った話"
url: "https://note.com/chaba08/n/nb0a82c1de5dd"
source: "note"
category: "claude-code"
tags: ["claude-code", "API", "GPT", "Python", "note"]
date_published: "2026-05-03"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

Claude Codeを触り始めてから「完全自動化」という言葉をよく目にするようになった。

でも実際に使ってみると気づく。  
PCを操作している間はAIが動いてくれる。  
でも電源を落とした瞬間、止まる。

「PCオフでも動かないなら、完全自動化じゃないよな」

そう思ってから、本当に自動化できる環境を作るまでの話を書く。  
ハマったポイントは全部正直に書く。

## やりたかったこと

Claude Codeでnote記事の生成から投稿まで、全工程を自動化したかった。  
フローはこうだ。

1. メモファイルを読んでテーマを決定
2. WebSearchで7クエリ調査
3. Claude案・ChatGPT案を生成
4. 2つをマージして最終稿を作成
5. note.comに下書き投稿

ローカルでは1週間かけて動かせるようにした。  
でもセッションを閉じると止まる。  
毎朝起動して実行するのは自動化ではない。

寝ている間に処理を進めたかった。

## Claude Code Routinesを知った

2026年4月14日、AnthropicがClaude Code Routinesをリサーチプレビューとして公開した。

一言で言うと、**Anthropicのクラウドインフラ上でClaude Codeをスケジュール実行できる機能**だ。

* PCを閉じていても動く
* 電源を落としていても動く
* 旅行中でも動く

Pro・Max・Team・Enterpriseプランで追加費用なく使える。  
実行上限はProが1日5回、Maxが15回だ。

設定は `claude.ai/code/routines` にアクセスして「New routine」をクリックするだけ。  
CLIから `/schedule` コマンドでも作れる。

これで「完全自動化」が実現できると思った。  
ここからハマりが始まる。

## ハマり①｜GitHub連携は2か所に設定が必要

Routinesはリポジトリのコードを読み込んで動く。  
GitHubとの連携が必要だ。

自分はclaude.aiとGitHubをすでに連携していた。  
そのまま使えると思っていた。

**甘かった。**

Routinesから読み込むためには、`github.com/apps/claude` から**別途インストール**が必要だった。  
claude.aiの連携とは完全に別の設定だ。

【連携先 ／ 用途】

この2か所を設定しないとRoutinesがリポジトリを認識してくれない。  
ドキュメントをよく読まずに進めて30分無駄にした。

## ハマり②｜リモート環境でPlaywrightが動かない

GitHub連携を解決して実行してみた。  
記事生成フローは動いた。  
問題はnote.comへの投稿処理だ。

もともとPlaywright（ブラウザ自動操作ライブラリ）でnote.comをUI操作して投稿していた。  
これがRoutinesの環境では完全に動かない。

理由はシンプル。  
**リモート環境にはブラウザがない。**

Playwrightはブラウザを起動して画面操作する。  
Anthropicのクラウドには当然ブラウザが入っていない。  
選択肢は1つ——Playwrightを捨てることだった。

## ハマり③｜reCAPTCHAがログインをブロック

Playwrightを諦めて、requests（PythonのHTTPライブラリ）でnote.comのAPIを直接叩く方式に切り替えた。

まず認証。  
note.comにメールアドレス＋パスワードでログインしようとした瞬間、reCAPTCHAが発動した。  
Pythonスクリプトからは突破できない。

**解決策はCookie認証だ。**

ブラウザで一度ログインした状態のCookieを取得して、それをスクリプトに渡す。

取得手順：

1. Chromeでnote.comにログイン
2. F12でDevToolsを開く
3. 「Application」タブ → 「Cookies」→「https://note.com」
4. `note\_gql\_auth\_token`と`\_note\_session\_v5`の値をコピー
5. `.env`ファイルに保存してスクリプトから参照

これだけでreCAPTCHAなし・ログイン不要で投稿できるようになった。  
Cookieが失効するまで使い続けられる。

## ハマり④｜X-Requested-Withヘッダーが必須

Cookie認証でリクエストを送った。  
ステータス200が返ってきた。  
でも記事が作成されていない。

調べたら、**note.comのAPIはヘッダーに`X-Requested-With: XMLHttpRequest`が必要**だとわかった。  
このヘッダーがないとAPIが正しく動かない。

```
headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": f"note_gql_auth_token={token}; _note_session_v5={session}",
    "Content-Type": "application/json",
}
```

Cookieと一緒に必ずセットで送ること。

## ハマり⑤｜本文はHTML形式で送らないとレイアウトが崩れる

投稿成功。  
でもnoteで記事を確認すると、改行がすべて消えて1つの長い段落になっていた。

原因はフォーマット。  
**note.comのAPIは本文をHTMLで受け取る。**  
プレーンテキストをそのまま送ると改行が無視される。

マークダウンをHTMLに変換してから送る。

```
import markdown
html_body = markdown.markdown(article_text)
```

これで正常にレイアウトされた状態で投稿できた。

## 結果

5つのハマりを越えて、全工程がRoutines上で動くことを確認した。

【ステップ ／ 内容 ／ 実行場所】

* メモ読み込み ｜ テーマ確認 ｜ クラウド
* 調査 ｜ WebSearch 7クエリ ｜ クラウド
* 記事執筆 ｜ Claude案・ChatGPT案生成 ｜ クラウド
* マージ・校閲 ｜ 最終稿作成 ｜ クラウド
* note投稿 ｜ Cookie認証でAPI投稿 ｜ クラウド

PCの電源を落とした状態でスケジュールを設定した。  
翌朝起きたらnoteに下書きが保存されていた。

これが「完全自動化」だと思う。

## まとめ：ハマりポイントの地図

Claude Code Routinesでnote自動投稿を実現するまでの落とし穴をまとめる。

**① GitHub連携は2か所に設定** claude.aiとgithub.com/apps/claudeは別々にインストールが必要

**② Playwrightは使えない** リモート環境にブラウザがない。API直接呼び出しに切り替える

**③ reCAPTCHAはCookie認証でスキップ** DevToolsから`note\_gql\_auth\_token`と`\_note\_session\_v5`を取得

**④ X-Requested-Withヘッダーを必ずセット** このヘッダーがないとAPIが動かない

**⑤ 本文はHTML形式で送る** プレーンテキストだとレイアウトが崩れる

エラーを見て、調べて、直す。その繰り返しで見えてきたことだ。「PCオフでも動く」を実現したい人の参考になれば嬉しい。

## この記事が参考になった方へ

▶ 有料マガジン「生成AI実践ラボ」   
https://note.com/chaba08/m/m6d5e6b3f79a2   
▶ Mentaで個別相談   
https://menta.work/user/222691

[#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#AI自動化](https://note.com/hashtag/AI%E8%87%AA%E5%8B%95%E5%8C%96) [#Claude](https://note.com/hashtag/Claude) [#副業](https://note.com/hashtag/%E5%89%AF%E6%A5%AD) [#note自動投稿](https://note.com/hashtag/note%E8%87%AA%E5%8B%95%E6%8A%95%E7%A8%BF) [#ClaudeCodeRoutines](https://note.com/hashtag/ClaudeCodeRoutines) [#完全自動化](https://note.com/hashtag/%E5%AE%8C%E5%85%A8%E8%87%AA%E5%8B%95%E5%8C%96)
