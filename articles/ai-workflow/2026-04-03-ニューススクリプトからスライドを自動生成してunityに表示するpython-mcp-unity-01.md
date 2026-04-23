---
id: "2026-04-03-ニューススクリプトからスライドを自動生成してunityに表示するpython-mcp-unity-01"
title: "ニューススクリプトからスライドを自動生成してUnityに表示する【Python + MCP + Unity】"
url: "https://zenn.dev/acropapa330/articles/yabou01_slide_mcp_unity"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "Python", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

## はじめに

AIニュース動画自動生成パイプライン **yabou01** の品質改善として、クロエちゃん（VRMアバター）の横に **ニューススライドをリアルタイムで表示する機能** を実装しました。

**実装したこと：**

* ニューススクリプト（Markdown）を解析してスライドPNGを自動生成（Pillow）
* 各ニュース記事のOG画像をスクレイピングしてスライドに埋め込む
* UnityにC#スクリプトを仕込み、MCP経由でPythonからスライドを切り替える
* 録画中、音声の長さに合わせてスライドを自動切り替え

完成イメージ：

```
録画中
  ↓ TTS音声1件分の尺が終わると
  Python → MCP → Unity: "次のスライドに切り替えて"
  ↓
  クロエちゃんの右横のモニターに次のトピックが表示される
```

---

## システム全体像

```
output/scripts/script_*.md     ← Phase 1で生成したニューススクリプト
  ↓ (slide_generator.py)
output/slides/slide_000.png    ← オープニングスライド
output/slides/slide_001.png    ← トピック1（OG画像付き）
output/slides/slide_002.png    ← トピック2
  ...
  ↓ (unity_recorder.py 録画中)
copy → C:\work\GDrive\slides\slide_000.png 〜
  ↓ MCP: pendingSlide = "C:\work\GDrive\slides\slide_001.png"
  ↓
Unity: SlideController が pendingSlide を検知 → テクスチャ差し替え
```

---

## Phase 1: スライド自動生成（Pillow）

### スクリプトMDの解析

Phase 1で生成されるニューススクリプトはこんな形式：

AIと量子コンピュータが変える2026年の技術トレンド

```
### [AI] OpenAIが新モデルを発表

**概要**
OpenAIが次世代モデル「GPT-5」を発表...

**クロエのひと言**
ついに来ましたね！エーアイ業界がまた動きます！

**影響度** ★★★★☆
```

これを `parse_script()` で解析し、トピックごとにデータを取り出します。

```
def parse_script(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")

    # 動画タイトルを取得
    title_match = re.search(r"##\s*動画タイトル\s*\n```\s*\n(.+?)\n```", text, re.DOTALL)
    video_title = title_match.group(1).strip() if title_match else "テックニュース"

    # ### [カテゴリ] タイトル 形式のブロックを抽出
    topics = []
    topic_blocks = re.split(r"\n(?=### [\[【])", text)
    for block in topic_blocks:
        m = re.match(r"### [\[【](.+?)[\]】]\s*(.+?)(?:\n|$)", block)
        if not m:
            continue
        category = m.group(1).strip()
        title    = m.group(2).strip()
        # 概要・コメント・影響度も同様に抽出...
        topics.append({"category": category, "title": title, ...})

    return {"video_title": video_title, "topics": topics}
```

### スライドデザイン（Pillow）

ダークテック系のデザインで各スライドを生成します：

```
# カラーパレット
BG_COLOR     = (10, 14, 30)      # ほぼ黒の濃紺
ACCENT_COLOR = (0, 200, 255)     # シアン
TITLE_COLOR  = (255, 255, 255)   # 白
HIGHLIGHT    = (255, 200, 60)    # ゴールド（影響度★など）

def make_slide(title, category, summary, comment, impact,
               slide_num, total, image_url="") -> Image.Image:
    img  = Image.new("RGB", (1280, 720), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 上部アクセントライン
    draw.rectangle([0, 0, WIDTH, 6], fill=ACCENT_COLOR)

    # 右側にOG画像（あれば）
    if image_url:
        thumb = fetch_image(image_url, 420, 236)
        if thumb:
            img.paste(thumb, (IMG_X, IMG_Y))

    # カテゴリバッジ・タイトル・概要・クロエのひと言・影響度★ を描画
    ...

    return img
```

