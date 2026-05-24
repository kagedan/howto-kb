---
id: "2026-05-24-claude-codeからcodexへ複雑な作業を任せるならどっちがいいai開発-01"
title: "Claude CodeからCodexへ。複雑な作業を任せるならどっちがいい？【AI開発】"
url: "https://note.com/lithe_nerine2263/n/nc2e71ba3fd34"
source: "note"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "Gemini"]
date_published: "2026-05-24"
date_collected: "2026-05-24"
summary_by: "auto-rss"
query: ""
---

こんにちは

AIに仕事を投げるのが大好きなこまっちゃんです。

Claude Code、最近なんか調子悪くなってきていませんか？

XやYouTubeを見ていると、そんな話をチラホラ見かけます。

複雑な指示をしていたらオートコンパクトが働いているからでしょ？とか、推論レベルが下がっているからでしょ？と思う方もいるかもしれません。

でも、そういうことでもないんです・・

例えば・・

```
僕「保存ボタンのレイアウトを〇〇に変更してください」

Claude Code「やりました」

僕「いや、これ変えたら入力欄もエラー表示も一覧画面も影響するでしょ・・」
```

頼んだところだけしか、直さない

影響するところは見に行かない。

いちいち説明するのもめんどくさいし、こっちでチェックするのもめんどくさい。

AIを使って楽をしたいのに、結局こっちが監督している。

## 1. 複雑になるほど無視する

