---
id: "2026-05-05-半月かけて作ったnote自動投稿スクリプトがある日突然死んだ話-browser-use-と-play-01"
title: "半月かけて作ったnote自動投稿スクリプトが、ある日突然死んだ話 — browser-use と Playwright の使い分けで学んだこと"
url: "https://note.com/st_dev0/n/n2975c219c40a"
source: "note"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "note"]
date_published: "2026-05-05"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## 「ツール選定は実装でぶつかってから変える」をリアルに体験した4時間+の修羅場

先月、半月くらいかけて、note の自動投稿スキルを作りました。Markdown1ファイルから、ログイン・本文流し込み・サムネアップロード・挿絵挿入・CTAバナー3箇所配置・下書き保存まで、ターミナルで1コマンドで完了するスキルです。1325行の Python スクリプトで、自分でも結構気に入っていました。

数記事は問題なく動きました。ところが昨日、急に動かなくなりました。

タイトルとサムネだけ入った、本文0文字の空ドラフトが量産される、という形でです。気付いたときには下書きが5件以上、白紙状態で並んでいました。

しかも皮肉なことに、私はそのとき **「note自動投稿スキルを作った話」を Substack で配布する企画記事** を書いていました。「自動化スキルを配ります」という記事を書きながら、その自動化が壊れる。コントみたいな話です。

そこから4時間以上かけて原因を調査し、最終的に **browser-use CLI 2.0 → Playwright Python SDK** に書き直して復旧しました。書き直した結果、1037行（22%減）になり、テストも全項目パスしました。

今日はその顛末と、そこで得た「ブラウザ自動化ツールはサイト別に使い分ける」という結論を、できるだけ赤裸々に書いておきます。同じツールで消耗している誰かの一助になれば、と。