**ポイント：**

* 日本語フォントは `/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc` を優先で探す
* テキストの折り返しは自前実装（`wrap_text()`）。`font.getbbox()` で幅を計測しながら1文字ずつ追加

### OG画像の取得

ニュース収集時（`news_collector.py`）に各記事ページから `og:image` を取得して保存しておきます：

```
# news_collector.py
from bs4 import BeautifulSoup
import urllib.request

def fetch_article_snippet(url: str) -> tuple[str, str]:
    """記事のスニペットとog:imageを返す"""
    req = urllib.request.Request(url, headers={"User-Agent": "..."})
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    soup = BeautifulSoup(html, "html.parser")

    # og:image タグを取得
    og_image = ""
    og_tag = soup.find("meta", property="og:image")
    if og_tag:
        og_image = og_tag.get("content", "")

    # スニペットも取得（略）
    return snippet, og_image
```

スライド生成側では収集データ（JSON）から `タイトル → image_url` のマップを作り、トピックタイトルとの単語オーバーラップで最も近い画像URLを使います：

```
def find_image_url(topic_title: str, image_map: dict) -> str:
    # 単語オーバーラップで最良一致を選ぶ
    t_words = set(re.findall(r'\w+', topic_title.lower()))
    best_url, best_score = "", 0
    for title, url in image_map.items():
        overlap = len(t_words & set(re.findall(r'\w+', title.lower())))
        if overlap > best_score:
            best_score, best_url = overlap, url
    return best_url if best_score >= 2 else ""
```

---

## Phase 2: UnityにSlideControllerを実装

### SlideController.cs

Python から MCP 経由で `pendingSlide` フィールドを書き換えるだけでスライドが切り替わるようにします。

```
public class SlideController : MonoBehaviour
{
    [Header("MCP制御（外部から設定）")]
    public string pendingSlide = "";  // ← Python から MCP でここを書き換える

    private Renderer _renderer;
    private Texture2D _texture;
    private string _loadedSlide = "";

    void Update()
    {
        // pendingSlide が変わったら即座にテクスチャを差し替え
        if (!string.IsNullOrEmpty(pendingSlide) && pendingSlide != _loadedSlide)
        {
            _loadedSlide = pendingSlide;
            LoadTextureFromPath(pendingSlide);
        }
        // ... ファイル監視（後方互換）
    }

    private void LoadTextureFromPath(string path)
    {
        byte[] data = File.ReadAllBytes(path);
        if (_texture == null)
            _texture = new Texture2D(2, 2, TextureFormat.RGBA32, false);
        _texture.LoadImage(data);
        _texture.Apply();
        _renderer.material.mainTexture = _texture;
        Debug.Log($"[SlideController] スライド更新: {Path.GetFileName(path)}");
    }
}
```

**設計の肝：**

* ファイル監視（ポーリング）ではなく `pendingSlide` プロパティへの直接代入で制御
* `File.ReadAllBytes()` → `LoadImage()` でランタイムにテクスチャを差し替えられる

### SlideMonitorSetup.cs（エディタ拡張）

シーンへのオブジェクト配置を `yabou01/Setup Slide Monitor` メニュー一発で完了させます：

```
[MenuItem("yabou01/Setup Slide Monitor")]
public static void SetupSlideMonitor()
{
    var quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
    quad.name = "SlideMonitor";

    // クロエちゃんの右横・斜め後方に配置（16:9比率）
    quad.transform.position    = new Vector3(1.8f, 1.1f, 0.3f);
    quad.transform.rotation    = Quaternion.Euler(0f, -10f, 0f); // 少し内向き
    quad.transform.localScale  = new Vector3(2.56f, 1.44f, 1f);  // 16:9

    // Unlit/Texture でライティングの影響を受けない
    var mat = new Material(Shader.Find("Unlit/Texture"));
    quad.GetComponent<MeshRenderer>().material = mat;

    quad.AddComponent<SlideController>();
    Debug.Log("[SlideMonitorSetup] SlideMonitor を配置しました");
}
```

---

## Phase 3: PythonからMCP経由でスライドを切り替える

### スライドをWindowsにコピー

