---
id: "2026-04-07-rust-wgpu-wasmで3dポートフォリオサイトを作った-01"
title: "Rust + wgpu + WASMで3Dポートフォリオサイトを作った"
url: "https://zenn.dev/mutafika/articles/caaf6100f11c9c"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

<https://mutafika.com>

## 動機

RustでReactみたいなリッチなUIを作りたい。が、発端だったはずなのになぜか3Dのサイトを作っていた。

やりたかったのは、フロントもバックエンドも**RustでWebを作る**こと。  
wgpu + WASMならRustのコードがそのままブラウザで動くらしいということで、自作フレームワークで作ってみた。

3D要素はただの思いつきで、  
別でRustでCADソフトや3Dレンダラーを作っており、そこで作った資産（行列演算、シェーダー、テクスチャ管理など）を、もしかしたら使えるかもという程度のノリで組み込んだ。

結果として、自作UIフレームワーク + 自作3Dライブラリ + WASMで動く**3Dポートフォリオサイト**ができた。

## 全体構成

このポートフォリオは3つのレイヤーで成り立っている。

* **Sabitori** がウィンドウ管理、UIオーバーレイ（テキスト、ボタン、パネル）、イベントループを担当
* **Seimei** がテクスチャ管理とポストプロセス（Bloom等）を提供
* **アプリケーション層** がWGSLシェーダーで3D空間を描画し、Sabitoriの上にUIを重ねる

## Sabitori — Rust製自作GPU UIフレームワーク

<https://sabitori-gallery.mutafika.com>

Sabitoriは、wgpu上に構築した宣言的UIフレームワーク。11個のクレートに分割されたモジュラー設計になっている。  
当初はTUIツール用のUIを作るために作成していた。

<https://magatsu.mutafika.com>

このMagatsuは女神転生風の何かを作ってとClaudeに指示して作らせたゲーム性0のSabitoriを用いた別のサンプル

### クレート構成

```
sabitori/crates/
├── sabitori/          # ファサード（re-export + ランナー）
├── sabitori-core/     # Elementツリー、レンダーリスト、テーマ
├── sabitori-gpu/      # wgpu描画バックエンド（矩形・画像パイプライン）
├── sabitori-text/     # cosmic-textベースのテキスト描画・グリフアトラス
├── sabitori-layout/   # Flexboxレイアウト（taffy wrapper）
├── sabitori-style/    # CSSライクなスタイルプロパティ
├── sabitori-anim/     # アニメーション（Spring / Easing / Keyframe）
├── sabitori-input/    # 入力イベント型定義
├── sabitori-widgets/  # 高レベルコンポーネント（Button, Modal, Table等）
├── sabitori-window/   # ウィンドウ管理（winit）
└── sabitori-scene/    # ノードツリー抽象（レガシー）
```

### 2つのトレイト — `DeclarativeApp` と `SceneApp`

Sabitoriの中心にあるのは2つのトレイト。

**`DeclarativeApp`** は純粋な2D UIアプリ向け。毎フレーム `view()` でElementツリーを組み立てる、React的な宣言型API。

```
trait DeclarativeApp {
    fn view(&self, ctx: &ViewContext) -> Element;
    fn on_input(&mut self, event: &InputEvent) -> bool;
    fn tick(&mut self, dt: f32);
    // title(), size(), fonts() など設定系メソッドも
}
```

**`SceneApp`** は `DeclarativeApp` を拡張し、**UIの下に自前のGPU描画を差し込める**。これがポートフォリオの核になっている。

```
trait SceneApp: DeclarativeApp {
    fn setup(&mut self, ctx: &GpuContext);
    fn render_scene(&mut self, ctx: &mut SceneRenderContext);
    fn on_resize(&mut self, ctx: &GpuContext);
}
```

フレームの描画順は：

1. `render_scene()` — アプリが自前のレンダーパスで3D空間を描画
2. Sabitori が `LoadOp::Load` で既存の描画結果を保持しつつ、UIオーバーレイを重ねる

つまり、**3D空間の上に2D UIが載る**。ゲームエンジンのHUD的な構造だが、UIはReact的な宣言型APIで組める。

### GPU描画パイプライン

Sabitori内部では、Elementツリーが以下の流れでGPU描画に変換される。

```
Element → build_tree_measured() → RenderList → Bridge → GPU Instances
```

