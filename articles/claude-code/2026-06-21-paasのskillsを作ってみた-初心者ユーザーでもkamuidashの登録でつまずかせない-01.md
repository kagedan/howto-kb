---
id: "2026-06-21-paasのskillsを作ってみた-初心者ユーザーでもkamuidashの登録でつまずかせない-01"
title: "PaaSのSkillsを作ってみた ~ 初心者ユーザーでもKamuiDashの登録でつまずかせない"
url: "https://zenn.dev/kamuidash/articles/bd5468ff2e4d2f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

## はじめに

私たちは [KamuiDash](https://kamui-platform.com/ja/) という日本発のPaaSを運営しています。「GitHubにコードをpushするだけで本番稼働、無料プランでもコールドスタートなし」のPaaSです。

我々はエンジニアのユーザーだけではなく、バイブコーディングを始めたいというユーザーにも使って欲しいなと思いました。\*\*「最初の登録までが、人によってはけっこう難しい」\*\*という問題を解決したいと思いました。

PaaSの本質的な価値は「デプロイの面倒を肩代わりすること」にあります。それなのに、その手前のGitHubアカウント作成・MCPの設定・最初のデプロイあたりで詰まってしまうと、価値を体験する前に離脱してしまう。エンジニア経験が浅い方ほどここで止まってしまうと思うのです。

そこで私たちは、ドキュメントを厚くするのではなく、**AIエージェントに「KamuiDashの正しい操作方法」そのものを教え込む**というアプローチを取りました。それが今回作った [kamui-skills](https://github.com/kamui-project/kamui-skills) です。

この記事では、なぜPaaSがSkillsを用意したのか、何ができるのか、どう設計したのか、そしてユーザーがどう使うのかを紹介します。

## Agent Skills とは何か

まず前提の整理です。Agent Skills は、Claude Code・Codex・Cursor といったAIコーディングツールに対して「特定領域の手順や知識」を渡すための仕組みです。実体は `SKILL.md` という1枚のMarkdownファイルで、YAMLフロントマター（`name` と `description`）と本文の手順で構成されます。

```
kamui-skills/
├── .claude-plugin/
│   └── marketplace.json     ← /plugin の入り口になるカタログ
├── skills/
│   ├── kamui-github-setup/SKILL.md
│   ├── kamui-mcp-setup/SKILL.md
│   ├── kamui-deploy-workflows/SKILL.md
│   └── kamui-troubleshooting/SKILL.md
├── install.sh               ← macOS / Linux 用インストーラ（Codex・Cursor）
├── install.ps1              ← Windows PowerShell 用インストーラ
└── README.md
```

ポイントは、`SKILL.md` がツールをまたいだ共通フォーマットだということです。1セットの定義を書けば、**Claude Code・Codex・Cursor の3つで同じように動く**。それぞれインストール方法が違うだけで、中身は同じものを使い回せます。

MCP（Model Context Protocol）と組み合わせると効果が一段上がります。MCPがKamuiのAPIを「AIが叩ける道具」として公開し、Skillsが「その道具をいつ・どの順番で・どう安全に使うか」という運用知を与える、という役割分担です。AIにとって、MCPは手で、Skillsは作法、と言い換えてもいいかもしれません。

## なぜPaaSがSkillsを用意したのか

ドキュメントには構造的な弱点があります。

ひとつは、**読む側がどこで詰まっているか分からない**こと。GitHubのアカウントすら持っていない人と、git pushまでは慣れている人とでは、必要な説明がまったく違います。一本道のドキュメントはどちらにも最適化できません。

もうひとつは、**手順が状況で分岐する**こと。「ghコマンドが入っているか」「PATをどう安全に扱うか」「デプロイがどこで失敗したか」——こうした判断はユーザーの環境を見ないと決められません。静的なドキュメントは「見て判断する」ができないのです。

AIエージェントはここが得意です。画面やログの状態を聞き取り、足りないものを補い、次の一手を提示できる。ならば、**そのAIに正しい作法を教えておけば、ドキュメントの限界を超えられる**——これがSkillsを作った動機です。

実際、私たちは初心者向けの導線として [専用の案内ページ](https://kamui-platform.com/ja/beginners) も用意しました。そこには「KamuiDashの登録にAIツールは必須ではありません」と明記しています。Skillsはあくまで、**迷ったときに隣にいてくれる伴走者**という位置づけです。

## kamui-skills でできること

今回公開したのは4つのSkillです。それぞれが、ユーザーがつまずきやすいフェーズに対応しています。

### 1. `kamui-github-setup` ― GitHubの準備を肩代わり

KamuiDashはGitHub連携が前提なので、まずGitHubのアカウントとリポジトリが要ります。このSkillは `gh` CLI を使って、ghが入っているかの確認・インストール・認証・デプロイ用リポジトリの作成や接続までを案内します。

設計上の工夫として、**安全な手順は能動的に進め、破壊的な操作は必ず確認を取る**という線引きを入れています。「リポジトリを作る」は進めても、「何かを消す」前には立ち止まる、という具合です。

### 2. `kamui-mcp-setup` ― MCPの接続をミスなく

AIアシスタントからKamuiを操作できるようにするための設定パートです。PAT（Personal Access Token）の安全な扱い、クライアントへの登録、接続テスト、認証まわりのトラブルシュートをカバーします。

ここはセキュリティが絡むので特に神経を使いました。**トークンを平文でchatに貼らせない**、漏れやすい操作を促さない、といったガードを作法として組み込んでいます。

### 3. `kamui-deploy-workflows` ― デプロイの一連の流れ

MCP経由で、プロジェクトの作成、GitHub連携のdynamic/staticアプリのデプロイ、アプリ設定、起動コマンドや環境変数の設定までを面倒見ます。「git pushするだけ」の手前にある初期設定を、対話しながら埋めていくイメージです。ここでも安全確認のステップを挟んでいます。

### 4. `kamui-troubleshooting` ― 失敗したときの原因究明

デプロイや実行時の問題を、MCPの読み取り系ツールで診断します。アプリの状態、デプロイ実行の履歴、ビルドログ、ランタイムログを順に確認し、原因と次の一手を示します。

このSkillは「**まず読み取り、証拠を示してから説明する**」という運用モデルで書いています。報告の型まで決めていて、

```
Current state: ...
Evidence: ...
Likely cause: ...
Next action: ...
```

という形で、現状・根拠・推定原因・次のアクションを簡潔に返すようにしています。よくある詰まりどころ——ビルドコマンドの失敗、起動コマンドの欠落、ポートのハードコード、環境変数の未設定、GitHubリポジトリへのアクセス権——にも、それぞれ定石の対応を持たせました。

そして重要なのが**境界線**です。MCPでの診断は読み取り専用に徹し、削除・更新・再デプロイ・認証情報のローテーション・課金変更などは、勝手にAPIを叩かせません。必要ならダッシュボードか正規の `kamui` CLI に誘導する、という安全側の設計にしています。

## 設計で意識したこと

4つのSkillを書くなかで、意識したポイントが3つあります。

**1つめは、初心者を置き去りにしないこと。** READMEにも「エンジニアでなくても大丈夫」という前提を明記しました。後述するClaude Codeのインストール方法は、ターミナルもgitも不要で、WindowsでもMacでも同じ2行で済みます。AIに渡す指示文も、専用ページから「コピーして貼るだけ」で動くよう、こちらで完成形を用意しています。

**2つめは、安全第一であること。** AIに操作を任せる以上、暴走は許されません。「破壊的操作は確認」「読み取りと書き込みを分ける」「秘密情報を貼らせない」「権限のない操作はやらせず正規ルートへ誘導」——これらをSkillの本文に作法として埋め込みました。AIの自由度を上げつつ、危ない方向には進ませない設計です。

**3つめは、特定ツールに縛られないこと。** `SKILL.md` という共通規格に乗ることで、Claude Code・Codex・Cursorのどれを使っているユーザーでも同じ体験を届けられます。ユーザーに「うちのサービスのためにこのツールを使え」と強制したくなかった、というのが本音です。

## ユーザーはどう使うのか

ここからは実際の使い方です。[初心者向けページ](https://kamui-platform.com/ja/beginners) の「迷ったときの3ステップ」に沿って説明します。

### STEP 1: 相談に使うAIツールを用意する

Claude Desktop（Claude Code）、Codex、Cursorのいずれかを開いて、ログインできる状態にしておきます。

### STEP 2: AIにKamuiDashの操作方法を教える（＝Skillsを入れる）

一番簡単なのはClaude Codeです。**ターミナルもgitも要りません**。チャット欄に次の2行を順に入力するだけです。

```
/plugin marketplace add kamui-project/kamui-skills
/plugin install kamui@kamui-skills
```

そのあと `/reload-plugins` を実行する（またはClaude Codeを再起動する）と読み込まれます。これはAnthropic公式の [`anthropics/skills`](https://github.com/anthropics/skills) マーケットプレイスと同じ仕組みで、インストール・キャッシュ・名前空間・自動更新まで面倒を見てくれます。

Codex・Cursorの場合はワンライナーのインストーラを使います。ターミナルに1行貼るだけです。

```
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/kamui-project/kamui-skills/main/install.sh | bash
```

```
# Windows（PowerShell）
irm https://raw.githubusercontent.com/kamui-project/kamui-skills/main/install.ps1 | iex
```

デフォルトでは3ツールすべて（`~/.claude/skills` と `~/.agents/skills`）に入ります。

| ツール | Skillsの読み込み元 |
| --- | --- |
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/`、`.agents/skills/`、`/etc/codex/skills` |
| Cursor | `.cursor/skills/`、`~/.agents/skills/`、`~/.claude/skills/`（互換） |

インストール後は、Skillsを読み込ませるためにツールを一度完全に終了して開き直します。

### STEP 3: 「登録を手伝って」と頼む

あとは普通の言葉で頼むだけです。専用ページにはコピペ用の文面も置いてあります。

> KamuiDashにアカウント登録をしたいです。GitHubアカウント作成からKamuiDashの登録まで一緒に進めてください。

これでAIがSkillsの作法に従い、GitHubの準備からKamuiDashの登録、最初のデプロイまで、画面の状況を聞きながら伴走してくれます。途中で詰まっても、状況を伝えれば原因を切り分けて次の一手を出してくれる——というのが狙った体験です。

## おわりに

ドキュメントは「読む人」を選びます。でもAIエージェントは、相手のレベルに合わせて説明を変え、環境を見て判断し、失敗したら原因を一緒に探してくれます。

私たちが kamui-skills でやりたかったのは、**「PaaSの使い方」という運用知をAIに移植して、ユーザー一人ひとりに専属の伴走者をつける**ことです。ドキュメントを増やす代わりに、ドキュメントを読んで動いてくれる存在にKamuiDashを正しく教える、という発想の転換でした。

リポジトリはこちらで公開しています。

<https://github.com/kamui-project/kamui-skills>

初心者向けの導線はこちらです。

<https://kamui-platform.com/ja/beginners>

PaaSに限らず、「自社サービスの操作方法をAIに教える」というのは、これからのオンボーディング設計のひとつの形になりそうだと感じています。同じようなことを考えている方の参考になれば嬉しいです。
