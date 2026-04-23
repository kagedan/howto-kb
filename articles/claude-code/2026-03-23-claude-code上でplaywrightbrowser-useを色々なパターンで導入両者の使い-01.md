---
id: "2026-03-23-claude-code上でplaywrightbrowser-useを色々なパターンで導入両者の使い-01"
title: "Claude Code上でPlaywright、Browser Useを色々なパターンで導入＆両者の使い分けについて考えてみる"
url: "https://zenn.dev/shinyaa31/articles/dd315ea4868eb1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/5b794e85b24a-20260323.png)

生成AIと絡める形での『ブラウザ自動化ツール』として共に著名なサービスである**Playwright**と**Browser Use**。私個人も最近はこれらのサービスに興味関心が強く、様々な局面や課題に有効活用出来ないものか...と調べ始めたところです。

当エントリではまず最初のステップとして、この両サービスをClaude/Claude Code経由で利用出来るような手筈を整えるところまでを備忘録としてまとめておこうと思います。そして最後のパートでは『どういう使い分けをすれば良いのか？』という所に思いを馳せていきます。

## 前提条件

私個人の作業環境はプライベート/仕事共にmacOS(Apple M4)。なので設定手順諸々もmacOSを想定したものとなります。

```
% sw_vers
ProductName:    macOS
ProductVersion: 26.3
BuildVersion:   25D125
```

