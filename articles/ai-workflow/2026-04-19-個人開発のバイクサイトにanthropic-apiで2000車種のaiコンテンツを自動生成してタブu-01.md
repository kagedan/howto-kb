---
id: "2026-04-19-個人開発のバイクサイトにanthropic-apiで2000車種のaiコンテンツを自動生成してタブu-01"
title: "個人開発のバイクサイトにAnthropic APIで2,000車種のAIコンテンツを自動生成してタブUIに載せた話"
url: "https://qiita.com/ausssxi0/items/a224ae993850c39d3f7e"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

# 個人開発のバイクサイトにAnthropic APIで2,000車種のAIコンテンツを自動生成してタブUIに載せた話

## はじめに

バイクポータルサイト「[MotoHub](https://motohub.jp)」を個人開発しています。

Google March 2026コアアップデート（3/27開始、4/8完了）の影響で、DAUがピーク420から57〜100まで急落しました。回復のために**車種モデルページと車両詳細ページを根本的に作り変えた**1週間の記録です。

やったことは大きく5つ：

1. **Anthropic APIで車種コンテンツを自動生成**（enriched\_content + model\_history）
2. **価格.com参考のタブ式UIに全面リニューアル**
3. **年式分布グラフ・レビュー項目別評価の追加**
4. **買取予想V2（BuybackPriceCalculator）**
5. **クイズのAPI化 + Redis 50問プール**

---

## 環境

```
さくらVPS 4GB
├── Docker Compose
│   ├── PHP-FPM 8.3（Laravel 12）
│   ├── MySQL 8.0
│   ├── Redis Alpine
│   └── Meilisearch
├── Cloudflare CDN
└── Anthropic API（Claude Sonnet 4）

開発: WSL2 + Claude Code（CLI）
```

---

## 背景：コアアップデートで何が起きたか

3月中旬にDAU 420を記録した直後、Google March 2026コアアップデートが来ました。

| 時期 | DAU | 状態 |
| --- | --- | --- |
| 3月中旬 | 420 | ピーク |
| 3月下旬 | 200前後 | ハネムーン期間終了 + コアアップデート開始 |
| 4月中旬 | 57〜100 | Bot除外後の実数 |

GSCの平均掲載順位は26位→10位に改善中なので、**順位は上がっているのにクリックが減っている**という不思議な状態。Googleが「このサイトのコンテンツは薄い」と判断したページを一気にインデックスから外した可能性があります。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F218c44da-1a3e-4271-beb4-544d91c8be95.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=57f54c35525433f265c3181fd608a0c1)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F218c44da-1a3e-4271-beb4-544d91c8be95.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=57f54c35525433f265c3181fd608a0c1)

**結論：車種モデルページのコンテンツが圧倒的に足りなかった。**

価格.comのバイクページと比較すると、MotoHubの車種ページには数字の羅列しかない。紹介文・市場分析・購入アドバイス・ライバル比較——全部ない。これを一気に埋める必要がありました。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F77ade9d2-d8bf-4876-a963-b564cbcd40e4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5fab0a2437a521fd0f61bdf7cfaded21)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F77ade9d2-d8bf-4876-a963-b564cbcd40e4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5fab0a2437a521fd0f61bdf7cfaded21)

---

## 1. Anthropic APIでAIコンテンツ自動生成

### なぜAI生成か

2,000車種に手書きでコンテンツを用意するのは不可能です。でも適当なテンプレート文を量産するとGoogleに「薄いコンテンツ」と判定されます。

**MotoHubにはリアルな販売データがある。** 平均価格・走行距離分布・年式分布・地域別人気・売れるまでの日数——このデータをAIに渡して「数字に基づく解説」を生成させれば、車種ごとにユニークなコンテンツになります。

### Anthropic APIとは何をしているのか

「claude.aiのチャットで同じ質問をしてコピペすれば同じでは？」——その通りです。結果は同じです。

ただし2,000車種を手動でやると：

