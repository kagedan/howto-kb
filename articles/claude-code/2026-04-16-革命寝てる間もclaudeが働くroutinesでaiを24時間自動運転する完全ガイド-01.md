---
id: "2026-04-16-革命寝てる間もclaudeが働くroutinesでaiを24時間自動運転する完全ガイド-01"
title: "【革命】寝てる間もClaudeが働く！「Routines」でAIを24時間自動運転する完全ガイド"
url: "https://qiita.com/emi_ndk/items/116c1703e44bcfbc9b69"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

**「毎晩2時にバグを自動で直して、朝起きたらPRが届いてる」**

これ、もう夢じゃない。

2026年4月14日、Anthropicが**Claude Code Routines**を発表した。これはマジでゲームチェンジャーだ。

## 結論から言うと...

Claude Codeが**クラウド上で24時間365日**、あなたの代わりにコードを書き続ける。しかも**ラップトップを閉じても**動く。

「え、それってGitHub Actionsと何が違うの？」

全然違う。**AIがコードを理解して、自分で判断して、PRまで作る**んだ。

## Routinesとは何か？3つのトリガータイプ

Routinesには3種類のトリガーがある：

### 1. 🕐 Scheduled（スケジュール実行）

```
毎晩2時 → Linearから最優先バグを取得 → 修正を試みる → Draft PRを作成
```

cronジョブのAI版だと思ってほしい。ただし、このcronは**コードを理解している**。

### 2. 🔗 API（HTTP POSTで起動）

```
curl -X POST https://api.anthropic.com/v1/claude_code/routines/trig_xxx/fire \
  -H "Authorization: Bearer sk-ant-oat01-xxxxx" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -d '{"text": "Sentry alert SEN-4521 fired in prod."}'
```

アラートが飛んだ瞬間、Claudeがスタックトレースを解析して**自動で修正PRを作る**。人間は寝てていい。

### 3. 🐙 GitHub Webhook（イベント駆動）

PRがオープンされた瞬間にClaudeが起動して：

* セキュリティチェック
* パフォーマンスレビュー
* コーディング規約チェック
* 要約コメント投稿

これが**全自動**で走る。

## 実践：5分でRoutineを作る

### Step 1: claude.ai/code/routines にアクセス

「New routine」をクリック。

### Step 2: プロンプトを書く

ここが**最重要**。Routineは完全自律で動くので、プロンプトは曖昧さゼロで書く必要がある。

**悪い例：**

**良い例：**

```
このPRに対して以下のチェックを実行してください：
1. OWASP Top 10の脆弱性がないか確認
2. N+1クエリがないか確認
3. 未使用のimportがないか確認
4. テストカバレッジが80%以上か確認

問題があればインラインコメントを残し、
最後にサマリーコメントを投稿してください。
問題がなければ「LGTM 🚀」とだけコメントしてください。
```

### Step 3: リポジトリを選択

複数リポジトリを選択可能。Claudeは毎回最新をcloneして作業する。

デフォルトでは `claude/` プレフィックスのブランチにしかpushできない。`main`への直pushを許可するなら「Allow unrestricted branch pushes」を有効化。

### Step 4: トリガーを設定

| トリガー | ユースケース |
| --- | --- |
| Hourly | ログ監視、軽微な自動修正 |
| Daily | バックログ整理、ドキュメント更新 |
| Weekdays | 平日のみのPRレビュー |
| Weekly | 依存関係アップデート、セキュリティスキャン |
| API | アラート連携、デプロイ後検証 |
| GitHub | PR自動レビュー、Issue自動分類 |

### Step 5: Connectorを追加

Slack、Linear、Google Driveなど、MCP経由で外部サービスと連携可能。

例：毎晩のバグトリアージ結果を**Slackに自動投稿**できる。

## 神ユースケース5選

### 1. 🐛 夜間バグ修正マシン

```
毎晩2時に実行：
1. Linearから「bug」ラベルのIssueを取得
2. 優先度順にソート
3. 上位3件の修正を試みる
4. 成功したらDraft PRを作成
5. 結果をSlackに投稿
```

朝起きたら3つのPRが待ってる生活、想像してみてほしい。

### 2. 📝 ドキュメント自動更新

```
毎週月曜に実行：
1. 先週マージされたPRを取得
2. APIの変更があるか確認
3. 該当するドキュメントを更新
4. PRを作成してレビュアーをアサイン
```

「ドキュメントが古い」問題が**消滅**する。

### 3. 🔥 アラート即時対応

```
Datadogからアラート受信時：
1. スタックトレースを解析
2. 最近のコミットと照合
3. 原因箇所を特定
4. 修正案をPRで提出
5. オンコールにSlack通知
```

オンコールの人間は**レビューするだけ**。

### 4. 🔒 セキュリティ自動監査

```
PR作成時に実行：
1. 認証モジュールに変更があるかチェック
2. SQLインジェクションの可能性を確認
3. シークレットのハードコードを検出
4. 結果をインラインコメントで報告
```

セキュリティレビューが**即座に**完了。

### 5. 🌐 多言語SDK同期

```
Python SDKのPRがマージされたら：
1. 変更内容を解析
2. Go SDKに同等の変更を実装
3. テストを実行
4. PRを作成
```

SDK間の乖離が**永久に**なくなる。

## 料金と制限

| プラン | 1日の実行上限 |
| --- | --- |
| Pro ($20/月) | 5回 |
| Max ($100/月) | 15回 |
| Team | 25回 |
| Enterprise | 25回 |

上限を超えた場合は「Extra usage」を有効にすることで従量課金で継続可能。

## CLIからも作れる

```
# 会話形式で作成
/schedule

# ワンライナーで作成
/schedule daily PR review at 9am

# 一覧表示
/schedule list

# 即時実行
/schedule run
```

## 注意点：これだけは気をつけろ

### 1. プロンプトは超具体的に

Routineは**質問してこない**。曖昧なプロンプトは予期しない動作を引き起こす。

### 2. ブランチ権限に注意

`main`への直pushを許可すると、Claudeが本番ブランチを変更できてしまう。基本は`claude/`プレフィックスのみに制限しておくべき。

### 3. Connectorは必要最小限に

全Connectorがデフォルトで有効になっている。使わないものは外しておこう。

### 4. GitHub Appのインストールが必要

Webhookトリガーを使うには、対象リポジトリにClaude GitHub Appをインストールする必要がある。

## まとめ：AIが「本当に」働く時代が来た

これまでのAIツールは「人間が使う」ものだった。

Routinesは違う。**AIが自律的に働く**。

```
人間: 寝る
Claude: バグを直す、PRを作る、レビューする、Slackに報告する
人間: 起きる
人間: 「おー、PR3つ来てる。LGTM」
```

これが2026年の開発スタイルだ。

---

## 参考リンク

Automate work with routines - Claude Code Docs

Introducing routines in Claude Code | Claude

Anthropic's Claude Code gets automated 'routines' and a desktop makeover - SiliconANGLE

---

**この記事が役に立ったら「いいね」と「ストック」をお願いします！**

質問があればコメントで聞いてください。Routinesの設定で困ったことがあれば一緒に考えます。
