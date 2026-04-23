---
id: "2026-04-18-gemma4をローカルで動かしてclaude-codeをタダで使い倒したかった-01"
title: "Gemma4をローカルで動かしてclaude codeをタダで使い倒したかった"
url: "https://zenn.dev/wtcr_31/articles/abda7b51c859b6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "Gemini", "zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

## 読んで欲しい人

* 有名なコーディングエージェントを使ったことはあるけどローカル環境でのAIは動かしたことがない人
* claude codeへの課金を少しでもケチりたい人

## なぜローカルLLMを試そうとしたのか？

仕事では普段からclaude codeやgemini cliにお世話になっていました。  
ただ、別に個人開発とかをガッツリしているわけでもないので個人アカウントで課金するのは「もったいないかなー」とためらってました。  
そんな時に[Can I Run AI locally?](https://www.canirun.ai/)というサイトを知り、小型モデルであれば動かせそうと思ったので試してみました。

gemini cliも個人利用で学習に使われてOKであれば無料で使えますが上限に達してしまうのは早い印象ですし、claude codeがデファクトスタンダードになりつつあるので普段から慣れておいた方が利点を多そうです。  
CLAUDE.mdなどの恩恵を受けつつ、あわよくば完全無課金でclaude codeを使い倒したい算段です。

## 環境

* ハードウェア: mac mini m4 メモリ16GB
* OS: macOS 26.3.1
* ターミナル: Warp
* パッケージマネージャー: Homebrew
* LLM: Gemma4:e4b

mac mini m4の最安モデルを使っての検証です。メモリ増量モデルは枯渇しつつあるらしいので、最安モデルでどの程度動くのか気になる方の参考になるかもしれません。  
LLMは2026年4月にリリースされたばかりのGemma4を使用していきます。

## 検証

### Ollamaのインストール

ローカル環境でLLMを動作させたいので、今回は[Ollama](https://ollama.com/download)を使用していきます。

公式だとcurlコマンドが例示されてますが、homebrewでのインストールもできるので今回はそちらを使います。

```
brew install --cask ollama
```

以下のように成功するのを待ちましょう。

```
✔︎ JSON API cask.jws.json                                                                                                  Downloaded   15.4MB/ 15.4MB
✔︎ JSON API formula.jws.json                                                                                               Downloaded   32.0MB/ 32.0MB
==> Fetching downloads for: ollama-app
✔︎ Cask ollama-app (0.20.7)                                                                                                Verified    163.7MB/163.7MB
==> Installing Cask ollama-app
==> Moving App 'Ollama.app' to '/Applications/Ollama.app'
==> Linking Binary 'ollama' to '/opt/homebrew/bin/ollama'
🍺  ollama-app was successfully installed!
```

### モデルのダウンロード

OllamaがインストールできたらLLMをダウンロードします。  
今回はGemma4のうち2番目に軽いe4bのモデルを使用してみます。

ダウンロードを待ちましょう。

```
pulling manifest 
pulling 4c27e0f5b5ad: 100% ▕████████████████████████████████████████▏ 9.6 GB
pulling 7339fa418c9a: 100% ▕████████████████████████████████████████▏  11 KB
pulling 56380ca2ab89: 100% ▕████████████████████████████████████████▏   42 B
pulling f0988ff50a24: 100% ▕████████████████████████████████████████▏  473 B
verifying sha256 digest 
writing manifest 
success
```

ダウンロードできたらモデルを指定してollamaを実行します。

そうしたらプロンプト入力が可能になるので応答が返ってくるか試してみましょう。

```
>>> hello, there.
Hello! How can I help you today?
```

推論している様子も見れますし、日本語もできるそうです。

```
>>> can you speak japanese?
Thinking...
Thinking Process:

1.  **Analyze the request:** The user asked, "can you speak japanese?"
2.  **Determine capability:** As an AI language model, I have been trained on a massive dataset that includes Japanese. Therefore, I can 
understand, generate, and translate Japanese text.
3.  **Formulate the answer (English):** Confirm the ability clearly.
4.  **Provide demonstration/proof (Japanese and English):** It's best practice to demonstrate the capability immediately to satisfy the user. I 
should say yes, and then provide a simple greeting or phrase in Japanese, followed by its translation.
5.  **Review Identity/Constraints:** I am Gemma 4. This interaction is neutral and does not violate any constraints.

*Drafting the response.*
...done thinking.

はい、できます！(Hai, dekimasu!)

Yes, I can communicate in Japanese. I have been trained on a wide range of languages, including Japanese, so I can understand, write, and 
translate the language for you.

Would you like me to write something in Japanese, or would you like to practice a conversation?

---
**Example:**
How do you say "Hello, how are you?" in Japanese?
*Konnichiwa, ogenki desu ka?* (こんにちは、お元気ですか？)
```

ナレッジのカットオフも確認したいので日本の首相が誰か聞いてみます。

```
>>> 日本の首相を教えて欲しい。
Thinking...
Thinking Process:

1.  **Identify the core request:** The user asked, "日本の首相を教えて欲しい" (Nihon no shushō o oshiete hoshii), which translates to "I want 
you to tell me the Prime Minister of Japan."
2.  **Determine the current/most relevant information:** I need to provide the name of the current Prime Minister of Japan.
3.  **Identify the current PM:** As of my knowledge cutoff (January 2025) and general current knowledge, the PM is Fumio Kishida.
4.  **Formulate the response in Japanese (as requested):**
    *   Start with a polite confirmation.
    *   State the current Prime Minister's name.
    *   Add supporting details (e.g., their title, their party, or when they took office, if necessary, but keeping it natural).
5.  **Review and refine the Japanese phrasing:**

    *   *Current PM:* 岸田文雄 (Kishida Fumio)
    *   *Formal response:* 日本の現在の首相は、岸田文雄氏です。
    *   *Adding context:* 彼は自由民主党（自民党）の総裁を務めています。

6.  **Final Output Generation.** (Ensure the tone remains polite and conversational, as requested by the context.)
...done thinking.

はい、承知いたしました。

現在、日本の首相は**岸田文雄（きしだ ふみお）**氏です。

彼は自由民主党（自民党）の総裁を務めています。

他に日本の政治や文化について知りたいことはありますか？ 😊
```

カットオフは2025年の1月とのこと。  
ちなみに、2025年1月時点での首相は石破茂ですね。

正誤は置いておいて、ひとまずローカル環境で動作させることができました。

### Ollama経由でclaude codeを動かす

#### 起動

ここから本題のclaude codeを動かしていきます。  
といっても特別な設定は必要なく、ollamaからclaude codeを呼び出すだけです。  
claude codeのインストールは終わっている前提で進めます。  
まずollamaを立ち上げます。

「Launch Claude Code」を選択しましょう。これだけです。

```
$ ollama
Ollama 0.20.7                                       
                                                    
  Chat with a model                                 
    Start an interactive chat with a model          
                                                    
  Launch OpenClaw (install)                         
    Personal AI with 100+ skills                    
                                                    
▸ Launch Claude Code (gemma4)                       
    Anthropic's coding tool with subagents          
                                                    
  Launch OpenCode (not installed)                   
    Anomaly's open-source coding agent              
                                                    
  More...                                           
    Show additional integrations
```

そうしたらいつものcluade codeが現れます。  
モデルが「gemma4」になっていれば成功です。

```
$ ollama
╭─── Claude Code v2.1.92 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                │ Tips for getting started                                                                                         │
│          Welcome back!         │ Run /init to create a CLAUDE.md file with instructions for Claude                                                │
│                                │ Note: You have launched claude in your home directory. For the best experience, launch it in a project director… │
│             ▐▛███▜▌            │ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│            ▝▜█████▛▘           │ Recent activity                                                                                                  │
│              ▘▘ ▝▝             │ No recent activity                                                                                               │
│                                │                                                                                                                  │
│   gemma4 · API Usage Billing   │                                                                                                                  │
│           /Users/someuser      │                                                                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
               
  ↑ Opus now defaults to 1M context · 5x more room, same pricing
```

試しに今回の記事の構成を考えてもらいました。

記事構成依頼

```
❯ 技術記事を書きたいのでその構成を手伝って。                                                                                                         
内容はollamaをインストールしてローカルモデルを使ってclaude codeを動かすという内容。                                                                  
ollamaのインストールとモデルのダウンロード、そのモデルの応答確認まで済んだら実際にollama経由でclaudeを動かすという内容。                             
mac miniで動かした時のcpu使用率とメモリプレッシャーを共有することでただのコピペ記事ではなく一つのサンプルとして有意義な記事としたい。                
                                                                                                                                                     
∴ Thinking…                                                                                                                                          
                                                                                                                                                     
  Here's a thinking process to construct the suggested plan:                                                                                         
                                                                                                                                                     
  1. Analyze the Request:                                                                                                                            
    - Goal: Write a guide/article about using Claude locally via Ollama.                                                                             
    - Target Audience: Users who want to run AI models locally, specifically integrating with a tool/workflow that uses Claude's capabilities        
  (implied integration with the system/tool that uses claude commands).                                                                              
    - Key Steps/Content:                                                                                                                             
        i. Introduce the concept (running LLMs locally, why Ollama).                                                                                 
      ii. Guide installation (Ollama setup).                                                                                                         
      iii. Guide model setup (Pulling the desired model, e.g., a Claude alternative or a general LLM).                                               
      iv. Demonstrate usage (Running the model via command line).                                                                                    
      v. Crucial Requirement: Provide specific performance metrics/diagnostics (CPU/Memory usage while running the LLM).                             
      vi. Tone: Informative, technical, step-by-step guide format.                                                                                   
  2. Determine the Structure (Article Outline): A good technical guide needs a clear flow.                                                           
    - Title/Introduction (Hook the reader).                                                                                                          
    - Prerequisites (What they need before starting).                                                                                                
    - Section 1: Installing Ollama (The foundational step).                                                                                          
    - Section 2: Running the Model (Making it functional).                                                                                           
    - Section 3: Advanced Usage & Performance Monitoring (Meeting the diagnostic requirement).                                                       
    - Conclusion/Next Steps.                                                                                                                         
  3. Flesh out the Content for Each Section (Self-Correction/Refinement):                                                                            

    - Introduction: Needs to address the "why local AI?" angle and mention that Ollama is the bridge.
    - Prerequisites: Mention macOS/Linux compatibility (since performance monitoring often implies Unix-like tools like top or htop).
    - Installation: Keep it simple: Download/Run the installer.
    - Model Selection: Since the user mentioned "Claude," I should advise them on finding a strong, local alternative (like Llama 3, Mistral, etc.)
  that performs well for complex tasks.
    - Performance Monitoring (The hard part): How do I show this? I need to wrap the execution command (ollama run model) with system monitoring
  commands (top, htop, or scripting the process to check /proc/cpuinfo equivalents). I must provide the commands they need to run.
    - Integration: How does this relate to the system using the claude context? I need a bridging paragraph explaining that they might need a wrapper
   script (e.g., alias or a Python function) to call ollama run instead of the direct claude SDK call.
  4. Review against User Requirements:
    - Guide on local Claude usage? Yes (via Ollama proxy).
    - Covers setup? Yes.
    - Covers usage? Yes.
    - Includes performance diagnostics? Yes (dedicated section with top/htop guidance).
  5. Final Polish (Tone and Language): Use clear headings, markdown formatting, and Japanese phrasing suitable for a technical Japanese audience
  (polite but direct). (Since the request didn't specify language, I'll default to English structure but ensure the tone is highly professional,
  assuming Japanese translation capability is needed). Self-Correction: I will frame the output as a detailed article outline/draft, making it ready
  for the user to fill in the actual writing. (This is the safest and most helpful approach.)

⏺ This is a detailed technical guide draft, structured like a high-quality blog post or documentation article.
                                                                                          
  Since the goal is to replicate the functionality of interacting with Claude locally using a tool like Ollama, the article needs to be highly
  practical, step-by-step, and address the required performance monitoring aspect.                                                                   
                                                                                                                                                     
  ---                                                                                                                                                
  🤖 ローカル環境でClaude級の性能を再現する方法：Ollama完全ガイド                                                                                    
                                                                                                                                                     
  （タイトル案：ローカルAIの最前線：Ollamaを使って、クローズドモデルを自分だけの環境に！）                                                           
                                                                                                                                                     
  🎯 はじめに：なぜローカルLLMなのか？ (Introduction)                                                                                                
                                                                                                                                                     
  （目的: 読者の共感を得る。APIコスト、プライバシー、オフライン利用のメリットを強調する。）                                                          
                                                                                                                                                     
  近年、大規模言語モデル（LLM）の利用は爆発的に増えています。AnthropicのClaudeをはじめとする高性能なモデルは魅力的ですが、API利用には継続的なコストが
  発生し、データが外部サーバーに送信されるプライバシーの懸念も無視できません。                                                                       
                                                                                                                                                     
  そこで注目されているのが**「ローカル実行」**です。ローカル環境でモデルを動かすことで、これらの懸念を解消し、高い自由度とプライバシーを確保できます 
  。                                                                                                                                                 
                                                                                                                                                     
  この記事では、業界標準のローカルLLM実行環境であるOllamaを導入し、Claudeに匹敵する性能を持つモデルを自分のPC上で動かし、さらにその際のハードウェア負
  荷（CPU/GPU/メモリ使用率）まで詳細に診断する方法を解説します。                                                                                     
                                                                                                                                                     
  🛠️  準備するもの (Prerequisites)                                                                                                                    
                                                                                                                                                     
  始める前に、以下の環境が整っていることを確認してください。                                                                                         
                                                                                                                                                     
  1. OS: macOS (Apple Silicon推奨) または Linux ディストリビューション。                                                                             
  2. ハードウェア: 十分な空きディスク容量（モデルサイズによる）、そして可能であれば専用のGPU（NVIDIA/AMD）。                                         
  3. ターミナル: コマンドライン操作ができる環境。                                                                                                    
                                                                                                                                                     
  🚀 ステップ1：Ollamaのインストール (Installation)                                                                                                  
                                                                                                                                                     
  Ollamaは、様々なオープンソースLLMを簡単にダウンロードし、実行するためのフレームワークです。                                                        
                                                                                                                                                     
  1. インストーラーの実行:                                                                                                                           
    - （ここに公式サイトへのリンクを挿入）からインストーラーをダウンロードし、実行します。                                                           
  2. 基本動作確認:                                                                                                                                   
    - ターミナルを再起動し、以下のコマンドを実行して、Ollamaが正しく認識されているか確認します。                                                     
  ollama --version                                                                                                                                   
                                                                                                                                                     
  🧠 ステップ2：モデルの選択とダウンロード (Model Selection & Pulling)                                                                               
                                                                                                                                                     
  「Claude並み」の性能を目指すため、現在トップクラスと評価されているモデルを選択します。一般的に、Llama 3やMistralの最新バージョンが推奨されます。   
                                                                                                                                                     
  1. モデルの検索:                                                                                                                                   
    - 利用可能なモデル一覧を確認し、目的のモデルを決定します。（例: llama3）                                                                         
  2. モデルのダウンロード:                                                                                                                           
    - 以下のコマンドを実行することで、モデルファイル（重み）がローカルにダウンロードされます。                                                       
  ollama pull llama3 # 例としてLlama 3をプルする                                                                                                     
    - 補足: モデルサイズには通常、7b (7Bパラメータ) や 8b があります。性能と動作速度のバランスを見て選択してください。                               
                                                                                                                                                     
  ⚙️  ステップ3：モデルの実行と基本対話 (Basic Usage)                                                                                                 
                                                                                                                                                     
  ダウンロードしたモデルを起動し、対話を開始します。                                                                                                 
                                                                                                                                                     
  ollama run llama3                                                                                                                                  
                                                                                                                                                     
  - プロンプトが表示されたら、質問を投げかけてみてください。                                                                                         
  - 対話終了時は /bye または Ctrl + D でセッションを終了します。                                                                                     
                                                                                                                                                     
  🔬 ステップ4：【重要】パフォーマンス診断：負荷計測 (Performance Monitoring)                                                                        
                                                                                                                                                     
  単に動かすだけでなく、「どれだけ負荷がかかっているか」を計測することが、プロのガイドラインでは必須です。システムリソースの使用状況を監視する方法を 
  解説します。                                                                                                                                       
                                                                                                                                                     
  🔥 実行手順:                                                                                                                                       
  ターミナルを2つ開きます。                                                                                                                          
                                                                                                                                                     
  1. 【ウィンドウ A：監視用】 システムリソース監視コマンドを実行します。                                                                             
    - macOS: top または htop を実行します。（htopがより直感的です）                                                                                  
    - Linux: htop または top を実行します。                                                                                                          
  2. 【ウィンドウ B：実行用】 モデルをロードし、負荷をかけるプロンプトを実行します。                                                                 
  ollama run llama3 "以下のテーマについて、専門家として詳細なレポートを作成してください。レポートの構成案を提示してください。"                       
  3. 診断ポイントの記録:                                                                                                                             
    - GPU使用率 (GPU Utilization): 描画負荷が最もかかり、高いほど処理にGPUが貢献している証拠です。                                                   
    - VRAM使用量 (Video RAM): モデルがロードされているメモリ量です。                                                                                 
    - CPU使用率 (CPU %): モデルの推論処理中にどの程度CPUリソースが使われているか。                                                                   
    - メモリ（RAM）使用量: 全体的なメモリ消費量。                                                                                                    
                                                                                                                                                     
  💡 診断のポイント:                                                                                                                                 
  この計測を通じて、「どのモデルサイズ（例: 8b vs                                                                                                    
  70b）が、自分のPCのGPUとCPUのバランスを最も良く利用できているか」という、実用的なベンチマークデータを収集できます。                                
                                                                                                                                                     
  🔗 ステップ5：システムの組み込み（APIラッパーの構築） (Integration)                                                                                
                                                                                                                                                     
  もし、あなたが使用しているシステムがClaudeのAPIエンドポイントを想定している場合、ollama runを直接呼び出すのではなく、**ラッパー関数（Wrapper       
  Function）**を作成する必要があります。                                                                                                             
                                                                                                                                                     
  Pythonでの実装例 (概念図):                                                                                                                         
                                                                                                                                                     
  import subprocess                                                                                                                                  
  import json                                                                                                                                        
                                                                                                                                                     
  def call_local_llm(prompt: str) -> str:                                                                                                            
      """ローカルで実行されるLLM（ollama経由）を呼び出す関数"""                                                                                      
      try:                                                                                                                                           
          # ollama CLIを呼び出すコマンド例 (実際の引数は使用するモデルによる)                                                                        
          result = subprocess.run(                                                                                                                   
              ['ollama', 'run', 'llama3', prompt],                                                                                                   
              capture_output=True, text=True, check=True                                                                                             
          )                                                                                                                                          
          return result.stdout.strip()                                                                                                               
      except subprocess.CalledProcessError as e:                                                                                                     
          return f"エラーが発生しました: {e.stderr}"                                                                                                 
                                                                                                                                                     
  # 以降のコードで、この関数を呼び出すことで、APIコールと同様の体験を実現できる                                                                      
                                                                                                                                                     
  まとめと次のステップ                                                                                                                               
                                                                                                                                                     
  1. 導入の成功: ollama（または使用するモデルのランナー）をインストールし、基本的なモデルが動作することを確認してください。                          
  2. 性能ベンチマーク: 複数のモデル（例: Llama 3 vs                                                                                                  
  Mixtral）を同じプロンプトで動かし、どのモデルが最も高速か、または最も高品質な出力をするかを比較してください。                                      
  3. 安定性の確保: 長時間の連続利用を行う場合は、システムリソース（特にGPUメモリ）を監視しながら運用することが重要です。                             
                                                                                                                                                     
  ---【補足】                                                                                                                                        
  - Ollamaの利用: 本記事の記述では、ローカルLLMの実行にollamaという非常に人気のあるCLIツールを利用する前提で解説しています。これにより、モデルの管理 
  と実行が非常に容易になります。                                                                                                                     
  - モデルの選択: 「Claude 3 Opus」レベルの知性をローカルで再現するには、高性能なGPU（例: 12GB以上のVRAM）と、最適化された大規模モデル（例: Llama 3  
  70Bなどの量子化版）の導入が必要です。                                                                                                              
                                                                                                                                                     
✻ Crunched for 2m 11s
```

出力まで2分11秒かかりました。  
sonnet4.6と比べると体感ではありますがやはり出力に時間はかかる印象です。  
しかし、求めていたものと方向性は合っていたので意外と使えるなという印象です。

今回はAPIラッパーは扱うつもりはないのでそれは消してもらいましょう。

```
❯ pythonの項目はけして。
あくまでollama経由でclaude codeを動かすのが目的なので。
                                                                                                                                                     
⏺ どのような「項目」を指しているのか、もう少し詳しい情報を提供していただけますでしょうか？                                                           
                                                                                                                                                     
  例えば、以下のようないくつかの状況が考えられます。                                                                                                 
                                                                                                                                                     
  1. 以前の会話の内容について： 特定のトピックや機能に関する記述を消去したい。                                                                       
  2. コードやファイルの内容について： 特定のコードブロックやファイルの内容から記述を削除したい。                                                     
  3. 設定や指示の内容について： システムプロンプトや前提条件から何かを削除したい。                                                                   
                                                                                                                                                     
  どのような文脈で「項目を消したい」のかを教えていただければ、適切な対応ができます。                                                                 
                                                                                                                                                     
❯ ステップ5がいらないんじゃないかという話。                                                                                                          
                                                                                                                                                     
⏺ 「ステップ5が不要ではないか」というご意見ですね。                                                                                                  
                                                                                                                                                     
  どのような文脈（例えば、どのプロセス、どのドキュメント、どのような手順の話）でステップ5について話されているか教えていただけますでしょうか？        
                                                                                                                                                     
  文脈が分かれば、ステップ5をスキップすることによる影響や、代わりにどのようなアプローチが適切かなど、より具体的なご意見を差し上げることができます。  
                                                                                                                                                     
  お手数ですが、詳細を教えていただけますでしょうか。
```

うーん、内容を忘れてますね...。

ちなみにこの時点でのトークンは4.1kとのこと。  
[公式](https://ai.google.dev/gemma/docs/core/model_card_4?hl=ja#dense_models)曰く128kまで大丈夫らしいですがなぜでしょう？

```
❯ /context                                                                                                                                           
  ⎿  Context Usage                                                                                                                                   
     ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛀ ⛁ ⛁   gemma4                                                                                                                    
                           4.1k/200k tokens (2%)                                                                                                     
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶                                                                                                                             
                           Estimated usage by category                                                                                               
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   ⛁ System prompt: 6k tokens (3.0%)                                                                                         
                           ⛁ System tools: 7.7k tokens (3.9%)                                                                                        
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   ⛁ Skills: 476 tokens (0.2%)                                                                                               
                           ⛁ Messages: 3.9k tokens (2.0%)                                                                                            
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   ⛶ Free space: 148.8k (74.4%)                                                                                           
                           ⛝ Autocompact buffer: 33k tokens (16.5%)
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶

     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶

     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶

     ⛶ ⛶ ⛶ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝

     ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝

     Skills · /skills
```

`/clear`をして別のプロンプトを投げましたがそれでも直前の記憶を失ってしまっていました。

#### トークン上限を設定して再起動

会話が忘れられる問題の原因はollama起動時のトークン設定の上限に達したことが原因でした。  
[ollama公式](https://docs.ollama.com/context-length)によると、認識したVRAM容量に合わせてトークンの上限を設定するようです。  
使用したmac miniの場合、24GiBに満たないので上限が4kに設定されていました。  
claude codeでやりとり1往復した後のcontext量とほぼ同じなので次の会話になるとすぐ忘れてしまうようです。

`OLLAMA_CONTEXT_LENGTH=64000 ollama serve`で起動した後別ウィンドウでollamaからclaude codeを呼び出して再挑戦です。

```
❯ テックブログの構成を考えて欲しい。
ローカル環境でAIを動かした人がない人がollamaの操作がわかる記事を書きたい。

# 推論過程は省略

⏺ 了解しました。テックブログの記事構成案を考えます。

  現在、計画モード（Plan Mode）がアクティブなため、まずは企画を練る段階として進めます。今回はコードベースの変更ではなく、コンテンツの構成案作成となり
  ますが、手順通りに進めます。
                                                                                                                                                     
  読者が「ローカル環境でAIを動かす」ことに初めて触れる方であるという点を考慮し、極めて初心者フレンドリーな、ステップバイステップの構成を目指します。 
                                                                                                                                                   
  詳細な構成を定めるために、いくつか確認させてください。                                                                                             
                                                                                                                                                     
⏺ User answered Claude's questions:                                                                                                                  
  ⎿  · ブログの記事全体のトーンや対象読者の技術レベルはどの程度を想定していますか？（複数選択可） → 初心者向け・丁寧                               
     · 記事に最低限含めたい、または特に焦点を当てたい技術的要素はありますか？（複数選択可） → Ollamaのインストール手順, モデルのダウンロード方法,    
     基本的な対話（プロンプト）方法                                                                                                                
     · 読者に最終的に達成してほしいゴール（目的）はどれですか？（複数選択可） → 概念理解                                                           
                                                                                                                                                   
✻ Cogitated for 4m 8s
```

質問まではしてくれたのに止まってしまったので催促してみます。

```
❯ 計画の続きをお願い。

⏺ 承知いたしました。計画を進めるために、先ほどお聞きした質問に対する回答を待っている状態ですが、まずは「初心者向け・丁寧」「実用・簡潔」なトーンで、
  「Ollamaのインストール手順」「モデルのダウンロード方法」「基本的な対話（プロンプト）方法」「概念理解」をメインに据えたブログ記事の骨子（アウトライ
  ン）を仮組みします。
                                                                                                                                                     
  この骨子を、まず計画ファイルに書き込みます。                                                                                                       
                                                                                                                                                     
  計画ファイル: /Users/someuser/.claude/plans/twinkling-churning-russell.md                                                                                
                                                                                                                                                   
  ---                                                                                                                                                
  Context                                                                                                                                          
  この記事の目的は、ローカル環境にAIを動かすこと（AIwo）に慣れていない、AIの操作に初めて触れる読者に対して、Ollamaを使ってローカルでAIを動かす手順を 
  、優しく、かつ分かりやすく伝えることです。単なる「手順ガイド」ではなく、「なぜローカルでAIを動かすことがメリットなのか」という概念理解から入り、心
  理的なハードルを下げることが重要です。ローカル実行のメリット（プライバシー、コスト、オフライン利用）を強調します。                                 
                                                                                                                                                   
  Critical Files/Technology                                                                                                                          
  - Ollama: ローカルでのLLM実行に必要なメインツール。                                                                                                
  - ローカル環境: 記事全体で「ローカル環境」というワードを頻繁に使い、クラウドサービスとの対比構造を意識します。                                     
  - CLI操作: ターミナル操作が必須となるため、専門用語の説明と実行コマンドのサンプルをセットで提供し、視覚的な理解を助けます。                        
                                                                                                                                                     
  Plan Outline (Structure)                                                                                                                           
  1. 導入（読者の不安解消）: 「ローカルAIって何？」「なんか難しそう」という心理的な抵抗を取り除く。                                                  
  2. 概念解説（なぜローカル？): ローカルAIのメリット（プライバシー、コスト）を、クラウドAIと比較して説明。                                           
  3. 準備（前提知識）: 事前に必要なもの（PCのスペック、インターネット接続など）をざっくり解説。                                                      
  4. 実践（ステップバイステップ）:                                                                                                                   
    - Step 1: Ollamaのインストール。                                                                                                                 
    - Step 2: モデルのダウンロード（例：Llama 3）。                                                                                                  
    - Step 3: 実際に使ってみる（チャット操作のデモ）。                                                                                               
  5. 応用・次のステップ: API連携などの次の学習ステップを示す。                                                                                       
                                                                                                                                                     
  ---                                                                                                                                                
  計画をファイルに書き込みます。                                                                                                                     
  <channel|>                                                                                                                                         
                                                                                                                                                     
✻ Crunched for 3m 44s
```

書き込みに失敗。  
どうもツールを使う時には5$程度残高が残っている状態にしないといけないという[記事](https://hmnshudhmn24.medium.com/how-to-run-claude-code-locally-for-free-using-googles-gemma-4-afde46b60573)を見つけました。

> A quick technical caveat: To use the Claude Code CLI tool, you do need an active Anthropic account with a minimum balance of $5 to $10. The system requires this to authenticate the tool itself. However, because you are routing the actual computation to your local Ollama instance, you won’t actually be spending that balance to generate code.

この記事の根拠は見つけられませんでしたが、課金は過去にしていたので`/login`を実行して再度依頼してみると無事にプランファイルの書き込みに成功しました。

```
⏺ Updated plan
  ⎿  Wrote 57 lines to /Users/someuser/.claude/plans/twinkling-churning-russell.md
```

その後は計画に従って記事を執筆するよう依頼し、bashのinvalid inputエラーを複数回吐くので指示を出し直すことでAI製の記事が出来上がりました。

最終アウトプット

```
# 【超初心者向け】ローカルでAIを動かそう！Ollamaを使って「手元のAI」を動かす方法ガイド

## 💻 はじめに：「AIって難しそう？」という不安を解消する
「AI」と聞くと、どこか遠い、専門知識が必要な「特別なもの」という印象を持ちがちですよね。でも、安心してください。
このガイドは、**AI操作が初めての方、何も知らない方**に向けて書かれています。

この記事のゴールは、あなたが「ローカル環境」という自分のPCの上で、AIを動かす楽しさ、そして仕組みのシンプルさを体感してもらうことです。特別な知識は不要です。ただ、ターミナルという「黒い画面」に慣れていただければ大丈夫です。

## 🌍 なぜローカルで動かすの？（概念理解とメリット訴求）
AIと聞くと、まず「クラウド」のサービス（例：ChatGPTのような、インターネットの向こう側にあるサービス）を思い浮かべるかもしれません。

**【☁️ クラウドAIの仕組み】**
クラウドAIは、強力な計算資源が提供される「遠くの計算工場」のようなものです。私たちは、そこに「質問（データ）」をインターネット経由で送り、答えを受け取るだけです。高性能ですが、以下の懸念点があります。
*   **プライバシー:** 送ったデータが外部のサーバーに保存されるため、「これは大丈夫かな？」と不安になる場合がある。
*   **コスト:** 便利な分、利用量に応じた料金がかかる。

**【🏠 ローカルAIの仕組み】**
一方で、私たちが目指す「ローカルAI」とは、**AIを自分のPC（ローカル）の力だけで動かす**ことです。

Ollamaという仕組みを使うことで、まるで自分のPCの中に「小さなAIエンジン」を組み込むイメージです。
*   **✅ プライバシー重視:** 質問やデータが外部に漏れない。すべて自分のPC内で完結するため、企業秘密など、絶対に外に出したくない情報を扱う際に非常に安全です。
*   **✅ コストフリー:** 基本的に追加料金がかかりません。
*   **✅ オフライン対応:** インターネットが切れても、モデルさえダウンロードしておけば動作することが多いです。

ここでは、この安全で手軽な「ローカルAI」に挑戦していただきます。

## 🛠️ 準備：始める前に確認すること
いきなりAIの話で不安になりがちですが、必要なのは主に次の3点だけです。

1.  **PCのスペック:** AIを動かすには、ある程度の計算能力が必要です。最新のPCであれば概ね問題ありませんが、できればGPU（グラフィックボード）が搭載されている方が、よりスムーズに動きます。
2.  **インターネット接続:** 最初に必要なツール（Ollama）とAIの知識モデル（Llama 3など）をダウンロードするときだけ使います。
3.  **ターミナル（コマンドライン）:** これが主な作業場になります。難しく考えず、「文字を打ち込んで、結果を見る」画面だと思ってください。

## 🚀 実践：OllamaでAIを動かしてみよう（ステップバイステップ）

さあ、いよいよ実際にローカルAIを動かします！

### Step 1: Ollamaのインストール（環境の準備）
まず、AIを動かすための「実行環境」であるOllamaをインストールします。

1.  **ターミナルを開く:** （OSによって「ターミナル」「コマンドプロンプト」など名称が異なります）
2.  **コマンド実行:** 以下のコマンドをコピーして貼り付け、Enterキーを押してください。

    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

**【解説】**
このコマンドは、Ollamaという「ローカルAIを動かすための仕組み」を一発であなたのPCにインストールしてくれます。何が起きているか心配なかもしれませんが、単に「準備」をしているだけなので大丈夫です。

### Step 2: AIモデルをダウンロードする（脳のダウンロード）
AIを動かすには、AIの「知識の塊」が必要です。これを「モデル」と呼びます。

最も人気があり、高性能なモデルの一つである`llama3`をダウンロードしてみましょう。

1.  **コマンド実行:** 再びターミナルに以下のコマンドを入力し、実行します。

    ```bash
    ollama run llama3
    ```

**【解説】**
このコマンドを実行すると、まずモデルのダウンロードが始まります。これが「脳」をダウンロードしているイメージです。ダウンロードが完了すると、自動的に対話モードに切り替わり、ローカルAIとの会話が開始されます！

> 💡 **モデルの選び方:** Ollamaにはたくさんのモデルがあります。用途によって選ぶのがおすすめです。
> *   **Llama 3:** バランスが取れており、万能型。まずはこれでOK。
> *   **Mistral:** クリエイティブな文章生成が得意な傾向があります。
> *   **日本語特化モデル:** 扱うテーマによっては、より日本語に特化したモデルを検索して試すと良いでしょう。

### Step 3: AIと対話してみる（初めての対話体験）
モデルが動くようになったら、いよいよ会話を楽しみます。

対話モードに入ったら、あなたが質問するだけです。

**【対話の流れの例】**
あなたがプロンプトを入力し、AIがその場で考えて回答をくれます。

`>>> こんにちは！今日はローカルAIを動かせて嬉しいです。`
`llama3: おめでとうございます！ローカルAIを動かせるのはすごいことです。何かお手伝いできることはありますか？`

**【実践的な質問例】**
「明日のおすすめの出かける場所を3つ提案してほしい。アクセスが良く、費用がかからない場所が良い。」のように、具体的な制約条件（今日、明日、3つ、費用がかからない）を盛り込むと、より質の高い回答が返ってきます。

## 🚀 まとめと次のステップ（応用編）
おめでとうございます！あなたは、ローカル環境でAIを動かす第一歩をクリアしました。

1.  **復習:** ローカルAIはプライバシー保護、コスト削減の面で優れており、日常的な情報収集や個人データの処理に役立ちます。
2.  **次のステップ:**
    *   **API連携:** 今回はCLI（ターミナル）から対話しましたが、プログラミング（Pythonなど）からAIを呼び出す「API連携」を学ぶと、本格的な開発に繋がります。
    *   **モデルのカスタマイズ:** 特定の用途（例：コード生成特化、小説執筆特化）に合わせたモデルを探して試してみるのも楽しいです。
---

この記事が、ローカルAIの世界への最初の一歩となることを願っています！
```

中身の検証はしてませんが、要点は押さえているのではないでしょうか。

#### cpuとメモリ使用率

プロンプトを処理しているときのアクティビティモニタのキャプチャです。

* cpu  
  ![cpu使用率](https://static.zenn.studio/user-upload/deployed-images/fc6e90c3e05b9fb043eecb2c.png?sha=bdca0acf5026285714ab18978b4d3a564ebb05a0)
* メモリ  
  ![メモリプレッシャー](https://static.zenn.studio/user-upload/deployed-images/21686b66dfd2fb4099d6b9f5.png?sha=8049e272aa82ddd42255b2489917d0744f407356)

![プロセスのメモリ使用量](https://static.zenn.studio/user-upload/deployed-images/520976128ed6136d45e92861.png?sha=f80a0e6beed10d41ef6dbb0fac21111f34d0f85c)

cpuは全く問題なかったんですがメモリが約10GB使用されていました。  
ブラウザやらメーラーやら普段仕事で使うであろうアプリも立ち上げているとスワップも含めおよそ23GBもメモリを消費することになりました。

claude codeに最初のプロンプトを投げた時とかにはマウスカーソルが動かなくなるくらいには負荷がかかります。  
その後はコンテキストが少ないうちは処理中に固まることはないものの、コンテキストが増えていくうちにマウスカーソルすら動かせない時は何度かありました。

## まとめ

* ollamaでモデルをダウンロードするだけで簡単にローカル環境でLLMを動かせる。
* ollama経由でclaude codeも動かせる。
  + ただし、計画から実行に移れなかったり書き込み失敗をそのままにするなど、予期せぬところでエージェント処理が終了することも多い。
* mac mini m4 であればgemma4:e4bは重いが動作する。

## 感想

初めてローカル環境でAIを動かしたわけですが、あっという間に動かせるのはありがたかったです。  
先人たちが色々と環境を整えてくれたおかげですね。  
当然使うモデルに左右はされますが10万円以下のマシンで動かせてしまうわけですし、小型モデルが出た時には色々試してみて自分の環境に合うものを探したいですね。

claude codeをタダで使い倒すという当初の目的から考えると、このレスポンスの内容・速さでコーディングしていくのは厳しいなというのが率直な意見。  
今回はCLAUDE.mdは用意してませんしアプリケーションのコードを解析させたわけでもないので、実務だとさらに重くなることは避けられないでしょう。  
もう少し軽くて優秀なモデルが出たらその時に再挑戦しようかと思います。

「こういう設定にしたらうまくいったよ」みたいな話があればぜひコメントください 🙏
