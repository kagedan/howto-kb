---
id: "2026-04-03-cesium-for-unity-東京3dマップで鬼ごっこゲームを作ったmixamoキャラレーダーu-01"
title: "Cesium for Unity × 東京3Dマップで鬼ごっこゲームを作った【Mixamoキャラ・レーダーUI追加】"
url: "https://zenn.dev/acropapa330/articles/tokyo_tag_game_cesium"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

# Cesium for Unity × 東京3Dマップで鬼ごっこゲームを作った【地面落下バグとの戦い】

## はじめに

「現実の東京を舞台にした鬼ごっこゲームが作りたい」という思いつきから、**Cesium for Unity** を使ってリアルな東京の3D建物マップでプレイできる鬼ごっこゲームを作りました。

完成してみたら**鬼に本当に捕まった**ので、ゲームとして成立していました笑

ただし、Cesium を使ったゲーム開発には独特のハマりポイントがありました。特に **「プレイヤーが地面を突き抜けて Y=-451 まで落下する」** 問題には相当悩まされました。この記事ではその解決策を中心に記録します。

## デモ動画

実際のプレイ動画です。Cesiumの東京3Dマップ上でRemyが走り回り、Mutantに追いかけられます。

## 使用技術

* Unity 2022 LTS
* Cesium for Unity 1.23.0
* Japan 3D Building Data（Cesium ion / PLATEAU ベース）
* Mixamo（3Dキャラクター・アニメーション）
* Claude Code（スクリプト生成・デバッグ補助）

## ゲーム概要

| 項目 | 内容 |
| --- | --- |
| ジャンル | 三人称視点・鬼ごっこ |
| マップ | 東京（新宿御苑周辺）の実際の3D建物 |
| 勝利条件 | タイマー（60秒）が切れるまで逃げ切る |
| 敗北条件 | 鬼に距離2m以内まで近づかれる |
| 操作 | WASD移動、Shift でスプリント、Space でジャンプ、マウスでカメラ |

## 実装したスクリプト

```
Assets/Scripts/
├── Player/
│   ├── PlayerController.cs   # 移動・カメラ・ジャンプ・落下検知・アニメーション
│   └── GroundFinder.cs       # Cesiumタイル読み込み後に地面着地
├── Enemy/
│   └── OniController.cs      # 鬼のAI（追跡・巡回）・アニメーション
├── Game/
│   └── GameManager.cs        # ゲーム状態管理・ローディング待機
├── UI/
│   ├── GameUI.cs             # ローディング画面・タイマー・勝敗表示
│   └── RadarUI.cs            # レーダーUI（半径10mの鬼位置表示）
└── Editor/
    └── TokyoTagSetup.cs      # セットアップ自動化（Editor拡張）
```

## 最大のハマり：プレイヤーが Y=-451 に落下する

### 問題

Unity の Play を開始した直後、コンソールに以下のログが出ていました：

```
[Oni] Player found: Player at (12.67, -451.70, 12.67)
```

**プレイヤーが地面の遥か下に落下していた**のです。

### 原因

Cesium for Unity は起動時に 3D タイルをオンラインから非同期でダウンロードして、コライダーを生成します。

**Play 開始直後はまだ地面のコライダーが存在しない**ため、CharacterController がすり抜けてどこまでも落下してしまいます。

```
Play開始
 ↓
Cesiumタイルのダウンロード開始（数秒〜数十秒かかる）
 ↓  ← この間、地面コライダーなし
プレイヤーが落下しまくる
 ↓
Cesiumタイル生成完了（遅い）
 ↓
プレイヤーはもう Y=-451 にいる
```

### 解決策：GroundFinder

`GroundFinder.cs` というコンポーネントを作成しました。

動作の流れ：

1. Start() で CharacterController を一時停止（落下防止）
2. 一定間隔（0.5秒）で真下にレイキャストを飛ばす
3. Cesium コライダーが生成されたら地面の Y 座標を取得して着地
4. タイムアウト（15秒）したらフォールバック座標（Y=5）にテレポート

```
IEnumerator FindGroundAndLand()
{
    // CharacterController を一時停止して落下を防ぐ
    if (_cc != null) _cc.enabled = false;

    float elapsed = 0f;
    bool found = false;

    while (elapsed < maxWaitSeconds)
    {
        // 現在の XZ 位置から高い Y でレイキャスト
        Vector3 origin = new Vector3(transform.position.x, raycastFromY, transform.position.z);
        RaycastHit hit;

        if (Physics.Raycast(origin, Vector3.down, out hit, raycastDistance))
        {
            float groundY = hit.point.y + landingOffset;
            Debug.Log($"[GroundFinder] Ground found at y={groundY:F1} (hit: {hit.collider.name})");
            Teleport(new Vector3(transform.position.x, groundY, transform.position.z));
            found = true;
            break;
        }

        elapsed += retryInterval;
        yield return new WaitForSeconds(retryInterval);
    }

    if (!found)
    {
        // フォールバック：Cesiumタイル未ロード時
        Teleport(new Vector3(transform.position.x, 5f, transform.position.z));
    }

    if (_cc != null) _cc.enabled = true;
    _landed = true;  // ← GameManager がこれを待つ
}
```

