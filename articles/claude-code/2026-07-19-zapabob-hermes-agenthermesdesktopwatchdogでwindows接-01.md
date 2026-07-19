---
id: "2026-07-19-zapabob-hermes-agenthermesdesktopwatchdogでwindows接-01"
title: "zapabob × Hermes Agent：HermesDesktopwatchdogでWindows接続を安定させる"
url: "https://zenn.dev/zapabob/articles/zapabob-hermesagent-watchdog-contributor"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-07-19"
date_collected: "2026-07-20"
summary_by: "auto-rss"
query: ""
---

## はじめに

[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) は「The agent that grows with you」をキャッチコピーとした、自律型AIエージェント基盤です。2026年7月7日にリリースされた **v0.18.2** は WhatsApp ゲートウェイの依存関係（`Baileys` を特定の git コミットではなく `7.0.0-rc13` に固定解除）を修正したパッチリリースです。

本記事では、日本人コントリビューターとして知られる **zapabob** の活動と、その独自ツール **HermesDesktopwatchdog** が何を解決しているのかをDeepresearchに基づき解説します。

> **一次資料**

---

## zapabob は 0.18.2 以降も活発に貢献しているか？

**✅ 事実確認：貢献継続を確認**

GitHub のメタデータから、`zapabob` は NousResearch 公式リポジトリのコントリビューターリストに登録されており、fork（`zapabob/hermes-agent`）を通じた上流へのフィードバック・バグ報告も継続しています。

| 観点 | 状況 |
| --- | --- |
| NousResearch 公式リポジトリへの貢献 | コントリビューターとして記載済み |
| fork の目的 | Windows ワークステーションでの運用最適化 |
| 0.18.2 以降の活動 | fork の維持継続・Windows 固有の修正を提供 |
| 主な貢献領域 | Electron（デスクトップ GUI）の安定化、パス処理、プロセス管理 |

v0.18.0（「Judgment Release」）では NousResearch チームが「P0/P1 のバグをゼロにする」方針を掲げて大規模修正を行いました。zapabob はその方針に沿ったWindows 側の追従作業を担っています。

---

## HermesDesktopwatchdog とは何か

### 概要

[HermesDesktopwatchdog](https://github.com/zapabob/HermesDesktopwatchdog) は、**Go** 製のスタンドアロン・プロセス監視ツールです。

> Standalone Go watchdog for Hermes Agent on Windows.  
> It mutually monitors packaged **Hermes Desktop** (`Hermes.exe`) and the Desktop-spawned / prewarmed `hermes serve` backend.
>
> *— README より直接引用*

```
Not a Hermes plugin, skill, MCP server, or cron job.
Hermes Agent tools and sessions must not control this process.
```

Hermes Agent のスキル・セッションから**意図的に分離**された設計になっています。

### アーキテクチャ上の分離

| 項目 | 詳細 |
| --- | --- |
| プロセス | Hermes Python / Electron とは独立した Go プロセス |
| 状態管理 | `%LOCALAPPDATA%\HermesWatchdog\`（ロック + ステータス JSON） |
| ログ | `%HERMES_HOME%\logs\hermes-go-watchdog.log` |
| Mutating API | `HERMES_WATCHDOG_ADMIN_TOKEN` が必要（なければ **403**） |
| Read API | `GET /health`, `GET /api/status`（localhost / Tailscale 経由） |

### 解決している問題

Hermes Agent の Windows 運用における既知の不安定性：

1. **ゲートウェイ停止**：長時間稼働でネットワーク断絶・API タイムアウトにより `hermes serve` が落ちる
2. **誤検知再起動ループ**：`ss` コマンドベースの監視スクリプトが Windows 環境で誤動作し、不要な再起動を繰り返す
3. **stale marker 問題**：古い「計画停止マーカー」が残ると、再起動時に「UNKNOWN 終了」判定でクラッシュ（upstream Issue #34597 相当）

HermesDesktopwatchdog はこれらを Go の独立プロセスで解決します。

```
# ビルド
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Build-HermesGoWatchdog.ps1
# 出力: dist\hermes-watchdog.exe

# 起動
$env:HERMES_WATCHDOG_ADMIN_TOKEN = "<operator-secret>"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-HermesGoWatchdog.ps1 `
  -HermesRoot "C:\path\to\hermes-agent" `
  -BuildIfMissing
```

---

## zapabob fork の位置づけ

```
NousResearch/hermes-agent  ← 本流（upstream）
        │
        └── zapabob/hermes-agent  ← Windows 最適化 fork
                │
                └── HermesDesktopwatchdog  ← scripts/windows/watchdog-go/ から抽出・公開
```

* `HermesDesktopwatchdog` の README には「`zapabob/hermes-agent` の `scripts/windows/watchdog-go/` から抽出した公開オペレーターツール」と明記されています
* fork 内で育てた Windows 向けツールを独立リポジトリとして公開するという、日本人 OSS コントリビューターとして珍しい実装ループです

---

## Hermes Agent v0.18.x のデスクトップ・バックエンド分離

v0.18.0 以降、Hermes Desktop は「単なる UI レイヤー」として機能します：

* デスクトップアプリ → ローカル CLI (`hermes serve`) に接続
* または → リモートバックエンド（WebSocket `/api/ws`）に接続

接続が不安定になる主因はゲートウェイ（WebSocket 接続）の再起動ループです。HermesDesktopwatchdog はこの「`Hermes.exe` と `hermes serve` の相互監視」を担います。

```
Hermes.exe (Electron) ←── HermesDesktopwatchdog (Go) ──→ hermes serve (Python)
```

単方向ではなく**相互監視**である点が重要です。デスクトップが落ちたらバックエンドも制御し、バックエンドが落ちたらデスクトップに通知することで、孤立プロセスによるリソース浪費を防ぎます。

---

## Deepresearch まとめ

| 検証項目 | 結果 |
| --- | --- |
| zapabob が v0.18.2 以降も活発に貢献しているか | ✅ 確認。fork 維持継続・upstream フィードバック継続 |
| HermesDesktopwatchdog が接続不安定性を解決しているか | ✅ 確認。Go スタンドアロン相互監視により既知の Windows 固有クラッシュ・再起動ループを解消 |
| HermesDesktopwatchdog の独立性 | ✅ 確認。Hermes の skill / MCP / cron から意図的に分離された設計 |
| 情報の信頼度 | 一次資料（README 直接引用・GitHub メタデータ）に基づく |

---

## おわりに

zapabob のアプローチは「本流に従いつつ、現場（Windows）の問題を自分で解く」という実装者スタイルです。HermesDesktopwatchdog は「AIエージェントをAIに管理させない」という設計哲学を体現しており、Hermes の長期安定運用に関心がある方には参考になるツールです。

---

## 参考リンク
