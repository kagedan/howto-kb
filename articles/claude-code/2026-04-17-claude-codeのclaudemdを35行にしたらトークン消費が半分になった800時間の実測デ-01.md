---
id: "2026-04-17-claude-codeのclaudemdを35行にしたらトークン消費が半分になった800時間の実測デ-01"
title: "Claude CodeのCLAUDE.mdを35行にしたらトークン消費が半分になった——800時間の実測データを本にした"
url: "https://qiita.com/yurukusa/items/f9ce40864b7471e3f30b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

CLAUDE.mdの書き方でトークン消費が2倍変わる。これは推測ではなく、800時間の自律運用で測定した結果だ。

この記事では、実際に効果が大きかった3つの変更を**コピペできる形で**紹介する。

## 1. CLAUDE.md: 100行→35行で消費が半減した

### Before（100行版・抜粋）

```
# プロジェクトルール

## コーディング規約
- TypeScriptを使用すること
- ESLintのルールに従うこと
- Prettierでフォーマットすること
- 変数名はcamelCaseを使うこと
- 関数は50行以内にすること
- コメントは日本語で書くこと
- importの順序はbuilt-in → external → internal
- ...（以下50行続く）

## Git規約
- コミットメッセージは日本語で書くこと
- ブランチ名はfeature/xxx形式にすること
- PRにはテンプレートを使うこと
- ...（以下20行続く）

## テスト
- テストカバレッジ80%以上を維持すること
- ...
```

### After（35行版）

```
# Rules
- TypeScript, ESLint, Prettier. See .eslintrc for details
- Functions ≤50 lines. Japanese comments
- Git: Japanese commits. Branch: feature/xxx

# Hooks handle these automatically — don't repeat in text:
# → syntax validation (post-edit hook)
# → branch protection (pre-push hook)
# → secret leak prevention (pre-commit hook)

# Context: ~/docs/ARCHITECTURE.md for project structure
# Don't read files >100KB without asking
```

### 結果

| 指標 | Before | After |
| --- | --- | --- |
| CLAUDE.md行数 | 100行 | 35行 |
| キャッシュ読み取り率 | 89% | 95% |
| セッション消費（推定） | 2x | 1x |
| compaction発生頻度 | 2h以内 | 4h+ |

**原理**: CLAUDE.mdは毎ターンシステムプロンプトとして送られる。100行≒2,500トークン×毎メッセージ。35行にすれば**毎ターン1,600トークン節約**。50往復のセッションで80,000トークン＝$2-3の差。

ポイント:

* hookで自動化できるルールはCLAUDE.mdに書かない（書くとトークンの二重払い）
* 詳細は別ファイルに分離し、必要な時だけ参照させる
* `# Context: ファイルパス` で「読むべき時に読め」と指示

## 2. hookで不要な読み込みを自動ブロック

Claudeは必要以上にファイルを読む。100KBのログファイルや`node_modules`配下を読みに行くのを防ぐだけで、セッションあたり10-20%のトークンを節約できる。

```
// settings.json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Read",
      "hooks": [{
        "type": "command",
        "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path // empty\"); [ -z \"$FILE\" ] && exit 0; SIZE=$(stat -c%s \"$FILE\" 2>/dev/null || echo 0); if [ \"$SIZE\" -gt 102400 ]; then echo \"WARNING: File is $(( SIZE / 1024 ))KB. Consider reading specific sections.\" >&2; fi'"
      }]
    }]
  }
}
```

これで100KB超のファイルを読もうとした時に警告が出る。ブロックはしない（exit 0）が、Claudeは警告を見て行動を変える。

ワンコマンドで8つの安全hookをまとめてインストールすることもできる:

## 3. /costで現状を把握する

最適化の前に、まず現状を知る。`/cost`コマンドを実行すると:

```
Session cost: $2.47
  API cost: $2.47 (cache_read: 85%, cache_creation: 12%, output: 3%)
  Duration: 47 minutes
```

`cache_read`が85%なら健全。**50%以下は異常**——全文をキャッシュなしで毎回送っている状態だ。

最近Opus 4.7に更新した場合は特に注意。[4倍のquota消費](https://github.com/anthropics/claude-code/issues/49618)や[cache\_creationの94%膨張](https://github.com/anthropics/claude-code/issues/47528)が報告されている。

## トークン消費が気になっている人へ

GitHub Issueの[トークン消費スレッド](https://github.com/anthropics/claude-code/issues/42796)には2,600+件のリアクションがある。Anthropic公式も[平均$13/dev/day](https://code.claude.com/docs/en/costs)というデータを公開し、hookによる削減を推奨している。

[Token Checkup](https://yurukusa.github.io/cc-safe-setup/token-checkup.html)（5問・30秒）で自分の消費パターンを無料診断できる。`/cost`の出力を貼り付ける[Cache Health Checker](https://yurukusa.github.io/cc-safe-setup/cache-health.html)もある。

> **Opus 4.7で問題が起きていませんか？** [Safety Scanner](https://yurukusa.github.io/cc-safe-setup/opus47-scanner.html)でsettings.jsonの脆弱性を無料チェック。[Survival Guide](https://yurukusa.github.io/cc-safe-setup/opus-47-survival-guide.html)で全対策を確認。

hookの設計パターンは[Anthropic公式ガイドにない事故防止——800+時間で19点→85点にした全記録](https://zenn.dev/yurukusa/books/6076c23b1cb18b)（¥800・第3章まで無料）。

---

**関連記事**: [Claude Codeのトークン消費を減らす5つの方法——Opus 4.7で+35%になった今やるべきこと](https://qiita.com/yurukusa/items/435810e1e8a046c99916)  
:::note info  
**📖 AIで事業を回す実体験を全記録** → [Claude Code×個人事業 800時間の全記録](https://zenn.dev/yurukusa/books/3c3c3baee85f0a19?utm_source=qiita-f9ce40864b74&utm_medium=article&utm_campaign=book3)（¥800・第2章まで無料）  
:::

---

**⚠️ CVE-2026-21852（2026年4月公開）**: プロジェクト内`.claude/settings.json`経由でAPIキー窃盗。対策: `npx cc-safe-setup`（ユーザーレベル設定で免疫）→ [詳細](https://yurukusa.github.io/cc-safe-setup/opus-47-survival-guide.html#cve-settings-exfil)
