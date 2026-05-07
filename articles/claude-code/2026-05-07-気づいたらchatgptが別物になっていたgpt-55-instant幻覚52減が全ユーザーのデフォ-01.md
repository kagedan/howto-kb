---
id: "2026-05-07-気づいたらchatgptが別物になっていたgpt-55-instant幻覚52減が全ユーザーのデフォ-01"
title: "気づいたらChatGPTが別物になっていた──GPT-5.5 Instant「幻覚52%減」が全ユーザーのデフォルトに、AnthropicはMuskのGPU 22万枚でClaudeを強化"
url: "https://note.com/kei_tmt/n/n22b7c55682d8"
source: "note"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "OpenAI", "Gemini"]
date_published: "2026-05-07"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

5月5日、あなたが何もしていなくても、ChatGPTのデフォルトモデルは静かに入れ替わっていた。GPT-5.5 Instantへの切り替えは全ユーザーに対して実施済みだ。翌6日、AnthropicはSpaceXのColossus 1データセンター（300MW超・GPU 22万枚以上）との大規模契約を発表し、ClaudeがユーザーのPCを直接操作する「Computer Use」機能を開発者向けに解禁した。AIツールを「使う」という行為の前提が、また一段階変わりつつある。

## この記事でわかること

* ChatGPTのデフォルトが切り替わり、具体的に何がどう変わったか（幻覚率・回答スタイル・HealthBenchスコア）
* AnthropicがなぜMusk傘下のSpaceXと組んだのか、Claude Pro/Maxユーザーへの影響
* Claude CodeのComputer Useとは何か、エンジニアの仕事にどう影響するか

---

## 今日の3行サマリ

* ChatGPTのデフォルトがGPT-5.5 Instantに切り替わり、医療・法律・金融領域での幻覚が52.5%減少
* AnthropicがSpaceX Colossus 1と300MW・GPU 22万枚超の契約を締結、Claude利用制限が緩和へ
* Code w/ Claudeイベント（5/6）でComputer Use解禁・「Dreaming」機能発表──AIが自分の失敗から学ぶ

---

## ChatGPTが「別の脳」になった──GPT-5.5 Instantがデフォルトモデルに

5月5日、OpenAIはGPT-5.5 Instantを全ユーザーのデフォルトモデルに切り替えた。前モデルGPT-5.3 Instantと比べ、高リスク質問（医療・法律・金融）での幻覚件数は52.5%減少し、難解な会話での不正確な主張は37.3%減った。医療ベンチマーク「HealthBench」のスコアは51.4（前モデル49.6）、臨床版では38.4（前モデル32.9）と明確に向上している。

回答スタイルも変化した。絵文字が減り、返答が短く、余計な問い返しが少なくなった。過去の会話・ファイル・Gmailを参照したパーソナライズ回答はPlus/Proユーザー向けにウェブから先行展開する。

**他社との比較：** AnthropicのClaude 3.7 Sonnetが医療・法律系の幻覚抑制でリードしてきたが、GPT-5.5 Instantは「デフォルトモデルの底上げ」という点で影響範囲が桁違いに広い。Claude ProやGemini Ultra Proは有料プランが前提だが、GPT-5.5 InstantはChatGPT無料ユーザーにも届く。

**今日から試せること：** 医療・法律・金融関連の調査にChatGPTを使う場合、GPT-5.5 Instantの精度向上を活かしつつ、「この情報の一次情報源は？」と必ず続けて問うこと。「幻覚52%減」は「幻覚ゼロ」ではない。精度が上がった分だけ、出力をそのまま信じるリスクが逆に見えにくくなる点に注意したい。

---

## ClaudeがあなたのPCのマウスを握る──Computer Use、開発者向けに解禁

「Code w/ Claude」イベント（5月6日・サンフランシスコ）でAnthropicが発表したComputer Use機能は、Claudeが「スクリーンのスクリーンショットを読み取り、ポインタを動かし、クリックし、フォームを入力し、ブラウザを操作する」機能だ。接続セットアップは不要で、Claude ProおよびMaxサブスクライバーのResearch Previewとして提供が始まった。

できることの具体例：

* UIテスト──Webアプリを実際に操作し、レイアウト・フォームの動作を検証
* APIを持たないレガシーシステムとのデータやり取り
* ビジュアルQA──「コードが通る」ではなく「画面上のUIが正しく見える」かを確認
* スクリーン上の情報収集・スクレイピング

ClaudeはActions実行前に毎回ユーザーへの許可を求めるため、完全自律ではない。また、Anthropicは「機密データが表示されている状態での使用は推奨しない」と明示している。

**エンジニア目線での比較：** OpenAI OperatorやMicrosoft Copilot Studio（Computer Use対応）と同カテゴリに入るが、Claude CodeはIDE統合が前提のため「コーディングの延長線上でUIも触れる」点が差別化要因だ。E2Eテストの自動化や、ノーAPIのレガシーツールとの連携コストが大幅に下がる可能性がある。

---

## ライバルMuskのデータセンターでClaudeが動く──Anthropic×SpaceX 300MW契約

5月6日、AnthropicとSpaceXは大規模コンピュート契約を発表した。AnthropicはテネシーのColossus 1データセンターが持つ全容量──300MW超、NVIDIAのGPU 22万枚以上──を今月中に利用可能になる予定だ。

なぜSpaceXか。月次アクティブユーザーの急増でClaude ProおよびMaxのレート制限が問題になっていた。AnthropicはすでにAWS・Google・Microsoft・NVIDIAとコンピュート契約を持つが、それでも需要が供給を上回っていた。Anthropicはこの追加容量が「Claude ProおよびMaxの利用可能性を直接改善する」と明言している。

