---
id: "2026-06-17-claude-codeで勝手に高額課金される私がcodexに確認させた課金リスク-01"
title: "Claude Codeで勝手に高額課金される？私がCodexに確認させた課金リスク"
url: "https://note.com/renkon40/n/n445769312d3b"
source: "note"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "GPT", "note"]
date_published: "2026-06-17"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

![](https://assets.st-note.com/img/1781633372-oJCbFfuG6yIiAtXpv1jD54Qc.png?width=1200)

こんにちは、れん学長です（2026年6月17日時点）。

Xで、Claude Codeまわりの課金に関する注意喚起が流れてきました。

きっかけになったポストはこちらです。

https://x.com/beku\_ai/status/2066383281470451818?s=46&t=mixAmHANimvjcgX-2NMVvg

こういう話を見ると、正直ちょっと不安になりますよね。

「いつも通りClaude Codeを使っていただけなのに、設定次第で数十万円単位の請求になることってあるの？」

「自分はサブスクで使っているつもりだけど、どこかでAPI課金に切り替わっていない？」

特に私は、メンバーシップ向けにClaude CodeやCodexで使うスキルも配布しています。

なので、自分だけの話ではなく、読んでくれている方の環境でも事故が起きないかを確認しておく必要があるなと思いました。

そこで今回は、Xポストを起点に、Codexに自分のローカル環境とClaudeまわりの設定をチェックさせました。

途中でAgent SDKや claude -p という聞き慣れない言葉も出てきますが、知らなくても大丈夫です。

あとで「何に使うものなのか」「どんなときに課金されるのか」まで、順番に整理します。

この記事では、次のことを整理します。

* 今回の問題は、そもそも何なのか
* 2026年6月17日時点で、Anthropic公式では何が一時停止されているのか
* claude -p、Claude Agent SDK、GitHub Actions、第三者アプリは何が違うのか
* ANTHROPIC\_API\_KEY が未設定なら本当に安心なのか
* 私が配布した parallel-infographics は、Claude Codeで使っても大丈夫なのか
* あなたが自分の環境でそのまま使えるチェック用プロンプト

先に結論を言うと、Claude Codeが急に勝手に高額課金する、という単純な話ではありません。

ただし、AIエージェント時代は課金経路が複数あります。

なので、「Claude側だけ見ればOK」でもないし、「このMacにAPIキーがなければ絶対に安心」とも言い切れません。

ここを一緒に整理していきましょう。

## まず重要な訂正です

![](https://assets.st-note.com/img/1781633372-j35svx4OflQZMiIHw97c68Lh.png?width=1200)

今回いちばん大事なのはここです。

2026年6月17日時点のAnthropic公式では、6月15日に予定されていたClaude Agent SDKまわりの課金変更は一時停止中です。

今は、サブスク認証で使うClaude Agent SDK、claude -p、Claude Code GitHub Actions、SDK経由の第三者アプリ利用は、基本的には従来どおりサブスクの使用制限から消費されます。

公式ページはこちらです。

<https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan>

つまり、現時点の結論はこうです。

「6月15日からAgent SDKや claude -p が必ず別課金になった」という話ではありません。

サブスク認証で使う分は、今はまだ従来どおりサブスクの使用制限から消費されます。

また、Anthropic公式には、今後アップデートがある場合は、何かが有効になる前に共有すると書かれています。

つまり、現時点では「いつから再開される」と決まっているわけではありません。

だからこそ、今のうちに自分がどの認証でClaudeを使っているのか、どこにAPIキーや利用クレジットの設定があるのかを把握しておくのが大事です。

これは、「いつ再開されるか分からないから今すぐ高額請求に怯えよう」という話ではありません。

仕様が動いても慌てないように、課金経路を見える化しておこう、という話です。

ただし、注意は必要です。

理由は、6月15日の変更とは別に、今でも残っている課金経路があるからです。

たとえば、APIキーを設定している場合、Claudeの利用クレジットで続ける場合、GitHubや第三者アプリ側にAPIキーを入れている場合は、サブスクとは別の課金経路が出てきます。

なのでこの記事で言いたいことは、

「課金変更が一時停止中だから完全に安心」

でもなく、

「Claude Codeを使うだけで危ない」

でもありません。

どの認証で、どのサービスを、どこから呼んでいるのかを、一度ちゃんと確認しておきましょう、という話です。

## 私が最初にCodexへ投げたプロンプト

![](https://assets.st-note.com/img/1781633372-mtSfyUw73zgehaIJcdkujDbQ.png?width=1200)

今回、最初からきれいな監査プロンプトを投げたわけではありません。

実際には、かなり素朴にこう聞きました。

> クロードコードで使うときに、以下の記事にあるようなことが起こって勝手に課金されちゃう可能性がないか調べて。  
> https://x.com/beku\_ai/status/2066383281470451818?s=46&t=mixAmHANimvjcgX-2NMVvg

これだけです。

で、そこから追加で、

* 私のMacにAnthropicのAPIキーが入っていないか
* ClaudeのUsage画面では何が有効になっているか
* ccusage のドル表示は実請求なのか
* parallel-infographics でCodexを呼ぶときはどこが消費されるのか

を順番に確認していきました。

この流れなら、確認場所を整理しながら点検できます。

自分で設定画面を全部思い出して確認するより、まずAIに「見るべき場所」を洗い出させる。

そのうえで、APIキーやトークンの中身は絶対に表示させず、setかunsetだけ確認する。

この流れにすると、かなり安全に点検できます。

## 今回名前が出てきた4つを整理します

![](https://assets.st-note.com/img/1781633372-GcwheAB5ZsfaD8uWi3IP42op.png?width=1200)

今回の話でややこしいのは、似た名前のものがいくつも出てくることです。

非エンジニアの方にも分かるように、まず4つに分けて説明します。

順番は、今回の課金変更の中心にあるClaude Agent SDKから見ていきます。

そのうえで、claude -p、GitHub Actions、外部アプリを「その周辺の使い方」として見ると整理しやすいです。

## 1. Claude Agent SDK

![](https://assets.st-note.com/img/1781633372-NCHdh7KR6vwk9fDPnWi8Tyos.png?width=1200)

Claude Agent SDKは、Claude Codeのように、ファイルを読んだり、コマンドを実行したり、作業を進めるAIエージェントを自作アプリに組み込むための開発キットです。

SDKは、Software Development Kitの略で、開発者が機能を組み込むための部品セットのようなものですね。

非エンジニア向けに言うなら、「Claude Codeっぽい作業ロボットを、自分のアプリや社内ツールに入れるための部品」です。

使う場面としては、こういうものがあります。

まず大事なのは、SDKだから必ず追加課金、ではないということです。

ここでは、予定変更とAPIキー利用を分けて見ます。

一時停止された予定変更では、サブスク認証のAgent SDK利用をサブスク枠から外し、Agent SDK用の月間クレジット側に回す予定でした。

ただし現時点では、その変更は止まっています。

サブスク認証で使う場合、今は従来どおりサブスク使用制限から消費されます。

APIキーで使う場合はAPI課金です。

つまり、見るべきポイントは「SDKかどうか」ではなく、「どの認証で使っているか」なんです。

## 2. claude -p

![](https://assets.st-note.com/img/1781633372-npHPsTUoC1l3VuFRZrxtWOYJ.png?width=1200)

次が claude -p です。

claude -p は、Claude Codeを画面で会話せず、1回だけ命令して結果を返すモードです。

たとえば、コマンドを打ち込む画面やスクリプトから、

> このファイルを要約して

> このフォルダをチェックして

> 毎朝レポートを作って

みたいに呼び出す使い方ですね。

使う場面としては、こんなものがあります。

* レポートを自動生成します
* ファイルをまとめてチェックします
* 毎朝の要約を作ります
* スクリプトからClaudeを呼びます

課金や消費の見方はこうです。

ここは、2つの話を分けると分かりやすいです。

1つ目は、今回一時停止された予定変更です。

もともと6月15日からは、サブスク認証で使う claude -p がサブスク枠ではなく、Agent SDK用の月間クレジット側に回る予定でした。

そのクレジットを超えた分は、利用クレジットを有効にしていればAPI単価で消費される、という設計でした。

ただし、2026年6月17日時点ではこの変更は一時停止中です。

なので今は、Claudeサブスクでログインしていれば、従来どおりサブスク枠を消費します。

2つ目は、APIキーを設定している場合です。

ただし、ANTHROPIC\_API\_KEY が設定されている場合はAPI課金になります。

APIキーというのは、プログラムやコマンドからClaudeを呼ぶための鍵のようなものです。

これは今回一時停止された変更とは別に、もともとある認証の優先ルールです。

さらに、サブスク上限後に「利用クレジットで続ける」を選ぶと、API単価でクレジット消費になります。

## 3. Claude Code GitHub Actions

![](https://assets.st-note.com/img/1781633372-glMnV0o2Qi8TRWk4HqCN7axc.png?width=1200)

Claude Code GitHub Actionsは、GitHub上でClaudeを自動実行する仕組みです。

GitHubは、コードやプロジェクトをネット上に置いておく場所です。

Actionsは、その中で「こういうことが起きたら、この処理を自動で走らせる」と決めておく機能です。

たとえば、こんな使い方をします。

* 誰かがコードの変更案を出したら、Claudeに内容をチェックさせます。エンジニア向けに言うと、PRレビューです
* GitHub上の相談コメントをきっかけに、Claudeにプログラムや設定ファイルの修正案を作らせます。エンジニア向けに言うと、Issueコメントから修正を走らせる使い方です
* コードを公開する前の自動チェックの中で、Claudeにも確認してもらいます。エンジニア向けに言うと、CIの中でClaudeを動かす使い方です

ここはかなり注意です。

Claude Code GitHub Actionsも、一時停止された予定変更の対象に含まれていました。

公式の変更予定では、Agent SDK用の月間クレジット側に回る対象として説明されていました。

ただし現時点では、この変更は止まっています。

一方で、GitHub Actionsは多くの場合、GitHub Secretsに ANTHROPIC\_API\_KEY を入れて使います。

GitHub Secretsは、GitHub側にAPIキーなどの秘密情報を保存しておく場所です。

つまり、あなたのMacでAPIキーが未設定でも、GitHub側にAPIキーが入っていれば、そちらで課金される可能性があります。

ローカル環境だけ見て「自分のMacにはAPIキーがないから大丈夫」と判断すると、ここを見落とすんですよね。

## 4. Claude連携の外部アプリ

![](https://assets.st-note.com/img/1781633372-RfY2QXvOFKISHLDWwht4iuU1.png?width=1200)

最後が、Claudeと連携して作業してくれる外部アプリです。

たとえば、ブラウザ上の自動化ツールや、開発支援サービスの中にClaudeが組み込まれているケースですね。

こういうアプリの中には、裏側でAgent SDKを使ってClaudeを動かしているものがあります。

ここでいうAgent SDKは、外部アプリがClaudeを呼び出して作業させるための開発用の部品セットです。

使う側のあなたがSDKを直接触る、という意味ではありません。

Claudeアカウントでログインして使うものもあれば、自分のAPIキーを入れて使うものもあります。

使う場面としては、こういうものですね。

* 外部の自動化ツールを使います
* Claude連携アプリを使います
* エージェント型の開発支援サービスを使います

ここも同じです。

一時停止された予定変更では、Claudeサブスクで認証する第三者アプリの利用も、Agent SDK用の月間クレジット側に回る予定でした。

ただし現時点では、その変更は止まっています。

Claudeサブスク認証なら、従来どおりサブスク枠を消費します。

APIキーをアプリに入れたならAPI課金になります。

さらに、アプリ独自の課金体系がある場合もあります。

なので、ここも「ClaudeっぽいからClaudeサブスクだけ」とは限りません。

どのログイン方法なのか、APIキーを入れたのか、アプリ側の料金はどうなっているのかを分けて見る必要があります。

## ANTHROPIC\_API\_KEYが未設定なら絶対安全なのか？

![](https://assets.st-note.com/img/1781633372-AhT7E85b6GeotRN2DqBSQvJu.png?width=1200)

ここ、今回いちばん誤解しやすいところです。

質問への答えは、

> このMacに ANTHROPIC\_API\_KEY が設定されていなければ、それら全部から絶対に課金されない

ではありません。

正しくはこうです。

このMacの ANTHROPIC\_API\_KEY が未設定なら、Claude Codeが勝手にローカルAPIキー課金へ切り替わるリスクはかなり下がります。

でも、それだけでは全部の確認にはなりません。

別に見るべき場所があります。

* GitHub SecretsにAPIキーが入っていないかを確認します
* 第三者アプリ内にAPIキーを入れていないかを確認します
* .env という設定ファイルにAPIキーが入っていないかを確認します
* クラウド環境変数にAPIキーが入っていないかを確認します
* まずClaude Webの Settings > Usage で利用クレジットを確認します
* API課金用のClaude Consoleを使っている人は、Console側の支払い設定や自動チャージも確認します

利用クレジットも大事です。

これは、サブスク上限に達したあとも作業を続けるための仕組みです。

便利なんですが、標準API料金で消費されます。

サブスク上限後に「利用クレジットで続ける」を明示的に選ぶと、APIキーがなくてもクレジット消費になる可能性があります。

Claude/Anthropic側で見るべき場所は、まず3つです。

* Claude Codeでは /status を確認します
* Claude Webでは Settings > Usage を確認します
* GitHubではプロジェクトや組織のSecretsを確認します

Claude Code with Pro/Maxの公式説明はこちらです。

<https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan>

APIキーが優先される公式説明はこちらです。

<https://support.claude.com/en/articles/12304248-manage-api-key-environment-variables-in-claude-code>

利用クレジットの公式説明はこちらです。

<https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans>

## 私の環境ではどうだったか

![](https://assets.st-note.com/img/1781633372-xogNYrfS9MidzUF4VanAbOWG.png?width=1200)

今回、私のMacでも再確認しました。

2026年6月17日時点で、このシェル環境では次の状態でした。

* ANTHROPIC\_API\_KEY は未設定でした
* ANTHROPIC\_AUTH\_TOKEN は未設定でした
* ANTHROPIC\_BASE\_URL は未設定でした

つまり、少なくともこのMacのClaude Codeが、環境変数のAPIキーを優先してAPI従量課金に切り替わる状態ではありませんでした。

また、ClaudeのUsage画面では、利用クレジットの残高、月間上限、自動チャージ状態、今月の使用額を確認しました。

私の確認時点では、自動チャージはオフでした。

## ccusageの数字は「請求額」ではなく「見積もり」として見る

![](https://assets.st-note.com/img/1781633372-KqFBZJQNdHMvSO2G9boiaW4P.png?width=1200)

ここで誤解しやすいのが、ccusage のドル表示です。

ccusage は、Claude Code利用者の間でよく使われている利用量チェックツールです。

Claude Codeの使用履歴をAPI単価で換算して、目安のドル表示を見せてくれます。

これは便利なんですが、表示されているドルが、そのまま実際の請求額とは限りません。

サブスクで使っている分も、API単価に置き換えて見積もることがあるからです。

なので、ccusage の数字だけを見て、

「もう請求されている！」

と判断するのは危ないです。

実際の請求やクレジット消費は、まずClaude WebのUsage画面で確認します。

API課金用のClaude Consoleを使っている人は、Console側の支払い設定や自動チャージも別に確認してください。

同じように、Codex/OpenAI側もClaude側とは分けて見ます。

Codex/OpenAI側では、OPENAI\_API\_KEY の有無とCodexの認証状態を別に確認しました。

私の環境では、OPENAI\_API\_KEY は未設定で、CodexはChatGPTログインの認証でした。

## parallel-infographicsは大丈夫なのか？

![](https://assets.st-note.com/img/1781633372-lO43NiPrv7gykUZCEqQsBI6m.png?width=1200)

ここからは、使ってくれているあなたに特に大事な話です。

私はメンバーシップ向けに、parallel-infographics というスキルを配布しています。

<https://note.com/renkon40/n/nf35398101024>

スキルというのは、AIに仕事のやり方を覚えさせる機能です。

parallel-infographics は、記事をイントロ、各章、まとめに分けて、複数のグラレコ画像を並列で作るためのものです。

もともとはCodex用に作りました。

でも、意外と知られていないんですが、Claude Codeからも呼べます。

ここが少しややこしいんですよね。

Claude Codeから呼べるからといって、画像生成までClaudeのサブスク枠だけで完結するわけではありません。

Claude Codeは進行役になれます。

でも、実際の画像生成はCodex側で行われます。

私の環境では、parallel-infographics はAnthropic APIを直接叩く設計ではありません。

ClaudeのAPIキーを使ってClaude APIを直接呼ぶものでもありません。

その意味では、Claude側のAPIキー課金とは別の話です。

ただし、codex app-server というCodexを裏側で動かす仕組みを使います。

なので、Anthropic側の請求ではなくても、Codex/OpenAI側の利用枠やOpenAI側のクレジットは消費しうる。

ここはちゃんと分けて伝えたいところです。

つまり、

> Claude側でAPI課金されない

と、

> 完全に無料で何も消費しない

は別です。

## プレゼン資料作成でもつながっています

![](https://assets.st-note.com/img/1781633372-Cg3rDSaJ1je69tyudc2EVsHX.png?width=1200)

もう一つ、補足しておきたいことがあります。

parallel-infographics は、Note記事用の図解画像を作るだけで終わりません。

下流に infographics-to-pptx というプレゼン資料作成スキルがあります。

画像スライドを編集できるPowerPointに戻す流れは、こちらの記事でも書いています。

<https://note.com/renkon40/n/n5fc957639188>

これは、parallel-infographics が作った note\_infographic\_\*.png を、1枚ずつスライドに変換するためのものです。

必要なら、notebooklm-generate側の Insert.pptx もマージできるため、挿入スライドを合流させられます。

ここでの課金面の見方は、前の章と同じです。

PPTX化そのものより、上流の parallel-infographics で画像を作るときに、Codex/OpenAI側の画像生成枠をどれだけ使ったかを見ます。

## 自分の環境を確認するプロンプト

![](https://assets.st-note.com/img/1781633372-WGJgnjB9VdMKxwUfmZNrHQSz.png?width=1200)

今回のような不安がある方は、下のチェックプロンプトをClaude CodeやCodexに渡して、

「自分の環境ではどうか確認して」

と頼むのも有効です。

もう少し丁寧に聞くなら、次のプロンプトを使ってください。

以下をそのままコピーしてください。

> Claude Code / Codex / AIエージェントの課金リスクを点検してください。

目的: 意図せずAPI課金や利用クレジット消費に切り替わっていないか確認したいです。 確認してほしいこと: Claude Codeが通常のClaudeサブスク利用になっているか ANTHROPIC\_API\_KEY / ANTHROPIC\_AUTH\_TOKEN / ANTHROPIC\_BASE\_URL などが設定されていないか ClaudeのSettings > Usageで、利用クレジット、月間上限、自動チャージがどうなっているか ccusage などの表示額を、実請求と誤解していないか Claude Agent SDK、claude -p、GitHub Actions、第三者アプリがAPI課金やクレジット消費に回る条件 CodexやOpenAI APIを呼ぶスクリプトがある場合、OPENAI\_API\_KEYやCodexログイン認証で別枠の利用枠・OpenAI側のクレジットを消費しないか 注意: APIキーやトークンの値は表示しないでください。set/unsetだけ確認してください。 設定変更や購入はしないでください。読み取り確認だけしてください。 公式ドキュメントと実際のローカル設定を分けて報告してください。

上のプロンプトは日本語のまま使えます。

## 最後にチェックする場所

![](https://assets.st-note.com/img/1781633372-0EeI84Va2iSZJqxXvP1ytcQL.png?width=1200)

最後に、見る場所だけ短くまとめます。

Claude Code側で見るものは、まず /status です。

自分がサブスク認証で使っているのか、APIキー側になっていないかを確認します。

Claude Web側では、Settings > Usage を見ます。

利用クレジット、月間上限、自動チャージ、今月の使用額を確認します。

GitHubを使っている場合は、GitHub Secretsを見ます。

このMacにAPIキーがなくても、GitHub側に ANTHROPIC\_API\_KEY が入っていれば、そちらから使われる可能性があります。

Codexや画像生成を使う場合は、OpenAI側も見ます。

parallel-infographics のようにCodexを呼ぶスキルは、Claude側だけ見ても不十分です。

CodexをChatGPTプランで使っている人は、ChatGPT/Codex側の利用枠を見ます。

OpenAI APIキーを使っている人は、OpenAI Platform側のUsageやBillingを見ます。

Codex with ChatGPT planの説明はこちらです。

<https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan>

Codexの料金説明はこちらです。

<https://developers.openai.com/codex/pricing>

## 動画で見たい方へ

![](https://assets.st-note.com/img/1781633372-twT7WLurJ4IAsl1YVvQD9kon.png?width=1200)

この記事の内容は、画面を見ながら確認した方が分かりやすい部分があります。

特に、Claude WebのUsage画面、Claude Codeの /status、GitHub Secrets、Codex側の利用枠は、実際の画面で見ると一気に理解しやすくなると思います。

動画化したら、ここにリンクを追加します。

## まとめ

![](https://assets.st-note.com/img/1781633372-ELm8Xqj1cW3Gx7IbDlUzHnuN.png?width=1200)

今回の話をまとめると、ポイントは3つです。

* 2026年6月17日時点では、6月15日予定のAgent SDK課金変更は一時停止中です。ただし、再開時期は未定なので課金経路は把握しておくのが大事です
* このMacの ANTHROPIC\_API\_KEY が未設定なら、ローカルAPIキー課金へ勝手に切り替わるリスクはかなり下がります
* ただし、ローカル環境とは別の課金経路は分けて確認してください

要は、Claude Codeが危ないという話ではありません。

AIエージェント時代は、課金経路が複数あるので、「どの課金経路から消費されるのか」を分けて見よう、という話です。

不安な方は、まずこの記事のチェックプロンプトをClaude CodeやCodexに貼って、自分の環境を点検させてみてください。

APIキーの中身は出さず、setかunsetだけ確認する。

これだけでも、かなり安心感が変わると思います。

この記事が役に立ったら、いいねやフォローで教えてもらえると嬉しいです。

「自分の環境だとここが不安」「このツールも課金経路を見てほしい」みたいなものがあれば、コメントで教えてください。次の記事のネタにします。

次回は、AIエージェントに作業を任せるときの安全な設定確認や、Codex/Claude Codeの運用まわりをもう少し掘っていく予定です。

それではまた、れん学長でした！

---

### れん学長のAIツール実験室

![](https://assets.st-note.com/img/1781633372-fjrqLws96gacnk3iKRmHOT8p.png?width=1200)

メンバーシップでは、この記事では書ききれなかった実験ログや、AI活用の試行錯誤をもう少し踏み込んで共有しています。

今回触れた parallel-infographics のような再現キットや、Codex / Claude Codeまわりの検証メモも、必要に応じて整理して置いています。

価格や参加条件、どんな内容が読めるかは、入口記事にまとめています。

気になっていた方は、まず内容をのぞいてみてもらえるとうれしいです。

メンバーシップの入口記事をのぞいてみる

<https://note.com/renkon40/n/nab9c378d2148>

---

[#AI](https://note.com/hashtag/AI) [#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#Codex](https://note.com/hashtag/Codex) [#AIエージェント](https://note.com/hashtag/AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88) [#課金リスク](https://note.com/hashtag/%E8%AA%B2%E9%87%91%E3%83%AA%E3%82%B9%E3%82%AF) [#parallelInfographics](https://note.com/hashtag/parallelInfographics) [#AIツール](https://note.com/hashtag/AI%E3%83%84%E3%83%BC%E3%83%AB) [#自動化](https://note.com/hashtag/%E8%87%AA%E5%8B%95%E5%8C%96)