```
チャットでコピペ方式:
  1車種あたり3分（質問入力→回答待ち→コピー→DBに貼り付け）
  × 2,000車種 = 6,000分 = 約100時間

API自動化方式:
  コマンド1行実行 → 寝てる間に完了 = 約12時間（放置）
```

APIは**プログラムからClaude に質問を送って、回答を受け取る仕組み**です。チャットで人間がやっていることを、コードで自動化しています。

```
① php artisan models:generate-content を実行
    ↓
② LaravelがMySQLから車種の販売データを集計
   （平均価格、走行距離分布、年式分布、地域別人気...）
    ↓
③ そのデータ + プロンプトをAnthropic APIにHTTPリクエストで送信
   POST https://api.anthropic.com/v1/messages
    ↓
④ Claude Sonnet 4が紹介文を生成してJSONで返す
    ↓
⑤ 返ってきたJSONをDBのenriched_contentカラムに保存
    ↓
⑥ 次の車種に進む（②に戻る × 2,000回）
```

APIは**送ったトークン数（input）と返ってきたトークン数（output）に応じて従量課金**されます。

```
Claude Sonnet 4の料金:
  Input:  $3 / 100万トークン（送信側）
  Output: $15 / 100万トークン（生成側）

1車種あたり:
  Input  約1,000トークン（データ+プロンプト）→ $0.003
  Output 約1,000トークン（生成された文章）  → $0.015
  合計: 約$0.02（約3円）
```

2,000車種で約$40。claude.aiのProプラン（$20/月）でチャットしてコピペするより安くて、100時間の手作業がゼロになります。

### enriched\_content：車種紹介コンテンツ

Artisanコマンドでバッチ生成します。

```
// GenerateModelContent.php
php artisan models:generate-content --chunk=50
```

AIに渡すデータ：

```
$stats = [
    'total_count'     => $model->listings()->count(),
    'avg_price'       => $model->listings()->avg('total_price'),
    'min_price'       => $model->listings()->min('total_price'),
    'max_price'       => $model->listings()->max('total_price'),
    'avg_mileage'     => $model->listings()->avg('mileage'),
    'year_distribution' => $this->getYearDistribution($model),
    'region_ranking'  => $this->getRegionRanking($model),
    'days_to_sell'    => $this->getAvgDaysToSell($model),
];
```

**プロンプト設計で一番こだわったポイント：**

最初のプロンプトでは「圧倒的な実用性を誇る国民的モデルです」「安定した需要を持つ車種です」みたいな**曖昧な形容詞だらけの文章**が生成されました。GooBikeの紹介文と変わらない。

修正後のプロンプトでは、こう指示しています：

```
# 絶対ルール
- 「人気」「定番」「圧倒的」などの曖昧な形容詞を使わない
- 必ず具体的な数字（価格、台数、走行距離）を引用して説明する
- 「つまり○○ということです」「○○万円の予算があれば○○」のように
  データから導かれる具体的な解釈・アドバイスを書く
```

Before：

> 「圧倒的な実用性を誇る国民的モデルです」

After：

> 「新しいモデルが中心となって流通している一方で、古い年式まで幅広く選択できる車種です。5000km以下の低走行個体を狙う場合は35万円以上の予算を見込んでおくと選択肢が広がります」

**数字が入ると説得力が段違い。** しかも車種ごとにデータが違うので、自動的にユニークなコンテンツになります。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2Fa5d21353-36fa-45e5-9a15-921f821a4ba7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9c335dce9b50ba3cf53d365a04b72b3c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2Fa5d21353-36fa-45e5-9a15-921f821a4ba7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9c335dce9b50ba3cf53d365a04b72b3c)

### 生成されるJSON構造

```
{
  "introduction": "車種の概要と市場での位置づけ",
  "market_trends": "価格帯・流通量の分析",
  "recommended_for": "こんな人におすすめ",
  "buying_points": "購入時のチェックポイント",
  "rivals": [
    {"name": "ライバル車種名", "comparison": "比較コメント"}
  ]
}
```

DBの `enriched_content` カラム（JSON型）に保存。Bladeテンプレートで各セクションを表示します。

### model\_history：モデル履歴の自動生成

