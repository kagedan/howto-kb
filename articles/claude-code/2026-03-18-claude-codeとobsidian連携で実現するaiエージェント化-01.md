---
id: "2026-03-18-claude-codeとobsidian連携で実現するaiエージェント化-01"
title: "Claude CodeとObsidian連携で実現するAIエージェント化"
url: "https://note.com/antrefreepreneur/n/nabdcbc1aa26b"
source: "note"
category: "claude-code"
tags: ["claude-code", "Gemini", "GPT", "note"]
date_published: "2026-03-18"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

生成AIでChat GPT, Gemini, Claudeをそれぞれ使っている人が多いと思います。  
2025年は機能の進化が多すぎて激動の1年でしたが、そろそろ2026年か2027年にシェアの順位や勝者が決まってきそうな展開ではあります。  
しかし、使う側にとっては単体のツールで完結しなくても良いので、「**ClaudeとObsidianを連携**」「**ManusとGeminiを連携**」など複数のツールを連携することも増えてきています。  
単体ではできなかったことが、複数のツールを繋げることでより便利に作業ができて試している方も多いでしょう。  
  
そんな中で情報整理に目を向けると「Obsidianが便利。プラグインも色々試した。でも時間が経つとただのメモアプリになっていた」という方も多いのではないでしょうか。私もそうなりつつありました笑

最近アップデートが目まぐるしい「**Claude Code**」と「**Obsidian**」を連携させることで、個人のPCのデスクトップ内のファイル整理や情報収集がグンと便利になります。実際に使ってみたり顧客の相談にのることで、役に立つ事例もいくつか見つかったので、今回はそれをまとめてみます。

