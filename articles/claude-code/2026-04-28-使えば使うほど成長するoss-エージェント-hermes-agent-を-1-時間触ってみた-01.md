---
id: "2026-04-28-使えば使うほど成長するoss-エージェント-hermes-agent-を-1-時間触ってみた-01"
title: "「使えば使うほど成長する」OSS エージェント Hermes Agent を 1 時間触ってみた"
url: "https://zenn.dev/flinters_blog/articles/e3bf5fafce3ed7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "LLM"]
date_published: "2026-04-28"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

## はじめに

こんにちは。FLINTERS の河内です。

「The only agent with a built-in learning loop」——そんな強めのコピーを掲げる OSS エージェントが、OpenRouter のアプリランキングで OpenClaw に並ぶ勢いで上位に出てきていました。Nous Research が公開している Hermes Agent です。SOUL.md / メモリ / スキル / SQLite による永続化を組み合わせ、ポケモンプレイヤーから Minecraft MOD パックサーバーまで 100 を超えるプリセットスキルを抱えた、いかにも盛っている代物です。

これは触ってみたい、ということで 2026-04-27 の AIソムリエでは、朝に「何かネタないですか」と振ったら拾ってくれた川上さんがこのプロダクトを取り上げてくれました。お互い予習なしで、参加者みんなで一緒に触りながら見ていく回になりました。

結論から言うと、30 分から 1 時間のデモでは「普通のエージェントと変わらない」という感想に着地しました。「使えば使うほど振る舞いが蓄積される」という売りは、短時間で体感できる類のものではない、という当たり前のことを確認した格好です。それでも、`skill_manage` というメタツールでスキルを自動生成する仕組みや、SQLite + 外部メモリプロバイダーという memory アーキテクチャがこの界隈の標準パターンになりつつあることが見えたのは収穫でした。差が分かりづらかった観察記として、そのまま残します。

本記事は勉強会の内容を AI を活用しながらまとめています。

## Hermes Agent とは

<https://github.com/NousResearch/hermes-agent>

Hermes Agent は Nous Research が公開している OSS の自律エージェントです。「the only agent with a built-in learning loop」を掲げていて、ローカルで動くパーソナル AI のようなポジションになります。

主な構成要素は以下です。

* **SOUL.md**: パーソナリティ・ユーザーモデルを書き込む設定ファイル
* **メモリシステム**: エージェント自身が書き換えるメモリ。SQLite に全会話履歴を保存して FTS5 でセッション横断検索できる
* **スキルシステム**: 手続き的な知識を保存。Hermes が自分で作ったり、外部の `agentskills.io` 標準のスキルをインポートして使ったりできる
* **ツールシステム**: ファイル操作・シェル・ブラウザなど
* **マルチプラットフォーム接続**: Telegram / Discord / Slack / WhatsApp / Signal などの統一ゲートウェイ
* **ターミナルバックエンド**: ローカル / Docker / SSH / Daytona / Singularity / Modal

対応 OS は macOS / Linux / WSL2 / Android（Termux 経由）です。LLM プロバイダーは OpenRouter・NVIDIA NIM・OpenAI など 200 以上のモデルから選べます。

立ち位置としてはよく似たプロダクトに **OpenClaw** があります。後述する Genspark Claw のベースにもなっているフレームワークで、OpenClaw は外部のスキルをインポートして使う側に振り、Hermes Agent は自分でスキルを獲得していく側に振っている、というのが我々の理解です。

<https://openclaw.ai>

## インストールしてみる

ワンライナーのスクリプトを叩くと、uv や ffmpeg などの依存関係も含めて全部入れてくれます。AI エージェント文脈であまり見ない並びだったので「動画でも生成するの？」とざわつきました。ドキュメントを見ると、ffmpeg は YouTube などの動画を分析するときに使うようです。

インストール後、`hermes` コマンドを叩くとセットアップウィザードが起動します。

LLM プロバイダーの選択画面で AWS Bedrock の認証情報がローカルにある場合は自動検出してくれて、そのまま選択できる状態になっていました。GitHub Copilot トークン経由で利用する選択肢もあります。今回は Copilot トークン経由で Sonnet 4.6 を選びました。

