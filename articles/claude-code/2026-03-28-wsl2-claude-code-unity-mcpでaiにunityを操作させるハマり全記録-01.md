---
id: "2026-03-28-wsl2-claude-code-unity-mcpでaiにunityを操作させるハマり全記録-01"
title: "WSL2 × Claude Code × Unity MCPで、AIにUnityを操作させる【ハマり全記録】"
url: "https://zenn.dev/acropapa330/articles/unity_mcp_wsl_claude"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "Python", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

# WSL2 × Claude Code × Unity MCPで、AIにUnityを操作させる【ハマり全記録】

## はじめに

「Claude CodeにUnityを操作させたい」と思って調査を始めたところ、**MCP for Unity** というOSSパッケージを発見。

ただしWSL2環境では素直に繋がらず、ポート競合・Python競合など複数のハマりどころがありました。

この記事では**完全に動作するまでにつまずいたポイントをすべて記録**しています。同じ環境で試す人の時間を節約できれば幸いです。

そして最後に、**想定外のおまけ発見**もあります。

---

## 環境・構成

```
Windows 11
├── Unity 2022 LTS（yabou01_studio プロジェクト）
│   └── MCP for Unity パッケージ（CoplayDev/unity-mcp）
└── WSL2 Ubuntu
    └── Claude Code CLI（claude コマンド）
```

**接続イメージ：**

```
Claude Code (WSL2)
  ↕ MCP (HTTP)
Unity Editor (Windows)
```

Claude CodeはWSL2側で動かし、Unity EditorはWindows側で動かします。MCP for UnityがHTTPサーバーとして動作し、両者を繋ぎます。

---

## Step 1: MCP for Unity パッケージを Unity にインストール

Unity Package Manager でGit URLからインストールします。

```
Window > Package Manager > + > Add package from git URL
```

Git URL:

```
https://github.com/CoplayDev/unity-mcp.git#main
```

インストール後、以下でウィンドウを開きます：

---

## Step 2: uv / uvx のインストール

MCP for Unityのサーバーは**uvx**（Pythonランタイム管理ツール）経由で起動します。

**WSL2側：**

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows側（PowerShell）：**

```
# uvxが入っていない場合
pip install uv
```

---

## Step 3: Unity側の設定（ここで最初のハマり）

MCP for Unity ウィンドウを開くと以下の設定項目があります：

* **Transport**: `HTTP Local` を選択
* **HTTP URL**: `http://127.0.0.1:8081`
* `Start Server` ボタンを押す

### ハマり1: `Failed to Start`

**現象：** `Start Server` を押すと `Failed to Start` と表示される。

**原因：** ポート `8080` が他のプロセス（WSL2ネットワーキング等）に占有されていました。Unityコンソールに以下のログが出ていました：

```
Refusing to stop port 8080...
```

**対処：** ポートを `8081` に変更。URLを `localhost` ではなく `127.0.0.1` に統一することで解決しました。

### ハマり2: Python実行エラー

**現象：** `Start Server` 時に以下のようなエラー：

```
Could not find a suitable Python executable ... LibreOffice ...
```

**原因：** `uvx` がLibreOffice同梱のPythonを参照していました。

**対処1：** `UV_PYTHON` 環境変数で正しいPythonを固定：

```
setx UV_PYTHON "C:\Users\YourName\AppData\Local\Python\bin\python.exe"
```

**対処2（確実）：** Unityウィンドウの `Advanced > UVX Path` にuvxのフルパスを入力。

**対処3（最終手段）：** Unityのサーバー起動をスキップして、PowerShellから**手動起動**：

```
$env:UV_PYTHON="C:\Users\YourName\AppData\Local\Python\bin\python.exe"
& "C:\Users\YourName\.local\bin\uvx.exe" `
  --python "C:\Users\YourName\AppData\Local\Python\bin\python.exe" `
  --from "mcpforunityserver==9.6.2" `
  mcp-for-unity --transport http --http-url http://127.0.0.1:8081
```

### 正常起動の確認

Unityウィンドウで以下の状態になれば成功：

* `Local Server: Stop Server` 表示（起動中）
* `Session Active` が**緑表示**

---

## Step 4: WSL2側でClaude Codeに登録

**重要：** Unity側のHTTPサーバーが起動したら、WSL2側のClaude CodeにMCPサーバーとして登録します。

```
# 古い設定が残っている場合は削除
claude mcp remove unity-mcp

