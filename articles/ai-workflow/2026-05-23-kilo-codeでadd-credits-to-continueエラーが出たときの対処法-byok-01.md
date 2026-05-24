---
id: "2026-05-23-kilo-codeでadd-credits-to-continueエラーが出たときの対処法-byok-01"
title: "Kilo Codeで「Add credits to continue」エラーが出たときの対処法 — BYOK運用のすゝめ"
url: "https://zenn.dev/hiroakikody/articles/5fd2979470c2b7"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "OpenAI", "zenn"]
date_published: "2026-05-23"
date_collected: "2026-05-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

kilo codeのエラーを検索すると、[自分のブログポスト](https://zenn.dev/hiroakikody/articles/d62916769f8d23)がAIの回答のソースとなっていました。  
「自分でエラーにハマって抜け出した経験は、ブログに書くべきだ！」  
と過去の自分に感謝をしつつ、今回のkilo codeで急に発生したエラーの対処方法もブログとして記録しておこうと記しました。

## 起：突然のエラーに見舞われる

2026年5月、いつものようにKilo Codeでコーディングしていたところ、突然こんなエラーが出た。  
Add credits to continue, or switch to a free model

現在の私のkilo codeの運用方法は以下の通りです。

> BYOK（自前のキー）とサブスクのハイブリッド運用  
> ここでKilo Codeの「賢い」仕組みを理解しました。
>
> * BYOK (Bring Your Own Key): kilo.jsonc に自分のAPIキーを書けば、Kilo側に課金せずとも実費だけで動かせる。
> * Z.ai連携: Kiloアカウントでログインするだけで、Z.aiの強力なインフラをそのままゲートウェイとして利用できる。

Z.aiのクレジット残高を確認しても、週間制限にはまだ余裕がありました。  
まずはGoogle検索。しかしヒットしたのは過去の自分のブログ記事（アカウントの不一致について）ばかり。解決策が見つからない。

## 承：原因を探る — Kilo GatewayとBYOKは別物

途方に暮れて、**Kilo Codeの公式ドキュメントにエラーメッセージを貼り付けて質問**してみた。

すると、原因が判明した。このエラーは**Kilo Gateway（Kilo公式の従量課金プロバイダー）のクレジット切れ**である。

重要なのは、以下の2つが**別物**だということ：

| 項目 | 説明 |
| --- | --- |
| **Kilo Gateway** | Kilo Code内蔵のプロバイダー。500以上のモデルにアクセス可能だが、有料モデルはクレジットが必要 |
| **BYOK（Bring Your Own Key）** | 自分のAPIキーを使って外部プロバイダーに接続。Kilo Gatewayのクレジットとは無関係 |

私の環境では、`kilo.json`の`model`フィールドがKilo Gateway側のモデルを指していたため、BYOKで設定したはずのモデルとは別にKilo Gatewayのクレジットが消費されていた。

## 転：解決方法

公式ドキュメントの回答は2つのオプションを提示していた。

### Option 1: クレジットを追加する

app.kilo.aiで$50〜$1000以上のクレジットを購入する。クレジットは全Kilo製品で共有され、有効期限はない。

### Option 2: 無料モデルまたはBYOKに切り替える

`/models`コマンドでモデルピッカーを開き、BYOKで設定したモデルを選択する。

私は**Option 2**を選択。チャット欄のモデルセレクターから、BYOKに指定している`zai-coding/glm-5.1`（Z.ai BYOK）を選んだところ、即座に解決した。

### 再発防止：設定ファイルの書き換え

しかし、プロジェクトを変えるたびに手動で切り替えるのは面倒だ。

調べた結果、Kilo Codeの設定は**階層的にマージ**されることがわかった：

| 優先度（低→高） | 場所 | 用途 |
| --- | --- | --- |
| 1 | `~/.config/kilo/kilo.json` | グローバル設定（全プロジェクト共通） |
| 2 | `./kilo.json` | プロジェクト固有設定 |

**BYOKのモデル設定はグローバル設定に書けば、全プロジェクトで共通**して使える。フォルダやリポジトリが変わるたびに再設定する必要はない。

### `disabled_providers`で誤使用を防ぐ

さらに、`disabled_providers: ["kilo"]` をグローバル設定に追加しておけば、**Kilo Gatewayがモデル選択肢から消え、誤ってクレジットを消費することがなくなる**。

```
{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "zai-coding/glm-5.1",
  "disabled_providers": ["kilo"]
}
```

* disabled\_providersとは、指定したプロバイダーを使用不可にする設定項目：
* Kilo内蔵プロバイダーがモデル選択肢に表示されなくなる
* Kiloのマネージドモデルやクレジットを使用できなくなる  
  その代わり、OpenAI、Anthropic、Ollamaなど他のプロバイダーを自分のAPIキーで（BYOK）利用することになる

## 結：BYOK運用が快適になった

最終的なグローバル設定（~/.config/kilo/kilo.json）はこうなった：

```
{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "zai-coding/glm-5.1",
  "instructions": ["AGENTS.md"],
  "permission": {
    "bash": "allow",
    "edit": { "src/**": "allow", "*": "ask" },
    "read": "allow"
  },
  "disabled_providers": ["kilo"]
}
```

この設定により：

* デフォルトモデルがBYOKに固定され、Kilo Gatewayのクレジット切れエラーが起きなくなった
* プロジェクトを切り替えても再設定不要
* Kilo Gatewayの誤使用を完全に防止  
  同じエラーに遭遇した方は、まず自分がどのプロバイダーを使っているか（Kilo GatewayかBYOKか）を確認し、グローバル設定でデフォルトモデルを明示的に指定することをおすすめする。
