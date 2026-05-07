---
id: "2026-05-06-google-chatのapi制限を乗り越えてgithub-copilotに現場の文脈を理解させるa-01"
title: "Google ChatのAPI制限を乗り越えて、GitHub Copilotに「現場の文脈」を理解させるAI同僚を誕生させた話"
url: "https://zenn.dev/matsuken3bar/articles/00da35b7751639"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "Gemini", "VSCode", "Python", "JavaScript"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

今、自分の開発現場では**GitHub Copilot CLI**をAIエージェントとして使用しています。今の現場ではネットの海にある知識やコードの書き方については、彼は最高の相棒です。

しかし、彼には決定的な欠点があります。**「昨日のチャットで決まった仕様変更」や「今朝のMTGでの議論」を知らない**ことです。Gemini CLI のようにGoogle系のAIエージェントだったら多分Google ChatやGoogle Meetとの連携機能とかありそうだけど、今の現場で使えるAIコーディングエージェントはGitHub Copilot CLIなんだよなあ……でも、GitHub Copilotの「GitHubやVSCodeとの連携が強い」という強みも活かしたいから、GitHub　CopilotがGoogle ChatやGoogle Meetの記録を読めるようになったら最高なんだけどなあ……よし！いっちょ作ってみるか！

この「ソースコードやWebに載らない社内知識」という欠けたピースを埋めるために、Google Workspaceの機能をフル活用して自律型ナレッジ基盤を作ってみたので、その泥臭い裏側を共有します。

※注：この記事にはオチがあります。いいから結論を先に知りたいという時間の無い方は、[結論へジャンプ](#6.-%E7%B5%90%E3%81%B3%EF%BC%9Aai%E3%81%AE%E5%90%8C%E5%83%9A%E3%82%92%E4%B8%80%E4%BA%BA%E3%80%81%E9%9B%87%E3%81%A3%E3%81%9F%E6%84%9F%E8%A6%9A%E3%80%82%E3%81%9D%E3%81%97%E3%81%A6%E2%80%A6) をクリックして飛んで下さい。

## **1. 全体アーキテクチャ図**

まずはシステムの全体構成図がこちらです。

## **2. なぜこんな面倒な構成になったのか：GCPという「立ちはだかる壁」**

今の業務では、グループウェアとしてGoogle Workspaceを使用しており、会議はGoogle Meet、コミュニケーションは主にGoogle Chat で行っています。それゆえ当初は「Google MeetやGoogle Chatから直接データを引っこ抜けばいい」と考えていました。そして、Google MeetはGASを使用することで以下のファイルをGoogleドライブに出力することが出来ました

* Meet会議の録画ファイル
* Meet会議の文字起こしテキストファイル
* Meet会議のGeminiによる要約テキストファイル

しかし、現実は甘くありません。問題はGoogle Chatの方で、Google Chat APIを真面目に叩こうとすると、技術的な難易度以上に **Google Cloud Platform (GCP) の運用とセキュリティの壁** が立ちはだかりました。

### **企業のセキュリティポリシーとの衝突**

単にAPIを有効化するだけでは済みません。

* **「チャットアプリ」としての制約**: Google Chat APIは「特定のアプリ（ボット）」として動作することを前提としています。全スペースのメッセージを横断的にさらってバックアップするような「バックグラウンドサービス」を作ろうとすると、**ドメイン全体の委任（Domain-wide Delegation）** という、つよつよ権限が必要になります。

組織の権限設定によっては、個人の開発用ツールに chat.messages.readonly などの強力なスコープを許可されてないこともあるでしょう。自分の職場もグループウェア管理者によってそこはブロックされていました。

Google Chat API が使えないか〜。じゃあ、どうしよう…と思った時に舞い込んできたのが**Google Workspace Studio** の正式リリースというニュースでした。

<https://workspace.google.com/intl/ja/studio/>

Google Workspace Studio とは何かというと

> Gemini を使用して Google Workspace サービス全体で日常の定型的なタスクを自動化できるオンライン アプリです

(引用元: [Google Workspace ラーニング・センター](https://support.google.com/a/users/answer/16430812?hl=ja) )

だ、そうです。（詳しくは上記サイトをご覧下さい。）

この知らせを聞いて私は思いました。「ひょっとして…Google Workspace Studioなら、**標準機能（Flow）でドキュメントとして吐き出させ、そのDocをGASでさらえば、セキュリティの枠組みの中でハックできる**のではないか？」

この発想が、今回の「Docsバッファリング戦略」の始まりでした。

## **3. 【Hack 1】Workspace Studio Flow × Google Docs のバッファリング戦略**

ここで閃いたのが、**Workspace Studio Flow の「Googleドキュメント作成」アクションを一時的なバッファとして使う**アイディアです。

### **Flowの定義**

Workspace Studio（旧称：AppSheet Automation等から進化中）のFlowで、以下のようなフローを組みました。

1. **Trigger**: 「チャットメッセージが投稿されたとき」をフック。
2. **Action**: 特定のフォルダに、メッセージ1件につき1つの **Googleドキュメント** を新規作成。
3. **タブの活用（ここが肝）**: Flowのステップで、ドキュメントに以下のタブを作らせます。
   * message\_text: 本文（リッチテキストもそのまま放り込む）
   * message\_link: 投稿への直リンク
   * sender\_name: 投稿者の名前
   * sender\_email: 投稿者のメールアドレス
   * post\_time: 投稿日時
   * space\_id: スペースの一意識別子
   * space\_name: スペースの名称

完成形は下記の図参照  
![](https://static.zenn.studio/user-upload/1fdfb27ef2fb-20260506.png)  
↑ ご覧の通り、space\_name タブにはスペースの名前が保存されています

この方法に辿り着くまでは、Flowから直接JSONやMarkdownを吐き出そうと試行錯誤していました。しかし、Flowの動的な値埋め込みでは、エスケープ漏れでJSONが壊れたり、Markdownの階層構造が不意に変わったりと、出力がどうしても安定しませんでした。一方、ドキュメントの「タブ」として出力するのはFlowの標準機能そのものであり、どれほど複雑な本文が含まれていてもフォーマットが崩れる余地がありません。

## **4. 【Hack 2】GASによる「集約」と「隔離」の実装**

次に、バラバラに吐き出されたドキュメントをGAS（Google Apps Script）で回収します。ここでのポイントは、AIに読ませるための「マスターJSON」を作る際に、**スペース名などのメタデータを最上位に持たせる**ことです。

### **具体的なGASの実装イメージ（TypeScript）**

AIが「どのファイルを開くべきか」を即座に判断できるよう、JSONの構造を工夫しています。

```
//※ typescriptで書いてるので、トランスパイルしてJavaScriptにしてGASにデプロイします。

// マスターJSONの構造。単なる配列ではなくメタデータを付与。  
interface MasterJson {  
  space_id:   string;  
  space_name: string;  
  last_updated: string;  
  threads:    ChatThread[]; // スレッドごとに集約されたメッセージ  
}

function groupChatLogsByThread(): void {  
  // 1\. バッファ用Docをスキャン  
  const items = readAllMessages(inputFolder);  
    
  // 2\. スペースごとにグルーピングしてJSONを更新  
  items.forEach(item => {  
    const masterData = loadMasterJson(item.space_id);  
    masterData.threads = mergeMessages(masterData.threads, item.message);  
      
    // 3\. 【重要】二重書き出しの実装  
    // 原本（Master）とAI配布用（Distribution）を物理的に隔離  
    writeToFolder(masterFolder, fileName, masterData);  
    writeToFolder(distFolder, fileName, masterData); // ここだけをローカル同期  
  });  
}
```

この「二重書き出し」がミソです。MacのGoogleドライブクライアントでは「配信専用フォルダ」のみを同期します。これにより、ローカルでAIが暴走してファイルを書き換えても、クラウド上のログ原本が破壊されることはありません。

## **5. AIに「自分で資料を探させる」2段階ルーティング**

ログが溜まると数万行になります。これを毎回全部AIに食わせるとトークン代が破産します。

そこで、Pythonで変換する際に **Front Matter（メタデータ）** を付与した小分けのMarkdownファイルと、その地図となる index.md を生成するようにしました。

AIエージェントには、以下のような手順（Skill）を定義しています。

1. **インデックス参照**: まず index.md を読み、質問に関連する「スペース名」や「更新日」から最適なファイルを探す。
2. **ピンポイント参照**: 特定した1つのファイルだけを読み込んで、最終的な回答を出す。

これで「昨日のあの議論について教えて」という質問に対し、AIは数あるスペースの中から**自律的に正しいログを探し出し、回答する**能力を手に入れました。

## **6. 結び：AIの同僚を一人、雇った感覚。そして…**

このシステムのおかげで、僕のGitHub Copilotは「社内の事情に一番詳しいエンジニア」になりました。

* 「なぜこの関数はこんな仕様なの？」と聞けば、過去のチャットの議論から背景を教えてくれる。
* 「昨日のMTGの決定事項、コードに反映して」と言えば、Meetの要約を読んで実装を提案してくれる。

ネットの海だけでなく、**社内の文脈にもアクセスできる**。もはやツールではなく、「**全てを覚えている優秀な同僚**」が一人隣に座っている感覚です。

### **ところで…（落ちパート）**

このシステムを必死に組み上げ、隔離フォルダやインデックス化に知恵を絞っていた時のことです。

ふとニュースを見ると、**「Google Workspace Intelligence」** という新機能の発表がありました。

> Google Chatにおいては、Chat内のGeminiに質問し、重要なタスク、未読のスレッド、緊急のアクションアイテムを提示するデイリーブリーフィングを提供。質問だけでなく、Workspaceのスキルを活用し、複雑なタスクを完了させ、ドキュメントやスライドの作成も行なえる。

(引用元：　[YAHOO!JAPANニュース　グーグル、文書やメールの“文脈”を理解して支援する「Workspace Intelligence」](https://news.yahoo.co.jp/articles/cafad9661e01c2c4e59f19dd3f9edb7a3628b356) )

「あれ…これ、ひょっとしたらこの機能が弊社のGoogle Workspaceにリリースされたら、今回開発した仕組みいらなくなるかもなあ…？？😢」

ひょっとしたら、数ヶ月後には標準機能のボタン一つで実現しているかもしれません。でも、それまでの数ヶ月間、自力でハックした「最強のAI同僚」と一緒に開発できる体験は、何物にも代えがたいものです。

AIエージェントの活用方法を探している皆さん、こんな「力技のハック」で未来を先取りしてみませんか？（もしくはGoogle Workspace Intelligenceがやってくるのを正座して待とう）