もう一つ、車種の**世代・フルモデルチェンジ履歴**も自動生成しました。

```
php artisan models:generate-history --chunk=50
```

こちらもAnthropic APIに車種名とカテゴリを渡して、世代情報をJSON配列で返してもらいます。

```
{
  "generations": [
    {
      "name": "初代",
      "years": "1958-2011",
      "changes": "空冷4ストローク単気筒49cc、自動遠心クラッチ採用",
      "new_price": 20,
      "is_current": false
    },
    {
      "name": "2代目（AA09）",
      "years": "2012-現在",
      "changes": "FI化、LEDヘッドライト採用",
      "new_price": 25,
      "is_current": true
    }
  ]
}
```

Blade側では縦のタイムラインUIで表示しています。現行世代は緑のドット、過去の世代はグレー。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2Fe6ad5368-9eec-4082-8eaf-d8ab2c450740.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8866c88b05303ddc049b84de5e1eb7aa)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2Fe6ad5368-9eec-4082-8eaf-d8ab2c450740.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8866c88b05303ddc049b84de5e1eb7aa)

### バッチ実行のコスト

| 項目 | 数値 |
| --- | --- |
| 対象車種数 | 約2,000（販売台数5台以上） |
| enriched\_content | 1車種あたり約$0.02 |
| model\_history | 1車種あたり約$0.02 |
| 合計API費用 | **約$80** |
| 実行方法 | VPSでscreenコマンド、バックグラウンド実行 |
| 実行時間 | 約12時間（rate limit考慮） |

```
# VPSでバックグラウンド実行
screen -S enrich
docker compose exec app php artisan models:generate-content --chunk=9999
# Ctrl+A → D で抜ける

screen -S history
docker compose exec app php artisan models:generate-history --chunk=9999
# Ctrl+A → D で抜ける
```

既に生成済みの車種はスキップされるので、途中で止まっても再実行すれば続きから処理されます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F4f746fab-eb3c-46b7-880d-97795f0caf11.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5af780dca46252c56b41e9716eb63a25)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F4f746fab-eb3c-46b7-880d-97795f0caf11.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5af780dca46252c56b41e9716eb63a25)

---

## 2. 価格.com参考のタブ式UIにリニューアル

### Before：縦スクロール地獄

車種モデルページは全セクションが縦に並んでいて、スマホだと延々スクロールする必要がありました。ユーザーは「相場だけ見たい」のに、FAQやニュースを全部通過しないとたどり着けない。

### After：6タブ構成

価格.comのバイクページを参考に、タブ切り替え式に変更しました。

| タブ | 内容 |
| --- | --- |
| 概要 | AI生成コンテンツ + 基本スペック + 年式分布 + モデル履歴 |
| 相場・価格 | 価格分布グラフ + 価格推移チャート + 買取予想 |
| 在庫・エリア | 販売中車両カード + 都道府県別リンク |
| パーツ | カテゴリ別パーツ + 消耗品チェックリスト |
| ニュース・動画 | 関連ニュース + YouTube動画 |
| レビュー・FAQ | レビュー一覧 + 項目別評価 + FAQ |

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F46cc44a2-97f9-446f-ad91-380840fc5434.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a8b810a68924bea3ca73a3e95acfc1bb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F46cc44a2-97f9-446f-ad91-380840fc5434.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a8b810a68924bea3ca73a3e95acfc1bb)  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2Fb3bf8716-c110-422c-a9b0-de1e0f54d007.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6e0749814d923ffe4053b090c9bc83c0)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2Fb3bf8716-c110-422c-a9b0-de1e0f54d007.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6e0749814d923ffe4053b090c9bc83c0)

### 実装

JavaScriptのタブ切り替えはシンプルです：

```
function switchTab(tabName) {
    document.querySelectorAll('.tab-panel').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('border-blue-600', 'text-blue-600');
        el.classList.add('border-transparent', 'text-gray-400');
    });

    document.getElementById('tab-panel-' + tabName).classList.remove('hidden');
    const btn = document.getElementById('tab-' + tabName);
    btn.classList.remove('border-transparent', 'text-gray-400');
    btn.classList.add('border-blue-600', 'text-blue-600');

    history.replaceState(null, '', '#' + tabName);
}
```