ターミナル上の TUI でセッションが始まると、起動時の出力が結構派手で「おお」と声が出るくらいの見た目になります。パーソナリティ自体はデフォルトでも素直に動いてくれて、気になればすぐに `~/.hermes/SOUL.md` を編集してカスタマイズできます。

## メモリとスキルを試してみる

### スキル一覧で見えるディレクトリの広さ

セットアップ直後にスキル一覧を眺めると、すでにいろいろなスキルがプリセットされていました。インストール時に `~/.hermes/skills/` 以下へ 100 以上のスキルがコピーされる作りで、19 カテゴリにわたります。

代表的なところでは以下のような並びです。

* **Note-Taking**: `obsidian`（Obsidian Vault に対する読み書き・検索）
* **Code Execution & Development**: `jupyter-live-kernel` / `python-debugpy` / `node-inspect-debugger` / `test-driven-development`
* **AI Agent Integration**: `claude-code`（Claude Code CLI に委譲）/ `native-mcp`（MCP クライアント）
* **ML Ops**: `llama-cpp` / `vllm` / `axolotl` / `dspy` / `outlines` / `huggingface-hub`
* **Gaming**: `minecraft-modpack-server`（CurseForge / Modrinth サーバーホスティング）/ `pokemon-player`（ヘッドレスエミュレーター + RAM 読み取りでポケモンを遊ぶ）

「Minecraft の MOD パックサーバー、ポケモンプレイヤーが入ってるのは何…？」と画面を見ながらざわついたあたりが、Hermes Agent が想定しているユーザー像をなんとなく感じさせるラインナップでした。

[Bundled Skills Catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) でカタログ全体を眺められます。

参加者から「これは Obsidian の MCP 経由で繋いでいるわけじゃなくて、ディレクトリを直接見にいける、という意味ですよね？」という確認があり、まさにその通りでした。Obsidian スキルは `OBSIDIAN_VAULT_PATH` 環境変数（未設定なら `~/Documents/Obsidian Vault`）を直接読みにいきます。

承認モードはデフォルトで「マニュアル」、つまりツール実行のたびに人間に確認を取る挙動になっています。「auto」モードに切り替えると確認なしで動き出します。注意したいのは、デフォルトのローカルターミナルバックエンドにはサンドボックスがなく、エージェントは実行ユーザーと同じファイルシステム権限を持つ、という点です。ユーザーが触れる範囲ならどこでも読み書きできます。実運用では `docker` / `modal` / `daytona` などのバックエンドに切り替えてホストから隔離することがドキュメント上でも推奨されています。

### 名前を覚えさせる

メモリの動きを見るために、川上さんが「私はObsidianを使っていつもメモを取っているんですよ。覚えておいて」と入力しました。Hermes は了解の返事を返したあと、メモリディレクトリに新しい Markdown ファイルを書き出していました。Claude Code でいう auto memory 相当のメモリ書き込みは、当然のように動きます。

問題は、ここから先でした。

### スキル自動生成を体感したかったが

Hermes Agent の特徴のひとつに、**5 回以上のツール使用を伴う複雑なタスクを完了したあと、エージェントが自分の手順をスキルとして保存する** という挙動があります。トリッキーなエラーを直したときや、非自明なワークフローを発見したときも同様です。

これを体感したくて「天気でも調べてもらえますか」など、いくつかのプロンプトを試しました。が、30 分くらいの試行錯誤では新しいスキルが生まれる様子は観察できませんでした。「これでスキル生成が走ったら盛り上がるんだけどな」と粘ってもその場では起こらず、デモとしては「普通のエージェントとして動いている」という事実を確認するだけになってしまいました。

参加者からは「Hermes だろうが OpenClaw だろうが、本質的にはマークダウンでエージェントに指示を出す方法の違いでしかないのでは」「ほかのエージェントでも『こういうタスクはスキル化しといて』とお願いすれば同じ振る舞いができる気がする」というコメントがあり、確かにそうだなと思いつつ、Hermes の独自性を短時間で見せる難しさを実感しました。

別の参加者は「使えば使うほど馴染むのが本質のプロトコルなので、短時間で体験できるプリセットを作るのが難しい」と表現していて、これがいちばん腑に落ちる整理でした。

## アーキテクチャを DeepWiki で覗く

ここで時間が余ったので、DeepWiki で Hermes Agent の中身を読みに行きました。

