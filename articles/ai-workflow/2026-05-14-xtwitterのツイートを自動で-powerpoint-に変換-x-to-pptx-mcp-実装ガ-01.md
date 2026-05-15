---
id: "2026-05-14-xtwitterのツイートを自動で-powerpoint-に変換-x-to-pptx-mcp-実装ガ-01"
title: "X（Twitter）のツイートを自動で PowerPoint に変換 | x-to-pptx MCP 実装ガイド"
url: "https://qiita.com/mesaka/items/d02d181bf4f10bc5aa20"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "Python", "JavaScript", "qiita"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

<font color="red">この記事自体もClaudeが書いています。</font>
## はじめに

こんにちは。

**X（Twitter）の記事を PowerPoint で共有したい**と思ったことはありませんか？
<font color="red">※ただし、Xの記事自体は、ポストした人（ユーザ）の著作物なので、そのポストしたユーザの著作権を尊重してください。</font>
通常であれば、ツイート内容を手動でスライドに入力し、手作業でレイアウトを整える必要があります。

しかし、**Claude Desktop の MCP（Model Context Protocol）** を使えば、この作業を完全に自動化できます。

この記事では、**x-to-pptx MCP** という X のツイートから自動で PowerPoint ファイルを生成するツールの実装方法と使い方を、実例を交えて解説します。

## 目次

* はじめに
* x-to-pptx MCP とは
* 動作の仕組み
* 環境構築
* セットアップ手順
* 使用方法
* 実装のコツ
* おわりに

## x-to-pptx MCP とは

**x-to-pptx MCP** は、X（Twitter）のツイート URL から自動的に PowerPoint ファイルを生成する Claude Desktop 用の MCP（Model Context Protocol）サーバーです。

### できること

- **ツイート URL を入力** → Puppeteer がツイート内容をスクレイピング
- **コンテンツを抽出** → タイトル、本文、著者名、画像を自動取得
- **PowerPoint を生成** → python-pptx で美しいスライドを作成
- **自動保存** → Windows のダウンロードフォルダに PPTX ファイルを保存

### 用途

- 技術情報をまとめた記事の共有
- X のスレッドをスライド資料に変換
- チーム内での情報共有フロー の自動化
- ツイート情報からプレゼンテーション資料を自動生成

## 動作の仕組み
![mcp_process_flow.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/76892/e7f3effc-3ba9-4acb-899b-5a3bb48c1ab7.png)


### 全体フロー

1. **入力**: X のツイート URL（例: `https://x.com/user/status/123456789`）
2. **スクレイピング**: Puppeteer がブラウザでツイートを読み込み、テキスト・著者名・画像を抽出
3. **データ処理**: 抽出したデータを JSON 形式に変換
4. **PPTX 生成**: python-pptx が複数スライドを自動生成
5. **出力**: `X_Article_YYYYMMDD_HHMMSS.pptx` として保存

### 技術スタック

- **Node.js + Puppeteer**: X のコンテンツを動的にスクレイピング
- **Python + python-pptx**: PowerPoint スライドを生成
- **Claude Desktop MCP**: Claude がツールを呼び出すインターフェース

### なぜ MCP を使うのか？

MCP は Claude Desktop 上で外部ツールを拡張可能にするプロトコルです。このアーキテクチャにより：

- Claude が直接 Python や Node.js スクリプトを実行可能
- 複雑な処理を段階的に実行可能
- エラーハンドリングが簡潔

## 環境構築

### 前提条件

以下をすべて用意してください：

- **Claude Desktop** アプリ
- **Python 3.12** 以上
- **Node.js** LTS 版
- **インターネット接続**

### Python 3.12 のインストール