Claude(Claude Desktop)/Claude Codeは予め導入済みな状態とします。  
![](https://static.zenn.studio/user-upload/34528e201936-20260323.png)

```
% claude --version
2.1.81 (Claude Code)
```

## 様々な方法で導入を試してみる

### PythonライブラリとしてPlaywrightをインストール

まずは1ケース目。PythonライブラリとしてPlaywrightをインストールするところから始めてみました。

既にuvは導入済み、pythonも任意のバージョンで指定をしておいた状況でplaywrightによるブラウザバイナリのダウンロードまで行いました。(※実際はClaude Codeの設定で`CLAUDE.md`ファイルにpipなどのコマンド禁止、パッケージ管理・仮想環境には `uv` のみを使う旨指定した上で、Claude Codeに『Playwrightをインストールして』と伝えただけでした)

```
# 1. 仮想環境を作成
% uv --version
uv 0.9.5 (Homebrew 2025-10-21)
% uv venv .venv

# 2. 仮想環境を有効化してplaywrightをインストール
% source .venv/bin/activate && uv pip install playwright
# (なお、導入時のuv配下pythonバージョンは以下の通り)
% python --version
Python 3.12.12

# 3. ブラウザバイナリをダウンロード
% playwright install
```

動作確認用にPythonコードを用意し、実行。

hello.py

```
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)           # Chrome系のブラウザを開く
    page = browser.new_page()                             # 新しいタブを開く
    page.goto("https://github.com/microsoft/playwright")  # サイトにアクセス
    page.screenshot(path="sample.png")                    # スクリーンショットを撮る
    browser.close()
```

プログラムを実行し、下記のような画面キャプチャが取れていれば成功です。

![](https://static.zenn.studio/user-upload/f2fcd63fe84c-20260322.png)

※参考：

### Playwright MCPサーバ連携設定

Playwright MCPサーバーの設定に関しては下記公式GitHubリポジトリを参照。いずれも手順はシンプルです。

<https://github.com/microsoft/playwright-mcp>

Claude Codeの場合は下記コマンド一発。

```
% claude mcp add playwright npx @playwright/mcp@latest
```

Claude Desktopの場合は左下ユーザーメニューから[設定]→[開発者]を選択し、[設定を編集]から対応する設定ファイル(`claude_desktop_config.json`)を開いて下記設定を追記。

claude\_desktop\_config.json

```
  "mcpServers": {
    : 
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
    :
  }
```

設定完了後、以下のような形でPlaywrightの設定が有効化(running)されていればOKです。

![](https://static.zenn.studio/user-upload/3fa1a06aa575-20260322.png)

Playwright MCPに指示を出して、欲しい結果が得られました。

![](https://static.zenn.studio/user-upload/32dd3198e14e-20260322.png)  
![](https://static.zenn.studio/user-upload/8650be8c6694-20260322.png)

### PlaywrightをCLI&Skillとしてインストール

playwrightはCLIコマンドとして導入することも可能です。

<https://github.com/microsoft/playwright-cli>

上記リポジトリの説明曰く、「コーディングエージェントを使っている場合、CLI呼び出しの方がトークン効率が良く、大きなツールスキーマや冗長なアクセシビリティツリーをコンテキストに読み込まずに済むためにMCPではなくCLI+SKILLSの方が恩恵がある(かもしれない)」とのこと。確かにトークン消費量が押さえられるのは利用者にとっては非常に嬉しいポイントですね。これも入れてみましょう。

導入自体はnpmコマンドで速攻です。

```
## npmコマンドでインストール
% npm install -g @playwright/cli@latest
% playwright-cli --version
1.59.0-alpha-1771104257000
## help内容を参照してみる.
% playwright-cli --help

上述の様に、CLIと併せてSkillの導入も案内されています。これもコマンド一発。
```shell
## この導入方法だとグローバルな形でインストールすることは出来なさそう。なので導入が必要なClaude Codeプロジェクト配下でコマンドを実施する必要あり
% playwright-cli install --skills
✅ Workspace initialized at `/Users/xxxxxxxx/Desktop/xxxxxxxx-claude-code-workspace`.
✅ Skills installed to `.claude/skills/playwright-cli`.
✅ Found chrome, will use it as the default browser.
```

Claude Code上で`/skills`コマンドにて確認。プロジェクトのスキルとして表示されていれば導入完了です。

![](https://static.zenn.studio/user-upload/ebf1278f0144-20260323.png)

Claude Code上で以下の指示を出してみます。

> Playwrightのスキルを使って <https://demo.playwright.dev/todomvc/>  
> をテストし、成功パターンと失敗パターンのそれぞれでスクリーンショットを取得してください。

結果は以下の通り。上記説明の通り、確かにサクサクテストが進んでいる感じはありました。

![](https://static.zenn.studio/user-upload/b3501cd48eee-20260323.png)

対象ページのスクリーンショットも以下のようにちゃんと取ってくれています。

![](https://static.zenn.studio/user-upload/b9e181cc0d1c-20260323.png)

### Browser UseをCLIとしてインストール

続いてはBrowser Use。CLIから導入してみます。コマンド一発での導入が推奨ということなので今回はそれに従ってみました。

実行後はシェルの設定ファイルに情報を追記して読み込め、と言っています。

```
% curl -fsSL https://browser-use.com/cli/install.sh | bash
:
 Installed profile-use v1.0.2 to /Users/xxxxxxxx/.browser-use/bin/profile-use

Note: /Users/xxxxxxxx/.browser-use/bin is not in your PATH.
Add it by running:

  export PATH="/Users/xxxxxxxx/.browser-use/bin:$PATH"

Or add that line to your ~/.bashrc, ~/.zshrc, or equivalent.

Get started:
  profile-use auth    # set your API key
  profile-use list    # see detected browsers
  profile-use --help  # see all commands
✓ profile-use installed
✓ Added to PATH in /Users/xxxxxxxx/.bashrc
ℹ Validating installation...

Diagnostics:

  ✓ package: browser-use unknown
  ✓ browser: Browser profile available
  ✓ network: Network connectivity OK
  ✓ cloudflared: cloudflared installed (/opt/homebrew/bin/cloudflared)
  ✓ profile_use: profile-use installed (/Users/xxxxxxxx/.browser-use/bin/profile-use)

✓ All checks passed!
✓ Installation validated successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Browser-Use installed successfully!

Next steps:
  1. Restart your shell or run: source ~/.bashrc
  2. Try: browser-use open https://example.com

Documentation: https://docs.browser-use.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

私個人は普段zshrc派なので、~/.bashrcに書かれていた内容をそのまま~/.zshrcに転記しました。(最下行は後続の設定を進める過程で追記したものです。必要に応じて追加しておいてください)

```
# Browser-Use
export PATH="/Users/xxxxxxxx/.browser-use-env/bin:/Users/xxxxxxxx/.local/bin:$PATH"
export PATH="$HOME/.browser-use-env/bin:$PATH"
```

設定後はdoctorコマンド実行で診断します。『cloudflaredを入れろ』と指摘されました。

```
% browser-use doctor

Diagnostics:

  ✓ package: browser-use unknown
  ✓ browser: Browser profile available
  ✓ network: Network connectivity OK
  ○ cloudflared: cloudflared not installed (needed for browser-use tunnel)
      Fix: Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
  ✓ profile_use: profile-use installed (/Users/xxxxxxxx/.browser-use/bin/profile-use)

⚠ 4/5 checks passed, 1 missing
```

Cloudflareのドキュメントに従いインストール。brewでサクッと入りました。  
<https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/>

```
% brew install cloudflared
```

改めて診断。今度は全部通りました。

```
% browser-use doctor

Diagnostics:

  ✓ package: browser-use unknown
  ✓ browser: Browser profile available
  ✓ network: Network connectivity OK
  ✓ cloudflared: cloudflared installed (/opt/homebrew/bin/cloudflared)
  ✓ profile_use: profile-use installed (/Users/xxxxxxxx/.browser-use/bin/profile-use)

✓ All checks passed!
```

setupコマンド実行。

```
% browser-use setup

✓ Running checks...

  ✓ browser use package: browser-use installed
  ✓ browser: Browser available

✓ No additional setup needed!

✓ Validation:

  ✓ browser use import: ok
  ✓ browser available: ok

✓ Setup complete!
Next: browser-use open https://example.com
```

```
% browser-use install
📦 Installing Chromium browser + system dependencies...
⏳ This may take a few minutes...

✅ Installation complete!
🚀 Ready to use! Run: uvx browser-use
```

`browser-use`の各種コマンドを使って動作確認。

```
## ヘッドレスモードで開く
% browser-use open https://zenn.dev/shinyaa31/ 
## 可視モードで開く
% browser-use --headed open https://zenn.dev/shinyaa31/
```

※参考

### Browser UseをSkillsとしてインストール

[Browser Use CLIのドキュメント](https://docs.browser-use.com/open-source/browser-use-cli)には、以下の記述があります。『強くお勧めします』と言われたらやらない訳にはいかないですね。導入しましょう。

> CLIは、そのスキルと組み合わせることで最大の効果を発揮します。スキルは、コーディングエージェントにすべてのコマンド、フラグ、ワークフローに関する完全なコンテキストを提供します。CLIと並行してスキルをインストールすることを**強くお勧めします**。

![](https://static.zenn.studio/user-upload/65dbbce7cfb4-20260323.png)

Node.js をインストールして npm を使える状態にしておきます。npxというコマンドも利用出来るようになっているはず。

以下npxコマンドを実行。

```
% npx skills add https://github.com/browser-use/browser-use --skill browser-use
```

[Additional Agents]で `Claude Code`を選択(移動は上下キー、選択はスペースキーで)し、Enter押下。

![](https://static.zenn.studio/user-upload/702a86806756-20260323.png)

スコープとインストール方法を任意の方式で選択し、インストール実行。今回はスコープ：グローバル(全てのプロジェクトで使いたかったから)、インストール方法＝複製(推奨とされているsymlinkで最初試したんだけど、Claude Code側で`/Skills`の一覧に出てこなかったので結局こっちにした)で進めました。

無事インストール完了です。

![](https://static.zenn.studio/user-upload/b808c82a1bbf-20260323.png)

また、併せて`find-skills`というのもインストールしました。(※これは当初symlink方式で導入した際、上述browser-use導入のタイミングで併せて導入されていたもの。symlink方式を止めて複製方式でやるとなった際に上述手順でbrowser-use導入時に入ってこなかったので、念のためこちらも同じ方式で揃えて入れてみました。実際今後必要かどうか、無いと困るかどうかまでは調査しておらず)

```
% npx skills add vercel-labs/skills@find-skills
```

Claude Code側で`/skills`コマンドを実行、上述2つのスキルが導入されていることを確認出来ました。  
![](https://static.zenn.studio/user-upload/80a6ec97293f-20260323.png)

Claude Codeから以下の指示を出してみたところ、

```
> browser-useのSkillsを使って、神奈川県横浜市の直近1週間の天気予報情報を調べてください。
```

良い感じで情報を出してきてくれました。

![](https://static.zenn.studio/user-upload/5e1d86f29674-20260323.png)

## Playwright/Browser Useはどのように使い分ける？

エントリ冒頭でも言及したように『PlaywrightとBrowser useの使い分け』について考えてみたいと思います。世の中的には『こっちが良いのでもう片方は...』派と『両方使い分けるのが良いのでは...』派で分かれているようです。個人的には後者の『使い分け』派ではあるのですが、じゃあどういう使い分けが良いのか？という部分に関しては全然検討がついてません...。

と、色々調べていたらこのトピックについて詳細に言及解説しているエントリがあったのでこちらを読み解いていきたいと思います。  
<https://www.nxcode.io/resources/news/stagehand-vs-browser-use-vs-playwright-ai-browser-automation-2026>

要約内容は概ね以下の通り。比較的考えとしても棲み分け、振り分けしやすい判断軸となったような気がします。

* **記事の全体像**
  + 元記事はPlaywright、Browser Use、そしてStagehand(これは今回考慮に入れてなかったので除外)を「AIブラウザ自動化の設計思想」で比較する内容
  + 大きく見ると、Playwrightは決定論的自動化、Browser Use は自律エージェント、Stagehand はその中間に置かれている
  + "Claude連携の観点"では、「Claudeにどこまで判断を任せるか」が見分け方の軸になっている
* **Playwrightの位置付け**
  + 既知の画面を正確に操作するための高速・低コスト・高再現性の基盤的側面が強い
  + UIテスト、回帰テスト、決まった操作手順の自動化に特に向いている
  + 一方で、UI変更やDOM変更には弱く、保守が必要になりやすい
* **Browser Useの位置付け**
  + Browser Useは、LLM が画面を見て次の行動を判断する"エージェント型のブラウザ自動化サービス"
  + 細かい手順を固定するより、「ゴールだけ渡す」使い方に向いている
  + 複数サイト横断の調査、比較、探索、入力補助のような作業と相性が良い
* **Claudeとの連携について**
  + PlaywrightをClaude Codeと組み合わせる場合は、「Claudeが考え、Playwrightが確実に実行する」という分担が自然
  + Browser Useの公式ドキュメントでは、Claude Codeには HTTP ベースの MCP、Claude DesktopにはローカルstdioベースのMCPが案内されている
  + Anthropic の公式情報では、Claude Desktop から Claude in Chrome コネクタ経由でブラウザ操作を始められる
* **実務での使い分け方針**
  + 開発・検証・既知フローの品質確認を重視するなら、Playwright
  + 調査・比較・探索・柔軟な操作代行を重視するなら、Browser Use
  + 実践的には、安定部分を Playwright、曖昧で変化しやすい部分を Browser Use に任せるハイブリッド運用が最も現実的

上記NxCodeのエントリを含め、その他参考になりそうなエントリを幾つか置いておきます。

## まとめ

という訳で、ブラウザ自動化ツールのPlaywrightとBrowser Useの導入パターン数ケースの実践、及び導入後の『両サービスの使い分け』方針についての情報をまとめてみたご紹介エントリでした。実に様々な方法が提供されていることに驚く一方で、やはりコンテキスト消費量を考えるとCLI・Skill方面で活用したほうが良いのかなぁ...と思う次第です。このような形で環境導入の手順を提供、整えてくれている方々に感謝しつつ、より効率化、高速化を目指して引き続き関連ツールの習熟と整備に邁進していこうと思います。

---

## この記事を読んだ方へ

感想・フィードバックは X（[@shinyaa31](https://x.com/shinyaa31)）までお気軽にどうぞ。
