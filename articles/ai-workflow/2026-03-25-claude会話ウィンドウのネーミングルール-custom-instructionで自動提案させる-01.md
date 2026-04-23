---
id: "2026-03-25-claude会話ウィンドウのネーミングルール-custom-instructionで自動提案させる-01"
title: "Claude会話ウィンドウのネーミングルール — Custom Instructionで自動提案させる"
url: "https://qiita.com/imyshKR/items/495bb9e910bea3c682b6"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

Claudeでプロジェクトを複数並行すると、サイドバーの自動生成タイトルでは「どの会話がどの段階か」が判別できなくなります。この記事では、Custom Instruction（User Preferences）に入れるだけで、Claudeが会話開始時にネーミングを自動提案してくれる仕組みを紹介します。

## やりたいこと

> [![네이밍_전_대화목록.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2F1079e499-a4e1-4d66-8d54-45bdba9b89af.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=637644386de41867b34a322088bc627e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2F1079e499-a4e1-4d66-8d54-45bdba9b89af.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=637644386de41867b34a322088bc627e)

* 会話ウィンドウ名で**プロジェクト名**と**作業段階**を一目で把握
* Claudeが自動で名前を提案、手動リネームするだけ
* すべてのプロジェクトで一貫適用

## 設定方法

Settings > Profile > User Preferencesに以下を追加します。

```
## 会話ウィンドウのネーミング
すべてのClaude会話開始時、会話の目標/内容を把握して会話ウィンドウ名を提案すること。
- 形式：「段階 | プロジェクト 作業内容」
- 段階3種：企画（アイデア具体化/スペック）、実装（Claude Codeハンドオフ含む）、完了（終了した会話）
- 例：「企画 | kigaru プレミアム機能」「実装 | kigaru 相性機能」「完了 | kigaru 今日の運勢」
- サイドバーでリネームするよう案内
- 会話中に段階の切り替わりを検知したら新しい名前を提案
  - 企画→実装：Claude Codeハンドオフプロンプト作成時
  - 実装→完了：該当機能の議論終了時
```

### 絵文字バージョン

```
## 会話ウィンドウのネーミング
すべてのClaude会話開始時、会話の目標/内容を把握して会話ウィンドウ名を提案すること。

- 形式：「絵文字 | プロジェクト 作業内容」
- 絵文字3種：💡（企画/アイデア具体化/スペック）、💻（実装/Claude Codeハンドオフ含む）、✅（完了/終了した会話）
- 例：「💡 | kigaru プレミアム機能」「💻 | kigaru 相性機能」「✅ | kigaru 今日の運勢」
- サイドバーでリネームするよう案内
- 会話中に段階の切り替わりを検知したら新しい名前を提案
  - 💡→💻：Claude Codeハンドオフプロンプト作成時
  - 💻→✅：該当機能の議論終了時
```

これだけです。新しい会話を開くと、Claudeが内容を把握して名前を提案してくれます。

## なぜこの設計か

### 3段階（企画/実装/完了）にした理由

最初は`TODO / PROGRESS / DONE / ENHANCE`の4分類を試しましたが、TODOとPROGRESSの境界が曖昧で「どっち？」と毎回悩む → 使わなくなりました。

「ステータス」ではなく「パイプライン上の位置」で分けると判断がシンプルになります。

3つなら迷いません。

### 切り替え基準を明示した理由

「mdファイル出力＝実装」と思いがちですが、Claude Webでspec.mdを出力するのはまだ企画段階の成果物です。

明確な基準：

* **企画 → 実装：** Claude Codeハンドオフプロンプト作成時
* **実装 → 完了：** 機能の議論終了時

### User Preferencesに置いた理由

⚠️ **プロジェクトメモリに入れると他のプロジェクトで適用されません。** Claudeのメモリはプロジェクト単位で分離されているため、全プロジェクト共通のルールはUser Preferencesに入れる必要があります。

## 設計判断まとめ

| 判断 | 理由 |
| --- | --- |
| 3段階 | 4つ以上は境界が曖昧で使わなくなる |
| ステータスではなく段階 | パイプラインと1:1対応 |
| 「段階 | 内容」形式 | サイドバーで一目把握 |
| 切り替え基準の明示 | 曖昧な判断を排除 |
| User Preferences配置 | プロジェクトメモリは分離される |

## 適用結果

> [![네이밍_후_대화목록.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2F0f0fa346-e5b5-49a9-9c3d-e609eb21adcb.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=87721539e350595f3ae64edf8e9abf61)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2F0f0fa346-e5b5-49a9-9c3d-e609eb21adcb.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=87721539e350595f3ae64edf8e9abf61)

```
# Before（自動生成）
プロジェクト構造設計
機能追加の議論
バグ修正

# After（ネーミングシステム）
企画 | kigaru プレミアム機能
実装 | kigaru 相性機能
完了 | kigaru 今日の運勢
企画 | imysh ポートフォリオ設計
```

Claudeを複数プロジェクトで使っている方は試してみてください。User Preferencesにコピペするだけで動きます。

> [![실사용.jpeg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2Feb27b50a-d0ea-4a78-be8a-16795660a162.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fedb1ca2649d01daf43c38727053521b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2Feb27b50a-d0ea-4a78-be8a-16795660a162.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fedb1ca2649d01daf43c38727053521b)

---

*この記事の構成および執筆にClaudeを活用しています。*
