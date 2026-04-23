---
id: "2026-04-09-mermaidの図作成画像化をclaude-code-skillで自動化する古家大-aiオペレーショ-01"
title: "mermaidの図作成・画像化をClaude Code Skillで自動化する｜古家大 | AIオペレーションマネージャー"
url: "https://note.com/masaru_furuya/n/n18ff1c4d6b8b"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-04-09"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

ブログ記事やObsidianノート、PRの説明、設計ドキュメントに「フローチャートを1枚挟みたい」と思うことはよくあります。そのたびにdraw.ioを立ち上げてポチポチやるのは面倒ですし、GUIで作った図は後から差分管理がしづらいです。

そこで、Mermaid記法をテキストで書いて、mmdc でPNG化するワークフローを回しています。テキストなのでGitで差分管理できますし、AIに「この内容で図にして」と頼めば .mmd ファイルを吐いてくれます。あとは1コマンドでPNGになります。

ただ、毎回AIに「Mermaidで縦フローで色分けして、横1600pxで書き出して…」と指示するのは面倒です。一度Claude Codeの Agent Skill として定義してしまえば、「この内容をフローチャートにして」と雑に頼むだけで全部やってくれます。この記事では、その仕組み化の手順をまとめます。

### 前提

- mmdc（@mermaid-js/mermaid-cli）がインストール済みであること  
  npm install -g @mermaid-js/mermaid-cli  
- Claude Code を使用していること（Agent Skill機能が前提）

### Agent Skill とは

Claude Code の Agent Skill は、.claude/skills/スキル名/SKILL.md に置いたマークダウンファイルで定義できる「再利用可能なワークフロー」です。description に書いたトリガーとなる文言や状況を Claude が検知すると、そのスキルのワークフローを自動で読み込んで実行してくれます。

ざっくり言えば、プロンプトのテンプレート＋手順書をスキルとして登録しておき、会話の文脈に応じて自動起動させる仕組みです。

### SKILL.md を書く

.claude/skills/mermaid-flowchart-generator/SKILL.md を作ります。

```
name: mermaid-flowchart-generatordescription: 
"note記事やドキュメントに貼るフローチャート画像を、Mermaid記法から自動生成する。
AIにMermaidのmarkdownを書かせて、mmdc（@mermaid-js/mermaid-cli）
でPNG画像化するまでを一気通貫で実行。
使用タイミング: 
(1) note記事やObsidianノートに貼るフロー図を作りたい時
(2) Claude Code hooksやアーキテクチャのライフサイクルを可視化したい時
(3) 対話でラフに図の要件を固めて即画像化したい時
トリガー: 「フローチャート作って」「フロー図」「mermaid画像化」「mmdc」「mermaid flowchart」

# Mermaid Flowchart Generator

## 概要
ユーザーから図にしたい内容を受け取り、Mermaid記法のフローチャートを生成 
→ mmdc でPNG画像化 → 指定ディレクトリに保存する。

## ワークフロー

### Phase 0: 要件確認
1. 図の目的を確認（note記事用 / Obsidian用 / PR用 など
2. 図にしたい内容を確認（既にテキストがあればそれを元にする）
3. 方向を確認（縦フロー=TD / 横フロー=LR）。デフォルトはTD
4. 長い日本語ラベルがある場合は brタグ で改行を入れて横幅を抑える

### Phase 1: 
Mermaid記法の生成

1. date +%Y%m%d で今日の日付を取得
2. /tmp/slug.mmd にMermaidコードを書き出す
3. 推奨スタイル: ノードを色分けして視認性を上げる
4. 分岐は {条件?}、終端は ([...])、処理は [...] を基本に使い分け

### Phase 2: PNG化
1. 出力先ディレクトリを作成
2. mmdcで画像生成:   mmdc -i /tmp/slug.mmd -o ./assets/flowcharts/YYYYMMDD_slug.png -b white -w 1600 -s 2

### Phase 3: 確認
1. 生成されたPNGを表示してユーザーに確認
2. 修正要望があれば .mmd を編集して再実行
3. FIXしたら保存先パスを提示
```

ポイントは3つあります。

### 1. description にトリガー語を羅列する

「フローチャート作って」「フロー図」「mermaid」などの自然な言い回しを並べておくと、Claudeが会話の中で「あ、これはこのスキルを使うべきだな」と判断してくれます。

### 2. ワークフローをフェーズ分けする

Phase 0（要件確認）→ Phase 1（生成）→ Phase 2（画像化）→ Phase 3（確認）と明確に区切ると、Claudeが途中で迷子になりません。特に Phase 0 の要件確認を明記しておくと、いきなり図を書き始めずにきちんと「縦？横？」と聞いてくれます。

### 3. 出力パスとコマンドを具体的に書く

mmdc -i ... -o ... -b white -w 1600 -s 2 のように具体的なコマンドを書いておけば、毎回安定した品質のPNGが出てきます。「横幅は1600pxがおすすめ」みたいな曖昧な指示だと、実行するたびにパラメータがブレてしまいます。

### スキルを実行する

SKILL.md を置いたら、あとはClaude Codeのセッション内で雑に頼むだけです。

ユーザー: Claude Code hooksのライフサイクルをフローチャートにして

Claude側の動きは次のようになります。

1. description のトリガーにマッチ → mermaid-flowchart-generator スキルを起動  
2. Phase 0: 「縦フローでいいですか？色分けは入れますか？」と確認  
3. Phase 1: /tmp/cc\_hooks\_lifecycle.mmd にMermaid記法を書き出し  
4. Phase 2: mmdc を実行して assets/flowcharts/20260408\_cc\_hooks\_lifecycle.png を生成  
5. Phase 3: 画像を表示して「これでOKですか？」と確認

修正したいときも「この分岐を追加して」と自然言語で指示するだけで、.mmd を書き換えて再レンダリングしてくれます。

### 実行例

試しにこの記事のワークフロー図を、このスキルで作らせてみました。指示はたった一行です。

「mermaid CLIでPNG化する流れのフローチャート作って」

すると今回はこんな感じの画像が出てきました。

![](https://assets.st-note.com/img/1775695409-UfAEdk9tMYDysjuncJahKmCT.png?width=1200)

### まとめ

* Mermaid記法 + mmdc の組み合わせは、テキストからPNGを1コマンドで生成できる強力なワークフローです
* 毎回パラメータを指示するのは面倒なので、Claude Code の Agent Skill として SKILL.md に手順を固定化しましょう
* description のトリガー語、フェーズ分けされたワークフロー、具体的なコマンドを書き込んでおくのがコツです
* 実行は「これ図にして」と雑に頼むだけ。Phase 0の要件確認からPhase 3の確認までスキルが全部面倒を見てくれます

GUIツールを開く時間すら惜しい人には、かなり効くワークフローだと思います。記事や資料に挟む図が増えてきた人はぜひ試してみてください。
