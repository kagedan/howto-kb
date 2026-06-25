---
id: "2026-06-25-aiニュース速報2026年6月2425日openai独自チップclaude-opus-48figma-01"
title: "AIニュース速報（2026年6月24〜25日）｜OpenAI独自チップ、Claude Opus 4.8、Figma AI、Samsung全社AI、富士通PHOTON、Devin急伸ほか"
url: "https://note.com/t_kawa_awak/n/n128ec0f41f1c"
source: "note"
category: "ai-workflow"
tags: ["MCP", "LLM", "OpenAI", "Gemini", "GPT", "note"]
date_published: "2026-06-25"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

2026年6月24〜25日のAIニュースは、AI業界の競争軸がモデルの賢さだけではなく、 **推論コストを下げる半導体、AIを日常業務へ展開する組織運用、会話AIを入口にした消費者体験、そして日本企業の実装力** へ広がっていることを示しました。

OpenAIはBroadcomと共同開発した独自AIチップJalapeñoを発表し、GPU依存と推論コストの抑制に動きました。AnthropicはClaude Opus 4.8を公開し、Google DeepMindからはAlphaFold関連のトップ研究者がAnthropicへ移籍しています。

同時に、Figmaはコードレイヤーやアニメーション対応を含む大型AIアップデートを発表し、Samsung ElectronicsはChatGPT EnterpriseとCodexを全従業員へ展開しました。日本では富士通がTransformer比で最大475倍のGPUスループットをうたうPHOTONを発表し、Devinの国内ユーザー数は前年比1,582%増、メルカリはApps in ChatGPTに対応しました。

## 2026年6月24〜25日のAIニュース全体像：AI競争はモデル性能から運用・半導体・実装へ広がった

今回のニュースを俯瞰すると、AI競争は大きく4つの方向へ進んでいます。

第一は **AIインフラの垂直統合** です。OpenAIが独自チップを持つ意味は、単にNVIDIA対抗という話にとどまりません。ChatGPTやCodexのような大規模サービスでは、学習よりも日々の推論処理が膨大なコストになります。モデルを提供する企業がチップ、メモリ、ネットワーク、データセンター運用まで最適化することで、AIサービスの価格と速度を自社で制御しようとする流れが強まっています。

第二は **AI人材とモデル性能の争奪戦** です。AnthropicがClaude Opus 4.8を公開する一方、Google DeepMindの研究者がAnthropicへ移籍したニュースは、フロンティアAI企業にとって人材が最大級の競争資源であることを改めて示しました。

第三は **AIの業務基盤化** です。Samsungの全社員展開、FigmaのAI機能強化、企業のAIトークン予算管理は、AIが一部の先進部門だけでなく全社運用の対象になったことを示します。

第四は **日本での実装加速** です。PHOTON、Devin、メルカリ、AWS Summit Japan、Woodstock MCPなど、国内でも技術・業務・金融・イベントが同時に動いています。

## OpenAI独自AIチップJalapeñoとAI予算管理：推論コストがAI事業の主戦場になる

OpenAIがBroadcomと共同開発した推論専用AIチップJalapeñoを発表したことは、AIサービスの経済性を考えるうえで大きな節目です。

生成AIはモデルの訓練にも巨額の計算資源を使いますが、サービスが普及するほど日々の推論、つまりユーザーの入力に応答する処理が継続的なコストになります。GPUの調達競争が続くなか、OpenAIが自社ワークロードに合わせたASICを持てば、ChatGPTやCodexのような高頻度サービスの単価を下げ、処理速度や電力効率を改善できる可能性があります。

この動きは、AI企業がモデルだけでなくインフラ企業にも近づいていることを意味します。GoogleはTPU、AmazonはTrainium、Microsoftも独自AI半導体を進めており、OpenAIがJalapeñoを持つことで、フロンティアAI企業の競争はさらにフルスタック化します。

重要なのは、独自チップがすぐにNVIDIAを置き換えるという単純な話ではない点です。多くの企業はNVIDIA GPU、クラウド事業者のAIチップ、自社専用チップを用途別に組み合わせる方向へ進むはずです。高性能な学習、低遅延の推論、社内ツール向けの大量リクエストでは最適な基盤が異なるためです。

