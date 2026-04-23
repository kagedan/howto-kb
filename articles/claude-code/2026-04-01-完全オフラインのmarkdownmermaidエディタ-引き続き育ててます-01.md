---
id: "2026-04-01-完全オフラインのmarkdownmermaidエディタ-引き続き育ててます-01"
title: "完全オフラインのMarkdown/Mermaidエディタ 引き続き育ててます"
url: "https://zenn.dev/akinobukato/articles/6a19fb5479a80f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

## はじめに

[前回の記事](https://zenn.dev/acntechjp/articles/5a8b7b334b15bc)で紹介した **Markdown Studio** — Claude Codeで毎日育てる完全オフラインのMarkdown/Mermaidエディタ — を、その後も日々の業務で使いながら改善を続けてきた。

今回は **〜 v1.4.0** で追加した機能をまとめて紹介する。

**ダウンロード（Windows 64bit・インストール不要）：**  
<https://github.com/5843435/markdown-sheet/raw/main/markdown-sheet-v1.4.0.exe.dat>

### セットアップ（3ステップ）

1. 上のリンクからファイルをダウンロード
2. ファイル名を `markdown-sheet.exe` にリネーム
3. exe を右クリック → **プロパティ** → 「セキュリティ: このファイルは他のコンピューターから…」の **「許可する」にチェック** → OK

あとはダブルクリックで起動するだけ。インストール不要、レジストリも汚さない。好きなフォルダに置いて使える。

> GitHub Releases（`.exe` / `.msi`）からのダウンロードが社内NWでブロックされる場合があるため、`.dat` 拡張子で配布しています。

## 今回の主な追加機能

| 機能 | 概要 |
| --- | --- |
| **WYSIWYGプレビュー編集** | プレビュー上の見出し・段落・テーブルを直接クリックして編集 |
| **編集/閲覧モード切替** | 誤編集防止のトグルボタン |
| **クリップボード画像ペースト** | Ctrl+Vで画像を自動保存＋Markdown挿入 |
| **.md ファイル関連付け** | ダブルクリックでMarkdown Studioが起動 |
| **左パネル非表示** | フォルダ/アウトラインを隠してプレビューに集中 |
| **Mermaidレンダリング修正** | シーケンス図などが描画されない問題を解決 |
| **HTML出力の改善** | 不要なUIボタンの除去、タイムスタンプファイル名 |

## WYSIWYGプレビュー編集（v1.3.0）

![](https://static.zenn.studio/user-upload/873311bef597-20260401.png)  
一番大きな変更。プレビュー画面の**見出し・段落・リスト・テーブルセル**を直接クリックして、その場で編集できるようにした。

![](https://res.cloudinary.com/zenn/image/fetch/s--5cMjLoO6--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/images/20260401_wysiwyg.png?_a=BACAGSGT)

### 仕組み

1. markedのカスタムレンダラーで各要素に `data-editable="true"` と `data-source-start/end`（ソース行番号）を付与
2. `contentEditable` を使ってブラウザネイティブの編集機能を有効化
3. 編集確定時に `reconstructBlock()` でHTMLをMarkdownに逆変換
4. ソース行番号を使って元のMarkdownテキストの該当箇所だけを差し替え

テーブルセルの編集はTab/Shift+Tabでセル間移動にも対応。右クリックで行列の追加・削除もできる。

### 編集/閲覧モード切替

「プレビューを見たいだけなのに触ると編集されてしまう」問題を解決するため、プレビュー上部のコントロールバーにトグルボタンを追加した。

* **✏ 編集モード** — 従来通りクリックで直接編集可能
* **👁 閲覧モード** — クリックしても編集されない、hover時のボーダーも非表示

設定はlocalStorageに保存されるのでアプリ再起動後も維持される。

## クリップボード画像ペースト（v1.4.0）

Zennのエディタのように、**スクリーンショットや画像をCtrl+Vでそのまま貼り付け**できるようにした。

### 動作フロー

1. スクリーンショットを撮る or 画像をコピー
2. エディタにフォーカスして **Ctrl+V**
3. 画像が自動保存され `![](images/20260401153022.png)` が挿入される

保存先のルール：

| 状態 | 画像の保存先 | Markdown挿入 |
| --- | --- | --- |
| ファイル保存済み | `{ファイルと同じフォルダ}/images/` | `![](images/xxx.png)` （相対パス） |
| 無題タブ | `%TEMP%/markdown-studio-images/` | `![](C:/.../xxx.png)` （絶対パス） |

プレビュー側の画像表示も対応済み。相対パス・絶対パスどちらもローカルファイルから読み込んで表示する。

## .md ファイル関連付け（v1.4.0）

エクスプローラーで `.md` ファイルをダブルクリックすると Markdown Studio が起動してそのファイルを開く。

実装はシンプル：

* `tauri.conf.json` に `fileAssociations` を設定
* Rust側に `get_initial_file` コマンドを追加（`std::env::args()` からファイルパスを取得）
* フロントエンド側で起動時にこのコマンドを呼んでファイルを読み込み

```
// tauri.conf.json
"fileAssociations": [
  {
    "ext": ["md", "markdown"],
    "description": "Markdown Document",
    "role": "Editor"
  }
]
```

## Mermaidレンダリング修正（v1.2.2）

**シーケンス図やガントチャートがプレビューに描画されない**というバグを修正。

### 原因

React 19 StrictModeとの相互作用で、`innerHTML` を設定するeffectと Mermaid レンダリングを実行するeffectが別々だったため、タイミングによってDOM更新前にMermaidが走ってプレースホルダーを見つけられなかった。

### 修正

2つの `useEffect` を1つに統合。innerHTML設定直後にMermaidレンダリングが確実に走るようにした。

```
// BEFORE: 2つの別々のeffect
useEffect(() => { div.innerHTML = html; }, [html]);
useEffect(() => { /* mermaid rendering */ }, [html, ref]);

// AFTER: 1つに統合
useEffect(() => {
  div.innerHTML = html;
  // ... mermaid rendering follows immediately
}, [html, filePath, ref]);
```

## その他の改善

### 無題タブを閉じられるように

最後のタブを閉じると自動で新しい空タブが生成される。「タブが閉じれない」ストレスを解消。

### 左パネルの表示/非表示

フォルダ/アウトラインパネルを隠せるようにした。ツールバーの「◁ パネル / ▷ パネル」で切替。エディタも非表示にすればプレビューだけのフルスクリーン表示になる。

### エクスポートファイル名の改善

PDF/HTML出力時、無題ファイルの場合は `YYYYMMDDHHMM.pdf` のようなタイムスタンプ形式のファイル名がデフォルトになるようにした。`document.pdf` で毎回上書きしてしまう問題を解消。

### HTML出力のクリーンアップ

HTMLエクスポート時にMermaid図のUIボタン（ズーム、SVGコピー、AI編集）が含まれてしまう問題を修正。DOMクローン時に `.mermaid-actions` と `.mermaid-ai-panel` を除去してからHTMLを取得するようにした。

## 開発スタイルは変わらない

前回の記事で書いた「Claude Codeで毎日育てる」開発スタイルは今も継続中。Zennの 記事エディタが結構良い感じで、これをオフラインで使える ＋ α にした感じに今はなっている。

今回の機能も、すべてClaude Codeとの対話で実装。日々使っていながら、「この機能欲しいな」→ Claude Codeに依頼 → ビルド → そのまま実務で使う、というサイクルを回しています

ただ、Claude Codeも信じすぎちゃダメ。使ってみると意外にバグがあったり、なんかデグレったりしているので、やはり自分できちんと使って試してみるは必要だな、と思っています。

---

**GitHub**: <https://github.com/5843435/markdown-sheet>  
**ダウンロード**: <https://github.com/5843435/markdown-sheet/raw/main/markdown-sheet-v1.4.0.exe.dat>
