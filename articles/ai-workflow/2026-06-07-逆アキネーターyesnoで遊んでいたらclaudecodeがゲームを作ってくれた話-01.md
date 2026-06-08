---
id: "2026-06-07-逆アキネーターyesnoで遊んでいたらclaudecodeがゲームを作ってくれた話-01"
title: "【逆アキネーター】Yes/Noで遊んでいたらClaudeCodeがゲームを作ってくれた話"
url: "https://qiita.com/Higemal/items/6bf6b93a0d597edf8ec6"
source: "qiita"
category: "ai-workflow"
tags: ["API", "JavaScript", "qiita"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

ClaudeCodeを利用してなんとなく開発はしてみたい、でも、何を開発すればいいか思いつかない、といった悩みはありませんでしょうか。

今回は"逆アキネーター"こと、自分の気持ちを2択で回答していくことで深層的な理想像を炙り出すような、Claudeとのインタラクティブでゲームアプリを作ってもらうことにします。

:::note info
このような問答は`ソクラテス式問答`というみたいです。
（ソクラネーターではちょっとしっくりこなかった）
:::

# 前提
１．**敢えて具体的な "作りたいもの" は考えない**
２．`Planモード`で進め、内容が煮詰まったら一気にゲームアプリを作成する
３．プログラム言語ヨクワカラナイので`html`だけで実装する
４．トークン枯渇しないように`Claude Sonnet 4.6`を使う

# はじめかた
シンプルな3ステップに絞ります。

ステップ１：ClaudeCodeを起動します。
```
$ claude
```

<br>

ステップ２：`Planモード`にします。
```
> /plan
```


<br>

ステップ３：進め方を指示します。
```
❯ html言語を利用して、ブラウザで利用可能なゲームを作成します。
  私の要望が明確になるように、3択(はい、いいえ、わからない)で選択肢を提示し続け、
  要件が具体的になってきたら整理をして作成するゲームを示してください。

```

これだけ！

# やってみた
ではスタートします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/5ec076d3-5f0a-481e-b7d8-33597da4a2ec.png)



<br>

`ジャンルをアクション系にするか`は`No`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/84ce5663-adb0-44c3-8017-146f30257d0d.png)

<br>

`操作方法はマウスメインにする`は`No`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/de89ba38-b290-46bc-b569-a2c505641480.png)

<br>

`ソロプレイ中心にする`は`Yes`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/3190ac0f-9c98-45fc-b2eb-01def8200d2c.png)

<br>

`スコアによる達成感を重視する`は`No`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/ea7c13cd-c735-4b1a-9a02-e7bc25784a00.png)


<br>

`パズル要素を中心にする`は`No`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/97c80301-6675-41ec-9c4a-366aaa2ae0ef.png)


<br>

`テキスト読み要素を多く含む`は`No`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/362e395c-4d92-4a7d-9bf5-4a638e31fba7.png)

<br>

`グリッドフィールドを使いたい`はNoで。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/165fca9c-8d4b-40b1-abd9-7d5cfcd641db.png)

<br>

`ターン性のゲームにする`は`Yes`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/056efb64-60f0-401f-a024-306f12675632.png)


<br>

`リズム系要素を取り入れる`は`No`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/f01aef00-53b0-44ce-834b-1e0093dda0d6.png)

<br>

`数字・言語・文字列要素を使うゲームにする`は`No`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/d2177230-87e5-42b7-ac2b-6770e5e2cea3.png)

<br>

`シミュレーション/育成要素を入れる`は`Yes`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/cf91a3a6-07c3-4754-a2a6-424447226638.png)

<br>

`戦闘要素を入れる`は`どちらでもいい`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/340f46d3-4de3-48a0-a38b-2bf7599be5cd.png)

<br>

`育成要素を取り入れる`は`Yes`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/bc672890-b721-436f-bd89-750657709a40.png)

<br>

`デッキ/カードゲーム要素を入れる`は`Yes`で。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/d382da23-c7c4-4d57-a6aa-af9a22213670.png)

<br>

