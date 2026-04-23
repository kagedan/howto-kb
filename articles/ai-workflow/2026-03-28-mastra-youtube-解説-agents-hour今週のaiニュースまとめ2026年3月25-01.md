---
id: "2026-03-28-mastra-youtube-解説-agents-hour今週のaiニュースまとめ2026年3月25-01"
title: "[Mastra YouTube 解説] Agents Hour：今週のAIニュースまとめ（2026年3月25日）"
url: "https://zenn.dev/shiromizuj/articles/9ac4c2824fc0c1"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式YouTubeチャンネル](https://www.youtube.com/@mastra-ai)にアップされた動画を速報ベースでお伝えします。ただの文字起こしではなく、扱われているトピックの抽出と、トピックごとの要約をしています。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra YouTube動画 速報解説一覧](https://zenn.dev/shiromizuj/articles/8d6e4fd86631e9)

---

## 動画情報

<https://youtu.be/YPK6IG0zaY8>

## 概要

MastraチームによるAIニュース週次ポッドキャスト「Agents Hour」。エンジニアのトークン消費目標、OpenAIによるAstral買収、Cursor Composer 2とKimi K2.5の騒動、Anthropicのチャンネル機能やコンピューター操作機能、Stripe・Cloudflareのエージェント向け新機能、LiteLLMサプライチェーン攻撃など、多岐にわたるAI業界ニュースを取り上げています。

## 要点

1. NvidiaのジェンスンCEOが「50万ドルエンジニアは少なくとも25万ドル分のトークンを消費すべき」と発言
2. OpenAIがPythonツール（UV、ruff）のメーカーAstralを買収し、Codexチームへ
3. Cursor Composer 2がKimi K2.5を使用していたことが発覚、その後Kimiが正式なパートナーシップと声明
4. AnthropicがClaude CodeにChannels機能を追加（Telegram/Discord対応MCPを通じてセッション制御）
5. Claudeのコンピューター操作機能がMac OSで公開、関連ツイートが5200万ビュー
6. StripeがMPP（Machine Payments Protocol）をリリース。ACPとの使い分けはショッピング（ACP）vs APIサービス支払い（MPP）
7. Cloudflareが動的ワーカーを発表、従来コンテナの100倍速いAI生成コードの安全実行
8. LiteLLMにサプライチェーン攻撃、特定バージョンが環境変数をリモートサーバーへ送信
9. Morph Flash CompactがコンテキストをMastraのObservational Memoryへ応用できないか実験中
10. ターミナルUIがAIの最終インターフェースにはならないと予測。Channels（Slack/Discord/Telegram）が本命

## 詳細

### Jensen HuangのトークンROI発言

NvidiaのCEOジェンスン・フアンがAll-Inポッドキャストで「50万ドルのエンジニアが25万ドル分のトークンを消費していないなら何かがおかしい」と発言。これはNvidiaのビジネス利益とも一致しているが、エンジニアがAIにどれだけ投資すべきかのベンチマークとして注目を集めた。

### OpenAI Astral買収

UVやruffなどPythonツールキットで知られるAstralをOpenAIが買収し、Codexチームに加入。AnthropicがBunを買収してTypeScriptエコシステムを確保したのに対し、OpenAIはPythonエコシステムを押さえるとも読み取れる。

### Cursor Composer 2 + Kimi K2.5の騒動

Cursor Composer 2のベースURLを調べた人が「実態はKimi K2.5のRL版」と指摘。ライセンスのアトリビューション問題が浮上したが、Kimiが「FireworksHQ経由の正式商業パートナーシップの一環」と声明を出して決着。事前協議があったかどうかは不明で、コミュニティの推測を呼んだ。

### Anthropicのシッピング攻勢

* **Claude Code Channels**: TelegramやDiscordのMCPを経由してClaude Codeセッションをリモート制御
* **Dispatch**: コンピューターで作業を走らせたまま外出先のスマートフォンから指示・確認できるリサーチプレビュー機能
* **コンピューター操作**: Mac OSでClaudeがアプリを操作できるようになり、関連ツイートが5200万ビュー。スプレッドシートなどのよく使われるアプリには効果的だが、PhotoshopやFigmaなど複雑なアプリでの性能は未知数
* **スキル活用ブログ**: Anthropic内部でのスキル活用方法を詳述した記事が公開。スキルを丁寧に整備すれば大きな効果が得られるという知見

### Claude Code + Claude Maxプラン問題

Open Code 1.3がClaude MaxプラグインをAnthropicの法的圧力により削除。Anthropicは「サポートはしないがバンもしない」という微妙なスタンス。T3 ChatのTheoは同様の手法でAnthropic製モデルをT3 Chatに追加して気にしていない。Anthropicはオープンソースモデルをリリースしたことがない唯一の大手モデル企業でもある。

### エージェント決済とAuth

* **Stripe MPP（Machine Payments Protocol）**: Tempoとの連携でAPIサービス支払い向けエージェントプロトコルをリリース。既存のACP（ショッピング向け）との使い分けが必要
* **Better OAuth**: エージェント認証（Agent Auth）のオープン標準。エージェントを人間と同じように認証すべきか、固有のメカニズムを持つべきかという問いへの答えを提示

### Cloudflare Dynamic Workers

AI生成コードを安全な軽量アイソレートで実行する仕組み。従来コンテナの100倍速いとされ、Mastraも今後このCloudflareサンドボックスを活用する予定。

### 自律メンテナンスとSRE

Rampが自己メンテナンス型のスプレッドシートをエージェントで構築。本番環境を監視し、アラートをトリアージして修正PRを自動生成（コードのマージは人間がレビュー）。SREのオンコール業務にドメイン知識を持ったエージェントを組み込む動きが加速している。

### コーディングベンチマーク批判 (ESO lang bench)

フロンティアLLMは標準ベンチマークで85〜95%を出すが、記憶できない言語で同等の問題を出すと0〜11%まで激減。これはモデルがベンチマークを記憶しているだけで真の推論能力ではないという批判。ただし言語固有の訓練不足という反論もある。

### その他クイックヒット

| トピック | 概要 |
| --- | --- |
| **GPT-5.4 Mini** | コーディング・コンピューター操作向けに最適化、GPT-4o Miniの2倍高速 |
| **MiniMax M2.7** | M2.5対比88%勝率、SWEとTerminal Benchで最先端性能 |
| **Morph Flash Compact** | コンテキスト圧縮専用モデル、33,000トークン/秒、200K→50Kを約1.5秒 |
| **Okara.ai CMO** | SEO・ターゲティング・コンテンツライティングを自動化するエージェントサービス |
| **Letta** | メモリプロバイダーからメモリファーストのコーディングエージェントへ転換 |
| **GLM-OCR** | 9億パラメータ、8K解像度・8言語対応のOCRビジョンモデル |
| **LiteLLM サプライチェーン攻撃** | 特定バージョンが環境変数をリモートサーバーへ送信する悪意あるコードを含む。PyPIからは削除済み |
| **Google Stitch** | 自然言語からハイフィデリティデザインを生成するバイブデザインプラットフォーム |
| **Netlify** | Mastra Codeから直接Netlifyプロジェクトを起動できるよう連携 |
| **Langchain OpenSWE** | 内部コーディングエージェント向けオープンソースフレームワーク |

### AIの最終インターフェース論

ホストは「ターミナルがAIの最終インターフェースになることはない」と断言。2年以内にほとんどの人がCLI/ターミナルUIを通じてAIと対話していないと予測。Channels（Slack・Discord・Telegram・Email）での対話が主流になると見ており、Mastraも近日中にChannels対応を追加予定。

## 関連リンク
