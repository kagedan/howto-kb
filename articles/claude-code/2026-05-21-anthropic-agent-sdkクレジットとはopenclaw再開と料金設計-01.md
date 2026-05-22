---
id: "2026-05-21-anthropic-agent-sdkクレジットとはopenclaw再開と料金設計-01"
title: "Anthropic Agent SDKクレジットとは？OpenClaw再開と料金設計"
url: "https://zenn.dev/zenchaine/articles/anthropic-agent-sdk-credits-openclaw"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-05-21"
date_collected: "2026-05-22"
summary_by: "auto-rss"
query: ""
---

## 何が変わったのか？

Anthropicは、Claude有料プランに **Agent SDKクレジット** という月次枠を追加します。これはClaudeの通常チャット枠とは別に、Claude Agent SDKや `claude -p`、Claude Code GitHub Actions、Agent SDK経由のサードパーティーアプリで使う専用クレジットです。

開始日は公式ヘルプ上で2026年6月15日とされています。対象はPro、Max、Team、Enterpriseの有料ユーザーです。

| プラン | 月次クレジット |
| --- | --- |
| Pro | $20 |
| Max 5x | $100 |
| Max 20x | $200 |
| Team Standard | $20 |
| Team Premium | $100 |
| Enterprise usage-based | $20 |
| Enterprise Premium | $200 |

ポイントは、通常のClaudeチャットや対話型Claude Codeの枠とは分かれることです。

## 何に使えて、何に使えないのか？

Agent SDKクレジットの対象は、プログラムからClaudeを呼ぶ用途です。

対象:

* Claude Agent SDK
* `claude -p`
* Claude Code GitHub Actions
* Agent SDKで認証するサードパーティーアプリ

対象外:

* Claude Web / Desktop / Mobile の会話
* 対話型Claude Code
* Claude Cowork
* APIキー経由のClaude Developer Platform利用

クレジットは個人単位で、チーム内共有や翌月繰り越しはできません。使い切った後は、追加利用をONにしていれば標準API料金へ移り、OFFなら次回更新までリクエストが止まります。

## なぜOpenClawが関係するのか？

OpenClawは、LLMを接続して自律型エージェントを動かすオープンソース基盤です。人間が1回ずつチャットするのではなく、エージェントがファイルを読み、調査し、再試行しながらタスクを進めます。

この使い方は便利ですが、モデル提供側から見ると計算資源の消費が大きくなります。2026年4月、AnthropicはOpenClawのようなサードパーティーエージェントがClaudeサブスクリプション枠を使うことを制限しました。

今回のAgent SDKクレジットは、その制限を完全に元に戻すものではありません。むしろ、外部エージェント利用を専用クレジットに閉じ込める再設計です。

```
以前の争点:
  Claudeサブスク枠で外部エージェントが大量推論を消費

今回の設計:
  外部エージェントはAgent SDKクレジットを消費
  超過分は標準API料金、または停止
```

## OpenAI / Codexとの違いは？

OpenAI公式ヘルプでは、CodexはChatGPT Plus、Pro、Business、Enterprise/Eduプランに含まれると説明されています。Codex CLIやIDE拡張はChatGPTアカウントでサインインできます。

OpenClawのOpenAIプロバイダードキュメントも、OpenAI APIキーとChatGPT/Codexサブスクリプション認証の2系統を説明しています。つまりOpenAI側は、「CodexをChatGPTプランの一部として使う」体験を前面に出しています。

一方、Anthropicは今回、次のように分けました。

| 観点 | Anthropic | OpenAI |
| --- | --- | --- |
| 通常チャット | Claudeサブスク枠 | ChatGPTプラン |
| コーディングエージェント | 対話型Claude Codeは通常枠 | CodexはChatGPTプランに含まれる |
| 外部エージェント | Agent SDKクレジット | OpenClaw docsはCodex OAuthを案内 |
| 超過 | API料金または停止 | プラン制限・追加クレジット・APIキー |

これは推測を含みますが、AnthropicにとってAgent SDKクレジットは、OpenAI/Codex陣営に対抗しつつ、計算資源コストを制御するための折衷案に見えます。

## Claude Code週次制限50%増も同じ文脈で見る

もう1つ重要なのが、Claude Code本体の週次利用制限も一時的に増えていることです。

PC Watchは、ClaudeDevsの公式X投稿として、Claude Codeの週次利用制限が2026年7月13日まで50%増加すると報じています。対象はPro、Max、Team、シートベースEnterpriseで、CLI、IDE拡張、デスクトップ、Webに適用されます。

これは、Anthropicが外部エージェントを締めたいだけではないことを示しています。むしろ構図は次のように見えます。

```
Claude Codeの対話型利用:
  5時間制限を2倍化
  週次制限を7月13日まで50%増

Agent SDK / claude -p / 外部エージェント:
  通常サブスク枠から分離
  Agent SDKクレジットへ移動
```

OpenAI側では、CodexがChatGPTプランに含まれ、Plus/Proユーザーは上限到達後に追加クレジットも購入できます。さらにCodexは、2026年4月からトークンベースのレートカードへ移っています。

そのため、今回のClaude Code週次制限50%増は、OpenAI/Codexの「ChatGPTプランでコーディングエージェントを使う」体験への対抗策にも見えます。Anthropicは、Claude Codeの体験を厚くしつつ、自動実行系だけを別会計に分ける方向へ舵を切っています。

## 開発者はどう使い分けるべきか？

Agent SDKクレジットは、個人の自動化や軽いエージェント実験には向いています。突然の高額請求を避けたい場合は、追加利用をOFFにしておくのが安全です。

一方で、長時間OpenClawを回す、CIで大量にClaudeを呼ぶ、チーム共通の本番自動化を作る、といった用途では、専用クレジットだけを前提にしないほうがよいです。

おすすめの使い分け:

* 個人の検証: Agent SDKクレジット
* 対話型の開発: Claude Code通常枠
* 長時間OpenClaw: 使用量監視 + API料金想定
* チームの本番自動化: APIキー + 予算管理
* OpenAI系ワークフロー: Codexプラン制限と追加クレジットを確認

## まとめ

AnthropicのAgent SDKクレジットは、「OpenClawを再び使えるようにした」というニュースであると同時に、「自律型エージェントは通常チャットとは別会計にする」という料金設計のニュースです。

AIエージェントの競争は、モデル性能だけでは決まりません。サブスクでどこまで動かせるか、超過時に止まるのか課金されるのか、外部ツールがどこまで認証できるのか。こうした料金と認証の設計が、開発者体験を大きく左右します。

## 参考ソース

---

詳しい背景と比較は、ZenChAIneの記事でも公開しています。

<https://zench-aine.io/media/anthropic-agent-sdk-credits-openclaw>
