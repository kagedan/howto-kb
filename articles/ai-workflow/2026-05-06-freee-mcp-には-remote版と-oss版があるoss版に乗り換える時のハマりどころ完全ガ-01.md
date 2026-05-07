---
id: "2026-05-06-freee-mcp-には-remote版と-oss版があるoss版に乗り換える時のハマりどころ完全ガ-01"
title: "freee MCP には Remote版と OSS版がある——OSS版に乗り換える時のハマりどころ完全ガイド"
url: "https://zenn.dev/yoshiki_otagaki/articles/8d8fe8ef7bf0fa"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

## 想定読者

* freee 公式 MCP を使いたい人
* Claude Desktop で領収書アップロードまで自動化したい人
* 「Remote MCP 使ったら画質が落ちるんだけど」と詰まっている人
* 「OSS版を入れたのに動かない」と詰まっている人

## TL;DR

| やりたいこと | 選ぶべき版 |
| --- | --- |
| 試算表閲覧・取引参照・請求書発行 | **Remote MCP** で OK |
| 領収書のファイルボックス自動アップロード | **OSS版必須**（Remote版だと画像が圧縮されて電子帳簿保存法200dpi要件を満たさない） |

そして OSS版に乗り換える時、**多くの人が以下の2点で詰まる**：

1. **Remote MCP のコネクタが残っている**と、そちらが優先されて OSS版が使われない
2. **Claude Desktop は「✕」では完全終了しない**。タスクバー右下から「終了」を選ばないと設定が反映されない

僕はこの2点で**丸2日**消費した。本記事はその記録。

## freee MCP には2種類ある

