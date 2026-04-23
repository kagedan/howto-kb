---
id: "2026-03-19-完全解説claude-coworkの始め方windowsmac対応セットアップガイド2026年3月版-01"
title: "【完全解説】Claude Coworkの始め方｜Windows・Mac対応セットアップガイド（2026年3月版）"
url: "https://note.com/matomarusan/n/n30ab3e97758f"
source: "note"
category: "cowork"
tags: ["cowork", "note"]
date_published: "2026-03-19"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

「Claudeに仕事を丸ごと任せて、終わったら結果だけ受け取る」——そんな働き方を実現するのが **Claude Cowork** です。

本記事は、私が毎日noteで配信している **「AI活用最前線」シリーズ** の前提知識編です。このシリーズでは、曜日ごとに以下のテーマでClaude Coworkの実践的な使い方をお届けしています。

毎日の記事テーマ  
月曜日｜営業・顧客対応の自動化  
火曜日｜資料作成・レポートの自動化  
水曜日｜マーケティング・広報の自動化  
木曜日｜経営判断・データ分析の自動化  
金曜日｜全社業務プロセスの自動化  
土曜日｜週まとめ＆来週の自動化チャレンジ  
日曜日｜Claude Code/Coworkで会社を丸ごと管理（研究レポート）

月〜金は業務シーン別のAI活用、土曜は週の振り返り、日曜はClaude Code/Cowork特化の研究テーマという構成です。

