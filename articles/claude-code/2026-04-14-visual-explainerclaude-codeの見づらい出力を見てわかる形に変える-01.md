---
id: "2026-04-14-visual-explainerclaude-codeの見づらい出力を見てわかる形に変える-01"
title: "【visual-explainer】Claude Codeの見づらい出力を「見てわかる形」に変える"
url: "https://zenn.dev/aiforall/articles/81ca1629bbb9bd"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

# はじめに

Claude Codeは強力なエージェント型AIコーディングツールですが、出力はすべてターミナル上のテキストです。コードの構造説明、実装計画、diffの確認、どれもテキストベースで流れてくるため、情報量が多いほど全体像の把握が難しくなります。  
システムのアーキテクチャや仕様をドキュメントとして残したい場面でも、ターミナルの出力をそのまま転記するわけにはいかず、整理し直す手間が発生します。

本記事では、この課題に対してClaude Codeのカスタムスキルという切り口でアプローチする **visual-explainer** を紹介します。

# visual-explainerとは

**visual-explainer** は、Claude Codeの出力を**図解・スライド・表・diffレビュー画面などの見やすいHTMLページに自動変換し、ブラウザで開いてくれる**カスタムスキル（Custom Slash Command）です。  
簡単にまとめると以下の通りです。

## **これまでの課題は何か**

Claude Codeの出力はターミナル上のプレーンテキストです。たとえば以下のような場面で「見づらさ」が顕在化します。

| 場面 | 課題 |
| --- | --- |
| **コード構造の説明** | テキストで「この関数がこのクラスを呼んで…」と書かれても、依存関係の全体像が掴みにくい |
| **diffの確認** | ターミナルの差分出力は行数が多いと追いきれず、変更の意図を見落としやすい |
| **実装計画の提示** | タスクの依存関係や優先度がフラットなテキストでは整理しづらい |
| **チームへの共有** | ターミナル出力をそのままSlackに貼っても、受け取る側が読む気にならない |

要するに、**LLMの出力品質は高いのに、表示形式がボトルネックになっている**という状態です。

## **visual-explainerの仕組み**

### 従来のフロー

### visual-explainer導入後

出力内容に応じて、最適なレンダリング方式が自動で選択されます。

| 出力の種類 | レンダリング方式 |
| --- | --- |
| フローチャート・依存関係図 | Mermaid |
| アーキテクチャ概要 | CSS Grid Layout |
| データ比較・一覧 | HTML Table |
| グラフ・チャート（数値データの可視化） | Chart.js |

# セットアップ

Claude Codeのプラグインマーケットプレイスからインストールできます。ビルドは不要です。

```
/plugin marketplace add nicobailon/visual-explainer
/plugin install visual-explainer@visual-explainer-marketplace
```

これだけで完了です。生成されたHTMLは`~/.agent/diagrams/` に保存され、自動でブラウザが開きます。

# 出力例

実際にサンプルプロジェクト（Python + FastAPI の3層構造API）で `/visual-explainer:generate-web-diagram` を実行した結果です。

## **リクエストフロー図**

Mermaidによるフローチャートが自動生成され、Client → Middleware → Router → Service → Repository → Firestore のリクエストの流れが一目で把握できます。  
![](https://static.zenn.studio/user-upload/6d8f341a22e1-20260413.png)

## **レイヤー構成の詳細**

各レイヤーの責務がカード形式で整理されます。クラス名、メソッド一覧、レイヤー間の依存関係がコードバッジ付きで表示されており、ターミナルのテキスト出力とは情報の読みやすさが段違いです。  
![](https://static.zenn.studio/user-upload/32b2d769e88b-20260413.png)

## **APIエンドポイント一覧**

HTTPメソッドがカラーバッジで色分けされたテーブルとして出力されます。認証の要否も一覧できるため、API仕様の確認にそのまま使える品質です。  
![](https://static.zenn.studio/user-upload/fcdd2ea038d0-20260413.png)

また、4行以上・3列以上のテーブルをターミナルに出力しようとした場合、自動的にHTMLページとしてレンダリングされます。

# コマンド一覧

インストール後、以下のスラッシュコマンドが使えるようになります。

| コマンド | 内容 |
| --- | --- |
| /visual-explainer:generate-web-diagram | コード構造や処理フローの図解 |
| /visual-explainer:generate-visual-plan | 実装計画の視覚化 |
| /visual-explainer:generate-slides | スライドデッキの生成 |
| /visual-explainer:diff-review | diffの色分けレビュー画面 |
| /visual-explainer:plan-review | 実装計画のリスク評価付き比較 |
| /visual-explainer:project-recap | プロジェクト概要スナップショット |
| /visual-explainer:fact-check | ドキュメントのファクトチェック |
| /visual-explainer:share | VercelにデプロイしてURL共有 |

# 所感

Claude Codeの出力品質は高い一方で、ターミナルというインターフェースの制約から「**せっかくの情報が活かしきれない**」と感じる場面は少なくありません。visual-explainerは「出力の中身はそのまま、表示形式だけを変える」というシンプルなアプローチで、この課題を解消してくれます。

特にdiffの色分け表示やコード構造の図解は、コードレビューや設計の確認で即効性があると感じました。Vercelデプロイによる共有機能も、チーム開発での活用を考えると実用的です。

日常的にClaude Codeを使っている人は、試してみる価値があると思います。

# 参考リンク
