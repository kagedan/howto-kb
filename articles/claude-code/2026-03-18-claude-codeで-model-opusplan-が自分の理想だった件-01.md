---
id: "2026-03-18-claude-codeで-model-opusplan-が自分の理想だった件-01"
title: "Claude Codeで `/model opusplan` が自分の理想だった件"
url: "https://zenn.dev/takibilab/articles/claude-code-model-opusplan"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

## はじめに

Claude Codeには `/model` コマンドがあり、使用するモデルを切り替えられます。

以下のツイートを見て試してみたところ、これが自分の理想にドンピシャでした。

## `/model opusplan` とは

![スクリーンショット](https://static.zenn.studio/user-upload/deployed-images/4a3e3e9df6dd6c9b0e9ef538.png?sha=708c61fcb6118dfa45873bf716aa013c48e27d63)

コマンドを入力すると、こんなメッセージが表示されます。

```
Set model to Opus 4.6 in plan mode, else Sonnet 4.6
```

つまり：

* **プランモード（`/plan` や EnterPlanMode）のとき → Opus 4.6 を使用**
* **それ以外の通常の作業 → Sonnet 4.6 を使用**

## なぜこれが理想なのか

### Opus と Sonnet の使い分け

| モデル | 特徴 | 向いている用途 |
| --- | --- | --- |
| Claude Opus 4.6 | 高精度・深い推論 | 設計・計画・複雑な問題解決 |
| Claude Sonnet 4.6 | 高速・コスト効率 | コーディング・リファクタ・一般的なタスク |

日常的なコーディング作業は Sonnet で十分こなせます。しかし、設計や実装方針を決める「計画フェーズ」は、より深く考えられる Opus に任せたい。

でも毎回手動でモデルを切り替えるのは面倒です。

### `opusplan` はこの問題を解決する

`/model opusplan` を設定しておくと、**プランモードに入ったときだけ自動的に Opus 4.6 に切り替わり、抜けたら Sonnet 4.6 に戻ります。**

「考えるときは賢く、作業するときは速く」が自動で実現されます。

## 実際の使い方

### 設定方法

Claude Code を起動して、以下のコマンドを入力するだけです。

### プランモードとの組み合わせ

設定後は通常通り作業できます。何か大きな実装に取り掛かる前に `/plan` コマンドを使うと、その間だけ Opus 4.6 が動きます。

```
# 通常作業（Sonnet 4.6）
> このファイルのバグを直して

# プランモード（Opus 4.6 が起動）
/plan
> 認証機能をリファクタリングしたい。現状の問題点と改善案を考えて

# プランモードを抜ける（Sonnet 4.6 に戻る）
> 計画通りに実装して
```

---

## あわせて読む

## まとめ

`/model opusplan` は、コストと品質のバランスを自動で最適化してくれる設定です。

* 重要な設計・計画 → Opus 4.6 の深い推論
* 日常的なコーディング → Sonnet 4.6 の高速処理

「常に最強モデルを使いたいけどコストが…」という悩みを持つ方には、ぜひ試してほしい設定です。
