---
id: "2026-04-24-claude-codex-zai-ollama-の使用量を一画面でまとめて見るaimoを作った-01"
title: "Claude / Codex / ZAI / Ollama の使用量を一画面でまとめて見る「aimo」を作った"
url: "https://zenn.dev/ouchan_ip/articles/aimo-ai-usage-monitor"
source: "zenn"
category: "ai-workflow"
tags: ["API", "OpenAI", "GPT", "zenn"]
date_published: "2026-04-24"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

Claude、Codex（ChatGPT）、Z.ai の GLM、Ollama Cloud。複数の AI サービスを並行運用していると、**「今どれなら安全に使えるか？」** を確認するために毎回タブを行き来する羽目になります。

それを 1 画面にまとめる小さなツール、**aimo** を作りました。

<https://github.com/ouchanip/aimo>

![aimo — AI Usage Monitor: unified usage limits for Claude / Codex / ZAI / Ollama Cloud](https://static.zenn.studio/user-upload/deployed-images/d6cf33531fcb413d3ceb0c87.png?sha=78de8e6271ff710d95bf335fd22e87ea43a2fd1d)

## 作ったもの

一言でいうと、**複数 AI サービスの利用制限を束ねて見るためのダッシュボード**です。

* Chromium 系ブラウザ拡張（ポップアップで 4 プロバイダを一覧）
* ローカル HTTP ダッシュボード（`http://localhost:3030`）
* エージェント/スクリプト向け JSON API（`/api/usage`, `/api/refresh`）

対応プロバイダと取得項目：

| プロバイダ | 表示する項目 |
| --- | --- |
| Claude | 5時間 / 週間（All / Sonnet / Opus）/ 追加クレジット |
| Codex（ChatGPT プラン） | 5時間 / 週間 / GPT-5.3-Codex-Spark（Pro プラン時） |
| ZAI（Z.ai） | 5時間クォータ / ツール使用量（プラン次第で月次・週次） |
| Ollama Cloud | セッション / 週間 |

## なぜ作ったか

AI ツールは強力ですが、**使用制限の表示が分断されすぎている** のが地味にストレスでした。

* Claude は `claude.ai/settings/usage`
* Codex は `chatgpt.com/codex/settings/usage`
* ZAI は `z.ai/manage-apikey/subscription`
* Ollama は `ollama.com/settings`

プロバイダごとに **ウィンドウの長さ**（5h / 週 / 月）、**呼び方**（session / five\_hour / TIME\_LIMIT / 5 Hours Quota）、**レスポンスの形** が全部違う。複数使っていると「今どれが安全か」の確認だけでコンテキストが飛ぶ。

aimo はそれを解くだけの道具です。ベンチマークツールでも、プロキシでも、自動化 Bot でもない。**複数 AI システムを能動的に運用する人のための燃料計** です。

## セットアップ画面

一番こだわったのはセットアップ画面です。**API key を貼らなくても動く** のが基本方針。

![aimo Options ページ：プロバイダ有効化、サーバー状態、エージェント API、ZAI JWT キャプチャ状態、各プロバイダの usage ページへのリンク](https://static.zenn.studio/user-upload/deployed-images/327792b25aa77829b84f7084.png?sha=45163c3ead0d0dae4a96fa1aa5a9290cab6f49a0)

各プロバイダの認証は以下の通りに自動化されています：

* **Claude**：`claude.ai` のログインセッション Cookie を使って `/api/organizations/{uuid}/usage` を叩く
* **Codex**：`chatgpt.com` の NextAuth session から `accessToken` を取り出し、Bearer として `/backend-api/wham/usage` へ
* **ZAI**：`z.ai` の `localStorage` に保存されている JWT を content script で自動キャプチャして `api.z.ai/api/monitor/usage/quota/limit` へ（API key は fallback のみ）
* **Ollama**：`ollama.com/settings` を HTML パース

要するに、**既にブラウザで各サービスにログインしているなら、追加の認証設定は実質ゼロ** です。ZAI だけ、初回に `z.ai` を一度開いて JWT をキャプチャする必要があります（拡張の Options から「Open z.ai」ボタン一発）。

## 拡張ポップアップ

拡張アイコンをクリックすると、4 プロバイダが 1 画面に並びます。

![aimo 拡張ポップアップ：Claude / Codex / ZAI / Ollama の各プロバイダの現在の使用率を縦に並べて表示](https://static.zenn.studio/user-upload/deployed-images/e02407eba82135ebf7b7685a.png?sha=102f6bff3d6c69dfe7ae706444b9c58cf3167b65)

各プロバイダのカードには：

* プラン名
* 各ウィンドウ（5h / 週間 / 月次など）の **使用率** と **リセットまでの時間**
* プロバイダ固有の詳細（Claude なら Sonnet / Opus 別、Codex なら Spark 別、ZAI ならツール使用量）

ウィンドウは **リセットまでが短い順** に並んでいるので、今すぐ気にすべき制限が上に来ます。

## インストール

```
git clone https://github.com/ouchanip/aimo
cd aimo
npm install
```

ダッシュボードサーバーを起動：

```
node server.mjs
# → http://localhost:3030
```

拡張の読み込みは：

1. `chrome://extensions`（または `brave://extensions`）で **デベロッパーモード** を有効化
2. 「パッケージ化されていない拡張機能を読み込む」→ `extension/` フォルダを選択
3. 各プロバイダに普通にブラウザでログイン（ZAI は `z.ai` を一度開く）
4. 拡張アイコンをクリックして完了

## エージェント連携例：余裕のあるプロバイダに仕事を振る

エージェントに重めのプロンプトを投げる前に、一番タイトな制限からまだ離れているプロバイダを選ぶ、という使い方ができます。

```
// pick-provider.mjs
const results = await fetch('http://localhost:3030/api/usage').then(r => r.json());

const headroom = (p) => {
  if (!p.ok || !p.windows?.length) return -1;
  const peak = Math.max(...p.windows.map((w) => w.used_pct ?? 0));
  return 100 - peak;
};

const ranked = results.filter((p) => p.ok).sort((a, b) => headroom(b) - headroom(a));
const pick = ranked[0];

console.log(`${pick.provider} に振る — 最もタイトな窓でも ${headroom(pick).toFixed(1)}% 余裕あり`);
```

「使用率の一番高い窓」を各プロバイダで見て、その残量が最大のプロバイダを選ぶ単純なロジック。モデル性能で重み付け、`used_pct > 90` を hard-no にする、コストと組み合わせる、などに拡張できます。

## TOS への配慮

aimo は **自動ポーリングしません**。リクエストが飛ぶのは次のタイミングのみです：

* 拡張ポップアップを開いた時
* ダッシュボード / ポップアップの Refresh ボタンを押した時
* ダッシュボードページを開いた時（1 回）
* エージェントが `GET /api/usage` / `POST /api/refresh` を叩いた時

各リクエストで取得するのは、各プロバイダの使用量ページで自分が見るのと同じデータだけです。aimo は Anthropic / OpenAI / Z.ai / Ollama とは無関係の個人プロジェクトなので、共有アカウントや商用用途で使う場合は各社 TOS を各自で確認してください。

テレメトリーもクラウド同期も持たず、保存される認証トークンは `chrome.storage.local`（ブラウザローカル、非同期）だけです。

## まとめ

* 複数 AI サービスの使用制限を 1 画面にまとめる軽量ツール
* 既存ブラウザのログイン Cookie / localStorage JWT で自動認証、API key は任意
* 手動トリガーのみ、バックグラウンド poll なし
* ダッシュボード + エージェント向け JSON API
* MIT ライセンス

<https://github.com/ouchanip/aimo>

フィードバック / Issue / PR 歓迎です。

## 関連リンク
