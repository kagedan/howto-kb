---
id: "2026-04-08-claude-codeサブエージェント使ってみた-qiita-01"
title: "【Claude Code】サブエージェント使ってみた - Qiita"
url: "https://qiita.com/pro-tein/items/faac5d1b79093cda33b1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

# はじめに

今回はClaude Codeの便利機能の一つ、**サブエージェント**を実際に作成して使ってみました。  
前提知識として、サブエージェント機能を簡単にまとめた記事もありますので、ぜひご参照ください。

# まずは作ってみた

今回は、例としてわかりやすく、かつ実用的な「コードレビュー」専門のサブエージェントを作成して見たいと思います。

Claude Codeを起動し、`/agents`コマンドを実行します。  
すると、作成済みのサブエージェント一覧が表示されます。（私はまだありません）  
（Built-inに表示されているサブエージェントは内部で使われるもので、操作できません）  
**Create new agent**を実行します。

[![SCR-20260331-uqfg.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fe6eff7f0-9adc-426b-bbdd-30231398414e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bd2a6acc515ec4d757acf5cb2ef7bd5f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fe6eff7f0-9adc-426b-bbdd-30231398414e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bd2a6acc515ec4d757acf5cb2ef7bd5f)

サブエージェントを作成する場所（グローバルかプロジェクト内か）を選択します。  
今回はプロジェクト内を選択します。

[![SCR-20260401-bcba.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F4ab8d694-eab0-4259-aa53-8fdb4ffee021.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=864da520293f6f2de74cc3bfa05638a7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F4ab8d694-eab0-4259-aa53-8fdb4ffee021.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=864da520293f6f2de74cc3bfa05638a7)

サブエージェントの役割内容を、

1. Claude(AI)と自然言語で会話しながら作成する（おすすめ）
2. 手動でファイルに設定を書いていく  
   かを選択できます。

今回は1を選択します。

[![SCR-20260401-bcva.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fd25ac6cd-79be-40df-8eae-2fb8e78c7a71.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f844aea0c58c83498140db282eab4a25)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fd25ac6cd-79be-40df-8eae-2fb8e78c7a71.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f844aea0c58c83498140db282eab4a25)

サブエージェントにどんな役割を依頼するかをプロンプトに入力します。  
今回は公式ドキュメントから引用した、コードレビュアー用サブエージェントの設定をそのまま使います。

> Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.

[![SCR-20260401-bege.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F6546c499-2adf-43b3-a1e9-042191ae7d43.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0b7e426071f4ac6103b7e0d3fe0585f3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F6546c499-2adf-43b3-a1e9-042191ae7d43.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0b7e426071f4ac6103b7e0d3fe0585f3)

しばらく待つと、ツール選択が表示されます。  
ここでは、作成したサブエージェントの使用できるツールや権限を制限することができます。(必要最低限の権限を与えるのがおすすめです)  
今回は公式ドキュメントのコードレビュアーを真似て、[Read, Grep, Glob, Bash] のみを選択します。  
一番上の **[ Continue ]** を実行します。

[![SCR-20260401-bhkv.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F13fee9f8-0aff-4ae0-be65-b2992009ec86.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9a51d68c920f9cd935b00d48dbe4413b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F13fee9f8-0aff-4ae0-be65-b2992009ec86.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9a51d68c920f9cd935b00d48dbe4413b)

このサブエージェントが使用するLLMモデルを選択します。  
用途に合わせて選択しましょう。  
例）  
・ブラウザでの調べ物を依頼する　→Haiku  
・実装するうえでのアーキテクチャやデータベース構成を考えてもらう　→Opus

今回は公式ドキュメントのコードレビュアーを真似て、inherit（現在のセッションで使われているモデル）を選択します。

[![SCR-20260401-bipd.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F1314a5b6-12c1-4625-87ca-31d434f0c263.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=32bfb5082ae2fb6c17902dd53f466b50)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F1314a5b6-12c1-4625-87ca-31d434f0c263.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=32bfb5082ae2fb6c17902dd53f466b50)

作成したサブエージェントにタグカラーを設定することができます。  
セッション内で、サブエージェントが起動したさいにUIで識別しやすくなります。  
今回はRedを選択しました。  
サブエージェント名は`code-review-specialist`になったらしいです（あとから設定ファイルを手動編集で変更可能です）

[![SCR-20260401-bkin.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fa7285781-0e4e-4bc5-8b92-9546fa608657.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=aa2f5e23819444153e3ebb71d853ebe4)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Fa7285781-0e4e-4bc5-8b92-9546fa608657.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=aa2f5e23819444153e3ebb71d853ebe4)

メモリ（記憶）の配置場所を設定します。

> User scope を選択して、サブエージェントに ~/.claude/agent-memory/ の永続メモリディレクトリを提供します。サブエージェントはこれを使用して、コードベースパターンや繰り返される問題など、会話全体で洞察を蓄積します。サブエージェントが学習を永続化しないようにする場合は、None を選択します。

今回はプロジェクト単位のコードレビュー用サブエージェントなので、プロジェクトスコープを選択します。

[![SCR-20260401-bmlq.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F64019bd8-bf45-46ce-9a6e-c5a5d4d17e03.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ea1b36db88c37a5eb93d90f3611be35a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F64019bd8-bf45-46ce-9a6e-c5a5d4d17e03.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ea1b36db88c37a5eb93d90f3611be35a)

最後に、概要が表示されるので、問題なければそのまま`Enter`を押せば作成完了です。

[![SCR-20260401-bnkr.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F897570d7-7ec3-4e6b-9087-f476a0b7b7c9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9fe4db0733eed1089b77e542c3bb600c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F897570d7-7ec3-4e6b-9087-f476a0b7b7c9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9fe4db0733eed1089b77e542c3bb600c)

指定したスコープの配置場所に、`/.claude/agents/~.md`が作成されていると思います。

# さっそく使ってみた

すでに実装済みの簡易的なtodoアプリを用意し、新機能の追加実装を依頼しました。

[![SCR-20260401-brjf.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F0e2310bf-35b2-426e-a822-18d05bcbf75c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e378484c9ac640c895d17918aac734f9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F0e2310bf-35b2-426e-a822-18d05bcbf75c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e378484c9ac640c895d17918aac734f9)

すると、実装が完了したタイミングでコードレビュー用サブエージェントが起動し、自動コードレビューを開始しました。

[![SCR-20260401-brrv.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F7dab8cf0-c20f-484d-836a-8c5a4244a223.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=951b134fc73ee1fa3919fa1c2cd5dc05)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F7dab8cf0-c20f-484d-836a-8c5a4244a223.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=951b134fc73ee1fa3919fa1c2cd5dc05)

[![SCR-20260401-bsvk.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Ffb207596-00b0-45af-8574-6ce94f2085d7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5ce7974c16f93dc2c45e3974a2d20370)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2Ffb207596-00b0-45af-8574-6ce94f2085d7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5ce7974c16f93dc2c45e3974a2d20370)

### しっかりレビューしてくれました！