さらに将来的な「軌道上コンピュート」の協議も含まれており、数ギガワット規模の宇宙空間でのAI処理も視野に入れている。

**他社との比較：** xAIのGrokも同じColossus 1を使っている。Anthropicの参入でSpaceXのデータセンターが「AI業界向けニュートラルインフラ」として確立されつつある。AWSのAmazon BedrockやGoogle Cloudと同様、コンピュートの確保力そのものがAI企業の競争力になってきた。

---

## 「Dreaming」──Claudeが自分の失敗から学ぶ機能が登場

Code w/ Claudeイベントで発表されたClaude Managed Agentsの3機能は、自律エージェントの設計思想を一歩前に進めた。

**Multi-agent orchestration（マルチエージェント統制）：** 複数のClaudeエージェントをフリートとして生成・管理し、複雑なタスクを並列処理する。**Outcomes（アウトカム設定）：** 「何をもって成功とするか」を定義すれば、ClaudeがそのゴールをKPIとして繰り返し実行・改善する。人間のレビューサイクルを最小化できる。

**Dreaming（ドリーミング）：** Claudeが過去のセッションを振り返り、「何をミスしたか」「何を見落としたか」を自律的に分析し次のセッションに活かす機能。AIが自分の失敗ログをもとに動作改善するループが、エージェントレベルで実装された。

**比較：** OpenAIのAgent SDKやGoogle DeepMindの研究と同じ「エージェント自律性向上」の方向だが、「Dreaming」は「セッションをまたいだ自己評価」という点で新しいアーキテクチャだ。長期タスクを任せるエージェントに実装されると、人間のフィードバックループを代替できる。

---

## ウォールストリートをAIで制圧する──$1.5B JVと10の金融エージェント

5月4〜5日にかけて、Anthropicは金融業界への攻勢を本格化させた。Goldman Sachs・Blackstone・Hellman & Friedmanとの$1.5B規模のJV設立を発表。新会社はPE各社のポートフォリオ企業にClaude導入支援を行う。Goldman、Blackstone、H&Fが各$300M、GoldmanがさらにJV向けに$150Mを拠出するほか、Apollo、General Atlantic、Sequoia、GICも参画している。

同時に、金融業界向け専用エージェントを10本リリース。ピッチデック作成・財務諸表レビュー・コンプライアンス審査エスカレーション・保険/資産管理向けワークフローをカバーする。金融業界向け最高位モデル「Claude Opus 4.7」もデビュー。JPMorganChase、Goldman Sachs、Citi、AIG、Visaにはすでに本番導入済みだ。

**比較：** MicrosoftのCopilot for Financeが「Officeの延長線上」でのAI化を狙うのに対し、AnthropicはJV設立によって「AIソフト販売」から「AIサービス会社」への転換を鮮明にした。McKinseyやBoston Consulting Groupが手がけてきた経営変革コンサルの領域に直接踏み込む動きだ。

---

## Google I/O 2026まで12日──Gemini 4の登場で三つ巴が始まる

Googleは5月19日にGoogle I/O 2026を開催する。Gemini 4（「最も高性能なオープンモデル」と評価されているベータ版の正式発表を含む）が中心的な発表になる見込みだ。第8世代TPUも披露予定で、エージェント向けに最適化されたエネルギー効率向上が特徴とされる。

現時点でGemini AI Pro/Ultraサブスクライバー向けにはカスタム練習問題生成・ChromeへのGemini統合（WindowsおよびmacOS）が段階的にロールアウト中だ。

Gemini 4.0が正式リリースされれば、Claude 3.7 SonnetおよびGPT-5.5 Instantとの三つ巴のベンチマーク競争が始まる。Anthropicの「Code w/ Claude」に対するGoogleの直接の回答になる12日間だ。

---

## AIエージェントに「身分証明書」が必要になる──ServiceNow AI Governance

ServiceNowは「Knowledge 2026」で「Autonomous Workforce」プラットフォームを拡張。IT・CRM・セキュリティ・HR・調達・リスク管理の6領域をカバーする専門エージェントを追加した。Gartnerは2026年末までに40%の企業アプリにタスク特化型AIエージェントが組み込まれると予測している。

同時に「プロンプトインジェクション」攻撃が急浮上している。これは悪意ある外部コンテンツがAIエージェントを乗っ取り、ファイル削除やメール送信など不正なアクションを実行させる攻撃だ。ServiceNowはエージェントのID・権限・接続先を一元管理するガバナンスプラットフォームとして差別化を図る。

**IT担当者・エンジニア向けTips：** 社内でAIエージェントを展開している場合、エージェントごとに「どのデータにアクセス可能か」「どのアクションが許可されているか」のポリシーを今すぐ棚卸しすること。エージェントの権限過剰が現時点でのセキュリティリスク最大要因だ。

---

## 明日から変えられる1つのこと

ChatGPTを医療・法律・金融調査に使っているなら、今日からGPT-5.5 Instantの精度向上を活かしつつ「この回答の根拠となった情報源を教えて」と必ず続けて問いかけること。精度が上がった今こそ、出力を無批判に信じるリスクが見えにくくなっている。「幻覚52%減」を「信頼100%」と読み違えないことが、AIを正しく使いこなす唯一の防衛線だ。

---

## 参考リンク

---

## このアカウントについて

このアカウントでは、AI・テクノロジーの最新情報・実践Tips・業界動向を毎日わかりやすく解説しています。次の記事では、Google I/O 2026（5月19日）の発表内容を速報でお届けする予定です。ぜひフォローしてお待ちください。

---

## 関連記事

---

## このアカウントについて

📌 「AIを使いたいけど何から始めれば？」という方へ。  
個人・中小企業向けにAI導入支援をしています → <https://www.kac-ai.jp/>  
気軽にフォロー＆サイトをのぞいてみてください。
