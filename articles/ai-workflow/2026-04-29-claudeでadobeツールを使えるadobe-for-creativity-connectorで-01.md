---
id: "2026-04-29-claudeでadobeツールを使えるadobe-for-creativity-connectorで-01"
title: "ClaudeでAdobeツールを使える！「Adobe for creativity connector」でできることまとめ＋試してみた"
url: "https://qiita.com/katoriko/items/d3d6fa09e226999a6dd1"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "qiita"]
date_published: "2026-04-29"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

## これは何
Adobe for creativity connectorについて、できることと使ってみた感想をまとめた記事です。

## Adobe for creativity connectorとは？
Adobe for creativity connectorは、Claudeのチャット内で、Adobeのプロ向けクリエイティブツールを直接操作・実行できる連携機能です。
2026年4月28日に発表・提供開始されました :tada: 

https://blog.adobe.com/en/publish/2026/04/28/adobe-for-creativity-connector

Claudeにサインインして、コネクタを直接インストールすると使えます。

https://adobe-creativity.adobe.io/mcp






## Adobe for creativity connectorで何ができるのか
- Photoshop・Lightroom（画像編集）
- Illustrator・Express（デザイン作成）
- Premiere（動画編集）
- Firefly（生成AI機能を備えたツール）

などのCreative Cloudアプリにまたがる複数ステップのワークフローを自動的に構築し、実行してくれます！




## Adobe for creativityのツール
公式ドキュメントに個別ツールの説明ページはまだ公開されていないため、
ツール名・Adobe製品の機能・Firefly Services API をもとに、推測される機能を項目ごとにまとめました :eyes: 

:::note warn
正式な情報は公式からの公開をお待ちください
:::




### 1. システム / 初期化（1）

| ツール名 | 推測される機能|
|---|---|
| `adobe_mandatory_init` | 他のツールを使う前に必須の初期化処理。セッション開始時に自動実行される |

### 2. アセット管理（16）

ファイル・ブランド素材・Adobe Stock の操作。

| ツール名 | 推測される機能 |
|---|---|
| `asset_add_file` | アセットにファイルを追加 |
| `asset_copy_assets` | アセットを別の場所にコピー |
| `asset_create_folders` | フォルダ構造を作成 |
| `asset_initialize_file_upload` | ファイルアップロードを開始（マルチパート） |
| `asset_finalize_file_upload` | アップロードを確定・コミット |
| `asset_preview_file` | ファイルのプレビューを取得 |
| `asset_inline_preview` | チャット内にプレビューを表示 |
| `asset_search` | アセットを検索 |
| `asset_list_brands` | 登録ブランドの一覧を取得 |
| `asset_get_brand` | 特定ブランドの情報を取得 |
| `asset_get_brand_colors` | ブランドカラーを取得 |
| `asset_get_brand_color_themes` | ブランドのカラーテーマを取得 |
| `asset_get_brand_fonts` | ブランドフォントを取得 |
| `asset_get_brand_logos` | ブランドロゴを取得 |
| `asset_get_brand_guidelines` | ブランドガイドラインを取得 |
| `asset_license_and_download_stock` | Adobe Stock素材をライセンス購入してダウンロード |



### 3. デザイン / テンプレート（4）

| ツール名 | 推測される機能 |
|---|---|
| `search_design` | Expressのテンプレートをキーワードで検索 |
| `animate_design` | デザインにアニメーションを適用（Express） |
| `change_background_color` | 背景色を変更 |
| `create_firefly_board` | Firefly のボード（アイデアボード）を作成 |



### 4. ドキュメント生成（5）

InDesign・Illustrator ベースのデータマージや PDF 出力に対応。

| ツール名 | 推測される機能 |
|---|---|
| `document_merge_data_layout` | データをレイアウトテンプレートに差し込み（InDesignのデータ結合相当） |
| `document_merge_data_vector` | データをベクターテンプレートに差し込み |
| `document_render_layout` | レイアウトドキュメントをレンダリング・書き出し |
| `document_render_vector` | ベクタードキュメントをレンダリング・書き出し |
| `document_convert_pdf` | ファイルをPDFに変換 |


### 5. テキスト / フォント（2）

| ツール名 | 推測される機能 |
|---|---|
| `fill_text` | テンプレートのテキスト枠に文字を流し込む |
| `font_recommend` | コンテキストに合ったフォントをAIが推薦（Adobe Fonts連携） |



### 6. 画像調整（12）

