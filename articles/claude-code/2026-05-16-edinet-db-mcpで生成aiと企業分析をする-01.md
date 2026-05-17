---
id: "2026-05-16-edinet-db-mcpで生成aiと企業分析をする-01"
title: "EDINET DB MCPで生成AIと企業分析をする"
url: "https://qiita.com/hokutoh/items/86fd68abd2531f286ef1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

生成AIで投資や企業調査のために生成AIを使っていらっしゃる方は多いのではないでしょうか？
その際、最新の情報が反映されておらずなかなか歯がゆい思いをされた方もいらっしゃると思います。

EDINET等で有価証券報告書等の書類は誰でも閲覧できますが、複数の企業比較や時系列分析をPDFでひとつひとつ入手するのはとても手間ですし、それを生成AIに渡すのも大変です。

## EDINETとは

EDINETは金融庁が運営する有価証券報告書などの開示書類を電子化・集約したデータベースです。上場企業が定期的に提出する有価証券報告書・決算短信・四半期報告書などが網羅されており、企業の財務情報・事業内容・リスク・経営方針などを誰でも閲覧できます。
APIは用意されていますが、生のXBRLデータやPDFを取得するためのREST APIであり、MCPには対応していません。

## EDINET DB / EDINET MCPとは

EDINET DBは、Cabocia社のサービスで、EDINETのデータを構造化・API化したサービスです。
日本の上場企業3,832社の財務データをAIから直接参照できるよう整備されており、そのアクセス手段として **MCP（Model Context Protocol）** を提供しています。

利用できるツールは以下の通りです。

| ツール名 | 説明 |
|---|---|
| `get_company` | 企業の基本情報・最新財務・財務健全性スコアを取得 |
| `get_financials` | 最大6年分の財務時系列データを取得 |
| `get_analysis` | AI分析（財務健全性スコア、業界ベンチマーク比較） |
| `search_companies` | 企業名・証券コード・業種・財務健全性スコア・事業タグで検索 |
| `search_companies_batch` | 複数企業を一括検索（比較分析に便利） |
| `get_ranking` | ROE・配当利回り等の財務指標ランキングを取得 |
| `get_text_blocks` | 有報の全文テキスト（事業概況・リスク・MD&A等） |
| `get_earnings` | TDNet決算短信データ（速報業績・前年比） |
| `get_earnings_calendar` | JPX決算発表スケジュール |
| `screen_companies` | 125指標で複数条件スクリーニング |

## 活用例

### 📊 財務分析・企業調査

- 「〇〇社の直近5年間の売上推移と収益性を分析して」
- 「キーエンスの財務健全性を分析して、同業他社と比べてどうか教えて」
- 「〇〇社の有報に記載されているリスク情報をまとめて」

### 🏆 ランキング・業界比較

- 「半導体業界のROEトップ10を教えて」
- 「医薬品業界の営業利益率ランキングを見せて」
- 「情報・通信業のROEトップ10を取得して、業界の特徴を教えて」

### 💹 個人投資家向け：銘柄スクリーニング

- 「配当利回り4%以上で財務健全性スコアが70以上の企業を探して」
- 「ROE15%以上、PBR1倍以下の割安高収益企業を探して」
- 「配当利回りが高くて、かつ業績が安定している企業を10社ピックアップして」

### 📈 個人投資家向け：銘柄分析・投資判断サポート

- 「ソニーと任天堂の直近5年間の業績を比較して」
- 「この会社、買い増すべきか財務面から意見をくれ」
- 「自己資本比率が高くて、かつ増収が続いている企業を探して」

### 🏢 ビジネス利用（営業・M&A・取引先調査）

- 「取引先候補の〇〇社について、財務面での懸念点を洗い出して」
- 「M&A候補の〇〇社の開示情報から見えるリスクを整理して」
- 「SaaS企業の中でROEが高い順に10社教えて」

### 📝 レポート作成

- 「〇〇社の直近5期の業績推移をまとめてレポートにして」
- 「競合3社の財務指標を比較表にして」

---

## EDINET MCP設定方法

