---
id: "2026-05-04-github-copilot-instructions-入門-毎回の指示を減らして回答精度を上げる-01"
title: "GitHub Copilot instructions 入門: 毎回の指示を減らして回答精度を上げる"
url: "https://zenn.dev/sawa_shin/articles/github-copilot-instructions-guide"
source: "zenn"
category: "claude-code"
tags: ["MCP", "AI-agent", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

第 1 回で Agent Mode を使ってみて、「毎回同じことを書いているな」と感じませんでしたか？ たとえば「日本語で」「余計なライブラリは追加しないで」「計画してから動いて」——  
こうした前提を、**一度書いておけば自動で反映してくれる仕組み** が instructions です。

この記事の前提

* 2026-04 時点の GitHub Docs と VS Code Docs を根拠にしています
* 主役は instructions のみです。AGENTS.md、prompt files、hooks、MCP はいったん脇に置きます
* VS Code の Agent Mode を利用する前提で書いています

## この記事で得られること

1. 第 1 回の次に **instructions を足す理由**
2. **repo instructions と path instructions** の使い分け
3. instructions の有無で **Agent Mode の動きがどう変わるか** の具体例

---

## なぜ instructions が必要なの？

第 1 回で Agent Mode を試してみると、こんなことを毎回チャットに書いていたはずです。

* 「**日本語**で出力して」
* 「事実と推論は**分けて**書いて」
* 「**計画 → 実施 → 検証**の順番で動いて」
* 「最後に実行方法を**短く**説明して」

これを毎回書くのは面倒ですよね。instructions はこの問題を解決します。**プロジェクトのルートに置いておくだけで、Agent Mode が毎回その前提を踏まえて動いてくれる**ようになります。

![毎回チャットで伝えていた指示を1枚のルールにまとめるイメージ](https://static.zenn.studio/user-upload/deployed-images/ca98308e349429cb395ff3b0.png?sha=ea889cbd623f5207fb26a7f1517ae2ccf24408fb)

---

## repo instructions と path instructions はどう違う？

VS Code では、2 種類の instructions を使い分けられます。

### repo instructions — プロジェクト全体のガイド

* ファイル: `.github/copilot-instructions.md`
* Agent Mode 利用時に**常に読み込まれる**
* 「このプロジェクトで毎回言いたいこと」を書く

> 一言でまとめると: **プロジェクト全体に効かせる 憲法 的な存在**

### path instructions — 特定ファイル向けのルール

* ファイル: `.github/instructions/*.instructions.md`
* `applyTo` で対象パターンを指定すると、**そのファイルに触れるときだけ**自動適用される
* 「README だけ」「テストだけ」のように、一部のファイルだけに寄せたいルール向け

> 一言でまとめると: **特定のファイルに絞って効かせるピンポイントルール**

> 📖 公式ドキュメントでも、この 2 種類の使い分けが説明されています。  
> [Copilot customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)

最初から全部を path instructions に分ける必要はありません。**先に repo instructions を 1 枚置き、足りない差分だけを path instructions に分ける** と分かりやすいです。

![リポジトリ全体に効くルールと特定ファイルだけに効くルールを分けるイメージ](https://static.zenn.studio/user-upload/deployed-images/5ed6ca8a53ebf44c3e19b7ea.png?sha=3c0d5c2004d915e7851e0bdfa75cb26102ac929b)

---

## instructions を書いてみよう

### ディレクトリ構成

```
your-project/
├── .github/
│   ├── copilot-instructions.md          ← repo instructions
│   └── instructions/
│       └── readme.instructions.md       ← path instructions (README向け)
├── src/
│   └── ...
└── README.md
```

### Step 1: repo instructions を書く

`.github/copilot-instructions.md` に、毎回伝えている前提をまとめます。

```
# プロジェクト共通ルール

- 日本語で回答すること。
- 事実と推論は明確に分けて書くこと。
- 計画 → 実施 → 検証 の順で作業を進めること。
- 変更後は、作成・変更したファイルと実行方法を短く説明すること。
```

### Step 2: README 向けの path instructions を追加する

`.github/instructions/readme.instructions.md`:

```
---
applyTo: "README.md"
---

# README 向けルール

- セットアップ手順は短く、コピペで実行できる形にすること。
- コマンド例は実際に生成されたファイルと一致させること。
```

### Step 3: 依頼を出す

instructions を置いたら、Agent Mode でいつも通り依頼するだけでOKです。「日本語で」「最小構成で」と書かなくても、instructions が自動で反映されます。

```
この空ディレクトリに、GitHub Copilot Agent Mode の使い方を整理した
README.md を作ってください。初めて使う人向けに、概要、できること、
始め方、注意点の順でまとめてください。
```

---

## instructions があると何が変わる？

instructions の有無で、Agent Mode の動きには具体的な違いが出ます。ここでは私の手元で確認できた変化を紹介します。

### Before（instructions なし）

Agent Mode に「Agent Mode の使い方を整理した README.md を作って」と頼むと：

* 回答が**英語**で返ってくることがある
* 事実と推論が**混在**した説明になりやすい
* README が長くなりがち
* 作業の進め方が毎回バラバラ

### After（instructions あり）

まったく同じ依頼でも：

* 回答が**日本語**で統一される
* 「これは事実」「これは推論」のように**区別して**説明してくれやすくなる
* README が実行手順中心の**短いもの**になりやすい
* 計画 → 実施 → 検証 の**順序を意識した**進め方になる

つまり instructions は、**「毎回言うこと」を事前に渡しておくことで、Agent Mode の動きを自分の期待に近づける仕組み** です。逐一チャットで指示しなくても、前提が揃った状態で仕事を進めてくれる——これが一番のメリットです。

---

## 書きすぎると逆効果になるポイント

instructions は長いほど強いわけではありません。公式ドキュメントでも「短く自己完結した文」が効果的だと案内されています。

![短く整理された instructions と詰め込みすぎた instructions を比べるイメージ](https://static.zenn.studio/user-upload/deployed-images/e571092fedd05d7e7cee59bc.png?sha=271b0966575c99930c4970e08eada2531c87edf9)

> Custom instructions consist of natural language instructions and are **most effective when they are short, self-contained statements**. Consider the scope over which you want the instruction to apply when choosing whether to add an instruction on the personal, repository, or organization level.  
> — [About customizing GitHub Copilot responses](https://docs.github.com/en/copilot/concepts/prompting/response-customization)

また、[公式チュートリアル](https://docs.github.com/en/copilot/tutorials/customize-code-review)では、**以下のような instructions は効果がない**と明示されています。

* **曖昧な品質指示**: 「もっと正確にして」「問題を見逃さないで」「一貫したフィードバックを」  
  → Copilot はすでにそうするよう最適化されており、ノイズになるだけ
* **長すぎる instructions**: 1,000 行を超えると品質が低下する可能性がある  
  → 最初は 10〜20 項目から始めて、効果を見ながら追加する

さらに、**repo / path を分けずに 1 ファイルに混ぜる**のも避けた方がよいです。  
path-specific instructions を使うことで、特定のファイルにだけ効かせるルールを分離し、repo-wide instructions の肥大化を防ぐことを目指しましょう。

---

## まとめ

instructions を足す理由は、Agent Mode を万能化するためではなく、**毎回の前提説明を減らして、Agent Mode の動きを自分の期待に近づけるため**です。

手順をおさらいすると：

1. まずは `.github/copilot-instructions.md` で「毎回言っていること」をまとめる
2. 必要になったら `.github/instructions/*.instructions.md` で一部のファイルだけにルールを追加する
3. 依頼を出して、instructions の有無で動きが変わるかを確認する

---

!

➡️ **次回: custom agents と Agent Skills で役割を分ける**

instructions でプロジェクト全体のルールは整いました。でも使い込んでいくと、「品質チェックに特化した agent がほしい」「レビュー専門の agent と実装 agent を分けたい」と感じるようになるかもしれません。第 3 回では、custom agents と Agent Skills を使って Agent Mode に**役割と武器**を持たせる方法を見ていきます。

👉 [第3回: GitHub Copilot custom agents と Agent Skills 入門](https://zenn.dev/sawa_shin/articles/github-copilot-subagents-skills-guide)