`Slay the Spireのようなログライク要素を取り入れる`は`どちらでもいい`で。

:::note warn
この時点で私がSlay the Spireが好きなことがバレていますが、
照れ隠しで`どちらでもいい`にしています
:::

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/736af9f6-08dd-43e6-9db7-a61ef7633547.png)


<br>

`カードのレアリティ要素を入れる`は`Yes`にします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/22744809-0856-48e6-bbb7-9fb2b45a016c.png)

<br>

`ボスクリア要素を入れる`は`No`にします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/f419739f-61cf-4402-9e02-4ad2d77cff3d.png)


<br>

`ビジュアルはテキスト等のシンプルでよいか`は`Yes`にします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/023f06f9-f766-4482-bc0f-d47971116605.png)


<br>

`テーマやデザインはファンタジー系`については`No`にします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/b39a894c-1e12-4f82-82a6-eb2fb5af7b29.png)


<br>

`カードのテーマ`について、ここだけは`Type something`を選択し、`レガシーシステムをモダンなシステムへリニューアルするシステム開発がテーマ`と打ち込んでいます。
（ここの問答はYes/Noだけで進めるとが非常に長くなる気がしたため）
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/641e7295-a030-4775-98d9-39294e7b9064.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/a329c45f-29cb-4003-8099-2031fc515caf.png)

# 結果
ClaudeCodeによって以下の提案がなされました。

