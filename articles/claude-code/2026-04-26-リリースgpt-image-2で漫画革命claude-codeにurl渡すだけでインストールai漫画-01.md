---
id: "2026-04-26-リリースgpt-image-2で漫画革命claude-codeにurl渡すだけでインストールai漫画-01"
title: "【リリース】GPT-image-2で漫画革命——Claude CodeにURL渡すだけでインストール、AI漫画生成ツール「AMG」公開"
url: "https://note.com/muutan_ai_lab/n/nd5c835419d13"
source: "note"
category: "claude-code"
tags: ["claude-code", "API", "note"]
date_published: "2026-04-26"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

2026年4月、OpenAIが投入した最新画像モデル GPT-image-2 が、漫画生成の景色を完全に塗り替えた。日本語テキストの誤字ゼロ、縦書き吹き出し維持、画風統合、見開きクライマックスまで——一年前まで「AIには無理」とされていた領域を、素の能力で踏破してきた。

そして、その GPT-image-2 をフル活用するためのパイプラインを、自作の AI 漫画生成ツール AMG (Auto Manga Generator) として正式公開した。

GitHub: https://github.com/ranran747/amg

インストールは「Claude Code に URL を渡すだけ」

AMG は git clone も pip install も手で叩かなくていい。手順はこれだけ。

1. Claude Desktop をインストール (claude.ai/download)
2. 2. ターミナルから claude を起動して Claude Code に入る
3. 3. Claude Code に「<https://github.com/ranran747/amg> を README どおりにインストールして、最初のサンプルまで動かしてくれ」と日本語で投げる
4. 4. Claude Code が clone・依存解決・.env 雛形作成・サンプル世界観での1ページ生成まで全部やってくれる

あなたが手で打つのは OPENAI\_API\_KEY を .env に入れる、その1行だけ。Claude Code 自身が自然言語でツールを生やす形なので、Python や Node の知識ゼロでも動く。「Claude Code に GitHub URL を渡すだけで AI ツールがインストールできる時代」を、AMG はその設計前提で組んである。

