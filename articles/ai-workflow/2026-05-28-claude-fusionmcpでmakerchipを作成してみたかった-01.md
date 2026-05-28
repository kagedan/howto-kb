---
id: "2026-05-28-claude-fusionmcpでmakerchipを作成してみたかった-01"
title: "Claude × FusionMCPでMakerChipを作成してみたかった"
url: "https://qiita.com/polar-workshop/items/916e8fd70787cf841072"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "Python", "qiita"]
date_published: "2026-05-28"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

# この記事の概要

お疲れ様です！Polar工房です！
今回は3Dプリンター×MCPの検証として、MakerChipの作成を試みました。
検証がうまくいけば、NASのケースなどを作成していきたいと思います！
以下目次となります。
- [FusionMCPのセットアップ](https://qiita.com/polar-workshop/items/916e8fd70787cf841072#fusionmcp%E3%81%AE%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97)
- [実際に動かしてみる](https://qiita.com/polar-workshop/items/916e8fd70787cf841072#%E5%AE%9F%E9%9A%9B%E3%81%AB%E5%8B%95%E3%81%8B%E3%81%97%E3%81%A6%E3%81%BF%E3%82%8B)
- [MakerChipの作成(失敗)](https://qiita.com/polar-workshop/items/916e8fd70787cf841072#makerchip%E3%81%AE%E4%BD%9C%E6%88%90)
- [FusionMCPを使いこなすには？](https://qiita.com/polar-workshop/items/916e8fd70787cf841072#fusionmcp%E3%82%92%E4%BD%BF%E3%81%84%E3%81%93%E3%81%AA%E3%81%99%E3%81%AB%E3%81%AF)
# FusionMCPのセットアップ
今回はお試し&手軽に利用したいのでClaudeのデスクトップ版からMCPを利用していきます。

### Claudeの設定
1. まずはMCPサーバの準備をしていきます。
「アプリを接続」を押下します
![FusionMCP説明画像.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380710/6b64bde4-eb2b-4856-9102-05afbac2e221.png)

1. コネクタで「Fusion」と検索すると"Autodesk Fusion"のアイコンが表示されるのでクリックします。
![FusionMCP説明画像②.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380710/e15c3300-d6bb-4667-8228-9e5be8b63940.png)

1. 迷わずインストール！
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380710/26ec050a-8cc1-4efa-9726-657329919215.png)
これでClaude側の設定は完了です！（昔のMCP連携の５倍くらい簡単になってて、時代の流れを感じる、、、）

### Fusion側の設定
こちらもシンプルなのでサクサク行きます！！

1. 右上のアイコンをクリック→基本設定を選択！
1. 画像のMCPの有効化にチェックを入れます！
![タイトルなし.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380710/30fa65f2-06a2-44f3-80f6-3f20ffc8540d.png)
これで完了です！！

# 実際に動かしてみる
では、実際に動かしてみます！まずはお手並み拝見！
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380710/d578f3ce-8f0b-40b3-9e7f-424ce3856ac0.png)
成果物
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4380710/b36405ed-2f9c-47c1-a7e1-4cd107938d3b.png)
ん？？？
これはArduinoNano？
どうやら、LLMそのものはMakerChipという概念が学習データにない様子。
では、MakerChipという概念について調べさせてそのあとにMakerChipを一緒に作っていきましょう！

### MakerChipの作成

MakerChipの規格などを学習させてみたものの、デザインをうまく反映できずに断念。

### 振り返り
#### できたこと
- MakerChipの原型の作成
- モナカ構造(分割構造)の作成

#### できなかったこと
- Claudeとのやり取りのなかで作成したデザインをボディに反映させること

デザインをMCPのツールのみで反映させるというのがデザインの反映に手間取った原因と分析しました。
人間に例えるとExcelでアニメやイラストを描けと言っているようなものなので、技術的には可能だが非常に手間がかかることをやらせていたことが失敗の原因であると分析しました。

### FusionMCPを使いこなすには？
そもそも何ができるのかをあまり把握していない状態でMCPを使ったことがうまく使いこなせない原因と判断し何ができるのかをAIにリストアップしてもらうことにしてもらいました。
#### 🔍 Read（読み取り）

| 機能 | 説明 | 主なパラメータ |
|------|------|----------------|
| スクリーンショット取得 | 現在のビューを画像（PNG）で取得 | direction（front/top/iso など）, width, height |
| プロジェクト一覧 | ハブ内の全プロジェクトを列挙 | なし |
| ドキュメント検索 | 名前でファイルをあいまい検索 | name（検索ワード）, project（絞り込み） |
| 開いているドキュメント一覧 | 現在 Fusion で開いている全ファイルを表示 | なし |
| 最近のドキュメント一覧 | 最近使ったファイルの履歴を表示 | なし |
| API ドキュメント検索 | Fusion API のクラス・メンバーを正規表現で検索 | searchPattern, apiCategory, filter |

---

#### ⚙️ Execute（実行）

| 機能 | 説明 | 備考 |
|------|------|------|
| Python スクリプト実行 | Fusion API を使った任意のモデル操作 | `def run(_context):` を定義する必要あり |
| ドキュメントを開く | ファイル ID を指定してドキュメントを開く | 事前に Read でファイル ID を取得 |
| ドキュメントを閉じる | アクティブなドキュメントを閉じる | 未保存の場合はユーザー確認が必要 |
| ドキュメントを保存 | アクティブなドキュメントを保存 | ユーザーが明示的に指示した場合のみ実行 |

#### Python スクリプトでできる主な操作例

| カテゴリ | 操作例 |
|----------|--------|
| 形状作成 | ボックス・円柱・スフィア・トーラスなど |
| フィーチャ操作 | 押し出し（Extrude）・回転（Revolve）・スイープ・ロフト |
| フィレット・面取り | エッジへのフィレット・チャンファー追加 |
| マテリアル設定 | 素材・外観（アルミ・鉄・樹脂など）の変更 |
| 寸法・パラメータ変更 | スケッチ寸法・フィーチャパラメータの編集 |
| 情報取得 | ボディ・コンポーネント・スケッチの一覧取得 |
| エクスポート | STL・STEP・OBJ・F3D などへの書き出し |
| コンポーネント操作 | 移動・コピー・ミラー・パターン配置 |

---

#### ↩️ Update（更新）

| 機能 | 説明 |
|------|------|
| Undo（元に戻す） | 直前の操作を取り消す |
| Redo（やり直し） | 取り消した操作を再実行する |

MCP自体は基本的なFusionの操作と変わらないことから、ステップバイステップで作成していくことで意図しない出力を抑制できる可能性が高そうですね。
次回は今回得られた知見を基に作成に停滞していたNASのケースの作成を行います！