1. [Python 公式サイト](https://www.python.org/downloads/) からダウンロード
2. インストール時に **「Add Python 3.12 to PATH」にチェック** を入れる
3. ターミナルで確認:

```bash
python --version
# Python 3.12.x が表示されれば成功
```

### Node.js のインストール

1. [Node.js 公式サイト](https://nodejs.org/) から LTS 版をダウンロード
2. インストーラーを実行（デフォルト設定で OK）
3. ターミナルで確認:

```bash
node --version
npm --version
# バージョン番号が表示されれば成功
```

### Claude Desktop のインストール

1. [Claude Desktop ダウンロード](https://claude.ai/download) ページから入手
2. インストールして起動
3. Anthropic アカウントでログイン

## セットアップ手順
![setup_flowchart.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/76892/63181072-4246-4fd9-950d-29755a60ab89.png)
![directory_tree_structure.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/76892/ee35faef-abf4-4f32-9297-e09164cdb8b3.png)

### ステップ 1: プロジェクトフォルダを作成

Windows PowerShell を「管理者として実行」して、以下を実行:

```powershell
mkdir "C:\Users\[ユーザー名]\Claude_MCP\x-to-pptx-mcp"
cd "C:\Users\[ユーザー名]\Claude_MCP\x-to-pptx-mcp"
```

`[ユーザー名]` は自分の Windows ユーザー名に置き換えてください。

### ステップ 2: package.json を作成

テキストエディタで以下の内容を保存:

```json
{
  "name": "x-to-pptx-mcp",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "puppeteer": "^21.0.0"
  }
}
```

### ステップ 3: npm パッケージをインストール

```powershell
npm install
```

### ステップ 4: index.js を作成

テキストエディタで以下の内容を `index.js` として保存:

```javascript
// index.js - Puppeteer スクレイピング版 MCP サーバー

import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import readline from "readline";
import puppeteer from "puppeteer";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class MCPServer {
  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: false,
    });

    this.rl.on("line", (line) => {
      try {
        const message = JSON.parse(line);
        this.handleMessage(message);
      } catch (e) {
        // サイレント
      }
    });
  }

  handleMessage(message) {
    const { jsonrpc, id, method, params } = message;

    if (method === "initialize") {
      this.respond(id, {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: {
          name: "x-to-pptx-mcp",
          version: "1.0.0",
        },
      });
    } else if (method === "tools/list") {
      this.respond(id, {
        tools: [
          {
            name: "x_article_fetch",
            description:
              "X のツイート URL からコンテンツを取得します。",
            inputSchema: {
              type: "object",
              properties: {
                x_url: {
                  type: "string",
                  description: "X のツイート URL",
                },
              },
              required: ["x_url"],
            },
          },
          {
            name: "x_to_pptx",
            description:
              "X の記事情報から PPTX ファイルを生成します。",
            inputSchema: {
              type: "object",
              properties: {
                x_url: {
                  type: "string",
                  description: "X の記事 URL",
                },
                title: {
                  type: "string",
                  description: "記事のタイトル",
                },
                content: {
                  type: "string",
                  description: "記事の本文",
                },
                author: {
                  type: "string",
                  description: "著者名",
                },
                image_url: {
                  type: "string",
                  description: "画像 URL（オプション）",
                },
              },
              required: ["x_url", "title", "content", "author"],
            },
          },
        ],
      });
    } else if (method === "tools/call") {
      const { name, arguments: args } = params;
      if (name === "x_article_fetch") {
        this.fetchXArticlePuppeteer(args, id);
      } else if (name === "x_to_pptx") {
        this.generatePPTX(args, id);
      } else {
        this.respond(id, { error: `Unknown tool: ${name}` });
      }
    }
  }

  async fetchXArticlePuppeteer(args, id) {
    let browser = null;
    try {
      const { x_url } = args;

      if (!x_url.includes("x.com") && !x_url.includes("twitter.com")) {
        this.respond(id, {
          content: [
            {
              type: "text",
              text: "❌ エラー: X の URL が正しくありません。",
            },
          ],
        });
        return;
      }

      browser = await puppeteer.launch({
        headless: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox"],
      });

      const page = await browser.newPage();
      await page.goto(x_url, {
        waitUntil: "networkidle2",
        timeout: 30000,
      });

      const tweetData = await page.evaluate(() => {
        const tweetTextElement = document.querySelector(
          '[data-testid="tweet"] [data-testid="tweetText"]'
        );
        const text = tweetTextElement
          ? tweetTextElement.innerText
          : "テキスト取得失敗";

        const authorElement = document.querySelector(
          '[data-testid="tweet"] [data-testid="Tweet-User-Name"]'
        );
        const author = authorElement
          ? authorElement.innerText
          : "不明";

        const imageElements = document.querySelectorAll(
          '[data-testid="tweet"] img[alt*="画像"]'
        );
        let imageUrl = null;
        if (imageElements.length > 0) {
          imageUrl = imageElements[0].src;
        }

        return {
          text,
          author,
          imageUrl,
        };
      });

      await browser.close();

      const title =
        tweetData.text.substring(0, 100) +
        (tweetData.text.length > 100 ? "..." : "");
      const authorName = tweetData.author.split("\n")[0];

      this.respond(id, {
        content: [
          {
            type: "text",
            text: `✅ ツイート内容を取得しました！

【タイトル】
${title}

【本文】
${tweetData.text}

【著者】
${authorName}

${tweetData.imageUrl ? `【画像 URL】\n${tweetData.imageUrl}` : ""}`,
          },
        ],
      });
    } catch (error) {
      if (browser) await browser.close();

      this.respond(id, {
        content: [
          {
            type: "text",
            text: `❌ スクレイピングエラー: ${error.message}`,
          },
        ],
      });
    }
  }

  generatePPTX(args, id) {
    const pythonScript = path.join(__dirname, "generate_pptx.py");
    const pythonPath =
      "C:\\Users\\[ユーザー名]\\AppData\\Local\\Programs\\Python\\Python312\\python.exe";

    const argsWithDefaults = {
      ...args,
      image_url: args.image_url || "",
    };

    const process = spawn(
      pythonPath,
      [pythonScript, JSON.stringify(argsWithDefaults)],
      {
        stdio: ["pipe", "pipe", "pipe"],
      }
    );

    let stdout = "";
    let stderr = "";

    process.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    process.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    process.on("close", (code) => {
      if (code === 0) {
        this.respond(id, {
          content: [
            {
              type: "text",
              text: stdout,
            },
          ],
        });
      } else {
        this.respond(id, {
          content: [
            {
              type: "text",
              text: `❌ PPTX 生成エラー:\n${stderr}`,
            },
          ],
        });
      }
    });
  }

  respond(id, result) {
    const response = {
      jsonrpc: "2.0",
      id,
      result,
    };
    console.log(JSON.stringify(response));
  }
}

new MCPServer();
```

`[ユーザー名]` を自分の Windows ユーザー名に置き換えてください。

### ステップ 5: generate_pptx.py を作成

テキストエディタで以下の内容を `generate_pptx.py` として保存:

```python
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import os
from datetime import datetime
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    import requests
except ImportError:
    print("❌ 必要なパッケージがありません: pip install python-pptx pillow requests")
    sys.exit(1)

def generate_pptx(args):
    x_url = args.get("x_url", "")
    title = args.get("title", "無題")
    content = args.get("content", "内容なし")
    author = args.get("author", "不明")
    image_url = args.get("image_url", "")
    
    output_dir = Path.home() / "Downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # スライド1: タイトル
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide1.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(25, 29, 34)
    
    title_box = slide1.shapes.add_textbox(
        Inches(0.5), Inches(2), Inches(9), Inches(2)
    )
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    title_frame.text = title
    title_frame.paragraphs[0].font.size = Pt(44)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    author_box = slide1.shapes.add_textbox(
        Inches(0.5), Inches(4.2), Inches(9), Inches(1)
    )
    author_frame = author_box.text_frame
    author_frame.text = f"著者: {author}"
    author_frame.paragraphs[0].font.size = Pt(18)
    author_frame.paragraphs[0].font.color.rgb = RGBColor(113, 118, 123)
    
    url_box = slide1.shapes.add_textbox(
        Inches(0.5), Inches(5.5), Inches(9), Inches(1)
    )
    url_frame = url_box.text_frame
    url_frame.text = f"Source: {x_url}"
    url_frame.paragraphs[0].font.size = Pt(12)
    url_frame.paragraphs[0].font.color.rgb = RGBColor(113, 118, 123)
    
    # スライド2: 記事概要
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    background2 = slide2.background
    fill2 = background2.fill
    fill2.solid()
    fill2.fore_color.rgb = RGBColor(247, 249, 249)
    
    heading = slide2.shapes.add_textbox(
        Inches(0.5), Inches(0.5), Inches(9), Inches(0.8)
    )
    heading_frame = heading.text_frame
    heading_frame.text = "📝 記事概要"
    heading_frame.paragraphs[0].font.size = Pt(32)
    heading_frame.paragraphs[0].font.bold = True
    heading_frame.paragraphs[0].font.color.rgb = RGBColor(25, 29, 34)
    
    content_box = slide2.shapes.add_textbox(
        Inches(0.5), Inches(1.5), Inches(9), Inches(5.5)
    )
    content_frame = content_box.text_frame
    content_frame.word_wrap = True
    content_frame.text = content
    content_frame.paragraphs[0].font.size = Pt(16)
    content_frame.paragraphs[0].font.color.rgb = RGBColor(25, 29, 34)
    
    # スライド3: 画像（オプション）
    if image_url:
        slide3 = prs.slides.add_slide(prs.slide_layouts[6])
        background3 = slide3.background
        fill3 = background3.fill
        fill3.solid()
        fill3.fore_color.rgb = RGBColor(247, 249, 249)
        
        img_heading = slide3.shapes.add_textbox(
            Inches(0.5), Inches(0.5), Inches(9), Inches(0.8)
        )
        img_heading_frame = img_heading.text_frame
        img_heading_frame.text = "🖼️  参考画像"
        img_heading_frame.paragraphs[0].font.size = Pt(32)
        img_heading_frame.paragraphs[0].font.bold = True
        img_heading_frame.paragraphs[0].font.color.rgb = RGBColor(25, 29, 34)
        
        try:
            response = requests.get(image_url, timeout=10)
            temp_img_path = output_dir / "temp_image.jpg"
            with open(temp_img_path, 'wb') as f:
                f.write(response.content)
            
            slide3.shapes.add_picture(
                str(temp_img_path),
                Inches(1),
                Inches(1.5),
                width=Inches(8)
            )
            temp_img_path.unlink()
        except Exception as e:
            print(f"⚠️  画像追加失敗: {e}", file=sys.stderr)
    
    # ファイル保存
    filename = f"X_Article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    filepath = output_dir / filename
    prs.save(str(filepath))
    
    return str(filepath)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            args = json.loads(sys.argv[1])
            filepath = generate_pptx(args)
            
            print(f"✅ PPTX ファイルを生成しました")
            print(f"📁 保存先: {filepath}")
            print(f'PowerShell: start "{filepath}"')
            print(f"🎉 処理完了！")
        except Exception as e:
            print(f"❌ エラー: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("❌ 引数がありません", file=sys.stderr)
        sys.exit(1)
```

### ステップ 6: Python パッケージをインストール

PowerShell を「管理者として実行」して:

```powershell
pip install python-pptx pillow requests --break-system-packages
```

### ステップ 7: Claude Desktop の設定を編集

以下のパスにある `claude_desktop_config.json` を開く:

```
C:\Users\[ユーザー名]\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

以下の内容を追加:

```json
{
  "mcpServers": {
    "x-to-pptx": {
      "command": "node",
      "args": [
        "C:\\Users\\[ユーザー名]\\Claude_MCP\\x-to-pptx-mcp\\index.js"
      ]
    }
  }
}
```

### ステップ 8: Claude Desktop を再起動

Claude Desktop を完全に終了して、再度起動してください。

## 使用方法
![usage_flow_diagram_fixed.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/76892/e7255e05-6060-4888-98b6-13c83d845a31.png)

### 基本的な使い方

Claude Desktop で以下のように入力:

```
URL: https://x.com/user/status/1234567890 を x_to_pptx でまとめて。
```

### 処理フロー

1. **入力**: X のツイート URL を指定
2. **ツイート取得**: Claude が `x_article_fetch` ツールを呼び出し
3. **コンテンツ抽出**: タイトル、本文、著者、画像を自動取得
4. **PPTX 生成**: Claude が `x_to_pptx` ツールを呼び出し
5. **ファイル保存**: `C:\Users\[ユーザー名]\Downloads\X_Article_YYYYMMDD_HHMMSS.pptx` に保存

### 出力ファイルの確認

生成されたファイルは Windows のダウンロードフォルダに保存されます。

自動的に PowerPoint が開きます。

## 実装のコツ
![tech_stack_diagram_corrected.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/76892/8d4f6808-b0b6-4e7b-9d64-4bda3b0602d6.png)

### カスタマイズ例

#### 1. スライドデザインの変更

`generate_pptx.py` の色設定を編集:

```python
# ダークテーマ（現在）
fill.fore_color.rgb = RGBColor(25, 29, 34)

# 自分の好みに変更
fill.fore_color.rgb = RGBColor(100, 150, 200)  # 青系
```

#### 2. フォントサイズの調整

```python
title_frame.paragraphs[0].font.size = Pt(44)  # タイトル
content_frame.paragraphs[0].font.size = Pt(16)  # 本文
```

#### 3. スライド数の追加

`generate_pptx.py` に新しい `slide` を追加:

```python
slide4 = prs.slides.add_slide(prs.slide_layouts[6])
# スライド4の設定...
```

### トラブルシューティング

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `Command not found: python` | Python が PATH に登録されていない | Python を再インストール（PATH チェック） |
| `Module not found: pptx` | python-pptx がインストールされていない | `pip install python-pptx` を実行 |
| `Puppeteer timeout` | ネットワーク接続が遅い | URL を再度確認、ネット接続を確認 |
| Claude Desktop でツール表示なし | MCP サーバーが起動していない | Claude Desktop を再起動 |

## おわりに

**x-to-pptx MCP** は、X のコンテンツを効率的に PowerPoint に変換できる強力なツールです。

### このツールで実現できること

- 手作業でのコンテンツコピーが不要
- デザイン統一されたスライドが自動生成
- チーム内での情報共有が加速
- コンテンツライブラリの構築が容易

### 次のステップ

1. **環境構築を完了** → セットアップ手順に従う
2. **テスト実行** → サンプルツイート URL で試す
3. **カスタマイズ** → デザインや機能を自分好みに調整
4. **運用自動化** → 日常のワークフローに組み込む

分かりやすい記事を書くことは、読者に**情報を効果的に伝える**ためのスキルです。

このツールが、皆さんの情報発信をより効率的にしてくれることを願っています！

**ぜひ実装してみて、フィードバックがあればお聞きかせください。**
