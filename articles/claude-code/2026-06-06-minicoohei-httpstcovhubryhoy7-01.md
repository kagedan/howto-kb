---
id: "2026-06-06-minicoohei-httpstcovhubryhoy7-01"
title: "@minicoohei: https://t.co/VHUbRYhoy7"
url: "https://x.com/minicoohei/status/2063105741976952929"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "x"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/VHUbRYhoy7


--- Article ---
Claude Code を Team プランで〜とか会社に入れて欲しい！みたいな話があると思います。確かに最高に便利だしみんながAI使ってハッピーになる未来もあります。

ただ、**「配って終わり」にすると地味に危ないしもったいない**です。(Enterpriseの場合はこの辺も対応されてるけど、従量課金なので、今回Teamプランの方向け。）

理由はシンプル。Claude Code（Agentic AI）は質問に答えるだけでなく、ファイルを書き換え、コマンドを実行し、外部に接続し、PR まで自分で作る。

だから**「うっかり'Credentials' / '.env' を読む」「`curl` で外に投げる」「`sudo` で何かを無効化する」が、悪意ゼロ・設定不足だけで起きる可能性がある**。危ない。悪意のない漏洩とか攻撃とか。一番危ない

本格運用するなら、最初にやっておきたい"3つの設定"を、なぜやるかとセットで説明します。

**1. Team の管理設定** … 権限を全社で強制（＝事故らせない）
**2. OTel の設定** … 利用状況を見える化（＝誰が・何トークン・どの Tool・どのモデル）
**3. Hooks の設定** … コマンドの中身を検査して止める（＝最後の砦）

## ① Team の管理設定 ― 権限を全社で強制する

Claude Code には「権限バイパスモード（`--dangerously-skip-permissions`）」がある。便利だが ON のまま配ると全員が承認なしで何でも実行できる。事故の一番太い線がここ。

転機が 2026/6/5。claude.ai の権限まわりが ON/OFF トグルから**「管理設定（managed settings）」**に移行した。これでトグルでは無理だった deny リスト（`.env`/鍵の読取、`sudo` の実行）まで Web 管理画面から全社一括で強制できる。利用者は外せない。

![](https://pbs.twimg.com/media/HKGaifYaEAAs1Om.jpg)

(Enterpriseの場合はこの辺も対応されてるけど、従量課金なので）

```json

{
  "permissions": {
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(~/.ssh/**)", "Bash(sudo:*)
", "Bash(git push:--force*)"],
    "allow": ["Bash(git status:*)", "Bash(npm test:*)", "Bash(pytest:*)"],
    "disableBypassPermissionsMode": "disable"
  },
  "allowManagedPermissionRulesOnly": true
}
```

やり方は簡単でこれを

![](https://pbs.twimg.com/media/HKGa57OawAAaDOg.jpg)

Claude Code ->  組織設定　-> "管理" で設定するだけ

![](https://pbs.twimg.com/media/HKGbEp-aoAAa5KJ.jpg)

deny と allow、最低限これだけは。`deny`=絶対やらせない禁止（外せない）、`allow`=安全な定番を承認レスにして摩擦を減らす。評価は `deny → ask → allow` で deny が必ず勝つ。最低ラインは「`.env`・鍵・`sudo` を deny」

![](https://pbs.twimg.com/media/HKGbRRAaMAAhisr.jpg)

効いているかは再起動して `/status`。`Enterprise managed settings (file / remote)` と出ればその設定が読まれている証拠。

![](https://pbs.twimg.com/media/HKGbyv4aQAAQJh1.png)

bypass を試すと弾かれる（実機 v2.1.165 で確認）し、ダメなツールを呼ぼうとすると防ぐ。コンテキストとして返してくれるから、LLM側もエラーの理由を把握しやすい。

![](https://pbs.twimg.com/media/HKGcIFPaAAABHct.jpg)

## **② OTel の設定 ― 利用状況を見える化する**

「誰がどれだけ使ってる？」「どのモデル？」
