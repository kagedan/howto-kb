---
id: "2026-06-07-github-copilot法人利用の移行先検討結果-01"
title: "GitHub Copilot法人利用の移行先検討結果"
url: "https://zenn.dev/nuits_jp/articles/2026-06-07-copilot-business-migration"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

2026年6月1日より、GitHub Copilot Business / Enterprise のAIモデル利用は、AI Creditsベースの従量課金に移行しました。

それなりに使っていた方が従量課金で同程度利用しようとすると、月額$100〜$2,000程度の予算が必要になる可能性があります。

先にGitHub Copilotを擁護しておくと、公開されているモデル別単価を見る限り、主要モデルはOpenAIやAnthropicのAPI価格とほぼ同水準です。つまり、Copilotが特別に高いというより、これまでの固定料金がかなり強かった、という見方もできます。

とはいえ、今年度の予算はすでに決まっています。そこで、もう少し現実的な移行先を検討してみました。

## 注意事項

下記の計算は、あくまで公式情報を起点にした推論値です。実際の使用感や請求額と一致しない可能性があるため、最終判断は各社の公式情報と実利用データを確認してください。

また、GitHub Copilotのコード補完とNext Edit Suggestionsは、AI Creditsの課金対象外です。この記事で主に扱うのは、Copilot Chat、Copilot CLI、Copilot cloud agentなど、AI Creditsを消費する機能です。

なお、既存のCopilot Business / Enterprise顧客には、2026年6月1日〜2026年9月1日の移行期間中、通常より多いAI Credits枠が付与されます。この記事の比較は、原則として通常枠を前提にしています。

## 結論

法人プラン限定で、セルフサービス契約とクレジットカード払いが許容できるなら、下記のいずれかが有力候補です。

* OpenAI「Business ChatGPT & Codex」プラン
* Anthropic「Team Standard」または「Team Premium」プラン

請求書払いが必須でEnterprise契約しか選べない場合は、他社も従量課金要素が強くなるため、今回の試算だけでは乗り換えの決め手は弱そうです。

## 詳細な比較

APIベースの利用額が$200〜$300以内に収まる場合は、CodexとClaudeの好みで選べばよさそうです。それ以上利用する場合は、ClaudeのTeam Premiumがかなり有力な候補になります。

![](https://static.zenn.studio/user-upload/deployed-images/465328ccd457112b1bd03cba.png?sha=b4e5292f34ab9ca1e1d9373b71f800546f37dcb4)

最近はCodexを好んでいるので、Codex側にも$125程度の中間プランがあればそちらを選びたいところです。ただ、私の個人利用では、現状の固定枠だけだと足りないことが分かっています。

なお、Claude Codeは最大150シートまでで、それ以上はEnterpriseの従量課金が必要になります。

## 推論根拠

ざっくり説明すると下記の通りです。

![推定利用可能トークンの推測観点](https://static.zenn.studio/user-upload/deployed-images/1efd4399485c955873ab1f19.png?sha=20fe00888ea70000785f44163421200643a4e9d7)

### Codex

Codexは、OpenAI公式のCodex Pricingに公開されている**5時間あたりの利用枠**を起点にしています。

たとえばPlusおよびBusinessでは、GPT-5.4のlocal messagesが **20〜100 / 5h** と示されています。また、local messagesとcloud tasksは5時間枠を共有し、追加の週次制限があり得るとも説明されています。

URL：<https://developers.openai.com/codex/pricing>

今回の試算では、この公開利用枠を

で月次化し、API価格に換算しています。

Business ChatGPT & Codexはこの前提で、利用可能価格を約$257〜$1,303と推定しています。一方、Business CodexやEnterprise flexibleは従量課金型のため、利用可能倍率はx1.0としています。

### Claude Code

Claude Codeは、Anthropic公式のClaude Code Costsに公開されている平均利用コストを起点にしています。

公式ドキュメントでは、Claude CodeはAPI token consumptionで課金され、企業導入では平均して$13/developer/active day、$150〜$250/developer/month程度と説明されています。

URL：<https://code.claude.com/docs/en/costs>

今回の試算では、この$150〜$250/monthをPro相当の基準値として扱い、Team StandardやTeam Premiumを倍率換算しています。Claude PricingではTeam PremiumがStandardより 5x more usage と説明されているため、この関係も加味しています。

URL：<https://claude.com/pricing>

Enterpriseは$20/seat + usage at API ratesのため、API従量課金部分だけを見るとx1.0です。ただしseat費込みでは、実効倍率はx1.0未満になり得ます。

## さいごに

あくまで実際に利用する前の推論です。実際に利用してみる予定なので、共有できる内容があればまた書きます。すでに実利用されている方がいれば、ぜひ情報提供いただけるとうれしいです。

あと、この種のプランは遠くないうちに変更される可能性もあり、年間契約するかは悩みどころです。