URLハッシュ対応（`#price` でアクセスすれば相場タブが開く）も入れています。

---

## 3. 年式分布グラフ・レビュー項目別評価

### 年式分布（Chart.js棒グラフ）

「概要」タブに販売中車両の年式分布を棒グラフで表示。

```
// Controller側
$yearDistribution = $listings
    ->whereNotNull('model_year')
    ->groupBy('model_year')
    ->map->count()
    ->sortKeys();
```

**これがあるとユーザーが一目で「この車種は新しいモデルが多いのか、古いのが多いのか」がわかります。** 中古バイク選びでは重要な情報です。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2Fc7adbd00-84a9-4efb-baf5-733eaefa162b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9a59651e1772ac702f7e670c60a86d83)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2Fc7adbd00-84a9-4efb-baf5-733eaefa162b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9a59651e1772ac702f7e670c60a86d83)

### レビュー項目別評価（5項目 + レーダーチャート）

レビュー投稿フォームに5項目の★評価を追加しました。

| 項目 | カラム名 |
| --- | --- |
| デザイン | rating\_design |
| エンジン性能 | rating\_engine |
| 取り回し | rating\_handling |
| 燃費 | rating\_fuel\_economy |
| コスパ | rating\_cost\_performance |

全て任意入力（nullable, tinyint unsigned, 1-5）。Chart.jsのレーダーチャートで平均値を可視化しています。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F7b787486-c643-4cc9-bc5c-717d58497317.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bfacac89f424fb2f572f15ff699bfd32)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F7b787486-c643-4cc9-bc5c-717d58497317.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bfacac89f424fb2f572f15ff699bfd32)

**車両詳細ページにも同じ項目別評価フォームを追加し、車種モデルページの項目別評価プレビューを車両詳細ページのレビューセクション上部に表示。** 両ページ間でレビューデータが連携する構造です。

---

## 4. 買取予想V2（BuybackPriceCalculator）

### V1の問題

V1は単純な平均価格ベースの計算で、年式や走行距離による減価が反映されていませんでした。

### V2のロジック

```
class BuybackPriceCalculator
{
    public function calculate(BikeModel $model, ?int $year, ?int $mileage): array
    {
        // 1. ベース価格（同車種の販売価格中央値の60-70%）
        $basePrice = $this->getMedianPrice($model) * 0.65;

        // 2. 年式による減価（1年あたり3-5%減）
        $yearFactor = $this->getYearDepreciation($year);

        // 3. 走行距離による減価（5000km刻みで段階的に）
        $mileageFactor = $this->getMileageDepreciation($mileage);

        // 4. 人気度補正（販売台数・閲覧数ベース）
        $popularityFactor = $this->getPopularityBonus($model);

        $estimated = $basePrice * $yearFactor * $mileageFactor * $popularityFactor;

        return [
            'min' => (int)($estimated * 0.85),
            'max' => (int)($estimated * 1.15),
            'factors' => [...], // 計算根拠
        ];
    }
}
```

**MotoHubの実データ（実際の販売価格・売れるまでの日数）に基づく予測**なので、一般的な買取相場サイトより精度が高くなるはずです。

---

## 5. クイズのAPI化 + Redis 50問プール

### Before

クイズの問題はフロントエンドのJSファイルにハードコードされていました。問題追加のたびにJSファイルを編集してデプロイが必要。

### After

Laravel API化して、Redisに50問のプールをキャッシュ。

```
// QuizController.php
public function getQuestions(Request $request)
{
    $category = $request->input('category', 'price');
    $count = min($request->input('count', 10), 20);

    $cacheKey = "quiz_pool_{$category}";

    $pool = Cache::remember($cacheKey, 3600, function () use ($category) {
        return $this->generateQuestionPool($category, 50);
    });

    // プールからランダムに出題
    return response()->json(
        collect($pool)->random($count)->values()
    );
}
```

