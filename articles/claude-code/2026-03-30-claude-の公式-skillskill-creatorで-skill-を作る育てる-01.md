---
id: "2026-03-30-claude-の公式-skillskill-creatorで-skill-を作る育てる-01"
title: "Claude の公式 skill「skill-creator」で skill を作る・育てる"
url: "https://qiita.com/s-sakano/items/b8ec3acf55153a252d6e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-03-30"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

こんにちは！

この記事では、Claude の公式 skill「**skill-creator**」で skill を自分で作ったり直したりする方法を紹介します。  
伝えたいことは次の3つです。**skill とは何か**、**skill と MCP それぞれの役割は何か**、**skill-creator の入れ方と使い方**です。とくに Claude Code を触り始めたばかりの人や「skill って聞いたことはあるけど中身は知らない」という人がいましたら、最後まで読んでいただけると嬉しいです。

## skill って何？ どう使う？

**skill** は、Claude に「この仕事のときはこの手順を見て動いて」と渡す**指示のまとまり**です。`SKILL.md` というファイルに書いておくと、Claude がそれを参照して動きます。

呼び出し方は次の2つです。**手動**で **`/` を付けて** skill を読み込むか、**会話の内容に合わせて自動**で読み込まれるかです。手動で使う名前は `SKILL.md` の **`name`** に対応します。

---

ここまで読んで、**MCP（Model Context Protocol）** の名前を知っている人なら、**「skill と MCP はそれぞれどんな役割があるの？」** と思うかもしれません。

ただし、**同じ「拡張」でも、担っている役割は別物です。** 大雑把に言えば、skill は**エージェントに渡す手順・知識・ワークフロー**をファイルにまとめたもの、MCP は**AI アプリとデータソース・ツール等をつなぐためのオープンな接続規約**です。

MCP では別プロセスの **MCP サーバー**がツールやリソースを公開し、クライアント側の Claude がそれを呼び出します。Claude Code では両方を同時に使え、skill の本文に「必要なら MCP のツールで調べる」と書く、といった**併用**もよくあります。

## Skill と MCP それぞれの役割

さきほどの説明を、**役割・構成・動き** の 3 点に整理したのが次の表です。

| 観点 | Skill（Agent Skills） | MCP |
| --- | --- | --- |
| **目的** | 手順・知識・文脈をAIに伝える | 外部ツール・データソースに接続する |
| **構成** | フォルダ＋`SKILL.md` | サーバーが公開し、クライアントが接続 |
| **動き** | AIが読み込んで推論に活かす | AIが呼び出して結果を得る |

**「手順と文脈は skill、外との接続は MCP」** と思っておくのがよいです。

## skill のフォルダ構成と SKILL.md

1 つの skill は**1 つのフォルダ**で、中に `SKILL.md` と、必要ならサブフォルダを置きます。

```
skill名/
├── SKILL.md          # 必須。いつ使うか＋何をするか
├── scripts/          # 実行用スクリプト（任意）
├── references/       # 参照用ドキュメント（任意）
└── assets/           # テンプレートやアイコンなど（任意）
```

**SKILL.md** は、**`---` で囲んだ先頭（YAML frontmatter）と本文**の2つでできています。frontmatter には **`name`** と **`description`** を書きます。本文には、skill が呼ばれたあとに Claude が従う指示をマークダウンで書きます。

### SKILL.md の例

```
---
name: explain-code
description: コードを図やたとえで説明する。コードの動きを聞かれたとき、「どういう仕組み？」と聞かれたときに使う。
---

コードを説明するときは、次の4つを含める:

1. **たとえで始める**: 日常生活の何かに例えて説明する
2. **図を描く**: ASCII で流れや構造を示す
3. **コードをたどる**: 何が起きるかを順に説明する
4. **落とし穴を1つ**: よくある勘違いやミスを挙げる

説明は会話調で。
```

**`name`** は、その skill の**名前**です。上の例では `explain-code` になります。手動でスキルを呼び出す場合は **`/explain-code`** の形で呼び出せます。

**`description`** は、**どんな場面でこの skill を使ってほしいか**を書く欄です。会話の内容が、ここに書いた説明に合いそうだと判断されると、**自動で skill が動く**ようになります。ユーザーの言い方の例を具体的に書いておくと、狙ったタイミングで使われやすくなります。

## skill-creator とは・入れ方

**skill-creator** は、skill を**作る・直す・テストする・測る**ための公式 skill（プラグイン）です。

やりたいことに応じて **いくつかのモード**の中から選べます。

* **Create**: 意図の整理・ヒアリング、`SKILL.md` のドラフト、テストプロンプトの作成
* **Eval**: テストプロンプトでスキルあり／スキルなしを並列実行し、採点・集計・レビューで期待どおりか確認
* **Improve**: フィードバックと採点をもとに SKILL.md などを直し、Eval を再度実行
* **Benchmark**: Eval の採点結果を集約し、スキルありとスキルなしの合格率・時間・トークンなどを数値で比較

### 導入方法（Claude Code）（執筆時: v2.1.72）

1. Claude Code で **`/plugin`** を入力
2. **Discover** タブで「Skill Creator」または「anthropics/skills」を検索
3. インストール
4. **`/skill-creator`** が出れば完了

別方法として、`/plugin install skill-creator@claude-plugins-official` でもインストールできます（[Claude Code でのプラグイン発見・インストール](https://code.claude.com/docs/ja/discover-plugins)）。

## skill-creator でやることの流れ（イメージ）

`/skill-creator` を実行すると、**Create / Eval / Improve / Benchmark** のいずれかのモードで進められます。おおまかな流れは次のとおりです。

### 新規で作る場合

1. **Create**  
   意図の整理（何をするか・いつ使うか・出力形式）を対話で行います。skill-creator がヒアリングし、フォルダ構成・SKILL.md のドラフト・必要ならスクリプトまで作成してくれます。
2. **Eval**  
   「このプロンプトで skill を動かしたとき、期待どおりか」を確認するテスト（eval）を 2〜3 個つくり、実行します。評価には**出力品質**（期待した結果になっているか）と**トリガー精度**（適切なときに skill が選ばれるか）の両方を見ます。実行は独立したエージェントで並列に行われます。ユーザーはテスト結果をレビューし、フィードバックを渡します。
3. **Improve**  
   フィードバックに基づいて SKILL.md を修正します。複数バージョンを比較する Comparator、改善案を出す Analyzer といった専用サブエージェントも使用できます。
4. **Benchmark**  
   同じ eval を複数回実行し、成功率・所要時間・トークン使用量などを計測します。ばらつきも確認できるので、モデルや skill を変えたあとに「本当に良くなったか」を確かめるときに使います。

### 既存の skill を直す場合

上記の **Eval 以降**から入ります（eval 追加・実行 → Improve → benchmark で確認、の繰り返し）。

## まとめ

* **skill** = Claude が参照する手順のまとまりです。手動では **`SKILL.md` の `name`** に対応する **`/スキル名`** でskillを読み込みます。会話が frontmatter の **`description`** に合いそうなときは、**自動で読み込まれる**こともあります。**`/skill-creator`**
* **中身** = skill 用フォルダの **`SKILL.md`**（frontmatter ＋ 本文）が必須で、必要なら **`scripts/`**・**`references/`**・**`assets/`** を同梱します。
* **skill-creator** = その skill を「作る・直す・テストする・測る」ための公式プラグインです。**`/plugin`** の Discover タブからインストールし、**`/skill-creator`** で起動します。

この記事をみて興味を持った方は、ぜひ **skill-creator** で、自分用の skill を作ってみてください。

## 参考リンク