![](https://assets.st-note.com/img/1773811868-rwFVIkCxsve4tY7BLzAUpm3P.png?width=1200)

おすすめの使い方を簡潔にまとめると下記です。本記事の概要を最後まで読んでいただいて、自分のPCである程度扱えるようになってきたら試してみましょう。  
①Obsidian内に .claude/settings.local.json を作成し、自分の役割と技術スタックを記述する 。  
②最も解決したい課題に合わせて「vault-master」か「business-planner」のどちらかのスキルファイルを1つ作成する 。  
③日々のメモを /daily コマンドで作成し、AIとの協働リズムを体感する 。

## Claude Codeの立上げ

まず最初にClaude Codeを使えるようにするためには、デスクトップ用の「**Claude Desktop**」をPCにダウンロードする必要があります。これを公式サイトの「アプリと拡張機能を入手」の遷移先からダウンロードしましょう。

[![](https://assets.st-note.com/img/1773809382-XeERSIZ5sG2OTu1wnyUrb64k.png?width=1200)](https://claude.ai/downloads)

そして、PC内で専用のフォルダを作成して、Claudeを立ち上げると**「チャット」「Cowork」「コード」**の3つに分かれているのが分かるので、アカウントにログインをして「コード」を選びましょう。無料プランでは使用量がかなり制限されてしまうので、**月$20**のプラン、毎日使うなら月$100の有料プランに課金するのがお勧めです。

![](https://assets.st-note.com/img/1773809822-dVXblvGpMjHAkS9xT7Qo13sO.png)

## Obsidian使用のPCフォルダ構成

フォルダ内に第一階層で「.claude/」のフォルダを作成して個人の技術スタックや秘密情報を管理する **settings.local.json** を置くことで、自分独自の環境が構築されます 。下記のように個別のフォルダの役割を認識させるルール設定を行いました。

![](https://assets.st-note.com/img/1773809896-UGiTW9dmjxVRcEOYaIkzQLoJ.png)

この他にも**rules/、commands/** 、**skills/** をフォルダとして配置して、その中にmarpdown形式のテンプレートを順番に追加していくようにすると便利です。これは「.claude」の配下におくかobsidian大元でも良いのですが、前者では隠れファイルとして配置されるので、キーボードで「Ctrl」＋「Shift」＋「.」を同時に押さないと表示されるようになりません。

![](https://assets.st-note.com/img/1773809958-q0M9Ta6Ei2WGoQ5JnuhZc1vO.png)

## 良く使う操作をcommands/化

上記の.claude/commands/ 内に便利なスラッシュコマンドを保存しています。

![](https://assets.st-note.com/img/1773810086-gNU5IrJQV2evCnlFx7yYWP3s.png)

カテゴリーに分けており、これらのMarkdownファイルを扱う際に操作して欲しい内容を定義することで、Obsidian単体で呼び出すよりも深いところまで正確に実行してくれます。例えば次のようなコマンドです。

/daily: 今日のタスク、スケジュール、体調を要約してデイリーノートの雛形を作成  
/inbox-review: Inboxフォルダ内の未整理メモを適切なフォルダへ振り分け提案  
/research: 指定したトピックについて、Vault内の既存メモを横断検索して要約  
/mtg: 会議の生ログから、決定事項、宿題、次回日程を構造化して抽出  
/explain: 難解な技術概念を、自分の過去の知識ベースに合わせて解説  
/gift-ideas: 家族や友人の性格メモから、プレゼントの候補を提案

![](https://assets.st-note.com/img/1773809827-gzyMopR4LJbqSEHsfrTIZGA8.png?width=1200)

## AIの判断基準をrules/化

Vaultのルール（.claude/rules/）に、今までマニュアル化や定義書などで統一ルールを制定していた内容をMarpdown形式のファイルで保存します。

![](https://assets.st-note.com/img/1773810205-3OD6yRfPtMnKmcWbCoidrZJh.png)

このようにすることで、Claude Codeで実行するときにVaultのルール（.claude/rules/）を参照しながら、それに沿った一貫性のある出力ができるようになります。

例えば「フォルダ構造とファイル配置のルール」を下記のように設定することで、乱雑にフォルダ内に保存されたメモも内容をClaude Codeが読み取って推論とともに整理した内容を提案して、利用者が許可すれば進めてくれます。

![](https://assets.st-note.com/img/1773810431-8BpYFWVyHGx9zo2AhemjLX7k.png?width=1200)

その他にも、ルールファイルに「パス情報やAPIキーなどの機密情報は保存しないでください」と伝えてセキュリティ面を意識して機密情報を適切に管理することも重要です。

### 朝の5分を変える /daily

例えば「/daily」 コマンドを実行すると、rule/の内容も参照しながら前日の未完了タスクを自動で引き継いで当日のスケジュールと体調を整理したデイリーノートの雛形が生成されます。最優先事項、行動記録、タスク一覧、振り返りの各セクションが用意され、朝の準備時間が劇的に短縮されます。

### 過去の自分と対話する /research

Obsidianの他にはない価値として蓄積したノート同士のつながりがありますが、これらを「/research」コマンドによってVault内のメモを横断検索して、各ノートから結論と根拠を抽出してまとめてくれます。さらにリンクされていない関連ノートがあれば [[リンク]] 形式でどこに接続したら良いか提案してくれます。これによって、忘れかけていたり整理し損ねていた重要なメモを思い出すきっかけとなり、INPUTの効率が上がります。

![](https://assets.st-note.com/img/1773811373-Qza5JS7wokThrWUlEIV08pO9.png)

## リサーチ情報の管理と循環

「vault-master」と「zettelkasten.md」を活用すれば、日々のリサーチした内容を自分で整理するよりはるかに緻密に管理、変換できます 。

![](https://assets.st-note.com/img/1773811566-ZkgPqFCNBvGmUlsJ2tuaHWdR.png?width=1200)

例えば、新しいAIツールの調査結果をObsidianに投入すると、AIが自律的に「既存の競合ツールとの比較」や「自社スタックへの適合性」を分析します 。もし優れた機能が見つかれば、その機能を自動化するための**新しいコマンド作成を提案**し、重複した古い情報は自動的にアーカイブへ移動させます。こうすることで、常に最新の知恵だけが残る状態を維持できます 。

## まとめ

このようにClaude CodeとObsidianを連携すれば、身近な日々の作業を自動化することができる強力な武器となり得ます 。AIが人間の仕事を代替するようになればOUTPUTが重視されて、その分情報収集や整理などのINPUTは時間をかけずに自動化することが必須になっていくでしょう。そこに追われることから解放されて、より本質的な意思決定やクリエイティブな活動に集中できるヒントに本記事がなれば幸いです。