**問題はMotoHubの実データから動的生成。** 「このバイクの平均中古価格は？」「今月一番売れたバイクは？」——データが更新されれば問題も変わるので、常に最新の内容になります。

カテゴリも4種類に拡充：

| カテゴリ | 内容 |
| --- | --- |
| 中古価格 | 平均価格を当てろ！ |
| 売れ筋ランキング | 今売れてるのは？ |
| 売却スピード | 何日で売れる？ |
| 地域別人気 | どの都道府県で人気？ |

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F984f3247-68be-4555-9433-981c91953084.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e174e5d68682e44ca6652971d45206b2)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F984f3247-68be-4555-9433-981c91953084.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e174e5d68682e44ca6652971d45206b2)

---

## 車両詳細ページの改善

車種モデルページだけでなく、**22万件の車両詳細ページも同時に改善**しました。

| 改善項目 | 内容 |
| --- | --- |
| 情報整理 | セクション順の最適化 |
| 車種データ取込 | enriched\_contentがある車種では定型文を非表示→車種紹介セクションで代替 |
| FAQ改善 | 排気量別の免許・車検・維持費FAQを動的生成 |
| モバイル価格バー | 画面下部に固定表示 |
| レビュー項目別評価 | 5項目★の投稿フォーム追加 |

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F151f46ca-4196-4e49-9607-5d57756b9f5f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=17af7fd84f21856ac1abe0d3b0306d79)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F151f46ca-4196-4e49-9607-5d57756b9f5f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=17af7fd84f21856ac1abe0d3b0306d79)

車両詳細ページにAI生成コンテンツを個別で生成するのは22万件あるので不可能ですが、**条件分岐テンプレートで車両ごとに異なる文章を出す**仕組みにしています。

```
@if($listing->price < $stats->avg_price * 0.8)
  この車両は相場より20%以上お買い得です。
@endif

@if($listing->mileage < 3000)
  走行距離3,000km未満の極上車です。
@endif
```

---

## コスト

| 項目 | 費用 |
| --- | --- |
| Anthropic APIクレジット | $81 |
| さくらVPS（月額） | 約¥3,000 |
| Cloudflare | 無料 |
| YouTube API | 無料枠内 |
| **合計追加コスト** | **約$81（約¥12,000）** |

2,000車種分のAIコンテンツが¥12,000で生成できました。ライターに依頼したら1車種¥3,000×2,000=¥600万。50分の1のコストです。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F47dbe3e6-08d0-4002-b5c1-a5e9013c769b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=674bfe2ada48499957428d91998fd327)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3669654%2F47dbe3e6-08d0-4002-b5c1-a5e9013c769b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=674bfe2ada48499957428d91998fd327)

---

## 次のコアアップデートに向けて

次のGoogleコアアップデートは6〜7月と予想されています。それまでに仕込めることはまだあります。

* ゲーム機能（バイク2048パズル）でさらなるエンゲージメント向上
* フリーゲームサイト登録で被リンク獲得
* UGCレビューの蓄積
* 車種比較機能
* 相場アラート

**データに基づく独自コンテンツをどれだけ積み上げられるか。** アグリゲーターからの脱却はこの一点にかかっています。

---

## まとめ

| やったこと | 効果 |
| --- | --- |
| Anthropic APIでAIコンテンツ生成 | 2,000車種にユニークな紹介文 |
| タブ式UIに変更 | 縦スクロール解消、UX向上 |
| 年式分布・レビュー項目別評価 | データの視覚化 |
| 買取予想V2 | 実データベースの精度向上 |
| クイズAPI化 | 動的出題、カテゴリ拡充 |

**全部合わせて実装期間は約3日。** Claude Code（CLI）で指示→実装→テスト→デプロイのサイクルを高速に回しました。本業ありの個人開発でも、AIツールを活用すれば週末だけでこれだけの改善ができます。

---

🏍 MotoHub: <https://motohub.jp>  
🎮 バイク4択クイズ: <https://motohub.jp/quiz>  
🔄 バイクわらしべ長者: <https://motohub.jp/warashibe>  
X: <https://x.com/motohub_jp>