```
●ありがとうございます！テーマが決まりました。要件が揃ったので整理してゲーム概要を提示します。

---

作成するゲーム: "Legacy Burst"

ゲーム概要
レガシーシステムをモダン化するプロジェクトマネージャーとして、
毎スプリント（ターン）カードを引いてプレイし、
技術的負債と障害に対処しながら近代化を進めるターン制カードシミュレーション。


ゲームプレイの流れ
[ドロー]
→ [カードプレイ（数字キー）]
→ [チーム効果]
→ [レガシーAI行動]
→ [スプリント終了（Space）]
→ [ドラフト（新カード追加）]

主な要素
┌────────────┬──────────────────────────────────────────────────────────────┐
│ 要素       │ 内容                                                         │
├────────────┼──────────────────────────────────────────────────────────────┤
│ 操作       │ キーボードのみ（1〜5でカード、Space終了、Enter確定）         │
├────────────┼──────────────────────────────────────────────────────────────┤
│ カード種   │ 🔧リファクタ / ☁クラウド移行 / 🧪品質改善 /                 │
│            │ 👥エンジニア / 🚨インシデント対応                            │
├────────────┼──────────────────────────────────────────────────────────────┤
│ 育成       │ エンジニアカードをチームに配置 →                            │
│            │ スプリントごとにXP獲得・Lv1〜3に成長                        │
├────────────┼──────────────────────────────────────────────────────────────┤
│ 収集       │ スプリント後に3枚から1枚ドラフトでデッキに追加              │
├────────────┼──────────────────────────────────────────────────────────────┤
│ レアリティ │ Common / Rare / Epic（色で視覚的に区別）                    │
├────────────┼──────────────────────────────────────────────────────────────┤
│ ゲーム     │ System Health が0になったら終了（再スタート可）             │
│ オーバー   │                                                              │
├────────────┼──────────────────────────────────────────────────────────────┤
│ ビジュアル │ テキスト・絵文字・数字のみのシンプルなUI                    │
└────────────┴──────────────────────────────────────────────────────────────┘


カードの一例
- コードリファクタ（Common） → 技術的負債を -2
- SREエンジニア（Rare / 育成） → 毎ターンHealthを自動回復（Lv3で効果2倍）
- マイクロサービス化（Epic） → 大幅なモダン化スコア獲得
- 緊急パッチ（Common） → インシデントを即時解決

---
Plan: Legacy Renewal - ターン制カードシミュレーションゲーム


Context
ブラウザで動作するHTML単体ファイルのゲームを作成する。
ユーザーの要望を3択Q&Aで収集した結果、以下の要件が確定した。


確定した要件
┌──────────┬──────────────────────────────────────────────────────┐
│ 項目     │ 内容                                                 │
├──────────┼──────────────────────────────────────────────────────┤
│ ジャンル │ ターン制カードゲーム ＋ シミュレーション             │
├──────────┼──────────────────────────────────────────────────────┤
│ テーマ   │ レガシーシステムをモダンなシステムへリニューアルする │
│          │ システム開発                                         │
├──────────┼──────────────────────────────────────────────────────┤
│ 操作     │ キーボード中心                                       │
│          │ （数字キーでカード選択、Enterで確定、               │
│          │  Spaceでターン終了）                                │
├──────────┼──────────────────────────────────────────────────────┤
│ プレイ数 │ 1人（vsレガシーシステムAI）                         │
├──────────┼──────────────────────────────────────────────────────┤
│ ビジュアル│ シンプル（テキスト・アイコン・数字のみ）            │
├──────────┼──────────────────────────────────────────────────────┤
│ 育成要素 │ エンジニアカードをチームに配置し、                  │
│          │ スプリントごとにXP獲得・レベルアップ                │
├──────────┼──────────────────────────────────────────────────────┤
│ カード収集│ レアリティあり（Common/Rare/Epic）、               │
│          │ スプリント後にドラフトで追加                        │
├──────────┼──────────────────────────────────────────────────────┤
│ クリア条件│ なし（継続シミュレーション形式、                   │
│          │ モダン化スコアを上げ続ける）                        │
├──────────┼──────────────────────────────────────────────────────┤
│ 勝敗     │ 「システム障害レベル」が最大になるとゲームオーバー   │
└──────────┴──────────────────────────────────────────────────────┘

---

ゲーム概要: "Legacy Burst"

世界観
あなたはプロジェクトマネージャー。巨大なレガシーシステムを抱えた企業で、
モダン化プロジェクトを進めながら日々の障害に対処する。
レガシーシステムは毎ターン「技術的負債」と「インシデント」を生み出し続ける。


ターン構造（1ターン = 1スプリント）
1. ドロー       : デッキから5枚引く
2. プレイ       : Budgetを消費してカードを使用（数字キー1〜5）
3. チーム効果   : 配置済みエンジニアのパッシブ効果を適用
4. レガシーAI   : 技術的負債・インシデントを自動生成
5. スプリント終了（Space）
6. ドラフト     : 3枚から1枚選んでデッキに追加


リソース
┌────────────────────┬─────────────────────────────┐
│ リソース           │ 説明                        │
├────────────────────┼─────────────────────────────┤
│ Budget 💰          │ 毎ターン補充。カードのプレイコスト │
├────────────────────┼─────────────────────────────┤
│ Tech Debt 🪙       │ 蓄積すると障害レベルが上がる      │
├────────────────────┼─────────────────────────────┤
│ Modernization Score│ 高ければ高いほど良い。           │
│ ★                  │ ゲームの進捗指標               │
├────────────────────┼─────────────────────────────┤
│ System Health 🛡   │ 0になるとゲームオーバー         │
└────────────────────┴─────────────────────────────┘


カード種別（全20種程度）
┌────────────┬──────────────────────────────┬──────────────────────────┐
│ カテゴリ   │ カード例                     │ 効果                     │
├────────────┼──────────────────────────────┼──────────────────────────┤
│ 🔧 Refactor│ コードリファクタ / テスト追加 │ Tech Debt 削減           │
├────────────┼──────────────────────────────┼──────────────────────────┤
│ ☁ Cloud    │ API化 / コンテナ移行 /       │ Modernization Score ↑    │
│            │ CDN導入                      │                          │
├────────────┼──────────────────────────────┼──────────────────────────┤
│ 🧪 Quality │ コードレビュー / CI/CD構築   │ Health ↑, Debt ↓         │
├────────────┼──────────────────────────────┼──────────────────────────┤
│ 👥 Engineer│ フロントエンジニア / SRE /   │ チームに配置、           │
│            │ アーキテクト                 │ パッシブ効果             │
├────────────┼──────────────────────────────┼──────────────────────────┤
│ 🚨 Incident│ 緊急パッチ / ロールバック    │ インシデント即時解決     │
└────────────┴──────────────────────────────┴──────────────────────────┘


育成（エンジニアカード）
- 手札から「チーム」に置く（最大3枠）
- 毎スプリント自動でXP獲得
- Lv1 → Lv2 → Lv3でパッシブ効果が強化される
  - 例:
    SRE Lv1 「毎ターンHealth +1」
    → Lv3 「毎ターンHealth +2 かつインシデント確率 -20%」


レアリティ
- Common（灰） : 基本カード、序盤から入手可
- Rare（青）   : 強力な効果、ドラフトで低確率
- Epic（紫）   : 特殊な複合効果、ゲーム後半のみ出現


レガシーAI の動作
毎ターン以下をランダムに実行:
- Tech Debt +1〜3
- ランダムなインシデント発生（放置するとHealth減少）
- スプリント数が増えるほど強化


---

実装計画

ファイル構成
単一HTMLファイル（legacy_burst.html）にすべて含める。
CSS・JavaScript をインラインで記述。
外部ライブラリ一切なし。


実装ステップ
1. HTML構造
   - ゲーム画面レイアウト
     （手札エリア、チームゾーン、ステータスバー、ログ）

2. ゲームステート管理
   - JavaScriptオブジェクトで全状態を管理

3. カードデータ定義
   - 20種のカード定義
     （名前、コスト、レアリティ、効果関数）

4. デッキ・ドロー処理
   - シャッフル
   - ドロー
   - 手札枯れ時のリシャッフル

5. ターンエンジン
   - プレイヤー → チーム効果 → AI → スプリント終了
     の流れ

6. 育成システム
   - チームゾーン管理
   - XP計算
   - レベルアップ

7. ドラフトUI
   - スプリント後の3択カード選択

8. キーボード操作
   - 1〜5でカード選択
   - Enter確定
   - Space終了
   - Escキャンセル

9. ゲームオーバー判定
   - System Health = 0 の検出とリスタート

10. UI仕上げ
    - ログ表示
    - アニメーション（CSSのみ）
    - レアリティ色分け

```


