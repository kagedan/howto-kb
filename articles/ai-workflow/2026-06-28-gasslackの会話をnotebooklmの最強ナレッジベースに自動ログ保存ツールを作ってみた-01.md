---
id: "2026-06-28-gasslackの会話をnotebooklmの最強ナレッジベースに自動ログ保存ツールを作ってみた-01"
title: "【GAS】Slackの会話をNotebookLMの最強ナレッジベースに！自動ログ保存ツールを作ってみた"
url: "https://note.com/right_stuff/n/nc6548c0520e9"
source: "note"
category: "ai-workflow"
tags: ["API", "LLM", "note"]
date_published: "2026-06-28"
date_collected: "2026-06-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

「Slackで議論したはずの仕様、どのスレッドだっけ…？」  
「途中からプロジェクトに参加したから、過去の経緯が全くわからない…」

そんな悩みを解決し、話題のAIツール「NotebookLM」に社内の暗黙知をすべて学習させるための\*\*「Slack日次ログ自動保存ツール」\*\*をGoogle Apps Script（GAS）で開発しました。

本記事では、ただログをバックアップするだけでなく、\*\*「AIが文脈を正確に理解できる構造」\*\*にするための設計上の工夫や、GASの実行制限の壁をどう乗り越えたか、そして実際のコードやAI生成用プロンプトまで全公開します。

## 開発の背景と目的

Slackは非常に便利なコミュニケーションツールですが、情報が「フロー」として流れていってしまうため、過去の決定プロセスや有益な知見が埋もれがちです。

最近はこれらをNotebookLMなどのLLM（大規模言語モデル）に読み込ませて「社内専用のAIアシスタント」を作るアプローチが流行っています。しかし、\*\*「Slackの生データ（JSON等）をそのまま投げ込んでも、AIがスレッドの文脈や発言者の関係性を正しく理解してくれない」\*\*という課題がありました。

そこで、AIにとって最高の「ナレッジベース（参照データ）」を自動構築するため、以下の要件を満たすツールを企画しました。

* Slackの会話を、人間にもAIにも読みやすい「Googleドキュメント」形式で出力する。
* 「親メッセージ」と「スレッド返信」の文脈を構造的に維持する。
* メッセージ内の添付ファイルもGoogleドライブに自動保存し、リンクを記載する。
* 毎日自動で最新の差分を追記・更新する。

## Slack Botの作り方の基本と「会社管理」の壁

ツールの開発に入る前に、まずはSlackの会話を読み取るための「Bot（アプリ）」を作成する必要があります。

**■ 一般的なBotの作成手順**