1. **Elementツリー構築** — `div().pos(x, y).child(text("hello"))` のようなビルダーAPIでツリーを組む
2. **レイアウト計算** — taffyによるFlexboxレイアウト。CSS Grid的な配置もサポート
3. **RenderList生成** — `RectDraw`（矩形）、`TextDraw`（テキスト）、`ImageDraw`（画像）のリストに変換
4. **GPUインスタンス化** — Bridgeが各DrawをGPU向けインスタンスデータにパック

矩形はSigned Distance Functions（符号付き距離関数）ベースで描画される。  
各 `RectInstance`（128バイト）に、座標・角丸半径・色・ボーダー・シャドウの全パラメータが入り、1つのシェーダー（`rect.wgsl`）で角丸矩形・ボーダー・影・グラデーションを全部処理する。

テキストは `cosmic-text` でシェイピングし、グリフを動的アトラスにラスタライズ。各グリフが `GlyphInstance`（44バイト）として個別にレンダリングされる。

### ネイティブ vs WASM — 同一コードで動く仕組み

Sabitoriのプラットフォーム抽象は `#[cfg(target_arch = "wasm32")]` による条件コンパイルで実現している。差分は3箇所だけ。

**1. レンダラー初期化**

```
// ネイティブ: pollster で同期的に初期化
let renderer = pollster::block_on(GpuRenderer::new_async(...));

// WASM: spawn_local で非同期初期化（DOM にキャンバスをアタッチしてから）
wasm_bindgen_futures::spawn_local(async move {
    let renderer = GpuRenderer::new_async(...).await;
});
```

**2. GPUバックエンド選択**

```
let backends = if cfg!(target_arch = "wasm32") {
    wgpu::Backends::GL    // WebGL2 フォールバック
} else {
    wgpu::Backends::all() // Metal / Vulkan / DX12
};
```

**3. デバイスのlimits**

```
let limits = if cfg!(target_arch = "wasm32") {
    wgpu::Limits::downlevel_webgl2_defaults() // WebGL2 互換
} else {
    wgpu::Limits::default()
};
```

アプリケーション側のコードは一切変更不要。`DeclarativeApp` / `SceneApp` を実装すれば、`sabitori::run_scene(app)` 一行でネイティブでもWASMでも起動する。

## Seimei — 3D PBRレンダリングライブラリ

SeimeiはUI非依存の3Dレンダリングライブラリ。今回はフルのPBRパイプラインは使わず、2つの機能だけを利用した。

### TextureManager — テクスチャの統一管理

```
let mut textures = TextureManager::new(device, queue);
textures.create_from_rgba(device, queue, "proj-0", 128, 96, &rgba_data);

// 描画時
pass.set_bind_group(1, textures.get_bind_group(Some("proj-0")), &[]);
```

内部では各テクスチャに対してバインドグループ（テクスチャ + サンプラー）を保持し、キーで引ける。

バインドグループレイアウト：

* Binding 0: 2Dテクスチャ（RGBA8UnormSrgb, filterable）
* Binding 1: リニアサンプラー（リピートアドレッシング）

### PostProcessPipeline — HDRポストプロセス

Seimeiのポストプロセスパイプラインは、HDRレンダリング → 各エフェクト → ACESトーンマッピング → ガンマ補正の流れ。

```
シーン描画 → [HDR Rgba16Float テクスチャ]
                 ↓
            Bloom Extract (閾値 > 1.0 の輝度を抽出)
                 ↓
            Downsample ×3 (1/2 → 1/4 → 1/8 → 1/16)
                 ↓
            Upsample ×3 (加算合成で戻す)
                 ↓
            Composite (シーン + Bloom → ACESトーンマップ → sRGBガンマ)
```

サポートするエフェクト：

* **Bloom** — ミップチェーンベースの光溢れ
* **SSAO** — 64サンプル半球カーネル + ブラーパス
* **SSR** — Gバッファ深度+法線によるレイマーチ反射
* **DOF** — 焦点距離ベースのボケ
* **EdgeBevel** — エッジ強調

今回のポートフォリオではBloomのみ有効にして、グローやHDR発光をリッチに見せている。

## WASM対応 — Trunkで一発ビルド

### ビルド

`index.html` に `<link data-trunk rel="rust" />` を書くだけで、Trunkがwasm-bindgen + wasm-opt まで自動で行い、`dist/` に `index.html` + `.js` + `.wasm` を出力する。

## まとめ

Rust + wgpu + WASM + Trunkの組み合わせで、GPUレンダリングを含むアプリケーションがそのままWebで動く。

見た目は今後に期待。
