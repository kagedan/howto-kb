---
id: "2026-03-27-claude-code専用サーバーを無料で建ててcron-remote-control-で超便利な開-01"
title: "# Claude Code専用サーバーを無料で建てて、cron + remote-control で超便利な開発環境を作る方法"
url: "https://zenn.dev/momozaki/articles/62d027e36657d6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## 使うサービス：Oracle Cloud Free Tier

Oracleの「Always Free」枠が異次元に太っ腹。

| スペック | 内容 |
| --- | --- |
| CPU | Ampere A1（ARM）× 4コア |
| メモリ | **24GB**（永久無料） |
| ストレージ | 200GB |
| 料金 | **永久無料** |

---

## Step 1：インスタンス作成

1. Oracle Cloud に無料登録
2. Compute > Create Instance
3. Shape: **VM.Standard.A1.Flex** / OS: Ubuntu 22.04
4. OCPU: 4 / Memory: **24GB**（スライダー最大）

---

## Step 2：Claude Code インストール

```
# Node.js 20 インストール後
npm install -g @anthropic-ai/claude-code
claude  # APIキー入力で完了
```

---

## Step 3：cron で定期タスク

```
# 毎朝9時にタスクサマリーをLINEへ
0 9 * * * claude -p "今日のタスクをまとめてLINEに送って" --dangerously-skip-permissions

# 毎週月曜にコードレビュー自動実行
0 8 * * 1 cd /home/ubuntu/myproject && claude -p "コードレビューして問題があればissueを作って" --dangerously-skip-permissions
```

---

## Step 4：どこからでもリモートコントロール

**Discord プラグイン（おすすめ）**

```
/plugin install discord@claude-plugins-official
```

→ スマホのDiscordから「あれやっといて」で完結

**SSH + tmux**

```
tmux new -s claude
claude
# Ctrl+B → D でデタッチ（バックグラウンド継続）
```

---

## 実際の使用例

```
📱 スマホのDiscordから：
「今日のプロジェクトの進捗確認して」

☁️ サーバーのClaude Codeが：
→ GitHub 最新コミット確認
→ 未解決issue集計
→ Discordに返信
```

---

## まとめ

* コスト：**永久無料**
* メモリ：最大24GB
* 常駐：24時間稼働
* 操作：Discord / iMessage / SSH
* 自動化：cron + Claude Code

PCを開かずにスマホから「あれやっといて」で完結する世界、最高です。

---

⚠️ `--dangerously-skip-permissions` は確認スキップフラグ。**自分のサーバーのみで使うこと。**