![](https://assets.st-note.com/img/1779542986-8lCxhGL6NM5BPd1keYZa9o0s.png?width=1200)

Claude Codeは、指示が複雑になればなるほど記憶が薄れていく感じがあります。

短い修正ならまだいいです。

![](https://assets.st-note.com/img/1779542986-2IUNGztXRY0gjAwWBMdf1yS4.png?width=1200)

これは昔から変わらないClaudeの癖だと思っています。

Claude Codeは、僕の作業だとこの「指示通りにしかやらない感」が目立つようになりました。

人間に頼めば、ここを直したらここも直さないといけないよな、というのは分かります。

でもClaude Codeはそこを毎回言わないと拾わない。

## 2. レート制限がきつい

次にレート制限。

以前から感じていましたが、Claude Codeをちゃんと使うと、週レートがすぐ上限に近づきます。

僕の使い方だと、2〜3日で厳しくなることがありました。

作業が乗ってきたところで止まる。

数日待つ。

だるい。

これは複雑な作業を頼むほど起きやすいです。

Claude公式ヘルプにも、Claude CodeはPro/Maxプランの利用上限をClaude本体と共有すると書かれています。

Use Claude Code with your Pro or Max plan

従量課金やプラン変更をすればいいのかもしれませんが・・

でも、そこまでしたくないんですよね。

その点、Codexは今のところ僕の使い方だとレート制限をそこまで気にせず使えています。

まあ、さすがに1日中使いっぱなしにすればなくなりますけどね。

## 3. Claudeは1問1答。Codexは丸ごと

![](https://assets.st-note.com/img/1779542986-Aa78pVFxhrGOmEvIjCY9ugRB.png?width=1200)

それぞれのAIの癖として、Claude Codeは1問1答。

「ここ直して」

「直しました」

これで終わりやすい。

複雑な作業は、それではダメ。

アプリの保存処理を直すなら、保存ボタンだけ見ればいいわけではありません。

入力欄、エラー表示、一覧への反映、テスト、関連ファイル。

このへんまで見ないと、保存処理を直したとは言えません。

Claude Codeはそこが弱いです。

こいつは指示通りにしかやらないな・・と思うことが増えました。

Codexはどちらかというと、人間寄りです。

「ここを直して」と言うと、関連するファイルや確認作業まで見に行かせやすい。

ファイルを読んで、直して、コマンドを実行して、ログを見て、もう一回直して、最後に確認結果を出す。

この流れが作りやすいです。

OpenAIのCodex紹介でも、Codexはバグ修正、コードベースへの質問、テスト実行、PR提案まで行うエージェントとして紹介されています。

Codex | OpenAI Developers

1問1答でじっくりやりたいならClaude。

まとめて細部まで確認して、まるっとやってほしいならCodex。

この辺は自分の好みですね。

## 4. Codex周辺機能の充実

![](https://assets.st-note.com/img/1779542987-yXLINdJSMgZx4cbCVi1qaoDQ.png?width=1200)

最近はCodex周りが盛り上がっています。

アプリ、CLI、IDE拡張、スキル、プラグイン、Automations、ブラウザ操作。

このへんがだいぶ揃ってきました。

だいたいClaudeでできることはCodexでもできます。

だったら、もうCodexに乗り換えるしかないでしょ、という感じです。

僕がやりたいのは、ただコードを書かせることではありません。

記事を書くなら、調査して、画像を作って、表を作って、ブラウザで確認して、ファイルへ保存するところまで頼みたい。

Claude Codeだと、このへんがどうしてもつぎはぎになります。

Codexは最初から作業場に入れてしまえる感じがある。

## 5. 画像生成を自前でできないのも痛い

Claudeで地味にストレスだったのが画像生成です。

Claude Codeでは、精度のいい画像生成を自前で回す感じではありません。

記事を書くならカバー画像がいります。

図解も欲しい。比較表も画像化したい。アイキャッチも作りたい。

でもClaude側だけでは完結しにくい。

結局、別の画像生成を使うことになります。

僕もClaudeからCodex CLIを介してGPT Image系を使うようなことをしていました。

それなら最初からCodexでいいじゃん、となります。

文章、コード、画像、ブラウザ確認。

これを同じ側でできる方が楽です。

毎日使うなら、この楽さは大事です。

## 6. 課金も地味に高い

課金も地味に気になります。

ClaudeのProは公式価格だと月払い20ドル、年払い割引で月あたり17ドルです。

Claude pricing

ここだけ見ると、まあ普通です。

でも、Claudeは日本向けに消費税10%が乗るようになりました。

Impress Watchでも、Anthropicが2026年4月1日から日本の顧客向けに10%の消費税を別途徴収すると出ています。Claudeの全プラン価格に10%が加算され、APIも対象です。

Claude、4月1日から消費税10%を徴収開始

同じ20ドルに見えても、日本で払うなら消費税分高い。

20ドルなら22ドル。

100ドルなら110ドル。

地味ですが、毎月払うと気になります。

しかも僕の中では、最近のClaude Codeは納得感が落ちています。

複雑な作業で鈍る。レート制限も気になる。画像生成も別で考える。指示通りにしか動かない場面も増えた。

そのうえ税込みで高くなる。

これで多めに払う意味ある？となりました。

所詮2ドル前後かもしれません。

でも、性能の落ちるものに消費税分まで乗せて払うのは微妙です。

## 7. Claudeで使っていたものはCodexへ引っ越しできる

乗り換えで気になるのは、今までClaude Code側で使っていたものです。

作業ルール、コマンド、MCP設定、プロンプト、プロジェクトごとのメモ。

これを全部ゼロから作り直すのはめんどくさい。

でも、Claude CodeからCodexへ引き継ぐ方法は出てきています。

こちらの記事では、Claude Codeの制限に達したときにCodexへ引き継ぐ方法として、CLIツール、Codexアプリのインポート、設定ファイルの手動移行が紹介されています。

Claude Codeの制限に達したら？Codexに引き継ぐ3つの方法

引き継ぎできるのはよかったです。

Claude Codeに閉じ込められている感じがない。

移れるなら移ればいい。

## 8. Googleの新AI発表

Google I/O 2026では、Gemini 3.5、Antigravity 2.0、Gemini Omni、Google AI Studio、Google Flow、検索、Workspace、YouTube、Android XRグラスまで発表されています。

Google I/O 2026で発表されたことすべて

Google公式でも、Gemini 3.5 Flash、Antigravity 2.0、Managed Agents、AI StudioのAndroidバイブコーディングが出ています。

Google I/O 2026 デベロッパー向けハイライト

Antigravity 2.0やManaged Agentsは、CodexやClaude Codeを使っている人なら気になる内容です。

僕も触りました。

ただ、今のところメインを変えるほどではありません。

Codexとの比較は別記事でやります。

## まとめ

- Claude Codeは、複雑になるほど鈍る。

- 指示通りにしか動かない場面が増えた。

- レート制限もきつい。

- 画像生成も自前でやりにくい。

- Claudeは日本だと消費税10%分も高くなった。

- Google比較は別記事でやる。

- メインで使うなら、僕はCodex。

迷っているなら、少し面倒な作業を両方に投げてみるといいです。

複数ファイルにまたがる修正。

保存処理、エラー表示、一覧反映、テストまで絡むやつ。

ここで差が出ます。

## 参考にしたい本

Claude Code側を整理したい人はこちら。

[Claude Code](https://www.amazon.co.jp/s?k=Claude+Code+AI%E9%A7%86%E5%8B%95%E9%96%8B%E7%99%BA%E5%85%A5%E9%96%80&tag=blackpokonyan-22)[による](https://www.amazon.co.jp/s?k=Claude+Code+AI%E9%A7%86%E5%8B%95%E9%96%8B%E7%99%BA%E5%85%A5%E9%96%80&tag=blackpokonyan-22)[AI](https://www.amazon.co.jp/s?k=Claude+Code+AI%E9%A7%86%E5%8B%95%E9%96%8B%E7%99%BA%E5%85%A5%E9%96%80&tag=blackpokonyan-22)[駆動開発入門を](https://www.amazon.co.jp/s?k=Claude+Code+AI%E9%A7%86%E5%8B%95%E9%96%8B%E7%99%BA%E5%85%A5%E9%96%80&tag=blackpokonyan-22)[Amazon](https://www.amazon.co.jp/s?k=Claude+Code+AI%E9%A7%86%E5%8B%95%E9%96%8B%E7%99%BA%E5%85%A5%E9%96%80&tag=blackpokonyan-22)[で探す](https://www.amazon.co.jp/s?k=Claude+Code+AI%E9%A7%86%E5%8B%95%E9%96%8B%E7%99%BA%E5%85%A5%E9%96%80&tag=blackpokonyan-22)

Claude Codeの基本、GitHub Actions、サブエージェント、セキュリティ設計まで見られます。

離れるにしても、何が得意だったのかを整理するにはちょうどいいです。

Codex / OpenAI側を見たい人はこちら。

[OpenAI / ChatGPT](https://www.amazon.co.jp/s?k=OpenAI+GPT-5+ChatGPT+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0%E5%AE%9F%E8%B7%B5%E5%85%A5%E9%96%80&tag=blackpokonyan-22)[の開発本を](https://www.amazon.co.jp/s?k=OpenAI+GPT-5+ChatGPT+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0%E5%AE%9F%E8%B7%B5%E5%85%A5%E9%96%80&tag=blackpokonyan-22)[Amazon](https://www.amazon.co.jp/s?k=OpenAI+GPT-5+ChatGPT+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0%E5%AE%9F%E8%B7%B5%E5%85%A5%E9%96%80&tag=blackpokonyan-22)[で探す](https://www.amazon.co.jp/s?k=OpenAI+GPT-5+ChatGPT+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0%E5%AE%9F%E8%B7%B5%E5%85%A5%E9%96%80&tag=blackpokonyan-22)

Codex専門書というより、OpenAI側で開発する入口として見る本です。

これからCodex寄りに作業環境を変えるなら、OpenAI側の考え方に慣れておくのはありです。
