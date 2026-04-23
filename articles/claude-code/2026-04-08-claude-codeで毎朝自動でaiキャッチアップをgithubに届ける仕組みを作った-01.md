---
id: "2026-04-08-claude-codeで毎朝自動でaiキャッチアップをgithubに届ける仕組みを作った-01"
title: "Claude Codeで毎朝自動でAIキャッチアップをGitHubに届ける仕組みを作った"
url: "https://zenn.dev/nijima/articles/85347de8a5a8f3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

# Claude Codeで毎朝7時に自動でAIキャッチアップをGitHubに届ける仕組みを作った

## はじめに

AI界隈の情報は流れが速い。Zenn・Qiita・X・HackerNews・Redditを毎日チェックするのは  
現実的に難しく、気づいたら数日分の情報が溜まっていた、という経験がある人も多いはず。

そこで **Claude Code のスケジュール実行機能（リモートエージェント）** を使って、  
平日の毎朝7時に自動でAI情報をまとめてGitHubにコミットする仕組みを作った。

この記事はその構築記録と、ハマったポイントを共有するものです。

---

## 作ったもの

* **実行タイミング**：平日（月〜金）朝7時 自動実行
* **収集ソース**：Zenn・X・HackerNews・Reddit
* **収集スタイル**：公式ニュースではなく「やってみた」系の実践記事を優先
* **出力形式**：Markdown（`2026-04-08.md` など日付ファイル）
* **保存先**：GitHubリポジトリ（`main`ブランチに直接コミット）

### 出力イメージ

AI Daily Catch-up 2026-04-08

▎ 2026年4月8日（水曜日）

Zenn — 実践事例 5選

1. Claude Codeで「AI部下10人」を作ったら、勝手にバグ直して「違反は切腹」ルールを追加してきた話

何をやったか： Claude Codeで10体のAIエージェントを封建的な武家制度に  
なぞらえて構築したところ、バグを自律的に発見・修正するだけでなく、独自の  
「違反は切腹」ルールを自発的に追加してきたという実験レポート。...  
URL： <https://zenn.dev/>...

HackerNews — 注目記事 4選（英語→日本語訳）

...

---

## 技術構成

### Claude Code スケジュール実行（リモートエージェント）

Claude Code には **リモートエージェントをcronスケジュールで動かす機能** がある。  
Anthropicのクラウド上で隔離された環境（CCR）が起動し、指定したプロンプトを  
自律的に実行してくれる。

/schedule

コマンドから設定できる。

### エージェントへの指示（プロンプト設計）

最初は「公式ニュースを集めて」という指示だったが、結果が味気なかった。  
改善のポイントは2つ：

**1. ソースを「やってみた」系に絞る**  
公式アナウンス・ニュース記事は除外。  
個人・チームの実践・活用事例を優先

**2. タイトルではなく「何をやったか」を要約させる**  
タイトルをそのまま書かない。  
「何をやったか」を自分の言葉で簡潔に説明

この2つの変更だけで、読み応えが大きく変わった。

### 収集ソースと件数配分

| ソース | 件数 | 選定基準 |
| --- | --- | --- |
| Zenn | 5件 | ライク数・ブックマーク数順 |
| X | 2件 | インプレッション数順（宣伝系除外） |
| HackerNews | 4件 | ポイント数順 |
| Reddit | 3件 | upvote数順 |
| **合計** | **14件** |  |

英語記事（HackerNews・Reddit）は日本語に翻訳・要約させている。

### GitHubへの書き込み

リモートエージェントはクラウド上で動くため、ローカルの `~/ai-catchup/` には  
書き込めない。そこでGitHub Personal Access Tokenを使い、直接リポジトリに  
コミット・プッシュする構成にした。

```
mkdir -p /tmp/ai-catchup && cd /tmp/ai-catchup 
git init 
git remote add origin https://@github.com/ユーザー名/AI-info.git
git fetch origin 2>/dev/null && git checkout main 2>/dev/null || git checkout -b main 
git add 2026-04-08.md 
git commit -m 'AI Catch-up: 2026-04-08' 
git push -u origin main 

注意：GitHubトークンをプロンプトに埋め込む形になるため、 
Fine-grained tokenで対象リポジトリ・Contents権限のみに絞ることを推奨。
```

---

ハマったポイント

1. リポジトリが空だとgit checkoutが失敗する

空のリポジトリに対して git checkout main すると存在しないブランチへの  
チェックアウトになりエラーになる。以下の記述で回避：

git fetch origin 2>/dev/null && git checkout main 2>/dev/null || git checkout -b main

2. メール送信（SMTP）がCCR環境でブロックされる

smtplib でGmailのSMTPに接続しようとすると、CCRのサンドボックスが  
アウトバウンドのSMTP通信をブロックしているため失敗する。

[Errno -3] Temporary failure in name resolution

解決策：SMTPではなくHTTP APIで送信するサービス（Resendなど）を使う。  
WebSearchが通るということはHTTPSは許可されているため、  
urllib.request でRESend APIを叩く形に変更することで解決できる。

3. GitHubトークンの権限設定

Fine-grained tokenでリポジトリを指定しても、  
Permissions → Contents → Read and write を明示的に追加しないと403になる。  
デフォルトでは「権限なし」状態なので注意。

---

実際に届いたコンテンツ（4/8分より抜粋）

実際に出力された記事の質が思ったより高かった。特に印象的だったのは：

* Claude Codeで11人編成のマルチエージェント開発チームを構築した話（Zenn）
* Claude CodeがLinuxの23年間発見されなかった脆弱性を発見した話（HackerNews）
* RTX 5090 1枚で350万件の米国特許を分類した個人開発者の話（Reddit）

英語記事も日本語で読めるのが地味に便利だった。

---

まとめ

Claude Codeのスケジュール実行は、  
「毎日やりたいけど面倒でできていないこと」を自動化するのに向いている。  
今回はAIキャッチアップだったが、週次レポートや定点観測など応用範囲は広い。

プロンプト設計次第でコンテンツ品質が大きく変わるので、  
最初は数日試してフィードバックしながら育てていくのがおすすめ。

---

参考

---
