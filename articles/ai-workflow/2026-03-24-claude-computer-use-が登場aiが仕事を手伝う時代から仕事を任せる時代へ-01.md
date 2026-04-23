---
id: "2026-03-24-claude-computer-use-が登場aiが仕事を手伝う時代から仕事を任せる時代へ-01"
title: "Claude Computer Use が登場！AIが「仕事を手伝う」時代から「仕事を任せる」時代へ"
url: "https://qiita.com/AppTime-mizoi/items/0305fe068347fdf493e3"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

## はじめに

2026年3月23日、Anthropic が **Claude Computer Use** をリリースしました。

VIDEO
> [公式ページ：Put Claude to work on your computer]

Claude がついに**パソコンを直接操作**できるようになりました。アプリを開く、ブラウザを操作する、スプレッドシートに入力する——デスクに座ってやっていた作業を Claude が代行してくれます。

**「教えてもらう → 自分でやる」から「任せる → 確認する」への転換**です。

---

## お知らせ（採用情報）

AppTime では一緒に働くメンバーを募集しております。  
詳しくは採用情報ページをご確認ください。

みなさまからのご応募をお待ちしております。

---

## Claude Computer Use とは

[![20260324-5fe79983c19544bda3ef9fa9c02c8c1c-attachment.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4285209%2F0456ffa2-b36e-44c1-a321-ee9a397e2a96.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4ad6be0672ef88d9f96140ccacfbc08e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4285209%2F0456ffa2-b36e-44c1-a321-ee9a397e2a96.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4ad6be0672ef88d9f96140ccacfbc08e)

> Claude が、人間のようにマウスやキーボードを使って、パソコン上のアプリを操作できるようになった機能

|  | これまでの AI | Claude Computer Use |
| --- | --- | --- |
| **できること** | テキストで回答 | パソコンを直接操作 |
| **作業の完結** | 人間が結果を転記 | 最終成果物まで仕上げる |
| **スマホから** | チャットで質問するだけ | Dispatch で PC 作業を丸ごと指示・実行 |
| **たとえるなら** | 詳しい相談相手 | 実際に手を動かしてくれる同僚 |

## 仕組み：2 段階で動く

**① コネクタを探す** → Slack や Google カレンダーなど公式連携があれば API 経由で操作（安定・高速）

**② なければ画面を操作** → 人間と同じようにマウス・キーボードで GUI を直接操作（= Computer Use）

```
例：「今週の会議予定をまとめて Excel に整理して」

1. Google Calendar → コネクタで予定取得
2. Excel → コネクタなし → 画面操作で起動・入力・整形・保存
```

セットアップ不要。有効化するだけですぐ使えます。

## 対応環境（2026年3月時点）

| 項目 | 内容 |
| --- | --- |
| **ツール** | Claude Cowork（一般向け GUI）/ Claude Code（開発者向け CLI） |
| **対応 OS** | macOS のみ（Windows は Cowork 対応済み、Computer Use は未対応） |
| **プラン** | Pro（$20/月）/ Max（$100〜200/月）※Team/Enterprise は未対応 |
| **ステータス** | リサーチプレビュー |
| **有効化** | Settings > General > Desktop app からオン |

## Dispatch：スマホから仕事を振れる

[![20260324-af4b5ca159b34d64a6110743cc2c5b01-attachment.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4285209%2F35f52c50-12f3-4042-a600-67634d0fc14c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c0b6dff9a58c5328f257e9945721aeaa)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4285209%2F35f52c50-12f3-4042-a600-67634d0fc14c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c0b6dff9a58c5328f257e9945721aeaa)

**Dispatch = スマホからデスクトップの Claude にタスクを指示する機能**。Computer Use と組み合わせると、スマホ 1 台で PC の実アプリ操作まで完結します。

```
📱 スマホ → タスクを指示
🖥️ デスクトップ → Claude が自動実行（画面操作含む）
📱 スマホ → 結果を確認
```

**公式が挙げる活用例：**

* 通勤中にモーニングブリーフィングを作成（メール・Slack を確認→まとめ）
* IDE でコード変更 → テスト → PR 作成
* `/schedule` で定期タスク化（毎朝メール要約、毎週レポート作成など）

**注意点：**

* Claude Desktop アプリは起動したままにする必要あり
* ローカル処理（クラウド実行ではない）
* Computer Use は VM の外で動作 → 実際のデスクトップに影響あり
* 現時点では 1 スレッドのみ

## 具体的にどんなことができる？

### スマホから PC 作業を丸ごと指示

```
📱「今月の売上データを Excel にまとめて、グラフ付きで」
  ↓
🖥️ CSV 読込 → Excel 起動 → データ入力 → SUM関数設定 → グラフ挿入 → 保存
  ↓
📱「完了。売上サマリー.xlsx を保存しました」
```

### ユースケース

* **Excel 操作** — セル入力・数式・条件付き書式・ピボットテーブルまで直接操作
* **ドキュメント作成** — 議事録 → PowerPoint、領収書画像 → 経費レポートなどアプリ間連携
* **開発ツール（Claude Code）** — IDE でコード変更、ビルド・テスト実行、Git 操作、PR 作成
* **リサーチ** — ブラウザで複数サイト巡回 → 比較表をスプレッドシートに自動作成
* **定型業務** — `/schedule` で毎週金曜にダッシュボードからデータ取得→レポート化

## 🔥 開発者向け：アプリ開発 → TestFlight 配信の自動化

Flutter / SwiftUI 開発者にとって一番アツいシナリオがこれです。

```
📱「ログイン画面を実装して、ビルドして、TestFlight にアップしておいて」

🖥️ Claude Code が実行：
  コード生成 → Xcode ビルド → テスト → Archive → App Store Connect → TestFlight 配信
```

### 現時点での実現度

| レベル | 内容 | 状況 |
| --- | --- | --- |
| **今すぐ実用** | コード生成、`flutter build` / `xcodebuild`、Git 操作、PR 作成 | ✅ |
| **可能だが要監視** | Xcode GUI 操作、Archive、App Store Connect アップロード、シミュレーター確認 | ⚠️ |
| **慎重に** | 証明書操作、本番配信、審査提出 | 🔒 |

### おすすめのワークフロー

**コーディングとビルドは Claude、配信確認は自分で**。

```
📱「ビルドが通るところまでやっておいて。Archive は不要」
→ Claude が実装 → ビルド → テスト
→ 📱「ビルド成功。テスト全パス」
→ 帰宅後に自分で Archive & TestFlight アップロード
```

## SNS で話題！リリース直後の実例

リリース直後の X のタイムラインが大賑わいだったので、印象的だった事例をピックアップ。

### ① Premiere Pro を AI が直接操作して無音カット

* Premiere Pro の画面を Claude に渡したら、**マウス＋キーボードで無音部分をカット編集**してくれた
* 従来は ffmpeg コマンドやスクリプト経由だったが、**プロ向けソフトの GUI を直接操作**
* 「人間様のやること無くなる」というコメントが印象的

### ② 操作スクショ自動取得 → 画像付きマニュアル作成

* Claude にアプリを操作させつつ、**操作時のスクリーンショットを自動保存**
* その流れを**画像付きの操作説明書として自動生成**
* 社内ツール導入マニュアル、新入社員向け手順書などに使える

```
従来：操作→スクショ撮影→貼り付け→説明文→整形 → 数時間〜数日
Computer Use：「手順をマニュアルにして」と指示 → 指示1回で完成
```

### ③ 動画ポストプロダクションの完全自動化

### ④ Remotion × Claude Code でプロンプトから動画生成

* 「30 秒のプロダクト紹介動画を作って」→ Claude が Remotion コードを書いてレンダリング
* SNS 向けリサイズもバッチ処理可能
* 参考：[Remotion 公式ガイド](https://www.remotion.dev/docs/ai/claude-code)

### ⑤ 公式が挙げるデモ例

* 競合分析レポート作成
* スマホシミュレーターで UX テスト
* 複数ソースからスプレッドシート作成→共有フォルダ保存
* コネクタのない社内ツールを画面操作

> 参考：[GIGAZINE](https://gigazine.net/news/20260324-claude-computer/)

## 安全性：押さえておくべきポイント

**安全対策：**

* **許可制** — 新しいアプリへのアクセスは都度ユーザー承認が必要
* **ブロックリスト** — 投資プラットフォーム・暗号資産ウォレットはデフォルトでブロック
* **ファイル削除保護** — 削除時は明示的な「Allow」ボタン押下が必要
* **プロンプトインジェクション対策** — 自動スキャン・防御機構あり（ただし発展途上）

**注意すべきこと：**

* **Computer Use は VM の外で動作**（画面操作は実デスクトップ上で実行される）
* 医療・金融・個人記録など**機密データでの利用は非推奨**
* Chrome 拡張と併用する場合は**信頼できるサイトに限定**

> Computer use is still early compared to Claude's ability to code or interact with text. Claude can make mistakes.  
> （Computer Use はまだ初期段階。ミスの可能性あり）— Anthropic 公式ブログ

## 競合比較

| プロダクト | 提供元 | 特徴 |
| --- | --- | --- |
| **Claude Computer Use** | Anthropic | Cowork/Code 統合、セキュリティ重視、Dispatch 連携 |
| **OpenClaw** | OSS（OpenAI 買収） | GitHub 32万スター、多 LLM 対応 |
| **Perplexity Computer** | Perplexity | ブラウザ操作特化 |
| **Manus** | Meta | マルチモーダルエージェント |

## 今後の検討ポイント

* **ワークフロー設計** — 「任せる前提」で指示を明確・構造的に。チェックポイントの設計
* **セキュリティ** — ファイルアクセスは最小権限。企業利用なら IT 管理者によるプラグイン管理
* **プラグイン開発のチャンス** — 日本固有業務（年末調整等）、社内ツール MCP コネクタ、業界特化パッケージ
* **自律レベルの段階設計** — 単発タスク → 複数ステップ → 定期実行 → 判断委任（慎重に）

## まとめ

| ポイント | 内容 |
| --- | --- |
| **何が起きたか** | Claude がパソコンを直接操作できるようになった |
| **ツール** | Cowork（一般向け）/ Code（開発者向け） |
| **対応環境** | macOS / Pro・Max プラン / リサーチプレビュー |
| **スマホ連携** | Dispatch で指示→実行→確認が完結 |
| **開発作業** | 実装→ビルド→テスト→PR。TestFlight も視野に |
| **今後のカギ** | ワークフロー設計、セキュリティ、プラグイン開発 |

## おわりに

**「仕事を手伝う」から「仕事を任せる」への転換**が確実に進んでいます。

まだリサーチプレビュー段階で完璧ではありませんが、方向性は明確です。まずはダウンロードフォルダの整理など、機密性の低いタスクから試して Claude の得意・不得意を体感してみてください。

---

**参考情報**

*公式ドキュメント*

* [Anthropic 公式ブログ：Dispatch and Computer Use]

* [ヘルプセンター：Let Claude use your computer in Cowork]

* [ヘルプセンター：Use Cowork safely]

* [ヘルプセンター：Assign tasks to Claude from anywhere]

*メディア報道*

* [Engadget：Claude Code and Cowork can now use your computer]

* [GIGAZINE：Claudeで自分のPCを操作できる新機能が登場]

* [9to5Mac：Anthropic is giving Claude the ability to use your Mac]

*技術ブログ・ツール*

* [Claude Code Skills for Video Editing]

* [Remotion 公式：Claude Code での動画作成]

*SNS 上の活用報告*
