---
id: "2026-06-04-madogiwacowork-httpstcowaeijfdqps-01"
title: "@madogiwacowork: https://t.co/WaEIjFdQPs"
url: "https://x.com/madogiwacowork/status/2062662530741551199"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "GPT", "cowork", "x"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-x"
query: "Cowork スケジュール OR Cowork スキル作成 OR Cowork 自動化"
---

https://t.co/WaEIjFdQPs


--- Article ---
エージェントが、誰も知らないうちに動いている。

これは未来の話ではありません。

Claude Enterpriseを140名弱に展開し、Copilot Studioでエージェントを作っているチームもあります。

でも今この瞬間、誰がどのエージェントをどの業務で使っているか、管理者である私にはほとんど見えていません。承認したはずのエージェントですら、実態が把握できていない。

問題は「AIを使うか」ではなくなりました。「動き始めたAIを、誰がどう管理するのか」です。

今回は、Scoutが来る前に大企業が設計しておくべきことを全部書きます。
Scoutは2026年5月のMicrosoft Buildで発表された自律型AIエージェントです。OpenClawをベースとし、Teams・Outlook・SharePoint・OneDriveと連携しながら、プロンプトなしで先回りして動きます。前回記事でその概要を書きました。
[https://x.com/madogiwacowork/status/2062125973940891846](https://x.com/madogiwacowork/status/2062125973940891846)

*※*この記事は私の環境での考察です。他社・他環境での動作を保証するものではありません（*2026*年*6*月*5*日時点の情報）。

---

## **第1章：エージェントが、誰も知らないうちに動いている**

まず2つのソリューションの関係を整理します。ScoutはM365の中で先回りして動くエージェントです。Agent 365はそのエージェントを観測・統制・保護する管理基盤です。この2つが組み合わさることで、M365上で自律動作するAIエージェントを、管理可能な形で企業に導入する設計が初めて成立します。

![](https://pbs.twimg.com/media/HJ-lR9EaoAAwIcN.jpg)

AIエージェント巡る企業の現場における問題は2層あります。

一つは、承認済みのClaude Enterpriseでさえ使用状況が管理者に見えないという可視化の問題。もう一つは、IT部門が把握しないまま社員が個人のChatGPTアカウントや個人PC上のOpenClaw系エージェント、各種APIを直接叩いているという、本来の意味でのシャドーAI問題です。シャドーAIとは後者、つまり承認なく使われている未承認ツールのことです。

Agent 365は、この二番目のシャドーAI問題を含め、社内外で増殖するAIエージェントを観測・統制・保護するための管理基盤としてMicrosoftが提供しています。Agent 365自体は2026年5月1日にGA。Shadow AI検出など一部機能はPreviewとして提供されています。M365管理センターに「Shadow AI」ページが新設され、少なくともIntune管理下のWindows端末では、OpenClawなどの未承認エージェントの検出・ブロックができるようになりました。対象はOpenClawから始まり、GitHub Copilot CLIやClaude Codeなど広く使われるエージェントへ順次拡大予定です。

ここで一つ、重要なことを言っておきます。

OpenClawやHermesAgentで社内に小規模なエージェントを導入していた企業はすでに存在します。ただ、それらはあくまで個別導入でした。

今回のスキームは次元が違います。M365と完全連携しながら、社内で動く主要なAIエージェントを一つの管理基盤で統合的に扱おうとしている。少なくとも多くの日本企業にとって、まだ経験したことのない管理領域です。

この枠組みを最初に取り込み、AIネイティブな組織として動き始めた企業が、大きな競争優位性を手にします。手探りでいい。ただ、スピードが重要です。先に動いた組織から、差がつき始めます。

これはIT部門だけの話ではありません。

「どのエージェントを許可して、何を禁止するか」というポリシーの中身は、IT部門には設計できません。業務を知っている人間が先に定義しなければ、IT部門はルールを執行できないのです。

AI推進担当として、ここを先手で動く必要があります。

![](https://pbs.twimg.com/media/HJ-fVnBbkAAOjHz.jpg)

---

## **第2章：Work IQという「文脈エンジン」がScoutを動かす**

OpenClawはもともとスケジュールやトリガーで先回り動作できます。

Work IQが追加
