---
id: "2026-05-01-lit-forge-mcp-v01-v04-進化記録-dev-utility-10-ツールから金融特-01"
title: "lit-forge-mcp v0.1 → v0.4 進化記録 — dev utility 10 ツールから金融特化 12 ツールへ"
url: "https://zenn.dev/nob193/articles/38b3c50b240f86"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "JavaScript", "zenn"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* 2026-04-25 〜 05-01 の **6 日間** で `lit-forge-mcp` は v0.1.0 → v0.4.0 まで進化した
* v0.1.x: lit-forge.com の **dev utility 10 個（JSON 整形・正規表現・JWT デコード等）** を MCP 化したもの
* v0.2.0: AdSense 不合格を機に **金融特化に 180 度ピボット**。dev utility 全廃、NISA / iDeCo シミュレーター系 4 ツールに刷新
* v0.3.0: 「毎朝の市況チェック」系 3 ツール追加。**初の HTTP fetch 解禁**（Yahoo Finance）
* v0.4.0: 市況俯瞰系 5 ツール追加、銘柄 9 → **28** まで拡大、計 **12 ツール**
* 学び: MCP の参入障壁は実装より **「配布・発見・所有権主張」** のほうが高い。Glama claim や公式 Registry の namespace 仕様、awesome-mcp-servers の前提条件など、登録経路ごとに固有のハマりどころがある

---

## 1. 背景：なぜ MCP サーバーを作ったか