ポイントは `IsLanded` プロパティです：

```
public bool IsLanded => _landed;
```

これを `GameManager` が参照することで、**プレイヤーと鬼が両方着地するまでゲームを開始しない**仕組みにしました。

## ゲーム開始をCesiumロードに合わせる

### GameManager のローディング待機

```
IEnumerator WaitForGroundAndStart()
{
    GroundFinder playerGF = null, oniGF = null;
    float elapsed = 0f;

    while (elapsed < loadingTimeout)  // 最大30秒待つ
    {
        // Player・Oni の GroundFinder を取得
        if (playerGF == null)
        {
            var p = GameObject.FindGameObjectWithTag("Player");
            if (p != null) playerGF = p.GetComponent<GroundFinder>();
        }
        if (oniGF == null)
        {
            var o = GameObject.FindGameObjectWithTag("Oni");
            if (o != null) oniGF = o.GetComponent<GroundFinder>();
        }

        // 両方着地完了でゲーム開始
        bool playerReady = playerGF == null || playerGF.IsLanded;
        bool oniReady    = oniGF    == null || oniGF.IsLanded;

        if (playerReady && oniReady)
        {
            Debug.Log($"[TagGame] 着地完了！ゲーム開始（{elapsed:F1}秒待機）");
            break;
        }

        elapsed += Time.deltaTime;
        yield return null;
    }

    IsLoading = false;
    StartGame();
}
```

### UI でローディング中を表示

`OniController` も `GameManager.IsPlaying` が `false` の間は動かないようにしています：

```
void Update()
{
    if (GameManager.Instance != null && !GameManager.Instance.IsPlaying)
        return;  // ローディング中は動かない
    // ...
}
```

これにより：

1. Play 開始 → 「マップ読み込み中...」画面を表示
2. プレイヤー・鬼が両方着地 → ゲーム開始
3. タイマースタート・鬼が追いかけてくる

という自然な流れになりました。

## 鬼のAI

鬼は距離に応じて速度を変える追跡 AI です：

```
void ChasePlayer(float dist)
{
    // 近いと全力ダッシュ、遠いと通常速度
    float speed = dist < sprintStartDistance ? sprintSpeed : chaseSpeed;

    Vector3 dir = (_player.position - transform.position);
    dir.y = 0;
    dir.Normalize();

    Vector3 move = dir * speed;
    move.y = _verticalVelocity;
    _cc.Move(move * Time.deltaTime);
}
```

| パラメータ | 値 |
| --- | --- |
| 通常追跡速度 | 3 m/s |
| スプリント速度 | 5.5 m/s |
| スプリント開始距離 | 10m 以内 |
| 捕捉距離 | 2m |

## Cesium の SSL エラーについて

ログに大量に出ていたこのエラーは**タイル画像（空撮テクスチャ）の読み込み失敗**です：

```
Exception while creating asset: Request for https://assets.ion.cesium.com/...
failed: Unable to complete SSL connection
```

ゲームロジック（コライダー、3D建物）には影響しないため、**建物は表示されてゲームは問題なく動作します**。テクスチャなしのグレーの建物になりますが、鬼ごっこは普通にプレイできます。

根本解決したい場合は：

* Windows の証明書ストアを更新（`certmgr.msc` → 信頼されたルート証明機関）
* Unity の **Edit → Project Settings → Player → Other Settings** で TLS 設定を確認

## 動作結果

実際にプレイしたところ、**鬼に捕まりました**笑

鬼のAIが正常に追跡して、距離2mでタグ判定が機能していることを確認。Cesiumの東京3Dマップ上でゲームとして成立しています。

コンソール出力：

```
[GroundFinder] Ground found at y=-0.5 (hit: InvisibleGround)
[TagGame] 着地完了！ゲーム開始（0.0秒待機）
[TagGame] Caught! Game Over.
```

## キャラクターの見た目を改善：Mixamo導入

プリミティブ（カプセル＋球体）からMixamoの3Dキャラクターに差し替えました。

### キャラクター選定

| キャラ | Mixamoモデル | 理由 |
| --- | --- | --- |
| Player | Remy | 親しみやすい人型 |
| 鬼（Oni） | Mutant | モンスター感があってゲームに合う |

### Mixamoからダウンロードする設定

| 設定 | 値 |
| --- | --- |
| Format | FBX for Unity |
| Skin | **With Skin**（最初の1ファイルのみ）、以降は **Without Skin** |
| Keyframe Reduction | **None**（Root Motionずれ防止のため重要！） |

ダウンロードしたFBX：

```
Assets/Characters/
├── Remy@Idle.fbx          ← With Skin
├── Remy@Running.fbx       ← Without Skin
├── Remy@Walking To Dying.fbx
├── Mutant@Orc Idle.fbx    ← With Skin
├── Mutant@Running.fbx     ← Without Skin
└── Mutant@Mutant Dying.fbx
```

### ハマり：MutantはGenericリグが正解

`Mutant@Orc Idle.fbx` の Rig を Humanoid に設定すると、Inspectorにエラーが出ます。MutantはモンスターでHumanoidのボーン構造（背骨・首・膝など）が標準人体と一致しないためです。

**解決策：Animation Type を Generic に変更**

```
Mutant@Orc Idle.fbx → Rig → Animation Type: Generic → Apply
（Runningとdyingも同じく Generic に設定）
```

Humanoid限定の機能（AvatarMask等）は使えなくなりますが、アニメーション自体は問題なく動作します。

### ハマり：Running FBXのRoot Motionで位置がずれる

MixamoのRunningアニメーションはデフォルトで**Root Motion**（アニメーション自体に前進の移動量が含まれている）になっています。これをそのままUnityに取り込むと、CharacterControllerで移動させているのに**アニメーションが勝手に前進して位置がずれる**問題が起きます。

試みた対策と結果：

| 試みた対策 | 結果 |
| --- | --- |
| `animator.applyRootMotion = false` | Genericリグでは効かないことがある |
| FBXインポーターで `lockRootPositionXZ = true` | 効果なし |
| `LateUpdate()` でローカル位置をリセット | 部分的に改善するが不完全 |
| **FBXをKR:Noneで作り直し** | **完全解決** |

**根本解決：** MixamoでダウンロードするときのKR（Keyframe Reduction）を **None** にすると、Root Motionのカーブが正しく除去された状態でダウンロードされます。

### アニメーションのループ設定

MixamoのFBXはデフォルトでループが無効です。`TokyoTagSetup.cs` でインポート時に自動でループを有効化します：

```
foreach (var clip in animationImporter.clipAnimations)
{
    var settings = AnimationUtility.GetAnimationClipSettings(clip);
    settings.loopTime = true;
    AnimationUtility.SetAnimationClipSettings(clip, settings);
}
animationImporter.SaveAndReimport();
```

### Animator Controller の構成

PlayerとOniそれぞれに Animator Controller を自動生成：

```
[Idle] --IsRunning=true--> [Run]
[Idle] --IsDead=true-----> [Die]
[Run]  --IsRunning=false-> [Idle]
```

### ハマり：Cesium地形の実際のYが0より低い

Mixamoキャラを導入して気づいたのが、キャラクターが地面から浮いて見える問題です。

原因を調査したところ：

* Unity上でスフィアを置いて地形表面に合わせると Y ≈ **-1.2**
* `InvisibleGround`（フォールバック用の透明な床）は Y=0 に配置していた
* Cesiumの視覚的な地形は Y=0 より**1m以上下**にある

つまりキャラはY=0付近に着地しているのに、目に見える地面は-1.2にあるため「浮いて見える」状態でした。

**解決策：** `InvisibleGround` を Y=-1.2 に下げ、`landingOffset = -0.5f` で着地位置を微調整：

```
// GroundFinder.cs
[SerializeField] float landingOffset = -0.5f;  // 地面ヒット点からのオフセット

float groundY = hit.point.y + landingOffset;
// InvisibleGround Y=-1.2 の場合: -1.2 + (-0.5) = -1.7 → ちょうど足元に合う
```

Cesiumの地形Y座標はエリアによって異なるため、実際にスフィアを置いて確認するのが一番確実です。

### ハマり：Dying アニメーション中に空中で固まる

捕まったとき（Player）や60秒逃げ切り（Oni）の死亡アニメーションで、キャラが空中に浮いたまま固まる問題が発生しました。

**原因：** `CharacterController` が有効なまま死亡アニメーションが再生されると、物理演算との競合が起きる。

**解決策：** ゲーム終了時に CC を無効化してキャラを固定する：

```
// PlayerController.cs - ゲーム終了時
void OnCaught()
{
    _isDead = true;
    if (_cc != null) _cc.enabled = false;  // 物理演算を止める
    _animator?.SetBool("IsDead", true);
}
```

また、Generic リグのキャラ（Mutant）ではアニメーションが `transform.position` を直接書き換えるため、`LateUpdate()` でモデルのY位置を固定する処理も必要でした：

```
// OniController.cs
void LateUpdate()
{
    if (_model != null)
        _model.localPosition = new Vector3(0, 0, 0);
}
```

### 勝利時に鬼が倒れる演出

60秒逃げ切って勝利したとき、鬼（Mutant）が倒れるアニメーションを追加しました：

```
// OniController.cs
public void OnPlayerWon()
{
    _isDefeated = true;
    if (_cc != null) _cc.enabled = false;
    _animator?.SetBool("IsDead", true);
}
```

`GameManager` の `Win()` から `OniController.OnPlayerWon()` を呼ぶだけで、プレイヤーの勝利演出と鬼の敗北演出が同時に発動します。

---

## レーダーUIで鬼の位置を把握

鬼が建物の陰に隠れているとき、プレイヤーは鬼の位置が分からなくなります。そこで画面右上にレーダーを追加しました。

### 仕様

| 項目 | 内容 |
| --- | --- |
| 表示位置 | 画面右上（150×150px） |
| 検出範囲 | 半径10m |
| プレイヤー | 中心の緑ドット |
| 鬼 | 赤ドット（10m以内で点滅） |
| 向き | 上方向 = プレイヤーの前方（カメラ向き） |

### 実装のポイント

`OnGUI()` でリアルタイム描画：

```
void OnGUI()
{
    // レーダー背景（半透明の円）
    GUI.color = new Color(0, 0, 0, 0.6f);
    GUI.DrawTexture(radarRect, _bgTexture);

    // プレイヤーを中心とした相対位置を計算
    Vector3 relPos = oni.position - player.position;

    // カメラのY回転でレーダーの向きを合わせる
    float angle = -Camera.main.transform.eulerAngles.y * Mathf.Deg2Rad;
    float rotX = relPos.x * Mathf.Cos(angle) - relPos.z * Mathf.Sin(angle);
    float rotZ = relPos.x * Mathf.Sin(angle) + relPos.z * Mathf.Cos(angle);

    // レーダー座標に変換
    float radarX = radarCenter.x + (rotX / radarRange) * radarRadius;
    float radarY = radarCenter.y - (rotZ / radarRange) * radarRadius;  // Y軸反転

    // 10m以内なら点滅（0.4秒間隔）
    if (dist <= radarRange * 0.5f)
        blinkToggle = Time.time % 0.4f < 0.2f;

    if (blinkToggle || dist > radarRange * 0.5f)
        GUI.DrawTexture(dotRect, _oniTexture);
}
```

---

## まとめ

| ハマりポイント | 解決策 |
| --- | --- |
| Cesiumタイル読み込み前に地面がなくプレイヤーが落下 | `GroundFinder` でレイキャスト着地待機 |
| ゲームが即開始されて鬼もプレイヤーも落下 | `GameManager` でIsLandedを待ってからStartGame() |
| Cesium SSL エラーが大量に出る | ゲームロジックに無関係なので無視（テクスチャが消えるだけ） |
| MutantのHumanoidリグエラー | Animation Type を Generic に変更 |
| Mixamo RunningのRoot Motionで位置ずれ | Keyframe Reduction を None でダウンロード |
| アニメーションがループしない | TokyoTagSetup.cs でインポート後に loopTime=true を設定 |
| Cesium地形のYが-1.2でキャラが浮いて見える | InvisibleGroundをY=-1.2、landingOffset=-0.5fで調整 |
| Dying時に空中で固まる | ゲーム終了時にCCを無効化、Generic リグはLateUpdateでY固定 |
| 勝利時に鬼が反応しない | GameManager.Win() から OniController.OnPlayerWon() を呼ぶ |
| レーダーで鬼の向きが分からない | カメラのY回転でレーダーを回転させてプレイヤー視点に対応 |

Cesium for Unity は非同期の世界なので、**「コライダーがいつ生成されるかわからない」** という前提でゲームロジックを組む必要があります。Mixamoキャラを使うときはRoot MotionとリグタイプがUnityのお作法と微妙にずれることがあるので注意です。

最終的なゲームの構成：

* **Player**：Remy（Mixamo）+ 三人称カメラ + レーダーUI（右上）
* **鬼**：Mutant（Mixamo, Generic リグ）+ 追跡AI + 勝利時Dying演出
* **マップ**：東京・新宿御苑周辺のCesium 3D建物

---

Claude Code（AIアシスタント）と一緒にデバッグしながら作りました。Y=-451の落下原因特定から、Root Motionのずれ問題、Cesium地形とキャラの高さ合わせまで、ログを読んで原因を絞り込んでもらいながら進めました。
