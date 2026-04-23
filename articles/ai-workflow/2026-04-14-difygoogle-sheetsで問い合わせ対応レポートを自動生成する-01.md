---
id: "2026-04-14-difygoogle-sheetsで問い合わせ対応レポートを自動生成する-01"
title: "Dify×Google Sheetsで問い合わせ対応レポートを自動生成する"
url: "https://note.com/oshima0627/n/nae9fead7e140"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-04-14"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

---

## 問い合わせ対応の「見える化」、できていますか？

「毎日大量の問い合わせが来るけど、どのカテゴリが多いか把握できていない」  
「月末にレポートをまとめるのが手作業で大変すぎる」  
「問い合わせ内容を分析して製品改善に活かしたいが、データが散らばっている」

カスタマーサポートや社内ヘルプデスクを運営していると、こうした悩みはよく耳にします。問い合わせは毎日届くのに、それを「データとして活用する仕組み」が整っていないケースが非常に多いのです。

本記事では、**Dify**のAIワークフローと**Google Sheets**を連携させて、問い合わせ内容の自動分類・集計・レポート生成までを一気通貫で自動化するシステムの構築手順を解説します。コーディングは最小限で、Difyのノーコード操作を中心に進められるので、バックエンド開発に自信がない方にもおすすめです。

---

## このシステムで実現できること

本記事で構築するシステムは、以下のフローで動作します。

1. **問い合わせフォーム（またはメール）からテキストを受信**
2. **DifyのAIが問い合わせ内容を自動分類**（例: バグ報告／機能要望／使い方質問／クレーム）
3. **分類結果・要約をGoogle Sheetsに自動記録**
4. **週次・月次でサマリーレポートを自動生成**してスプレッドシートに追記

手作業でやると数時間かかる集計・レポート作成が、**完全自動で数秒のうちに完了**します。

### 使用するツール・サービス