# HTTP モードで再登録
claude mcp add --transport http unityMCP http://127.0.0.1:8081/mcp
```

### 接続確認

以下のように `✓ Connected` が出れば完了です：

```
unityMCP: http://127.0.0.1:8081/mcp (HTTP) - ✓ Connected
```

### 疎通確認（curlで直接叩く）

```
curl -i http://127.0.0.1:8081/mcp
```

`406 Not Acceptable` と `Client must accept text/event-stream` が返ってくれば正常です（SSE前提のエンドポイントのため、素のcurlではこの反応が正常）。

---

## Step 5: Claude CodeからUnityを操作してみる

Claude Codeを起動して試します：

セッション内で話しかけます：

**結果：**

```
SampleScene の GameObject 一覧：
- Main Camera（コンポーネント: Transform, Camera, AudioListener / タグ: MainCamera）
- Directional Light（コンポーネント: Transform, Light / タグ: Untagged）
```

Unity EditorのSceneビューに配置されているオブジェクトが取得できました。

他にもこんなことができます：

```
# GameObjectを作成
「Player という空のGameObjectを作って、位置を (0, 1, 0) にして」

# コンポーネントを追加
「PlayerにCharacterControllerを追加して、height=1.8に設定して」

# スクリプト生成
「Assets/Scripts/Player/PlayerController.cs を作成して、WASD移動を実装して」

# コンソールログ確認
「Unityコンソールの最新エラーを20件見せて」
```

---

## 再起動後のチェックリスト

毎回以下の順番で確認すると安定して使えます：

1. Unity Editorを起動、`Window > MCP For Unity` を開く
2. `HTTP URL = http://127.0.0.1:8081` を確認
3. `Start Server` → `Session Active` （緑）を確認
4. WSL2で `claude mcp list` → `✓ Connected` を確認

---

## おまけ：TelegramボットからもUnityが操作できた

ここからが想定外の発見です。

私はClaude Codeを呼び出すTelegramボット（クロエちゃん）を運用しています。「このボットからもUnity操作できたりするかな？」と半分冗談で試したところ、**できてしまいました。**

### なぜ動くのか

MCP for UnityのHTTPサーバーは `http://127.0.0.1:8081/mcp` というエンドポイントで動いています。これは**Claude Code専用のプロトコルではなく、HTTPが話せれば何でも叩けるエンドポイント**です。

PythonのHTTPリクエストで直接叩けます：

```
import requests
import json

MCP_URL = "http://127.0.0.1:8081/mcp"

def call_unity_mcp(tool_name: str, arguments: dict):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(MCP_URL, json=payload, headers=headers)
    return response.json()

# GameObjectの一覧を取得
result = call_unity_mcp("get_hierarchy", {})
print(result)
```

### 実際にやってみた：TelegramからCubeを作成

Telegramで「Cubeを作成してGameObject一覧を表示して」と送ったところ、**本当に動いた**ので結果を記録しておきます。

**Cube作成後のGameObject一覧（Telegramへの返答）：**

```
現在の SampleScene の GameObject 一覧（全3件）：

| 名前           | コンポーネント                                        | タグ       |
|--------------|------------------------------------------------|----------|
| Main Camera  | Transform, Camera, AudioListener               | MainCamera |
| Directional Light | Transform, Light                          | Untagged |
| MyCube       | Transform, MeshFilter, BoxCollider, MeshRenderer | Untagged |
```

`MyCube` が座標 (0, 0, 0) に作成されており、Unity Editor を見るとシーン上にCubeが出現していました。

スマホのTelegramから「Cube作って」と打ち込んで、Unity Editor上にオブジェクトが出現するのは、かなり不思議な感覚です。

### さらにやってみた：TelegramからMyCubeにマーブルマテリアルを適用

調子に乗って「MyCubeのマテリアルをマーブルにして」と送ったところ、これも成功しました。

**実行された内容：**

1. `Assets/Materials/MarbleMaterial.mat` を作成（Standard シェーダー）
2. MyCube の MeshRenderer に MarbleMaterial を割り当て
3. カラーを大理石風のオフホワイト（R:0.92, G:0.90, B:0.87）に設定
4. Smoothness を 0.9 に設定（大理石らしいツヤ感）

自然言語の指示1行で、マテリアル作成からオブジェクトへの割り当てまで一連の作業が完了しました。テクスチャ画像なしでプロシージャル的にそれらしい見た目を再現できています。

### 気づき

> **MCPはClaude Code専用の仕組みではない。HTTPが話せれば、TelegramボットでもPythonスクリプトでも、何でもUnityに命令できる。**

MCP（Model Context Protocol）はあくまで「AIツールと外部システムをつなぐプロトコル」であり、クライアントはClaude Codeに限られません。これはかなり応用が広そうです。

---

## まとめ

| 項目 | 内容 |
| --- | --- |
| 使用パッケージ | CoplayDev/unity-mcp |
| 推奨ポート | 8081（8080は競合しやすい） |
| 接続方式 | HTTP（`127.0.0.1` で統一） |
| Python問題 | UV\_PYTHON で固定 or 手動起動で回避 |
| Claude Code登録 | `claude mcp add --transport http` |
| 意外な発見 | TelegramボットなどHTTPクライアントなら何でも叩ける |

WSL2環境特有のハマりどころは多いですが、一度繋がってしまえば非常に快適にUnityを操作できます。AIに「Playerオブジェクト作って」と頼むだけでUnity EditorにGameObjectが出現するのは、やはり面白いです。

---

## 参考
