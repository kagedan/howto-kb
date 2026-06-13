---
id: "2026-06-12-mastra-youtube-解説-agents-hour今週のaiニュースまとめ2026年6月11-01"
title: "[Mastra YouTube 解説] Agents Hour：今週のAIニュースまとめ（2026年6月11日）"
url: "https://zenn.dev/shiromizuj/articles/9c0415d195c051"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "OpenAI"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の公式YouTubeチャンネルで配信されている週次ニュース番組「Agents Hour」の内容を、日本語で読みやすく整理しました。今回は loop engineering の是非を軸に、OpenAI の Codex Sites、Cognition の productivity guarantee、Cloudflare の買収、中国系モデルへの急速なシフト、Anthropic の信頼性問題、そして on-device / open model の加速まで、一週間の話題をかなり広く俯瞰しています。

特に今回は、単なるニュースの羅列というより、「これからの coding agent をどう運用するか」という実務的な論点が前面に出ていました。何をプロンプトするかより、どの loop を回すか。どのモデルが一番賢いかより、どの層にどのモデルを置くか。2026 年半ばの空気感がよく出ている回です。

[Mastra YouTube動画 速報解説一覧](https://zenn.dev/shiromizuj/articles/8d6e4fd86631e9)

---

## 動画情報

<https://www.youtube.com/watch?v=yUtcNZEW-2A>

* **URL**: <https://youtu.be/yUtcNZEW-2A>
* **原題**: Loop Engineering, OpenAI Sites & the Great China Model Shift | This Weeek In AI
* **チャンネル**: Mastra
* **公開日**: 2026年6月11日
* **長さ**: 24分15秒
* **言語**: 英語

## 概要

今回の Agents Hour の話題の多くは、「loop engineering が実務の主戦場になってきた」というトレンドに関係していました。Claude Code の Boris や Peter Steinberger の発言をきっかけに、「直接 agent にプロンプトするのではなく、agent を動かす loop 自体を設計するべきだ」という考え方が盛り上がっています。ただし番組の 2 人は、その主張をそのまま受け入れているわけではありません。短いバグ修正や、人間が途中で介入したい作業では、昔ながらの対話ループも依然として有効だと明確に述べています。

一方で市場の現実は、モデルの知能競争だけではなくなっています。OpenAI は Codex Sites で「作ってすぐ共有できる」体験を押し出し、Cognition は Devin の価値保証を掲げ、Cloudflare は VoidZero を買収し、中国系モデルは OpenRouter 上の利用量で米国モデルを超え始めたと語られます。Notion が Anthropic の信頼性問題でモデルを切り替えた話まで出てくると、今の競争軸は「最強モデルは誰か」より「安く、速く、止まらず、仕事として成立するか」へ移っているのがよく分かります。

後半のモデル紹介も同じ文脈で読むと腑に落ちます。Gemma 4、MiniMax M3、GLM 5.1、Liquid の structured JSON VLM、Nemotron の streaming ASR など、それぞれが単体で覇権を狙うというより、voice、vision、UI、自動化、on-device、model routing といった実務の部品として整ってきています。「エージェントは何ができるか」ではなく、「エージェントをどういう構成で回すべきか」に関心が移りつつあることを示す良い観測点でした。

## 要点

1. **Anthropic の「エンジニアは 8 倍多くコードを出荷している」という主張に対し、番組は「コード量と価値は別だ」と冷静に見ている。**
2. **Cloudflare の Matthew Prince によれば、agentic traffic が人間トラフィックを初めて上回った。** エージェント利用の立ち上がりは予想よりかなり速い。
3. **loop engineering は今年の重要キーワードになりつつある。** ただし「もう prompting するな」という極論には懐疑的で、タスクによって loop を使い分けるべきだという立場だった。
4. **traditional loop、Ralph loop、goal loop、dynamic workflows** という 4 段階の整理が示され、それぞれの向き不向きがかなり実務的に語られた。
5. **OpenAI の Codex Sites は Lovable や Replit 的な領域に本格参入する動き**として捉えられていた。
6. **Cognition は Devin の productivity guarantee と Devin Desktop を打ち出し、価値保証と運用画面の両面から enterprise へ寄せている。**
7. **OpenRouter では中国系モデルの利用量が米国モデルを上回り始めた。** Lindy が 100% DeepSeek V4 に切り替えた話は、その象徴として紹介された。
8. **Notion が Anthropic の信頼性問題でモデル切り替えを迫られた話は、性能より reliability が重要な局面を示している。**
9. **Gemma 4、Gemma 4 QAT、Magenta RealTime 2、Miso One、Nemotron、Liquid、GLM 5.1、MiniMax M3** など、多様な open / specialized model が一気に紹介された。
10. **今の焦点は frontier model 一択ではなく、安価なモデル、速い推論、model routing、on-device 実行をどう組み合わせるかに移っている。**

---

## 詳細

### Anthropic の「8倍のコード出荷」は、AI 生産性の伸びと限界を同時に示している

![](https://static.zenn.studio/user-upload/c7e89065f1e0-20260611.png)

番組の冒頭では、Anthropic が「自社エンジニアは 2021 年から 2025 年の間に四半期あたり 8 倍のコードを出荷するようになった」と投稿した話題が取り上げられます。これはいかにも強いメッセージですが、Shane と Abhi は最初からかなり冷静です。lines of code は AI 時代の成果指標としてかなり怪しく、HTML や React コンポーネント、MCP サーバーや workflow ファイルが大量に増えただけでも数字は大きく伸びるからです。

![](https://static.zenn.studio/user-upload/38833e3ecdd8-20260611.png)

それでも 2 人は、「平均的なエンジニアがモデルによって以前より多くを出せるようになっている」感触自体は否定していません。重要なのは、出荷コード量の増加をそのまま価値の増加とみなさないことです。8 倍のコードは 8 倍の価値ではない。AI 導入の効果測定を考えるとき、ここは非常に本質的な視点です。

![](https://static.zenn.studio/user-upload/0e589b3efa2b-20260611.png)

その直後に「Anthropic の社員は落ち込んでいるらしい」という投稿が並んだことも、番組では半ば皮肉として扱われていました。スピードが上がることと、働く人の納得感や幸福感は別物だということです。AI がコード出力を増やしても、組織運営や仕事の質の問題までは自動的に解決しません。

### agentic traffic はもう人間トラフィックを超え始めている

Cloudflare の Matthew Prince が「agentic traffic が人間トラフィックを上回った」と述べた投稿は、番組の前半でかなり印象的なトピックでした。最初は 2027 年末と見ていたものが、2027 年初頭に前倒しされ、いまでは 2026 年半ばに起きている。予想以上に速い立ち上がりです。

![](https://static.zenn.studio/user-upload/931b812c981f-20260611.png)

ここで重要なのは、単に Web クローラが増えたという話ではなく、docs、CLI、Web サービス全体において「人間が読む・操作する」よりも「agent がアクセスして処理する」流量が本格的に増えていることです。今後のプロダクト設計では、人間向け UI に加えて agent 向け surface をどう設計するかがますます重要になります。

この話は、MCP や agent-facing API、structured output、machine-readable docs など、ここ 1 年の流れともつながります。閲覧者が人間中心だった時代の前提が、かなり速い速度で崩れてきています。

### loop engineering は hype でもあり、実務上の本質でもある

今回の中心テーマは間違いなく loop engineering です。きっかけになったのは、Claude Code の Boris が「もう prompting ではなく、どの loop を回すかを考えている」と語ったこと、そして Peter Steinberger も「coding agent に直接 prompt するな。agent を prompt する loop を設計しろ」と投稿したことでした。

![](https://static.zenn.studio/user-upload/ce6f4624bb67-20260611.png)

ただし、番組のスタンスは極論への反論です。Shane は「もう prompting すべきではない」という言い方を clickbait （日本語で言う「釣りタイトル」）だと切って捨てています。実際、答えが見えている単純なバグ修正なら、短い prompt を投げて 1 ターンで直す方が早い。逆に、重要で探索的な仕事や長時間走らせる仕事なら、goal loop や dynamic workflow の方が有利です。つまり、loop engineering は prompt engineering の完全な置き換えではなく、選択肢を増やす考え方として見るのが妥当です。

AI 界隈ではすぐに「古い方法は終わった」と言い切る言説が流行りますが、実際のところは単純な操作と複雑なオーケストレーションを両方使い分けるべきでしょう。

### 4つの loop の整理がかなり分かりやすい

番組内では、coding agent の運用パターンが 4 種類に整理されていました。

![](https://static.zenn.studio/user-upload/7c06a2a88548-20260611.png)

まず **traditional loop** は、人間がプロンプトし、agent が出力し、人間がフィードバックし、必要なら PR まで持っていく、という古典的な対話型ループです。短い修正、意図が明確な変更、人間が途中で強く介入したい作業に向いています。

次に **Ralph loop** は、plan をタスクリストへ分解し、agent が fresh context でタスクを順番に消化していく形式です。コンテキスト保持や compaction が弱かった時代の工夫として出てきたもので、プロトタイプ用途では有効だった一方、実運用コードとしてはそのまま出ないことも多かったと振り返られていました。

その次が **goal loop** です。詳細な goal と plan を与え、長時間 agent を走らせ、judge が plan 達成を検証していく構成です。番組では、今もっとも実用価値が見えている loop として扱われていました。数十分から数時間、場合によっては十数時間以上走る long-running agent の基盤として有望だ、という立て付けです。

最後が **dynamic workflows** です。Claude Code が出してきた新しい流れで、agent 自身がタスクに応じた workflow を組み立て、並列 subagent や judge を含めた実行構造を自動生成する。繰り返し性のある仕事や、高度な分解・並列化が必要な仕事には魅力があります。ただし番組内では、Mastra チーム自身はまだ goal loop ほどの価値を dynamic workflows で実感できていないとも率直に語っていました。

この整理は、いま coding agent を使っている人にとってかなり有用です。何が最先端かを追うのも大事ですが、実務的には「自分の仕事はどの loop に向いているか」で選ぶ方がより重要です。

### OpenAI の Codex Sites は、アプリ生成領域に対する直接攻勢

![](https://static.zenn.studio/user-upload/25b3473e7df7-20260611.png)

OpenAI の Codex Sites については、番組中でもかなり率直に「Lovable や Replit に近い」と表現されていました。仕事のアイデアや計画から、チームで共有できるインタラクティブな Web サイトやアプリを生成する。まず business / enterprise から展開するという点も、単なる遊びのデモではなく、実務導線の中に入れにきていることを示しています。

> 註：Lovable は、要件を文章で伝えるとフロントエンド中心のアプリや UI を比較的すばやく形にする AI アプリビルダーです。非エンジニアや少人数チームでも、プロトタイプを短時間で作りやすいのが売りです。  
> Replit はもともとブラウザ上の開発環境ですが、最近は AI を使ってアプリ生成やコード修正まで一気通貫で進められる方向に強く寄っています。つまり「オンライン IDE」でもあり、「AI 付きのアプリ作成基盤」でもあります。

2 人が面白がっていたのは、「Lovable が最も依存しているモデルが、その Lovable 自体の市場を取りに来る」という構図です。モデル提供者は、アプリレイヤーのユースケースが伸びれば伸びるほど、そのデータと需要を吸収して垂直統合しやすくなります。AI 時代のアプリスタートアップが直面する構造的な厳しさが、かなり露骨に表れた例といえます。

この話は、単に「OpenAI がまた新機能を出した」で終わりません。モデルラボが自前プロダクトを広げるほど、その上に乗る SaaS は差別化をより深い部分、つまり workflow、独自データ、運用導線、コミュニティ、ブランドに求められるようになります。

### Devin は「価値保証」と「運用画面」で enterprise へ寄せている

AI ソフトウェアエンジニア Devin を作っている会社 Cognition は、「AI should earn its keep」という表現と一緒に、Devin が支払額に見合う engineering value を出せなかったら、価値が出るまで利用分を補填する、という「AI Productivity Guarantee（AI生産性保証）」を打ち出しました。

![](https://static.zenn.studio/user-upload/42255c5ab69c-20260611.png)

これは今の業界の不信感を逆手に取った打ち手だと二人は言います。つまり背景には、「AI コーディングエージェントは PR はたくさん作るが、実際にどれだけ価値を出しているのか怪しい」という空気がある、からこの発表は、単なる機能追加ではなく、AI エージェント市場全体の不信感に対する営業メッセージとして読める、ということです。

もし Devin が支払額より少ない engineering value しか出さないなら、価値が出るまで使用料を補填する。最大 1000 万ドルまでという表現も含めて、かなり強気です。

番組では、ここで重要なのは marketing の派手さより「みんなが token 消費の割に成果が出ていないのではと疑い始めている」点だと語られていました。AI エージェントは PR を量産できますが、マージされない PR が増えても価値は増えません。プロトタイピングなら unmerged code にも価値がありますが、本来の目的が修正の完遂だったなら、それは失敗です。

![](https://static.zenn.studio/user-upload/b2a3dca95c4d-20260611.png)

この文脈で Devin Desktop が続けて紹介されたのも興味深いところです。ローカル agent とクラウド agent の fleet を 1 つの面で管理する発想は、単一の超賢い agent を売るというより、agent 運用の control plane を売る方向に近い。エンタープライズ実装で必要なのは、単なるモデル性能だけではなく、誰に何を任せてどう review するかを見渡せる画面だからです。

### 中国系モデルシフトは、コスト最適化の現実解として加速している

![](https://static.zenn.studio/user-upload/9107a1b82b30-20260611.png)

今回もっとも重要な市場トピックの 1 つが、「中国系モデルの台頭」でした。OpenRouter の利用データでは、中国系モデルへの token 消費が米国モデルを超え始めていると紹介され、さらに Lindy が Anthropic から DeepSeek V4 へ 100% 切り替えたという投稿も引用されました。

![](https://static.zenn.studio/user-upload/40a22f57681b-20260611.png)

ここでの論点はシンプルです。frontier model は確かに高性能ですが、高すぎる。業務全体のどこにその知能が本当に必要かを見極めないと、採算が合わなくなる。もし DeepSeek や Qwen、GLM、MiniMax のようなモデルが、ある種のタスクで 95% 以上の品質を出し、しかも 10 分の 1や 20 分の 1 のコストなら、多くの企業はそちらへ寄ります。

番組で印象的だったのは、「最強である必要はない。十分にできればいい」という感覚がかなり共有されていたことです。これは 2025 年までの frontier model 中心の議論から、一段進んだ地点です。いま重要なのは、どのユースケースで open / cheaper model が実用域に入っているかを見極め、必要な場所だけ高価なモデルを使う構成を組むことです。

### reliability の問題は、モデル切り替えをさらに加速させる

Notion が Anthropic モデルを無効化したという話題も、その流れを後押しする材料として取り上げられていました。高性能モデルを採用していても、止まるなら業務システムには組み込みづらい。しかも Notion のような大手プロダクトが継続的に障害の影響を受けるなら、ほかの企業も冗長化や代替モデルを真剣に検討します。

![](https://static.zenn.studio/user-upload/336f92a43d71-20260611.png)

ここで効いてくるのが、まさに model routing や multi-model 構成です。単一ベンダーへの依存は、性能面でも価格面でも運用面でもリスクになります。今回の番組全体を通して、「frontier model 一択の時代は終わりつつある」という空気がかなり明確でした。

### モデルの話題は「勝者探し」ではなく「部品の充実」として見るべき

後半では Gemma 4 12B、Gemma 4 QAT、Magenta RealTime 2、Miso One、Nemotron 3.5 ASR Streaming、Liquid LFM 2.5-VL-Extract、GLM 5.1、MiniMax M3 など、多数のモデルが一気に紹介されます。一見するといつものモデルダンプですが、今回の文脈では意味合いが少し違います。

![](https://static.zenn.studio/user-upload/975932ac200c-20260611.png)

Gemma 4 QAT は少メモリ動作を後押しし、on-device AI の現実味を高めます。これは単に「軽いモデルが出た」という話ではなく、スマートフォンやラップトップ、社内端末のようなローカル環境に agentic reasoning を持ち込める可能性が広がったという意味です。クラウドへ毎回問い合わせなくても済むなら、遅延、コスト、プライバシー、ネットワーク依存のすべてに効いてきます。

その一方で、Magenta RealTime 2 は音楽生成、Miso One は感情豊かな音声、Nemotron は streaming ASR、Liquid は画像から structured JSON を返す VLM と、それぞれ別の弱点を埋める方向に進んでいます。ここで見えているのは、1 つの万能モデルがすべてを飲み込む未来というより、音声入力、画面理解、構造化抽出、軽量ローカル推論のような各サブシステムが着実に強くなっていく未来です。エージェントが現実の業務で使えるようになるには、推論本体だけでなく、こうした周辺能力が揃うことの方が重要な場面も多くあります。

特に Liquid のような structured JSON を返す VLM は、agent 実務との相性がかなり良い部類です。自動化では、自由文の説明をあとから別工程で JSON に詰め直すより、最初から機械処理しやすい形で返ってくる方が圧倒的に扱いやすいからです。画面理解や帳票処理、フォーム読取、GUI オートメーションのようなタスクでは、この差がそのまま実装コストや壊れにくさの差になります。

GLM 5.1 や MiniMax M3 の速度改善も同じくらい重要です。モデル評価ではつい「どれだけ賢いか」に目が向きますが、長い loop を回す agent では、応答が遅いだけで総実行時間もコストも大きく膨らみます。十分な品質を保ちながら高速に動くモデルは、subagent を複数回す構成や judge を何度も挟む構成で特に効いてきます。つまり今の勝負は、モデル単体の IQ ではなく、オーケストレーションしやすさ、構造化出力、推論速度、運用コストまで含めた「システム部品としての使いやすさ」に移っているわけです。

### on-device AI と UI 再設計の気配も見えている

Gemma 系の話題では、Abhi が「これは Android 上の on-device AI へ向かう流れだ」とかなりはっきり述べていました。もし小さなモデルでスマホ上のタスクが十分こなせるなら、常時クラウド依存の構成は必須ではなくなります。これはコストだけでなく、遅延、プライバシー、オフライン動作の面でも意味があります。

一方、Brian Chesky が新しい AI ラボを始める話題からは、「今の AI は front-end を作れても、似た見た目ばかりになりがちだ」という問題意識も見えていました。AI で UI を量産できるようになった結果、本当に差が出るのは“何を速く作れるか”ではなく、“どんな新しい UX を発明できるか”になる、という見方です。

### 「AI は儲かっているのか」という問いは、業界内相互送金を除くとまだ厳しい

isaiprofitable.com の話題は小ネタのようでいて、かなり本質的です。AI 企業が別の AI 企業へ支払っている金額を除いてみると、業界全体として本当に利益が出ているのかは怪しい、ということです。落語の「花見酒」みたいですね。番組では「実際には 1 社にお金が流れているだけではないか」というニュアンスで語られていました。

![](https://static.zenn.studio/user-upload/7eeee209d407-20260611.png)

これは、AI エコシステムの多くがまだ infra / model 依存で回っていることを示しています。アプリ層や導入支援、運用ソフト、vertical SaaS がどこまで外部実需を取れるかが、今後の大きな分水嶺になりそうです。

### quick hits も、全部「適材適所」の方向へ向かっている

最後の quick hits では、v0 の Shopify storefront 生成、Factory の model routing、Nous Research の Hermes Desktop が紹介されました。小粒に見えますが、方向性は一貫しています。より多くの仕事を agent が肩代わりし、その際に 1 つのモデルや 1 つの UI に閉じない構成が求められている、ということです。

Factory の model routing に対するコメントも象徴的でした。prompt cache は確かに強力ですが、それに縛られて高価なモデルを使い続けるのが正しいとは限らない。キャッシュ済み Opus より、場合によっては DeepSeek の方がまだ安い。この感覚は、今後の agent 設計でかなり重要になるはずです。

---

## 関連リンク