| ツール | 役割 |  
|--------|------|  
| [Dify](https://dify.ai/) | AIワークフロー・API提供 |  
| Google Sheets | データ蓄積・レポート出力先 |  
| Google Apps Script | Sheets操作の仲介 |  
| Webhook（任意） | 問い合わせデータの受け口 |

---

## STEP 1: Difyで問い合わせ分類ワークフローを構築する

まずはDify側で、問い合わせテキストを受け取り、分類と要約を行うワークフローを作成します。

### 1-1. Difyプロジェクトの準備

[Dify公式サイト](https://dify.ai/)にログインし、「スタジオ」から「ワークフロー」タイプのアプリを新規作成します。アプリタイプは必ず「ワークフロー」を選択してください（チャットボットタイプでは今回の構成に対応しにくいため）。

### 1-2. 入力変数の定義

ワークフローの「開始」ノードをクリックし、以下の入力変数を設定します。

| 変数名 | 型 | 説明 |  
|--------|-----|------|  
| `inquiry\_text` | String | 問い合わせ本文 |  
| `customer\_id` | String | 顧客ID（任意） |  
| `received\_at` | String | 受信日時 |

### 1-3. LLMノードで分類・要約を実装

「開始」ノードの次に「LLM」ノードを追加します。使用するモデルはGPT-4oやClaude 3.5 Sonnetなど精度の高いものを推奨します。

プロンプトは以下のように設定してください。

```
# 役割
あなたはカスタマーサポートの問い合わせ分析AIです。

# タスク
以下の問い合わせ内容を分析し、JSON形式で結果を返してください。

# 問い合わせ内容
{{inquiry_text}}

# 出力形式（必ずこのJSON形式のみ出力すること）
{
  "category": "分類カテゴリ（バグ報告/機能要望/使い方質問/クレーム/その他 のいずれか）",
  "priority": "優先度（高/中/低）",
  "summary": "問い合わせ内容の要約（50文字以内）",
  "sentiment": "感情トーン（ポジティブ/ネガティブ/ニュートラル）",
  "keywords": ["キーワード1", "キーワード2", "キーワード3"]
}

# 注意事項
- JSON以外の文字は出力しないこと
- categoryは必ず指定された5種類から選ぶこと
- summaryは事実ベースで簡潔にまとめること
```

### 1-4. コード変換ノードでJSONを整形

LLMの出力はテキストなので、後続処理で扱いやすいように「コード」ノードを追加してPythonでパースします。

```
import json

def main(llm_output: str, inquiry_text: str, customer_id: str, received_at: str) -> dict:
    """
    LLMの出力JSONをパースして構造化データに変換する
    """
    try:
        # LLM出力をJSONとしてパース
        parsed = json.loads(llm_output.strip())
        
        return {
            "category": parsed.get("category", "その他"),
            "priority": parsed.get("priority", "中"),
            "summary": parsed.get("summary", ""),
            "sentiment": parsed.get("sentiment", "ニュートラル"),
            "keywords": ", ".join(parsed.get("keywords", [])),
            "original_text": inquiry_text[:200],  # 元テキストは200文字まで
            "customer_id": customer_id,
            "received_at": received_at,
            "processed_at": "{{current_datetime}}"
        }
    except json.JSONDecodeError:
        # パース失敗時のフォールバック
        return {
            "category": "その他",
            "priority": "中",
            "summary": "分類に失敗しました",
            "sentiment": "ニュートラル",
            "keywords": "",
            "original_text": inquiry_text[:200],
            "customer_id": customer_id,
            "received_at": received_at,
            "processed_at": "error"
        }
```

### 1-5. HTTP Requestノードでシートに書き込む

次に、「HTTP Request」ノードを追加し、後述するGoogle Apps ScriptのWebアプリURLにPOSTリクエストを送信します。

設定内容：

ワークフローの最後に「終了」ノードを接続し、HTTPレスポンスのステータスコードを出力変数として設定すれば完成です。

### 1-6. APIとして公開する

ワークフローが完成したら「公開」ボタンをクリックし、「APIアクセス」セクションからAPIキーを取得してください。このAPIが、外部からの問い合わせデータを受け取る入口になります。

---

## STEP 2: Google Sheetsとスクリプトを準備する

### 2-1. スプレッドシートの構成

新しいGoogle Sheetsを作成し、以下の2つのシートを用意します。

**シート1: `inquiries`（問い合わせログ）**

| A: 受信日時 | B: 顧客ID | C: カテゴリ | D: 優先度 | E: 感情 | F: 要約 | G: キーワード | H: 元テキスト（抜粋） | I: 処理日時 |

**シート2: `reports`（レポート）**

| A: レポート期間 | B: 総件数 | C: バグ報告 | D: 機能要望 | E: 使い方質問 | F: クレーム | G: その他 | H: 高優先度件数 | I: ネガティブ件数 |

シートIDはURLの `[https://docs.google.com/spreadsheets/d/【ここがID】/edit`](https://docs.google.com/spreadsheets/d/%E3%80%90%E3%81%93%E3%81%93%E3%81%8CID%E3%80%91/edit%60) から確認できます。

### 2-2. Google Apps Scriptの実装

Google Sheetsのメニューから「拡張機能」→「Apps Script」を開き、以下のコードを貼り付けます。

```
// スプレッドシートのID（URLから取得）
const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE';

/**
 * Difyからのデータを受け取りシートに書き込むWebhookエンドポイント
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = ss.getSheetByName('inquiries');
    
    // 問い合わせログを追記
    sheet.appendRow([
      data.received_at || new Date().toISOString(),
      data.customer_id || '',
      data.category || 'その他',
      data.priority || '中',
      data.sentiment || 'ニュートラル',
      data.summary || '',
      data.keywords || '',
      data.original_text || '',
      data.processed_at || new Date().toISOString()
    ]);
    
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'success', message: 'Data recorded.' }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * 週次レポートを自動生成してreportsシートに追記する
 * タイマートリガーで毎週月曜朝に実行
 */
function generateWeeklyReport() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const inquirySheet = ss.getSheetByName('inquiries');
  const reportSheet = ss.getSheetByName('reports');
  
  // 過去7日間のデータを取得
  const allData = inquirySheet.getDataRange().getValues();
  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  
  // 集計用オブジェクトの初期化
  const counts = {
    total: 0,
    'バグ報告': 0,
    '機能要望': 0,
    '使い方質問': 0,
    'クレーム': 0,
    'その他': 0,
    highPriority: 0,
    negative: 0
  };
  
  // 1行目はヘッダーなのでスキップ
  for (let i = 1; i < allData.length; i++) {
    const row = allData[i];
    const receivedAt = new Date(row[0]);
    
    if (receivedAt >= oneWeekAgo) {
      counts.total++;
      const category = row[2];
      const priority = row[3];
      const sentiment = row[4];
      
      if (counts[category] !== undefined) counts[category]++;
      else counts['その他']++;
      
      if (priority === '高') counts.highPriority++;
      if (sentiment === 'ネガティブ') counts.negative++;
    }
  }
  
  // レポート期間の文字列を生成
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 7);
  const period = `${formatDate(startDate)} 〜 ${formatDate(endDate)}`;
  
  // reportsシートに追記
  reportSheet.appendRow([
    period,
    counts.total,
    counts['バグ報告'],
    counts['機能要望'],
    counts['使い方質問'],
    counts['クレーム'],
    counts['その他'],
    counts.highPriority,
    counts.negative
  ]);
  
  Logger.log(`週次レポート生成完了: ${period}, 総件数: ${counts.total}`);
}

/**
 * 日付を「YYYY/MM/DD」形式にフォーマット
 */
function formatDate(date) {
  return `${date.getFullYear()}/${String(date.getMonth()+1).padStart(2,'0')}/${String(date.getDate()).padStart(2,'0')}`;
}
```

### 2-3. WebアプリとしてデプロイしてURLを取得

Apps Scriptのエディタ右上「デプロイ」→「新しいデプロイ」→「種類の選択: ウェブアプリ」を選択します。

設定：

「デプロイ」をクリックするとWebアプリURLが発行されます。このURLをDifyのHTTP RequestノードのURLとして設定してください。

### 2-4. 週次レポートのトリガー設定

Apps Scriptのエディタ左メニューから「トリガー」を選択し、`generateWeeklyReport` 関数に\*\*時間ベースのトリガー（毎週月曜 午前8時〜9時）\*\*を設定します。これにより、毎週月曜日に自動でレポートが生成されます。

---

## STEP 3: 外部からDify APIを呼び出す

問い合わせフォームやメールシステムからDify APIを呼び出す実装例を紹介します。

### Python実装例（問い合わせ受信時に呼び出す）

```
import requests
import json
from datetime import datetime

# Dify APIの設定
DIFY_API_URL = "https://api.dify.ai/v1/workflows/run"
DIFY_API_KEY = "app-XXXXXXXXXXXXXXXXXXXX"  # DifyのAPIキー

def classify_inquiry(inquiry_text: str, customer_id: str = "") -> dict:
    """
    問い合わせテキストをDifyに送信して分類結果を取得する
    
    Args:
        inquiry_text: 問い合わせ本文
        customer_id: 顧客ID（任意）
    
    Returns:
        分類結果の辞書
    """
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {
            "inquiry_text": inquiry_text,
            "customer_id": customer_id,
            "received_at": datetime.now().isoformat()
        },
        "response_mode": "blocking",  # 同期処理
        "user": f"system-{customer_id or 'anonymous'}"
    }
    
    try:
        response = requests.post(
            DIFY_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        # ワークフロー実行結果を返す
        return {
            "status": "success",
            "workflow_run_id": result.get("workflow_run_id"),
            "outputs": result.get("data", {}).get("outputs", {})
        }
        
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "APIタイムアウト"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

# 使用例
if __name__ == "__main__":
    test_inquiry = """
    先週から急にログインできなくなりました。
    パスワードリセットを試しても「メールが届かない」と表示されます。
    早急に対応をお願いします。業務に支障が出ています。
    """
    
    result = classify_inquiry(
        inquiry_text=test_inquiry,
        customer_id="cust_12345"
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

### Google Formsと連携する場合（Apps Script）

Google Formsの回答をトリガーにDify APIを直接呼び出すこともできます。フォームに紐づいたスプレッドシートのApps Scriptに以下を追加してください。

```
/**
 * Googleフォーム回答時にDify APIを呼び出す
 * フォームの送信トリガーに設定する
 */
function onFormSubmit(e) {
  const response = e.values; // フォーム回答の配列
  
  // フォームの列順に合わせて調整してください
  const inquiryText = response[2]; // 問い合わせ内容の列
  const customerId = response[1];  // 顧客IDの列
  
  const DIFY_API_URL = 'https://api.dify.ai/v1/workflows/run';
  const DIFY_API_KEY = 'app-XXXXXXXXXXXXXXXXXXXX';
  
  const payload = {
    inputs: {
      inquiry_text: inquiryText,
      customer_id: customerId,
      received_at: new Date().toISOString()
    },
    response_mode: 'blocking',
    user: 'google-forms-integration'
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: `Bearer ${DIFY_API_KEY}`
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response_dify = UrlFetchApp.fetch(DIFY_API_URL, options);
  const result = JSON.parse(response_dify.getContentText());
  
  Logger.log('Dify API Response: ' + JSON.stringify(result));
}
```

---

## STEP 4: レポートをGoogle Sheetsで可視化する

データが `reports` シートに蓄積されてきたら、Google Sheetsのグラフ機能を使って可視化しましょう。

### おすすめのグラフ設定

1. **カテゴリ別件数の積み上げ棒グラフ**
2. **高優先度・ネガティブ件数の折れ線グラフ**

### Looker Studio連携（応用）

より高度なダッシュボードが必要な場合は、[Google Looker Studio](https://lookerstudio.google.com/)（旧Data Studio）と接続すると、インタラクティブなレポートをワンクリックで生成できます。DataソースとしてGoogle Sheetsを選択するだけで簡単に接続できます。

---

## 運用時のよくある問題と対処法

### LLMの分類精度が低い場合

プロンプトにFew-shotサンプルを追加することで精度が向上します。LLMノードのシステムプロンプトに以下のような例示を追加してください。

```
# 分類例
- 「ログインできません」→ category: "バグ報告", priority: "高"
- 「ダークモードが欲しいです」→ category: "機能要望", priority: "低"
- 「使い方を教えてください」→ category: "使い方質問", priority: "中"
- 「対応が遅すぎる！」→ category: "クレーム", priority: "高"
```

### Google Apps ScriptのWebアプリが403エラーになる場合

デプロイ時のアクセス権限設定を確認してください。Difyのサーバーから呼び出す場合は「全員（匿名ユーザーを含む）」に設定する必要があります。社内限定で使う場合は「Googleアカウントでログインしているユーザー」に制限することも可能です。

### Dify APIのレスポンスが遅い場合

`response\_mode` を `blocking` から `streaming` に変更することで非同期処理に切り替えられます。ただし、Google Sheets書き込みの成否確認が複雑になるため、初期構築段階では `blocking` のまま運用することを推奨します。

---

## まとめ：次のアクション

この記事で構築したシステムにより、以下が自動化されます。

次のステップとして、以下の拡張も検討してみてください。

* **Slack通知連携**: 高優先度の問い合わせが来たら即座にSlackへアラート
* **自動返信文の生成**: Difyのワークフローを拡張し、返信テンプレートもAIで生成
* **多言語対応**: 英語・中国語など多言語の問い合わせを日本語に翻訳してから分類
* **Looker Studioダッシュボード**: 経営層向けにリアルタイムダッシュボードを提供

まずは本記事のSTEP 1からDifyのワークフローを作成し、テスト問い合わせを送信して動作確認してみましょう。最初の動作確認は30分程度で完了するはずです。問い合わせ対応のデータを「資産」として積み上げ、製品改善やサービス品質向上に活かしていきましょう。

---

## 参考資料
