---
id: "2026-05-09-harness-engineering-とは何か-2026年2月から90日で業界共通語になった概念の-01"
title: "Harness Engineering とは何か ― 2026年2月から90日で業界共通語になった概念の正体"
url: "https://zenn.dev/zztomcat/articles/6ceaa1abea7f52"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "OpenAI"]
date_published: "2026-05-09"
date_collected: "2026-05-10"
summary_by: "auto-rss"
query: ""
---

# 

```
---
title: "Harness Engineering とは何か ― 2026年2月から90日で業界共通語になった概念の正体"
emoji: "🪝"
type: "tech"
topics: ["AI", "生成AI", "AIエージェント", "ClaudeCode", "GitHubCopilot"]
published: true
---
```

## TL;DR

* **Harness Engineering** は2026年2月5日にMitchell Hashimoto（HashiCorp共同創業者・Terraform作者）が命名した
* 90日後の現在、OpenAI / Anthropic / LangChain / Martin Fowler / Ethan Mollick が全員追随し、AIエンジニアリングの**標準語**になった
* 中核公式は **Agent = Model + Harness** ― AIエージェントの信頼性を決めるのはモデルではなく、その周りの制御環境
* 直訳すれば「馬具」。馬を制御し、同時に馬の力を引き出す。AIエージェントも同じ

## なぜこの言葉が必要だったか

過去2年、AI開発の語彙は急速に増えた。Prompt Engineering、Context Engineering、AGENTS.md、MCP、Spec-Driven Development、Vibe Coding ― 全部、関連はするが本質的に別物だ。

問題は、これらを**統括する上位概念がなかった**こと。

「プロンプトをどれだけ磨いても、47回目のループで忘れられる」  
「CLAUDE.md に書いた制約は、長いセッションの中盤で消える」  
「テストを書かせても、テスト自体をスキップする」

― この種の事故を防ぐのは、プロンプトでも、文脈でも、テストでもない。\*\*それら全部を上から束ねる「メカニズム」\*\*だ。

Hashimotoは、まさにそれに名前をつけた。

## Hashimoto の定義

> "It is the idea that anytime you find an agent makes a mistake, you take the time to engineer a solution such that the agent never makes that mistake again."
>
> （エージェントが何か間違えるたびに、その間違いが二度と起こらないように環境を作り直す ― それが Harness Engineering だ）
>
> ― Mitchell Hashimoto, "My AI Adoption Journey", February 5, 2026

短く、痛烈。**一度の修正ではなく、構造に対策を埋め込む**。これが Harness の本質だ。

## Agent = Model + Harness

Hashimotoが残した最重要公式：

意味するところ：

| 要素 | 役割 | 例 |
| --- | --- | --- |
| Model | 推論能力 | Claude Opus 4.7 / GPT-5.4 / Gemini |
| Harness | 制御環境 | AGENTS.md / lint / CI / Kill Switch / Eval suite |

**モデルをどれだけ強くしても、Harnessが弱ければエージェントは壊れる。**

OpenAIのRyan Lopopoloは、この公式を実証で裏付けた。彼らは2026年2月、3名のエンジニアが5ヶ月で**約100万行のコードを「人手による記述ゼロ」で本番投入**した（Codexエージェントが全コード生成、約1,500のPRを統合）。

これを可能にしたのが「Harness Engineering」だ。

## 構成要素：Guides と Sensors

Martin Fowler / Birgitta Böckeler は、Harness を2層に分解した：

### Guides（事前の制約）

* AGENTS.md / CLAUDE.md（過去の失敗を1行ずつ追記する学習履歴）
* システムプロンプト
* ルール文書

### Sensors（事後の検証）

* Lint / Type checker
* Eval suite
* CI/CDゲート
* Kill Switch

両者の組み合わせが Harness を作る。**片方だけでは機能しない**。

## Hashimoto 自身のジャーニー