[**freee-mcp**](https://www.npmjs.com/package/freee-mcp) は、freee 会計・人事労務・請求書・工数管理・販売の各 API を MCP（Model Context Protocol）経由で AI から呼び出せるようにする公式サーバー。

| 版 | エンドポイント / コマンド | 特徴 |
| --- | --- | --- |
| **Remote MCP** | `https://mcp.freee.co.jp/mcp` | OAuth 認証だけで即使える。手軽 |
| **OSS版** | `npx freee-mcp configure` でローカル起動 | 手間はかかるがフル機能 |

公式ドキュメントには「両方とも公式」と書かれている。**「どっちを選べば？」が初見ではわからない**。

## 違いの本質：画像の経路

両者の決定的な違いは、**ファイルアップロード時の画像経路**にある。

```
[Remote MCP]
Claude Desktop → freee Remote Server → freee API
                 ↑ ここで画像が圧縮・低解像度化される

[OSS版]
Claude Desktop → ローカル MCP (npx freee-mcp) → freee API
                 ↑ 画像は元解像度のまま通過
```

Remote MCP は経路上にサーバーが挟まる構造のため、**画像が中継時に圧縮**される。これは仕様で、設定で回避できない。

## 領収書アップロードでの実害

### Remote MCP で試したケース

```
[5枚の領収書画像を Claude に貼り付け]

これらを freee に取引登録して、画像もファイルボックスにアップロードしてください。
```

Claude が処理を進めて「✅ 完了しました」と返答。

freee のファイルボックスを開くと、**領収書の画像がぼやけている**。文字は読めなくはないが、**OCR で読み直すには厳しい**画質。

### なぜこれが致命的か：電子帳簿保存法

電子帳簿保存法のスキャナ保存要件：

* **解像度 200dpi 以上**
* **カラー画像**（256階調以上）
* **タイムスタンプ付与または訂正・削除の履歴管理**
* 後から検索できる検索機能

Remote MCP 経由でアップロードされた画像は、この**解像度要件を満たさない可能性が高い**。税務調査が入った場合、「電子保存の要件不備」を指摘されるリスクがある。

つまり「Claude で領収書を自動登録した」が、**税法上は「やっていない」と同じ扱いになり得る**。これは税理士業務として絶対に許容できない。

## OSS版へ乗り換える時にハマる2つの罠

### 罠1：Remote MCP のコネクタが残っている

OSS版をインストールして、Claude Desktop の設定ファイル（`claude_desktop_config.json`）に追記。Claude Desktop を再起動。

「よし、これで OSS版が動くはず」と思って試したら、**結果が低解像度のまま**。

原因：**Claude Desktop に登録した Remote MCP のカスタムコネクタが、まだ有効のまま**だった。

Claude Desktop は MCP サーバーを複数登録できるが、**同じ名前空間のツールが重複している場合、先に登録されているもの（または優先度が高いもの）が呼ばれる**仕様。OSS版を追加しても、Remote MCP が呼ばれていた。

#### 対処

Claude Desktop の「設定」→「カスタマイズ」→「カスタムコネクタ」から、freee の Remote MCP を**無効化または削除**する。

### 罠2：Claude Desktop の「✕」では完全終了にならない

これが**最大の落とし穴**。

`claude_desktop_config.json` を編集しても、**Claude Desktop を完全終了して再起動しないと、新しい設定が反映されない**。

問題は：**「✕ ボタンで閉じる」は完全終了ではない**こと。

Claude Desktop（特に Windows 版）は、**ウィンドウを閉じてもバックグラウンドで動き続ける**仕様。「✕」を押してウィンドウが消えても、**裏でプロセスが生きている**。

そして、再度 Claude Desktop を起動しても、**裏で動いている古いプロセスがそのまま使われる**。新しい `claude_desktop_config.json` の変更は読み込まれない。

#### 正しい完全再起動（Windows）

1. デスクトップ右下のタスクバー、`^` マーク（隠れているインジケーターを表示）をクリック
2. **Claude Desktop のアイコンを右クリック**
3. メニューから **「Quit」または「終了」**
4. これで初めて Claude Desktop が完全終了する
5. 改めて Claude Desktop を起動

#### 正しい完全再起動（Mac）

または Dock 上の Claude Desktop アイコンを右クリック →「終了」。

ウィンドウの「✕」を押すだけだと完全終了にならないのは Mac でも同じ。

## OSS版乗り換え：正しい手順

僕がハマった2点を踏まえた、正しい手順：

```
Step 1: OSS版をインストールして設定ファイルに追記
Step 2: Claude Desktop の Remote MCP コネクタを無効化または削除
Step 3: Claude Desktop を「完全終了」
        Windows: タスクバー右下 → 右クリック → 終了
        Mac:     Cmd + Q
Step 4: Claude Desktop を改めて起動
Step 5: チャットで動作確認
```

このうち **Step 2 と Step 3 をスキップすると、絶対に動かない**。説明している記事が世の中にほぼ無いので、ここで詰まる人が多い。

## OSS版セットアップ詳細

### 事前準備

### 1. freee-mcp の設定（初回のみ）

ブラウザが開いて freee の OAuth 認証画面に遷移する。事業所を選択して認証を完了。設定は以下に保存される：

* macOS: `~/.config/freee-mcp/config.json`
* Windows: `%APPDATA%\freee-mcp\config.json`

### 2. Claude Desktop の設定ファイルに追記

設定ファイルの場所：

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`

追記内容：

```
{
  "mcpServers": {
    "freee": {
      "command": "npx",
      "args": ["freee-mcp"]
    }
  }
}
```

### 3. Remote MCP を無効化

Claude Desktop を起動 → 「設定」→「カスタマイズ」→「カスタムコネクタ」から freee の Remote MCP を無効化（または削除）。

### 4. 完全終了

タスクバー右下から右クリック → 終了（Windows）、または `Cmd + Q`（Mac）。

### 5. 再起動して動作確認

Claude Desktop を改めて起動して、チャットで以下を聞く：

返ってくるツール一覧に **`freee_file_upload`** が含まれていれば、OSS版が正しく動いている。

## OSS版で何ができるようになるか

OSS版に切り替えた後、領収書の自動登録パイプラインが完全動作する：

```
[領収書5枚を Claude に貼り付け]

これらを freee に取引登録して。
- 事業所は「税理士法人Baton One」
- 飲食代は「会議費」または「交際費」を判断
- 5万円超のタクシーは家事按分の確認を僕に
- ファイルボックスにも画像添付（高解像度のまま）
- 完了したら一覧で報告
```

Claude が

1. 画像の OCR
2. 日付・金額・取引先・摘要の抽出
3. 勘定科目を判断
4. 家事按分が必要なものを質問
5. `freee_api_post` で取引登録
6. **`freee_file_upload` で高解像度のままファイルボックスに画像添付**
7. 完了一覧の生成

を全部、1つの会話の中で連続的に処理する。

## API コール数の制限

freee API には**プランごとの1日あたりコール数上限**がある：

| プラン | 上限 |
| --- | --- |
| 記帳代行プラン | 3,000 回/日 |
| 上位プラン | 10,000 回/日 |

100件の取引登録で 100 コール超を消費する。月次で大量処理する場合は、上位プランへの切り替えを検討する必要がある。

## ハマったら確認するチェックリスト

「設定したのに動かない」と感じた時に確認すべきこと：

このチェックリストを上から順に確認すれば、たいていの不具合は解消する。

## まとめ

* freee MCP には Remote版と OSS版があり、領収書アップロード自動化には OSS版必須
* OSS版乗り換え時は、**Remote MCP コネクタの無効化** と **Claude Desktop の完全終了** が必須
* Claude Desktop の「✕」は完全終了ではない。タスクバー右下から右クリック → 終了

僕はこの2点に気づくまで丸2日消費した。本記事を読んでくれた人は、数十分で乗り換えが終わるはず。

---

## 関連記事

本記事は note にも投稿しています（より体験談寄りの構成）：  
**[【freee MCP】Remote版で領収書アップロードが実用にならず、OSS版に乗り換えた話](https://note.com/yoshiki_otagaki)**（note版）

その他の弁護士・税理士 × AI の記事：

質問・実装相談、お気軽にコメントください。