<https://deepwiki.com/>

`github.com` の URL を `deepwiki.com` に書き換えるだけで、AI 生成のリポジトリドキュメントとコード Q&A 画面に飛べる Cognition 製のサービスです。今回のように初見のリポジトリでアーキテクチャを掴みたいときに便利でした。AI ソムリエ自体のネタになるくらいのポテンシャルがあります。

### `skill_manage` というメタツール

ソースを覗いて面白かったのが、スキル自動生成の仕組みが [`skill_manage`](https://github.com/NousResearch/hermes-agent/blob/main/tools/skill_manager_tool.py) というツールと、それをどのタイミングで呼び出すかを規定する [プロンプト](https://github.com/NousResearch/hermes-agent/blob/main/agent/prompt_builder.py) のセットで実装されている点です。

プロンプト側（`SKILLS_GUIDANCE`）には次のような指示が書かれていました。

> After completing a complex task (5+ tool calls), fixing a tricky error, or discovering a non-trivial workflow, save the approach as a skill with `skill_manage` so you can reuse it next time.  
> When using a skill and finding it outdated, incomplete, or wrong, patch it immediately with `skill_manage(action='patch')` — don't wait to be asked. Skills that aren't maintained become liabilities.

5 回以上のツール使用を伴う複雑なタスクを完了したあと、トリッキーなエラーを直したとき、非自明なワークフローを発見したとき。この 3 つを境にして自分の手順をスキル化しろ、という命令が入っています。さらに、使っているスキルが古かったり不完全だったり間違っていることに気づいた場合は、確認なしで `patch` で直してしまえ、という指示まで含まれていました。

`skill_manage` 自体は `create` / `edit` / `patch` / `delete` / `write_file` / `remove_file` の 6 アクションを持つだけのシンプルなツールで、バリデーションを通したあと `~/.hermes/skills/` 以下にディレクトリと SKILL.md を書き出します。コードで書かれているぶん、確実に実行される側面はあるなと感じました（Claude Code のスキルはマークダウンで書かれるので、実行確率は一段下がる）。

外部スキル向けのセキュリティスキャナー（[`skills_guard.py`](https://github.com/NousResearch/hermes-agent/blob/main/tools/skills_guard.py)）も別に用意されていて、regex ベースの静的解析でデータ持ち出し・プロンプトインジェクション・破壊的コマンド・永続化などのパターンをスキル本文から検出します。OpenAI / Anthropic の公式スキル以外（community）は、findings が出れば原則ブロックされます。一方でエージェント自身が `skill_manage` で作るスキルはデフォルトでスキャン対象外で、コメントには「同等のコマンドはどうせ `terminal()` 経由で素通りするから、スキャンしてもセキュリティ的な意味はなく摩擦が増えるだけ」と書かれていて、ここの割り切りは正直だなと感じました。

### Honcho という外部メモリプロバイダー

DeepWiki を読み進めていて目にとまったのが「Honcho」というキーワードでした。

<https://honcho.dev/>

最初は何の略か分からなかったのですが、対話を後追いで分析してユーザーモデル（嗜好やコミュニケーションスタイル）を維持する AI ネイティブのメモリバックエンドでした。Hermes はこれを含む複数の外部メモリプロバイダーをサポートしていて、エージェントとメモリシステムを分離して接続する設計になっています。

ちなみに、調べてみると OpenClaw 側も `~/.clawdbot/memory/<agentId>.sqlite`（`chunks_vec` で sqlite-vec、`chunks_fts` で FTS5）という形で SQLite ベースのメモリインデックスを持ち、Hindsight などの外部メモリプロバイダーもサポートしていました。Hermes / OpenClaw 系のパーソナル AI 文脈では、「会話履歴を SQLite に持つ + 外部メモリ層を差し込めるようにする」というのは、もはや標準パターンに近そうです。一方で Claude Code はビルトインだと JSONL のセッションログと `MEMORY.md` / `CLAUDE.md` どまりで、SQLite ベースの記憶や Honcho 的な外部メモリは [`claude-mem`](https://github.com/codenamev/claude_memory) などの MCP プラグイン経由で後付けする世界観です。設計思想の違いがそのまま出ています。

## OpenRouter ランキングという脇道

もうひとつの話題が OpenRouter のアプリランキングでした。

<https://openrouter.ai/rankings>

そもそも私が Hermes Agent を取り上げたいと思ったのも、前日に DeepSeek V4 Flash を触っていて、関連で OpenRouter のランキングを眺めていたら Hermes Agent がかなり上位に来ていた、というのが入り口でした。DeepSeek V4 Flash 自体は Hermes / OpenClaw のトップ利用モデルではなく、あくまで私の関心がオープンウェイト系を眺める方向に向いていただけです。

ランキングを眺めていて気づいたのは、Hermes Agent と OpenClaw の傾向差です。OpenClaw 経由の利用が減少している一方で Hermes Agent の利用は増えていました。OpenRouter 経由の数字なので別プロバイダー直叩きが増えているだけの可能性は十分ありますが、傾向としては面白いポイントでした。

利用されているモデルにも傾向があります。Hermes Agent のトップに並んでいたのは以下のような中国発のオープンウェイトモデルでした。

* **MiMo-V2-Pro**: Xiaomi の MoE モデル。総パラ 1T 超 / アクティブ 42B、Hybrid Attention、コンテキスト 1M。Artificial Analysis Index で世界 8 位
* **Step-3.5-Flash**: StepFun（上海・阶跃星辰）製の MoE モデル。総 196B / アクティブ 11B、コンテキスト 256K、100〜300 tok/s

`MiMo-V2-Pro` を「Xiaomi のやつですよね」と確認しながら、結構安価なオープンウェイトを API で叩く文化が前提になっているんだな、と眺めていました。

ついでに少し脱線して、Genspark が「Genspark Claw」という OpenClaw ベースのマネージドサービスを始めて UI もきれいになっている、という話題も出ました（2026-03-12 ローンチ）。VM・スキル・メッセージングアプリ連携が一通り入った状態で月額数十ドル + 従量という値段感で、「ちょっとお高めかも」というのが共有された印象でした。

<https://www.genspark.ai/genspark-claw>

## 業務文脈との距離

参加者の議論で、いちばん腑に落ちた整理がありました。

> 本当にこう権限を渡せる人向けですよね。Google アカウントも Discord も全部、自分のコンテキスト情報をコネクトできるという風に割り切ってしまう人にはめちゃくちゃ使いやすいと思う。

Hermes Agent や OpenClaw は、Mac mini に常駐させておいて Discord や LINE 経由でモバイルから話しかけ、Gmail や Google カレンダーを通して予定調整・メールの返信下書き・問い合わせ対応を勝手にやってもらう、というパーソナルアシスタント像で設計されています。事実上の同僚として使う、という表現がありました。

我々が業務でエージェントを使うときは、接続先を絞って制御したい欲求が強くなります。「全部繋いで全部見てもらう」とは真逆で、この設計思想の差が短時間デモでの違和感の正体だったかもしれません。プライベートでバーっと繋いで遊ぶには良さそうですが、業務向けに導入するなら別の切り口が要りそうです。

## まとめ

Hermes Agent については「短時間では違いが分からなかった」というのが今回の素直な結論です。スキル自動生成も SQLite ベースの全会話履歴も、長期間使い込むことを前提に設計されていて、30 分のデモで体感できる類のものではないと割り切るしかないと感じました。

それでも触ってみて良かった点は、

* Claude Code との設計差として「手続き的記憶を `skill_manage` というメタツールで自動構築する」という方向性があると分かったこと（これは OpenClaw とも一線を画す Hermes 寄りの特徴）
* Hermes / OpenClaw 系のパーソナル AI が、SQLite + 外部メモリプロバイダー差し込みという memory アーキテクチャをほぼ標準パターンとして共有していること
* OpenRouter ランキングを通して、中国発のオープンウェイトモデルが OSS エージェントの実利用基盤として伸びていることを確認できたこと
* DeepWiki という、初見リポジトリの構造を素早く掴むツールに改めて気づけたこと

あたりです。Hermes 独自と言える「手続き記憶の自己生成」がどこまで効くかは長期使用で検証してみたい部分で、誰かが資産（Obsidian のメモ群など）と組み合わせて数週間使ってみるくらいの粒度でないと、本当の手応えは見えてこない気がしています。
