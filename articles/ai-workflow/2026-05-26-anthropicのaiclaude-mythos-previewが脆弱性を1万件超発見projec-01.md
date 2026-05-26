---
id: "2026-05-26-anthropicのaiclaude-mythos-previewが脆弱性を1万件超発見projec-01"
title: "AnthropicのAI「Claude Mythos Preview」が脆弱性を1万件超発見——Project Glasswingが示す防御AIの可能性"
url: "https://note.com/shali_note/n/nc6db9b50c786"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-05-26"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

「AIが攻撃ツールになる」という懸念の裏側で、「AIが防御ツールになる」という動きも静かに加速しています。

Anthropicは2026年4月、Claude Mythos Previewを使ったセキュリティプロジェクト「Project Glasswing」を立ち上げました。  
1か月余りで深刻な脆弱性を**1万件超**発見するという成果を上げ、初期レポートが公開されています。

Project Glasswingとは何か、何が起きているのか、詳しく解説します。

## 🔐 Project Glasswingとは

![](https://assets.st-note.com/img/1779754635-l0VJoycpT9t5Efs7R3aSe4K8.png?width=1200)

Project Glasswingは、Anthropicが2026年4月に開始した**セキュリティ強化プロジェクト**です。

目的は明確で、Claude Mythos Previewを防御目的で使い、世界中で広く使われているソフトウェアの脆弱性を事前に洗い出し、修正を促すことです。

これまで、ソフトウェアの脆弱性発見は専門家がコードを一行ずつ読み込む、非常に時間のかかる作業でした。  
Mythos Previewはそのプロセスを自動化し、大幅に短縮することを目指しています。

## 🛡️ 発見した脆弱性の規模

![](https://assets.st-note.com/img/1779754650-TfPClybXrzM8L9mvHEtKkBac.png?width=1200)

Anthropicが独自にMythos Previewで1,000以上のプロジェクトをスキャンしたところ、深刻度「高」以上と推定される脆弱性候補を**6,202件**発見しました。

これは単独での数字です。  
AWS・Apple・Cisco・Google・Microsoft・NVIDIA・Palo Alto Networksなど約50のパートナー企業も参加し、合計では**1万件超**の脆弱性が世界規模の重要ソフトウェアで検出されています。

「深刻度が高い」とは、悪用されれば実際の被害につながる可能性のある脆弱性ということです。  
1万件という数字は、これまで専門家チームが長期間かけて行うような調査を、AIが短期間で達成したことを示しています。

## ⚡ 発見だけでなく「悪用可能性の検証」まで

![](https://assets.st-note.com/img/1779754680-G2MnRcbOfNHlkwrZpDW8qxJy.png?width=1200)

注目すべきは、Mythos Previewが脆弱性を見つけるだけでなく、**実際に悪用できるかどうかを高い精度で検証**できる点です。

従来の自動スキャンツールは偽陽性（実際には問題ないのにアラートが出る誤検知）が多く、専門家が一つひとつ確認する作業が必要でした。  
Mythos Previewはこの確認作業まで自動化できるとされており、セキュリティチームの負担を大幅に削減できます。

Anthropicは、Mythos Previewについて「ごく一部の高度な専門家を除く、ほとんどの人間を超える水準で脆弱性を発見・悪用できる可能性がある」と評価しています。

これは防御側にとっては頼もしい能力です。  
同時に、このモデルが悪意ある利用者の手に渡った場合のリスクも意味しています。  
Anthropicがプロジェクトを非公開・パートナー限定で進めているのは、そうした悪用リスクへの配慮からとみられています。

## 🤝 参加パートナーの顔ぶれ

![](https://assets.st-note.com/img/1779754468-fEvLcuqQF315WdwlJAsy9CnD.png?width=1200)

Project Glasswingに参加している企業は、IT業界の主要プレイヤーばかりです。

* AWS（Amazon Web Services）
* Apple
* Cisco
* Google
* Microsoft
* NVIDIA
* Palo Alto Networks

これらの企業は自社の重要ソフトウェアにMythos Previewを適用し、悪意ある攻撃者に先んじて脆弱性を発見・修正することを目指しています。  
世界中で使われているクラウド・OS・ネットワーク機器のセキュリティ強化に、AIが直接貢献している形です。

## 🇯🇵 日本の金融機関も動き出す

![](https://assets.st-note.com/img/1779754701-8ysi93wmYuAHqvhZjIpFUDgL.png?width=1200)

Project Glasswingの成果は、日本でも注目されています。

2026年5月12日、財務大臣兼金融担当大臣が、Claude Mythos Previewの金融システムへのサイバーリスクを検討する公民ワーキンググループの設立を発表しました。

三菱UFJフィナンシャル・グループ・みずほフィナンシャルグループ・三井住友フィナンシャルグループの3大銀行が、数週間以内にMythos Previewへのアクセスを持つ見込みとされています。

日本の金融インフラを守るためにAIを活用するという流れは、国内のセキュリティ対策の方向性を示す大きな動きです。

## ⚠️ 防御AIのジレンマ：強力さとリスクの裏表

![](https://assets.st-note.com/img/1779754714-HpDi1d2MaoJlxyGe0X9OZqPz.png?width=1200)

防御目的で強力なAIを使うことは、倫理的な問いも伴います。

「脆弱性を自律的に発見・検証できるAI」は、攻撃者の手に渡れば逆用されるリスクがあります。  
これは「防御AIのジレンマ」とも言える構造です。

防御側が先にスキャンして修正を促すことで、悪意ある攻撃者が同じ脆弱性を悪用する前に対処できます。  
「攻撃より先に動く防御」という競争で、AIが防御側のスピードを上げる役割を担いつつある現実が、Project Glasswingには凝縮されています。

## 📝 まとめ

![](https://assets.st-note.com/img/1779754488-xflvnbarcg6VMFk8p0t7ZCuq.png?width=1200)

AnthropicのProject Glasswingは、Claude Mythos Previewを防御目的で展開し、1万件超の脆弱性発見という実績を示したプロジェクトです。  
AWS・Apple・Google・Microsoftなどの主要パートナーを巻き込み、日本の3大銀行も参加を予定しています。

AIがサイバーセキュリティの最前線に立ちつつある現実を示す動きとして、今後の展開に注目です。  
少しでも参考になれば幸いです。  
最後まで読んでいただきありがとうございました。

---

[#AI](https://note.com/hashtag/AI) [#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#Claude](https://note.com/hashtag/Claude) [#AIエージェント](https://note.com/hashtag/AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88) [#テクノロジー](https://note.com/hashtag/%E3%83%86%E3%82%AF%E3%83%8E%E3%83%AD%E3%82%B8%E3%83%BC) [#Anthropic](https://note.com/hashtag/Anthropic) [#サイバーセキュリティ](https://note.com/hashtag/%E3%82%B5%E3%82%A4%E3%83%90%E3%83%BC%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3) [#脆弱性検出](https://note.com/hashtag/%E8%84%86%E5%BC%B1%E6%80%A7%E6%A4%9C%E5%87%BA)

---