[lit-forge.com](https://lit-forge.com) は元々「PC のみ・コストゼロで Web ツールを量産して広告収益化する」方針で 47 個の Web ツールを揃えていた個人サイトでした。本記事執筆時点では金融・個人投資家特化にピボット済みですが、ピボット直前の時点で MCP サーバー化の検討が始まっています。

**動機は集客拡大の最優先 2 施策のうちの 1 つ**として MCP サーバー化を選んだことでした。具体的には:

* **Google 検索以外の流入経路を開く**: 個人サイトは SEO 競争で大手に勝ちづらい。AI クライアント (Claude Desktop / Code / Cursor) のツール一覧から発見してもらうほうが、レッドオーシャンを避けられる
* **AI クライアント側からのブランド露出**: ユーザーが「JSON 整形して」と言ったときに `lit-forge` ブランドのツールが選ばれることで、サイト本体への認知が広がる

実装方針として、最初は **純関数だけ MCP 化する** ことを選びました。

> **純関数だけにした理由**: npm publish 後の運用コストをゼロに保つため。外部 API を叩かない、状態を持たない、ローカル PC で完結する。これなら無料 npm 配布だけでサーバー保守が一切不要になる。

この判断は v0.3.0 で覆ることになります（詳細は後述）が、最初の 6 日間はこの設計原則が芯にありました。

---

## 2. v0.1.x：dev utility 10 ツール時代

**2026-04-25**、初版 v0.1.0 を npm 公開。**6fb7458** で v0.1.1 が同日リリース。**40541a9** で v0.1.2 として公式 MCP Registry に登録。すべて 1 日で完了したスタートでした。

提供ツールは以下の 10 種:

| ツール | 機能 |
| --- | --- |
| `format_json` | JSON 整形（pretty） / 圧縮（minify） |
| `test_regex` | 正規表現マッチ（JavaScript 互換、フラグ指定可、名前付きグループ対応） |
| `decode_jwt` | JWT を Header / Payload / Signature に分解（exp/nbf/iat の人間可読化） |
| `convert_base64` | Base64 エンコード / デコード（UTF-8 / URL-safe 対応） |
| `convert_url` | URL パーセントエンコード / デコード |
| `generate_hash` | MD5 / SHA-1 / SHA-256 / SHA-384 / SHA-512（hex / base64 出力） |
| `generate_uuid` | UUID v4 / v7 を最大 100 件まで一括生成 |
| `convert_timestamp` | Unix 時刻 ⇔ ISO 8601 日時（秒/ミリ秒切替） |
| `convert_yaml_json` | YAML ⇔ JSON 相互変換 |
| `describe_cron` | cron 式を人間可読化 + 次回実行時刻を計算 |

すべて純関数で、外部 API を叩かない。Claude Desktop の設定 JSON に `npx -y lit-forge-mcp` 一行追加すれば即動作する設計でした。

サイト側に同等機能の Web 版がすでに実装済みだったので、最初は「ロジックを共通化して薄いアダプタだけ MCP 側に書く」案を検討しました。が、結論として **再利用せずに Node native で書き直しました**。

理由は単純で、Web 版が **ブラウザ依存**だったからです:

```
// Web 版 (lit-forge/app/lib) の Base64 実装
const encoded = btoa(unescape(encodeURIComponent(input)));

// MCP 版 (lit-forge-mcp/src/tools) の Base64 実装
const encoded = Buffer.from(input, "utf-8").toString("base64");
```

`btoa` / `atob` / `unescape` / Web Crypto API の一部は Node ランタイムでは動かない（または挙動が違う）。共通化を諦めて二重実装を選びました。**コードの DRY 性は犠牲になりますが、両環境のネイティブ機能を素直に使える**ほうが長期的にバグが少ない、という判断です。

### npm 公開時の地味なハマり

* **2FA + OTP**: npm の `Authorization and writes` モードに 2FA を設定していると、`npm publish` のたびに OTP が要求される（`npm publish --otp=XXXXXX`）。最初は `~/.npmrc` にトークンを書いて運用しようとしたが、漏洩リスクを考えて毎回 OTP 入力する運用に落ち着いた
* **`npm pkg fix` 警告**: package.json の `repository.directory` がないと警告が出る。v0.1.1 で修正
* **公式 MCP Registry の namespace**: 登録時の `name` フィールドは **`io.github.<org>/<repo>`** 形式が必須。`io.github.noblabs/lit-forge-mcp` で登録した

---

## 3. v0.2.0：金融特化への 180 度ピボット

**2026-04-26**、v0.1.2 公開の翌日。lit-forge.com 本体に Google AdSense から \*\*「有用性の低いコンテンツ」\*\*として不合格通知が届きました。

> 47 ツール体制で雑多すぎ、各ツールが浅い、というのが原因の仮説でした。

ここで経営判断として **金融・個人投資家特化** にサイト全体をピボットすることに。MCP サーバーもこの方針転換に連動して **dev utility 10 ツールを全廃** し、つみたて NISA / iDeCo / 退職資金プランナー系の **4 ツール** に刷新しました（commit `47b8548`）。

新ツール 4 種:

| ツール | 機能 |
| --- | --- |
| `simulate_nisa` | 月次積立額・想定年利・年数から月次複利で評価額・運用益・年次推移を試算 |
| `plan_retirement` | 年齢・現在貯蓄・収入・希望生活費・リスク許容度・年金から、楽観/現実/悲観 3 シナリオで老後資金の充足度を診断 + 必要月額の自動逆算 |
| `calculate_required_monthly` | 目標金額・現在貯蓄・年利・年数から、達成に必要な毎月の積立額を逆算 |
| `calculate_compound_interest` | 元本（一括）と月次積立を月次複利で評価する汎用複利計算 |

サイト側 dev 10 ツールも撤去（v1.36.0、commit `6e22bff`）。**MCP もサイトも完全に金融特化** に揃えました。

### ピボットで一番痛かったのは「**周辺資産の陳腐化**」

技術的なツール差し替え自体は半日もかからない作業でしたが、**周辺で進めていた配布・宣伝活動の棚卸し** のほうが面倒でした:

* **awesome-mcp-servers PR #5355** が v0.1.x 内容で submission 中だった → close + コメントで pivot 経緯を説明 → **新 PR #5428** を `💰 Finance & Fintech` セクションに再提出
* **mcpservers.org の掲載審査** が v0.1.x 内容で進行中 → 掲載は承認されたが、内容は古いまま（後で別途修正依頼）
* **Qiita / Zenn のクロスポスト記事** が v0.1.x 内容で公開済み → 旧記事として残置（本記事はその陳腐化の答え）

> **学び**: ピボットを決める瞬間に「**この方向性に依存している外部投稿・申請を全部リストアップしたか**」を問うべき。私は問い忘れて、後追いで全部対応する羽目になった。

---

## 4. v0.3.0：毎朝の市況チェックと HTTP fetch 解禁

ここから 4 日空きます。**2026-05-01**、v0.3.0 リリース（commit `c8dc914`）。

同日、サイト側にも `/today`（毎朝の市況チェック）ページを v1.50.0 で新設。**サイトと MCP サーバーで同等の市況情報を取得できる**ようにペア設計しました。

新ツール 3 種:

| ツール | 機能 |
| --- | --- |
| `get_market_snapshot` | 9 指標（USD/JPY、日経、S&P 500、米10年金利、金、原油、VIX、NY ダウ、NASDAQ）の現在値・前日比を一括取得 |
| `get_economic_events_today` | 当日 / 今週の経済イベント（FOMC・日銀・雇用統計・CPI・GDP 等、半年分の手動キュレーション） |
| `get_quote` | 任意の Yahoo Finance ティッカー（AAPL / ^DJI / BTC-USD / GBPJPY=X 等）の現在値・前日比 |

### 純関数原則を破った瞬間

このリリースで MCP サーバーは **初めてインターネットに出る**ことになりました:

```
// get-market-snapshot.ts の核心部分（簡略化）
const response = await fetch(
  `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${symbols}`,
  { headers: { "User-Agent": "Mozilla/5.0 ..." } }
);
const data = await response.json();
```

「サーバー保守ゼロ」の原則に対するちょっとした裏切りですが、ローカル PC からの fetch なので **サーバーホスティングは依然不要**。Yahoo Finance も無料で使える（公式 API ではないが、慣行的にスクレイピング扱いで OK）。

ここで自分の中の MCP 観が一段更新されました:

> **stdio + 純関数だけが美徳と思いがちだったが、実用上は外部データ取得が必須**。MCP の真の価値は「**AI クライアントから自然言語で具体的なデータが引ける**」ことで、純関数の電卓だけだと使い道が狭い。

---

## 5. v0.4.0：市況俯瞰の網羅性強化

v0.3.0 と同じ **2026-05-01** に v0.4.0 をリリース（commit `0b5bf99`）。同日中に 2 メジャーバージョン進めた格好です。

追加した分析系 5 ツール:

| ツール | 機能 |
| --- | --- |
| `get_market_thermometer` | VIX / S&P 500 / 米10年金利 / ドル指数を合成した 0-100 のリスクオン/オフスコア + 過去 30 営業日の推移 |
| `get_performance_ranking` | 28 銘柄を 1d / 1w / 1m でソートした上位/下位 N 件 |
| `get_yield_spread` | 米 10 年-5 年イールドスプレッド（順イールド / 逆イールド + 前日比 bp） |
| `get_market_sessions` | 東京 / 上海 / ロンドン / NY の現在の取引時間ステータス |
| `get_sector_heatmap` | 米株セクター ETF 11 種（XLK / XLF / XLV / XLE 等）の前日比ヒートマップ |

加えて、**追跡銘柄を 9 → 28 銘柄まで拡大**:

* 為替: USD/JPY、EUR/JPY、GBP/JPY、AUD/JPY、EUR/USD、CHF/JPY、ドル指数（DXY）
* 日本: 日経平均、TOPIX
* 米国: NY ダウ、S&P 500、NASDAQ、VIX、NYSE FANG+、SOX
* 欧州: DAX、FTSE 100
* アジア新興: 上海総合、ハンセン、KOSPI、SENSEX
* 金利: 米10年、米5年
* 商品: 金、原油、銅
* 暗号資産: BTC、ETH

計 **12 ツール**（プランナー 4 + 市況 3 + 分析 5）の体制が整いました。

### 使用例：朝の市況把握ルーティン

ある朝、Claude Desktop に「今日の朝のマーケット要約して」と話しかけたときの想定的な対話:

```
[ユーザー] 今のマーケット温度計は？過去 30 日と比べて高い？低い？
[Claude]   get_market_thermometer 呼びました。スコア 58.7（neutral、ややリスクオン寄り）。
           過去 30 日平均は 50.3 なので約 8 ポイント高めです。

[ユーザー] 今週の経済イベントで ★★★ のものは？
[Claude]   get_economic_events_today で今週分を取得。FOMC 議事録（火）、米 CPI（水）、
           ECB 金利決定（木）、米雇用統計（金）の 4 件です。

[ユーザー] イールドスプレッドは順？逆？
[Claude]   get_yield_spread で +35bp（順イールド）。前日比 +2bp 拡大。
           リセッション警戒域からは離れた水準です。
```

複数ツールを連携した「**朝 5 分で市況把握**」ルーティンが MCP 経由で組めるようになりました。

---

## 6. 配布・発見・所有権主張のハマりどころ

ここからが本記事の主旨です。**MCP サーバーは作るより「**見つけてもらう**」のが難しい**。経路ごとに固有の罠がありました。

### 6.1 公式 MCP Registry — namespace の仕様と org membership の罠

公式 Registry に登録するには `mcp-publisher` CLI を使います:

```
~/.local/bin/mcp-publisher login github
~/.local/bin/mcp-publisher publish
```

ハマりポイント:

* **Namespace は `io.github.<org>/<repo>` 形式が必須**。個人 GitHub アカウントだと `io.github.<username>/<repo>` になる
* **org に属するサーバーを publish する場合、`<org>` メンバーシップを Public に設定する必要がある**。私の `noblabs` org の `nob-owner` メンバーシップは元々 Private だったので、Settings から Public に変更が必要だった（`https://github.com/orgs/noblabs/people` で対象メンバーの行から変更）
* **server.json の description は maxLength: 100**。これを知らずに 200 文字以上書いて publish エラーで初めて気づいた
* **Registry の認証トークンは短時間で expire する**。`login github` → `publish` は連続で実行するのが安全

Glama は MCP サーバーを GitHub から自動索引している営利第三者ディレクトリです。

最初に気づいたとき、私のサーバーは **既に Glama に掲載されていました**。ただし v0.1.x 時代の表記のまま、**所有権が unclaimed** な状態。

awesome-mcp-servers のメンテナー (Frank Fiegel、Glama 運営者でもある) からの PR レビューコメントで「**Glama 上で所有者主張してくれればマージする**」と言われ、Claim フローに乗りました。

org-owned サーバーの Claim は **`glama.json` をリポジトリ root に置く**必要があります:

```
{
  "$schema": "https://glama.ai/mcp/schemas/server.json",
  "maintainers": ["nob-owner"]
}
```

これを commit して push すると、Glama の Claim ボタンから GitHub OAuth → 検証 → Admin パネルアクセス可能になります。

claim 後の追加作業:

* **Categories を `Developer Tools` から `Finance` へ変更**（Glama が v0.1.x 時代の自動分類を保持していた）
* **Description を v0.4.0 内容にリライト**（Glama の Admin パネルから編集）
* \*\*Repository サブタブの「Sync Server」\*\*を手動実行 → README が最新コミット版に再生成

### 6.3 awesome-mcp-servers — Glama Claim が前提条件

awesome-mcp-servers (punkpeye/awesome-mcp-servers) は MCP サーバー一覧の curated list です。PR を出すこと自体は簡単ですが:

* **「Glama 上で Claim していること」がメンテナーの暗黙の前提条件**
* 旧 PR #5355 (v0.1.x 内容) は close、新 PR #5428 (v0.4.0 / Finance & Fintech セクション) を提出
* メンテナーから「Glama Claim してください」コメント → Claim 完了後にコメントで通知 → マージ待ち

### 6.4 mcpservers.org — self-service 更新機能なし

mcpservers.org は別の第三者ディレクトリ。submission フォームから掲載申請して承認をもらう運用ですが、**掲載後の self-service 更新機能がありません**。

私の場合、v0.1.x 時代に submission した内容のまま掲載が承認され、v0.2.0 / v0.3.0 / v0.4.0 への更新は **`contact@mcpservers.org` にメールで再スクレイピング依頼** が必要でした。

> **設計の意図 (推測)**: キュレーション制御 × 収益設計（Premium Submit $39 が裏メニュー）× ボリューム小で運用回せている。Glama のような OAuth + 検証フローを実装するコストを払うほどのスケールではない、という判断と思われる。

これは MCP 固有ではないが、副次的な落とし穴。

`noblabs` org への移行作業中に過去の commit author を rewrite する必要があり、`git filter-branch` + `git push -f` で履歴を書き換えました。技術的には完了しているはずなのに、**GitHub の Contributors widget が旧 username をキャッシュし続ける**現象に遭遇。

解決策は **リポジトリを一度削除 → 再作成**:

```
# delete_repo スコープが必要
gh auth refresh -h github.com -s delete_repo
gh repo delete noblabs/lit-forge-mcp --yes
gh repo create noblabs/lit-forge-mcp --public --source . --push
```

これで Contributors widget が完全クリーンに再生成されました。**force-push では消えないキャッシュがある**、というのは GitHub 運用上の地味な常識として覚えておくと良いです。

---

## 7. 設計判断と運用学び

### 7.1 純関数原則は条件付きで維持

v0.3.0 で HTTP fetch を解禁しましたが、引き続き **「ローカル PC で完結・サーバーホスティング不要」** は守っています。MCP サーバーを「ホスト型サービス」にすると運用コストと可用性責任が一気に重くなる。**ホストレスなまま外部 API は叩く**、というスタンスがちょうど良いバランスでした。

サイト側 (Web) と MCP 側 (Node) で同じロジック（NISA 月次複利計算など）が重複実装されています。一見もったいないですが、共通化を試みた結果:

* ブラウザ依存 (`btoa` / Web Crypto / `unescape`) と Node native (`Buffer` / `node:crypto`) の差を吸収する抽象を作るコスト
* それを 2 つの実行環境でテスト維持するコスト
* 軽微な API 改修のたびに両方をデバッグするコスト

これらを総合すると、**「同じ計算ロジックを 2 ヶ所に書く」** ほうが結局は安かったです。共通化が本当に効くのは **3 環境以上** か、**ロジックが複雑で重複コストが計算量に対して大きい場合** に限る、という個人的な目安。

### 7.3 「機能差別化より露出」が MCP の正しい動機

MCP 化したツール 12 種のうち、**MCP 必須なのは実は 3 つくらい**です:

* `get_market_snapshot` — リアルタイムデータ取得は MCP（AI クライアント連携）でこそ価値が出る
* `get_economic_events_today` — 同上
* `get_market_thermometer` — 同上

残りの 9 ツール（NISA シミュレーター系、複利計算、フォーマッター系）は **Web 版で十分**で、MCP 化しても機能差はほぼゼロ。

それでも MCP 化する価値があったのは、**集客上の意味**:

* AI クライアント側のツール一覧から **発見**してもらえる
* ブランド名 (`lit-forge`) の **露出**が増える
* 「MCP サーバーを公開しているプロジェクト」という **技術的信頼性**のシグナル

> **MCP 化は機能差別化より露出が本命**。これは v0.4.0 まで来て初めて言語化できた仮説で、これから MCP サーバーを作る人には先に伝えたい。

### 7.4 クロスポスト記事の陳腐化問題（本記事執筆の動機）

v0.1.x 時代に Qiita / Zenn にクロスポストした「自家製 MCP サーバーで Web ツール集を Claude から呼べるようにした完全レシピ」が、ピボット後に **完全に陳腐化** しました。

旧記事を更新するか、新記事で上書きするか、悩んだ末に **新記事 (本記事) で上書き戦略** を取ることに。理由:

* 旧記事を編集すると、当時の文脈や公開時の反応が失われる
* 「進化記録」として両方残しておくほうが、技術記事としての価値が高い
* 個別の媒体（Qiita / Zenn）で旧記事に Pin で「最新版はこちら」リンクを足せば誘導できる

そして **新記事の原本を置く場所** として、専用の `noblabs/blog` リポジトリ（本記事を含むこのリポジトリ）を新設しました。lit-forge.com 側のブログ運営は畳んだ方針なので、独立した中立的な場所に原本を置く形を選んでいます。

---

## 8. 次の展開

直近で検討している拡張:

* **アラート系**: 為替・株価が閾値を超えたら通知（cron 連携 or push）
* **保有銘柄ウォッチ**: ユーザー定義のポートフォリオを継続追跡
* **ニュース要約**: 個別銘柄に紐づくニュースを取得して要約
* **国内銘柄サポート (JPX)**: 米株中心を脱して日本株個別もカバー
* **過去比較系**: 「先月の今日と比べて」「昨年の今日と比べて」型のコマンド

ただし、**機能を追加するほど MCP 経由で呼ぶより Web 版のほうが速い** 領域に入っていく恐れもあるので、追加は慎重に。

---

## まとめ

`lit-forge-mcp` の 6 日間の進化を振り返ると、以下の 3 つの教訓が残りました:

1. **MCP の参入障壁は実装より配布**。ツールを書く時間より、Glama / awesome-mcp-servers / mcpservers.org / 公式 Registry に登録して回る時間のほうが長い
2. **ピボット時は依存資産の棚卸し必須**。外部投稿・申請・他サイトの掲載が「ピボット前提で書かれている」ことを忘れて後追い対応に追われた
3. **MCP 化の本命はブランド露出**。機能差別化を狙うとがっかりするが、AI クライアント側からの発見経路としては効く

技術的な進化記録というより、**個人開発者が MCP エコシステムに参入したときの実録ドキュメント** として読んでいただければ。

---

## リポジトリ・関連リンク
