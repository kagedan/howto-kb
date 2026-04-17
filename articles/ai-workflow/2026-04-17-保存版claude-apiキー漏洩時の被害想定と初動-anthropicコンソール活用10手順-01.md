---
id: "2026-04-17-保存版claude-apiキー漏洩時の被害想定と初動-anthropicコンソール活用10手順-01"
title: "【保存版】Claude APIキー漏洩時の被害想定と初動 ─ Anthropicコンソール活用10手順"
url: "https://qiita.com/kawabe0201/items/71093745385be8c713b0"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

Claude APIキーが公開リポジトリやログに漏洩してしまった際、何分で何をやるかで被害額が桁違いに変わる。Anthropicコンソールから打てる打手を時系列に整理し、自社のインシデントランブックに落とし込めるレベルにまとめた。

## 被害想定

Claude APIは従量課金である。仮に Sonnet 4系で1Mトークン入力5ドル前後、出力15ドル前後という料金体系のもと、漏洩キーが大量の長文生成に悪用されると、数時間で数百ドルから数千ドルに到達しうる。加えて、自分のOrganizationの利用上限を食い潰され、正規ワークロードが止まる二次被害もある。

## 初動10手順

### 1. 漏洩を確認した瞬間にキー失効

Anthropicコンソール → Settings → API Keys から該当キーの `Delete` を押す。失効は即時反映され、以降その値では認証できなくなる。

### 2. 新しいキーを発行して動作確認

```bash
export ANTHROPIC_API_KEY=sk-ant-新しいキー
python -c "import anthrop
