---
id: "2026-05-02-claude-higgsfield-mcpでオリジナル楽曲のpvを作った話-01"
title: "Claude × Higgsfield MCPでオリジナル楽曲のPVを作った話"
url: "https://zenn.dev/yohei_data/articles/601656c37b7b55"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "LLM", "zenn"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

オリジナル楽曲（約2分17秒）のPVを、**Claude DesktopからHiggsfieldをMCP経由で操作**する構成で制作してみました。本記事は、AI動画生成サービス未経験の状態から、当日中にショート版PVを完成させるまでの作業ログです。

最終コスト: **¥2,450**（Higgsfield Starter Plan 1ヶ月分のみ）

技術選定・プロンプト設計・編集ソフト選びまで含めた、実際に動かしてみた個人記録としてシェアします。

## 完成物

* **長さ**: 50秒のショート版MV（10カット × 約5秒）
* **配置**: 楽曲のサビ後半 + アウトロ部分（1:29〜2:09）に動画を当てる構成
* **テーマ**: 生活感のあるコンセプトMV（部屋を舞台にしたストーリー仕立て）
* **解像度**: 1920×1080 / 24fps / H.264

## 使用ツール一覧

| ツール | 用途 | コスト |
| --- | --- | --- |
| Claude（Web版） | プロンプト設計・MCP経由でHiggsfield操作 | サブスク既存 |
| Higgsfield Starter | AI動画生成（Kling 3.0） | ¥2,450/月 |
| DaVinci Resolve 21 (Free) | 編集・カット割り・書き出し | 無料 |
| SUNO | 元楽曲生成（事前に作成済み） | サブスク既存 |

## 全体ワークフロー

```
[SUNOで楽曲生成（事前準備）]
    ↓
[Claudeで絵コンテ・プロンプト設計]
    ↓
[HiggsfieldアカウントとClaudeをMCP接続]
    ↓
[Starter Plan契約 → クレジット獲得]
    ↓
[Claude経由でMCPコマンドを発行 → Kling 3.0で10カット生成]
    ↓
[Higgsfieldから動画ダウンロード]
    ↓
[DaVinci Resolveで編集（音源 + 動画タイムライン）]
    ↓
[H.264 MP4で書き出し → 完成]
    ↓
[サブスクを解約]
```

## ステップ1: プロンプト設計フェーズ

### 楽曲の解析

最初にClaudeに楽曲情報を渡して、PVの設計を依頼しました。

* 歌詞のテキスト
* ジャンル（エレクトロポップ / ポップロック）
* BPM（推定 144）
* 楽曲構成（イントロ / Aメロ / Bメロ / サビ1 / サビ2 / アウトロ）
* ビジュアル方向性（実写寄りストーリーMV）

### 27カットの絵コンテ生成

Claudeに以下を順に作らせました:

* 各カットのタイムコード
* 各カットの内容（被写体・カメラワーク・ライティング）
* 各カット用の英語プロンプト（Higgsfield投入用）
* カラーパレット設計
* BPMに合わせたカット切替タイミング

LLMでここまで設計を詰めておくと、後の生成で再生成回数が減らせます。

## ステップ2: Higgsfield初期セットアップ

### アカウント作成

<https://higgsfield.ai> でGoogle認証。オンボーディングで以下を質問されます:

* AI経験レベル: Expert を選択（全モデルアクセスのため）
* 作りたいもの: Video Generation, Image Generation, Cinematic Visuals, Storyboarding, Filmmaking & VFX, Realistic AI Avatars
* 流入経路: 任意（マーケティング用、機能には影響なし）
* 不満点: 任意（機能には影響なし）

### アップセルオファーが連続で表示される

オンボーディング完了後、カウントダウン付きの割引オファーが複数表示されます。最初は無料枠を試して、必要に応じて契約するのが落ち着いた進め方なので、Starterプランで十分な場合は閉じて先に進めます。

## ステップ3: Claude × Higgsfield MCP接続

ここが今回のキーステップです。

### Higgsfield MCP設定手順

Claudeの設定画面で:

1. **Settings → Connectors → Add custom connector**
2. 以下を入力:
   * **Name**: `Higgsfield`
   * **URL**: `https://mcp.higgsfield.ai/mcp`
3. Connect → ブラウザでHiggsfieldのOAuth認証画面に遷移
4. Allow → Claudeに自動リダイレクト

これだけで接続完了。APIキー管理は不要。

### 動作確認

接続後、ClaudeのチャットでHiggsfield関連のツールが使えるようになります:

* `Higgsfield:balance` - 残高・プラン確認
* `Higgsfield:generate_video` - 動画生成ジョブ投入
* `Higgsfield:generate_image` - 画像生成ジョブ投入
* `Higgsfield:models_explore` - モデル一覧・推薦
* `Higgsfield:show_generations` - 生成履歴
* 他多数

## ステップ4: Starter Plan契約