WSL側のPNGをMCPで直接渡すことはできないため、先に `C:\work\GDrive\slides\` にコピーします：

```
def copy_slides_to_windows(slide_paths: list[str]) -> list[str]:
    """WSL側のスライドPNGをWindows共有フォルダにコピーして、Windowsパスを返す"""
    win_dir = "/mnt/c/work/GDrive/slides"
    os.makedirs(win_dir, exist_ok=True)

    win_paths = []
    for i, src in enumerate(slide_paths):
        filename = f"slide_{i:03d}.png"
        dst = os.path.join(win_dir, filename)
        shutil.copy(src, dst)
        # Windows形式のパスに変換
        win_path = dst.replace("/mnt/c/", "C:\\").replace("/", "\\")
        win_paths.append(win_path)

    return win_paths
```

### MCP経由でslide切り替え

`manage_components/set_property` ツールで `pendingSlide` を直接セットします：

```
def show_slide(slide_win_path: str) -> bool:
    """MCP経由で SlideController.pendingSlide を更新してスライドを切り替える"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "manage_components",
            "arguments": {
                "action": "set_property",
                "game_object": "SlideMonitor",
                "component_type": "SlideController",  # ← ここが重要！componentType ではない
                "property": "pendingSlide",
                "value": slide_win_path,
            }
        }
    }
    response = requests.post(UNITY_MCP_URL, json=payload, timeout=10)
    return response.status_code == 200
```

**ハマりポイント：** MCP for Unity のパラメータ名は `component_type`（スネークケース）です。`componentType`（キャメルケース）では無視されて失敗します。

---

## 録画パイプラインへの組み込み

`unity_recorder.py` の `record()` 関数内：

```
def record(duration: int, slide_paths: list[str] = None) -> bool:
    # スライドを事前にWindowsにコピー
    win_slide_paths = []
    if slide_paths:
        win_slide_paths = copy_slides_to_windows(slide_paths)
        show_slide(win_slide_paths[0])  # 最初のスライドを表示

    # Playモード開始
    enter_play_mode()
    time.sleep(2)

    # 録画開始
    start_recording()
    start_time = time.time()

    # スライド切り替えタイミングを計算（均等割り）
    if len(win_slide_paths) > 1:
        interval = duration / len(win_slide_paths)
        for i, slide in enumerate(win_slide_paths[1:], start=1):
            wait_until = start_time + interval * i
            time.sleep(max(0, wait_until - time.time()))
            show_slide(slide)

    # 残り時間を待機して録画停止
    elapsed = time.time() - start_time
    time.sleep(max(0, duration - elapsed))
    stop_recording()
    ...
```

`pipeline_all.py` のPhase 1.5として自動実行：

```
# Phase 1.5: スライド生成
from scripts.slide_generator import run as generate_slides
slide_paths = generate_slides()
notify(f"✅ Phase 1.5 完了（{len(slide_paths)}枚）")

# Phase 3U: Unity録画（スライド切り替えあり）
record(duration=audio_duration, slide_paths=[str(p) for p in slide_paths])
```

---

## ハマりポイントまとめ

| 問題 | 原因 | 解決策 |
| --- | --- | --- |
| スライドが切り替わらない | `shutil.copy2` がタイムスタンプを保持するのでUnityが「更新なし」と判断 | `shutil.copy` + `os.utime(dst, None)` で現在時刻に更新（後にMCP方式に切り替え） |
| MCP `set_property` が効かない | パラメータ名が `componentType`（キャメルケース）だった | `component_type`（スネークケース）に修正 |
| キャッシュ問題でFalse | `unity_recorder.pyc` が古いまま使われていた | `__pycache__` を削除してインポートし直す |
| 日本語テキストが表示されない | フォントパスが間違っていた | `/usr/share/fonts/truetype/noto/` のパスを優先リストで順番に試す |

---

## 結果

* 毎朝6:30に自動実行されるパイプラインで、**ニューススクリプトに対応したスライドが自動生成**されるようになった
* 各ニュース記事のOG画像がスライドに表示され、視覚的に情報が伝わりやすくなった
* クロエちゃんの右横のモニターにスライドが表示され、トピックごとに自動切り替え

---

## 関連記事
