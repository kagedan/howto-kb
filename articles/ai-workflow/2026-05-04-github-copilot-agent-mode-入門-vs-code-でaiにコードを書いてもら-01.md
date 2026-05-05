---
id: "2026-05-04-github-copilot-agent-mode-入門-vs-code-でaiにコードを書いてもら-01"
title: "GitHub Copilot Agent Mode 入門: VS Code でAIにコードを書いてもらおう"
url: "https://zenn.dev/sawa_shin/articles/github-copilot-agent-mode-guide"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

GitHub Copilot の補完やチャットは使っているけれど、Agent Mode はまだ仕事の流れに入れられていない——。  
この記事は、そんな方に向けて **VS Code で GitHub Copilot の Agent Mode を使い始める最初の一歩** を案内するガイドです。

この記事の前提

* 2026-04 時点の GitHub Docs・VS Code Docs を前提にしています
* UI やメニュー名は更新で変わることがあります
* この記事は **わかりやすさを優先** しています。厳密な定義や用語の違いが気になる方は、本文中にリンクしている公式ドキュメントもあわせて確認してください

## この記事で得られること

この記事を読み終えると、次のことができるようになります。

1. VS Code に **GitHub Copilot をセットアップ** して Agent Mode を使える状態にする
2. Agent Mode に**仕事を頼んでみて、どう動くか**を自分の目で確かめる
3. 「まず使ってみる」から、次回の instructions へつなぐ流れを理解する

---

## Agent Mode ってなに？

ざっくり言うと、**VS Code の中で AI がコードを読み、書き、コマンドを実行し、複数ファイルにまたがる作業をまとめて進めてくれる機能**です。

従来のコード補完やチャットとの違いは、Agent Mode では AI が **自分で計画を立て、ファイルを探索し、編集し、ターミナルでコマンドを実行する** ところまで自律的に動く点です。

> 📖 Agent Mode の詳しい仕組みについては公式ドキュメントを確認してみてください。  
> [VS Code Docs: Agents overview](https://docs.github.com/en/copilot/get-started/quickstart?tool=vscode)

この連載では「VS Code 上で Agent Mode を使う」ことにフォーカスします。たくさんの関連機能もありますが、まずは **VS Code だけで完結する体験** から始めましょう。

![Agent Mode が VS Code の中で依頼から作業結果までをつなぐイメージ](https://static.zenn.studio/user-upload/deployed-images/283a69ad59530569bb0b07a0.png?sha=0e0f032ef58a6fb331bb18b0f697f520e55e27ee)

---

## VS Code に GitHub Copilot をセットアップしよう

![Agent Mode を使い始めるまでのセットアップ手順を道筋で表したイメージ](https://static.zenn.studio/user-upload/deployed-images/f1fb775a99bc17ba6af4c8fc.png?sha=7ee415aa034ba6d94b1cf2c90df734bf1f37be51)

### Step 1: VS Code を最新バージョンにする

すでにインストール済みの方は、最新版にアップグレードしましょう。

**Windows（winget）:**

```
winget upgrade Microsoft.VisualStudioCode
```

**macOS（Homebrew）:**

```
brew upgrade --cask visual-studio-code
```

まだインストールしていない方は、`winget install Microsoft.VisualStudioCode` や `brew install --cask visual-studio-code` で新規インストールするか、VS Code 公式サイトからダウンロードしてください。

> 📖 公式ドキュメントでも、最新の stable な IDE と拡張機能の利用が推奨されています。  
> [Copilot customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)

### Step 2: GitHub Copilot 拡張機能をインストールする

VS Code を開いたら、**GitHub Copilot Chat** 拡張機能をインストールします。

1. VS Code の拡張機能タブ（サイドバーの四角いアイコン）を開く
2. 検索欄に `GitHub Copilot` と入力
3. **GitHub Copilot** をインストールする（Chat 機能も含まれます）

> 📖 [GitHub Docs: Quickstart for GitHub Copilot](https://docs.github.com/en/copilot/get-started/quickstart)

### Step 3: GitHub にサインインする

拡張機能をインストールすると、GitHub アカウントでのサインインを求められます。サインインすると、Copilot が使える状態になります。

---

## Agent Mode を使ってみよう

セットアップが完了したら、さっそく使ってみましょう。

### チャットパネルを開く

VS Code の上部バーにある チャット / Copilot アイコンをクリックするか、以下のショートカットでチャットパネルを開きます。

* **macOS:** `Ctrl + Cmd + I`
* **Windows / Linux:** `Ctrl + Alt + I`

### Agent Mode に切り替える

チャットパネル下部のドロップダウンで **Agent** を選択します（VS Code のバージョンによっては、デフォルトで Agent Mode になっている場合もあります）。

### 最初の依頼を出してみる

たとえば、空のフォルダを VS Code で開いて、こんな依頼を出してみてください。

```
GitHub Copilot の Agent Mode について整理した README.md を
新規に作成してください。「Agent Mode とは何か」「何ができるか」
「始め方」の 3 セクション構成でお願いします。
```

Agent Mode がファイルを新規作成し、内容を考え、書いてくれるはずです。VS Code の差分ビューで生成されたファイルを確認し、`Accept` で変更を受け入れるか、内容を見て判断してください。

---

## Agent Mode に何を任せられる？

Agent Mode は、想像以上に広い範囲の仕事を引き受けてくれます。

* 複数ファイルにまたがるコード生成や修正
* バグの原因調査と修正案の作成
* テストコードの生成
* ドキュメントの整理
* リファクタリング
* コマンドの実行と結果の確認

**大きな仕事を任せてもOK** です。むしろ、Agent Mode の強みは「大きな仕事を依頼し、レビューを繰り返すことで、統一感のある成果物を AI のスピードで仕上げられる」ところにあると考えています。

ただし、Agent Mode を理解し始める段階では、**小さな依頼から始めて、AI がどう動くかを観察する**のが効果的です。動き方の癖が見えてくると、もっと大きな仕事を任せるときにも安心感が持てるようになります。

---

## まだ自分が強く持つべき判断は？

Agent Mode を積極的に使っていく中でも、次の判断は**まだ人間が持っておいた方が安全**です。

* **どこまで変更してよいか**という範囲の設定
* **完了条件**と確認のポイント
* **実行してよいコマンド**の判断
* 公開物や本番影響のある変更の**最終判断**

![AI が作った変更を受け入れる前に人間が差分を確認するイメージ](https://static.zenn.studio/user-upload/deployed-images/998dbabc3156144f477ef8a6.png?sha=48cf4ba2134397edc2c4ddf84d794998faf7c168)

Agent Mode は VS Code 上で差分（diff）を表示してくれるので、**変更内容は必ず差分ビューでレビュー**してから受け入れましょう。大きな依頼ほど変更範囲が広くなるため、レビューも相応に丁寧に行う必要があります。

---

## 次回：毎回の指示が面倒になってきたら？

Agent Mode を何度か使っていると、こんなことを毎回書くことが増えてきます。

* 「**日本語**で出力して」
* 「**事実と推論を分けて**書いて」
* 「**計画 → 実施 → 検証**の順番で動いて」
* 「最後に実行方法を**短く**説明して」

毎回これを書くのは面倒ですよね。この **「毎回繰り返し書いている前提」を一度だけ書いておけば自動で反映してくれる仕組み** が、次回紹介する **instructions** です。

第 2 回では、instructions を使って Agent Mode の回答がどう変わるかを実際に見ていきます。