企業のAIトークン予算超過問題も、同じ構造を業務利用側から示しています。従業員が日常的な小タスクにAIを使うと、1回ごとのコストは小さくても、全社では急速に予算を消費します。使用上限、承認フロー、部門別コスト配賦、モデル選択ルールを設計しないままAIを展開すると、便利さがそのまま費用増に直結します。

> ソース：[TechCrunch](https://techcrunch.com/2026/06/24/openai-unveils-its-first-custom-chip-built-by-broadcom/)、[TechCrunch](https://techcrunch.com/2026/06/24/companies-are-scrambling-to-stop-employees-from-maxing-out-ai-budgets-with-small-tasks/)

## Claude Opus 4.8とGoogle人材流出：トップAI研究者と高性能モデルの争奪戦が続く

AnthropicがClaude Opus 4.8を公開し、コーディング、エージェントスキル、推論などで前世代を上回る性能を示したことは、AIエージェント時代のモデル改良がまだ高速に続いていることを示します。

とくにコーディングとエージェント能力は、単なるチャット性能よりも企業利用に直結します。コードを書く、リポジトリを理解する、複数ステップの作業を計画する、ツールを呼び出すといった能力が伸びるほど、AIは社員の横に置く補助ツールから、業務プロセスの一部を担う存在へ近づきます。

一方で、Google DeepMindのJonas Adler氏とAlexander Pritzel氏がAnthropicへ転職したニュースは、AI業界の競争が人材面でも激化していることを象徴します。AlphaFoldのような科学AIの成果に関わった研究者は、基礎研究と実用モデルの橋渡しができる貴重な存在です。

AIモデルの性能差は、データ、計算資源、評価基盤に加えて、研究者がどの仮説を試し、どの失敗を早く捨てられるかにも左右されます。トップ研究者の移籍は、単なる採用ニュースではなく、企業間の研究テーマやプロダクト戦略の移動でもあります。

企業側から見ると、モデル選定の考え方も変わります。Claude Opus 4.8のような高性能モデルは、高い推論力や長い作業を必要とする業務に向きます。一方で、すべての社員の軽い要約や翻訳に最高性能モデルを使えば、コストは膨らみます。精度が必要な設計・法務・開発支援と、低コストで十分な日常タスクを分けることが、AI活用の成熟度を左右します。

> ソース：[AI News](https://www.artificialintelligence-news.com/news/anthropic-releases-claude-opus-4-8-news/)、[TechCrunch](https://techcrunch.com/2026/06/24/ai-researchers-continue-to-leave-google-for-its-rivals/)

## Figma AIアップデートとSamsung全社展開：AIは専門職ツールから全社員の業務基盤へ進む

Figmaの大型AIアップデートは、デザインと開発の境界がさらに近づいていることを示します。コードレイヤーの追加により、リポジトリのクローンやコードからデザインレイヤーの抽出が可能になり、モーションやシェーダーのサポート、AIを活用したカスタムプラグイン機能も追加されました。

これまでデザインツールは画面を作る場所、コードは実装する場所として分かれていましたが、AIが両者を翻訳することで、デザイン変更と実装変更の往復が短くなります。デザイナーは実装可能性を意識した設計をしやすくなり、エンジニアは既存コードからUI構造を把握しやすくなります。

Samsung ElectronicsがChatGPT EnterpriseとOpenAI Codexを全従業員へ展開したことは、AIが専門職だけのツールではなく全社基盤になりつつあることを示す象徴的な出来事です。かつてChatGPT利用を制限していた企業が、統制されたエンタープライズ環境で全社利用へ移る流れは、多くの大企業にとって参考になります。

禁止から管理された活用へ移行するには、データ持ち出しルール、アカウント管理、利用ログ、社内教育、開発者向けCodexのレビュー体制が必要です。AI導入の本番は、ツール契約ではなく全社員が安全に使える業務設計から始まります。

> ソース：[TechCrunch](https://techcrunch.com/2026/06/24/figma-adds-code-layers-support-for-animations-more-ai-features-in-new-update/)、[AI News](https://www.artificialintelligence-news.com/news/samsung-chatgpt-enterprise-codex-employee-ai-use/)

## メルカリのApps in ChatGPTとロレアル試着機能：会話AIが消費者サービスの入口になる

メルカリがApps in ChatGPTに対応したニュースは、日本の消費者向けサービスにとって重要です。ChatGPT上の会話を通じて商品検索や出品サポートができるようになると、ユーザーはアプリ内の検索窓やカテゴリをたどる前に、自然文で目的を伝えられます。

フリマサービスでは、何を探すか、どう説明するか、いくらにするかといった小さな判断が利用の摩擦になります。会話AIがその入口になることで、検索と出品のハードルを下げられる可能性があります。

ロレアルとMaybellineがChatGPT内でバーチャルメイク試着機能を提供する動きも、同じ方向です。ModiFaceのAR技術を活用し、リップやアイシャドーの試着を会話形式で行えるようにすることで、ECやブランド接点がチャットのなかへ入り込みます。

GoogleがGemini Live対応のGoogle Home Speakerを発売したニュースも、会話AIの入口がスマホ画面だけではないことを示します。企業は、自社サービスがChatGPT、Gemini、スマートスピーカー、外部MCP基盤など、どのAI接点から呼び出されるべきかを考える必要があります。

> ソース：[ITmedia AI+](https://www.itmedia.co.jp/aiplus/article/2606/24/2000000123/)、[AI News](https://www.artificialintelligence-news.com/news/loreal-maybelline-virtual-try-on-chatgpt/)、[Google Blog](https://blog.google/products-and-platforms/devices/google-nest/google-home-speaker-gemini-features/)

## Agility Robotics上場とスイスApertus：フィジカルAIとオープンAI基盤が同時に前進する

ヒューマノイドロボットDigitを開発するAgility RoboticsがSPAC経由で上場へ向かうニュースは、フィジカルAI市場の期待を示します。評価額は約25億ドルとされ、トヨタ、GXO、Mercado Libreなど複数拠点で稼働している点が注目されます。

生成AIが言葉や画像の世界で進んだ次の段階として、AIが倉庫、製造、物流、店舗といった現実空間で作業するフィジカルAIに投資が集まっています。人型ロボットは汎用性が高い一方、安全性、保守、現場オペレーション、費用対効果の検証が不可欠です。

日本でもHIBANA ROBOTICSの設立が発表され、AIとロボティクスを組み合わせた製造・物流・サービス分野向けソリューションが狙われています。ロボット導入は単体の機械を買うだけでは成果が出ません。現場の業務フロー、センサー、既存システム、作業者の安全導線、保守体制をまとめて設計する必要があります。

一方、スイスが完全オープンソースAIモデルApertusを公開したニュースは、AI基盤の透明性を重視する別の流れを示します。モデル設計、学習データ、コードを公開することで、企業や研究機関が検証し、用途に合わせて改変できる余地が広がります。

> ソース：[TechCrunch](https://techcrunch.com/2026/06/24/agility-robotics-plans-to-go-public-via-spac-in-a-2-5b-deal/)、[AI News](https://www.artificialintelligence-news.com/news/switzerland-releases-its-own-fully-open-ai-model/)、[PR TIMES](https://prtimes.jp/main/html/rd/p/000000001.000184553.html)

## 富士通PHOTON、Mistral OCR 4、Devin急伸：日本市場では高速化・文書解析・開発自動化が焦点

富士通が発表したLLMアーキテクチャPHOTONは、Transformer比で最大475倍のGPUスループット向上をうたう技術として注目されます。大規模言語モデルの運用では、GPUコストと推論速度が普及の制約になります。少ないGPUリソースで大規模モデルを運用できる可能性があるなら、企業内AI、自治体、研究機関、国内クラウドにとって大きな意味があります。

Mistral AIが公開したOCR 4は、日本語を含む170言語に対応し、文字のバウンディングボックスや信頼度スコアを出力できる文書解析OCRとして紹介されています。企業内には契約書、申請書、帳票、マニュアル、紙資料のPDFなど、AI活用の前提となる文書データが大量にあります。

OCRの精度と構造化能力が上がれば、RAG、ナレッジ検索、業務自動化の土台が整います。生成AIの導入はチャットボットから始まりがちですが、実務成果を出すには社内文書をどれだけ正確に読み取れるかが重要です。

AI開発支援エージェントDevinの日本国内ユーザー数が前年比1,582%増となったニュースは、開発自動化への関心の高さを示します。定型的なコーディング、調査、修正、テスト作成をAIに任せる需要は、エンジニア不足の日本市場と相性がよい領域です。

ただし、AI開発エージェントは導入すればすぐに生産性が上がる道具ではありません。リポジトリの構造、テストの整備、レビュー基準、権限範囲、失敗時の巻き戻し手順が揃って初めて効果を出します。

> ソース：[ITmedia AI+](https://www.itmedia.co.jp/aiplus/article/2606/24/2000000125/)、[ITmedia AI+](https://www.itmedia.co.jp/aiplus/article/2606/24/2000000124/)、[ITmedia AI+](https://www.itmedia.co.jp/aiplus/article/2606/24/2000000122/)

## AWS Summit Japan、Woodstock MCP、OrcaRouter、CREATANT投資：国内AI実装は業務と金融へ広がる

AWS Summit Japan 2026が幕張メッセで開幕し、エージェンティックAIをテーマに260以上のセッションを展開したことは、日本企業の関心がAIの試用から本格実装へ移っていることを示します。OpenAI JapanとAnthropic Japanが基調講演に登壇する点も、グローバルAI企業が日本市場を重視している表れです。

Woodstock MCPは、ClaudeやGPTなどのAIを証券口座とノーコードで連携できる国内初のサービスとして紹介されています。AIが金融口座や投資分析に接続されると、資産状況の把握、銘柄分析、リスク説明、レポート作成の自動化が進む可能性があります。

一方で、金融領域では誤情報、投資助言の扱い、個人情報、権限管理のリスクが大きくなります。AIが口座情報に接続されるほど、認可範囲、操作ログ、人間による確認、説明責任を明確にする必要があります。

OrcaRouter月額プランは、Claude Opus 4.8、GPT-5.5 Pro、Gemini 3.5など200以上のモデルを利用でき、インテリジェントなルーティングでAIコスト削減をうたいます。第一電材によるCREATANTへの戦略的投資や、アオラナウとWorkatoのAIエージェント共同デモも、AIが製造業や業務自動化に広がる流れを示します。

> ソース：[AWS公式](https://aws.amazon.com/jp/events/summits/japan/)、[PR TIMES](https://prtimes.jp/main/html/rd/p/000000037.000092154.html)、[PR TIMES](https://prtimes.jp/main/html/rd/p/000000039.000138449.html)、[PR TIMES](https://prtimes.jp/main/html/rd/p/000000001.000184614.html)、[PR TIMES](https://prtimes.jp/main/html/rd/p/000000021.000134928.html)

## 企業が確認すべき実務ポイント：AIコスト、データ連携、権限、教育を一体で設計する

今回のニュースから、日本企業が確認すべき実務ポイントは4つあります。

第一は **AIコストの見える化** です。OpenAIの独自チップや企業のAI予算超過問題が示すように、AI活用は便利さと費用が直結します。部署別・用途別に利用量を可視化し、高性能モデルを使う業務と軽量モデルで十分な業務を分ける必要があります。

第二は **データ連携の設計** です。メルカリのApps in ChatGPT、Woodstock MCP、Figmaのコードレイヤー、Mistral OCR 4はいずれも、AIが外部サービスや社内データに接続されることで価値を出す事例です。

第三は **権限と監査** です。AIエージェントが作業を実行するほど、どの情報を読めるか、何を変更できるか、誰が承認するか、実行ログをどう残すかを設計しなければなりません。

第四は **教育と導入体制** です。Samsungの全社展開やAWS Summit Japanの盛り上がりは、AIを一部の専門家だけでなく、全社員が使う段階に来たことを示します。全社展開では、安全な利用環境、業務別テンプレート、レビュー手順、社内相談窓口、効果測定をセットにする必要があります。

## まとめ：2026年6月24〜25日のAIニュースが示す3つの変化

第一の変化は、 **AIの競争軸が推論コストへ移った** ことです。OpenAIのJalapeño、企業のAIトークン予算管理、OrcaRouterのモデルルーティングは、AIを広く使うほどコスト最適化が重要になることを示します。

第二の変化は、 **AIが業務と消費者サービスの入口になった** ことです。Samsungの全社展開、FigmaのAI機能、メルカリのApps in ChatGPT、ロレアルの試着機能、Google Home Speakerは、AIが専門ツールや検索窓を超えて、社員や消費者の日常動作に入り込む流れを示します。

第三の変化は、 **日本でもAI実装の選択肢が具体化した** ことです。富士通PHOTON、Devinの国内急伸、Mistral OCR 4、AWS Summit Japan、Woodstock MCP、CREATANT投資、WorkatoとのAIエージェントデモは、国内企業がAIを業務、開発、金融、製造、文書処理へ広げる段階に入ったことを示します。
