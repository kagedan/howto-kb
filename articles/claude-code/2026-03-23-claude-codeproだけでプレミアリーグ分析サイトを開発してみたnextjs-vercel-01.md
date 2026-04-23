---
id: "2026-03-23-claude-codeproだけでプレミアリーグ分析サイトを開発してみたnextjs-vercel-01"
title: "Claude Code（Pro）だけでプレミアリーグ分析サイトを開発してみた【Next.js / Vercel】"
url: "https://zenn.dev/zosuka/articles/663d76933ac0d3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

## はじめに

Claude Proで何かサイトを作りたくて、趣味であるプレミアリーグを題材に、  
データを可視化するサイトを作成しました。

特徴的なのは**ほぼすべての実装をClaude Proに依頼して開発した**点です。

トークン節約のため、ところどころ手修正を行いましたが、  
体感9割5分はエージェントに任せて開発しました。

現時点で週間制限を1.5週分くらい消費して開発しました。  
それでこの程度？と思うか、それでこんなに！と思うかは人それぞれだと思いますが、  
一見していただけると嬉しいです。

<https://www.premiernow.jp/>

![](https://static.zenn.studio/user-upload/590e99a88a1b-20260321.png)

---

## 作ったもの

* 順位表・試合結果・得点王
* xG分析（Understatスクレイピング）
* ホームvsアウェイ成績比較
* 優勝争い・降格争いレースチャート
* 順位予測シミュレーター
* 選手スタッツページ
* マッチプレビュー記事
* クイズ機能

それ以外にもUI向上のため以下の機能を実装しています

* ダークモード機能
* 画面遷移時のインジケータ機能
* ツールチップによる説明追加

---

## 技術スタック

* Next.js 15 (App Router)
* TypeScript
* Tailwind CSS
* Vercel（無料プラン）
* football-data.org API（無料プラン）
* Understat（xGデータ・スクレイピング）
* **Claude Pro（実装の中心）**

---

## ClaudeをどうAIに使ったか

### 基本的なやり方

「〇〇ページを実装してください」という形で  
機能単位でプロンプトを投げていました。

Claudeはコードを書くだけでなく、こちらが気づいていないエッジケースや  
パフォーマンス上の問題も指摘してくれるのでレビュアーとしても優秀でした。

### 具体的なプロンプト例

例えばxG分析ページの実装では、以下のように仕様を箇条書きで渡すとほぼそのまま動くコードを返してくれます。

```
Understatからxgデータを取得して
/charts/xg ページを実装してください。

## 取得するデータ
- チーム別 xG・xGA
- 選手別 xG・xA
...
```

また既存の画面を修正するときは以下のように何を改善するのか、  
どう修正するのかを明確に伝えました。

```
- クラブページを改善します。
  - 順位と順位表へのリンクをエンブレムの下に表示してください。
  - 監督とスタジアムの場所は今のままでよいですが、スタジアム名は折り返さないようにしてください
```

---

## 工夫したポイント

### ISRキャッシュ設計

無料APIの月1000リクエスト制限内に収めるため  
ページごとにrevalidateを調整しました。

```
// 順位表: 1時間
export const revalidate = 3600

// 試合結果: 30分
export const revalidate = 1800

// 得点王: 6時間
export const revalidate = 21600
```

### UnderstatでxGデータを取得

football-data.orgの無料プランにxGは含まれないため  
UnderstatのHTMLに埋め込まれたJSONを抽出しています。

```
function extractJson(html: string, varName: string): string {
  const regex = new RegExp(
    `${varName}\\s*=\\s*JSON\\.parse\\('(.*?)'\\)`
  )
  const match = html.match(regex)
  if (!match) throw new Error(`${varName} not found`)
  return decodeURIComponent(
    match[1].replace(/\\x([0-9A-Fa-f]{2})/g, '%$1')
  )
}
```

### Claudeとの開発で気をつけたこと

---

## ハマったところ

**Understatのエンコーディング問題**  
HTMLに埋め込まれたJSONが  
`\x`形式でエスケープされていて  
そのままparseできませんでした。

**ISRとuse clientの共存**  
データ取得をサーバー側・インタラクションをクライアント側と  
明確に分離する設計が必要でした。

**試合カードの中央寄せ**  
チーム名の長さが違うと  
スコアがずれる問題に地味に手こずりました。  
固定幅のflexboxで解決。

---

## Claudeを使った開発の所感

正直、1週目は週間制限をほぼ意識せずに使っていたため、制限に引っ掛かりました。  
面倒くさがりな性格なのでClaudeへの指示も曖昧だったため、  
トークンの使用量も増えていたように思います。

2週目からは定期的にチャットを切り替えるのと、具体的に指示をすることを心掛けて作業しました。  
トークンの使用量が減ったかは不明ですが。。

総じて**個人開発との相性は抜群**だと感じています。  
デザイン・実装・SEO・ビジネス戦略まで  
一人の壁打ち相手として使い倒せます。

---

## まとめ

PLファンでエンジニアの方、  
またはClaude×個人開発に興味がある方に  
参考になれば嬉しいです。

サイト: <https://www.premiernow.jp/>  
X: @PremierNow\_
