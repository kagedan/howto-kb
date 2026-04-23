---
id: "2026-04-14-claude-code-v21100でトークン消費が40増えたcache-creation膨張の原因-01"
title: "Claude Code v2.1.100でトークン消費が40%増えた——cache_creation膨張の原因と削減方法"
url: "https://qiita.com/yurukusa/items/c0acc6da4cb1c90fa431"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

Claude Code v2.1.100以降、同じCLAUDE.mdを使っているのにトークン消費が約40%増えている。

これは体感ではなく計測された事実だ。GitHub Issue [#46917](https://github.com/anthropics/claude-code/issues/46917)では、v2.1.98で49,726トークンだった`cache_creation_input_tokens`が、v2.1.100では69,922トークンに膨張していると報告されている。投稿から数日で92リアクションがついた。

## 何が起きているか

`/cost`コマンドで確認できる`cache_creation_input_tokens`が、v2.1.100以降で約20,000トークン増えている。ペイロードは同一。CLAUDE.mdも同じ。サーバー側で何かが変わった。

影響:

* **コスト**: cache\_creationはcache\_readの約4倍のコスト（Anthropic API価格表準拠）
* **コンテキスト**: 20Kトークン分だけコンテキストウィンドウが圧迫される
* **体感**: 同じ作業なのに早くquotaが尽きる

## 自分が影響を受けているか確認する方法

1. Claude Codeで`/cost`を実行する
2. `cache_creation_input_tokens`と`cache_read_input_tokens`を比較する
3. cache\_creationがcache\_readより一貫して高い場合、膨張の影響を受けている可能性が高い

```
Session cost:
  Input tokens:          12,345
  Cache creation:        69,922  ← ここが異常に高い
  Cache read:            45,000
  Output tokens:          8,000
```

## 一時的な回避策

最も効果的な回避策は、v2.1.98にバージョンを固定すること。

```
npm i -g @anthropic-ai/claude-code@2.1.98
```

v2.1.98は膨張が報告される前の最後のバージョンで、同一ペイロードでcache\_creationが正常値（約50K）を示す。

### 注意点

* バージョン固定はセキュリティパッチも固定するため、長期的な解決策ではない
* Anthropicが修正をリリースしたら、速やかにアップデートすること
* API直接利用の場合は影響を受けない（Claude Codeのラッパー層の問題）

## hookによる監視

バージョンに関係なく、トークン消費を監視するhookを設定できる。

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": {},
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/token-monitor.sh"
        }]
      }
    ]
  }
}
```

セッション内のトークン消費をログに記録し、異常な膨張を検知したら警告を出す設計。具体的な実装はcc-safe-setupの[token-budget-guard](https://github.com/yurukusa/cc-safe-setup)を参照。

## 背景: トークン消費問題の全体像

cache\_creation膨張は、Claude Codeのトークン消費問題の一つに過ぎない。

* [#42796](https://github.com/anthropics/claude-code/issues/42796)（2,600+リアクション）: 全体的なトークン消費の異常
* [#46829](https://github.com/anthropics/claude-code/issues/46829)（258リアクション）: キャッシュTTLが1時間→5分にサイレント変更
* [#47528](https://github.com/anthropics/claude-code/issues/47528): システムプロンプトキャッシュが94%増加（v2.1.98→v2.1.104で49.7K→96.5K）。[診断と回避策](https://gist.github.com/yurukusa/d30c07294bc15f698df058664bd4c344)
* [#45756](https://github.com/anthropics/claude-code/issues/45756)（102リアクション）: Pro Max 5xが1.5時間で枯渇

キャッシュ問題の詳細な計測データは[ArkNillの分析リポジトリ](https://github.com/ArkNill/claude-code-hidden-problem-analysis)、`--resume`時のキャッシュ修復は[cnighswongerのcache-fix](https://github.com/cnighswonger/claude-code-cache-fix)が参考になる。

トークン消費を半分にする体系的な方法は、CLAUDE.md最適化・コンテキスト管理・hookによるガード・ワークフロー設計の4つを組み合わせる必要がある。

---

---

**📖 トークン消費に困っているなら** → [Claude Codeのトークン消費を半分にする——800時間の運用データから見つけた実践テクニック](https://zenn.dev/yurukusa/books/token-savings-guide?utm_source=qiita-c0acc6da&utm_medium=article&utm_campaign=token-book)（¥2,500・はじめに+第1章 無料）

---

**関連記事**: [Claude Codeのトークン消費を減らす5つの方法——Opus 4.7対応](https://qiita.com/yurukusa/items/435810e1e8a046c99916)  
:::note info  
**📖 AIで事業を回す実体験を全記録** → [Claude Code×個人事業 800時間の全記録](https://zenn.dev/yurukusa/books/3c3c3baee85f0a19?utm_source=qiita-c0acc6da&utm_medium=article&utm_campaign=book3)（¥800・第2章まで無料）。hookの裏にある800時間の実体験——赤字$572からの回収記録。  
:::

---

**⚠️ CVE-2026-21852（2026年4月公開）**: プロジェクト内`.claude/settings.json`経由でAPIキー窃盗。対策: `npx cc-safe-setup`（ユーザーレベル設定で免疫）→ [詳細](https://yurukusa.github.io/cc-safe-setup/opus-47-survival-guide.html#cve-settings-exfil)
