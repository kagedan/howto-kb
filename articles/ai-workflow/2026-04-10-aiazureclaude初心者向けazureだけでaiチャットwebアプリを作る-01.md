---
id: "2026-04-10-aiazureclaude初心者向けazureだけでaiチャットwebアプリを作る-01"
title: "【AI】【Azure】【Claude】【初心者向け】AzureだけでAIチャットWebアプリを作る"
url: "https://qiita.com/yudai8155/items/7f85d1d9d7b60681ce0f"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

# はじめに

Azureを業務で使用するにあたり、学習目的でAzureのサービスを使用してシンプルなAIチャットを作ってみました  
Claudeに手順を作成してもらい進めました。  
下記の内容も全てClaudeに作ってもらっています。

### 使うサービス

| サービス | 用途 | 料金 |
| --- | --- | --- |
| Azure VM (B1s) | Webサーバー | 12ヶ月無料 |
| Azure OpenAI Service | AIの応答生成 | 従量課金 |
| Flask (Python) | Webアプリフレームワーク | 無料 |

### 完成イメージ

ブラウザからメッセージを送ると、GPT-4oが返答してくれるチャットアプリです。

---

## 1. Azure VMの作成

Azureポータル（[https://portal.azure.com）にログインして仮想マシンを作成します。](https://portal.azure.com%EF%BC%89%E3%81%AB%E3%83%AD%E3%82%B0%E3%82%A4%E3%83%B3%E3%81%97%E3%81%A6%E4%BB%AE%E6%83%B3%E3%83%9E%E3%82%B7%E3%83%B3%E3%82%92%E4%BD%9C%E6%88%90%E3%81%97%E3%81%BE%E3%81%99%E3%80%82)

### 推奨設定

| 項目 | 設定値 |
| --- | --- |
| OS | Windows Server 2022 |
| サイズ | B1s（無料枠対象） |
| 認証 | パスワード |
| リージョン | West US 2 など |

---

## 2. VMへの接続（リモートデスクトップ）

Windows ServerへはRDP（リモートデスクトップ）で接続します。SSHではないので注意。

1. Azureポータル → 仮想マシン → 対象のVM → 「接続」→「RDP」
2. `.rdp` ファイルをダウンロードしてダブルクリック
3. VM作成時に設定したユーザー名・パスワードでログイン

> **Macの場合** はApp Storeで「Microsoft Remote Desktop」を無料インストールして使用

---

## 3. Pythonのインストール

VM内のブラウザで以下のURLを開きます。

```
https://www.python.org/downloads/
```

### 注意点

インストーラーの最初の画面で **「Add Python to PATH」に必ずチェックを入れる**

チェックを忘れた場合はアンインストールして再インストールするのが確実。

### インストールの確認

PowerShellを開いて以下を実行：

```
py --version
py -m pip --version
```

> `python --version` で `Python` とだけ表示される場合は `py --version` を試す。  
> Windowsストア版が干渉している場合は「設定」→「アプリ」→「アプリ実行エイリアス」でストア版をオフにする。

---

## 4. ライブラリのインストール

PowerShellで以下を実行：

```
py -m pip install flask openai azure-storage-blob
```

| ライブラリ | 用途 |
| --- | --- |
| flask | WebサーバーフレームワークDB |
| openai | Azure OpenAI APIの呼び出し |
| azure-storage-blob | Blob Storageへの保存（将来的に使用） |

---

## 5. Azure OpenAI Serviceの作成

### リソースの作成

Azureポータルで「Azure OpenAI」を検索して作成します。

| 項目 | 設定値 |
| --- | --- |
| リージョン | Sweden Central（推奨） |
| 名前 | 任意（例：OA-dev01） |
| 価格レベル | Standard S0 |
| ネットワーク | すべてのネットワーク |

> **リージョンについて**  
> East USやWest US 2ではクォータ不足でモデルをデプロイできない場合がある。  
> Sweden Centralが最もクォータを取りやすくおすすめ。

### APIキーとエンドポイントの取得

作成したリソース → 左メニュー「キーとエンドポイント」から以下をコピーしておく。

> ⚠️ APIキーは絶対に公開しないこと。GitHubにアップしないよう注意。

---

## 6. GPT-4oのデプロイ

### Foundryポータルへ移動

リソース画面の「Foundryポータルに移動」をクリック。

### デプロイ手順

1. 左メニュー「デプロイ」→「モデルのデプロイ」→「基本モデルをデプロイする」
2. `gpt-4o` を選択
3. 以下の設定でデプロイ：

| 項目 | 設定値 |
| --- | --- |
| デプロイ名 | gpt-4o |
| デプロイの種類 | 標準 |
| トークン/分のレート制限 | 最小値 |

> **よくあるエラー**
>
> * `gpt-35-turbo` → 2025年11月に廃止済みで使えない
> * `InvalidCapacity` → トークン/分のレート制限が0になっている。スライダーを動かして最小値に設定する
> * `InvalidResourceSKU` → そのリージョンでそのモデルが使えない。リージョンを変更する

---

## 7. アプリのファイル作成

### フォルダ構成

```
C:\chatapp\
├── app.py
└── templates\
    └── index.html
```

PowerShellでフォルダを作成：

```
mkdir C:\chatapp
mkdir C:\chatapp\templates
cd C:\chatapp
```

### app.py

```
notepad C:\chatapp\app.py
```

以下を貼り付けて保存：

```
from flask import Flask, request, jsonify, render_template
from openai import AzureOpenAI

app = Flask(__name__)

client = AzureOpenAI(
    api_key="YOUR_API_KEY",       # Azure OpenAIのキー1
    api_version="2024-02-01",
    azure_endpoint="YOUR_ENDPOINT" # Azure OpenAIのエンドポイント
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}]
    )
    return jsonify({"reply": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### templates/index.html

```
notepad C:\chatapp\templates\index.html
```

以下を貼り付けて保存：

```
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>AIチャット</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 40px auto; }
    #messages { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
    input { width: 80%; padding: 8px; }
    button { padding: 8px 16px; }
  </style>