![](https://assets.st-note.com/img/1777164648-0o4ybc5JV1iWeP2jCMAhFl8N.png?width=1200)

![](https://assets.st-note.com/img/1777164654-W8Sa6UQN2CjEwZ4ihmsgIY9J.png?width=1200)

![](https://assets.st-note.com/img/1777164657-IOyRKJUqup4fkMSBexd1VYTr.png?width=1200)

なぜ今 GPT-image-2 なのか——「漫画はAIには無理」の最後の砦が崩れた

2026-04-21 公開の GPT-image-2 は、漫画用途で見ると前モデルから次のレベルに飛んでいる。

1. 日本語テキスト誤字ゼロ (今回検証範囲)
2. medium / high 品質で出した9コマ＋カラー版、すべて文字化け・謎漢字・崩れナシ。「文字精度のために high を選ぶ」必要がない。これは medium が ¥10/ページで本番運用に乗ることを意味する。

1. 縦書き吹き出しを構図ごと維持
2. コマ割り内に縦書きセリフを配置しても、上下の読み順が破綻しない。これが崩れると漫画にならないので最重要。

1. 画風統合 (劇画系 ⇄ マスコット系) が素で通る
2. 別系統の絵柄を同一ページに同居させても破綻しない。

1. 擬音 (オノマトペ) のフォントと筆致を出し分ける
2. 「ゴゴゴゴ」「ドォォンッ」「ぽんっ」「キリッ」を、それぞれ別フォントの別筆致で配置してくる。これは編集者がレタリング指示を入れる作業相当。

1. カラーと B&W が同コスト・同パイプライン
2. medium で B&W ¥10、フルカラー Webtoon も ¥10。色指定をプロンプトに足すだけで、日本漫画とWebtoon両形式が1本のパイプラインで回る。

要するに、2025年末まで「漫画はAIには無理」とされていた最後の砦——日本語、縦書き、画風統合、擬音、見開き——が GPT-image-2 一発で全部抜けた。AMG はそれを作品制作フローに乗せるためのラッパーだ。

AMG とは何か

AMG (Auto Manga Generator) は、GPT-image-2 を中核に据えた漫画1ページ自動生成パイプライン。コア責務はシンプルに3つに絞ってある。

* Director: 起承転結 → コマ割り → 各コマのカメラ/構図/セリフ分割を生成
* - CFKV (Character Fixed Key Vector): キャラクター一貫性を保つためのプロンプト固定層
* - Renderer: GPT-image-2 への投げ方・参照画像の渡し方・品質階層 (low/medium/high) の切り替え

YAML テンプレ駆動で、コマ割り・見開き・カメラ語彙はすべて差し替え可能。コア (TypeScript / Python) のロジック変更ナシで、表現の幅をプロンプト側で広げられる設計にしてある。

コア性能の検証ログ (2本サンプル抜粋)

実機で4本通したうち、特に指標になった2本を貼っておく。

検証1: 鳥山風カラー扉絵 (スーパーサイヤ人系)。筋肉の陰影、毛並みのハッチング、擬音「ゴゴゴゴ」の筆致、ひび割れエフェクト。商業単行本のカラー扉絵水準。

![](https://assets.st-note.com/img/1777164372-NcjrWCEl41kMInywhFU7tSZK.png?width=1200)

検証2: 8コマ料理実況 (パフェ)。8コマの読み順が完全成立、擬音「わくわく/キリッ/ぽんっ/くるくる/トンッ/わぁ〜っ/じゃッ」がそれぞれフォントを変えて配置。最後の大ゴマ (パフェ完成+ドヤ顔) が決めゴマとして機能。

![](https://assets.st-note.com/img/1777164381-y08dmQEBtaOSCoTKjhqrMzvI.png?width=1200)

このほかに、マスコット狙撃 + 魔法少女の画風統合ページ、ベジータ vs フリーザの見開きクライマックスもクリア済み。コア性能は商業誌級まで届くことが確定している。

実機コストマトリクス (検証済み)

同じ8コマ1ページを low / medium / high で出し分けて実測した。

| 用途                                | 推奨    | 料金   |  
|-------------------------------------|---------|--------|  
| ドラフト確認・背景コマ限定          | low     | ¥4     |  
| 通常ページ生成 (B&W / カラー両対応) | medium  | ¥10    |  
| 表紙・決めゴマ・見開き              | high    | ¥28    |

low (¥4): 8コマ揃う、縦書き吹き出し維持、擬音も読める。線がラフで顔の描き込みは浅い。ドラフト用。

![](https://assets.st-note.com/img/1777164400-2onVUIYl7kijRTFh3EPfcDgL.png?width=1200)

medium (¥10): 商業品質。決めゴマの炎・歯・鱗・請求書「100,000G」までクッキリ読める。本番ページ生成の標準。

![](https://assets.st-note.com/img/1777164408-2ICP5JMKvL4Newdn1iEprhAW.png?width=1200)

high (¥28): 線がさらにクリスプ、背景密度+1段。表紙・決めゴマ・見開き専用に温存。

![](https://assets.st-note.com/img/1777164415-yl7JvSCTEsMZLpBHaWt0Acw3.png?width=1200)

1話30ページ想定の原価試算:

* medium のみ: ¥300
* - 決めゴマ5枚を high に切替: ¥390
* - 全部 high: ¥840

ココナラ等で「漫画化サービス1ページ ¥3,000」が現状相場。原価 ¥10 で粗利率 99.7% という数字が出てしまう。コスト構造の根本書き換えが起きている。

カラー対応もコスト同額

medium の「白黒」と「カラー」を同条件で比較した結果、1ページ料金はどちらも ¥10 で同額。フルカラー、彩度高、虹色エフェクト・湯気・こぼれた液体の色表現すべて成立。

![](https://assets.st-note.com/img/1777164428-qovrlENunC9I1Ti3UgsHXZJW.png?width=1200)

これで「日本漫画 (B&W)」と「Webtoon (縦スクロールカラー)」の両形式が medium 1本で行ける確証が取れた。画像モデル側の特別処理は不要、プロンプトに色指定を入れるだけ。

5分で始める AMG クイックスタート

繰り返すが、Claude Code を入れているなら手動コマンドは1つも要らない。

1. Claude Desktop インストール → ターミナルで claude
2. 2. 「<https://github.com/ranran747/amg> をインストールしてサンプル動かして」と Claude Code に投げる
3. 3. Claude Code が clone・npm install・.env 雛形・サンプル実行まで自走
4. 4. .env に OPENAI\_API\_KEY を入れて、もう一度サンプルを叩いてもらう

これで examples/lumina\_alchemist の基準ページが output/ に出る。GPT-image-2 への課金は medium 設定で ¥10 前後 (1ページ)。

オリジナル世界観を作るなら:

* examples/\_template/ をコピーして自分の世界観 YAML を書く
* - characters/\*.yaml に主要キャラを定義
* - scenarios/\*.md にシナリオを書いて投入
* - 「medium で生成」「決めゴマだけ high」と Claude Code に指示すれば品質階層も自動で振り分けてくれる

low → medium → high の品質切替は --quality フラグだけ。コードは触らなくていい。

これから先のロードマップ

ここから先は、ソフトウェア工学の仕事ではなく、プロンプトエンジニアリングと作品制作の仕事になる。AMG コアにはほぼ手を入れない。

* sp\_camera\_vocab 拡張 (8語 → 20+語): カメラ語彙をプロンプト層で拡張
* - director\_dialogue\_style 投入: 口調ブレ抑制、世界観統合効果
* - 見開きテンプレ panels\_2\_spread.yaml: act=climax 時のみ Director に選択させる
* - three\_page\_short\_guidance: 3ページ短編フォーマット最適化
* - 量産フェーズ: 1日1〜3本、logs/cost.jsonl で単価監視

これらは全部 YAML / プロンプト側の追記で完結する。コアの再設計は不要。

個人副業視点での意味

GPT-image-2 + AMG の組み合わせで、漫画作画工程のコスト構造が以下のように変わる。

* 1話 (30ページ) を ¥300〜¥400 で生成、所要時間30分以内
* - 1日5話分の生成余力 → 月150話、新作投入頻度は人間作家比 30倍以上
* - カラーWebtoon と B&W 日本漫画の両ライン同時運用
* - ココナラ漫画化サービス (1P ¥3,000) と比較して粗利率 99.7%

ボトルネックは生成側ではなく、企画・販売・配信ルートに完全に移った。先行者利益のウィンドウは、プロンプト最適化サイクルを最初に回し切った人と、配信チャネルを早く確保した人に開く。

まとめ

GPT-image-2 のリリースで、漫画生成は「実用」を通り越して「商業誌級まで届く」フェーズに入った。AMG はその力を作品制作フローに乗せるための、最小構成のオープンソース実装だ。Claude Code に GitHub URL を渡すだけで動き出す。

* ツール: https://github.com/ranran747/amg
* - インストール: Claude Code に URL を投げるだけ
* - コア生成原価: ¥10/ページ (medium、B&W / カラー両対応)
* - 商業誌級は high (¥28) で温存、決めゴマと表紙だけに使えば十分
* - ソフトウェア側はもう触らない、ここからはプロンプトと作品の勝負

クローン (に相当する Claude Code 一言) で examples を1ページ出してみてほしい。その1ページが出た瞬間に、漫画制作のコスト感覚が永久に書き換わる。

[#AI](https://note.com/hashtag/AI) [#AI漫画](https://note.com/hashtag/AI%E6%BC%AB%E7%94%BB) [#GPTimage2](https://note.com/hashtag/GPTimage2) [#画像生成](https://note.com/hashtag/%E7%94%BB%E5%83%8F%E7%94%9F%E6%88%90) [#Claude](https://note.com/hashtag/Claude) [#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#AI副業](https://note.com/hashtag/AI%E5%89%AF%E6%A5%AD) [#漫画制作](https://note.com/hashtag/%E6%BC%AB%E7%94%BB%E5%88%B6%E4%BD%9C) [#自動化](https://note.com/hashtag/%E8%87%AA%E5%8B%95%E5%8C%96) [#コンテンツ生成](https://note.com/hashtag/%E3%82%B3%E3%83%B3%E3%83%86%E3%83%B3%E3%83%84%E7%94%9F%E6%88%90) [#個人開発](https://note.com/hashtag/%E5%80%8B%E4%BA%BA%E9%96%8B%E7%99%BA) [#OpenAI](https://note.com/hashtag/OpenAI) [#オープンソース](https://note.com/hashtag/%E3%82%AA%E3%83%BC%E3%83%97%E3%83%B3%E3%82%BD%E3%83%BC%E3%82%B9)
