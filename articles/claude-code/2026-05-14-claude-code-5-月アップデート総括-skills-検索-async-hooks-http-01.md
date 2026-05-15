---
id: "2026-05-14-claude-code-5-月アップデート総括-skills-検索-async-hooks-http-01"
title: "Claude Code 5 月アップデート総括 — skills 検索 / async hooks / HTTP hooks を個人開発パイプラインへ組み込む"
url: "https://qiita.com/creolab_dev/items/5f058d93b1f88c43f339"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "qiita"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

# Claude Code 5 月アップデート総括 — skills 検索 / async hooks / HTTP hooks を個人開発パイプラインへ組み込む

## はじめに

2026 年 5 月、Claude Code に静かですが構造的に重要な変更が三点入りました。

1. **skills 検索ボックス** の追加 (出典: https://code.claude.com/docs/en/skills)
2. **PostToolUse hooks の `updatedToolOutput` が全ツールに拡張**、加えて **`async: true`** フラグの追加 (出典: https://claudefa.st/blog/tools/hooks/hooks-guide)
3. **HTTP hook** の登場 — hook から外部 web server に POST 可能 (同上)

私は CreoLab メディア運営パイプラインを毎日触っており、この三点は単独機能というより「組み合わせて初めて効く」変更でした。本記事では企業エンジニア視点で、自社の開発自動化や CI/CD ワークフローに転用するときの設計観点を整理します。

## 1. skills 検索ボックス — 「skill 一覧の認知負荷」問題への解

これまで Claude Code の skills はファイル名で覚えるか、ヘルプで一覧表示するしかありませんでした。組織で skills を共有すると、すぐに数十〜100 を超え、誰も全体を把握できなくなります。

5 月の更新で `/` メニューから skill 名・description を曖昧検索できるようになりました。地味な UI 改修ですが、これは「skill カタログを資産として運用する」運用設計を実用可能にする変更です。チーム配布の skills 命名規則 (`{domain}-{verb}-{noun}`) や description テンプレート整備に投資する価値が出てきました。

## 2. async hooks — 同期 hook ではブロックしていた副作用を切り離す

PostToolUse hooks に `async: true` フラグが追加されました。

```jsonc
// ~/.claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "async": true,
        "command": "node scripts/notify-slack.mjs"
      },
      {
        "matcher": "Edit",
        "async": true,
        "command": "tsx scripts/run-lint-fix.ts"
      }
    ]
  }
}
```

従来 hooks は同期実行で、Slack 通知や lint 自動実行など秒オーダーの副作用を hook に挟むと、次のツール呼び出しまで Claude Code が止まりました。`async: true` を付けると hook はバックグラウンドへ切り離されメインフローは即時進行します。

CreoLab パイプラインの実測では、`master.md` 書き出し後の Discord 通知と画像生成 (1 分超) を async 化することで Phase 3 → 4 の遷移が 30-60 秒短縮されました。社内利用では Slack 通知 / 自動テスト実行 / CI ジョブのキック / GitHub Issue 自動更新といった用途で効きます。

ただし async hook の失敗が静かに闇に消える問題があります。バックグラウンドに切り離した副作用の stderr を集約する wrapper を 1 枚挟む構成を推奨します。

```bash
#!/usr/bin/env bash
# scripts/wrap-async-hook.sh
set -o pipefail
"$@" 2> >(tee -a /tmp/claude-async-hook.err >&2)
if [ $? -ne 0 ]; then
  curl -sS -X POST "$SLACK_ERRORS_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d "$(jq -nc --arg msg "async hook failed: $*" '{text: $msg}')"
fi
```

## 3. HTTP hooks — Claude Code を「外部サーバの起点」に変える

更に重い変更が、hook から外部 web server に直接 HTTP POST できるようになった点です。

```jsonc
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "async": true,
        "http": {
          "url": "https://example.internal/ci/trigger",
          "method": "POST",
          "headers": {
            "Authorization": "Bearer $INTERNAL_CI_TOKEN"
          },
          "bodyTemplate": "{\"file\": \"${updatedToolOutput.path}\", \"event\": \"write\"}"
        }
      }
    ]
  }
}
```

社内 CI、Issue Tracker、内製ダッシュボードへのイベント発火を、hook 1 行で書けるようになります。CreoLab では Buffer / Zenn / Qiita API への投稿予約 hook がこれに該当しますが、企業エンジニア視点では「PR を開いたら社内 lint daemon に POST」「ファイル変更を Datadog にメトリクス送信」などの用途が直接刺さるはずです。

## 4. 設計上の注意点 3 点

実運用で避けるべき設計上の落とし穴を 3 つ挙げます。

1. **async hook の失敗ハンドリング** — stderr 集約 wrapper を必ず挟み、Slack / Sentry / Datadog のいずれかへ転送する
2. **認証情報のベタ書き** — `~/.claude/settings.json` は git に乗りやすいため、トークンは `.env` 経由 or 秘匿 wrapper 越しに呼ぶ
3. **PreToolUse / PostToolUse の責務曖昧化** — 「結果を見て副作用」は PostToolUse、「結果を出す前に検証 / 拒否」は PreToolUse と原則を明文化しておく

## まとめ

5 月の三点更新は派手な機能追加ではないものの、「skills と hooks を増やすほどローカル運用が重くなる」というスケーリング問題への構造的回答です。CreoLab の見解として、これは Claude Code を個人開発から少人数チーム規模へスケールさせるための前提条件が一段揃った変更だと位置付けています。

私が CreoLab パイプラインで実装した結果、Phase 4 (packager 並列実行) の起動が 30-60 秒短縮されました。社内利用でも CI / 通知 / 検査の hook 化が現実的になります。

## 参考

- Claude Code Release Notes (2026 年 5 月): https://releasebot.io/updates/anthropic/claude-code
- Claude Code Hooks Guide: https://claudefa.st/blog/tools/hooks/hooks-guide
- Claude Code Skills Docs: https://code.claude.com/docs/en/skills

## 関連プロダクト

- CodeMap — 増えていく `~/.claude/skills/` や `agents/` ディレクトリを構造化し、hook 設計を俯瞰するための巨大コードベース読解ツール: https://codemap.creolab.dev
