---
id: "2026-03-24-zed-claude-code-agent-deckエディタ内で完結する生成ai開発環境の作り方-01"
title: "Zed × Claude Code × agent-deck：エディタ内で完結する生成AI開発環境の作り方"
url: "https://zenn.dev/milmed/articles/745aa734fcfdcc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

## なぜZed上でClaude Codeを動かすのか

生成AIツール（Claude Codeなど）をターミナルで使うとき、多くの方は別ウィンドウや専用ターミナルアプリを開き、その中でコマンドを実行します。  
しかし、その方法には次のような課題があります。

* ウィンドウやタブの切り替えが頻繁に発生する
* ターミナルとエディタで操作体系が異なり、コンテキストスイッチが大きい
* ファイルパスや行番号をコピーしてAIに渡す操作が手間になりがち

そこで私は、**Zedのエディタ領域そのものをターミナルとして使う**ことで、  
「普段のプログラミング操作の延長」でClaude Codeを扱えるようにしています。

さらに、Zedでは Shift+Esc でアクティブなタブを一時的に全体表示（フルスクリーン風に拡大）できるため、Claude Codeの出力やコードをじっくり読むときにも、タブ分割をいちいち戻さずに集中しやすくなります。

## 1. エディタ領域でターミナルを開く

Zedには専用の「ターミナル領域」もありますが、私はあえて**エディタのタブとしてターミナルを開く**ようにしています。

* エディタタブとして開くことで、タブの分割・移動・閉じるなどの操作がZed標準のショートカットで完結する
* 普段から慣れているエディタ操作のまま、ターミナルも扱えるため、学習コストがほぼゼロ
* ターミナルも「エディタの一タブ」として扱えるため、ウィンドウの行き来が減り、集中が続きやすい

設定例（キーコンフィグ抜粋）：

```
{
  "bindings": {
    "ctrl-cmd-n": "workspace::NewCenterTerminal"
  }
}
```

これにより、`Ctrl+Cmd+N` で中央にターミナルタブを開き、  
そのまま他のファイルタブと同じように扱うことができます。

