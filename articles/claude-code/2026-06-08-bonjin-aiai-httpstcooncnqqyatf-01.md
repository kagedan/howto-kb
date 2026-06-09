---
id: "2026-06-08-bonjin-aiai-httpstcooncnqqyatf-01"
title: "@bonjin_aiai: https://t.co/onCnqQyAtF"
url: "https://x.com/bonjin_aiai/status/2064110084050034763"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "cowork", "x"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-x"
query: "Cowork スケジュール OR Cowork スキル作成 OR Cowork 自動化"
---

https://t.co/onCnqQyAtF


--- Article ---
# 「Projects」って、結局どれも同じでしょ？——と思っていた

Claudeには「Projects」と呼ばれる機能があります。

ChatにもCoworkにもある。Claude Codeにも似た仕組みがある。名前が同じなので、最初は「全部同じものが別の場所にあるだけ」だと思っていました。

でも調べてみたら、全然違いました。

この記事では、3つのProjectsの違いを、非エンジニアの視点から整理していきます。まだ使ったことない人はProjectsを使ってみたくなり、Chatでしか使ったことない人はCoworkも使ってみようかなとなると思います。

## 前提：そもそも「Projects」とは何か

![](https://pbs.twimg.com/media/HKUtwyzaUAAzy3n.jpg)

3つの違いに入る前に、共通している概念を押さえておきます。

Projectsの本質は、**「Claudeに毎回ゼロから説明し直さなくていい仕組み」**です。

たとえば、あるクライアントのSNS投稿を考えるたびに「あなたはSNSマーケの専門家です。クライアント情報は〇〇で、ブランドトーンは信頼感と親しみやすさの両立で……」と毎回書くのは面倒ですよね。

これを一度だけ設定しておけば、そのプロジェクト内ではいつでも自動的に適用される。この「事前にセットしておく指示」を**カスタムインストラクション**と呼びます。

Claude Codeの場合は**「CLAUDE.md」**というテキストファイルが同じ役割を果たします。名前は違いますが、やっていることは同じです。

![](https://pbs.twimg.com/media/HKUuPaabgAAQN4i.jpg)

では、それぞれ何ができて、何ができないのか。順番に見ていきます。

## 1.Chat Projectsでできること

![](https://pbs.twimg.com/media/HKUuVJUawAAX0_W.jpg)

Chat Projectsは、デスクトップアプリとclaude.ai（ブラウザ）で使えます。しかもスマホアプリでも使えちゃうのがかなり便利です。

**⚪︎基本機能**

- カスタムインストラクションを設定し、プロジェクト内の全チャットに適用できる
- 参考資料（PDF、画像、CSVなど）をアップロードして、常に参照させられる
- Team / Enterpriseプランではチームメンバーと共有できる
- PC・スマホ・タブレットのどこからでもアクセスできる

**⚪︎記憶の仕組み**

ここが重要なポイントです。

Chat Projectsでは、**同じチャット内の会話は覚えています**。「カルーセルの提案書を作って」→「もっとCTA強めにして」という連続したやり取りは、1つのチャット内であれば問題なく機能します。

しかし、**新しいチャットを立てると前の会話は忘れます**。

カスタムインストラクションとアップロードしたファイルは引き継がれますが、「先週どんな提案書を作ったか」「過去にどんなフィードバックがあったか」といった会話の中身は引き継がれません。

**⚪︎向いている用途**

- アイデアの壁打ち・ブレインストーミング
- 参考資料を前提にした質問・相談
- チームで同じブランドガイドラインを共有した上での作業
- 移動中にスマホからサッと相談したいとき

## 2.Cowork Projectsでできること

![](https://pbs.twimg.com/media/HKUuqemawAACTcT.jpg)

Cowork Projectsは、Claude Desktop（Mac / Windows）のCoworkタブから使えるProjectsです。2026年3月末に追加されました。

⚪︎基本機能

Chat Projectsの機能に加えて、以下ができます。

- PCのローカルフォルダに直接アクセスし、ファイルの読み書きができる
- MCP（外部ツール接続）やプラグインを利用できる
- スケジュール実行で定期タスクを自動化できる
- **スコープ付きメモリ**により、セッションをまたいで文脈が蓄積される

⚪︎「スコープ付きメモリ」とは

これがCowork Projectsの最大の特徴です。

「スコープ付きメモリ」という言葉だけ聞くと難しそうですが、分解するとシンプルです。

- **メモリ** ＝ Claudeが過去のやり取りを覚えていること
- **スコープ付き** ＝ その記憶がプロジェクトの中だけ
