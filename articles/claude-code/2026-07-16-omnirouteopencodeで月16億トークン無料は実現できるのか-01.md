---
id: "2026-07-16-omnirouteopencodeで月16億トークン無料は実現できるのか-01"
title: "OmniRoute+OpenCodeで月16億トークン無料は実現できるのか"
url: "https://zenn.dev/mskbhd/articles/lab-127-omniroot-free-claude-code16"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "Gemini", "GPT", "zenn"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

X(旧Twitter)でこんな投稿が話題になっていました:

> You can run Claude Code on 1.6 billion free tokens a month.  
> Two open source projects make it work: free Claude Code + Omniroot.  
> Plug them together and you get the same Claude Code harness with a free brain inside.

「Claude Code を月16億トークン無料で動かせる」──本当なのか？ 実際に検証してみました。

## 「16億トークン」の内訳

まず結論から: **数字自体は誇大広告ではありません。** ただし現実的な使い方にはいくつかハードルがあります。

OmniRouteのドキュメント（FREE\_TIERS.md）を精査したところ、この数字の内訳は以下の通りです:

| カテゴリ | トークン数/月 | 備考 |
| --- | --- | --- |
| 定期無料枠（合計） | 約15.4億 | 文書化された無料枠のプール |
| + 初月限定クレジット | 約21.5億 | 新規登録ボーナス含む |
| キャップ無し永久無料枠 | 定量化不可 | siliconflow, GLM-4-Flash など |
| 圧縮による節約 | 15-95%削減 | RTK + Caveman |

最大の無料枠は **Mistral（約10億トークン/月）** で、他に Groq（1.17億）、 Gemini Flash系（6000万）、Cerebras（3000万）、Cloudflare AI（3000万）などが続きます。

2026年6月の再調査で「正直補正（honesty correction）」が入り、以前の約19.4億から下方修正されたことにも注目。乱高下する無料枠を正直に追跡している姿勢は好印象です。

## 検証: OmniRouteを実際にセットアップ

### インストール

```
npm install omniroute
# → v3.8.48, 739MB, インストール成功
```

### サーバー起動

```
omniroute serve --daemon --port 20128
# → 起動成功！ ダッシュボード: http://localhost:20128
#   API: http://localhost:20128/v1 (OpenAI互換)
```

### モデル一覧

APIを叩くと **445モデル** が確認できました:

* Claude系: 61モデル
* GPT系: 54モデル
* DeepSeek系: 43モデル
* Gemini系: 34モデル
* Groq, Mistral, Cerebras など

OpenAI互換のエンドポイントとして動作しているので、curlやOpenAI SDKから普通に呼べます。

### API呼び出しは通らなかった

ただし、無料モデルを実際に呼び出すには**各プロバイダの認証情報（APIキー or OAuth）をOmniRouteに登録する**必要があります。

```
curl http://localhost:20128/v1/chat/completions \
  -d '{"model":"gh/goldeneye-free-auto","messages":[{"role":"user","content":"hi"}]}'
# → {"error":{"message":"No active credentials for provider: github"}}
```

これはダッシュボードから設定するか、CLIで追加できます:

```
omniroute nodes add --provider openai --base-url https://api.openai.com/v1 \
  --auth-header "Authorization=Bearer sk-xxx"
```

## 検証: OpenCode（free Claude Code）

「free Claude Code」の実体として使われるのは OpenCode です。これは既にbrewでインストール済みでした（v1.17.10）。

```
opencode --version  # → 1.17.10
```

OpenCodeには **Zen** という無料プロバイダがありますが、実際にはAPIキーの取得（アカウント登録）が必要で、完全に「キーレス」ではありません。また、OpenCode自体は環境変数（OPENAI\_API\_KEY, GROQ\_API\_KEY等）を認識するため、お持ちのAPIキーをそのまま使えます。

## わかったこと・ハマったこと

### できたこと ✅

* OmniRouteのインストール・サーバー起動 → 問題なし
* 445モデルの確認
* サーバーの正常動作確認（HealthCheck, Batch, LiveWS等の全サービス起動）
* トークン試算の裏取り

### できなかったこと ❌

* 実際のAPI呼び出し成功まで至らず → ダッシュボードログイン or CLIでの認証情報設定が必要
* OpenCode Zen の無料モデル実行
* OmniRoute + OpenCode の組み合わせ動作確認

### ハマりポイント

* ダッシュボードの初期パスワード"CHANGEME"がログインできず（未解決）
* `opencode-zen` が古いバージョンのOpenCodeでは認識されない
* npmパッケージのサイズが739MBと巨大（インストールに時間がかかる）

## 総評: 16億トークン無料は「現実的か」

### 技術的には可能

OmniRouteはよくできたプロダクトです。インストールから起動までスムーズで、OpenAI互換APIとして動作します。無料枠のドキュメントも詳細で信頼性があります。

### ただし「タダ」ではない

* 最初に**複数のプロバイダに個別のアカウント登録**が必要
* 各プロバイダで**APIキーまたはOAuth認証**の設定が必要
* 無料枠は**頻繁に変わる**（2026年6月だけで10以上のプロバイダで変動）
* 多くの無料枠には**レート制限**がある（Groq: 30RPMなど）
* キャップ無しの永久無料枠も存在するが、**定量化できない**

### こんな人におすすめ

* 普段から複数のAI APIを使い分けている人
* 無料枠をかき集めてコストをゼロにしたい人
* 自動フェイルオーバーやルーティング戦略を試したい人

### こんな人には向かない

* 「インストールしたらすぐ使える」を期待する人
* 単一のプロバイダで済ませたい人
* 月に数万トークンしか使わない人（むしろ設定の手間が勝る）

## まとめ

「OmniRoute + OpenCodeで月16億トークン無料」は**技術的に実現可能な数字**であり、誇大広告ではありません。ただし、実際にその恩恵を受けるには相応のセットアップと運用の手間がかかります。

もしあなたが「複数の無料APIキーを管理してでもコストを削減したい」というタイプなら、OmniRouteは強力なツールになるでしょう。月に数回のセットアップで、数千円〜数万円のAPI費用をゼロにできる可能性があります。

一方で「とりあえずコードを書かせたい」なら、素直に1つのプロバイダで有料課金したほうが楽かもしれません。

---

**検証環境**: Mac mini (Apple Silicon) / Node.js v26.4.0 / OmniRoute v3.8.48 / OpenCode 1.17.10