![](https://static.zenn.studio/user-upload/44c3104230ac-20260324.gif)

## 2. キーコンフィグの柔軟性とAIによる自動生成

Zedはもともとエディタなので、キーコンフィグが非常に柔軟です。  
さらに、Claude Codeなどの生成AIに

> 「Zedで、ターミナルタブを左右に移動するショートカットを設定したい」

のように**口頭で説明するだけで、設定JSONを生成してもらえる**点が大きな強みです。

以前は「やりたい処理 → 対応するコマンド名を調べる → JSONを手書き」という手順が必要でしたが、  
今はAIに「こうしたい」と伝えるだけで、ほぼ完成形の設定が手に入ります。

実際の設定例（ターミナルタブの移動など）：

```
{
  "context": "Terminal",
  "bindings": {
    "ctrl-w h": "workspace::ActivatePaneLeft",
    "ctrl-w l": "workspace::ActivatePaneRight",
    "ctrl-w k": "workspace::ActivatePaneUp",
    "ctrl-w j": "workspace::ActivatePaneDown",
    "ctrl-w ctrl-h": [
      "workspace::MoveItemToPaneInDirection",
      { "direction": "left" }
    ],
    "ctrl-w ctrl-l": [
      "workspace::MoveItemToPaneInDirection",
      { "direction": "right" }
    ],
    "ctrl-w ctrl-k": [
      "workspace::MoveItemToPaneInDirection",
      { "direction": "up" }
    ],
    "ctrl-w ctrl-j": [
      "workspace::MoveItemToPaneInDirection",
      { "direction": "down" }
    ]
  }
}
```

これにより、Vimライクな `Ctrl+W` 系の操作で、  
ターミナルタブを「アクティブにする」「別ペインに移動する」といった操作が直感的に行えます。

---

## 3. ファイルエクスプローラーとタスク機能による「AI連携の自動化」

### 3.1 ファイルエクスプローラー

Zedには標準のファイルエクスプローラー（Project Panel）があり、  
`yazi` などターミナル上のファイラも便利ですが、**エディタ内で完結できる**点が利点です。

* ファイルツリーの表示・選択・新規作成がエディタ内で完結
* ショートカットでエクスプローラーとエディタを切り替えられる（例：`space e`）

```
{
  "context": "vim_mode == normal && !menu",
  "bindings": {
    "space e": "project_panel::ToggleFocus"
  }
}
```

これにより、Claude Codeに「このファイルのこの行を参照してほしい」というときも、  
エディタ内でファイルを選び、そのままターミナルタブにコマンドを打つ、という流れが自然になります。

### 3.2 タスク機能を使った「AI連携の自動化」

Zedのタスク機能を使うと、**「現在のファイル・行・選択範囲」を自動でAIに渡すためのコマンド**を定義できます。

私の設定例：

```
{
  "label": "Copy @file#line for Claude Code",
  "command": "echo -n \"@$ZED_RELATIVE_FILE\" | pbcopy && echo \"Copied: @$ZED_RELATIVE_FILE\"",
  "use_new_terminal": false,
  "allow_concurrent_runs": false,
  "reveal": "never",
  "hide": "always",
  "shell": "system"
},
{
  "label": "Copy @file#range for Claude Code",
  "command": "lines=$(printf '%s\\n' \"$ZED_SELECTED_TEXT\" | wc -l | tr -d ' ') && end=$ZED_ROW && start=$((end - lines + 1)) && echo -n \"@$ZED_RELATIVE_FILE#$start-$end\" | pbcopy && echo \"Copied: @$ZED_RELATIVE_FILE#$start-$end\" && osascript -e 'tell application \"System Events\" to key code 53'",
  "use_new_terminal": false,
  "allow_concurrent_runs": false,
  "reveal": "never",
  "hide": "always",
  "shell": "system"
}
```

これらをキーコンフィグから呼び出すことで、

* ノーマルモードで `space y` → 現在のファイルパスをクリップボードにコピー
* ビジュアルモードで `space y` → 選択範囲の行番号付きファイルパスをコピー

という動作が可能になります。

#### 具体的なファイルパス・行番号のフォーマット例

上記タスクによってコピーされる文字列の例は、たとえば次のようになります。

* ファイル全体を参照する場合  
  `@src/main.rs`
* 特定の行を参照する場合  
  `@src/main.rs#42`
* 行範囲を参照する場合  
  `@src/main.rs#10-20`

このような形式でファイルパスと行番号をClaude Codeに渡すことで、

> 「`@src/main.rs#10-20` の範囲をリファクタリングしてください」

のように、**ファイルと行番号を明示した指示**を簡単に行うことができます。

---

## 4. agent-deckを併用した「タブ内セッション管理」でさらに快適に

Zedのタブ単位での操作だけでも十分快適ですが、  
**[agent-deck](https://github.com/asheshgoplani/agent-deck)**（ターミナルセッション管理ツール）を併用することで、  
「タブ内で開くセッションの切り替え」も簡単になります。

* 1つのターミナルタブの中で、複数のセッション（例：Claude Codeセッション、通常シェルセッション）を切り替えられる
* タブの分割や再配置を頻繁にいじる必要が減り、画面レイアウトを安定させたまま作業できる
* Zedのタブ分割・移動ショートカットと組み合わせることで、「タブ構造 × セッション構造」の両方を自在に扱える

これにより、

* 「AI用タブ」「通常開発用タブ」といった**タブ単位の役割分担**
* その中での「Claude Codeセッション」「通常シェルセッション」といった**セッション単位の切り替え**

を分けて管理できるため、画面構成を頻繁に変えずに済み、よりストレスの少ない操作体験になります。

---

## 5. Diff・ジャンプ・LSPなど開発体験の一体化

ターミナルだけで開発を完結させようとすると、

* 変更差分（Diff）の確認
* 定義ジャンプ・参照ジャンプ
* LSPによる補完・型チェック

などをターミナル内のエディタ（Vimなど）で行うことになり、  
環境構築のコストが高くなりがちです。

一方、Zedはもともとプログラミング用エディタとして、

* Git連携によるDiff表示
* LSP連携による補完・エラー表示
* プロジェクト全体の検索・ジャンプ

といった機能が標準で備わっています。

**Zedの中でターミナルを動かし、agent-deckでセッション管理を行う**ことで、

* コード編集・Diff確認・ジャンプはZedの機能で
* 生成AIの実行はターミナルタブ内のagent-deckセッションで

という役割分担が自然にでき、  
「開発に必要な操作体験」を一つのエディタでまるごと得られる点が大きなメリットです。

---

## まとめ

* Zedのエディタタブとしてターミナルを開くことで、ウィンドウ切り替えを減らし、普段のエディタ操作の延長でClaude Codeを扱える
* キーコンフィグの柔軟性とAIによる自動生成で、欲しい操作をすぐにショートカット化できる
* ファイルエクスプローラーとタスク機能を組み合わせることで、「ファイルパス＋行番号」をAIに自動で渡すワークフローを構築できる  
  （例：`@src/main.rs#10-20` のような形式でファイルと行番号を渡せる）
* agent-deckを併用することで、タブ内セッションの切り替えも容易になり、タブ構成を頻繁に変えずに済む
* Diff・ジャンプ・LSPなど開発に必要な機能をZed内で完結させられるため、環境構築コストを抑えつつ快適な開発体験を得られる

このように、\*\*「エディタ内でターミナルを動かし、agent-deckでセッション管理する」\*\*という発想をZedで実現することで、  
生成AIツールとの連携がより自然で効率的なものになります。

PS: この記事はSakana AIで作成しました。
