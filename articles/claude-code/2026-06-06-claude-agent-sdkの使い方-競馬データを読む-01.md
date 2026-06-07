---
id: "2026-06-06-claude-agent-sdkの使い方-競馬データを読む-01"
title: "Claude Agent SDKの使い方 競馬データを読む"
url: "https://qiita.com/norihito_wada/items/e1f02121720e178b553b"
source: "qiita"
category: "claude-code"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "Python", "qiita"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

# 0.はじめに
Claudeを用いたAIシステム設計スキルの認定資格「Claude Certified Architect–Foundations(CCA-F)試験」の出題範囲にもあるClaude Agent SDK の理解を深めるため、このSDKを使ったPythonコードを書いて何か実際の動作を調べてみることにしました。
そこで今回は、Pythonのコードが、Claude Agent SDKを使ってファイル(競馬データ)を読むところまで試してみましたので、検証結果を共有します。
最初、Windows版もあるようなので Windows 11の個人PCで試してみたところ、Windows版では一部モジュールが利用できない旨のエラーとなったためLinux系のOSで動作させる事にしました。GoogleColabのJupiterNotebookを個人的によく使っていましたが、机上でAIにきいたところ、一部のコマンドはGoogle Colabでは制限があるとのことで、AWSのCloudShell(Linuxベース)上で検証しています。
# 1. Claude Agent SDK を使うために必要なもの
以下のものが必要です。
Anthropic API 契約	:Claude API を使うために必須
API キー	        :SDK が Anthropic に接続するために必要
Python 3.10〜3.12	:SDK が対応しているバージョン
Linux / macOS	    :Code Interpreter が動作する環境
# 2. Anthropic API 契約
Claude Agent SDK を使うためには、Anthropic API(Claude API)の契約をして、APIキーを取得する必要があります。
以下の手順で進めれば、すぐに API キーを取得できます。

#### 1.Anthropic公式サイトへアクセス
https://console.anthropic.com にアクセスし、右上の「Sign up」または「Log in」からアカウントを作成します。

#### 2.支払い情報を登録
Claude API を利用するにはクレジットカード登録が必要です。無料枠はありません。

#### 3.API Keys ページを開く
ログイン後、左側メニューの「API Keys」を選択します。

#### 4.新しい API キーを作成
「Create Key」ボタンを押して API キーを生成します。表示されたキーをコピーして保存します。

#### 5.環境変数に設定
CloudShell や Linux で export ANTHROPIC_API_KEY="取得したキー" を設定して SDK が利用できるようにします。

#### Claude API は 従量課金制です。
料金表（最新）はここで確認できます：
👉 https://www.anthropic.com/pricing

# 3. CloudShellでの実行環境作成

以下のコマンドを実行してClaude-agent-sdkをインストールしました。

```
python3 -m venv venv
source venv/bin/activate
pip install claude-agent-sdk

echo 'export ANTHROPIC_API_KEY="取得したキー"' >> ~/.bashrc
source ~/.bashrc
```

# 4. お試しコードの実行

