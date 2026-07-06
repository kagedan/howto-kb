---
id: "2026-07-07-claude-codeの出力トークンを65減らすcavemanの使い方と気をつけたいこと-01"
title: "Claude Codeの出力トークンを65%減らす「caveman」の使い方と気をつけたいこと"
url: "https://note.com/shali_note/n/n0ed0219099a9"
source: "note"
category: "claude-code"
tags: ["claude-code", "Gemini", "note"]
date_published: "2026-07-07"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

AIコーディングツールの利用量上限に、一度でも引っかかったことはありませんか。  
実はその原因の多くは「入力」ではなく「出力」の長さにあります。  
この記事では、AIエージェントの返信を短くして出力トークンを削減するツール「caveman」の導入方法と、使う前に知っておきたい注意点を紹介します。  
Claude CodeやCursorなどを日常的に使っていて、トークン消費を減らしたい人向けの内容です。

## なぜ今、出力トークンが気になるのか

![](https://assets.st-note.com/img/1783357248-SQi8cPgejLdoOnEB0Iahr6Kz.png?width=1200)

AIコーディングエージェントは、コードの説明やレビューコメントを書くとき、思っている以上に丁寧な前置きや言い換えを重ねます。  
「承知しました、確認します」といった社交辞令や、「〜することができます」のような回りくどい言い回しは、読み手には親切でも、トークン消費という面では無駄が多い部分です。  
cavemanは、こうした「文体そのもの」を圧縮することで出力トークンを減らすスキルです。  
テレメトリや分析機能は組み込まれておらず、インストール後に外部へ通信することもありません。  
プライバシー面の懸念が少ない点も、業務で使ううえでは安心材料になります。  
ただし先に断っておくと、削減されるのは出力トークンだけで、入力トークンには影響しません。  
むしろスキル自体が入力トークンを少し増やすため、詳しい注意点は記事の最後で扱います。  
まずは導入手順から見ていきます。

## ステップ1: 対応エージェントと前提条件を確認する

![](https://assets.st-note.com/img/1783357258-r7B8TQwmjYHA3VItDnUohXgx.png?width=1200)

cavemanはClaude Code、Codex、Gemini、Cursor、Windsurf、Cline、Copilotなど30以上のAIエージェントに対応しています。  
インストールにはNode.js18以上が必要です。  
手元の環境に対応エージェントが複数入っていても問題ありません。  
インストーラーが自動で検出し、入っていないエージェントはスキップしてくれます。

## ステップ2: ワンコマンドでインストールする

![](https://assets.st-note.com/img/1783357268-qAHNIbEFtjfKmvhCTBz3yw71.png?width=1200)

OSに応じて、次のいずれかのコマンドを実行します。

macOS・Linux・WSL・Git Bashの場合は、ターミナルで次を実行します。

「curl -fsSL <https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh> | bash」

Windows PowerShell5.1以降の場合は、次を実行します。

「irm <https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1> | iex」

所要時間はおよそ30秒です。  
再実行しても壊れる心配はないので、うまくいかなかったときはもう一度試してみるとよさそうです。  
Claude Codeだけに個別インストールしたい場合は、次のコマンドも用意されています。

「claude plugin marketplace add JuliusBrussee/caveman && claude plugin install caveman@caveman」

## ステップ3: 有効化して動作を確認する

![](https://assets.st-note.com/img/1783357277-7Zp2M5h1klungVGHFt4sQLe8.png?width=1200)

インストール後、「/caveman」と入力するか「talk like caveman」と話しかけると有効化できます。  
Claude Code・Codex・Geminiでは、インストール直後の最初のメッセージからすでに有効になっています。  
特別なコマンドを打たなくても、返信の文体が変わっていることに気づくはずです。  
普段の丁寧な口調に戻したいときは、「normal mode」と伝えるだけで解除できます。

## ステップ4: 圧縮レベルを使い分ける

![](https://assets.st-note.com/img/1783357285-xUlRoZO9QTckIszH2E1vb6aA.png?width=1200)

cavemanには「lite」「full」「ultra」「wenyan-lite」「wenyan-full」「wenyan-ultra」の6段階の圧縮レベルがあります。  
デフォルトは「full」です。  
「/caveman ultra」のように打つと、その場でレベルを切り替えられます。  
レベルは会話の途中で変更しても、セッションが終わるまで保持されます。  
なお、ポルトガル語やスペイン語で話しかけた場合はその言語のまま圧縮されます。  
翻訳されるわけではなく、あくまで文体だけが短くなる仕組みです。  
日本語での動作については、公式ドキュメントに具体的な記載が見当たらず、挙動は確認できていません。

## ステップ5: 削減効果を確認する

![](https://assets.st-note.com/img/1783357468-WlH7pXk3uPI5CMDrEjNf9dwS.png?width=1200)

「/caveman-stats」と打つと、そのセッションで実際に節約できたトークン数と、おおよそのドル換算額が表示されます。  
数字で効果を見られるので、体感だけでなく実際にどれくらい変わったのかを確かめられます。  
コミットメッセージを整えたいときは「/caveman-commit」、プルリクエストのレビューコメントを短くまとめたいときは「/caveman-review」も用意されています。

## 注意点とコツ

![](https://assets.st-note.com/img/1783357477-neY5x9HiC8qwQ1bvjB2ysFuk.png?width=1200)

cavemanを導入する前に、開発者自身が明かしている次の点は押さえておきたいところです。

**削減されるのは出力トークンだけ**で、入力や推論に使われるトークンは変わりません。  
それどころか、スキル自体が1ターンあたり1000から1500ほどの入力トークンを追加で消費します。  
そのため、セッション全体で見た節約幅は「65%」という数字より小さくなります。  
もともと簡潔な返信が多いワークロードでは、差し引きでトークン消費が増えてしまうケースもあると説明されています。  
公開されているベンチマークでは、10種類のプロンプトに対する実測で平均65%の出力削減が確認されていますが、この数字の前提を理解したうえで使うと、期待外れになりにくいはずです。

## まとめ

![](https://assets.st-note.com/img/1783357492-LK0O3SyYtDNbvXIQCUjxWpHw.png?width=1200)

cavemanは、AIエージェントの応答を「洞窟人語」のように短くすることで、出力トークンを大きく減らせるスキルです。  
インストールはOSに合わせたワンコマンドで完了し、Claude Codeなら数十秒で試せます。  
ただし節約されるのは出力トークンのみで、入力分はむしろ増える点は忘れずにおきたいところです。  
まずは「/caveman」と打って、いつもの返信がどう変わるか一度見てみると、自分の使い方に合うかどうか判断しやすくなります。

公式リポジトリはGitHubの「JuliusBrussee/caveman」で公開されています。  
インストール手順の詳細や対応エージェントの一覧、ベンチマークの生データも同じ場所で確認できます。  
リンク: <https://github.com/JuliusBrussee/caveman>

---

[#AI](https://note.com/hashtag/AI) [#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#仕事効率化](https://note.com/hashtag/%E4%BB%95%E4%BA%8B%E5%8A%B9%E7%8E%87%E5%8C%96) [#Claude](https://note.com/hashtag/Claude) [#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#caveman](https://note.com/hashtag/caveman) [#トークン削減](https://note.com/hashtag/%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3%E5%89%8A%E6%B8%9B)

---