</head>
<body>
  <h2>AIチャット</h2>
  <div id="messages"></div>
  <input id="input" type="text" placeholder="メッセージを入力...">
  <button onclick="sendMessage()">送信</button>
  <script>
    async function sendMessage() {
      const input = document.getElementById("input");
      const messages = document.getElementById("messages");
      const userText = input.value;
      if (!userText) return;
      messages.innerHTML += `<p><b>あなた:</b> ${userText}</p>`;
      input.value = "";
      const res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: userText})
      });
      const data = await res.json();
      messages.innerHTML += `<p><b>AI:</b> ${data.reply}</p>`;
      messages.scrollTop = messages.scrollHeight;
    }
  </script>
</body>
</html>
```

---

## 8. サーバーの起動・動作確認

PowerShellで以下を実行：

以下のように表示されれば起動成功：

```
* Running on http://127.0.0.1:5000
* Running on http://10.x.x.x:5000
```

VM内のブラウザで `http://127.0.0.1:5000` を開いてチャットが動けば完成！

---

## つまずきポイントまとめ

| エラー・症状 | 原因 | 対処法 |
| --- | --- | --- |
| `pip` が認識されない | PATHが設定されていない | `py -m pip` を使う or Pythonを再インストール |
| `python` だけ表示される | Windowsストア版が干渉 | アプリ実行エイリアスでオフにする |
| モデルが廃止済み | gpt-35-turboは2025年11月廃止 | gpt-4oを使う |
| スライダーが動かない | クォータ不足 | リージョンをSweden Centralに変更 |
| デプロイできない | リージョンがモデル非対応 | Sweden Centralに変更 |

---

## おわりに

これでAzure VMとAzure OpenAIだけでAIチャットアプリが動くようになりました。  
次のステップとして外部からアクセスできるようにポートを開放したり、Azure Blob Storageで会話履歴を保存する機能を追加したりするとより実用的なアプリになります。
