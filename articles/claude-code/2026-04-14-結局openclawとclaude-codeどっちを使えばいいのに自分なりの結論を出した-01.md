---
id: "2026-04-14-結局openclawとclaude-codeどっちを使えばいいのに自分なりの結論を出した-01"
title: "結局OpenClawとClaude Code、どっちを使えばいいの？に自分なりの結論を出した"
url: "https://zenn.dev/masarufuruya/articles/0f72fa7b765888"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月11日にopenclaw勉強会LTで発表した内容をベースに、OpenClawとClaude Codeの使い分けについて整理した記事です。

普段自分は会社でAI施策を推進するEMをしているのですが、個人ではClaude Codeをメインで使っていました。ただ最近はOpenClawが盛り上がっていて使うかどうか悩んでいたので、その時に調査 & 思考した内容をまとめました。

LT用にササッと調べた内容も含まれるので、細かい箇所は間違っているかもしれません。その場合はコメントで教えていただけると嬉しいです。

## OpenClawの歴史

| 時期 | 出来事 |
| --- | --- |
| 2024年中頃 | Peter Steinberger（PSPDFKit創業者）が個人実験で開発開始 |
| 2025年11月 | **Clawdbot** として公開（WhatsApp→AI、約1時間で構築） |
| 2026年1月 | Anthropic商標苦情 → **Moltbot** → **OpenClaw** にトリプルリブランド |
| 2026年2月 | Peter氏がOpenAIに入社、OpenClawを501(c)(3)財団に移管 |
| 2026年3月〜 | OSS AIエージェントの代表格に成長 |

注目すべきは、創業者がOpenAIに移ったあとも財団ベースで開発が継続している点です。OSSとしての持続性が担保されています。

## 開発モチベーション

OpenClawの当初の目標は3つありました。

1. **複数メッセージングプラットフォームの統合** — WhatsApp / Telegram / Slack / Discord などをバラバラに使う煩雑さを解消
2. **プラグインベースの機能拡張** — モジュラーなスキルシステムで拡張可能に
3. **非技術ユーザーでもAIアシスタントをデプロイ可能に**

Peter氏がPSPDFKitで複数プラットフォーム対応の煩雑さを実感してきた経験が土台になっています。

## OpenClawの仕組み — 3層アーキテクチャ

OpenClawは以下の3層構造で設計されています。

```
メッセージングチャネル（24+ プラットフォーム）
WhatsApp / Telegram / Slack / Discord / LINE / Teams ...
    │
    ▼
┌─────────────────────────────┐
│ Layer 1: Gateway（司令塔）     │
│ セッション管理・ルーティング・認証  │
└─────────────────────────────┘
    │ WebSocket (JSON)
    ▼
┌─────────────────────────────┐
│ Layer 2: Agent Layer（脳）    │
│ Claude / GPT / Gemini / Ollama 等 │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Layer 3: Skills/Actions（手足）│
│ ブラウザ / Canvas / デバイス / 音声 │
└─────────────────────────────┘
```

### 技術スタック

| レイヤー | 技術 |
| --- | --- |
| 主言語 | TypeScript (~65.5M行) |
| ネイティブアプリ | Swift (macOS/iOS), Kotlin (Android) |
| ランタイム | Node.js 24 (推奨) / Node.js 22.16+ |
| パッケージ管理 | pnpm (monorepo with workspaces) |
| ビルド | tsdown (ビルド), Vite (UI) |
| テスト | Vitest (80+設定ファイルでシャード) |
| デプロイ | Docker, Fly.io, Podman, Nix, systemd/launchd |

### 主要な設計判断

| 設計判断 | 説明 |
| --- | --- |
| ローカルファースト | データはすべてデバイス上に保存。クラウドバックエンド不要 |
| Gateway = 司令塔は1つだけ | 全プラットフォームからのメッセージを1つの司令塔で処理 |
| プラグインの出入口を厳しく制限 | Extensionは `plugin-sdk/*` からのみインポート可。core `src/**` の直接参照は禁止 |
| TypeScript主軸 | ネイティブ機能が必要な箇所のみSwift/Kotlin |
| MCPはブリッジ経由 | `mcporter` 外部ブリッジで対応。コアランタイムに組み込まず安定性を確保 |

## なぜセキュリティリスクがあるのか？

GMOサイバーセキュリティ（イエラエ）が指摘した「致命的な三要素」があります。

| # | リスク要素 | 内容 |
| --- | --- | --- |
| 1 | プライベートデータへのアクセス | ファイル、ブラウザデータ、APIキーに触れる |
| 2 | 信頼できないコンテンツの処理 | ClawHubスキルがフル権限で実行される |
| 3 | 外部通信能力 | ネットワーク・メール・ブラウザ操作が自由 |

PCに対する広範な操作権限を持って**自律的に動く**エージェントであるため、脆弱性・マルウェアの被害が増大しやすいという構造的な問題があります。

### 実際に起きたインシデント

**CVE-2026-25253（RCE脆弱性）**

* 悪意あるリンク **クリック1回** でリモートコード実行
* CVSSスコア **8.8**（深刻）
* 2026年1月29日パッチ済み

**ClawHub悪意あるスキル**

* Koi Security社監査: 2,857スキル中 **341件が悪意あるスキル**（約12%）
* Atomic macOS Stealer の配布に利用された事例も

**CVE-2026-32922（特権昇格）**

## セキュリティ対策 — 推奨

OpenClawを使うなら、以下のような対策が挙げられます。

