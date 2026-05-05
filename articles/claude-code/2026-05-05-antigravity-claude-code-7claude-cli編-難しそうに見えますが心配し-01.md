---
id: "2026-05-05-antigravity-claude-code-7claude-cli編-難しそうに見えますが心配し-01"
title: "【Antigravity × Claude Code】 7️⃣Claude CLI編 難しそうに見えますが心配しないで下さい（コマンド入れる練習 かっこいい！）"
url: "https://note.com/teyede1972/n/nef852f024764"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-05-05"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに ― シリーズのクライマックスへ

第6回でメイン画面に到達し、**Antigravity の中で Claude モデルが選べる**ことを確認しました。でも、それは**Antigravity のクオータを消費する**ので、根本的な解決ではない。

本当の戦略は **「ターミナルから直接 Claude Code を叩く」**こと。これで Claude Max プランの枠で運用できます。

第7回では、いよいよこれを実現します。シリーズの**真のクライマックス**です。

![](https://assets.st-note.com/img/1777935498-pRkTSb2IDG90K85mhi4QwUFa.png?width=1200)

> **📌 この記事での表記ルール**  
>   
> この記事では、ターミナル画面の表示を再現するときに「PS C:\Users\XXX>」と書きます。  
>   
> **「XXX」の部分は、あなたのPCのユーザー名**に読み替えてください。例えば:あなたのユーザー名が「tanaka」なら → PS C:\Users\tanaka>  
> 「doctor」なら → PS C:\Users\doctor>  
>   
>   
> あなた自身のユーザー名は、PowerShell を起動した時に最初に表示される行で確認できます。

## STEP 1Antigravity 内のターミナルを開く

Antigravity のメイン画面で、上部メニューから:

**Terminal → New Terminal**

![](https://assets.st-note.com/img/1777935625-PXY6wAaQiceSB1nlZouzdWvf.png?width=1200)

▲ 画面下部にターミナル(PowerShell)が開く

画面の下部に黒いターミナルパネルが現れました。**PowerShell**(Windows標準のシェル)が起動しています。

```
PS C:\Users\XXX> _
```

「PS」は PowerShell の略。  
「C:\Users\XXX」は今いるディレクトリ(=ユーザーフォルダ)。

### 勇気を出して claude と打ってみる

第6回で「Antigravity のメニューで Claude を選ぶのではなく、ターミナルから claude を直接叩く」と書きました。やってみます。  
📋 ターミナルに入力するコマンド(これだけコピペ)

```
claude
```

🖥️ ターミナル画面の表示

```
PS C:\Users\teyed> claude claude : 用語 'claude' は、コマンドレット、関数、スクリプト ファイル、または操作可能なプログラムの名前として認識されません。
```

> **⚠️ コピペの罠**  
>   
> 上の**黒い画面の表示**には「PS C:\Users\XXX>」というプロンプト記号がありますが、**これはコピーしないでください**。  
>   
> コピーするのは「claude」だけ。**「PS C:\Users\...」はターミナルが自動で表示する印**です。これを一緒にコピペすると「PS というコマンドが見つかりません」というエラーになります。

## 😅 罠ポイント発生
