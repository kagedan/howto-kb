---
id: "2026-07-03-h-a-t-a-r-a-k-e-github-copilotのモデルピッカーについにオープンウェイト-01"
title: "@h_a_t_a_r_a_k_e: GitHub Copilotのモデルピッカーに、ついにオープンウェイトのKimi K2.7 Codeが正式入りした。"
url: "https://x.com/h_a_t_a_r_a_k_e/status/2073125583551430880"
source: "x"
category: "claude-code"
tags: ["API", "x"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

GitHub Copilotのモデルピッカーに、ついにオープンウェイトのKimi K2.7 Codeが正式入りした。

Copilot側でホストされた形とはいえ、商用IDE内で「クローズドだけでない選択肢」が当たり前になる最初の一歩だと思う。

まずはPro系プランから順次展開で、BusinessとEnterpriseは管理者が明示的にオンにしない限り使えない設計になっている。

コストを抑えた日常のコーディングにはK2.7、セキュリティや本番リリース前の差分にはクローズドフロンティアモデル、といった「使い分け前提のルーティング設計」が現実解になっていきそう。

経営視点では、モデルそのものの性能比較よりも
どのタスクをどのモデルに流すか
ログや監査の粒度をどう変えるか
を設計できるかどうかが、開発チームの生産性とリスクの差になっていく。
省エネ経営的に言うと「1モデルで殴る時代」から「仕事ごとに最適なモデルへ自動で振り分ける時代」へのスイッチが、いよいよIDEの中まで降りてきた感じがある。
──────────────────────
▼ 補足情報
GitHub公式Changelogによると、Kimi K2.7 CodeはGitHub Copilotのモデルピッカーで選べる初のオープンウェイトモデルで、GitHubがMicrosoft Azure上でホストし、プロバイダのリスト価格に基づく従量課金として提供されるとされています。​⁠https://t.co/WNKatwiQh2

提供開始時点ではCopilot Pro、Pro+、Maxプランが対象で、Visual Studio CodeやVisual Studio、Copilot CLI、GitHub Webやモバイルアプリ、JetBrains、Xcode、Eclipseなど複数のクライアントから選択可能です。BusinessやEnterpriseではデフォルトで無効になっており、管理者がポリシー設定で有効化しない限り組織ユーザーは利用できません。​⁠https://t.co/WNKatwiQh2​⁠https://t.co/K3F5pvP8UX

Kimi K2.7 Code自体はMoonshot AIが開発したコーディング特化のオープンウェイトモデルで、1兆パラメータのMixture-of-Experts構成とおよそ256kトークンのコンテキスト長を持ち、長期のソフトウェアエンジニアリングタスクやマルチターンのツール呼び出しに強みがあるとされています。​⁠https://t.co/i6BBo6yX0Y​⁠https://t.co/MksKIRT03C
価格面では、KimiのAPI基準で入力約0.95ドル、出力約4ドルの100万トークンあたり料金が公開されており、同クラスのオープンウェイトモデルと比べると高めですが、フロンティア級クローズドモデルよりは低コスト帯に位置づけられています。​⁠https://t.co/MksKIRT03C


--- 引用元 @github ---
Kimi K2.7 Code is the first open-weight model you can select in the GitHub Copilot model picker. What does that mean for you?

@burkeholland explains how this low-cost, high-performance model gives you more choice and flexibility in your workflow. ▶️ https://t.co/rxkmT2cABP