| # | 対策 | 設定 |
| --- | --- | --- |
| 1 | バージョン更新 | **v2026.3.11以上**（最新CVE対応済み） |
| 2 | ゲートウェイバインド | `gateway.bind: "loopback"` 0.0.0.0で公開しない |
| 3 | ゲートウェイトークン | 64文字のランダム文字列 |
| 4 | ファイアウォール | ポート18789を外部からブロック |
| 5 | リモートアクセス | Tailscale Serve or SSHトンネルのみ |

### Docker隔離

```
services:
  openclaw-server:
    security_opt:
      - no-new-privileges    # 特権昇格を禁止
    cap_drop:
      - ALL                  # 全ケーパビリティをドロップ
    read_only: true          # read-onlyルートFS
    tmpfs:
      - /tmp                 # /tmpのみ書き込み可
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
```

### サンドボックス設定

```
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "all",
        "backend": "docker",
        "scope": "session",
        "workspaceAccess": "none"
      }
    }
  }
}
```

`workspaceAccess: "none"` でホストのファイルに一切触れなくなるのがポイントです。

## OpenClawとClawXの関係

ClawXは **OpenClawコアを内蔵** したデスクトップGUIアプリです。ClawX単体でAIエージェントとして使えます（OpenClaw別途インストール不要）。

| 項目 | ClawX（GUI） | OpenClaw（CLI/Docker） |
| --- | --- | --- |
| 位置づけ | オールインワンGUIアプリ | コアランタイム + CLI |
| 内部構造 | Electron内にGatewayをバンドル | Gateway単体 |
| 初期セットアップ | ウィザードで完結 | 設定ファイル手動編集 |
| ターミナル不要？ | **基本利用はYes** | ターミナル必須 |

### ClawXだけでできること（GUI）

* AIプロバイダー設定・モデル切替
* チャネル接続（Slack / Discord / Telegram等）
* スキルのインストール・有効化
* 基本的なサンドボックス設定（Docker Env変数注入等）
* セッション管理・承認操作

### ClawXだけではできないこと（ターミナル必須）

* Docker Composeによる本格隔離（`cap_drop: ALL`, `read_only` 等）
* ファイアウォール設定（ポート18789ブロック）
* Tailscale / SSHトンネル経由のリモートアクセス構築
* `openclaw.json` の細かいセキュリティパラメータ編集

**セキュリティを突き詰めるとターミナルが必要になる**、というのが重要なポイントです。ClawXは「OpenClawの入り口を簡単にするもの」であり「セキュリティの責任を肩代わりするもの」ではありません。

## 4ツール比較

Claude Code / OpenClaw / Agent SDK / Managed Agents を比較します。

### サマリー

| 観点 | Claude Code | OpenClaw | Agent SDK | Managed Agents |
| --- | --- | --- | --- | --- |
| 24/7稼働 | △ 工夫要 | ◎ 常駐設計 | ◎ 自由構築 | ◎ フルマネージド |
| 実装の要否 | 不要〜軽量 | 中程度 | 要 (Py/TS) | 要 (API/SDK) |
| セキュリティ | ◎ 多層防御 | △ 自己責任 | ○ 自己構築 | ◎ Anthropic管理 |

### セキュリティ詳細

| ツール | レベル | 特徴 |
| --- | --- | --- |
| **Claude Code** | ◎ | allow/ask/denyの3層 + OSサンドボックス + Hooks + SOC2準拠 |
| **OpenClaw** | △ | CVE多数（CVSS 9.9含む）。デフォルトが危険。ClawHubサプライチェーン攻撃実績 |
| **Agent SDK** | ○ | 粒度の細かいツール制御 + 多層サンドボックス。ただし全て自己構築 |
| **Managed Agents** | ◎ | セッション独立コンテナ + セキュアVault + ドメイン制限 + 監査トレース |

## 結論: 自分はOpenClawを使わない選択（現時点）

コードを読んでエージェント自作する上で **構成・設計を参考にする程度** に抑えています。

### 理由

1. **セキュリティ対策の運用コストを自分で払いたくない** — Docker隔離・CVE追従・ハードニング...継続的な負荷が大きい
2. **Mac mini/Studioを別で買って壊れる覚悟で運用するお金は使いたくない**
3. **Claude Code + Codexサブスクの使い分け + ハーネス整備が現実的** — コストを抑えつつセキュリティも担保できる
4. **会社でも横展開できるノウハウ方針にしたい** — 会社のAI施策を推進するマネージャーとして、セキュリティ担保しながら24/7・リモート稼働できる自作エージェントのノウハウは会社でも使える
5. **OpenClawの常駐Botでしかできないユースケースが思い浮かばない**

## おわりに

OpenClawは3層アーキテクチャや設計判断など、学びが多いOSSプロジェクトです。ただし、セキュリティ面でのデフォルト設定の危うさやサプライチェーン攻撃の実績を考えると、内部をしっかりと理解したエンジニア向けのツールでしょう。今までプログラミングを経験したことがないような非エンジニアは慎重に使った方が良いと思います。

自分のケースでは、Claude Code + ハーネス整備で24/7エージェント運用のニーズを満たしつつ、OpenClawのアーキテクチャは設計の参考として活かす、という使い分けに落ち着きました。

ツール選定は「何ができるか」だけでなく「自分が必要とするユースケース」で判断するのが大事だと思います。

## 元資料

<https://speakerdeck.com/mfuruya/20260410-openclawmian-qiang-hui-ltsuraito>