[![](https://assets.st-note.com/img/1777942245-aBNhs6QWdkEv2Xw9IHF5iJtl.png?width=1200)](https://www.fyve.co.jp/ai-advisor/intro)

活用について個別にご相談いただけます。  
→ AI業務効率化のスポット相談（30分 ¥6,000〜・初回限定）

## 1ヶ月前: なぜ browser-use CLI 2.0 を採用したか

時計を1ヶ月前、2026年4月に戻します。

ブラウザ自動化ツールとして当時注目されていたのが browser-use の CLI 2.0 でした。AI native なブラウザ自動化、つまり **「自然言語で指示すれば、LLMがDOMを解釈してブラウザを操作してくれる」** という代物です。

私が browser-use に惹かれた理由はシンプルでした。

* 自然言語で操作指示を書ける（セレクタを書かなくていい）
* DOM変化に追従するので、サイトのUI変更に強い
* 未知のサイトでもLLMがその場で構造を読んで動ける
* 私の「複雑さ排除」哲学に合う（高レベル抽象、自分で泥臭いコードを書かなくていい）

実際、note の自動投稿は browser-use で1ヶ月安定して動いていました。だから「これは正しい選択だった」と思っていたんです。1ヶ月後にその信頼が裏切られるとも知らずに。

## 構築した note 自動投稿スキルの中身

書いていたスクリプトは、概ねこんな構成でした。

* **マーカー記法**: 記事Markdown中に <!-- IMAGE: 説明 --> <!-- CTA: top|middle|bottom --> というHTMLコメントを置くと、自動投稿スクリプトがその位置に画像・バナーを差し込む
* **3戦略の本文挿入フォールバック**: synthetic ClipboardEvent → execCommand insertHTML → innerHTML + input event を順番に試す
* **CTAバナー自動配置**: バナー画像 + 配置位置別キャプション + リンク設定までを一括処理
* **下書き保存 or 公開**: コマンド引数で切り替え

合計1325行、それなりに作り込んだつもりでした。書いた直後の数記事は、本当に1コマンドで note 投稿が完了して、感動していました。

## 突然壊れた日 — 2026年5月4日

事件は昨日（5月4日）起きました。

いつも通りターミナルで投稿コマンドを叩いたら、note の編集画面までは開く。タイトルとサムネは入る。**でも本文が空**。試しに何度か走らせると、下書きフォルダに白紙ドラフトが5件並びました。

ログを見ると、本文挿入の3戦略すべてが silently fail していました。

* synthetic ClipboardEvent で paste 発火させる戦略 → 失敗
* document.execCommand('insertHTML', ...) 戦略 → 失敗
* innerHTML 直接書き換え + input event 発火 → 失敗

挿絵もCTAバナーも全滅。タイトルとサムネだけ入った骸骨ドラフトが量産される、という見事な惨状でした。

そして、私の memory ファイルに残っていた一行を思い出しました。

> 「Substackエディタはpbcopy+Cmd+V経由でのみ動く」（過去のフィードバック）

これと **同じ症状**が、note にも遅れて到来したのでした。

## 4時間+のデバッグ日記

ここから泥沼に入ります。同じ症状を3回繰り返すと、人間は判断力を失うんですよね。

### 仮説1: プロセス競合？

「もしかして browser-use の裏でプロセスが競合してる？」と思って、関連プロセスを片っ端から kill しました。Chromium を全終了。プロファイルディレクトリをリセット。再実行。**変わらず**。

### 仮説2: note 側の仕様変更？

「note のエディタ、何か変わったのでは」と思ってブラウザで手動操作して観察しました。確かに、エディタの reconciler の挙動が以前と微妙に違う気配がする。でも、何が変わったかは特定できない。

### 仮説3: JavaScript injection の根本問題？

ここでようやく正解の手前まで来ます。「JavaScript で合成イベントを発火させても、note の React/ProseMirror が userActivation を要求していて、合成イベントを弾いている説」。

これが正解でした。が、当時の私はまだ確信が持てず、3つの戦略を順番に試しては失敗、を繰り返していました。同じ症状の繰り返しで脳が固まる、という典型的な状態です。

### 4時間ロスして気付いたこと

「**これは私の問題じゃなくて、ツールの構造的な問題かもしれない**」と疑うのが遅すぎました。後で振り返ると、30分試して同じ症状を3回見た時点で抜本調査に切り替えるべきだったんです。

これは今後の自分への教訓です: **同じ症状を3回見たらツールを疑え**。

[![](https://assets.st-note.com/img/1777942263-WqEX2RaLwlZC4ptjF3ODfmbH.png?width=1200)](https://www.fyve.co.jp/ai-advisor/intro)

「AIで何ができるか分からない」「興味はあるが業務に活かせていない」  
── そんな方は、まず1回お話ししてみませんか。  
→ AI業務効率化のスポット相談（30分 ¥6,000〜・初回限定）

## claude-in-chrome MCP への寄り道で見えたヒント

「JavaScript injection が根本原因かも」と疑い始めたタイミングで、Anthropic 公式の claude-in-chrome MCP を試しました。

これは、私が普段使う Chrome をそのまま操作できる MCP です。**ヘッドレスブラウザではなく、実セッションを操作する**ので、本物のユーザー操作と区別がつかない。「これなら userActivation が降りるはず」という仮説でした。

結果は **部分成功** でした。

* ✅ 本文挿入が一発で成功（4650文字、document.execCommand('insertHTML') で）
* ❌ ファイルアップロードは全パスで -32000 "Not allowed" エラー
* 原因: claude-in-chrome MCP のサンドボックス層が file\_upload を弾いている

つまり、**本文は入るけど画像が入らない**。サムネ・挿絵・CTAバナーが全部手動配置になる。これでは自動化として未完です。

ただ、この寄り道で得た知見は大きかった。

「**ProseMirror エディタを突破するには、本物のキーボードイベント or execCommand insertText が必要**」という核心に届いたんです。

## 抜本調査 — Playwright が再評価される理由

![](https://assets.st-note.com/img/1777942234-usPTE2jS5YJFhkVblXMwGrCA.png?width=1200)

ここで私は4時間以上のデバッグを止めて、抜本調査に切り替えました。「ブラウザ自動化ツール、2026年現在の本当のベストプラクティスは何か」を改めて30分かけて調べました。

主要ファクトは以下です。

### ① browser-use 自身が Playwright を捨てていた

驚いた事実が一つ。browser-use は2025年末に **「Playwright をやめて CDP（Chrome DevTools Protocol）直叩きに移行した」** と公式ブログで発表していました。理由はラッパー層がパフォーマンスと信頼性のボトルネックだから、と。

これは何を意味するかというと、**「AI native ツールも結局、原始的な CDP に戻る」**という業界トレンドです。Playwright は古いと思われがちですが、その下のレイヤーが結局正解だった、という構図です。

### ② ProseMirror 突破策の確定解

調査して確信したのが、document.execCommand('insertText', false, text) だけが ProseMirror の beforeinput を native 発火するため、note / Substack / Notion / Linear / Confluence で動く確定解だ、ということ。

これは合成イベントでは絶対に出せない挙動です。

### ③ Playwright の set\_input\_files() は CDP 直叩き

page.set\_input\_files() は Wrapper 層を経由せず、CDP の DOM.setFileInputFiles を直接叩きます。だから claude-in-chrome MCP で起きた Not allowed エラーは出ない。

### ④ keyboard.press('Meta+V') はハードウェアレベル相当

Playwright の keyboard event は CDP の Input.dispatchKeyEvent で送られるので、**user-initiated として扱われる**。これによって navigator.clipboard の権限ゲートも通過します。

調査の結論はシンプルでした: **同じサイトを毎日叩く決定論タスクは、Playwright Python SDK 直叩きが2026年の最適解**。

## Playwright で書き直した結果

腹をくくって、note 投稿部分だけを Playwright Python SDK で書き直しました。1ヶ月前のスクリプト全体を捨てるのではなく、**壊れた部分だけ書き直す**方針です。

### 規模の変化

### テスト結果（全項目PASS）

書き直した直後のテストでは:

* ログイン（永続プロファイル）✅
* 本文挿入（4544文字 / クリップボード paste 経由）✅
* サムネアップロード（file\_chooser + crop保存）✅
* 挿絵 × 2（H2位置に挿入）✅
* CTAバナー × 3（画像 + キャプション + リンク）✅
* 全CTAリンク3本検証 ✅

書き直しに踏み切ってから、テスト成功までは約4時間でした。半月かけて作ったものを4時間で書き直したことになります。

## 7つの非自明ノウハウ — Playwright実装で詰まったところ

書き直しの過程で、ドキュメントには載っていない、実際にぶつかってから分かるノウハウが7つありました。同じ実装をする人のために残しておきます。

### ① page.expect\_file\_chooser() が正解

note のファイルアップロードボタンは、React popover 内で動的生成される input です。set\_input\_files のセレクタで先回り捕捉しようとしても、まだDOMに存在しない瞬間があるため失敗します。

代わりに、**ネイティブダイアログを横取りする** expect\_file\_chooser を使います。

```
with page.expect_file_chooser() as fc_info:
    page.click('text=画像')
file_chooser = fc_info.value
file_chooser.set_files(image_path)
```

これで「メニューから画像を選択 → ネイティブダイアログ表示 → ファイルパス送信」が一発で通ります。

### ② クリップボード paste が ProseMirror 突破策

note の本文（ProseMirror）は、合成 paste イベントを黙殺します。突破策は **クリップボードに書き込んでから物理 Cmd+V を送る** こと。

```
context.grant_permissions(['clipboard-write'], origin='https://editor.note.com')
page.evaluate('''
  navigator.clipboard.write([
    new ClipboardItem({"text/html": new Blob([html], {type: "text/html"})})
  ])
''')
page.keyboard.press('Meta+V')
```

Playwright の keyboard event は CDP-direct なので user-initiated 扱い → ProseMirror の権限ゲートを通過します。

### ③ 物理 mouse.click(x, y) が Range/Selection JS より確実

挿絵を H2 直後に入れるとき、JS で Selection を作ってカーソル配置しようとしました。**ProseMirror の reconciler が JS-set selection を黙殺**するため、これが効きません。

正解は、bounding-rect の右端を物理マウスでクリック → End キーで行末確定。

```
rect = h2.bounding_box()
page.mouse.click(rect['x'] + rect['width'] - 5, rect['y'] + rect['height'] / 2)
page.keyboard.press('End')
```

これで確実にカーソルが該当位置にコミットされます。

### ④ 図 id 追跡が必須

挿絵を複数枚入れるとき、figures.last で「最後に入った図」を取ろうとすると詰みます。**後続挿入で位置が変わるため、last が指す対象がズレる**んです。

私は「挿入前後で Set<figure id> を diff して新規 figure を特定」する方式に変えました。

```
before_ids = set(page.eval_on_selector_all('figure[id]', 'els => els.map(e => e.id)'))
# ... 挿絵挿入処理 ...
after_ids = set(page.eval_on_selector_all('figure[id]', 'els => els.map(e => e.id)'))
new_id = (after_ids - before_ids).pop()
```

これでどの操作がどの図に対するものか、確実に追跡できます。

### ⑤ figure[id="..."]（属性セレクタ）を使う

CSS の figure#id 形式は、id にハイフンや特殊文字が含まれると escape 問題で詰みます。**属性セレクタ figure[id="xyz-abc"] ならその問題を回避**できます。

地味ですが、これに気付かないとデバッグで1時間溶けます。

### ⑥ caption-before-link + verification 検証パス

CTAバナーは「画像 → キャプション入力 → リンク設定」の3段階ですが、**初回 CTA でリンクが silently fail することがある**んです。エラーは出ない、でもリンクは付いていない。

なので、最終スキャンで「figcaption に『¥6,000』を含む figure はリンクが付いているか」を検証して、欠けていれば自動再付与する verification パスを入れました。

### ⑦ note のリンクUIは textarea + 適用ボタン

これは小ネタですが、note のリンク設定UIは <input> ではなく <textarea placeholder="https://"> で、Enterではなく <button>適用</button> をクリックする必要があります。

API ドキュメントを読むだけでは分からない、画面を見て初めて気付くタイプの仕様です。

## 結論: browser-use と Playwright を「サイト別に」使い分ける

書き直しが完了して、改めて整理した結論はこれです。

### ❌ NG パターン: 1スクリプト内で混在させる

browser-use と Playwright を同じスクリプトに混ぜると、セッション管理が複雑化してデバッグ地獄になります。プロファイル・cookie・プロセス競合、すべて二重管理。これはやらない方がいい。

### ✅ OK パターン: スキル単位でツールを選ぶ

私の現在のスキル構成はこうなりました。

* note-article → **Playwright**（ProseMirror + ファイルUP）
* substack-article → **Playwright**（後日書き直し検討）
* x-article → **browser-use**（普通のフォーム、AI native の強み活きる）
* coconala-listing → **browser-use**（フォーム + 通常UI）
* 業種特化スクレイピング → **browser-use**（未知サイトのDOM解釈が強い）

### どっちを選ぶかの判断軸

**Playwright を選ぶ場面:**

* React/ProseMirror 系リッチエディタ（note / Substack / Notion / Linear / Confluence / Medium / Ghost）
* Hidden file input へのアップロード
* ネイティブキーイベント要求の操作
* 同じサイトを毎日叩く決定論タスク（実行速度・コスト・信頼性）

**browser-use 2.0 を選ぶ場面:**

ざっくり言うと、**毎日同じサイトを叩くなら Playwright、未知サイトを毎回違う指示で動かすなら browser-use**、という棲み分けです。

### 1ヶ月前の判断は間違っていなかった

ここが重要なポイントです。「browser-use を採用した1ヶ月前の判断はミスだったのか？」と聞かれると、**ノー**です。

browser-use 2.0 自体は依然として優秀なツールです。「現代的リッチエディタには合成イベントが効かない」というエッジケース知見が抜けていただけ。なので、スキル全体を捨てて作り直すのではなく、**note まわりだけ書き直し**で済んでいます。

ツール選定は「実装でぶつかってから変える」で正解だったわけです。最初から Playwright を選んでいたら、AI native の便利さを1ヶ月体験せずに終わっていました。

## メタ的な学び — 4時間消耗して得たもの

最後に、技術的な話を超えて、私が得たメタ的な学びを残します。

### ① ツール選定は「ぶつかってから」変える

完璧な事前調査をして決定的なツールを最初から選ぶ、というのは現実的に無理です。1ヶ月前の判断で予期できないエッジケースは絶対に存在する。

ぶつかったら抜本調査 → 適材適所で書き直し、で十分。「全部捨ててやり直し」ではなく「壊れた部分だけ書き直し」を選ぶ判断が、結果的に時間を節約します。

### ② AI native ツールにも限界がある

browser-use の自己修復能力は本当に強いです。でも、**user activation を必要とするフレームワーク（React/ProseMirror）には届かない**。これは LLM がどれだけ賢くても、ブラウザのセキュリティ層が JS コンテキストに対して降ろしてくれない権限の話だからです。

「LLMが解釈する層」と「ブラウザが実行する層」の間に、原理的な隙間がある、ということを覚えておくと、似た詰まりに高速で気付けます。

### ③ 4時間の試行錯誤は無駄じゃない

これも今振り返って思うことです。claude-in-chrome 経由で execCommand が通った経験が、ProseMirror 突破策の発見に直結しました。失敗の積み重ねが「次に何を試すべきか」の判断軸になる。

ただし、**抜本調査は早めに**入るべきです。私の場合、4時間以上デバッグして同じ症状を繰り返してから抜本調査に入りました。理想は30分試したら一度ステップバックする。

### ④ AI native vs deterministic の使い分け

これが一番大きな学びかもしれません。

これを意識的に使い分けると、トークン課金 + 信頼性の両方が最適化されます。AI native ツールは「未知への対応」に強みがあるので、毎日同じ作業に使うのはオーバースペックなんです。

## 同じ消耗をしている人へ

最後に、もしあなたがいま browser-use や類似のAI native ブラウザツールを使っていて、note や Substack や Notion で「合成イベントが効かない」「画像アップロードが通らない」と消耗していたら、伝えたいことがあります。

それはあなたのコードのせいじゃありません。ツールの構造的な限界に当たっています。

具体的にやることは3つだけです。

1. **症状を3回繰り返したら、ツールを疑う**: 自分のコードを直す前に、抜本調査に切り替える
2. **リッチエディタ部分だけ Playwright に書き直す**: 全部書き直す必要はない、その部分だけでいい
3. **pip install playwright && playwright install chromium**: これが最初の一歩

私は半月かけて作ったものを、4時間で部分的に書き直して復旧しました。書き直したコードは1037行で、テストも全部通っています。

「動くものを作る」と「動き続けるものを作る」の間には、こういう実体験を積まないと埋まらない溝があります。私は今回その溝を1つ埋めました。あなたも同じ溝にぶつかったら、この記事のことを思い出してもらえればと思います。

ちなみに、この記事自体は **書き直したばかりの Playwright 版スキルで投稿されています**。動くことを確認しないと記事として書けないので、ある意味では一番厳しいテストでした。今あなたが見ているサムネ・挿絵・3箇所のCTAバナーは、ターミナル1コマンドで自動配置されたものです。

「動くもので語る」、それが私のスタイルです。

[![](https://assets.st-note.com/img/1777942280-vOtbeMLQ54PlnIH1qr73wm0j.png?width=1200)](https://www.fyve.co.jp/ai-advisor/intro)

今回の話を「自分の業務に落とし込みたい」と思ったら、  
30分の対話から、専門家と進め方を見極められます。  
→ AI業務効率化のスポット相談（30分 ¥6,000〜・初回限定）