<br><br>

こちらを承認して出来上がったものが、以下のブラウザゲーム、**`LEGACY BURST`** になります。

限られた予算で行動を打ち、技術的負債(Tech Debt)とインシデントを解消しながら、モダン化を進めつつスプリントを進めるといったゲームになります。

## ゲーム画面
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/82053b07-a002-4b8d-a8f7-b06bb251b40b.png)


## ゲーム概要
```
ゲーム概要: "Legacy Burst"

世界観

あなたはプロジェクトマネージャー。巨大なレガシーシステムを抱えた企業で、
モダン化プロジェクトを進めながら日々の障害に対処する。

レガシーシステムは毎ターン「技術的負債(Tech Debt)」と「インシデント」を生み出し続ける。

ターン構造（1ターン = 1スプリント）

1. ドロー       : デッキから5枚引く
2. プレイ       : Budgetを消費してカードを使用（数字キー1〜5）
3. チーム効果   : 配置済みエンジニアのパッシブ効果を適用
4. レガシーAI   : 技術的負債(Tech Debt)・インシデントを自動生成
5. スプリント終了（Space）
6. ドラフト     : 3枚から1枚選んでデッキに追加
```

<br>

さっそく遊んでみたところ、ゲームシステムは意外なほどにしっかりしており、またシステム開発という点でのエスプリも効いていて、**下手にスペック駆動開発するより全然いいものができてしまった**感がありました。
~~（絶対にゲームクリアができず、システム開発失敗して終了するというところが一番好み）~~

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/b436545d-e332-491b-a42a-986a5e2e153c.png)



# そしてリファクタリング
ゲームシステム自体は良かったものの、無限にゲームが終わらない（続けられてしまう）といった難易度に関する課題や、やっぱりマウス操作もやりたい、などといった要望が出てきました。
`プレイ(人間)＆コメント(人間)`と`リファクタリング(Claude)`を進め、とりあえずマトモっぽくなった版の画面イメージとソースコードが以下になります。