### モデル別コスト調査

UI上では確認しづらかったが、Pricingページの比較表で確認できる重要情報:

| モデル | コスト/5秒（720p） |
| --- | --- |
| Seedance 2.0 標準 | 22 credits |
| Seedance 2.0 Fast | 17 credits |
| **Kling 3.0** | **7 credits** |

Kling 3.0はSeedanceの約1/3のコストで、シネマティック品質も今回のような静かなトーンのMVには十分でした。

### Top-up クレジットは契約後でないと購入不可

Free Planのままだとクレジット単発購入は不可。最低限のサブスクに加入する必要があります。

### Starter Plan ($15/mo monthly) を選択

* **Monthly** タブを選択（Annual はデフォルトで選択されている場合があるので要確認）
* 200 cr/月、月¥2,450（為替次第）
* Kling 3.0 / Seedance 2.0 / 主要モデル全部使える

### 決済

* Stripe決済、VISA等で即時購入
* 即200cr付与

## ステップ5: Cut 01テスト生成

接続が問題ないか、まず1カットだけテスト。

### テストプロンプト

```
Wide establishing shot of a Japanese minimalist apartment living room
in early morning, soft cool daylight filtering through sheer white curtains,
half-packed cardboard moving boxes stacked along one wall, sparse furniture,
a single empty couch, polished light wood floor, calm static camera,
slight haze, desaturated tones, cinematic 16:9, shallow depth of field,
no people, melancholy atmosphere, ARRI Alexa look. Slow push-in.
```

### MCP経由のジョブ投入

ClaudeがMCPツール `Higgsfield:generate_video` を呼び出し:

```
{
  "params": {
    "model": "kling3_0",
    "mode": "std",
    "aspect_ratio": "16:9",
    "duration": 5,
    "count": 1,
    "prompt": "..."
  }
}
```

返却値:

```
Submitted 1 job.
- 217ee32b-3889-479a-b6d8-4ada511a3e45 (kling3_0)
```

数分後、Higgsfield側で動画が完成。トーン・部屋の雰囲気・カメラワークすべて期待通りでした。

## ステップ6: 残り9カットを一括生成

テストが成功したので、残りカットをすべて投入。

### 戦略

* **Soul Character学習はスキップ**（顔が映るカットは後ろ姿・俯きで構図統一）
* 全カット **Kling 3.0 std / 5秒 / 16:9** で統一
* 一気に7ジョブを並列投入 → 約20-30分で全完成
* 後で2カット追加生成（重複カット差し替え用）

### 10カット構成

| # | カット内容 | 主人公 |
| --- | --- | --- |
| 01 | 部屋全景・朝の光 | × |
| 03 | 主人公の後ろ姿 | ◯（後ろ姿） |
| 04 | 空のハンガーが揺れる | × |
| 09 | 床に座る主人公 | ◯（俯き） |
| 11 | 空のキッチン・マグカップ1つ | × |
| 15 | 空のソファ・クッション1つ | × |
| 19 | 段ボールにテープを貼る手 | × |
| 22 | 部屋中央に立つ主人公 | ◯（遠景） |
| 24 | 完全に空の部屋に主人公座る | ◯（豆粒） |
| 27 | ドアが閉まる空の部屋 | × |

### コスト計算（実績）

* 10カット × 約10cr = **約100 cr 消費**
* 残高: 200cr → 110cr（バッファ十分）

## ステップ7: DaVinci Resolveで編集

### インストール