```
python
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4071206/99811293-d4b0-436c-946a-5a2f845b9cb9.png)
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    prompt = "CloudShell で Claude Agent SDK が動作するかテストします。"

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            allowed_tools=["bash", "python", "filesystem"],
            permission_mode="auto"
        ),
    ):
        print(message)

asyncio.run(main())
```
これをclaudetest-aws.pyファイルに記述して実行。
```
python claudetest-aws.py
```
以下のような結果が返ってきましたので、うまくいったようです。
```
SystemMessage(subtype='init', data={'type': 'system', 'subtype': 'init', 'cwd': '/home/cloudshell-user', 'session_id': '省略', 'tools': ['Task', 'AskUserQuestion', 'Bash', 'CronCreate', 'CronDelete', 'CronList', 'Edit', 'EnterPlanMode', 'EnterWorktree', 'ExitPlanMode', 'ExitWorktree', 'Glob', 'Grep', 'Monitor', 'NotebookEdit', 'PushNotification', 'Read', 'ScheduleWakeup', 'Skill', 'TaskCreate', 'TaskGet', 'TaskList', 'TaskOutput', 'TaskStop', 'TaskUpdate', 'ToolSearch', 'WebFetch', 'WebSearch', 'Write'], 'mcp_servers': [], 'model': 'claude-opus-4-7[1m]', 'permissionMode': 'auto', 'slash_commands': ['update-config', 'verify', 'debug', 'code-review', 'batch', 'fewer-permission-prompts', 'loop', 'claude-api', 'run', 'run-skill-generator', 'clear', 'compact', 'context', 'heapdump', 'init', 'review', 'security-review', 'usage', 'insights', 'goal', 'team-onboarding'], 'apiKeySource': 'ANTHROPIC_API_KEY', 'claude_code_version': '2.1.150', 'output_style': 'default', 'agents': ['claude', 'Explore', 'general-purpose', 'Plan', 'statusline-setup'], 'skills': ['update-config', 'verify', 'debug', 'code-review', 'batch', 'fewer-permission-prompts', 'loop', 'claude-api', 'run', 'run-skill-generator'], 'plugins': [], 'analytics_disabled': False, 'product_feedback_disabled': False, 'uuid': '省略', 'memory_paths': {'auto': '/home/cloudshell-user/.claude/projects/-home-cloudshell-user/memory/'}, 'fast_mode_state': 'off'})
AssistantMessage(content=[ThinkingBlock(thinking='', signature='セキュリティのため省略')], model='claude-opus-4-7', parent_tool_use_id=None, error=None, usage={'input_tokens': 6, 'cache_creation_input_tokens': 17110, 'cache_read_input_tokens': 0, 'cache_creation': {'ephemeral_5m_input_tokens': 17110, 'ephemeral_1h_input_tokens': 0}, 'output_tokens': 0, 'service_tier': 'standard', 'inference_geo': 'global'}, 省略
AssistantMessage(content=[TextBlock(text='CloudShell で Claude Agent SDK のテストですね。動作確認のため、環境を確認します。')], model='claude-opus-4-7', parent_tool_use_id=None, error=None, usage={'input_tokens': 6, 'cache_creation_input_tokens': 17110, 'cache_read_input_tokens': 0, 'cache_creation': {'ephemeral_5m_input_tokens': 17110, 'ephemeral_1h_input_tokens': 0}, 'output_tokens': 0, 'service_tier': 'standard', 'inference_geo': 'global'}, 省略
AssistantMessage(content=[ToolUseBlock(id='toolu_01XzELJGBdwRGsMsyQiHQ48b', name='Bash', input={'command': 'echo "=== 環境情報 ===" && uname -a && echo "" && echo "=== Node.js ===" && node --version 2>/dev/null || echo "Node.js 未インストール" && echo "" && echo "=== Python ===" && python3 --version 2>/dev/null || echo "Python 未インストール" && echo "" && echo "=== 作業ディレクトリ ===" && pwd', 'description': 'Check CloudShell environment'})], model='claude-opus-4-7', parent_tool_use_id=None, error=None, usage={'input_tokens': 6, 'cache_creation_input_tokens': 17110, 'cache_read_input_tokens': 0, 'cache_creation': {'ephemeral_5m_input_tokens': 17110, 'ephemeral_1h_input_tokens': 0}, 'output_tokens': 0, 'service_tier': 'standard', 'inference_geo': 'global'}, 省略
UserMessage(content=　省略
AssistantMessage(content=[TextBlock(text='AWS CloudShell (ap-northeast-1) で動作確認できました。Claude Agent SDK は正常に応答しています。\n\n**確認できた環境:**\n- OS: Amazon Linux 2023 (x86_64)\n- Node.js: v20.20.2\n- Python: 3.13.13\n- 作業ディレクトリ: `/home/cloudshell-user`\n\n何かテストしたい具体的な操作はありますか？例えば:\n- ファイル作成・編集\n- AWS CLI コマンドの実行\n- スクリプトの作成と実行\n- Git リポジトリのクローン\n\nなど、ご要望をお知らせください。')], model='claude-opus-4-7', parent_tool_use_id=None, error=None, usage={'input_tokens': 1, 'cache_creation_input_tokens': 558, 'cache_read_input_tokens': 17110, 'cache_creation': {'ephemeral_5m_input_tokens': 558, 'ephemeral_1h_input_tokens': 0}, 'output_tokens': 2, 'service_tier': 'standard', 'inference_geo': 'global'}, 省略
ResultMessage(subtype='success', duration_ms=13083, duration_api_ms=14186, is_error=False, num_turns=2, session_id='e750020d-ffd5-4dff-95e9-163eb3f60140', stop_reason='end_turn', total_cost_usd=0.133947, usage={'input_tokens': 7, 'cache_creation_input_tokens': 17668, 'cache_read_input_tokens': 17110, 'output_tokens': 576, 'server_tool_use': {'web_search_requests': 0, 'web_fetch_requests': 0}, 'service_tier': 'standard', 'cache_creation': {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 17668}, 'inference_geo': '', 'iterations': [{'input_tokens': 1, 'output_tokens': 218, 'cache_read_input_tokens': 17110, 'cache_creation_input_tokens': 558, 'cache_creation': {'ephemeral_5m_input_tokens': 558, 'ephemeral_1h_input_tokens': 0}, 'type': 'message'}], 'speed': 'standard'}, result='AWS CloudShell (ap-northeast-1) で動作確認できました。Claude Agent SDK は正常に応答しています。\n\n**確認できた環境:**\n- OS: Amazon Linux 2023 (x86_64)\n- Node.js: v20.20.2\n- Python: 3.13.13\n- 作業ディレクトリ: `/home/cloudshell-user`\n\n何かテストしたい具体的な操作はありますか？例えば:\n- ファイル作成・編集\n- AWS CLI コマンドの実行\n- スクリプトの作成と実行\n- Git リポジトリのクローン\n\nなど、ご要望をお知らせください。', 省略
```
# 5. 競馬データの読み込み
JRA公式の競馬分析ソフトウェア「TARGET frontier JV」画面を用いて適当にレースのデータのCSVファイルをたtarget.csvというファイル名で出力しておきます。そのままだとSJISコードのため、念のためエディタで開いたあとUTF-8にコード変換しておきます。
それをCloudShellにアップロードしておきます。
以下のようなPythonコードを記述します。
```
# python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

WATCH_DIR = r"/home/cloudshell-user/target.csv"
DB_TYPE = "postgresql"

async def main():
    prompt = f"""
あなたは TARGET frontier JV の CSV 自動処理エージェントです。

まずは {WATCH_DIR} 内の CSV を一覧し、最新のファイルを読み取ってください。

利用可能ツール:
- filesystem.glob
- filesystem.read_file
"""

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            allowed_tools=["filesystem"],   # ← まずはこれだけ
            permission_mode="auto"
        ),
    ):
        print(message)

asyncio.run(main())
```
実行してみますと、以下出力を抜粋していますが、CSVファイルの中身を読み込んでいることが確認できました。
```
AssistantMessage(content=[TextBlock(text='ツール名 `filesystem.glob` / `filesystem.read_file` は、この環境では実際には登録されていませんでした（利用可能なの は組み込みの Bash / Read などです）。同等の処理を組み込みツールで実行します。まず `/home/cloudshell-user/target.csv` の中身を確認します。')]
AssistantMessage(content=[TextBlock(text='Bash がセッション環境を作成できませんでした（ディスク容量不足: `ENOSPC: no space left on device`）。Bash に依存しない `Read` ツールで直接アクセスを試みます。')],
UserMessage(content=[ToolResultBlock(tool_use_id='', content='<system-reminder>[Truncated: PARTIAL view — showing lines 1-146 of 518 total (75315 tokens, cap 25000). Call Read with offset=147 limit=146 for the next page, or Grep to find a specific section. Do NOT answer from this page alone if the answer may be further in the file.]</system-reminder>\n\n1\t260314,中山,1, 1,未勝利・牝,ダ,1800,フローレスカラーズ,牝,3,丹内祐次,55.0,高木登, 美,ノルマンディーサラブレッドレーシング,オリオンファーム,ダノンレジェンド,ウイニフレッド,23100731,5,スペシャルウィーク,鹿毛,1,-1,0,0,15,     0,     0, 0,   0.0,0,0626250101
```
今回はただ単に競馬データをファイルから読み込んでみるだけの検証でしたが、このような使い方をするものだという事を理解することができました。試験対策として少しでも役立てれば幸いです。