## ゲーム画面
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/201787/7b93f831-4c41-4f28-9935-ced2e89ef19f.png)



## リファクタリング内容

<!-- open属性なし -->
<details><summary>リファクタ内容一覧</summary>


```plaintext
●以下が初期版（r1）から現在版への改善点の全リストです。

  ---
  機能改善ポイント一覧

  ゲームバランス調整（難易度強化）

  - Health 初期値変更: 30 → 12（大幅に緊張感を高める）
  - 初期Tech Debt: 0 →13（ゲーム開始直後から負債プレッシャーが存在）
  - Tech Debt 自動発生量増加: +1〜3/sprint →+2〜5/sprint（後半はさらに増加）
  - Tech Debt 複利発生: Debt が 15 を超えると毎スプリント利子が加算
  - Tech Debt フロア導入: floor(sprint/3) を下限とし、後半は削りきれなくなる
  - intensityキャップ引き上げ: sprint12 頭打ち →sprint20 まで増加し続ける
  - インシデントのダメージ引き上げ: COMMON 1→2、RARE2→3、EPIC2〜3→3〜4
  - インシデント発生確率上昇: baseP 0.30 →0.45、第2ロール base 0.10 →0.20
  - Sprint1から脅威あり: initGame() で legacyAI() を先行実行、初手からDebt・インシデントが存在

  インシデント拡充

  - インシデント種類を倍増: 8件 → 31件（COMMON×11、RARE×11、EPIC×9）
  - Debt発生インシデントを大量追加: 設計書なし・コーディング規約違反・アーキテクチャ腐敗・負債連鎖など15件
  - レアリティ別色分け表示: COMMON/RARE/EPICでインシデントカードの見た目を分離
  - RARE出現タイミング早期化: sprint5 →sprint3
  - EPIC出現タイミング早期化: sprint10 → sprint7
  - インシデント最大保有数拡大: 4件 →5件
  - 第3ロール追加: sprint8以降、連鎖インシデントが追加発生する可能性
  - エスカレーション機能: 放置インシデントはage増加し、age2でダメージ+1、age3でDebt+3追加（⬆AGE/⬆⬆ESC表示）

  カード調整

  - patch カード強化: インシデント解決時に Budget +1 を付与
  - rollback カード調整: 全件消去 →2件のみ消去に制限、回復効果(Health+2)を削除
  - container / cicd / cdn カード変更: Health回復効果を廃止 →Tech Debt削減に変換（HP回復源を絞ることで緊張感を演出）
  - SREエンジニアパッシブ変更: Health +lv/sprint（最大+3）→固定 +1/sprint（過剰な回復を制限）
  - 初期デッキ調整: refactor 5枚 →3枚、test_add 3枚 →4枚、docs 1枚追加

  Budget システム変更

  - Budget持越し制導入: 毎スプリントリセットから +3加算・持越し方式に変更
  - Budget上限撤廃: maxBudgetの概念を廃止、上限なしに蓄積可能
  - 表示変更: Budget: X/Y →Budget: X（シンプルに）

  初期状態改善

  - 初期手札にエンジニア1名を確定配置: ゲーム開始時から戦略的選択が発生

  UI・操作性改善

  - マウスクリック操作の追加（キーボードは引き続き使用可）
    - Actionカード: 1クリック選択 →2クリック目で実行
    - Engineerカード: 選択後にTeam Zoneのスロットをクリックで配置
    - Card Draft: 1クリック選択 →2クリック目または「入手する」ボタンで確定
  - スプリント終了ボタン: 大きな緑のボタンを手札下に追加、フェーズ外は自動でグレーアウト
  - ドラフト確定・スキップボタン追加: マウスのみでドラフト操作が完結
  - Team Zoneスロットのクリック対応: エンジニア選択中はスロットが黄色ハイライト＆クリック可能
  - デッキ一覧オーバーレイ追加: [L]キーで全保有カードを一覧表示
  - ヘルプオーバーレイ追加: [H]キーでゲームルールを全画面表示
  - キーボード操作拡充: [←][→]でカード移動選択、[7][8][9]でスロット直接指定、エンジニア入れ替え対応
  - エンジニアスロット入れ替え機能: Team Zone満員でも[7][8][9]で既存メンバーと入れ替え可能
  - インシデント詳細表示強化: レアリティ・副次効果・エスカレーション状態を表示

  ゲームオーバー画面の改善

  - タイトル変更: 「SYSTEM DOWN」→「PROJECT COLLAPSE」
  - 5段階ランク評価追加: Sprint数・Modernization Scoreそれぞれの閾値の低いほうで S/A/B/C/D を判定
  - ランク別カラー表示: S=金、A=青、B=緑、C=橙、D=赤

```
</details>


