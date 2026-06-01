---
id: "2026-06-01-anthropicproject-glasswing初動レポート1か月で1万件超の脆弱性発見myth-01"
title: "Anthropic「Project Glasswing」初動レポート――1か月で1万件超の脆弱性発見、Mythosが結果を出し始めた"
url: "https://qiita.com/quotidia/items/ffa0b92fbd55293ffdc4"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-06-01"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

> 本記事は筆者が運営する AI Quotidia (ai.quotidia.jp) の海外ニュース解説記事です。

# Anthropic「Project Glasswing」初動レポート――1か月で1万件超の脆弱性発見、Mythosが"結果"を出し始めた

みなさん、AIに「世界中のソフトウェアを点検させたら、いったいどれくらいの欠陥が見つかるのか」と考えたことはあるでしょうか。その問いに、Anthropicがひとつの初期回答を提示しました。

Anthropicは2026年5月22日、防御的サイバーセキュリティ支援プログラム**「Project Glasswing」**のローンチから約1か月時点の**初動レポート（initial update）**を公開しました。同社のフラッグシップモデル**Claude Mythos**を活用したこのプログラムは、当初の構想からわずか1か月で、想像を超える具体的な成果を出し始めています。

## 数字が示す「結果」のスケール

レポートで開示された数字を整理します。

- **発見された脆弱性：1か月で1万件超**
- **参加パートナー：50社に拡大**（ローンチ当初から大幅増）
- **Cloudflare事例：単独で2,000件の脆弱性を検出**
- **銀行詐欺の事前阻止：150万ドル（約2.3億円）相当のattackを検知**

どれも抽象的な「可能性」ではなく、すでに防いだ被害として記録された具体的な数字です。Anthropicがローンチ時に掲げた「AIを盾として使う」というビジョンは、わずか1か月で「実際に何かを守った」という結果へと変わりつつあります。

## 衝撃を呼んだwolfSSL事例

業界に最も衝撃を与えたのが、暗号通信ライブラリ**wolfSSL**での発見です。Mythosは、**偽造証明書を生成可能にする脆弱性**を検出しました。

wolfSSLはIoT機器や組み込みシステムで広く使われているセキュリティライブラリです。証明書偽造が可能ということは、暗号通信の信頼の根幹が揺らぐということ。AIがここまで深い層の欠陥を発見したという事実は、セキュリティライブラリ業界全体に「AIに監査される時代」の到来を告げました。

## Claude Security public beta と Cyber Verification Program

もうひとつの大きな動きが、**Claude Security**の**パブリックベータ**開始です。これまで承認制（gated access）だったMythosベースのセキュリティ機能が、一般開発者にも段階的に開放されます。さらに、第三者による検証スキームとして**Cyber Verification Program**も新設されました。「発見しました」だけで終わらせず、外部の独立した検証者によって結果の妥当性を担保する仕組みです。

## 日本にとって何が変わるのか

この動きは、日本の私たちにもいくつかの示唆を残します。

まず、**国内のセキュリティライブラリ・OSSプロジェクト**がAI監査を「いつ、誰が、どの基準で」受けるかという議論が現実味を帯びてきました。wolfSSL級の発見が、日本企業が依存するOSSにも起こりうるからです。

次に、**金融機関や重要インフラ事業者**にとって、Claude Securityのパブリックベータは「使うか、使わないか」の判断を迫る選択肢になります。150万ドルの詐欺阻止という具体例は、稟議書の中で重みを持つ数字です。

そして、**第三者検証スキーム（Cyber Verification Program）**は、日本のAIガバナンス議論にも参照点を提供します。「AIに任せたら検証はどうするのか」という問いに、ひとつの実装解が示されたわけです。

ローンチから1か月。Mythosは「動き始めた」段階を抜けて、「結果を出している」段階に入りました。次の1か月で、この数字がさらにどう積み上がっていくか――静かに、しかし確かな関心を持って見守りたいところです。


---

参考元: https://www.anthropic.com/research/glasswing-initial-update

---

> この記事は [AI Quotidia](https://ai.quotidia.jp?utm_source=qiita&utm_medium=referral) から転載しています。
> **文豪モード**（情景描写と比喩で読む）・**速報モード**（30秒で読める）もサイトで読めます。
> 👉 https://ai.quotidia.jp?utm_source=qiita&utm_medium=referral
