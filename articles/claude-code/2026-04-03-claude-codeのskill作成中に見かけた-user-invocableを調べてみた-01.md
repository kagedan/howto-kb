---
id: "2026-04-03-claude-codeのskill作成中に見かけた-user-invocableを調べてみた-01"
title: "🔍Claude CodeのSkill作成中に見かけた user-invocableを調べてみた"
url: "https://zenn.dev/dely_jp/articles/76842757cce7b6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

こんにちは、クラシルiOSエンジニアのkeiです。

皆さん、Skillを作るときに生成されたSKILL.mdの中身をちゃんとチェックしていますか？ 私はほぼAIに任せきりで、「動いたからヨシ！」で済ませがちでした。

でも先日、たまたまヘッダー設定を眺めていたら知らない設定を見つけて、「これ何だろう」と調べたら意外と面白かったので共有します。

## きっかけ

クラシルのiOSアプリで、Applovin SDKの更新作業がありました。更新の手順やチェックリストがそこそこあるので、それをClaude CodeのSkillとしてまとめるPRを出していたときのことです。

SKILL.mdのヘッダー設定を書いていて、ふと目に入ったのが `user-invocable: true` という設定項目でした。

```
---
name: update-applovin
description: Applovin SDKの更新手順
user-invocable: true
---
```

「invocable...呼び出し可能？trueってことはfalseもあるの？どういう使い分け？」——気になったので調べてみました。

## user-invocableとは

Claude CodeのSkillには、SKILL.mdの先頭にYAMLのヘッダー設定で動作を制御する項目がいくつかあります。`user-invocable` はその一つで、**そのSkillをユーザーが `/スキル名` で直接呼び出せるかどうか**を制御します。

デフォルトは `true` です。つまり、何も書かなければスラッシュコマンドメニューに表示されて、ユーザーが自分で呼び出せます。

`false` にすると、スラッシュコマンドメニューには表示されなくなります。ただし**Claudeは自動的にそのSkillを読み込んで参照できます**。

## どんなときにfalseにするのか

公式ドキュメントの例がわかりやすいです。たとえば `legacy-system-context` というSkillがあるとします。レガシーシステムの仕様を説明した内容で、Claudeがコードを書くときの参考情報として使ってほしいものです。

でも、ユーザーが `/legacy-system-context` とタイプしてもあまり意味がありません。実行する「タスク」ではなく、あくまで「背景知識」だからです。こういうSkillは `user-invocable: false` にしておくと、メニューがスッキリします。

## もう一つの紛らわしい設定: disable-model-invocation

調べていて混乱したのが、似たような設定 `disable-model-invocation` の存在でした。

こちらは `true` にすると、**Claudeが自動的にSkillを呼び出すのを禁止します**。つまりユーザーが明示的に `/スキル名` で呼んだときだけ動きます。

整理するとこうなります:

| 設定 | ユーザーが呼べる | Claudeが呼べる |
| --- | --- | --- |
| デフォルト（両方なし） | ✅ | ✅ |
| `disable-model-invocation: true` | ✅ | ❌ |
| `user-invocable: false` | ❌ | ✅ |

`disable-model-invocation: true` は、デプロイやSlackへのメッセージ送信など**副作用があるSkill**に使います。Claudeが勝手に「コード良さそうだからデプロイしておきますね」となったら困りますので。

`user-invocable: false` は、先述のとおり**背景知識系のSkill**に使います。

名前が対称的じゃないのでちょっとわかりにくいですが、制御する方向が逆なのがポイントです。

## 今回の学び

今回のApplovin SDK更新Skillは、ユーザーが `/update-applovin` で呼ぶものなので `user-invocable: true` はそのまま。一方で、Claudeに勝手にSDK更新を走らせたくないので `disable-model-invocation: true` を追加しました。

最初は `user-invocable` が気になっただけでしたが、調べた結果 `disable-model-invocation` という自分のSkillに必要な設定も見つけられました。たまにはAI任せにせず、自分の目で中身を確認してみるものですね。

皆さんはSkillを作るとき、よくいじる設定や「これ入れとくと便利」みたいなものがあれば、ぜひコメントで教えてください。

## 参考