## Legacy Burst


<!-- open属性なし -->
<details><summary>htmlファイルはこちら</summary>


```html:legacy_burst.html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Legacy Burst — System Renewal Simulation</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#080c18;color:#c8d8e8;font-family:'Courier New',Courier,monospace;font-size:13px;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:16px}
#app{width:920px;max-width:100%}

/* HEADER */
#hdr{display:flex;justify-content:space-between;align-items:center;background:#0b1222;border:1px solid #1e3a5f;padding:8px 14px;margin-bottom:6px;border-top:2px solid #4fc3f7}
#title{color:#4fc3f7;font-size:18px;font-weight:bold;letter-spacing:3px}
#stats{display:flex;gap:14px}
.st{display:flex;flex-direction:column;align-items:center;gap:1px}
.sl{color:#3a5a78;font-size:9px;text-transform:uppercase;letter-spacing:.5px}
.sv{font-weight:bold;font-size:15px}
.sv.g{color:#4caf50}.sv.r{color:#ef5350}.sv.y{color:#ffd54f}.sv.p{color:#ce93d8}.sv.b{color:#4fc3f7}.sv.d{color:#607d8b}

/* HEALTH BAR */
.hbw{width:70px;height:3px;background:#1e3a5f;border-radius:2px;margin-top:2px}
.hb{height:100%;border-radius:2px;transition:width .3s}
.hb.g{background:#4caf50}.hb.y{background:#ff9800}.hb.r{background:#ef5350}

/* SECTION */
.sec{background:#0b1222;border:1px solid #1e3a5f;padding:8px 12px;margin-bottom:6px}
.sec-h{color:#3a5a78;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;border-bottom:1px solid #1a2e45;padding-bottom:3px}

/* INCIDENTS */
#inc-list{display:flex;gap:8px;flex-wrap:wrap;min-height:24px;align-items:center}
.inc{background:#2e1010;border:1px solid #7a1a1a;padding:3px 8px;border-radius:3px;color:#ff7070;font-size:11px}
.inc.rare{background:#2a1840;border-color:#8030c0;color:#d090f0}
.inc.epic{background:#3a0505;border-color:#cc1a00;color:#ff6040;font-weight:bold}
.inc-rb{display:inline-block;font-size:8px;padding:0 3px;border-radius:2px;margin-right:4px;vertical-align:middle}
.inc-rb.common{background:#3a1a1a;color:#ff7070}
.inc-rb.rare{background:#3a1a50;color:#d090f0}
.inc-rb.epic{background:#4a0a0a;color:#ff6040}
.no-inc{color:#1e3a20;font-size:11px}

/* TEAM */
#team{display:flex;gap:8px}
.ts{flex:1;min-height:72px;border:1px dashed #1a2e45;border-radius:3px;padding:7px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;transition:border-color .15s,background .15s}
.ts.occ{border-style:solid}
.ts.occ.common{border-color:#455a64;background:#0a1520}
.ts.occ.rare{border-color:#1565c0;background:#0b1624}
.ts.occ.epic{border-color:#6a1b9a;background:#120b20}
.ts.swap-tgt{border-color:#ffd54f!important;background:#161400!important}
.eng-name{font-size:11px;font-weight:bold;color:#90caf9;margin-bottom:2px}
.eng-lv{font-size:11px;color:#ffd54f}
.eng-xp{font-size:10px;color:#3a5a78;margin-top:1px}
.eng-pas{font-size:9px;color:#80cbc4;margin-top:3px;line-height:1.3}
.ts-empty{color:#1e3050;font-size:11px}
.ts-slot-key{font-size:11px;color:#ffd54f;font-weight:bold;margin-bottom:4px}

/* HAND */
#hand{display:flex;gap:7px;flex-wrap:wrap;min-height:110px;align-items:flex-start}
.card{width:155px;border:1px solid #1a2e45;border-radius:3px;padding:7px;cursor:pointer;background:#090f1c;transition:border-color .12s,background .12s;position:relative;flex-shrink:0}
.card:hover{border-color:#3a7aaa}
.card.sel{border-color:#ffd54f!important;background:#161400;box-shadow:0 0 10px rgba(255,213,79,.35)}
.card.dim{opacity:.35}
.card.common{border-left:3px solid #455a64}
.card.rare{border-left:3px solid #1565c0}
.card.epic{border-left:3px solid #6a1b9a}
.c-key{position:absolute;top:4px;right:6px;color:#3a5a78;font-size:10px}
.c-rb{display:inline-block;font-size:8px;padding:1px 3px;border-radius:2px;margin-bottom:3px}
.c-rb.common{background:#263238;color:#90a4ae}
.c-rb.rare{background:#0d2a6e;color:#90caf9}
.c-rb.epic{background:#36006e;color:#ce93d8}
.c-name{font-size:12px;font-weight:bold;color:#c8d8e8;margin-bottom:3px;padding-right:16px}
.c-cost{font-size:11px;color:#ffd54f;margin-bottom:2px}
.c-type{font-size:9px;color:#3a5a78;margin-bottom:3px}
.c-desc{font-size:9px;color:#607d8b;line-height:1.4}
.c-hint{font-size:9px;color:#ffd54f;margin-top:4px}
.hand-empty{color:#1e3050;font-size:11px;align-self:center;margin:auto}

/* CONTROLS */
#ctrl{color:#2e4a62;font-size:11px;padding:5px 12px;text-align:center;background:#080c18;border:1px solid #111d2e;margin-bottom:6px}
#ctrl b{color:#4fc3f7}

/* LOG */
#log{height:75px;overflow-y:auto;font-size:11px;line-height:1.6}
.le{border-bottom:1px solid #0b1222;padding:0 1px}
.le.imp{color:#c8d8e8}.le.suc{color:#4caf50}.le.war{color:#ff9800}.le.dan{color:#ef5350}.le.inf{color:#4fc3f7}.le.def{color:#3a5a78}

/* PHASE */
#phase{text-align:center;font-size:10px;color:#2e4a62;margin-bottom:4px}
#phase .act{color:#ffd54f}

/* DRAFT OVERLAY */
#draft-ov{display:none;position:fixed;inset:0;background:rgba(0,0,0,.88);justify-content:center;align-items:center;z-index:100}
#draft-ov.on{display:flex}
#draft-panel{background:#0b1222;border:2px solid #1e3a5f;padding:22px;width:620px;max-width:95vw;border-top:2px solid #4fc3f7}
.draft-title{color:#4fc3f7;font-size:15px;margin-bottom:4px;letter-spacing:1px}
.draft-sub{color:#3a5a78;font-size:11px;margin-bottom:14px}
#draft-cards{display:flex;gap:10px}
.dc{flex:1;border:1px solid #1a2e45;border-radius:3px;padding:10px;cursor:pointer;background:#090f1c;transition:border-color .12s,background .12s}
.dc:hover,.dc.sel{border-color:#ffd54f;background:#161400}
.dc.common{border-left:3px solid #455a64}
.dc.rare{border-left:3px solid #1565c0}
.dc.epic{border-left:3px solid #6a1b9a}
.dc-key{color:#ffd54f;font-size:13px;font-weight:bold;margin-bottom:5px}

/* DECK VIEW OVERLAY */
#deck-ov{display:
