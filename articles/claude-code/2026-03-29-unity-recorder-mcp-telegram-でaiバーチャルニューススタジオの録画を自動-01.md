---
id: "2026-03-29-unity-recorder-mcp-telegram-でaiバーチャルニューススタジオの録画を自動-01"
title: "Unity Recorder × MCP × Telegram で、AIバーチャルニューススタジオの録画を自動化する"
url: "https://zenn.dev/acropapa330/articles/unity_recorder_ai_studio"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

# Unity Recorder × MCP × Telegram で、AIバーチャルニューススタジオの録画を自動化する

## はじめに

前回の記事（[WSL2 × Claude Code × Unity MCPで、AIにUnityを操作させる](./unity_mcp_wsl_claude)）では、WSL2 環境から Claude Code + MCP 経由で Unity を操作できるようにしました。

今回はその延長として、**Unity Recorder を使ってバーチャルスタジオの映像を録画する**ところまでを整えました。

最終ゴールはこちら：

```
毎朝自動でニュース収集
  → 原稿生成
  → TTS音声合成
  → Unity でクロエちゃん（VRMアバター）がニュースを読む
  → 録画 → YouTube自動アップ
```

この記事では **Unity Recorder のセットアップから、MCP経由での制御方針まで** をまとめています。

---

## 環境

| 項目 | 内容 |
| --- | --- |
| OS | Windows 11 + WSL2 (Ubuntu) |
| Unity | 2022 LTS |
| MCP for Unity | CoplayDev/unity-mcp |
| Claude Code | WSL2 側で起動 |
| Telegram Bot | クロエちゃん（Python製） |

---

## Step 1: Unity Recorder のインストール

### Package Manager から追加

1. Unity Editor で `Window` → `Package Manager` を開く
2. 左上のドロップダウンで **Unity Registry** を選択
3. 検索欄に `Recorder` と入力
4. **Unity Recorder** を選んで `Install`

インストール後、`Window` → `General` → `Recorder` → `Recorder Window` が使えるようになります。

### MCP 経由で確認

インストール前に MCP 経由でメニューを確認したところ、`Window/General/Recorder` のエントリが存在しないことで未インストールを検知できました。Unity の状態チェックにも MCP が役立ちます。

---

## Step 2: Recorder ウィンドウの設定

`+ Add Recorder` → `Movie` を選択し、以下の設定を行います。

| 設定項目 | 推奨値 |
| --- | --- |
| **Source** | Game View |
| **Output File > Path** | `C:/work/GDrive/videos/` |
| **Output File > File Name** | `yabou01_<Take>` |
| **Format** | MP4 (H.264) |
| **Resolution** | Match Window Size または 1920x1080 |
| **Frame Rate** | 30 fps |

**`<Take>` は連番で自動インクリメント**されるので、複数回録画してもファイルが上書きされません。

出力先を Google Drive Desktop の同期フォルダ（`C:/work/GDrive/videos/`）にしておくと、WSL2 側から `/mnt/c/work/GDrive/videos/` としてアクセスできて便利です。

---

## Step 3: バストショットカメラの設定

録画前に Main Camera をニュース番組風のバストショットに調整しました。

MCP 経由で取得した最終的なカメラ設定：

```
{
  "position": { "x": 0.0, "y": 1.572, "z": 1.753 },
  "rotation": { "x": 8.0, "y": 0.0, "z": 0.0 },
  "fieldOfView": 50
}
```

* **Z が正値（1.753）** → クロエちゃんの正面から撮影
* **Y = 1.572** → 胸の高さにカメラを置く
* **FOV = 50°** → ポートレート向けの狭め設定
* **X 回転 = 8°** → 自然な見下ろし角度

> ポイント：MCP 経由でカメラ値を取得できるので、手動で調整した位置をプログラムで記録・再現できます。

---

## Step 4: ライティング設定（3点ライティング）

MCP 経由で以下の3点ライティングを設定しています。

| ライト | 色 | 役割 |
| --- | --- | --- |
| キーライト | 暖色（#FFF5E0） | メインの光源 |
| フィルライト | クールホワイト（#E0EEFF） | 影を和らげる |
| リムライト | ライトブルー（#C0D8FF） | 輪郭を際立てる |

これにより、アバターが暗くつぶれず、ニュース番組らしい清潔感のある映像になります。

---

## Step 5: 手動録画テスト

Recorder ウィンドウの `Start Recording` → 数秒後に `Stop Recording` で録画完了。

`C:/work/GDrive/videos/yabou01_1.mp4` が生成されることを確認しました。

**確認チェックリスト：**

---

## Step 6: MCP 経由での録画自動化（方針）

Unity Recorder をプログラムから制御するには、**C# スクリプトからメニューアイテムとして呼び出す形**が現実的です。

```
// Editor/RecorderController.cs
using UnityEngine;
using UnityEditor;
using UnityEditor.Recorder;
using UnityEditor.Recorder.Input;

public class RecorderController
{
    [MenuItem("Tools/StartRecording")]
    public static void StartRecording()
    {
        // RecorderControllerSettings を使って録画開始
        var controllerSettings = ScriptableObject.CreateInstance<RecorderControllerSettings>();
        var controller = new RecorderController(controllerSettings);

        var videoRecorder = ScriptableObject.CreateInstance<MovieRecorderSettings>();
        videoRecorder.name = "yabou01";
        videoRecorder.Enabled = true;
        videoRecorder.OutputFile = "C:/work/GDrive/videos/yabou01_<Take>";
        videoRecorder.ImageInputSettings = new GameViewInputSettings
        {
            OutputWidth = 1920,
            OutputHeight = 1080
        };
        videoRecorder.EncoderSettings = new CoreEncoderSettings
        {
            Codec = CoreEncoderSettings.OutputCodec.MP4
        };

        controllerSettings.AddRecorderSettings(videoRecorder);
        controllerSettings.SetRecordModeToFrameInterval(0, 300); // 0〜300フレーム

        controller.PrepareRecording();
        controller.StartRecording();

        Debug.Log("録画開始");
    }

    [MenuItem("Tools/StopRecording")]
    public static void StopRecording()
    {
        // 実装省略
        Debug.Log("録画停止");
    }
}
```

このスクリプトを `Assets/Editor/` に置けば、MCP の `execute_menu_item` ツールで呼び出せます：

```
# Python側からMCP経由で録画開始
response = requests.post("http://127.0.0.1:8081/mcp", json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "execute_menu_item",
        "arguments": {"menuPath": "Tools/StartRecording"}
    }
})
```

---

## パイプライン全体像

yabou01 の最終的な自動化フローは以下の予定です：

```
pipeline_all.py
├── Phase 1: ニュース収集 & 原稿生成
├── Phase 2: TTS音声合成（VOICEVOX）
├── Phase 3: 仮想スタジオ録画（Unity Recorder）← ここ
│   ├── MCP経由で録画開始
│   ├── 音声ファイルを Unity に渡す
│   └── 録画停止 → MP4取得
├── Phase 4: BGM合成・サムネイル生成
└── Phase 5: YouTube自動アップロード
```

---

## まとめ

| ステップ | 状態 |
| --- | --- |
| Unity Recorder インストール | ✅ |
| 録画設定（MP4, Game View, 30fps） | ✅ |
| バストショットカメラ調整 | ✅ |
| 3点ライティング | ✅ |
| 手動録画テスト | ✅ |
| MCP経由での自動録画 | 🔜 実装中 |

Unity Recorder は GUI 操作が主体ですが、C# スクリプトと MCP を組み合わせることで **Telegram から録画を開始・停止する**ところまで自動化できます。

次回は実際に音声と映像を組み合わせたフル自動パイプラインを試していきます。

---

## 関連記事