Lightroom / Camera Raw 相当のパラメーター調整。

| ツール名 | 推測される機能 |
|---|---|
| `image_adjust_brightness_and_contrast` | 明るさ・コントラストを調整 |
| `image_adjust_exposure` | 露出を調整 |
| `image_adjust_highlights` | ハイライトを調整 |
| `image_adjust_dark_portions` | 暗部（シャドウ）を調整 |
| `image_adjust_light_portions` | 明部を調整 |
| `image_adjust_color_temperature` | 色温度（寒暖）を調整 |
| `image_adjust_hsl` | 色相・彩度・輝度（HSL）を調整 |
| `image_adjust_single_color_saturation` | 特定の色だけ彩度を調整 |
| `image_adjust_vibrance_and_saturation` | バイブランス・全体の彩度を調整 |
| `image_apply_auto_tone` | 一発でトーンを自動最適化 |
| `image_apply_preset` | Lightroomプリセットを適用 |
| `image_list_presets` | 適用可能なプリセット一覧を取得 |


### 7. 画像エフェクト（8）

| ツール名 | 推測される機能 |
|---|---|
| `image_apply_gaussian_blur` | ガウスぼかしを適用 |
| `image_apply_lens_blur` | レンズブラー（被写界深度）を適用 |
| `image_apply_color_overlay` | カラーオーバーレイを適用 |
| `image_apply_monochromatic_tint` | モノクロ＋単色ティントを適用 |
| `image_apply_glitch_effect` | グリッチアート効果を適用 |
| `image_apply_halftone` | ハーフトーン（網点）効果を適用 |
| `image_add_grain` | フィルムグレインを追加 |
| `image_add_noise` | ノイズを追加 |


### 8. 画像 AI（生成・選択）（6）

Firefly の生成AI機能に相当する核心ツール群。

| ツール名 | 推測される機能 |
|---|---|
| `image_fill_area` | 指定範囲をAIで塗り替え（Generative Fill） |
| `image_generative_expand` | 画像をキャンバス外にAIで拡張（Generative Expand / アウトペインティング） |
| `image_remove_background` | 背景をAIで自動除去 |
| `image_select_subject` | 被写体をAIで自動選択 |
| `image_select_by_prompt` | テキストプロンプトで選択範囲を指定（例：「空だけ選択して」） |
| `image_invert_selection` | 選択範囲を反転 |


### 9. 画像 変形・書き出し（4）

| ツール名 | 推測される機能 |
|---|---|
| `image_crop_and_resize` | 画像をクロップ＆リサイズ |
| `image_crop_to_bounds` | 指定した枠に合わせてクロップ |
| `image_auto_straighten` | 傾きを自動補正 |
| `image_vectorize` | ラスター画像をベクターに変換（Illustratorのライブトレース相当） |


### 10. メディア / 音声（2）

| ツール名 | 推測される機能 |
|---|---|
| `media_enhance_speech` | 音声をAIでクリアに強化（Premiereの「音声を強化」機能相当） |
| `media_summarize` | 動画・音声の内容をAIが要約 |


### 11. 動画（2）

| ツール名 | 推測される機能 |
|---|---|
| `video_create_quick_cut` | 長尺動画からハイライトクリップを自動生成 |
| `video_resize` | 動画を各SNSプラットフォームのサイズに自動変換 |


### 12. ポーリングヘルパー（5）

動画・音声処理など時間のかかる非同期ジョブの完了を待機するためのユーティリティ。ユーザーが直接呼ぶツールではなく、AIが裏側で使うもの。

| ツール名 | 推測される機能 |
|---|---|
| `enhanceSpeechPoll` | `media_enhance_speech` の完了待機 |
| `summarizePoll` | `media_summarize` の完了待機 |
| `quickCutPoll` | `video_create_quick_cut` の完了待機 |
| `resizeVideoPoll` | `video_resize` の完了待機 |
| `vectorPollingHelper` | `image_vectorize` の完了待機 |



## Adobe for creativity connector を使ってみた
### 画像のリサイズ
Geminiにこの記事のサムネイルを作ってもらったので、こちらを以下のサイズにリサイズしてもらいます
- 1080px × 1080px（正方形）
- 728px × 90px （横長）
- 1440px x 2560px （縦長）

![Gemini_Generated_Image_5ql4gh5ql4gh5ql4.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/7b854a1d-367d-49b9-b209-1ef8074651c6.png)