接続方法は2種類あります。自分の環境に合った方法を選んでください。

### 方法①：Claude.ai の Connectors 機能（Pro/Team/Enterprise プランのみ）

https://edinetdb.jp/docs/connect-claude

Claude.aiには公式のコネクタ機能があり、GUIから簡単に接続できます。**ただし、Freeプランは非対応です。**

方法に関しても上記URLに丁寧に記載されているのでここでは割愛します。

---

### 方法②：リモートMCPを手動設定（**Freeプランでも使える**）

https://edinetdb.jp/docs/mcp-guide

Freeプランや開発者ツール（Claude Code、Cursor等）で使いたい場合は、MCP接続を手動で設定します。

Claude Codeに契約されている方などではターミナルで一発で設定できますが、
ここではClaudeを無料プランで使用されている方向けにClaude Desktopでの設定方法を紹介します。

#### 事前準備

1. Claude Desktopのインストール
https://code.claude.com/docs/ja/desktop

2. Node.jsのインストール
https://nodejs.org/ja/download
Node.js 18以上をインストールする

3. EDINET DBでAPIキー発行
[EDINET DBのダッシュボード](https://edinetdb.jp/developers/dashboard)でAPIキーを発行して手元にメモしておく。

アカウント作成後に、APIキー一覧よりAPIキーを作成してください。
APIキーは作成時に一度しか表示あれないのでコピーを忘れた場合は再度作成してください。

#### Claude Desktop の場合

Claude Desktopの設定ファイルを開きます。

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
`C:\Users\ユーザ名\AppData\Roaming\Claude`等

以下の内容を追記します（`YOUR_API_KEY` を発行したキーに置き換えてください）。

```json
{
  "mcpServers": {
    "edinetdb": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://edinetdb.jp/mcp",
        "--header",
        "Authorization: Bearer YOUR_API_KEY"
      ]
    }
  }
}
```

Claude Desktopを再起動すれば接続完了です。

<details><summary>エラーが出た場合</summary>
私が試した際、以下のエラーが出ました。npx自体は他のMCP接続で使っているのでそちらの問題ではありません。
```
'C:\Program' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

`npx -y mcp-remote` はパッケージを動的にダウンロードして実行しますが、
その際に生成される `C:\Program Files\nodejs\...` のようなスペース入りパスが
Windows日本語環境で正しく処理されないようです。

```npm install -g mcp-remote```
で`mcp-remote`をグローバルにインストール後に
以下に記載を変えることでうまくいきました。
```json
{
  "mcpServers": {
    "edinetdb": {
      "command": "mcp-remote",
      "args": [
        "https://edinetdb.jp/mcp",
        "--header",
        "Authorization: Bearer YOUR_API_KEY"
      ]
    }
  }
}
```
</details>

#### 動作確認

「EDINET MCPを使って・・・」と指示すればEDINETに接続して回答してくれます。
(もちろん以下くらいの指示だったらEDINETにつながずとも回答できる内容ですが・・・)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/666388/9f2ee6df-818a-4f33-816c-65c6153e8677.png)


### 方法①と②の比較

| | Connectors（方法①） | リモートMCP手動設定（方法②） |
|---|---|---|
| 対応プラン | Pro/Team/Enterprise のみ | **Free を含む全プラン** |
| 設定の手軽さ | GUIでワンクリック | 設定ファイルの編集が必要 |
| APIキー | 不要（Google認証のみ） | 要発行 |
| できること | ほぼ同等 | ほぼ同等 |
| 対応クライアント | Claude.ai | Claude Desktop / Claude Code / Cursor など |

---

### 料金プラン（EDINET DB側）

| プラン | 日次上限 | 料金 |
|---|---|---|
| Free | 100回/日 | 無料 |
| Pro | 1,000回/日 | ¥4,980/月 |
| Business | 10,000回/日 | ¥29,800/月 |

全プランで全エンドポイント・全フィールドを利用できます。プランによる機能差はリクエスト上限のみです。

大学教員・大学院生の方はアカデミックプランがあるようです。
https://edinetdb.jp/pricing/academy
