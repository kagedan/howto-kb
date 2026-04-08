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

https://mutafika.com

 動機
RustでReactみたいなリッチなUIを作りたい。が、発端だったはずなのになゼか3Dのサイトを作っていた。
やりたかったのは、フロントもバックエンドもRustでWebを作ること。
wgpu + WASMならRustのコードがそのままブラウザで動くらしいということで、自作フレームワークで作ってみた。
3D要素はただの思いつきで、
別でRustでCADソフトや3Dレンダラーを作っており、そこで作った資産（行列演算、シェーダー、テクスチャ管理など）を、もしかしたら使えるかもという程度のノリで組み込んだ。
結果として、自作UIフレームワーク ...
