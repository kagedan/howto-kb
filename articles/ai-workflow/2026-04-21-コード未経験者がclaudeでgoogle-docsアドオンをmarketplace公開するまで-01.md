---
id: "2026-04-21-コード未経験者がclaudeでgoogle-docsアドオンをmarketplace公開するまで-01"
title: "コード未経験者がClaudeでGoogle DocsアドオンをMarketplace公開するまで"
url: "https://qiita.com/TateGaki/items/770a64b8fb490816a50f"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-21"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

📌

**この記事について**

* 対象：非エンジニア／AIで個人開発をやってみたい人／GAS開発者
* 読了時間：約10分
* 作ったもの：Google Docsの縦書きアドオン「TateGaki」

## はじめに

2026年2月まで、私はコードを一行も書いたことがありませんでした。

そんな私が、Claude（Anthropic社のAI）との対話だけでGoogle Docsの縦書きアドオン「TateGaki」を開発し、Google Workspace Marketplaceの審査を通過して公開するに至りました。

この記事は、**非エンジニアがAIを相棒にアドオンを作った実装記録**です。GAS（Google Apps Script）の制約、Marketplace審査のハマりどころ、そして「バイブコーディング」での開発プロセスをまとめています。

[![TateGaki-note.gif](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4412612%2Fd9d747df-5de5-4bb7-89ac-f3257156daf3.gif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2d4c627c0a787720ae1fb91a5d01cfaa)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4412612%2Fd9d747df-5de5-4bb7-89ac-f3257156daf3.gif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2d4c627c0a787720ae1fb91a5d01cfaa)  
*TateGakiの実動デモ。Google Docs内のダイアログで縦書き入力・マス配置・ルビ・保存が完結する。*

---

## 1. 背景・モチベーション

### なぜ作ったか

子供の作文の宿題をGoogle Docsで書かせようとしたとき、ふと気づきました。

> Google Docsって、縦書きできないんだ。

Wordは縦書きに対応していますが、重く、共有もしにくい。一方Google Docsはブラウザ完結で軽快です。小説家、同人作家、教育関係者、海外在住の日本人など、**Webで縦書きしたい人**は少なくないはずです。

GeminiとClaudeに聞いてみましたが、無料で使える縦書きアドオンは見当たらず、年額課金のものが一つあるくらい。自分が使うかと考えても使わない価格帯で、「競合がほぼいない領域」なのだと気づきました。

**ないなら作ろう。** とはいえ、私はコードが書けません。

### Claudeが相棒になった

「Claudeに聞きながら作れば、できるかもしれない」

これが出発点でした。結果として、設計・実装・デバッグ・Marketplace審査対応まで、ほぼ全てをClaudeとの対話（いわゆる**バイブコーディング**）で進めました。

---

## 2. 技術スタック

* **Google Apps Script (GAS)**：アドオン本体のランタイム
* **HTML Service**：モーダレスダイアログのカスタムUI
* **Google Docs Service**：本文取得・テーブル書き戻し
* **Drive Advanced Service** (`Drive.Files`)：ファイル保存・一覧取得（`drive.file` スコープで最小権限）
* **Canvas API**：縦書きレイアウトのレンダリング
* **Claude / Claude Code**：設計・実装のペアプログラミング相手

---

## 3. 技術的に難しかった点

### 3-1. 縦書きレンダリング（Canvas × DOMのハイブリッド方式）

Google Docs本体には縦書き機能がないため、モーダレスダイアログ内で縦書き表示を自前で描画する方針にしました。