▶ シリーズ一覧はこちら：[**https://note.com/matomarusan**](https://note.com/matomarusan)

毎日の記事では「フォルダにテンプレートを置いて、CLAUDE.mdで指示を書いて、Coworkに実行させる」という流れが繰り返し登場します。**本記事は、その土台となる環境構築を解説するもの**です。

プログラミングやターミナルの知識は**一切不要**。この記事の手順どおりに進めれば、30分以内にCoworkが使える状態になります。

---

## そもそもCoworkって何？

Claude Coworkは、2026年1月にAnthropicがリリースした **Claude Desktopアプリ内の機能** です。通常のChatモード（質問→回答の往復）とは根本的に異なります。

**Chatモード：** あなたが質問し、Claudeが答える。出力はチャット画面上のテキスト。ファイルが欲しければ自分でコピペして保存する必要がある。

**Coworkモード：** あなたが「こういう成果物を作って」と依頼し、Claudeが計画→実行→ファイル保存まで自律的にやり切る。完成したファイルはあなたのPC上のフォルダに直接保存される。

たとえば「このフォルダの情報をもとに、今週のSNS投稿案を5日分作って」と頼むと、Claudeがフォルダ内のファイルを読み、投稿案を生成し、指定した出力フォルダにMarkdownファイルとして保存してくれます。あなたはその間、別の仕事をしていてOKです。

Anthropicの公式ヘルプでも、Coworkは「成果を伝えて、席を離れて、戻ってきたら仕事が終わっている」という使い方が想定されています（出典：Anthropic公式ヘルプ「Get started with Cowork」 [https://support.claude.com/en/articles/13345190-get-started-with-cowork ）](https://support.claude.com/en/articles/13345190-get-started-with-cowork)

---

## 必要なもの（Windows・Mac共通）

Coworkを使い始めるには、以下の3つが必要です。

**① Claude Desktopアプリ** ブラウザ版（claude.ai）ではCoworkは使えません。必ずデスクトップアプリが必要です。

**② 有料プラン（Pro以上）** Coworkは有料プラン限定の機能です。対応プランは Pro（月額$20）、Max（月額$100〜$200）、Team、Enterpriseです。無料プランでは利用できません。

**③ インターネット接続** Coworkの作業中は常時インターネット接続が必要です。また、Claude Desktopアプリは作業中ずっと開いたままにしておく必要があります（閉じるとセッションが終了します）。

---

## STEP 1：Claude Desktopアプリをインストールする

### ▼ Macの場合

1. ブラウザで [**https://claude.com/download**](https://claude.com/download) にアクセスします
2. 「macOS」のダウンロードボタンをクリックして、.dmg ファイルをダウンロードします
3. ダウンロードした .dmg ファイルを開きます
4. Claudeアプリのアイコンを「Applications」フォルダにドラッグ＆ドロップします
5. Launchpad または Applications フォルダから **Claude** を起動します

**注意点：** Coworkタブ（後述）を利用するにはApple Silicon（M1以降）が推奨されています。Intel Macでも2026年2月のアップデートで対応済みとの報告がありますが、最新版にアップデートしておくことを推奨します（出典：Paweł Huryn「Claude Cowork: The Ultimate Guide for PMs」 <https://www.productcompass.pm/p/claude-cowork-guide> ）。

### ▼ Windowsの場合

1. ブラウザで [**https://claude.com/download**](https://claude.com/download) にアクセスします
2. 「Windows」のダウンロードボタンをクリックして、インストーラーをダウンロードします
3. ダウンロードした .exe ファイルを実行し、画面の指示に従ってインストールします
4. スタートメニューから **Claude** を起動します

**注意点：**

### ▼ 両OSとも：アカウントにログインする

アプリを起動すると、ログイン画面が表示されます。

ログイン後、有料プラン（Pro以上）に加入していることを確認してください。Settings > Subscription で確認できます。

---

## STEP 2：Coworkモードに切り替える

Claude Desktopアプリを開くと、画面上部にモード切り替えタブが表示されます。

**「Chat」** と **「Cowork」** （環境によっては「Tasks」と表示）の2つのタブがあります。**「Cowork」タブをクリック**してください。

これだけでCoworkモードに入れます。

もしCoworkタブが表示されない場合は、以下を確認してください。

---

## STEP 3：作業用フォルダを作成する

Coworkで最も大切なのは **「どのフォルダで作業するか」を決めること** です。Claudeはあなたが指定したフォルダの中身を読み書きできますが、逆に言えば、指定していないフォルダには触れません。これが安全の仕組みです。

### ChatGPT・Geminiとの決定的な違い

ここが、他のAIツールと最も異なるポイントです。

**ChatGPT / Gemini の場合：** チャット画面でファイルをアップロード → AIが回答をテキストで返す → あなたがその内容をコピペして、自分でファイルに保存する。毎回この手作業が発生します。ファイルを10個処理したければ、10回アップロードして10回コピペです。

**Claude Coworkの場合：** あなたのPC上にあるフォルダをClaudeに渡す → Claudeがフォルダ内のファイルを全部読む → 結果を同じフォルダ（または指定した出力フォルダ）に直接保存する。コピペは一切不要です。

つまり、ChatGPTやGeminiは「チャット画面の中で完結する」のに対し、Coworkは「あなたのPC上のフォルダで完結する」のです。この違いが、毎週・毎月の定型業務を自動化するうえで決定的に効いてきます。

たとえば、毎週月曜にSNS投稿案を作るとき。ChatGPTなら毎回「先週の投稿内容はこうで、ブランドガイドラインはこうで…」と説明し直す必要があります。Coworkなら、フォルダの中にブランドガイドラインとその週のネタを置いておくだけ。Claudeがフォルダを読んで、勝手に投稿案を作って、勝手にファイルとして保存してくれます。

**この「フォルダ」という仕組みが、Coworkの自動化を支える土台**です。だからこそ、最初のフォルダ設計が重要になります。

### ▼ Macの場合

1. Finder を開きます
2. 「書類」フォルダ内などに、新しいフォルダを作成します
3. フォルダ名は日本語でもOKですが、半角英数字が無難です

例：

```
/Users/あなたのユーザー名/Documents/Claude-Workspace/
```

### ▼ Windowsの場合

1. エクスプローラーを開きます
2. 「ドキュメント」フォルダ内などに、新しいフォルダを作成します

例：

```
C:\Users\あなたのユーザー名\Documents\Claude-Workspace\
```

### やってはいけないこと

---

## STEP 4：フォルダをCoworkに指定する

Coworkタブを開いた状態で、画面上の **「Work in a folder」**（フォルダで作業する）をクリックし、STEP 3で作成したフォルダを選択します。

これで、Claudeがそのフォルダ内のファイルを読み書きできるようになります。

---

## STEP 5：グローバル指示を設定する（推奨）

Coworkには「グローバル指示」という機能があります。これは**すべてのCoworkセッションに共通で適用される指示**です。あなたの役職、好みのトーン、出力フォーマットなどを一度書いておけば、毎回説明し直す必要がなくなります。

### 設定方法（Mac・Windows共通）

1. Claude Desktop アプリで **Settings**（設定）を開きます
2. 左メニューから **「Cowork」** を選択します
3. **「Global instructions」** の横にある **「Edit」** をクリックします
4. テキストボックスに指示を入力し、**「Save」** をクリックします

### グローバル指示の例（日本語）

```
# 基本情報
- 私の名前は〇〇です。マーケティング部でSNS運用と広報を担当しています。
- 出力は日本語で行ってください。

# 作業ルール
- 作業を始める前に、必ず計画を見せてください。
- ファイルを削除する前に確認してください。
- 出力ファイルは「出力/」フォルダに保存してください。
- 不明点があれば、推測せずに質問してください。

# 出力フォーマット
- ファイル形式はMarkdown（.md）を基本とします。
- ファイル名は「YYYY-MM-DD_内容.md」の形式にしてください。
```

---

## STEP 6：CLAUDE.mdファイルを作る（Coworkの心臓部）

ここが**Coworkの真価を発揮するポイント**です。

**CLAUDE.md**とは、フォルダ内に置いておくテキストファイルで、Claudeがセッション開始時に自動で読み込む「指示書」です。新しい社員に渡す業務マニュアルのようなものだと考えてください。ただし、この社員は毎朝マニュアルを最初から読み、一言一句忘れません。

Coworkにはセッション間のメモリがないため（前回のセッションで何をしたか覚えていない）、このCLAUDE.mdが「毎回のセッションで一貫した品質を保つ」ための鍵になります（出典：Alex Banks「How to properly set up Claude Cowork」 <https://thesignal.substack.com/p/how-to-properly-set-up-claude-cowork> ）。

### CLAUDE.md の作り方

1. テキストエディタを開きます（メモ帳、テキストエディット、VS Code など何でもOK）
2. 以下の内容を参考に記述します
3. ファイル名を **CLAUDE.md** にして、作業フォルダの直下に保存します

**Mac の場合：** テキストエディットで作成する場合は、「フォーマット」メニューから「標準テキストにする」を選んでから書いてください。リッチテキスト形式だと .md として正しく保存できません。

**Windows の場合：** メモ帳で作成する場合、「名前を付けて保存」の際に「ファイルの種類」を「すべてのファイル (.)」に変更し、ファイル名に **CLAUDE.md** と入力してください（そのままだと .txt が付いてしまいます）。

### CLAUDE.md のテンプレート例

```
# SNS投稿自動生成エージェント

## あなたの役割
あなたは、マーケティング部門のSNS運用担当者です。
入力フォルダの情報を元に、SNS投稿案を生成します。

## 処理ルール
1. 入力/ フォルダの weekly_brief.txt を読む
2. brand_guidelines.md のトーン・禁止事項を必ず守る
3. 各SNS媒体の特性に合わせて投稿を作成する

## 出力フォーマット
- 出力ファイル名：sns_posts_week.md
- 出力先：出力/ フォルダ

## やらないこと
- 実在の企業名・人名を根拠なく出力しない
- ブランドガイドラインに反する内容を含めない
- 投稿の実際の投稿（実行）はしない
```

毎日のシリーズ記事では、テーマに合わせたCLAUDE.mdの具体例をそのまま使える形で掲載しています。まずはこのテンプレートで仕組みを理解し、各記事のCLAUDE.mdに差し替えて使ってください。

---

## STEP 7：フォルダ構成を整える

CLAUDE.mdを置いたら、次にフォルダ構成を整えます。Coworkでの自動化は、このフォルダ構成が全てです。

### 推奨フォルダ構成

```
📁 Claude-Workspace/
├── CLAUDE.md          ← Claudeへの指示書
├── 📁 入力/            ← 毎回あなたが更新するファイルを置く
├── 📁 出力/            ← Claudeが生成したファイルが保存される
├── 📁 テンプレート/      ← 参考にさせたいフォーマット例
└── 📁 参考/            ← 過去のレポートや背景資料
```

このフォルダ構成は、毎日のシリーズ記事で共通のベースになっています。水曜日のSNS投稿自動化も、木曜日のデータ分析も、金曜日の全社プロセス自動化も、すべてこの「入力→CLAUDE.md→出力」の型で動きます。

### フォルダの作り方

**Macの場合：** Finderで作業フォルダを開き、右クリック → 「新規フォルダ」で各サブフォルダを作成します。

**Windowsの場合：** エクスプローラーで作業フォルダを開き、右クリック → 「新規作成」→「フォルダ」で各サブフォルダを作成します。

---

## STEP 8：最初のタスクを実行してみよう

すべての準備が整いました。実際にCoworkにタスクを依頼してみましょう。

1. Claude DesktopでCoworkタブを開く
2. 作業フォルダを選択する（STEP 4で設定済み）
3. テキストボックスに以下のように入力する：

```
このフォルダにある CLAUDE.md の指示に従い、
入力/ フォルダの情報を読んで、
今週のSNS投稿案を自動生成してください。

出力は 出力/ フォルダに保存してください。
```

1. Claudeが計画を表示するので、内容を確認して実行を許可する
2. 完成を待つ（または別の作業をする）
3. 出力/ フォルダに結果ファイルが保存されていることを確認する

---

## 便利な追加設定

### スケジュール実行（定期タスク）

Coworkでは、タスクを定期的に自動実行する「スケジュール機能」があります。たとえば「毎週月曜朝9時にSNS投稿案を生成する」といった設定が可能です。

設定方法：Coworkのテキストボックスで **/schedule** と入力するか、左サイドバーの「Scheduled」から作成・管理できます。

**ただし注意：** スケジュール実行は、PCが起動しており、Claude Desktopアプリが開いている状態でのみ動作します（出典：Anthropic公式ヘルプ <https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-cowork> ）。

### プラグイン

Coworkには、役割や業務に特化した「プラグイン」をインストールできます。マーケティング、財務、法務など、プリセットのスキルセットが用意されています。

設定方法：Settings > Cowork > Plugins からインストールできます（出典：Anthropic公式ヘルプ <https://support.claude.com/en/articles/13837440-use-plugins-in-cowork> ）。

### コネクター（Gmail、Slack、Notionなど）

Coworkは、Gmail、Google Drive、Slack、Notionなど38以上の外部サービスと連携できます。たとえば、Gmailの未読メールを読んでタスクリストを作成する、といった使い方が可能です（出典：FindSkill.ai「Claude Cowork Guide 2026」 <https://findskill.ai/blog/claude-cowork-guide/> ）。

---

## トラブルシューティング

**Q. Coworkタブが表示されない** → アプリを最新版にアップデートしてください。Mac: メニューバーの Claude > Check for Updates。Windows: Help > Check for Updates。

**Q. 「Setting up Claude's workspace」と表示されて待たされる** → 正常な動作です。Coworkが最新版に更新されています。しばらく待ってください。

**Q. タスクの途中でClaudeが止まった** → PCがスリープ状態になったか、アプリが閉じられた可能性があります。アプリを開き直し、サイドバーのタスク履歴から状況を確認してください。

**Q. 使用量の上限にすぐ達してしまう** → Coworkは通常のChatよりもトークン消費が多いです。シンプルな質問はChatモードで行い、Coworkは複雑なタスクに絞って使うことを推奨します。

**Q. Windows ARM64 のPCで使えない** → 現時点ではWindows ARM64は非対応です。x64版のPCが必要です。

---

## Mac vs Windows：Coworkの違いまとめ

🖥 ダウンロード先  
Mac → [claude.com/download（.dmg）](http://claude.com/download%EF%BC%88.dmg%EF%BC%89)  
Windows → [claude.com/download（.exe）](http://claude.com/download%EF%BC%88.exe%EF%BC%89)

🖥 対応アーキテクチャ  
Mac → Apple Silicon（M1以降）推奨、Intel対応済み  
Windows → x64のみ（ARM64非対応）

🖥 Coworkの基本機能  
Mac → ○  
Windows → ○

🖥 Excel/PowerPoint連携  
Mac → ○（Max以上）  
Windows → △（今後対応予定）

🖥 インストール場所  
Mac → Applications フォルダ  
Windows → Program Files

🖥 CLAUDE.md作成  
Mac → テキストエディット（標準テキストモード）or VS Code  
Windows → メモ帳（保存時に「すべてのファイル」指定）or VS Code

基本的なCoworkの機能（フォルダアクセス、タスク実行、スケジュール、プラグイン）はMac・Windowsとも同等です。

基本的なCoworkの機能（フォルダアクセス、タスク実行、スケジュール、プラグイン）は**Mac・Windowsとも同等**です。

---

## 安全に使うための5つのルール

1. **機密情報を入れたフォルダは絶対に指定しない** — 顧客リスト、売上データ、パスワードファイルなどは別の場所で管理してください
2. **CLAUDE.mdに「やらないこと」を必ず書く** — 「競合他社を批判しない」「個人情報を含めない」など、禁止事項を明示すると安全性が上がります
3. **出力は必ず人間が確認してから公開する** — 特にプレスリリースやSNS投稿は、公開前に上長の確認を通してください
4. **定期的にフォルダをバックアップする** — CLAUDE.mdやテンプレートは、一度作ったら何度も使う資産です
5. **Claudeがファイル削除する前には確認プロンプトが出る** — 必ず内容を確認してから「Allow」を押してください

---

筆者が書いたClaude Code実践書が出ました。プログラミング不要、日常タスクの自動化を全35章で解説しています。  
[「めんどくさいことはClaude Codeにまかせよう」（Kindle版）](https://amzn.asia/d/09vOAgrL)  
紹介記事: [その朝の90分、AIに渡したら15分になった——本を書いた話](https://note.com/matomarusan/n/nc3690ace4dbc)

![](https://assets.st-note.com/img/1776736366-dhoBFVXMRrI7yHfNYg134m8t.png?width=1200)

**参考リンク**

Anthropic公式：Get started with Cowork <https://support.claude.com/en/articles/13345190-get-started-with-cowork>

Anthropic公式：Claude Desktop ダウンロード <https://claude.com/download>

Anthropic公式：Use Cowork safely <https://support.claude.com/en/articles/13364135-use-cowork-safely>

本シリーズのnoteアカウント <https://note.com/matomarusan>