以下のプロンプトを投げてみました

```
Adobe for creativityを使って、この写真を以下のサイズに変換して
  [Image #1]

  - 1080px × 1080px（正方形）
  - 728px × 90px （横長）
  - 1440px x 2560px （縦長）
```

指示が簡潔すぎたのか、ただクロップされた画像が出来上がりました
縦長の場合は余白を持たせて補完しています

|正方形|横長|縦長|
|---|---|---|
|![1080x1080.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/7c808a64-25be-4aa4-8179-87f0a5a47a1b.png)|![728x90.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/ae0c14b2-d6ef-49d9-bfb5-9d8c7114f75e.png)|![1440x2560.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/51303af3-ed0a-4f3d-8a01-a918fa4932b3.png)|

そこで、以下の指示を追加してみました
```
サイズの変換によって、コンテンツが切り取られている。それぞれのサイズに合わせて
コンテンツのレイアウトを変えて、情報量が変わらないようにできる？
```

|正方形|横長|縦長|
|---|---|---|
|![1080x1080_expanded.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/4da4c3cf-34a7-4c13-b092-b72c1269ab96.png)|自動では対応困難です。理由：比率の差が4.5倍あるため|![1440x2560_expanded.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/7a470258-ce54-4302-a013-52fa337a1c4f.png)|


png,jpegなどの画像を投げて、できることは背景の拡張までで、**テキストなどを「個別のオブジェクト」として分離・移動するには、レイヤー付きのソースファイル（PSD や AI）が必要なようです**。

テンプレートのデータがあるものを、よしなにリサイズさせるにはいいのかも。
近いサイズへのリサイズは簡単にやってくれそうです。



### グリッチ or ハーフトーン加工でアート系
先ほどの写真でもう一つ試してみます。

```
「この写真にグリッチ効果とハーフトーンを重ねてポスター風にして」
```
以下が出力されました！

![poster-glitch-halftone.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/65c252f1-79b0-46f9-a12d-4beef0a215cf.png)


エフェクトの種類だけ指定していたので、Illustratorで設定するように、
ハーフトーンの数値もプロンプトに含めて試してみました

```
Adobe for creativityを使って、この写真にハーフトーンを重ねて。
カラーハーフトーンの指定は以下。
- 最大半径：4 pixel
- チャンネル1：45
- チャンネル2：45
- チャンネル3：45
- チャンネル4：45
```

ハーフトーンのパラメーターでサポートされているのは、**最大半径と白黒変換**のみのようです

>このツールのハーフトーンパラメーターは以下のみサポートされています：
>  - 最大半径（4〜127px）→ ご指定の 4px は適用可能です
>  - 白黒変換（true/false）
>チャンネル角度（チャンネル1〜4）はこのMCPツールではサポートされていないため、適用できません。

以下が出力されました
今回の画像には向いていない加工かもですが、指示するだけで得られる質感としては良さそうです :thumbsup: 


![halftone-result.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/a9c890bb-76f2-43eb-9280-04b5e838944f.png)



### 画像編集
適当なプロフィール画像をGeminiに作ってもらったので、実験です

```
Adobe for creativityを使って、この写真の被写体を選択して、
背景を削除した後、背景を真っ白に塗り替えてください。
```

|元画像|加工画像|
|---|---|
|![Gemini_Generated_Image_dvppg1dvppg1dvpp.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/42e5738b-b2b4-455d-9aab-d2a3cce48dd1.png)|![clipboard-photo-white-bg.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3632482/805e729e-1588-47ba-bb71-f363b036ac35.png)|

お〜！いい感じ！髪の毛の切り抜きも細かく処理されています。


## Adobe for creativity connector を使ってみた感想
Illustrator、Photoshopを使い慣れている人は自分が作業する時と同じ感覚で指示しやすそうです！
本来のツールよりも対応しているパラメーターは少ない点には注意です。

割とガッツリ画像を編集してくれて、画像の被写体選択の精度には結構感動しました。
素材をもらう → 画像加工 → サイトに反映する のようなフローの場合、画像加工を Claude上でできるとスイッチコストも減りそうです！

気になった方はぜひ試してみてください:v:

## 参考
https://developer.adobe.com/adobe-for-creativity/prompts-and-workflows/

https://9to5mac.com/2026/04/28/anthropic-releases-9-new-claude-connectors-for-creative-tools-including-blender-and-adobe/

https://developer.adobe.com/firefly-services/docs/firefly-api