[DaVinci Resolve 21 Public Beta（Free版）](https://www.blackmagicdesign.com/products/davinciresolve)をダウンロード（約3GB）。

ダウンロード時に登録フォーム（氏名・メール・住所）の入力が必須となります。利用規約に従って入力してください。

### プロジェクト設定

| 項目 | 値 |
| --- | --- |
| Timeline resolution | 1920 × 1080 HD |
| Timeline frame rate | 24 fps |
| Playback frame rate | 24 fps |

### 素材取り込み

すべてメディアプールにドラッグ&ドロップ。

### タイムライン構築

1. **音源（mp3）をA1トラックに先に配置** → 自動で2分17秒のタイムラインが作成される
2. **再生ヘッドを1:29に移動**（タイムコード `01012900` 入力でジャンプ）
3. 動画クリップを順番にV1トラックにドラッグ
4. 各カット5秒ずつ自動でスナップ

### ハマりポイント1: 音声トラックの扱い

AI生成動画には微小な音声トラックが含まれているケースがあり、楽曲と被ることがあります。

**対処**: 動画のオーディオトラックを選択 → `Cmd + Option + L` でリンク解除 → 不要なオーディオトラックを削除 or ミュート

### ハマりポイント2: 配置位置のズレ

タイムライン上のクリップが意図した位置から微妙にズレる場合がある。

**対処**: 各クリップを選択 → タイムコード入力欄で位置を直接指定。または `Cmd + Z` で戻して再配置。

## ステップ8: 書き出し（Deliver）

### 設定

| 項目 | 値 |
| --- | --- |
| プリセット | Custom Export |
| フォーマット | QuickTime |
| コーデック | H.264 |
| 解像度 | Timeline Resolution (1920×1080) |
| フレームレート | 24fps |
| 品質 | 自動 |
| ハードウェアアクセラレート | ON |
| レンダー範囲 | タイムライン全体（または イン/アウト範囲） |

### 推定ファイルサイズ

約450MB（2分17秒・1080p・H.264）

### 書き出し時間

Mac mini M2クラスで2〜5分。

## ステップ9: Higgsfieldサブスクの解約

PVが完成したら、追加課金を防ぐため解約。

### 解約手順の流れ

Higgsfieldの解約フローは多段階構成になっています。順を追って進める必要があります:

#### 段階1: 確認画面

「すでに支払い済みなのでクレジットを使い切ってから解約してはどうか」という案内が表示されます。

→ 画面下部の **Continue** リンクで次へ。

#### 段階2: 解約理由のアンケート

解約理由のラジオボタン + 自由記述（5文字以上必須）。

→ 該当する理由を選び、5文字以上のコメントを入力して **Next**。

#### 段階3: 期間限定割引オファー

割引オファー画面が表示されます。

→ 不要であれば **Continue** で次へ。

#### 段階4: 最終確認

「本当に解約しますか?」の最終確認画面。

→ **Confirm & Cancel** で解約確定。

### 解約完了後の挙動

> "Subscription canceled. You will retain access until [next billing date]"

クレジット残高は次回課金日まで使用可能。**解約手続きを今行っても今月分の機能は引き続き使える**仕様なので、PV完成後すぐに解約しておくのが課金事故を防ぐ上では確実です。

カレンダーリマインダーと組み合わせるとさらに安心。

## 学び・知見

### 1. AI動画生成の現実的な制約

* 1クリップ最大5〜15秒（モデルにより異なる）
* フルPV（2分以上）を一発生成は不可能
* 「**複数の短いクリップ + 編集**」が現実解

### 2. プロンプト設計で明示すべき要素

ジェネレーター任せにすると意図から外れがち。明示すべき要素:

* カメラワーク（static / push-in / pan）
* ライティング（cool daylight / warm tungsten）
* 被写界深度（shallow DoF）
* 色味（desaturated / muted）
* 動きの量（slow / minimal movement）
* 撮影機材の種類（ARRI Alexa look等）

### 3. キャラクター一貫性問題

* 顔が映るカットを複数作る場合、Soul Character等の学習機能を使うと再現性が上がる
* 学習なしでも「後ろ姿・俯き・遠景」で構図統一すれば破綻しにくい
* 今回は学習なしで成立した

### 4. モデル選択の戦略

* **Kling 3.0 std**: コスパ重視、シネマティック向け
* Seedance 2.0: 高品質だがコスト3倍
* Veo 3.1: さらに高品質、特定用途向け
* 用途と予算で使い分け

### 5. サブスクのつき合い方

* Free Planではクレジット単発購入不可（要サブスク）
* Annualトグルが初期選択になっている場合があるので、Monthly選択を確認
* 用が済んだら早めに解約手続き、カレンダーリマインダー必須
* 解約後も今月分のクレジットは課金日まで使える

### 6. MCP連携の威力

* Claudeのチャット内から複数モデル・複数ジョブを並列で投げられる
* ジョブ管理が自然言語で完結
* API設計を意識せず使える

## コスト内訳（最終）

| 項目 | 金額 |
| --- | --- |
| Higgsfield Starter Plan（1ヶ月のみ） | ¥2,450 |
| DaVinci Resolve | ¥0 |
| その他 | ¥0 |
| **合計** | **¥2,450** |

予算「¥2,500で5カットだけ試す」から始まって、最終的に10カットの50秒PVが完成しました。

## 次回やりたいこと

* **Soul Character学習を試す**（フルPV化、27カット完全版）
* **Lipsync機能で口パク映像生成**（主人公が歌うシーン）
* **9:16版の制作**（TikTok / Reels用）
* **複数曲のPV量産ワークフロー化**

## まとめ

* AI動画生成は「**短いクリップ生成 + 編集ソフトで合成**」のハイブリッド前提
* プロンプト設計に時間をかける価値あり
* Claude × Higgsfield MCPは**ツール切り替えなしで完結**できる強力な体験
* 必要分だけ契約 → 完了後に解約という運用で、¥2,450程度から作品制作が始められる
* DaVinci Resolveの無料版で編集は完全にカバーできる

個人クリエイターがAIだけでMVに近い形のものを作れる時代が見えてきた、という肌感の作業でした。

## 参考リンク

---

ここまで読んでいただきありがとうございました。同じワークフローを試した方や、別のアプローチを実践している方は、コメントでシェアいただけると嬉しいです。
