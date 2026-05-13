---
id: "2026-05-11-claude-code開発者が語るmarkdownでは読まれないhtmlで出せ-01"
title: "Claude Code開発者が語る「Markdownでは読まれない。HTMLで出せ」"
url: "https://qiita.com/daisuke-nagata/items/c5c5109bad01e6ff5dfc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "GPT"]
date_published: "2026-05-11"
date_collected: "2026-05-13"
summary_by: "auto-rss"
query: ""
---

**この記事の HTML 版:** https://html-effectiveness-jp.vercel.app/

> 文字を全部読むのはきつい、という人はまず HTML 版から開いてください。Qiita 版は Markdown の制約でこの見た目を再現できません(理由は本文中で自己実証しています)。

> **この記事の想定前提**
> Claude Code をすでに導入していて、「もっと業務でうまく使いこなしたい」と思っている人向けの記事です。`/init` の打ち方から学ぶ入門ではなく、すでに毎日のように呼んでいて、依頼の出し方やプロンプトの工夫で成果物の質を上げたい人を想定しています。エンジニアでなくても、PdM・編集者・企画・経営企画など、Claude Code に頼んだ出力を社内で配る立場でAIで出力した内容を読んでもらいたい方におすすめ。

---

### この記事を **読みやすい HTML 1 枚もの** で開く



