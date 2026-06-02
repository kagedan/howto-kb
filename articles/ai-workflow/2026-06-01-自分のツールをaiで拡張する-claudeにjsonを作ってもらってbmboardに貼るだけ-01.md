---
id: "2026-06-01-自分のツールをaiで拡張する-claudeにjsonを作ってもらってbmboardに貼るだけ-01"
title: "自分のツールをAIで拡張する — ClaudeにJSONを作ってもらってBMBoardに貼るだけ"
url: "https://zenn.dev/99letters/articles/1474c9c9ffa104"
source: "zenn"
category: "ai-workflow"
tags: ["API", "GPT", "JavaScript", "zenn"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

## 概要

Black Mirror Board（BMBoard）には「spell」という拡張システムがある。  
<https://bmboard.studio/>  
1行のJSONを書けば、自分だけのコマンドをBMBoardに追加できる。  
そのJSONをClaudeや ChatGPTに作ってもらえば、コードを書けなくてもキャンバスを拡張できる。

---

## spellの形

```
{"command":"circle-layout","action":"const sel = BM.getSelected();\nif (!sel.length) { BM.log('select objects first.', 't-err'); return; }\nconst N = sel.length;\nconst vc = BM.viewCenter();\nconst R = 300;\nsel.forEach((o, i) => {\n  const angle = (2 * Math.PI / N) * i - Math.PI / 2;\n  o.data.x = vc.x + R * Math.cos(angle) - 40;\n  o.data.y = vc.y + R * Math.sin(angle) - 40;\n});\nBM.redraw();\nBM.log('arranged ' + N + ' objects in a circle.');"}
```

* `command` → 呼び出し名（`$circle-layout` で実行）
* `action` → 実行されるJavaScript

---

## Claudeへのプロンプト

以下をそのままClaudeにコピペする：

```
You are creating a "spell" for BMBoard, a single-page canvas web app.
Output only a single line of JSON: {"command":"NAME","action":"JS"}

BM API:
- BM.getSelected()          → selected objects array
- BM.all()                  → all objects array
- BM.create(type, props)    → create object (type: circle|square|triangle|arrow|text)
- BM.translate(obj, dx, dy) → move object
- BM.setStroke(obj, color)  → set stroke color
- BM.setFill(obj, color)    → set fill color
- BM.remove(obj)            → remove object
- BM.viewCenter()           → {x, y} of current view center
- BM.rand(min, max)         → random number
- BM.log(msg, cls?)         → log to terminal
- BM.redraw()               → redraw canvas (always call at end)
- BM.save()                 → save state

Rules:
- NO 'rect' type (use 'square')
- NO async/await
- Always end with BM.redraw()
- Keep it under 300 chars of action JS

Now create a spell: [ここに何をしたいか日本語で書く]
```

最後の1行を変えるだけで、好きなspellが作れる。

---

## 具体例

### 「選択したオブジェクトを円形に並べる」

```
Now create a spell: 選択したオブジェクトを円形に並べる
```

Claudeの出力：

```
{"command":"circle-layout","action":"const sel=BM.getSelected();if(!sel.length){BM.log('select first','t-err');return;}const N=sel.length,vc=BM.viewCenter(),R=280;sel.forEach((o,i)=>{const a=(2*Math.PI/N)*i-Math.PI/2;o.data.x=vc.x+R*Math.cos(a)-40;o.data.y=vc.y+R*Math.sin(a)-40;});BM.redraw();BM.log('circle layout: '+N+' objects');"}
```

### 「全オブジェクトのサイズをランダムに変える」

```
{"command":"chaos-size","action":"for(const o of BM.all()){if(o.data.w){o.data.w=BM.rand(40,200);o.data.h=o.data.w;}}BM.redraw();BM.log('chaos applied.');"}
```

### 「今日の日付をテキストでキャンバス中央に置く」

```
{"command":"today","action":"const d=new Date(),s=d.getFullYear()+'/'+(d.getMonth()+1)+'/'+d.getDate(),vc=BM.viewCenter();BM.create('text',{x:vc.x-60,y:vc.y,text:s,fontSize:32});BM.redraw();BM.log('date placed: '+s);"}
```

---

## BMBoardへの貼り付け方

1. ClaudeやChatGPTがJSONを返したら
2. そのJSONをコピー（`Cmd+C`）
3. BMBoardのテキストボックスにペースト（`Cmd+V`）
4. **自動登録される**（Enterも不要）

ターミナルに `[OK] spell acquired — run: $circle-layout` と表示されたら完了。  
あとは `$circle-layout` と打つだけ。

---

## spellの共有

作ったspellは他の人にも渡せる。

ターミナルに打つとJSONがクリップボードにコピーされる。それをSlackやDiscordで送れば、受け取った人も同じspellを使える。

---

## なぜこの設計にしたのか

「自分のツールを自分で拡張できる」というコンセプトから生まれた。

プラグインシステムを作ろうとすると、ローカルサーバーが必要になったり、設定ファイルが必要になったり、複雑になりがちだ。

JSONひとつ、貼るだけ——この単純さがすべてだと思った。

AIが生成したコードをそのまま動かせる。コードが読めなくても、日本語で「こういう動きをするspellを作って」と言えば拡張できる。

自分のツールをAIで育てていく体験——これがTerminal Magicの本質だ。

---

*BMBoard → bmboard.studio（無料・登録不要・オフライン動作）*  
\*spell仕様の詳細 → bmboard.studio/spell-spec.html  
\*木下スタジオ → <https://kinoshita.studio/>
