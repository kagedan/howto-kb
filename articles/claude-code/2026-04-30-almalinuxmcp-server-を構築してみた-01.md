---
id: "2026-04-30-almalinuxmcp-server-を構築してみた-01"
title: "【AlmaLinux】MCP Server を構築してみた"
url: "https://zenn.dev/syyama/articles/a6d92f250f5793"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "zenn"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

Windows上のAIツール（Claude Desktopなど）から、VirtualBox内のLinuxサーバを呼び出してリアルタイムの天気を取得する「MCP（Model Context Protocol）サーバ」を構築する手順をまとめます。

# 0. はじめに

本記事では、OpenWeatherMap APIを利用したMCPサーバを構築する手順を紹介します。

# 1. 仮想マシンの準備

* VirtualBox のインストールと設定
* AlmaLinux 9 ISO をダウンロード

このあたりのインストール手順は他の記事にも上がってるかと思いますので割愛します。

* 設定のポイントとしては、ネットワーク「ブリッジアダプター」を選択しておくとよいでしょう（ホストOSと直接通信するため）。

# 2. 環境構築

AlmaLinux 9標準のPython 3.9ではMCPライブラリの要件を満たさないため、Python 3.11 を導入します。

```
sudo dnf update -y
sudo dnf install python3.11 python3.11-pip -y
```

プロジェクトディレクトリ作成を作成しておきます。

```
mkdir ~/weather-mcp && cd ~/weather-mcp
python3.11 -m venv venv
source venv/bin/activate
```

MCP で利用するライブラリをインストールします。

```
pip install fastmcp requests
```

# 3. MCP サーバの実装

今回は OpenWeatherMap を利用して天気予報を呼び出します。  
OpenWeatherMap の API キーを取得し、以下のファイルを weather\_server.py として保存します。

```
from fastmcp import FastMCP
import requests

mcp = FastMCP("WeatherServer")
API_KEY = "YOUR_API_KEY_HERE"

@mcp.tool()
def get_current_weather(city: str) -> str:
    """指定された都市の現在の天気を取得します。"""
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "ja"}
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{city}の天気は「{weather}」、気温は {temp}℃ です。"
    return f"エラー: {data.get('message', '取得失敗')}"

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

# 4. ファイアウォールの開放と起動

```
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload

python weather_server.py
```

# 5. Claude Desktop の設定

Claude Desktop の「ファイル」→「設定」→「開発者」→「設定を編集」を開く。  
フォルダ内にある `claude_desktop_config.json` を開き、作成した MCP サーバを登録します。

```
{
  "mcpServers": {
    "almalinux-weather": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/inspector",
        "http://[VMのIPアドレス]:8000/sse"
      ]
    }
  }
}
```

※Windows側に Node.js がインストールされている必要があります。

![](https://static.zenn.studio/user-upload/bddefeede68a-20260430.png)

# 6. 動作確認

Claude Desktopを再起動し、以下のように話しかけてみてください。

> AlmaLinux上のMCPサーバを使って、現在の東京の天気を教えて

![](https://static.zenn.studio/user-upload/a6bc6dfd4cbf-20260430.png)

Claude Desktop が MCP を使って get\_current\_weather を呼び出し、VM内のPythonスクリプト経由で最新情報を取得・回答してくれれば成功です！