1. [Slack APIの管理画面 (api.slack.com/apps)](https://api.slack.com/apps) にアクセスし「Create New App」をクリック。
2. 「OAuth & Permissions」メニューから、Botに必要な権限（スコープ）を付与する。
3. ワークスペースにインストールし、`xoxb-` から始まる「Bot User OAuth Token」を取得する。

**■ 自分が管理しているSlack（個人・テスト環境）の場合**  
自分が管理者（Admin）であれば、上記の手順をポチポチ進めるだけですぐにトークンが発行され、自由に開発をスタートできます。

**■ 会社が管理しているSlackの場合（ここが重要！）**  
セキュリティがしっかりしている企業の場合、アプリのインストールや権限付与には**情報システム部門（情シス・ICT）の承認**が必要になります。ここで「勝手に怪しいツールを入れようとしている」と思われないための相談・申請のコツを紹介します。

* **必要最小限の権限（Read-only）をアピールする:** 「メッセージを読み取る（history）」と「ファイルを見る（read）」権限だけを申請し、Slackへの書き込み（write）や外部へのWebhook送信は行わないことを明記します。
* **データの保存先を明確にする:** 「取得したログは社内のセキュアなGoogle Workspace上にのみ保存し、外部サービスには流出しない」という点を強調します。
* **先に情シスと会話する:** いきなり無言でシステム申請を出すのではなく、「業務効率化のためにこんなBotを作りたいのですが、どう申請すればスムーズですか？」と事前にヘルプデスクへ相談しておくことで、承認側の安心感が格段に変わります。

## ツールの設計（AI最適化と制限回避の裏技）

無事にトークンを取得できたら、いよいよGASでの開発です。技術的に工夫した3つのコア設計を紹介します。

### 1. AI向けの構造化フォーマット

NotebookLMは、見出しやインデント（字下げ）といった「ドキュメントの階層構造」から文脈を読み取るのが得意です。  
そのため、GASでドキュメントに書き込む際、日付が変わるごとに\*\*「見出し2 (Heading 2)」**を設定し、スレッド内の返信は親メッセージの下に**「36ptの字下げ」\*\*をして書き込む設計にしました。これでAIが「誰のどの発言に対する返信か」を完璧に把握できるようになります。

### 2. 「直近7日間」の変動エリアと確定エリアの分離

Slack最大の厄介な仕様として、「数日前の過去の投稿に、突然スレッド返信がつく」ことがあります。単純に「前日分のログを取る」だけでは、遅れてきた返信を取りこぼしてしまいます。  
そこで、ドキュメント内にマジックワード（区切り線）を設けました。

### 3. GAS「6分タイムアウト」の回避とレジューム機能

初回に数ヶ月分の過去ログを一気に取得しようとすると、GASの「1回の実行は最大6分まで」という制限に引っかかりエラーになります。  
これを防ぐため、実行から4.5分経過した時点で\*\*「最後に取得したメッセージのタイムスタンプ」をシステム（PropertiesService）にセーブして一時停止\*\*する機能を実装しました。再実行すれば、前回の続きから自動でレジューム（再開）します。

---

## サンプルのGASコード

Googleドキュメントを作成し、「拡張機能」＞「Apps Script」を開いて以下のコードを貼り付けます。  
上部の `SLACK\_TOKEN`、`CHANNEL\_ID`、`FOLDER\_ID` をご自身の環境に合わせて書き換えれば、そのまま動きます。

```
// ==================================================
// 設定エリア(ご自身の環境に合わせて書き換えてください)
// ==================================================
const SLACK_TOKEN = 'xoxb-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx'; // Bot User OAuth Token
const CHANNEL_ID = 'CXXXXXXXXXX'; // 対象のSlackチャンネルID
const FOLDER_ID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'; // 添付ファイル保存先のGoogleドライブフォルダID
// ==================================================
const SEPARATOR_TEXT = "[=== ここから下は直近7日間の変動エリア（実行時に上書き更新されます） ===]"; 
const userCache = {};

function onOpen() {
  DocumentApp.getUi().createMenu('🤖 Slack連携') 
    .addItem('📥 手動更新(直近7日間を再取得 / 過去分の続きを取得)', 'menuSync') 
    .addSeparator() 
    .addItem('⚠️ 過去データ全件取得 (初回リセット用)', 'menuSyncAll') 
    .addToUi(); 
}

function menuSync() { syncRoutine(false); } 
function menuSyncAll() { syncRoutine(true); } 

function syncRoutine(isReset) {
  const startTime = Date.now(); 
  const TIME_LIMIT = 4.5 * 60 * 1000; // 4.5分 (タイムアウト回避)

  const doc = DocumentApp.getActiveDocument(); 
  const body = doc.getBody(); 
  const props = PropertiesService.getScriptProperties(); 

  const now = new Date(); 
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0); 
  const ts7DaysAgo = Math.floor((startOfToday.getTime() - 7 * 24 * 60 * 60 * 1000) / 1000); 
  const tsNow = Math.floor(now.getTime() / 1000); 

  let lastCommittedTs = props.getProperty('LAST_COMMITTED_TS') || "0"; 

  if (isReset) {
    const ui = DocumentApp.getUi(); 
    const response = ui.alert('過去データ全件取得', 'ドキュメントを一旦空にして、過去の全履歴を取得します。\n※データ量が多い場合、途中で自動的に一時停止します。\n実行しますか？', ui.ButtonSet.YES_NO); 
    if (response != ui.Button.YES) return; 
    body.clear(); 
    lastCommittedTs = "0"; 
    props.setProperty('LAST_COMMITTED_TS', "0"); 
  }

  let searchResult = body.findText("\\[=== ここから下は直近7日間の変動エリア"); 
  let separatorElement; 
  if (searchResult) {
    separatorElement = searchResult.getElement().getParent(); 
  } else {
    separatorElement = body.appendParagraph(SEPARATOR_TEXT); 
  }

  let insertIndex = -1; 
  let currentPrintedDate = ""; 

  function addPara(text, indentNum, isHeading) {
    let p; 
    if (insertIndex >= 0) {
      p = body.insertParagraph(insertIndex, text); 
      insertIndex++; 
    } else {
      p = body.appendParagraph(text); 
    }
    if (indentNum > 0) p.setIndentStart(indentNum); 
    if (isHeading) p.setHeading(DocumentApp.ParagraphHeading.HEADING2); 
    return p; 
  }

  function writeSingleMessage(msg) {
    if (msg.thread_ts && msg.thread_ts !== msg.ts) return; 

    let msgDate = Utilities.formatDate(new Date(parseFloat(msg.ts) * 1000), Session.getScriptTimeZone(), 'yyyy年MM月dd日'); 
    if (msgDate !== currentPrintedDate) {
      addPara("==================================================", 0, false); 
      addPara(`📅 ${msgDate}`, 0, true); 
      currentPrintedDate = msgDate; 
    }

    let userName = userCache[msg.user] || fetchUserName(msg.user); 
    userCache[msg.user] = userName; 
    let time = Utilities.formatDate(new Date(parseFloat(msg.ts) * 1000), Session.getScriptTimeZone(), 'HH:mm'); 

    let formattedText = formatMessageText(msg.text); 
    addPara(`[${time}] ${userName}:\n${formattedText}`, 0, false); 

    if (msg.files && msg.files.length > 0) {
      processFiles(msg.files, 0, addPara); 
    }

    if (msg.thread_ts === msg.ts) {
      Utilities.sleep(1000); 
      let replies = fetchSlackReplies(CHANNEL_ID, msg.ts); 
      for (let i = 1; i < replies.length; i++) {
        let r = replies[i]; 
        let rUser = userCache[r.user] || fetchUserName(r.user); 
        userCache[r.user] = rUser; 
        let rTime = Utilities.formatDate(new Date(parseFloat(r.ts) * 1000), Session.getScriptTimeZone(), 'MM/dd HH:mm'); 
        
        let formattedRText = formatMessageText(r.text); 
        let rText = formattedRText.replace(/\n/g, '\n    '); 

        addPara(`    ↳ [${rTime}] ${rUser}:\n    ${rText}`, 36, false); 

        if (r.files && r.files.length > 0) {
          processFiles(r.files, 36, addPara); 
        }
      }
    }
    addPara("--------------------------------------------------", 0, false); 
  }

  if (parseFloat(lastCommittedTs) < ts7DaysAgo) {
    let commitMessages = fetchSlackHistory(CHANNEL_ID, lastCommittedTs, ts7DaysAgo.toString()); 
    
    if (commitMessages.length > 0) {
      insertIndex = body.getChildIndex(separatorElement); 
      let isTimeout = false; 
      commitMessages.reverse(); 

      for (let i = 0; i < commitMessages.length; i++) {
        let msg = commitMessages[i]; 
        if (msg.ts === lastCommittedTs) continue; 

        if (Date.now() - startTime > TIME_LIMIT) {
          isTimeout = true; 
          break; 
        }

        writeSingleMessage(msg); 
        lastCommittedTs = msg.ts; 
        props.setProperty('LAST_COMMITTED_TS', lastCommittedTs); 
      }

      if (isTimeout) {
        let lastDate = Utilities.formatDate(new Date(parseFloat(lastCommittedTs) * 1000), Session.getScriptTimeZone(), 'yyyy年MM月dd日 HH:mm'); 
        DocumentApp.getUi().alert(`⏳ 実行時間制限が近づいたため一時停止しました。\n再度メニューの「手動更新」をクリックして続きを取得してください。`); 
        return; 
      }
    }
    props.setProperty('LAST_COMMITTED_TS', ts7DaysAgo.toString()); 
  }

  let nextSibling = separatorElement.getNextSibling(); 
  while (nextSibling) {
    let toRemove = nextSibling; 
    nextSibling = nextSibling.getNextSibling(); 
    try {
      toRemove.removeFromParent(); 
    } catch (e) {
      if (toRemove.clear) toRemove.clear(); 
    }
  }

  let recentMessages = fetchSlackHistory(CHANNEL_ID, ts7DaysAgo.toString(), tsNow.toString()); 
  if (recentMessages.length > 0) {
    insertIndex = -1; 
    recentMessages.reverse(); 
    
    addPara("==================================================", 0, false); 
    addPara(`🔄 【直近7日間の変動エリア】`, 0, true); 
    
    currentPrintedDate = ""; 
    for (let i = 0; i < recentMessages.length; i++) {
      writeSingleMessage(recentMessages[i]); 
    }
  } else {
    body.appendParagraph("直近7日間のメッセージはありませんでした。"); 
  }

  DocumentApp.getUi().alert('✅ すべてのログ同期が完了しました！'); 
}

function formatMessageText(text) {
  if (!text) return ""; 
  return text.replace(/<@([A-Z0-9]+)(?:\|[^>]+)?>/g, function(match, userId) {
    let userName = userCache[userId] || fetchUserName(userId); 
    userCache[userId] = userName; 
    return '@' + userName; 
  });
}

function processFiles(files, indentNum, addParaFunc) {
  files.forEach(file => {
    if (!file.url_private_download) return; 
    try {
      const response = UrlFetchApp.fetch(file.url_private_download, { headers: { 'Authorization': `Bearer ${SLACK_TOKEN}` } }); 
      const blob = response.getBlob().setName(file.name); 
      const folder = DriveApp.getFolderById(FOLDER_ID); 
      const driveFile = folder.createFile(blob); 
      addParaFunc(`📎 [添付ファイル: ${file.name}] ${driveFile.getUrl()}`, indentNum, false); 
    } catch(e) {
      addParaFunc(`📎 [添付ファイル取得エラー]`, indentNum, false); 
    }
  });
}

function fetchSlackHistory(channelId, oldest, latest) {
  let allMessages = []; 
  let hasMore = true; 
  let cursor = ""; 

  while (hasMore) {
    let url = `https://slack.com/api/conversations.history?channel=${channelId}&oldest=${oldest}&latest=${latest}&limit=200`; 
    if (cursor) url += `&cursor=${encodeURIComponent(cursor)}`; 

    const options = { method: 'get', headers: { 'Authorization': `Bearer ${SLACK_TOKEN}` } }; 
    const response = UrlFetchApp.fetch(url, options); 
    const json = JSON.parse(response.getContentText()); 

    if (!json.ok) throw new Error(`Slack API Error`); 
    
    allMessages = allMessages.concat(json.messages); 

    if (json.response_metadata && json.response_metadata.next_cursor) {
      cursor = json.response_metadata.next_cursor; 
      Utilities.sleep(1000); 
    } else {
      hasMore = false; 
    }
  }
  return allMessages; 
}

function fetchSlackReplies(channelId, ts) {
  const url = `https://slack.com/api/conversations.replies?channel=${channelId}&ts=${ts}&limit=200`; 
  const options = { method: 'get', headers: { 'Authorization': `Bearer ${SLACK_TOKEN}` } }; 
  const response = UrlFetchApp.fetch(url, options); 
  const json = JSON.parse(response.getContentText()); 
  if (!json.ok) throw new Error(`Slack API Error`); 
  return json.messages; 
}

function fetchUserName(userId) {
  if(!userId) return "Bot/System"; 
  try {
    const url = `https://slack.com/api/users.info?user=${userId}`; 
    const options = { method: 'get', headers: { 'Authorization': `Bearer ${SLACK_TOKEN}` } }; 
    const response = UrlFetchApp.fetch(url, options); 
    const json = JSON.parse(response.getContentText()); 
    if (json.ok) return json.user.real_name || json.user.name; 
  } catch(e) {} 
  return userId; 
}
```
