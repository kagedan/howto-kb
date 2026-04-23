---
id: "2026-03-21-ゲーム開発記録-２unityclaudecode-01"
title: "ゲーム開発記録 #２｜Unity×ClaudeCode"
url: "https://note.com/niwabi_99/n/neaf72fa05a67"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

### はじめに

「Ad Lucem」というゲームを作っています。

企画フェーズが完了し、今日からプロトタイプフェーズに入りました。この記事では今日やったことを技術的な詰まりポイントも含めて正直に書いていきます。  
  
CCが何でもやってくれるわけではないので慣れないUnityを手探りで作業してます。

---

## 今日やったこと

* Tilemapの設定をイチからやり直し
* タイルを使ってステージを作成
* プレイヤーがステージ上を走れるように
* 敵（EnemyController）の実装と配置
* プレイヤーの仮近接攻撃の実装

---

## Tilemapでステージを作る

### Rule Tileとは

UnityのTilemapでは「Rule Tile」というアセットを使うと、隣接するタイルの状況に応じて自動的に見た目が変わるタイルを作れます。地面の端っこは角丸に、真ん中はフラットに、といった表現が自動でできるやつです。

今回はまず動作確認用の仮素材として、UnityのデフォルトスプライトをRule Tileに設定しました。

### 詰まったポイント①　ファイル名問題

Rule Tileを作ったら Main Object Name 'GroundTile' does not match filename 'GroundTile 1' という警告が出ました。

原因は過去に作ったファイルが GroundTile 1 という名前で残っていたこと。Projectウィンドウ上でリネームして解決しました。**Finderでリネームすると.metaファイルが壊れる**ので必ずUnity上で操作するのが正解です。

### 詰まったポイント②　スプライトが見つからない

Rule TileのDefault Spriteに設定するスプライトを探したら最初は見つかりませんでした。Select Spriteウィンドウで **「In Packages」タブ** に切り替えることで UISprite などのデフォルトスプライトが表示されます。

最終的には Create → 2D → Sprites → Square で生成したSquareスプライトを使いました。これが一番タイルらしくきっちり並んで正解でした。

### Tilemapにコライダーを追加する

タイルを描いただけではプレイヤーが地面を突き抜けてしまいます。以下のコンポーネントをTilemapに追加します。

1. **Tilemap Collider 2D** を追加
2. **Composite Collider 2D** を追加（物理演算を滑らかにする）
3. 自動追加されるRigidbody2Dの **Body Type を Static** に変更
4. Tilemap Collider 2Dの **Composite Operation を Merge** に変更

※Unity 6では「Used By Composite」という項目がなくなり、「Composite Operation」に変わっています。

### 詰まったポイント③　LayerをGroundに設定し忘れた

PlayerControllerの地面判定は groundLayer というLayerMaskを参照しています。TilemapのLayerがDefaultのままだとプレイヤーが地面にいるのに空中判定になり、2段ジャンプがおかしくなりました。

TilemapのLayerを **Ground** に変更して解決。地味ですが見落としやすいポイントです。

---

## 敵を実装する

### EnemyController.cs

敵の基本動作として以下を実装しました。

* **パトロール**：startPositionを起点に±patrolDistanceの範囲を左右に往復
* **HP制**：TakeDamage(int amount) メソッドを外部公開
* **死亡演出**：SpriteRendererの点滅後にDestroy
* **接触ダメージ**：OnCollisionEnter2DでPlayerタグを検出してダメージを与える

敵はスキルを失わない仕様（プレイヤーが「同じ力を得る」だけ）なので、SkillAbsorbable コンポーネントは別途アタッチする設計にしています。

### 詰まったポイント　Collider2Dが必要

EnemyControllerには [RequireComponent(typeof(Collider2D))] がついています。EnemyControllerをアタッチする前に **Box Collider 2D** を追加しておかないとエラーになります。コンポーネントのアタッチ順に注意。

---

## 仮近接攻撃を実装する

スキルシステムはまだ未実装なので、動作確認用の仮攻撃を実装しました。

### 詰まったポイント　エフェクトが固定座標に出た

LineRendererのデフォルト設定では **Use World Space** がオンになっています。これだとプレイヤーが動いてもエフェクトが最初の座標に固定されてしまいます。

**Use World Space のチェックを外す**ことでPlayerの子オブジェクトとしてローカル座標で描画され、プレイヤーにくっついて動くようになりました。

---

## 今日の成果

白い四角が白い四角を攻撃して倒す、という段階ですがゲームの骨格が動き始めました。

---

## 次回予定

* スキル吸収システムの実装
* プレイヤーの死亡・リスポーン処理
* 最初のステージの本格的な作り込み

---

Ad Lucem — 光へ、真実へ、知性へ。
