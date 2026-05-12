---
id: "2026-05-12-slackgasfreeeで請求業務を9割自動化する話第4回受取請求書の自動処理-01"
title: "Slack×GAS×freeeで請求業務を9割自動化する話【第4回：受取請求書の自動処理】"
url: "https://note.com/craftone/n/n8728adf00752"
source: "note"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "note"]
date_published: "2026-05-12"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

**連載：中小企業・スタートアップの経理業務を自動化する**   
第1回：[設計思想](https://note.com/craftone/n/n804ebe0a5ecd)  
 第2回：[案件獲得フォームと契約書ドラフト等の書類自動作成](https://note.com/craftone/n/nb52637edfccf)   
第3回：[請求書発行フォーム設計とSlack通知の自動化](https://note.com/craftone/n/n4545211f07cd)  
 第4回：受取請求書の自動処理（本記事）

---

  

---

## はじめに

取引先から請求書が届くたびに、以下の作業をしていませんか？

メールを開く。PDFをダウンロードする。上長に転送して承認をもらう。freeeに手動でアップロードする。フォルダに整理して保存する。

これを毎月、請求書の数だけ繰り返す。  
件数が増えるほど抜け漏れも増える。

今回構築したのは、**メールが届いた瞬間に全自動で処理が始まる仕組み**です。

担当者がやることは1つ。SlackでOKを押すだけ。

---

## この記事でできるようになること

* GmailのPDF添付メールを自動検知する
* PDFをGoogle Driveの指定フォルダに自動保存する
* SlackにPDFのリンクつきで通知を送る
* Slackのリアクション（✅/❌）で承認・差し戻しを判定する
* 承認されたPDFをfreeeのファイルボックスに自動アップロードする

対象読者：プログラミング未経験、Googleスプレッドシート経験者  
コードはそのままコピーして使えるように記載しています。

---

## 全体の流れ

```
取引先からPDF請求書がメールで届く
        ↓
GASが定期実行（毎朝9時など）
        ↓
Gmailで未処理メールを検索
        ↓
PDFをGoogle Drive「確認待ち」フォルダに保存
        ↓
SlackにPDFリンクつきで通知
「✅ で承認 / ❌ で差し戻し」
        ↓
担当者がSlackでリアクションをつける
        ↓
GASが定期実行でリアクションを確認
        ↓
✅ → freeeにアップロード → 「取込済み」フォルダへ移動
❌ → 「差し戻し」フォルダへ移動
```

**【税務上のポイント】**   
本フローでDriveに保存・freee会計に転送されたデータは、電子帳簿保存法における「電子取引データ」に該当します。  
freee会計のファイルボックスに正しく取り込むことで、同法の保存要件（検索性の確保・真実性の担保）を効率的に満たすことが可能です。

---

## 事前準備

### Google Driveのフォルダ構成

以下の4つのフォルダを作成してください。

①フォルダ名用途請求書\_確認待ち：受信直後のPDFを一時保存  
②請求書\_取込済み：freeeアップロード済み  
③請求書\_差し戻し：差し戻されたもの  
④請求書\_補足資料：請求書以外のPDF

各フォルダのURLに含まれるID（/folders/〇〇〇の部分）を控えてください。

### Slack Botの準備

Slack APIでBotを作成し、以下のスコープを付与してください。

* chat:write（メッセージ送信）
* reactions:read（リアクション取得）

BotをSlackの対象チャンネルに招待しておくこともお忘れなく

### freee APIの準備

freeeのアプリ管理画面でアプリを作成し、以下の権限を付与してください。

* ファイルボックス：参照・更新
* （オプション）請求書：参照・更新

トークンの取得方法は後述します。

---

## ステップ1：定数の設定

```
// Gmail
const GMAIL_SEARCH_QUERY_RCV = "has:attachment filename:pdf after:2026/04/01 -label:受領済み";

// Slack
const SLACK_BOT_TOKEN_RCV  = "xoxb-xxxxxxxxxxxx";
const SLACK_CHANNEL_RCV    = "C0XXXXXXXXX";

// Google Drive フォルダID
const FOLDER_PENDING  = "確認待ちフォルダのID";
const FOLDER_APPROVED = "取込済みフォルダのID";
const FOLDER_REJECTED = "差し戻しフォルダのID";
const FOLDER_DOCS     = "補足資料フォルダのID";

// Slackリアクション名
const REACTION_APPROVED  = "white_check_mark"; // ✅
const REACTION_REJECTED  = "x";                // ❌
const REACTION_INVOICE   = "page_facing_up";   // 📄
const REACTION_DOCS_MARK = "file_folder";      // 📁
const REACTION_SKIP      = "wastebasket";      // 🗑️

// freee
const FREEE_CLIENT_ID     = "クライアントID";
const FREEE_CLIENT_SECRET = "クライアントシークレット";
const FREEE_REFRESH_TOKEN = "リフレッシュトークン（初期値）";
const FREEE_COMPANY_ID_RCV = "事業所ID";
```

**検索クエリの説明：** -label:受領済みが重複処理を防ぐ最重要条件です。is:unreadは使わないでください。  
既読状態に関わらず「受領済みラベルなし」で絞ることで、処理漏れと重複の両方を防げます。

---

## ステップ2：freeeトークンの自動更新

freeeのアクセストークンは6時間で失効します。  
毎回手動で更新するのは現実的ではないため、リフレッシュトークンを使った自動更新の仕組みを実装します。

**重要なポイントが2つあります。**

1つ目は、リフレッシュトークンは使うたびに新しいものに更新されるため、必ずScriptPropertiesに保存し直す必要があります。  
定数に書いたままにすると、2回目以降のリフレッシュが失敗します。

2つ目は、トリガーが重複実行された場合に同じリフレッシュトークンを2回使ってしまうことがあります。  
LockServiceでこれを防ぎます。

```
function getFreeeAccessToken() {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
  } catch (e) {
    return PropertiesService.getScriptProperties().getProperty("FREEE_ACCESS_TOKEN");
  }

  try {
    const props = PropertiesService.getScriptProperties();
    
    // 有効期限内ならリフレッシュせずそのまま返す（重複リフレッシュ防止）
    const expiry = props.getProperty("FREEE_TOKEN_EXPIRY");
    const now = new Date().getTime();
    if (expiry && now < parseInt(expiry)) {
      return props.getProperty("FREEE_ACCESS_TOKEN");
    }

    const refreshToken = props.getProperty("FREEE_REFRESH_TOKEN") || FREEE_REFRESH_TOKEN;
    const response = UrlFetchApp.fetch(
      "https://accounts.secure.freee.co.jp/public_api/token",
      {
        method: "post",
        muteHttpExceptions: true,
        payload: {
          grant_type:    "refresh_token",
          client_id:     FREEE_CLIENT_ID,
          client_secret: FREEE_CLIENT_SECRET,
          refresh_token: refreshToken
        }
      }
    );

    const data = JSON.parse(response.getContentText());
    if (data.access_token) {
      props.setProperty("FREEE_ACCESS_TOKEN", data.access_token);
      if (data.refresh_token) {
        props.setProperty("FREEE_REFRESH_TOKEN", data.refresh_token);
      }
      // 有効期限を5時間後に設定（6時間有効なので余裕を持たせる）
      const expiryTime = now + (5 * 60 * 60 * 1000);
      props.setProperty("FREEE_TOKEN_EXPIRY", expiryTime.toString());
      return data.access_token;
    }

    return props.getProperty("FREEE_ACCESS_TOKEN");

  } finally {
    lock.releaseLock();
  }
}
```

freeeのリフレッシュトークンは使い捨てです。  
リフレッシュ成功時に発行される新しいトークンを保存し損ねると、次回からAPIが一切動かなくなるため、Propertiesへの保存処理は非常に重要です。

---

## ステップ3：メール検索・PDF保存・Slack通知

```
function checkAndSaveInvoices() {
  let label = GmailApp.getUserLabelByName("受領済み");
  if (!label) label = GmailApp.createLabel("受領済み");

  const threads = GmailApp.search(GMAIL_SEARCH_QUERY_RCV);
  if (threads.length === 0) return;

  for (const thread of threads) {
    // 最初にラベルを付ける（重複処理防止のため処理前に実行）
    thread.addLabel(label);
    thread.markRead();

    for (const message of thread.getMessages()) {
      const pdfs = message.getAttachments().filter(a =>
        a.getContentType() === "application/pdf" ||
        a.getName().toLowerCase().endsWith(".pdf")
      );
      if (pdfs.length === 0) continue;

      const subject    = message.getSubject();
      const from       = message.getFrom();
      const isInvoice  = /請求|invoice/i.test(subject);
      const folder     = DriveApp.getFolderById(FOLDER_PENDING);
      const fileInfos  = pdfs.map(pdf => {
        const file = folder.createFile(pdf.copyBlob().setName(pdf.getName()));
        return {
          name: file.getName(),
          url:  "https://drive.google.com/file/d/" + file.getId(),
          id:   file.getId()
        };
      });

      isInvoice
        ? notifySlackInvoiceBulk(subject, from, fileInfos)
        : notifySlackUnknownBulk(subject, from, fileInfos);
    }
  }
}
```

**ラベルを先に付ける理由：** 処理の途中でエラーが起きた場合でも、ラベルが先についていれば次回実行時に同じメールを再処理しません。  
後でつけるとエラー発生時に重複通知が起きる可能性があります。

---

## ステップ4：Slack通知

請求書と種別不明で通知内容を分けています。

```
// 請求書通知
function notifySlackInvoiceBulk(subject, from, fileInfos) {
  const count = fileInfos.length;
  const fileLines = fileInfos.map((f, i) =>
    "ファイル" + (count > 1 ? (i + 1) + "：" : "：") + "*<" + f.url + "|" + f.name + ">*"
  ).join("\n");

  const text =
    "🧾 *新しい請求書が届きました" + (count > 1 ? "（" + count + "件）" : "") + "*\n" +
    "送信元：" + from + "\n" +
    "件名：" + subject + "\n" +
    fileLines + "\n\n" +
    "✅ で承認 / ❌ で差し戻し";

  postToSlackAndSaveProps(text, fileInfos, "invoice");
}

// 種別不明通知
function notifySlackUnknownBulk(subject, from, fileInfos) {
  const count = fileInfos.length;
  const fileLines = fileInfos.map((f, i) =>
    "ファイル" + (count > 1 ? (i + 1) + "：" : "：") + f.name
  ).join("\n");

  const text =
    "📎 *PDFが届きました（種別不明" + (count > 1 ? "・" + count + "件" : "") + "）*\n" +
    "送信元：" + from + "\n" +
    "件名：" + subject + "\n" +
    fileLines + "\n\n" +
    "📄 請求書 / 📁 補足資料 / 🗑️ スキップ";

  postToSlackAndSaveProps(text, fileInfos, "unknown");
}

// Slack投稿＋メッセージtsをScriptPropertiesに保存
function postToSlackAndSaveProps(text, fileInfos, type) {
  const response = UrlFetchApp.fetch("https://slack.com/api/chat.postMessage", {
    method: "post",
    contentType: "application/json",
    headers: { "Authorization": "Bearer " + SLACK_BOT_TOKEN_RCV },
    payload: JSON.stringify({ channel: SLACK_CHANNEL_RCV, text: text })
  });
  const data = JSON.parse(response.getContentText());
  if (data.ok) {
    PropertiesService.getScriptProperties().setProperty(
      "msg_" + data.ts,
      JSON.stringify({ fileIds: fileInfos.map(f => f.id), type: type })
    );
  }
}
```

**ScriptPropertiesにtsを保存する理由：** Slackのメッセージには固有のタイムスタンプ（ts）があります。  
このtsを使ってリアクションを取得するため、投稿後すぐにScriptPropertiesに保存しておきます。

---

## ステップ5：リアクション確認・freeeアップロード

```
function checkReactions() {
  const accessToken = getFreeeAccessToken();
  const props = PropertiesService.getScriptProperties();

  for (const [key, value] of Object.entries(props.getProperties())) {
    if (!key.startsWith("msg_")) continue;

    const ts   = key.replace("msg_", "");
    const data = JSON.parse(value);

    const result = JSON.parse(UrlFetchApp.fetch(
      "https://slack.com/api/reactions.get?channel=" + SLACK_CHANNEL_RCV + "&timestamp=" + ts,
      { headers: { "Authorization": "Bearer " + SLACK_BOT_TOKEN_RCV } }
    ).getContentText());

    if (!result.ok) continue;
    const reactions = (result.message.reactions || []).map(r => r.name);

    if (data.type === "invoice") {
      const fileIds = data.fileIds || (data.fileId ? [data.fileId] : []);
      if (reactions.includes(REACTION_APPROVED)) {
        fileIds.forEach(id => {
          uploadToFreee(id, accessToken);
          moveFile(id, FOLDER_APPROVED);
        });
        props.deleteProperty(key);
      } else if (reactions.includes(REACTION_REJECTED)) {
        fileIds.forEach(id => moveFile(id, FOLDER_REJECTED));
        props.deleteProperty(key);
      }
    } else if (data.type === "unknown") {
      const fileIds = data.fileIds || (data.fileId ? [data.fileId] : []);
      if (reactions.includes(REACTION_INVOICE)) {
        fileIds.forEach(id => {
          const file = DriveApp.getFileById(id);
          notifySlackInvoiceBulk("（種別選択済み）", "手動分類", [{
            name: file.getName(),
            url:  "https://drive.google.com/file/d/" + id,
            id:   id
          }]);
        });
        props.deleteProperty(key);
      } else if (reactions.includes(REACTION_DOCS_MARK)) {
        fileIds.forEach(id => moveFile(id, FOLDER_DOCS));
        props.deleteProperty(key);
      } else if (reactions.includes(REACTION_SKIP)) {
        fileIds.forEach(id => DriveApp.getFileById(id).setTrashed(true));
        props.deleteProperty(key);
      }
    }
  }
}

// freeeファイルボックスにアップロード
function uploadToFreee(fileId, accessToken) {
  const file = DriveApp.getFileById(fileId);
  UrlFetchApp.fetch("https://api.freee.co.jp/api/1/receipts", {
    method: "post",
    headers: { "Authorization": "Bearer " + accessToken },
    payload: {
      "company_id": JSON.stringify(parseInt(FREEE_COMPANY_ID_RCV)),
      "receipt":    file.getBlob()
    },
    muteHttpExceptions: true
  });
}

// ファイルを指定フォルダに移動
function moveFile(fileId, toFolderId) {
  DriveApp.getFileById(fileId).moveTo(DriveApp.getFolderById(toFolderId));
}
```

---

## ステップ6：トリガーの設定

2つの関数にトリガーを設定します。

1. checkAndSaveInvoices：毎朝9時にメール検索と通知
2. checkReactions：1時間ごとリアクション確認とfreee連携

GASエディタの左メニューから時計アイコン（トリガー）を開き、それぞれ設定してください。

---

## freeeトークンの初期取得方法

初回のみ以下の手順でトークンを取得します。

**1. freeeアプリ管理画面でリダイレクトURIを設定**

<https://app.secure.freee.co.jp/developers/applications>でアプリを開き、リダイレクトURIに以下を設定します。

```
urn:ietf:wg:oauth:2.0:oob
```

**2. 認可コードを取得**

以下のURLにアクセスしてください（クライアントIDを入れてください）。

```
https://accounts.secure.freee.co.jp/public_api/authorize?client_id=クライアントID&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&prompt=select_company
```

**3. GASでトークンに交換**

```
function exchangeAuthCode() {
  const response = UrlFetchApp.fetch(
    "https://accounts.secure.freee.co.jp/public_api/token",
    {
      method: "post",
      muteHttpExceptions: true,
      payload: {
        grant_type:    "authorization_code",
        client_id:     FREEE_CLIENT_ID,
        client_secret: FREEE_CLIENT_SECRET,
        redirect_uri:  "urn:ietf:wg:oauth:2.0:oob",
        code:          "取得した認可コード"
      }
    }
  );
  const data = JSON.parse(response.getContentText());
  if (data.access_token) {
    const props = PropertiesService.getScriptProperties();
    props.setProperty("FREEE_ACCESS_TOKEN", data.access_token);
    props.setProperty("FREEE_REFRESH_TOKEN", data.refresh_token);
    Logger.log("トークンの保存完了");
  }
}
```

認可コードの有効期限は数分です。取得後すぐに実行してください。

---

## よくあるつまずきポイント

**Q1. freeeのトークンがすぐ失効する**

リフレッシュトークンは使うたびに新しいものに更新されます。  
定数に書いたままにすると古いトークンで再リフレッシュを試みてエラーになります。  
必ずScriptPropertiesに保存する設計にしてください。

またトリガーが短時間に重複実行されると、同じリフレッシュトークンを2回使ってしまい失効します。  
LockServiceで同時実行を防いでください。

**Q2. 同じ請求書の通知が2回届く**

検索条件にis:unreadを使っている場合は削除してください。  
既読処理が完了する前に次のトリガーが走ると重複します。  
-label:受領済みだけで十分です。

またラベル付けは処理の**前**に行ってください。処理中にエラーが起きてもラベルがついていれば再処理を防げます。

**Q3. freeeのファイルボックスにアップロードできない**

freeeアプリの権限に「ファイルボックス：参照・更新」が含まれているか確認してください。  
権限を追加した場合は、必ず新しい認可コードでトークンを再取得してください。  
既存のトークンには新しい権限が反映されません。

**Q4. Slackに通知は届くがfreeeにアップロードされない**

checkReactionsのトリガーエラー率を確認してください。  
99%近いエラー率になっている場合、トークンが失効しています。  
exchangeAuthCodeでトークンを再取得してください。

**Q5. 請求書以外のPDF（案内文など）が混ざった場合は？**

本スクリプトでは、件名に『請求』が含まれない場合は『種別不明』としてSlackに通知されます。  
そこで『📁 補足資料』を選択すれば、freeeには飛ばさず、Driveの保管専用フォルダに移動される設計にしています。

---

## まとめ

今回実装した仕組みのポイントをまとめます。

第3回の請求書発行フォームと合わせることで、発行・受領の両方向の請求書処理が自動化できます。

---

## 次回予告

第5回は**freee APIを使った請求書の自動生成**です。

請求書発行フォームに入力した内容をそのままfreeeの請求書下書きとして自動生成する仕組みを解説します。  
取引先の検索・新規登録、明細行の設定、消費税の扱いまで全工程を公開予定です。

なお現在、案件獲得時にfreeeへの取引先自動登録も実装済みです。  
案件獲得→請求書発行→freee自動生成まで、フォーム送信だけで一気通貫する仕組みの全貌は次回でご紹介します。

---

**免責事項**  
本記事の内容は執筆時点（2026年5月12日）の情報に基づいています。  
各ツールのAPI仕様・利用規約は変更される場合があります。  
本記事を参考に実装される際は、最新の公式ドキュメントをご確認ください。  
本記事で公開するサンプルコードは、私的利用または自社内での業務改善目的において自由にご利用・改変いただけます。  
ただし、本コードをそのまま転売することや、二次配布することはご遠慮ください。  
また、顧客の個人情報（メールアドレス等）を扱うため、Slackのチャンネル閲覧権限やスプレッドシートの共有設定は、必要最小限のメンバーに限定してください

---

CRAFT ONE合同会社では、バックオフィス業務の代行・自動化支援を行っています。お気軽にご相談ください。

![](https://assets.st-note.com/img/1778547786-Xm9AQsOzLJStIMjfZ2n86rVK.png?width=1200)

クリックすると弊社HPに遷移します