[![01_400字詰め原稿用紙.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4412612%2Fb208237b-5def-4081-9143-47c3138c7e82.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=dac5d1193e8afa0c6dd42ffc590c0ad3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4412612%2Fb208237b-5def-4081-9143-47c3138c7e82.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=dac5d1193e8afa0c6dd42ffc590c0ad3)  
*キャプション*：400字詰め原稿用紙モード。Canvasで罫線を、DOMで1マス＝1文字を配置するハイブリッド構成。

ただし、**純粋にCanvasだけで描画するとIMEとの相性が最悪**になります（変換中の文字表示、カーソル位置、ルビの個別クリックなど、編集UIとしての実用に耐えない）。そこでTateGakiでは以下のハイブリッド構成を採用しました。

* **Canvas**：原稿用紙の罫線（マス目）だけを描画
* **DOM `<div>`**：1マス＝1要素として文字・ルビ・改行マークを配置

#### エントリポイント：2つの表示モード

TateGakiには「プレーン縦書き」と「原稿用紙（400字詰め／200字詰め）」の2モードがあり、`render()` がディスパッチャの役割を担っています。

```
// ===== RENDER =====
function render() {
  const mode = $m.value;
  $w.innerHTML = '';
  $w.classList.remove('rtl');

  if (mode.startsWith('plain')) {
    // プレーン縦書き：マス目なし、自由入力
    renderPlain(mode);
    document.getElementById('sRW').style.display = 'none';
    document.getElementById('inst').textContent =
      '自由に縦書きで入力 ｜ 印刷時はページ単位で分割されます';
  } else {
    // 原稿用紙モード（200字詰めはさらにRTL方向）
    if (mode === '200') $w.classList.add('rtl');
    renderMS(mode);
    document.getElementById('sRW').style.display = '';
    document.getElementById('inst').textContent =
      '原稿用紙をクリックして入力開始 ｜ Enterで改行 ｜ ルビ欄クリックでふりがな入力 ｜ Ctrl+Z/Y で元に戻す/やり直し ｜ Ctrl+V で貼り付け';
  }
  updateStats();
  scrollToCursor();
}
```

地味ですが、`mode === '200'` のときだけ `rtl` クラスを付けているのがポイントです。200字詰め原稿用紙は伝統的に**ページ内の列が右から左へ流れる**ため、CSSの `direction: rtl` で一括制御しています（400字詰めは左→右なのでデフォルトのまま）。

この `render()` から `renderMS()` が呼ばれ、その中で次の「Canvas × DOM のマス描画ループ」が動きます。

#### 原稿用紙マス × DOMの描画ループ

```
// ===== Canvas グリッド（罫線だけCanvasで描画） =====
const cv = document.createElement('canvas');
cv.width  = c.pw;  cv.height = c.ph;
cv.style.cssText = 'position:absolute;top:0;left:0;pointer-events:none;z-index:1;';
if (gridOn) {
  drawGrid(cv, c);                  // マス目を描画
} else {
  const ctx = cv.getContext('2d');
  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, cv.width, cv.height);
}
paper.appendChild(cv);

const font = $f.value;
const fs   = c.ch * 0.68;           // 文字サイズはマス高の68%

// ===== マスごとにDOM要素を配置 =====
for (let col = 0; col < c.cols; col++) {
  for (let row = 0; row < c.rows; row++) {
    const rubyX = c.pw - c.mr - col * c.colW - c.rw;   // ルビ欄のX
    const cellX = rubyX - c.cw;                         // 本文マスのX
    const cellY = c.mt + row * c.ch;
    const key   = `${pi}-${col}-${row}`;
    const textIdx = layout.cellMap.get(key);            // 禁則処理で作ったマップを再利用

    // --- 1. ルビセル（親文字の右側に独立した <div> として配置） ---
    if (textIdx !== undefined) {
      const isCompChar = textIdx >= compStart && textIdx < compEnd;
      if (!isCompChar) {
        const origIdx = textIdx < compStart ? textIdx : textIdx - composingText.length;
        if (origIdx >= 0 && origIdx < T.length) {
          const rb = document.createElement('div');
          const hasR = RM[origIdx];
          rb.className = 'ruby-cell' + (hasR ? ' has-ruby' : '');
          // ルビ文字数に応じてフォントサイズを自動調整
          let rfs = 9;
          if (hasR && hasR.length > 2)
            rfs = Math.max(5, Math.min(9, (c.ch * 0.9) / hasR.length * 1.2));
          rb.style.cssText =
            `left:${rubyX}px;top:${cellY}px;width:${c.rw}px;height:${c.ch}px;font-size:${rfs}px;`;
          if (hasR) rb.textContent = hasR;
          // ルビセルをクリックするとルビ編集モーダルを開く
          const capturedIdx = origIdx;
          rb.addEventListener('mousedown', (ev) => {
            ev.stopPropagation(); ev.preventDefault();
            openRuby(capturedIdx);
          });
          paper.appendChild(rb);
        }
      }
    }

    // --- 2. 文字セル ---
    const cl = document.createElement('div');
    let cls = 'cell';
    // カーソル位置ならハイライト
    if (cursorCell && pi === cursorCell.p && col === cursorCell.c && row === cursorCell.r)
      cls += ' cursor-cell';
    // IME変換中ならハイライト
    if (textIdx !== undefined && textIdx >= compStart && textIdx < compEnd)
      cls += ' composing';
    cl.className = cls;
    cl.style.cssText =
      `left:${cellX}px;top:${cellY}px;width:${c.cw}px;height:${c.ch}px;font-size:${fs}px;font-family:${font};`;
    if (textIdx !== undefined && textIdx < displayText.length) {
      const ch = displayText[textIdx];
      cl.textContent = ch;
      // ー や （ など、縦書き時に90度回転が必要な文字
      const rot = getCharTransform(ch);
      if (rot) cl.style.transform = rot;
    }
    paper.appendChild(cl);

    // --- 3. 改行マーク（編集時の可視化用） ---
    if (layout.nlCells.has(key)) {
      const nlm = document.createElement('div');
      nlm.className = 'nl-mark';
      nlm.style.cssText =
        `left:${cellX}px;top:${cellY}px;width:${c.cw}px;height:${c.ch}px;`;
      nlm.textContent = '↵';
      paper.appendChild(nlm);
    }
  }
}
```

#### この設計のメリット

| **ポイント** | **効果** |
| --- | --- |
| 罫線だけCanvas | マス目の描画コストを1枚の画像に集約。文字が変わっても罫線は再描画不要 |
| 1マス＝1 `<div>` | `cursor-cell` / `composing` クラスを付け替えるだけでIMEや選択状態を可視化できる |
| ルビを独立 `<div>` に | ルビ欄にだけクリック判定を持たせ、`openRuby(idx)` で編集モーダルを起動できる |
| `getCharTransform(ch)` | 長音符 `ー` や括弧類を CSS `transform` で90度回転。縦書き特有の処理を描画と分離 |
| `layout.cellMap` を再利用 | 禁則処理で作ったマップをそのまま使えるので、配置ロジックと描画ロジックが疎結合 |

Claudeとは最初「全部Canvasで描画」を検討していたのですが、**IMEのcomposition表示が絶望的に難しく**、「罫線だけCanvas、文字はDOM」というハイブリッド案に切り替えた経緯があります。結果として、カーソル移動・IME変換中表示・ルビ編集など、編集UIに必要な挙動が素直に実装できました。

### 3-2. IME予測変換ウィンドウの位置合わせ（最大の難所）

実は、**一番苦労したのは禁則処理でもレンダリングでもなく、この「IME変換候補ウィンドウがどこに出るか」**でした。

横書きのテキストエディタならIMEはブラウザが自動でよしなに位置を決めてくれます。ところが**縦書きでは、そのデフォルト挙動が使い物になりません**。変換候補ウィンドウが書いている文字にガッツリ被ってしまい、**いま打ち込んだ文字が見えない**のです。

縦書きアドオンを作る人なら誰もが通るであろう地雷で、Claude と**何日もキャッチボール**を繰り返しました。

#### なぜ自動では解決しないのか

Web の IME 変換ウィンドウは、**実際にキー入力を受け取っている DOM 要素（隠し textarea など）の位置**を基準に表示されます。TateGaki は「1マス＝1 `<div>`」の DOM 方式でマス目を描画していますが、**入力自体は画面外の隠し textarea で受けている**ため、そのままだと IME ウィンドウが明後日の方向に出てしまいます。

* **入力を受け取る要素の位置** ≠ **ユーザーが文字を書いているマスの位置**

このズレを毎回解消する必要がありました。

#### 対策：隠し textarea を「幅2pxの縦線」としてカーソル付近に置く

TateGakiでは、**隠しIME用の `<textarea>`（`$ime`）を幅2pxの「細い縦線」として扱い、毎フレーム、カーソルのあるマスの近くに置き直す**という設計にしました。

* `$ime` を幅2pxにしておけば見た目の邪魔にならず、**位置アンカー専用**として機能する
* ブラウザはこの `$ime` の位置を基準に IME 変換候補ウィンドウを表示するので、**`$ime` を動かせばウィンドウも動く**
* カーソル位置のマス座標を計算し、書いている文字に候補ウィンドウが被らないよう**左右どちらかにオフセット**して配置する
* `render()` 直後やルビモーダルを閉じた直後に `focusIME()` を呼ぶ。`requestAnimationFrame` で DOM 描画を1フレーム待ってから位置を確定する

実際のコード（`positionIME()` と `focusIME()`）です。

```
// IME入力要素の位置を「いまユーザーが文字を書いているマス」に合わせる
function positionIME() {
  const mode = $m.value;
  if (mode.startsWith('plain')) return;   // プレーンモードはマス目なしなのでスキップ
  const c = CFG[mode];
  if (!c) return;

  // 変換中(composingText)も含めた仮テキストでレイアウトを再計算し、
  // 現在のカーソルが原稿用紙上のどのマスに来るかを求める
  const displayText = T.slice(0, CP) + composingText + T.slice(CP);
  const layout = buildLayout(displayText, c.cols, c.rows);

  let cellPos;
  if (CP < displayText.length) {
    cellPos = layout.textToCell[CP];
    if (cellPos && cellPos.nl) cellPos = layout.cursorPos;
  } else {
    cellPos = layout.cursorPos;
  }
  if (!cellPos) return;

  // 該当ページ(.ms-paper)の画面上の位置を取得
  const papers = $w.querySelectorAll('.ms-paper');
  const paper  = papers[cellPos.p];
  if (!paper) return;

  const rect  = paper.getBoundingClientRect();
  const cellX = c.pw - c.mr - cellPos.c * c.colW - c.rw - c.cw;  // ページ内のマスX
  const cellY = c.mt + cellPos.r * c.ch;                          // ページ内のマスY

  // ★ 一番ハマったポイント：IMEウィンドウを左右どちらに出すか
  // カーソルがページの右半分にあるなら左側、左半分なら右側にIMEを逃がす
  const cursorInRightHalf = cellX > c.pw / 2;
  const cellScreenX       = rect.left + cellX;

  let imeLeft;
  if (cursorInRightHalf) {
    imeLeft = cellScreenX - 320;                  // 左側に320pxずらす
  } else {
    imeLeft = cellScreenX + c.cw + c.colW * 2;    // 右側に2列ぶんずらす
  }
  // 画面外にはみ出さないようクランプ
  imeLeft = Math.max(10, Math.min(imeLeft, window.innerWidth - 20));

  // 隠しIMEは「幅2pxの細い縦線」として配置（位置アンカー専用）
  $ime.style.left     = imeLeft + 'px';
  $ime.style.top      = (rect.top + cellY) + 'px';
  $ime.style.width    = '2px';
  $ime.style.height   = c.ch + 'px';
  $ime.style.fontSize = (c.ch * 0.6) + 'px';
}

// render 直後やモーダル閉じ直後に呼ぶ。
// requestAnimationFrame でDOM描画を1フレーム待ってから位置を確定。
function focusIME() {
  requestAnimationFrame(() => {
    positionIME();
    $ime.focus({ preventScroll: true });
  });
}
```

#### この実装の勘どころ（地味にハマったやつ）

* **カーソル位置は「レイアウトの再計算」から求める**：`T` と `composingText` を結合した仮テキストで `buildLayout` を呼び直し、変換中の文字も含めてカーソルがどのマスに来るかを特定。DOM から `.cursor-cell` を探すより、**描画前でも位置が決まる**のが利点です。
* **右半分なら左、左半分なら右に IME を逃がす**：縦書きは右端から書き始めるので、書き始めはカーソルが「右半分」にあり IME 候補ウィンドウは自動で左にオフセットされる。書き進めて左半分に入ったら逆に右へ。この `cellX > c.pw / 2` という素朴な判定に落ち着くまで何度も試行錯誤しました。
* **320px というマジックナンバー**：Chrome の IME 変換候補ウィンドウがだいたい収まる幅。ブラウザや IME によってブレるので大きめに取り、`window.innerWidth` でクランプして画面外には出ないようにしています。
* **composition 中もレイアウト再計算する**：`composingText` を混ぜて `buildLayout` を呼び直さないと、変換中に列をまたいだ瞬間に IME が前のマス位置に張り付く挙動になりました。
* **`requestAnimationFrame` で1フレーム待つ**：`render()` 直後に同期で位置計算すると、DOM がまだ画面に反映されていないタイミングで `getBoundingClientRect()` が古い値を返すことがあり、IME が一瞬前のマスに引きずられてチラつきました。
* **隠しIMEは「幅2px の縦線」**：見た目の邪魔にならないよう `width: 2px` にしつつ、フォントサイズはマス高の60%に合わせて候補ウィンドウが読みやすいサイズに出るよう調整しています。

#### Claude との往復で磨かれた「質問力」

このセクションで痛感したのは、**Claude への質問の仕方が答えの質を決める**ということでした。

* 「IME ウィンドウを動かしたい」とだけ聞くと、`compositionstart` の教科書的な回答が返ってくる
* 「**縦書きで原稿用紙レイアウトの場合、隠し textarea がどこにあると変換候補がどこに出るか**」と**状況を具体的に切り分けて**聞くと、ブラウザ依存の挙動まで踏み込んだ答えが返ってくる

「何が問題か」を自分の言葉で切り分けて伝える力が問われた箇所で、**バイブコーディングの真骨頂**だったと思います。ここで磨かれた「状況分解＋具体質問」のスキルは、後の Marketplace 審査（英文の OAuth スコープ差し戻し）でも効いてきました。

### 3-3. 禁則処理（ぶら下げ＋追い出しの併用）

IMEの次に苦労したのがこれです。

行頭禁則文字（句読点・閉じ括弧に加えて、拗音・促音・長音・感嘆符なども含む）や行末禁則文字（開き括弧）を、縦書きの原稿用紙マス目上で正しく処理する必要がありました。

TateGakiでは、文字を1文字ずつ原稿用紙のマス（`p=ページ` / `c=列` / `r=行`）に配置していくループの中で、**その都度「禁則が発生するか」を判定**しています。

**禁則文字の定義**

```
// ===== 禁則処理 =====
// 行頭禁則：句読点・閉じ括弧・拗音・促音・長音・感嘆符など
const KINSHI_HEAD = new Set([...'。、．，！？）」』】〕〉》…‥ーっッゃャゅュょョぁァぃィぅゥぇェぉォ']);
// 行末禁則：開き括弧
const KINSHI_TAIL = new Set([...'（「『【〔〈《']);
```

`String.includes` ではなく `Set.has()` にしているのは O(1) 判定のためで、このアイデアはClaudeの提案でした。拗音（`っゃゅょ`）や長音（`ー`）まで行頭禁則に入れているのがポイントで、これがないと「こんにちは」が列をまたいだ瞬間に `ー` や `っ` が行頭に来て気持ち悪い縦書きになります。

**禁則の適用ロジック（ぶら下げ＋追い出しの併用）**

```
// 1文字ずつマスに配置していくループ内で、逐次禁則判定を行う

// --- 行頭禁則（ぶら下げ方式） ---
// 列の先頭に禁則文字が来そうなら、直前の文字と一緒に次の列に送る
if (r === 0 && !justNewline && KINSHI_HEAD.has(ch) && (c > 0 || p > 0)) {
  // 直前の実文字を探す（改行マーカーは飛ばす）
  let prevI = textToCell.length - 1;
  while (prevI >= 0 && textToCell[prevI].nl) prevI--;

  // 直前文字が前列の末尾にいた場合のみ処理
  if (prevI >= 0 && textToCell[prevI].r === rows - 1) {
    const prev = textToCell[prevI];
    const oldKey = `${prev.p}-${prev.c}-${prev.r}`;
    cellMap.delete(oldKey);

    // 直前文字を新しい列の先頭(r=0)に移動
    prev.p = p; prev.c = c; prev.r = 0;
    cellMap.set(`${p}-${c}-0`, prevI);

    // 禁則文字は続く r=1 に配置
    textToCell.push({ p, c, r: 1 });
    cellMap.set(`${p}-${c}-1`, i);
    r = 2;
    if (r >= rows) { r = 0; c++; if (c >= cols) { c = 0; p++; } }
    justNewline = false;
    continue;
  }
}

// --- 行末禁則（追い出し方式） ---
// 列の末尾に開き括弧が来そうなら、次の列の先頭に送る
if (r === rows - 1 && KINSHI_TAIL.has(ch)) {
  r = 0; c++;
  if (c >= cols) { c = 0; p++; }
}

// 通常の配置
textToCell.push({ p, c, r });
cellMap.set(`${p}-${c}-${r}`, i);
r++;
if (r >= rows) { r = 0; c++; if (c >= cols) { c = 0; p++; } }
```

**この実装のポイント**

* 行頭禁則は**ぶら下げ方式**（直前文字ごと次列に連れていく）
* 行末禁則は**追い出し方式**（次列の先頭に送る）
* 後処理パスではなく**配置ループ内で逐次判定**しているため、`textToCell` / `cellMap` の整合性も同時に保たれる
* `cellMap` のキーを `p-c-r` 文字列で管理することで、マス→文字インデックスの逆引きもO(1)

Claudeに「縦書きの禁則処理って、どう実装するのが一般的？」と聞き、**ぶら下げ方式**と**追い出し方式**の両方を併用する折衷案にたどり着きました。純粋な組版ライブラリよりも、原稿用紙マス目という制約下で「隙間を作らず、かつ禁則も守る」バランスを取っています。

### 3-4. ルビ（ふりがな）入力

ルビは縦書きの**親文字の右側**に小さく表示する仕様にしました。データ構造は、本文とルビを**別々に管理**しています。

* **`T`**：本文の文字列（ルビは含まない）
* **`RM`**：ルビマップ。`RM[i] = "かんじ"` のように、本文の i 番目の文字に対応するルビを持つスパースなオブジェクト
* **書き戻し時の記法**：`|漢字《かんじ》` のような独自記法で Docs にシリアライズ

この分離により、**本文の編集（文字挿入・削除）とルビの編集を独立して扱える**ようになっています。ルビ編集は本文に干渉せず、`RM[idx]` を書き換えるだけで済みます。

#### ルビ編集モーダル

3-1 で見た `rb.addEventListener('mousedown', ...)` からこの `openRuby(idx)` が呼ばれ、オーバーレイモーダルでルビを編集します。

[![03_ルビ入力.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4412612%2F5d4cc858-6299-4716-b8a1-7ff3ffb84ef6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4a805e3b7b5b99e03ddef9cd554ef7a6)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4412612%2F5d4cc858-6299-4716-b8a1-7ff3ffb84ef6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4a805e3b7b5b99e03ddef9cd554ef7a6)  
*キャプション*：ルビ編集モーダル。親文字のマス右側にあるルビ欄をクリックするとこのオーバーレイが開き、ふりがなを入力できる。

```
// ===== RUBY =====
// モーダルを開く（親文字インデックス idx を指定）
function openRuby(idx) {
  if (idx >= T.length) return;
  editRI = idx;                                        // 編集中の親文字インデックスを保持
  document.getElementById('rT').value = T[idx];        // 親文字を表示（読み取り専用）
  document.getElementById('rI').value = RM[idx] || ''; // 既存ルビを初期値に
  document.getElementById('rubyOv').classList.add('show');
  setTimeout(() => document.getElementById('rI').focus(), 50);
}

// 確定：ルビを保存（空文字なら削除扱い）
function applyRuby() {
  const v = document.getElementById('rI').value.trim();
  pushHistory();                                       // Undo/Redo のためスナップショット
  if (v) RM[editRI] = v; else delete RM[editRI];
  closeRuby(); render();
}

// 削除：ルビを明示的に消す
function removeRuby() {
  pushHistory();
  delete RM[editRI]; closeRuby(); render();
}

function cancelRuby() { closeRuby(); }

function closeRuby() {
  document.getElementById('rubyOv').classList.remove('show');
  editRI = -1;
  // プレーンモード以外なら、本文入力用の隠しIMEにフォーカスを戻す
  if (!$m.value.startsWith('plain')) focusIME();
}

// キーボード操作：Enterで確定、Escapeでキャンセル
document.getElementById('rI').addEventListener('keydown', (e) => {
  if (e.key === 'Enter')       { e.preventDefault(); applyRuby(); }
  else if (e.key === 'Escape') cancelRuby();
});

// オーバーレイ背景クリックでキャンセル
document.getElementById('rubyOv').addEventListener('mousedown', (e) => {
  if (e.target.id === 'rubyOv') cancelRuby();
});
```

#### 細部のこだわり

* **`pushHistory()` を保存/削除の直前に呼ぶ**：ルビ編集も Undo/Redo 対象にするため。これを忘れると「Ctrl+Z しても戻らない」バグになる
* **空文字の確定は「削除」扱い**：ユーザーがルビを消したいときに、わざわざ「削除ボタン」を押さなくても空のEnterで消せる
* **`focusIME()` で本文入力に復帰**：モーダルを閉じた直後、カーソルが本文側に戻るので、続きが自然に入力できる
* **`setTimeout(..., 50)` でフォーカス**：モーダル表示直後の `focus()` はCSSのtransitionと競合することがあるので、1フレーム遅らせて確実にフォーカス
* **オーバーレイ背景クリックでキャンセル**：`e.target.id === 'rubyOv'` でちゃんと背景クリックのみを拾う（モーダル内部をクリックしても閉じない）

最初は「ルビ入力フォームを本文と同じエディタ内に置く」設計だったのですが、Claudeに「モーダルで隔離した方が状態管理がシンプル」と提案されて変更しました。確かに `editRI` 一つ持つだけで済んで、本文とルビのイベント競合も起きません。

#### 次の課題：書き戻し時のシリアライズ

編集中は `T` と `RM` を分けて持っていますが、Google Docsへの書き戻し時は一本の文字列にまとめる必要があります。ここで独自記法 `|漢字《かんじ》` を使い、本文と逆変換できる形で保存しています（詳細は **3-5** で）。

### 3-5. Google Docsへの書き戻し（テーブル方眼方式）

縦書きした内容を「Google Docsのファイル」として保存する必要がありました。**Google Docs自体には縦書き機能がない**ため、次の方針を採用しています。

> **Docs のテーブル機能を使って「1セル＝1文字」の擬似縦書きDocsを生成する**

印刷・配布・原稿管理には十分実用的です。

#### ページ向きの自動切替

400字詰め（20×20マス）は横向きA4、200字詰め（10×20マス）は縦向きA4が自然なので、mode別に自動で切り替えています。

```
if (mode === '400') {
  body.setPageWidth(842);  body.setPageHeight(595);   // 横向きA4
} else {
  body.setPageWidth(595);  body.setPageHeight(842);   // 縦向きA4
}
body.setMarginTop(36);  body.setMarginBottom(36);
body.setMarginLeft(36); body.setMarginRight(36);
```

#### 列の反転（最大のハマリポイント）

縦書きの列は**右から左**へ流れますが、Docsのテーブルは**左から右**に並びます。そのまま書き出すと「文章が鏡文字もどきに読めなくなる」ので、列インデックスを反転してから配置します。

```
for (var tCol = 0; tCol < cols; tCol++) {
  // 縦書き列 → テーブル列の変換（右→左 を 左→右に反転）
  var tableCol = (cols - 1) - tCol;
  var colData = pageData[tCol]; // colData[row] = { char, ruby }

  for (var r = 0; r < rows; r++) {
    var cellData = colData[r];
    var cell = table.getRow(r).getCell(tableCol);
    // （後述のセル配置処理）
  }
}
```

これ、最初分からず「書き出したら文章が逆に読める」バグで半日溶かしました。Claudeに「縦書きの列順序を Docs のテーブルに流し込むときの注意」と聞いてやっと気づいた経緯があります。

#### 1セル＝1文字の配置

空のテーブルを `appendTable(cells)` で作ってから、セルごとに1文字ずつ流し込みます。セルのパディングを最小にして、**マス目が詰まって見える**ように調整しています。

```
var table = body.appendTable(cells);
table.setBorderColor(borderColor);
table.setBorderWidth(borderWidth);

for (var tc = 0; tc < cols; tc++) {
  table.setColumnWidth(tc, colWidth);   // 列幅を均等に
}

// セルにテキストを配置
var cell = table.getRow(r).getCell(tableCol);
cell.setPaddingTop(0);   cell.setPaddingBottom(0);
cell.setPaddingLeft(1);  cell.setPaddingRight(1);
cell.setVerticalAlignment(DocumentApp.VerticalAlignment.MIDDLE);
cell.clear();

if (cellData.char && cellData.char.length > 0) {
  var charPara = cell.appendParagraph(cellData.char);
  charPara.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  var charText = charPara.editAsText();
  charText.setFontSize(fontSize);
  charText.setForegroundColor('#000000');
  if (fontName) charText.setFontFamily(fontName);
  charPara.setSpacingBefore(0);
  charPara.setSpacingAfter(0);
  charPara.setLineSpacing(1.0);

  // cell.appendParagraph は最初の空パラグラフを残すので削除
  if (cell.getNumChildren() > 1) {
    var firstChild = cell.getChild(0);
    if (firstChild.getType() === DocumentApp.ElementType.PARAGRAPH &&
        firstChild.asParagraph().getText() === '') {
      cell.removeChild(firstChild);
    }
  }
}
```

#### GAS 特有の落とし穴

実装中、地味に時間を溶かしたポイント：

* **`cell.appendParagraph` は最初の空段落を残す**：テーブルセルは生成直後に空の段落を1つ持っていて、`appendParagraph` で文字を追加してもその空段落は残ったまま。結果、マス内に「空行＋文字」で上に寄って見える。明示的に `removeChild` する必要あり
* **`cell.clear()` では段落は消えない**：テキスト内容しか消せない。構造自体を空にするなら `removeChild` で個別に削る
* **列幅・行高の制約**：GAS APIで指定できるのは列幅のみ。行高はセル内容の高さに追従するので、パディングを0にしないとマス目がガタガタになる
* **フォントの安全値**：GAS側で指定できる和文明朝体は実質 `Noto Serif JP` ぐらい。それ以外は Docs 側で置換されるため、ユーザーが選んだフォントの名前に `Noto Serif` が含まれるかでフィルタしている

#### 複数ページ対応

ページをまたぐときは `appendPageBreak` を挟んで、各ページ末尾に「N / M 頁」を表示しています。

```
for (var pi = 0; pi < exportData.pages.length; pi++) {
  if (pi > 0) body.appendPageBreak();
  // （上記のセル配置ループ）
  if (exportData.pages.length > 1) {
    var pageNum = body.appendParagraph(
      (pi + 1) + ' / ' + exportData.pages.length + ' 頁'
    );
    pageNum.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
    pageNum.editAsText().setFontSize(8).setForegroundColor('#999999');
  }
}
```

#### ルビの書き戻しは？

**現状、Docsテーブル方式ではルビは書き戻していません**。Google Docsに縦書きのルビに相当する機能がなく、脚注・括弧書き・上付き文字のいずれも縦書きとの相性が悪いため、**「本文のみDocsに書き戻し、ルビは TateGaki 専用の JSON 保存で保持」**という割り切りにしています（JSON 保存は次の 3-6 で）。

Claudeとも「Docs にルビを表現する方法」を何度か議論しましたが、最終的には「縦書きのものは縦書きで扱う」のが一番素直だと落ち着きました。

### 3-6. Google Drive に JSON 直接保存（ローカルレス設計）

TateGaki はアドオンなので、ユーザーのローカルファイルシステムにはアクセスできません。そこで「保存先は常に Google Drive」に絞り、**マイドライブ直下に `TateGaki` フォルダを自動生成 → そこに JSON で本文・ルビ・設定を丸ごと保存**する設計にしました。

#### Drive Advanced Service で最小権限

`DriveApp` ではなく **Drive Advanced Service**（`Drive.Files`）を使うことで、`drive.file` スコープ（アプリが作ったファイルのみアクセス）で済み、ユーザーの Drive 全体を読みにいく必要がありません。Marketplace 審査でも OAuth スコープの厳しさを実感したので、ここは最小権限に振り切って正解でした。

```
/**
 * マイドライブ直下の「TateGaki」フォルダを取得 or 作成
 * @return {string} フォルダID
 */
function getOrCreateTategakiFolder() {
  var props = PropertiesService.getUserProperties();
  var folderId = props.getProperty('tategakiFolderId');

  if (folderId) {
    try {
      var folder = Drive.Files.get(folderId, { fields: 'id,title,labels' });
      if (!folder.labels.trashed) {
        return folderId;
      }
    } catch (e) {
      // フォルダが削除されている場合は再作成
    }
  }

  // 新規作成
  var newFolder = Drive.Files.insert({
    title: 'TateGaki',
    mimeType: 'application/vnd.google-apps.folder'
  });
  props.setProperty('tategakiFolderId', newFolder.id);
  return newFolder.id;
}
```

ポイントは `PropertiesService.getUserProperties()` にフォルダIDをキャッシュしていること。毎回 Drive を検索しなくて済みます。**ただし「ユーザーがフォルダをゴミ箱に入れる」ケースがある**ので、`labels.trashed` を見て再作成にフォールバックしています。この小さな防衛で「セーブしようとしたらエラー」クレームが防げました。

#### 保存：新規または上書き

```
function saveToGoogleDrive(data) {
  var json = data.json;
  var fileName = data.fileName || generateFileName();  // tategaki_YYYYMMDD_HHmm.json
  var blob = Utilities.newBlob(json, 'application/json', fileName);

  if (data.fileId) {
    // 既存ファイルの上書き
    try {
      var updated = Drive.Files.update({}, data.fileId, blob);
      return { fileId: updated.id, fileName: updated.title, message: '保存しました' };
    } catch (e) {
      // ファイルが見つからない場合は新規作成にフォールバック
    }
  }

  // 新規作成（TateGakiフォルダに保存）
  var folderId = getOrCreateTategakiFolder();
  var newFile = Drive.Files.insert(
    { title: fileName, mimeType: 'application/json', parents: [{ id: folderId }] },
    blob
  );
  return { fileId: newFile.id, fileName: newFile.title, message: '保存しました' };
}
```

**上書きに失敗したら新規作成にフォールバック**するのが細かいポイントです。ユーザーが保存したファイルを別端末で削除していたケースでも、そのまま新しいファイルとして保存され、データが消えません。

#### 一覧・読込・削除

CRUD の残りは標準的な Drive API の使い方です。`listTategakiFiles()` でフォルダ内の JSON 一覧を更新日順で返し、`loadFromGoogleDrive(fileId)` で `UrlFetchApp` 経由で中身を取得、`deleteFromGoogleDrive(fileId)` で `Drive.Files.trash` でゴミ箱行き、という構成です。

この「Driveアクセスを最小権限＋固定フォルダ」の割り切りも Claude の提案で、**「ファイル選択UI」を実装しなくてよくて、開発スコープが大幅に縮まりました**。アプリ特有のフォルダを作ってしまえば、Marketplace 審査の OAuth スコープ説明もシンプルになります。

---

## 4. アーキテクチャ概要

ポイントは **`Code.js` 一本がサーバ側、`dialog.html` + `script.html` + `style.html` の3ファイルがクライアント側** という素朴な二層構造です。サイドバーではなく **`showModelessDialog`**（モーダレスダイアログ）を使っているのは、原稿用紙レイアウトを広く表示したかったため。HTMLサービスの `include()` で複数の `.html` を1つのダイアログに連結しています。GASの「サーバ側」と「クライアント側」の役割分担は、Claudeに何度も説明してもらってようやく腑に落ちました。

---

## 5. 工夫したこと

### 5-1. 設計書を先にClaudeに書かせる

いきなり実装するとぐちゃぐちゃになるので、**まずClaudeに設計書（仕様書）を書かせて、私がレビューする**スタイルを取りました。

* 機能一覧
* 画面遷移
* データ構造
* エラーハンドリング方針

この設計書をNotionに保存し、実装中も常に参照できるようにしました。

### 5-2. 小さく作って都度動かす

「縦書き全機能を一気に作る」のではなく、段階的に拡張しました。

1. まず1行だけ縦書き表示
2. 複数行に対応
3. 原稿用紙のマス目を描画
4. 禁則処理を追加
5. ルビ対応
6. 保存機能

Claudeに「まずこの1機能だけ動くコードを書いて」と頼むのがコツです。

### 5-3. Marketplace審査の落とし穴

公開申請時の審査で、以下の点を指摘されました。

* **プライバシーポリシーの明記**：OAuthスコープごとの用途を具体的に書く必要がある
* **ブランドロゴ**：128×128pxなど複数サイズのアイコンが必要
* **スクリーンショット**：Marketplace掲載用に複数枚
* **利用規約**：英語版も必須ではないが、あると審査がスムーズ

Claudeに「Google Workspace Marketplaceの審査でよく指摘される点を教えて」と聞いて、**事前に対策リスト**を作ったのが効きました。

---

## 6. バイブコーディングをやってみて

非エンジニアがAIとペアプロするうえで、実感した3つのこと。

1. **日本語で仕様を説明する力が一番大事**

   コードが書けなくても、「こうしたい」を明確に言葉にできればAIが実装してくれます。
2. **エラーメッセージをそのままAIに貼る**

   スタックトレースをClaudeに投げると9割は解決します。
3. **小さく区切って確認する**

   一度に大量のコードを生成させると詰みます。100行ずつくらいがちょうど良かったです。

---

## 7. これから

TateGakiはまだ公開したばかりで、ユーザーもレビューもこれからです。現在は無料公開していますが、今後は有料版（高度な組版機能、EPUB出力など）も検討しています。

「Google Docsで縦書きしたい」という方、ぜひ使ってみていただけると嬉しいです。

---

## おわりに

コード未経験でも、AIと対話しながら本気で作れば、Marketplaceに公開できるプロダクトが作れる時代になりました。

「自分には無理」と思っている方の背中を、少しでも押せたら嬉しいです。

最後までお読みいただきありがとうございました♪