**HTML 版:** [html-effectiveness-jp.vercel.app](https://html-effectiveness-jp.vercel.app/)

Qiita(Markdown ベースのプラットフォーム)は記事保存時に生 HTML の `style` 属性をほぼ全て削除します。だからこのページでは色も影もアクセントも出ません。HTML の本来の表現は、URL を直接ブラウザで開いてもらう方式でないと届かない ─ それ自体が本記事の主張の自己実証です。

---


「AIの文章、長すぎて結局ちゃんと読んでないんですよね」

これ、かなり本質だと思っています。

Claude Code に毎月それなりの金額を払っている。
でも、返ってきた長い Markdown をちゃんと読んでいない。
自分が読んでいない資料を、チームの誰かが読んでくれるわけもない。

結果として、

「AIを使っている」
けど、「成果物として使われていない」という状態になる。

そこで最近かなり効いたのが、Claude Code への依頼の最後にこれを付けることです。

> HTMLで出して

これだけです。

きっかけは、Anthropic で Claude Code 本体を作っている **Thariq Shihipar** 氏の発信でした。彼は、Claude Code の出力として Markdown ではなく HTML を使うことの有効性を紹介しています。要するに、Claude Code を作っている側の人が「Markdown だけでは足りない」と言い始めている。

これは小技ではなく、出力の設計の話です。

Markdown は記録には向いています。
でも、人に読ませる資料、比較して判断してもらう資料、Slack で共有してそのまま見てもらう資料には弱い。

HTML にすると、色、レイアウト、カード、表、ボタン、図解、モバイル対応まで含めて、Claude Code が「読まれる形」にして返してくれます。

この記事では、なぜ Claude Code の出力を HTML にすると成果物の質が変わるのかを、日本の業務現場で使える形に落として整理します。

### 補足: 一次ソースと、入力との切り分け

- 出典: 2026 年 5 月、Anthropic Claude Code チーム所属 Thariq Shihipar 氏 "Using Claude Code: The Unreasonable Effectiveness of HTML"。Simon Willison が同日取り上げて業界に波及。
- Companion site: [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/) に Claude Code が生成した HTML 20 例が並んでいる。手触りを確かめたい人はここを開いてから読むと早い。
- 入力は別軸: Anthropic 公式は **入力には XML タグ**（`<instructions>` `<example>` 等）を推奨している。本稿は **出力に HTML** の話で、AI に情報を「入れる」軸ではなく「出させる」軸の話。ここを混ぜないように最初に切り分けておく。

## そもそも Markdown は AI 業界の暗黙の標準だった

ここで一度、当たり前と思っていた前提を一緒に確認します。これがないと、HTML への切り替えがただの好みの話に見えてしまうからです。

これまで、AI 出力の事実上の標準は Markdown でした。日々目にしているテキストを思い返してみてください。

- Claude Code が読み書きしているプロジェクト直下の `CLAUDE.md`、エージェント定義の `*.md`、Skills の `SKILL.md`
- Anthropic の公式ドキュメント、Claude.ai の Help、Claude Code の各種ガイド
- 同業の AI 開発ツール群、Cursor の rules、GitHub Copilot の instructions、Cline の指示書も、すべて `.md` 前提
- 社内 Wiki、GitHub README、Notion から書き出したテキスト、Slack に貼られる議事録
- ChatGPT のチャットからコピーしてきたまとめ文章

ここまで全部、Markdown 前提で組まれてきた世界です。あなたが AI と接している文字情報のうち、Markdown 以外のフォーマットを思い出すほうが難しいくらいです。

Karpathy 氏が公開した `CLAUDE.md` パターンが GitHub で 8 万スター以上を集めたのも、Markdown が業界の共通言語だったからこそ起きた現象です。

Thariq 氏の言葉をそのまま借りれば **Markdown は agent の主流フォーマットになっている**、です。彼自身、長らく Markdown 前提でツールを作ってきた立場の人です。

その立場の人が、今回はっきり言いました。**Markdown は自分にとって制約のあるフォーマットになってきた**、と。これは Anthropic の中の人が、業界全体が乗ってきた前提に「もう違う」と一石を投じた瞬間です。

「業界の標準」と書くと大げさに聞こえますが、要はこういうことです。あなたが Claude Code から受け取っている Markdown も、Cursor が読み込んでいる rules も、社内 Wiki に貼ってある AI 出力も、全部「Markdown でいいよね」という同じ流れの中にあった。その流れに、作っている本人が違う水路を引き始めた。

ここから先は、なぜ Markdown では届かないのか、何に置き換えれば届くのか、という具体の話に入っていきます。

## Markdown が読まれない 5 つの理由

ここで Markdown 側の限界を整理します。これは技術仕様の話ではなく、実務で Claude Code を使っている人の体感の話です。元記事で挙げられている HTML の利点を、Markdown の側に裏返して並べました。

**① 100 行を超えると、自分でも読まなくなる**

Thariq 氏自身が書いています。Markdown ファイルが 100 行を超えると、自分自身が読むのをやめる、と。

あなたが Claude Code に「先週の競合動向をまとめて」と頼んだとき、返ってきた 120 行をスクロールせずに閉じた経験が、おそらくあるはずです。出した本人が読まないものを、チームの誰かが読んでくれることはありません。著者本人だけでなく、組織の他のメンバーも同じように読み流している、というのが現実です。

**② 共有しても、ブラウザで綺麗に開けないから誰も触らない**

Markdown はブラウザでネイティブには綺麗に描画されません。Slack に貼ると改行が崩れる、メールに貼ると体裁が壊れる、提案資料に組み込むときは PDF 化やスクリーンショットを挟む手間が要る。

共有のたびに、誰かが「読める形」に変換する作業が発生していました。それが面倒で、結局リンクが届かない、というところまで含めて、Markdown は共有のたびに摩擦を生むフォーマットです。

**③ 色も図も付かないから、伝わるのは輪郭だけ**

数字の差を強調したい、警告だけ赤で出したい、フローを矢印で見せたい。Markdown でこれをやろうとすると、ASCII 文字でダイアグラムを描いたり、Unicode の罫線文字で色を表現したりする羽目になります。

誰も読み解こうとしないし、書く側も疲れる。Claude が頑張って図を描いても、結局は読み流されて終わりです。

**④ 触れない、動かせないから、読むだけで終わってしまう**

色を少し落ち着かせたい、アニメーションの速さを試したい、数値を 1.5 倍にしたらどう見えるか確かめたい。判断のために「触ってみる」が必要な場面は、ビジネスの現場でも頻繁にあります。Markdown ではそれができません。読んで、頭の中でシミュレートして、また文章で指示を返す、という非効率なループになります。

**⑤ モバイルで開くと崩れる**

移動中の Slack、移動中のメール、移動中の Notion。日本のビジネス現場では、共有された資料の半分はモバイルで最初に開かれます。Markdown のレイアウトは画面幅に追従しません。表が横にはみ出す、コードブロックが折り返される、見出しの階層が見えなくなる。読む気はその瞬間に消えています。

ここで一度、名前を付けておきます。読まれない Markdown を量産するたびに、出した本人にも、共有された相手にも、開く前から疲労だけが積もっていきます。100 行をスクロールするコスト、Slack で改行を直すコスト、図と色がないせいで伝わらないコスト、触れないせいで判断が遅れるコスト、モバイルで崩れるコスト。

これら全部が、目に見えないところで毎日支払われている料金です。本記事ではこれを **「フォーマット税」** と呼びます。

これは小さい税金ではありません。Claude Code の価値の半分以上は、出力の中身ではなく「誰に、どこまで届くか」で決まります。届かないフォーマットで出している時点で、契約の半分を捨てているようなものです。

## 実物で見比べる ─ 同じ週報を Markdown と HTML で

同じ依頼を 2 通り(Markdown で / HTML で)投げた実出力。

### Markdown 版

```markdown
# 週報 2026-05-04 〜 2026-05-10

## 今週の主な動き
- Project Alpha: 設計レビュー完了。来週から実装フェーズ
- Project Beta: ステークホルダーミーティングで方向性合意
- Project Gamma: 課題発見、要件再整理中(要相談)

## 数値KPI
| 指標     | 先週   | 今週   | 増減    |
|----------|--------|--------|---------|
| 新規登録 | 142    | 168    | +18%    |
| 解約率   | 3.2%   | 2.8%   | -0.4pt  |
| MRR ($)  | 4,200  | 4,380  | +4.3%   |

## 来週のフォーカス
1. Alpha 実装スプリント開始
2. Gamma の要件確定
3. Beta の進捗共有
```

### HTML 版

```html
<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>週報 2026-05-04 〜 2026-05-10</title>
<style>
  body { font-family: "Noto Sans JP", sans-serif; max-width: 760px;
         margin: 32px auto; padding: 0 24px; line-height: 1.8;
         color: #0a0a0a; letter-spacing: 0.04em; }
  h1 { font-size: 22px; border-bottom: 1px solid #ddd; padding-bottom: 8px; }
  h2 { font-size: 16px; margin-top: 32px; }
  .kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr);
              gap: 12px; margin: 16px 0; }
  .kpi { background: #f7f8fa; padding: 16px; border-radius: 8px; }
  .kpi .label { font-size: 12px; color: #666; }
  .kpi .value { font-size: 24px; font-weight: 600; margin-top: 4px; }
  .kpi .delta-up   { color: #057a55; font-size: 13px; }
  .kpi .delta-down { color: #c81e1e; font-size: 13px; }
  .project { padding: 12px 16px; border-left: 3px solid #2563eb;
             background: #fafafa; margin: 8px 0; }
  .alert   { background: #fff7ed; border-left: 3px solid #ea580c;
             padding: 12px 16px; margin: 8px 0; }
</style></head>
<body>
<h1>週報 2026-05-04 〜 2026-05-10</h1>

<h2>今週の主な動き</h2>
<div class="project">Project Alpha — 設計レビュー完了。来週から実装フェーズ</div>
<div class="project">Project Beta — ステークホルダーミーティングで方向性合意</div>
<div class="alert">Project Gamma — 課題発見、要件再整理中(要相談)</div>

<h2>数値KPI</h2>
<div class="kpi-grid">
  <div class="kpi"><div class="label">新規登録</div>
    <div class="value">168</div><div class="delta-up">▲ +18%</div></div>
  <div class="kpi"><div class="label">解約率</div>
    <div class="value">2.8%</div><div class="delta-up">▼ -0.4pt</div></div>
  <div class="kpi"><div class="label">MRR ($)</div>
    <div class="value">4,380</div><div class="delta-up">▲ +4.3%</div></div>
</div>

<h2>来週のフォーカス</h2>
<ol>
  <li>Alpha 実装スプリント開始</li>
  <li>Gamma の要件確定</li>
  <li>Beta の進捗共有</li>
</ol>
</body></html>
```

#### 実際の描画(Qiita上でインラインstyleがどこまで効くかの実証)

<div style="font-family: 'Noto Sans JP', sans-serif; max-width: 760px; margin: 16px 0; padding: 20px 24px; background: #fafafa; border: 1px solid #e5e7eb; border-radius: 8px; line-height: 1.8; letter-spacing: 0.04em; color: #0a0a0a;">
<div style="font-size: 18px; font-weight: 600; border-bottom: 1px solid #ddd; padding-bottom: 8px; margin-bottom: 16px;">週報 2026-05-04 〜 2026-05-10</div>
<div style="font-size: 14px; font-weight: 600; color: #444; margin-top: 8px; margin-bottom: 8px;">今週の主な動き</div>
<div style="padding: 10px 14px; border-left: 3px solid #2563eb; background: #ffffff; margin: 6px 0; font-size: 14px;">Project Alpha — 設計レビュー完了。来週から実装フェーズ</div>
<div style="padding: 10px 14px; border-left: 3px solid #2563eb; background: #ffffff; margin: 6px 0; font-size: 14px;">Project Beta — ステークホルダーミーティングで方向性合意</div>
<div style="padding: 10px 14px; border-left: 3px solid #ea580c; background: #fff7ed; margin: 6px 0; font-size: 14px;"><span style="color: #ea580c; font-weight: 600;">要相談</span>　Project Gamma — 課題発見、要件再整理中</div>
<div style="font-size: 14px; font-weight: 600; color: #444; margin-top: 20px; margin-bottom: 8px;">数値KPI</div>
<table style="width: 100%; border-collapse: separate; border-spacing: 8px 0;">
<tr>
<td style="background: #ffffff; padding: 12px; border-radius: 6px; border: 1px solid #e5e7eb; width: 33%;"><div style="font-size: 11px; color: #666;">新規登録</div><div style="font-size: 22px; font-weight: 600; margin-top: 2px;">168</div><div style="font-size: 12px; color: #057a55;">▲ +18%</div></td>
<td style="background: #ffffff; padding: 12px; border-radius: 6px; border: 1px solid #e5e7eb; width: 33%;"><div style="font-size: 11px; color: #666;">解約率</div><div style="font-size: 22px; font-weight: 600; margin-top: 2px;">2.8%</div><div style="font-size: 12px; color: #057a55;">▼ -0.4pt</div></td>
<td style="background: #ffffff; padding: 12px; border-radius: 6px; border: 1px solid #e5e7eb; width: 33%;"><div style="font-size: 11px; color: #666;">MRR ($)</div><div style="font-size: 22px; font-weight: 600; margin-top: 2px;">4,380</div><div style="font-size: 12px; color: #057a55;">▲ +4.3%</div></td>
</tr>
</table>
</div>

### Thariq 氏 companion site の代表例

- [11-status-report](https://thariqs.github.io/html-effectiveness/11-status-report.html) — 週報
- [18-editor-triage-board](https://thariqs.github.io/html-effectiveness/18-editor-triage-board.html) — ドラッグ振り分け編集画面(Markdown では原理的に作れない)
- [03-code-review-pr](https://thariqs.github.io/html-effectiveness/03-code-review-pr.html) — PR レビュー資料
- [08-prototype-interaction](https://thariqs.github.io/html-effectiveness/08-prototype-interaction.html) — クリック可能なフロー試作
- [19-editor-feature-flags](https://thariqs.github.io/html-effectiveness/19-editor-feature-flags.html) — feature flag 編集 UI

## 切り替え方は「HTML ファイルで出して」と書き加えるだけ

ここで身構える必要はありません。やることは思っているよりずっと少ないです。普段の Claude Code への依頼の最後に、1 行だけ書き加えるだけです。次の 3 つはどれも同じ意味で通ります。

```
HTML ファイルで出して
HTML の 1 枚もので出して
読み手がそのまま開けるように HTML にして
```

英語で書く方が安心するなら、`make a HTML file` や `make a HTML artifact` でも大丈夫です。中身は同じです。

Claude Code は MCP、ブラウザ、git、ファイルシステムから文脈を取り込めます。ChatGPT や Claude.ai の Web チャット側よりも、はるかに広い情報源を 1 つの HTML に束ねて返してくる、というのが Claude Code 側の強みです。

ここで、先ほど触れた話と繋がります。あなたが ChatGPT や Claude.ai で受け取って「綺麗だな」と感じてきた Artifacts、あれは HTML として出力されていたものです。同じ世界を、Claude Code 側でも受け取れるようになります。難しい技術の話ではなく、頼み方の 1 行を変えるだけで、ちゃんと届く資料が出てくるようになります。

ここで Thariq 氏が記事の中で念を押している点があります。**「これを /html Skill にしないでほしい、まずはプロンプトから慣れてほしい」** と書いているんです。彼自身が Claude Code チームの開発者で、Skill を量産する側にいるにもかかわらず、です。

これは Skill 化を否定しているのではありません。「使い方が固まる前にパッケージングすると、本当に効く部分を見逃す」という話です。Anthropic 内部でも、HTML 出力のうち頻度が高くなったものは、後に Playground プラグインのような形で部品化され始めています。最初から完成品を待つのではなく、まず 1 行プロンプトで試して、自分の業務にハマる型を見つける。そこに辿り着いてから初めて Skill 化に進む、というのが推奨される順序です。

毎回プロンプトに「HTML で出して」と書くのは作業に見えますが、フォーマットを選ぶ判断そのものは作業ではありません。Markdown のままで出してくる Claude を、HTML で出してくる Claude に切り替えた瞬間に、あなたは「設計済みの Skill を待つ前に、出力を設計する側に半歩回っている」状態になっています。

## シーン1: 週報・リサーチ要約を、図解つきで届ける

ここからが実務に効く章です。元記事に出てくる 5 つのユースケースを、日本の B2B 現場での出現頻度の高い順に並べ直しました。各シーンは、いまの困りごと、Before / After、最後に Claude Code に投げる指示文サンプル、の順でまとめます。

日本のビジネス現場あるあるですよね。月曜の朝、上司から「先週の動向まとめて」と振られる、あの仕事です。

**Before**：120 行の Markdown を Slack に貼り付けます。改行は崩れます。上司は開きません。経営会議の資料には載りません。「Claude にやらせたんですよ」と口頭で説明する羽目になります。

**After**：Slack の今週ログ、Linear や Notion のチケット履歴、`git log`、社内ドキュメントを横断して取り込んだ HTML 1 枚にまとめます。SVG で簡単な業務フロー図を入れ、注意点を 3 つだけ色付きブロックで下に置きます。これを社内ストレージに置いて URL を共有すれば、上司は移動中のスマホでも開ける、経営層は引用できる、議事録に貼れる、という状態になります。

ここで効くのが、Claude Code が MCP、ブラウザ、git、ファイルシステムから文脈を取り込める、という点です。同じ「HTML を作ってください」を Web チャットに頼んでも、これだけの情報源を 1 つの HTML に束ねるのは難しい。Claude Code 側だからこそ作れる週報です。

Thariq 氏自身も、自分が書く記事の図解を、自分のコードフォルダの全 HTML を Claude Code に読ませて、そこから 1 枚にまとめて作らせた、と書いています。「読まれる週報」と「読まれる解説記事の図」は、構造としては同じです。

```
先週の Slack のやり取りと、Linear のチケット消化と、git log を全部読んで、
上司が 1 分で把握できる週報を HTML 1 枚で出して。
SVG で簡単な業務フロー図と、注意点を 3 つだけ色付きブロックで下に付けて。
スマホで開いても崩れないようにして。
```

## シーン2: 企画書・調査資料を、6 案そのまま並列で見せる

来週の提案、どの方向で行くか。社内で複数案を作って意思決定者と擦り合わせる、企画／営業／経営企画でよくある場面です。

**Before**：6 つの案を 6 つの Markdown ファイルに分けて送る。クライアントは 1 つずつ開いて読み比べることができない。「結局どれが一番おすすめなんですか」と聞き返されて、自分の中でも比較しきれていなかったことに気付かされます。

**After**：トーン、密度、想定ターゲットを変えた 6 案を、1 枚の HTML にグリッド状に並べます。各案の下にトレードオフを 1 行ずつ付ける。意思決定者は 1 画面で全部を見比べて、「これとこれを混ぜたい」「3 番のターゲットで 1 番の密度にしてほしい」と即座に返してきます。並列で見せた瞬間に、議論の解像度が変わります。

意思決定者にとって、6 案を 6 ファイルで送られるのと、6 案を 1 画面で並べてもらうのとでは、判断にかかる時間が桁違いです。読んでもらえるようになる、というよりも、判断してもらえるようになる、という変化のほうが近いです。

```
来週の提案で出す企画案を 6 つ、トーン・密度・想定ターゲットを変えて、
1 枚の HTML にグリッドで並べて。各案の下にトレードオフを 1 行で書いて。
決定したら結果を Markdown でコピーできるボタンも下に付けて。
```

## シーン3: デザイン・プロトタイプを、触って決める

色やサイズや動きを決めるとき、文章ですり合わせるのは諦めたほうがいいです。マーケ、広報、企画でも、サンクスメールやランディングページのボタンを巡って何往復も認識合わせが起きる場面です。

**Before**：「もう少し落ち着いた青で」「動きをふわっと」と言葉で伝え合います。受け取る側のイメージは、毎回ずれます。1 周回って戻ってきた案を見て、「いや、そっちの落ち着きじゃなくて」とまた言葉を増やしていく。時間も精神も削れます。

**After**：Claude Code に、色とアニメーション速度をスライダーで動かせる HTML を作ってもらいます。サンクスメールのボタン、ランディングページの CTA ボタン、こうした要素のプロトタイプを HTML 1 枚で作って、関係者に URL を投げる。各自が触ってベストの値を決めて、その値だけを Claude にコピペして戻す。文章の往復が減って、合意までの時間が短くなります。

これに関連して、Anthropic の Labs 側でも、こうした「触って決めて、その操作内容を Claude にコピペして戻す」型の発想が、Playground プラグインとして公式機能化され始めています。HTML 出力は単なる小ワザではなく、Anthropic 自身が型として育て始めている方向、ということです。

```
サンクスメール内のボタンの色とアニメーション速度を、
3 種類のスライダーで動かしながら決められる HTML を作って。
決定した値をコピーできるボタンも下に付けて。
```

## シーン4: 編集画面を、3 分で 1 枚作って判断する

来期どの施策を Now、Next、Later、Cut に振り分けるか。30 件のチケットを並べ替えて優先順位を決める、PdM、企画、経営企画にとって典型的な「判断作業」です。

**Before**：スプレッドシートに 30 件並べ、優先度列を 1 つずつ手で埋めていく。ソートしては考え直し、別のシートに移しては戻す。30 分かけても結論が出ない、という日があります。

**After**：Claude Code に「Now、Next、Later、Cut の 4 列にドラッグで振り分けられる HTML を作って」と頼みます。3 分で専用の編集画面が出来上がります。30 件のカードをドラッグで移して、振り分けが終わったら結果をコピー。判断作業の時間が桁で縮みます。

ここでひとつ、見落とされやすいけれど効きどころとして大きい設計原則があります。Thariq 氏が記事の中で **「常にエクスポートで終わる」** と書いている、あの一文です。編集画面を作るときは、最後に必ず「JSON でコピー」「プロンプトでコピー」「Markdown でコピー」のボタンを置く。

これがないと、せっかく振り分けた結果を Claude に戻せず、ただの作業ツールで終わってしまいます。HTML で判断して、その結果を構造化テキストで Claude に戻す、というループまで作って初めて、編集画面は判断装置になります。

これは feature flag の編集、システムプロンプトの左右比較エディタ、データセットの approve / reject / tag のような場面でも丸ごと同じ発想で使えます。「専用の使い捨て UI を 3 分で作る」というのが、Claude Code の真価が一番分かりやすく出るところです。

```
来期 30 件の施策を Now / Next / Later / Cut の 4 列にドラッグで
振り分けられる HTML を作って。
最後に『Markdown でコピー』ボタンを置いて、
振り分け結果を 1 行ずつ理由付きで出力できるようにして。
```

## シーン5: PR レビュー・仕様書共有を、色分け差分で渡す

最後は、エンジニアと協働する場面です。PdM、ディレクター、編集者、コードを読まない立場でも、PR レビューや仕様書の確認に呼ばれる、あの場面です。

**Before**：GitHub の差分画面を開いてもらいます。差分のどこが大事で、どこは見なくていいのか、見ただけでは分かりません。コメント欄を読み込まないとストーリーが追えない。コードを読まない立場の人は、結局「何かあったら言ってください」と返して閉じます。

**After**：Claude Code に「この PR を、コードを読まない立場の人でも 30 秒で全体像が掴める HTML レビュー資料にして」と頼みます。差分の横にコメントが付き、影響範囲が色で分かれ、最後に懸念点が 3 つだけまとめられた HTML が返ってきます。これを社内ストレージに上げて URL で共有すれば、PdM やディレクターも 1 ボタンで意見を返せるようになります。エンジニアと協働する側の立場の人も、これでようやくレビューに参加できるようになります。

ここで言いたいのは、HTML はエンジニアの言語ではなく、ストーリーを渡すための道具だ、ということです。差分の意味、リスク、影響範囲、こうした「読み解きが必要な情報」を、注釈と色とレイアウトで一緒に渡す。それが HTML 化の意味です。

```
この PR を、コードを読まない立場の人でも 30 秒で全体像が掴める
HTML レビュー資料にして。差分の横にコメントを付けて、
影響範囲を色分けで示して、最後に懸念点を 3 つだけまとめて。
```

ここまでの 5 シーンを Markdown のままで出している間、フォーマット税は静かに、しかし毎日積み上がり続けています。気付いたタイミングで止めるかどうかが、来週からの違いになります。

## 切り替えるときに浮かぶ 6 つの疑問は先回りで消える

ここまで読んでいただいた方の頭の中に、おそらく順番に浮かんでくる疑問があります。元記事の FAQ 章を、日本のビジネス読者の出会いやすい順序に並べ直しました。

**■ トークンを多く使うのでは？**

使います。元記事では、Markdown の 2-4 倍の生成時間がかかる、と書かれています。一方で、Opus 4.7 は 1M トークンのコンテキストを持っていて、HTML を返してきても context 切れで会話が破綻するシーンは事実上なくなっています。

「数字としては増えるが、結果が読まれる方を選ぶと、トータルの仕事として元が取れる」というのが Thariq 氏の結論です。あなたの月3,000円超の契約を、開かれない Markdown 1,000 行に使うのか、開かれる HTML 1 枚に使うのか、という選択の話です。

**■ デザインがダサくなるのでは？**

これはもっともな心配ですが、対策が用意されています。1 つは、Claude Code の frontend design 系プラグインを使うこと。もう 1 つは、自社のサイトや既存資料からサンプルの HTML を 1 枚 Claude に渡しておくことです。「このトーンで」「このフォントとパレットで」と参照ファイルを渡しておけば、Claude はあなたの会社の見た目に合わせて HTML を出してきます。コードベースに `design-system.html` のようなファイルを 1 枚置いておくと、毎回参照させられます。

**■ HTML を編集するのが面倒では？**

これも気持ちは分かりますが、自分で編集する必要はありません。Thariq 氏自身、自分で HTML を直接いじることはしていない、と書いています。「ここの色を少しだけ落ち着けて」「3 番目のセクションだけもう少し小さく」と Claude に話しかければ直してくれます。仕様書、ブレインストーミング、参考資料として使う限り、編集は全部 Claude に任せられます。

**■ どうやって開くの？ どうやって共有するの？**

開くのは簡単です。Claude Code が出した HTML ファイルを、ブラウザでローカルに開くだけです。Claude に「このファイルを開いて」と頼めば、勝手にブラウザで開いてくれることもあります。共有するときは、社内ストレージや S3 のような場所にアップロードして、URL を渡すのが一番楽です。リンクを Slack やメールに貼れば、相手はブラウザで開けます。Markdown を PDF 化していたあのひと手間が、丸ごと消えます。

**■ バージョン管理はどうするの？(デメリット)**

正直、HTML は Git の差分管理にはあまり向いていません。1 行直すと、フォーマッタの都合で別の場所まで diff が動きます。Thariq 氏自身も、HTML は version control の最大の弱点だ、と書いています。

だからこそ、「人に届ける成果物」は HTML、「履歴を残したい仕様書や記録」は Markdown、という使い分けが現実解です。Markdown を全廃するという話ではなく、出力する目的別にフォーマットを選ぶ、という発想に切り替わります。

**■ Markdown はもう使わなくていいの？**

いいえ。記録、変更履歴、レポジトリに残しておきたい構造化されたテキストは、これからも Markdown のままで構いません。`CLAUDE.md` や Skills の `SKILL.md` は Markdown のままで運用したほうが、差分が追えて運用しやすいです。

HTML が向いているのは、「人に届ける」「触ってもらう」「複数案を並べる」「色付きで判断してもらう」、こういう成果物です。**「Markdown は AI とのやり取り、HTML は人への配り物」** という大づかみで理解すると、迷いません。

ここまでで、「気になっていた疑問が一通り消えた」状態になっているはずです。短所も含めて書いてある記事は信用できる、というのも記事を書く側の信念です。

> **ボトルネックはもう AI の性能ではなく、受け手の認知コストに移っている。**

## フォーマット税を払い続けるか、設計する側に回るか

ここまで来たら、最後に視座を 1 段上げて締めます。

以前扱った「プロンプト税」の話、つまり毎回同じ前提を Claude にチャットで打ち直しているコストの話。それから、`.claude` フォルダで設計レイヤーに上がる、という話。今回の「フォーマット税」は、その続編に当たる第 3 のテーマです。会話レイヤー、設計レイヤー、ときて、今回扱ったのが出力レイヤーです。

"フォーマット税"を、ここで一度、読者と共有できる定義として置いておきます。

> 読まれない出力フォーマットを選び続けると、自分にも他人にも、開く前から疲労が積もる。Claude Code に毎月3,000円以上払っているのに、成果物が会議で 1 度も使われない。あの感覚は、フォーマット選びを判断していなかったところから来ています。これがフォーマット税です。

Markdown のままで出すのは作業です。HTML を選ぶのは判断です。同じ Claude Code を使っていても、フォーマット選びという判断ひとつで、成果物の届く距離が大きく変わります。

そして、HTML はエンジニアの言語ではありません。読まれる資料を作るための道具です。Web サイトを組むという発想はいったん脇に置いて、明日の Claude Code への依頼の末尾に、まず 1 行だけ書き加えてみてください。

```
HTML ファイルで出して
```

これだけで、来週の Slack に流れる成果物の姿が変わります。
ここまで全てAIに記事を書いてもらい執筆したが、正直読む気にならない。最後まで読んでいただいた方は稀な存在であることは間違いない。この記事を最後まで読むのが面倒だったように、AIで記載した文章では認知コストがかかるのでHTMLで資格情報を整えてあげると言うことが今後大切になってくるかもしれない。

---

## 参考リンク(ソース)

**1次ソース**

- Thariq Shihipar 個人サイト: https://www.thariq.io/
- companion site(20 HTML サンプル一覧): https://thariqs.github.io/html-effectiveness
- 週報サンプル: https://thariqs.github.io/html-effectiveness/11-status-report.html
- チケット振り分けボード: https://thariqs.github.io/html-effectiveness/18-editor-triage-board.html
- PR レビュー資料: https://thariqs.github.io/html-effectiveness/03-code-review-pr.html
- Anthropic 公式: XML タグでプロンプトを構造化する(入力側の公式ガイダンス): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags
- Claude Code 公式ドキュメント: https://code.claude.com/docs/en/best-practices

**この議論を取り上げた 2次ソース(2026年5月)**

- Simon Willison: "Using Claude Code: The Unreasonable Effectiveness of HTML" — https://simonwillison.net/2026/May/8/unreasonable-effectiveness-of-html/
- StableLearn: "Claude Code Should Output HTML, Not Just Markdown" — https://stable-learn.com/en/claude-code-html-output/
- Pasquale Pillitteri: "HTML vs Markdown in Claude Code: Why Anthropic's Thariq Changed the Default" — https://pasqualepillitteri.it/en/news/2243/html-vs-markdown-claude-code-thariq-anthropic