彼は懐疑派からスタートし、6ステップでこの概念に到達した：

1. **Drop the Chatbot** ― ブラウザ上のChat UIをやめる
2. **Reproduce Your Own Work** ― 自分のコードをAIで再現させる訓練
3. **End-of-Day Agents** ― 終業時の宿題エージェント
4. **Outsource the Slam Dunks** ― 明白なタスクを外注する
5. **Engineer the Harness** ← ここで質的変化
6. **Always Have an Agent Running** ― 常時運用

Step 5 が「役割の質的変化」だ。コードを書く人 → 環境を設計する人。

## 日本での意義

日本語圏では、Phase 5（Harness確立期）の事例も書籍もまだ皆無に近い。  
本記事の続編として、以下を順次公開予定：

* Mitchell Hashimoto 6ステップを完全解説
* Agent = Model + Harness が示すAI信頼性の本質
* 5方法論の境界マップ（Vibe / Spec / TDD / Context / Harness）
* OpenAI Codex 100万行の内幕
* AGENTS.md / CLAUDE.md / copilot-instructions.md の3ファイル統一戦略

## 参考文献

* Mitchell Hashimoto, "My AI Adoption Journey", <https://mitchellh.com/writing/my-ai-adoption-journey> , Feb 5, 2026
* Ryan Lopopolo (OpenAI), "Harness engineering: leveraging Codex in an agent-first world", Feb 11, 2026
* Martin Fowler, "Harness Engineering - first thoughts", <https://martinfowler.com/articles/exploring-gen-ai/harness-engineering-memo.html>
* HumanLayer, "Skill Issue: Harness Engineering for Coding Agents", March 12, 2026
* LangChain, "Improving Deep Agents with Harness Engineering", Feb 17, 2026

---

## 📘 この記事は書籍『AI駆動開発 完全実践ガイド』の先行公開コンテンツです

本記事の内容は、**2026年6月15日発売予定**の書籍『AI駆動開発 完全実践ガイド ― Vibe期からHarness確立期へ』の一部を再編集したものです。

![alt text](https://static.zenn.studio/user-upload/05798be6ba6d-20260510.png)

書籍では本記事の3〜5倍の解像度で、以下を体系化しています：

* 5段階成熟度モデル（Vibe / Prompt整備 / Context整備 / SDD-TDD / Harness）
* Phase × 3大Agent（Copilot / Codex / Claude Code）マトリクス
* ルールファイル統一戦略（AGENTS.md / CLAUDE.md / copilot-instructions.md）
* 失敗パターン9種と対処法
* 18-24ヶ月の段階的導入ロードマップ

本書籍の特徴と位置付け：

| 軸 | 市場中他書籍の現状（2026年5月） | 本書の特徴独自ポジション |
| --- | --- | --- |
| 思想層 | Vibe Coding / プロンプト中心 | Phase 5 (Harness確立期) を扱う日本語圏初の書籍 |
| 方法論 | 単一ツール解説（Copilot本／Claude Code本） | 5方法論×5Phase×3大Agentのマトリクス |
| 経営視点 | 技術書中心、経営層向けはほぼ皆無 | Executive Summary 5セクションを巻頭装着 |
| 鮮度 | Karpathy 2025/Vibe命名止まり | Mitchell Hashimoto 2026/2、OpenAI Codex 100万行、Anthropic Managed Agentsを完全反映 |
| 差別化最強章 | ー | Ch.4-1 　　　　ルールファイル統一戦略（AGENTS.md / CLAUDE.md / copilot-instructions.md）= 世界初の書籍化 |

📅 電子版発売予定日：2026年6月15日　（※前後にする可能性がある）  
📅 書籍版の販売予定日は調整中  
📚 全75章 + 付録24種  
🎯 日本語圏初の Phase 5（Harness確立期）対応書籍

発売告知をX（[@ZY20240528]）でお届けします。事前興味のある方はフォローお願いします。
