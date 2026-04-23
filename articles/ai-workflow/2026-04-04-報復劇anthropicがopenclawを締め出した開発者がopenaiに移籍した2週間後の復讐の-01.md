---
id: "2026-04-04-報復劇anthropicがopenclawを締め出した開発者がopenaiに移籍した2週間後の復讐の-01"
title: "【報復劇】AnthropicがOpenClawを締め出した！開発者がOpenAIに移籍した2週間後の「復讐」の全貌"
url: "https://qiita.com/emi_ndk/items/dbff9450c004922c65a0"
source: "qiita"
category: "ai-workflow"
tags: ["API", "OpenAI", "qiita"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

**結論から言うと**：Anthropicは4月4日、OpenClawなどのサードパーティAIエージェントをClaudeサブスクリプションから締め出した。表向きは「サーバー負荷」だが、実態はOpenClaw開発者がOpenAIに移籍した直後の「報復」ではないかと業界で騒然となっている。

---

## 何が起きたのか？

2026年4月4日午後3時（米国東部時間）、**AnthropicはOpenClawとサードパーティツールからのClaudeサブスクリプションアクセスを遮断**した。

「え、月額$20払ってるのに使えなくなるの？」

そうだ。今後OpenClawでClaudeを使いたければ、**別途従量課金（pay-as-you-go）** が必要になる。

従来：Claudeサブスクリプション → OpenClawで無制限に使用可能  
今後：OpenClaw使用分は**API課金（トークン単位）** が必須に

## なぜこのタイミングなのか？

ここからが本題だ。

OpenClawの開発者**Peter Steinberger**は、2026年2月15日にOpenAIに入社した。Sam Altmanが直々にTwitterで発表した大型採用だ。

そして**わずか2週間後**、AnthropicはOpenClawを事実上「追放」した。

偶然？　業界の見方は違う。

## 「サーバー負荷」という建前

Anthropicの公式声明はこうだ：

> 「サードパーティツールの使用が当社のコンピュート資源とエンジニアリングリソースに**過大な負荷**をかけていた」

しかし、この説明には矛盾がある。

### 問題点1：自社ツールは許可されている

Claude Code自体には`/loop`コマンドや自動スケジュール機能がある。これは**同じような自律的な使用パターン**を可能にするが、こちらは禁止されていない。

### 問題点2：本当に負荷が問題なら

Hacker Newsでの議論を引用すると：

> 「それが問題なら、ToSを変えるんじゃなくて、リミットを調整すればいい」

サブスクリプションにはすでにトークン制限がある。「サードパーティツール経由」という**使い方**で制限をかけるのは不自然だ。

## ユーザーの怒りが爆発

開発者コミュニティは激怒している。代表的な声を紹介しよう：

> 「OpenClawのインスタンス2つをAPIキーに切り替えたら、コストが高すぎて使い物にならない」

> 「彼らは重要な変更をTwitterに埋め込んで発表する」

> 「これは容量の問題じゃない。ファーストパーティ製品に誘導するための**自社優遇（self-preferencing）** だ」

## OpenAIとの対照的な姿勢

一方、**OpenAIはOpenClawを歓迎している**。

Peter SteinbergerがOpenAIに入社した時点で、OpenAIはサードパーティハーネスを明示的にサポートする姿勢を示した。OpenClawはもちろん、OpenCodeなども利用可能だ。

この違いは何を意味するのか？

| 項目 | Anthropic | OpenAI |
| --- | --- | --- |
| サードパーティツール | 制限（API課金必須） | 許可 |
| OpenClaw対応 | 締め出し | 開発者を採用 |
| 姿勢 | クローズド | オープン |

## Anthropicが提示した「補償」

批判を受けて、Anthropicは以下を発表した：

* **月額プラン料金相当の一時クレジット**
* **割引使用バンドル**

しかし、これで納得するユーザーは少ない。固定費でバジェットを組んでいたチームは、突然**変動費**に直面することになる。

## 本当の問題：AIエコシステムの閉鎖性

この騒動は単なる「AnthropicがOpenClawを嫌っている」という話ではない。

**AIプラットフォームがサードパーティツールをどう扱うか**という、業界全体の方向性を示している。

### 閉鎖的アプローチのリスク

1. **開発者の離反** - 自由度の高いプラットフォームへ移行
2. **エコシステムの縮小** - サードパーティ開発が停滞
3. **イノベーションの阻害** - 多様なツール開発が困難に

### Apple vs Androidの既視感

これは「App Store対オープンエコシステム」の議論を思い出させる。ただし、AIエージェントの場合、**相互運用性がより重要**だ。

## あなたへの影響と対策

### OpenClawユーザーの選択肢

1. **API課金に移行** - コスト増を覚悟
2. **OpenAIに乗り換え** - GPTベースで継続
3. **Claude Code直接利用** - Anthropicの想定通り

### コスト試算

**具体例**：1日1万トークン使用の場合

* 従来：月額$20のサブスクリプション内
* 今後：API課金で**月$30〜50程度**（使用量による）

小規模なら影響は限定的だが、**ヘビーユーザーは2〜3倍のコスト増**も。

## まとめ：AIエージェント戦争の新章

今回の騒動は、以下を示している：

* **人材獲得競争**：主要人材の移籍がプラットフォーム戦略を変える
* **エコシステム戦略**：オープン vs クローズドの対立が激化
* **ユーザー軽視のリスク**：開発者コミュニティの信頼は一度失うと戻らない

Peter SteinbergerがOpenAIで何を作るのか、そしてAnthropicがこの批判にどう対応するのか。

**AIエージェント戦争は、まだ始まったばかりだ。**

---

## 参考リンク

Anthropic cuts off the ability to use Claude subscriptions with OpenClaw and third-party AI agents

OpenClaw creator Peter Steinberger joins OpenAI

Tell HN: Anthropic no longer allowing Claude Code subscriptions to use OpenClaw

Claude just shut the door on OpenClaw (unless you pay more)

---

この記事が参考になったら、**いいねとストックをお願いします！**

OpenClawを使っている方、Anthropicの決定についてどう思いますか？　**コメントで教えてください！**
