---
id: "2026-07-18-windowsでcodexからclaude-fablesonnetを呼ぶ環境を作る方法実録power-01"
title: "WindowsでCodexからClaude Fable/Sonnetを呼ぶ環境を作る方法【実録・PowerShell対応】"
url: "https://note.com/jidoka_bucho/n/n999d5fc74972"
source: "note"
category: "ai-workflow"
tags: ["API", "OpenAI", "note"]
date_published: "2026-07-18"
date_collected: "2026-07-18"
summary_by: "auto-rss"
query: ""
---

こんにちは、ジドウカ部長です。

業務を Google Workspace × AI × GAS で仕組み化する話をよく書いていますが、今回は少しだけ開発寄りです。  
ですので、サムネイルもイメージ変えてみました（笑）

テーマは、

**Windows版Codexから、Claude Fable / Sonnetを呼べるようにする環境構築**

です。

Mac/Linux向けの手順は出てきています。  
ただ、Windowsでそのまま試すと、だいたい次のところで止まります。

* `bash` がない
* `sqlite3` がない
* `install.sh` が動かない
* `claude.cmd` と `claude.ps1` の挙動が違う
* team名に日本語を使うとdelegate側で弾かれる
* `--setting-sources ""` がWindowsでは崩れる

私も実際に詰まりました。

この記事では、その失敗ログを潰しながら、WindowsでCodex → Claude連携をdry-runまで通した手順をまとめます。

## この記事でできること

最終的に、Codexから次のような依頼ができる状態を目指します。

```
Fableに設計レビューして
Sonnetに実装案を相談して
```

Codexをメインの作業場にして、Claudeを必要なときだけレビュー役・相談役として呼ぶイメージです。

ただし、いきなりモデル実行はしません。  
まずは **dry-run** で、

を確認します。

## 前提

この記事はWindowsユーザー向けです。

確認した環境は以下です。

重要なのは、Claude APIキーではなく、`claude auth login` 済みのClaude.aiサブスクを使うことです。

## 注意

この記事はOpenAI公式・Anthropic公式・元repo作者の公式Windows対応ではありません。

元repoはMIT Licenseなので、著作権表示とライセンスを残したうえで、Windows対応の検証手順としてまとめています。

また、Fable/Sonnetの実行はClaude側の利用に該当します。  
この記事では、まずdry-runまでを安全に確認する流れにしています。

---

ここから先では、実際にWindowsで詰まった箇所と、その回避手順を順番に書きます。

有料部分には以下を入れています。

* Windowsで動かすための全体手順
* Git Bash / SQLite CLI の準備
* `claude-agmsg-delegate` のWindows対応ポイント
* `install.ps1` の考え方
* agmsg team / delivery mode 設定
* 最終dry-run確認
* よくあるエラーと対処
* 実運用時の使い分けプロンプト

**※公開初期は検証版価格として1,480円にしています。  
今後、手順更新・追加検証・トラブル対応例を追記したら価格を上げる予定です。**
