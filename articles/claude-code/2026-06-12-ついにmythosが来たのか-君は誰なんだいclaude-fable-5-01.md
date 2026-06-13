---
id: "2026-06-12-ついにmythosが来たのか-君は誰なんだいclaude-fable-5-01"
title: "ついに、Mythosが来たのか…？ 君は誰なんだい、Claude Fable 5"
url: "https://qiita.com/kaichan_dot/items/f31aa748d8a45c2a2b25"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "qiita"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4165185/ef3f89ea-a9ec-443a-9976-5661945aa01c.png)


新しいClaude、また出ちゃいました、、。今回は「結局なにが変わったの？」をサクッとキャッチアップしていきます。

## はじめに

こんにちは！前回は[「出たてほやほやのClaude Opus 4.8を整理してみた」](https://qiita.com/kaichan_dot/items/a5234436a61194e24df7)を書きました。ありがたいことに、これまで書いた記事のなかで**一番多くのリアクションをいただきました**。読んでくださった方、ありがとうございました。

2026年6月10日（日本時間）、Anthropicが **Claude Fable 5** と **Claude Mythos 5** を発表しました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4165185/9ed0a695-0f24-4d27-b387-e8edfa8f933b.png)
[ザ・ファブル - 南勝久 作](https://www.kodansha.co.jp/comic/products/0000014927)

ところで「Fable」と聞いて、僕が最初に思い浮かんだのは漫画の『ザ・ファブル』でした(小声)。伝説のkし屋のほうです。

fable は「寓話・おとぎ話」のこと。じつは mythos（神話）も、もとをたどれば同じく「語られるもの＝おはなし」を指す言葉です。Anthropicいわく、だから対の名前にしたとのこと。つまり FableとMythosは"兄弟"的なネーミングになってます。じゃあ、同じ日に出た2つのモデルに、なぜわざわざ兄弟の名前を付けたのか——ここが今回の内容に直結しています。
 
前回はOpus 4.8の「正直さ」を主役に据えましたが、今回はその上をいく新世代モデルです。結論から言うと、**今回いちばん面白いのは性能の話ではないです**。「すごく賢いモデルを安全に世に出すために、どんな仕組みを発明したか」のほうが内容としてはあります。
 
その仕組みが **「フォールバック」**。危ないテーマを聞くと、Fable 5ではなく**一段下のOpus 4.8が代わりに答える**という、あまり聞いたことのない方式です。これが今回のAnthropicの発想です。
 

 
### この記事でわかること
 
- Claude Fable 5 / Mythos 5 で何が変わったのか
- 主役の「フォールバック」とは結局なに？ なぜそんな仕組みにしたのか
- 能力の目玉（コーディング・ビジョン・メモリ）
- 開発者が知っておくべき使い方の勘所（ここ地味に大事）
## まず結論（要点だけ）
 
**Mythosクラスという最上位モデルを史上はじめて一般公開しました。ただし危ないテーマは賢いまま答えさせず、Opus 4.8に"フォールバック"させる新方式になってます。**
 
| ざっくり | 中身 |
|---|---|
| 主役 | Mythos級を初の一般公開（=Fable 5） |
| 新方式 | 危険トピックは拒否でなくOpus 4.8が代打 |
| 価格 | 入力\$10 / 出力\$50（per 1M tokens） |
| 注意点 | サブスクは段階展開（6/22まで無償同梱→6/23以降クレジット制） |
 
## Claude Fable 5 とは
 
- **公開日**：2026年6月9日（米国）／6月10日（日本）
- **位置づけ**：Opusクラスの**さらに上**に新設された「Mythosクラス」。第1弾は4月にGlasswing限定で出た Mythos Preview で、今回が一般向けの第2弾。
- **Fable 5 と Mythos 5 の関係**：**中身は同一モデル**。違いはセーフガードの有無だけ。安全策ガッチリ版がFable、外した版がMythos（こちらは限定提供）。
- **名前の由来**：冒頭で触れたとおり、Fable はラテン語 *fabula*（「語られるもの」）由来で、*mythos* に通じる言葉。**中身が同じなのに安全装備が違うから、対になる別名を付けた**というわけです。
> Its capabilities exceed those of any model we've ever made generally available.
> ── [Anthropic公式（@claudeai）](https://x.com/claudeai/status/2064394146916229443)
 
「これまで一般提供したどのモデルより高性能」と言い切っています。えらい強気だな。
 
## フォールバックについて（今回の主役）
 
### 仕組み
 
普段、AIに危ない質問（爆弾の作り方など）をすると「お答えできません」と**拒否**してきます。Fable 5には、この拒否とは別に**もう一つの動き**が足されました。
 
**サイバー・生物化学・蒸留**に関連するクエリを検知すると、Fable 5ではなく**一段下のClaude Opus 4.8が代わりに応答（フォールバック）する**んです。画面には以下の表示になります
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4165185/3e6b4bfa-7326-4888-b783-4a0023e98850.png)

 

 
- **引き金は「危険かどうか」ではなく「話題」**。セキュリティ業務や生物の研究のような真っ当な質問でも、この3ジャンルに触れるとOpusに回されることがあります（公式も「無害なリクエストが引っかかることがある」と認めています）。
- **フォールバックは拒否の置き換えではない**。本当に危険な要求なら、代打のOpus 4.8がこれまでどおり拒否します。「Fableなら何でも答えてくれる」わけではないです。
ちなみに、このセーフガードを**一部解除した版が Mythos 5**。こちらは引き続き、サイバー防御の関係者など**一部にのみ限定提供**で、一般ユーザーは触れません。


 
### なぜフォールバックさせるのか（調べてみた）
 
公式ドキュメントとannouncementを読むと、検知対象は **3カテゴリ** でした。
 
> Fable 5's safeguards detect requests related to cybersecurity, biology and chemistry, and distillation.
> ── [Anthropic公式（@claudeai）](https://x.com/claudeai/status/2064394156735172627)
 
| カテゴリ | 中身 |
|---|---|
| ① サイバーセキュリティ | エクスプロイト/マルウェア作成、偵察・横展開などエージェント的ハッキングまで広く |
| ② 生物・化学 | 実験手法や分子メカニズム。当面、ほとんどの生物系要求が対象 |
| ③ 蒸留（distillation） | **モデルの思考の抽出**。docs上は `reasoning_extraction` という拒否カテゴリ |
 
注目したいのが③です。これは「**Fableの中身を抜き取られないようにする**」ための枠で、ざっくり2方向あります。ひとつは競合モデルを育てるための大規模な能力の抜き取り（蒸留）、もうひとつは「内部の推論を全部書き出して」系の指示で発動する `reasoning_extraction`。どちらも狙いは同じで、Fableの賢さをコピーされないようにする、というものです。
 
では「なんでそこまでするんや」ということですが、答えは**能力が高いから**です。公式によると、AAV（アデノ随伴ウイルス）の外殻組成を予測するタスクで、Mythos級が**専用のタンパク質特化モデルを「生物学的な推論だけ」で上回った**そうです。創薬を10倍速にする力は、裏を返せば悪用リスクにもなる。いわゆるデュアルユース問題ですね。だから「賢いまま誰にでも答えさせる」のではなく、危ない領域だけ賢さを絞る、という判断です。
 

 
## 能力ざっくり3つ
 
### ① ソフトウェアエンジニアリング
 
**Stripeが5,000万行のRubyコードベースの全体移行を、たった1日で完了**したそうです。人手だとチームで2か月超かかる規模です。SWE-Bench Proは80.3%。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4165185/5666643c-fb8f-4264-a459-eef86ca83747.png)

> ↑ Agentic coding（SWE-Bench Pro / FrontierCode）。
> ※これらはコーディング系なのでフォールバックの対象外＝Fable 5の素の実力（後述の `*` の話とは別枠）。
 
### ② ビジョン（視覚）
 
ここが個人的に一番驚いたところ。**ポケモン（FireRed）を、画面のスクショだけ＝ビジョンのみでクリア**しています。旧モデルは補助ツール（ハーネス）を与えてもクリアに苦戦していた領域です。

去年（2025年）のAWSサミットに参加した時に、Anthropicが展示で同じようなことを行っていたのを思い出しました。（Anthropicのメモとエンジニアにサインをもらったのが懐かしい）
 
https://youtu.be/CIQBP1w4B1M
 
### ③ メモリ／ロングコンテキスト
 
数百万トークンを横断しても集中が切れません。ローグライクの名作 **Slay the Spire で、持続メモリの効果がOpus 4.8の3倍**、最終章への到達率も3倍だったとのこと。
 

 
ほかにも「遊び心」デモが公式から出ていたので良ければ、見てください。
 
**物理の第一原理から太陽系の軌道を導いて、日食まで予測するシミュレーション**
 
https://youtu.be/5f5JYLZHdhw
 
**工場ゲーム Factorio を自力で戦略を立てて自動化**
 
https://youtu.be/6YPqoARpYuQ
 
**ブラウザCADで3Dプリント可能モデルを設計（しかもCADエディタ自体もAIコパイロットもFable製）**
 
https://youtu.be/tpjJeH1pPws
 
**流体シミュレーションをベートーベンのEDMリミックスに同期（その曲もコードで生成、"音楽を聴いたことがない"のに）**
 
https://youtu.be/xmP7bhigCWE
 
## 使い方（開発者向け）

 
まず切替方法から。Claude Codeなら：
 
```bash
/model claude-fable-5
```

 
Opus 4.8から何が変わったかを表にするとこうなります。
 
| 項目 | Opus 4.8 | Fable 5 |
|---|---|---|
| effortデフォルト | high | high（low/medでも旧xhigh超えることが多い） |
| thinking | adaptive（オフ可） | **常時オン**・要約出力のみ |
| 体感の応答時間 | 普通 | **長め**（数分〜、自律実行は数時間） |
| 危険トピック | 自分で応答 | **Opus 4.8 にフォールバック** |
| 価格（入/出 per 1M） | \$5 / \$25 | \$10 / \$50 |
 
ざっくり要点：
 
**思考が常時オンで、応答が長め**。1リクエスト数分〜、自律実行なら数時間に伸びることも。クライアント側のタイムアウト・ストリーミング・進捗表示は見直しておいたほうがいいです（公式も「移行時の最大の変化点」と言及）。
 
> Thinking is always on, and responses can take longer.
> ── [Anthropic公式（@ClaudeDevs）](https://x.com/ClaudeDevs/status/2064394925358366821)
 
**effortはhighが既定**でOK。Fableのlow/mediumが旧モデルのxhighをしばしば上回るので、xhighは本当に難しい問題だけ温存。
 
> In our evals, even low/medium often beat previous models at xhigh
> ── [Anthropic公式（@ClaudeDevs）]
(https://x.com/ClaudeDevs/status/2064394925358366821)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4165185/311bde9c-1ac3-4955-9b66-80e2ecc61ef0.png)

> ↑ FrontierCode（最難のDiamondサブセット）。精度 vs コスト。FableはどのeffortでもOpus 4.8の上にいる。
 
**プロンプトはむしろシンプルでいい**らしいです。旧モデル用に作り込んだプロンプトやskillは、Fableには過剰指定で、**かえって性能が落ちることすらある**そうです。一度素のままで試してみるのをおすすめします。
 
> Existing prompts or skills developed for prior models are often too prescriptive for Fable.
> ── [Anthropic公式（@ClaudeDevs）](https://x.com/ClaudeDevs/status/2064394926469840957)
 
**「自分の推論を本文に全部書き出して」系の指示はNG**。さきほどの `reasoning_extraction` を踏んでフォールバックが増えます。推論を見たいならadaptive thinkingの構造化thinkingブロックを使いましょう。
 
> 内部の推論を応答テキストとして書き出させる指示は `reasoning_extraction` を発動させ、Opus 4.8へのフォールバックを増やす（要旨）
> ── [公式docs：プロンプティングガイド](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
 
長時間タスクは「**進捗はツールの結果に照らして報告して**」と指示すると、捏造ステータスがほぼ消えるとのこと。…これ、前回Opus 4.8で推した「正直さ」路線がちゃんと続いているんですよね。シリーズを通して一本筋が通っています。
 
> 進捗報告をツールの実行結果に照らして行わせると、捏造された進捗ステータスがほぼ解消された（要旨）
> ── [公式docs：プロンプティングガイド](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

## ベンチマークについて
 
公式のベンチ表がこれです。**ただし読み方に注意点があるので先に言っておきます。**
 
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4165185/03033eda-6b5b-4846-ae25-d97d2d929ec2.png)

 
**その1：数値は「Mythos 5 と Fable 5 の高い方」を載せています。**
 
**その2：`*` 付きの項目（サイバー・Terminal-Bench・Health など）は、あくまでMythos 5の数字です。** 一般人が触るFable 5だと、ここはフォールバックが効いてOpus 4.8並みに落ちます。たとえばサイバーの78.0%ではあるが、Fableはそこを40%（Opus 4.8）にフォールバックします。
 
逆に `*` なしの項目（SWE-Bench Pro、Computer use、空間推論など）は、素直にFable 5の実力として読んで大丈夫です。
 
テスターの声も出ていて、Cursorは「長期タスクで扱える幅が一気に広がった」、Replitは「一年前なら百回プロンプトが要ったアプリを一発で作れた」といった評価。全14社が早期テストに参加しています。
 
## 今後の見通し
 
限定版の **Mythos 5** は、サイバーの安全策を外した版で、まずはGlasswingのサイバー防御パートナー向けです。
 
> For a small group of cyber defenders and critical infrastructure providers, we are also launching Claude Mythos 5.
> ── [Anthropic公式（@claudeai）](https://x.com/claudeai/status/2064394158056386684)
 
今後は米政府とも協議しながら、信頼アクセスプログラムで段階的に対象を広げる予定とのこと。さらに**生物医学の研究者向け**にも、生物・化学の安全策だけ外した版（サイバーは維持）を開放していくそうです。
 
あと重要なのが、**Mythosクラスは全トラフィックで30日のデータ保持が必須化**されたこと。学習には使わず安全目的限定で、原則30日後に削除。プライバシー的にはここは注意で、実務などでは一旦使えないですね。
 
## まとめ
 
- **Fable 5 = Mythosクラスを史上はじめて一般公開したモデル**。中身はMythos 5と同一で、違いは安全策の有無だけ。
- 主役は性能ではなく **「フォールバック」** という新方式。サイバー/生物・化学/蒸留（=思考の抽出）の3カテゴリを検知したら、Opus 4.8が代打する。
- 能力は本物。Stripeの1日移行、ポケモンをビジョンのみでクリア、Slay the Spireでメモリ3倍。
- ベンチ表の `*` には注意。Fableで素直に出ない数字がある。
- 価格は\$10/\$50。サブスクは6/22まで無償同梱→6/23以降クレジット制。
能力競争のニュースは見飽きるくらい出回ってますが、「賢すぎるモデルをどう安全に届けるか>>>拒否ではなく代打」という発想がこれから浸透していきそうですね。前回の「正直さ」とあわせて、Anthropicが何を大事にしているのかが、だんだん見えてきた気がします。
 
## 参考
 
- [Claude Fable 5 and Claude Mythos 5（Anthropic公式ブログ）](https://www.anthropic.com/news/claude-fable-5-mythos-5)
- [Anthropic公式X（@claudeai）発表スレッド](https://x.com/claudeai/status/2064394146916229443)
- [Claude プロンプティングのベストプラクティス（公式docs）](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Claude Opus 4.8 価格（公式）](https://www.anthropic.com/claude/opus)
