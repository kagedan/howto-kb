---
id: "2026-04-21-claude-skill-の-description-ー-公式ベストプラクティスを壊して測った-01"
title: "Claude Skill の description ー 公式ベストプラクティスを壊して測った"
url: "https://zenn.dev/shoki_sato/articles/c6a7c39b3b513c"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

!

* Anthropic 公式の [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) の「Writing effective descriptions」セクションにある 4 つの主張（三人称 / What+When / 具体性 / 曖昧さ回避）を、100 クエリ × 3 runs × 6 variants の binary LLM judge で検証した
* インパクトは一律ではなく **具体性（C3） >>> 曖昧さ回避（C4）≈ 一人称違反（C1-1st） >>> 二人称違反（C1-2nd）≈ When 節削除（C2）** の順。C3 を壊すと trigger rate が 0.62 → 0.26 まで落ちる
* 公式ルールを完全遵守した baseline ですら trigger rate 0.62 で頭打ち。description 最適化には天井があって、「用途指定」「間接表現」のクエリは description の質に関わらず半分漏れる

## 対象読者と前提

この記事は以下の人向けです。

* Claude Code の Skill を書いたことがある／これから書く人
* SKILL.md の `description` をどこまで真面目にチューニングすべきか悩んでいる人
* 公式 doc のベストプラクティスの「効き目」を定量的に知りたい人

Skill そのものの概念（SKILL.md や frontmatter の役割）の説明は省いています。必要な人は [Anthropic 公式の Skills ドキュメント](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) か、Zenn にいくつか出ている [入門解説記事](https://zenn.dev/explaza/articles/b3dde4451aa249) を先に読むと早いです。

## はじめに — 「三人称で書け」「具体的に書け」、ちゃんと効いてるのか？

Anthropic が公開している Skill authoring best practices の「Writing effective descriptions」セクションには、description の書き方に関する主張が並んでいます。

> Always write in third person. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.
>
> * Good: "Processes Excel files and generates reports"
> * Avoid: "I can help you process Excel files" / "You can use this to process Excel files"

「三人称で書け」「具体的な triggers を入れろ」「`Helps with...` みたいな汎称はやめろ」──読むと全部それっぽく聞こえます。ただドキュメントを読むだけだと、**4 つのうちどれがどれくらい効いているのか** が分かりません。全部守るコストと、一部だけ守ったときのペナルティは、同じ重さなのか？

なので壊してみました。公式 doc の中で検証可能な主張を 4 つ抽出して、それぞれ最小変更で違反した description を作り、同じ 100 クエリで差分を測ります。結論から言うと、**4 つの主張はインパクトが 6 倍以上違いました**。

## 公式 doc から取り出した 4 つの検証可能な主張

Writing effective descriptions セクションから、反例を作りやすい形に整理するとこうなります。

**C1（視点 / Point of view）**  
三人称で書け。一人称（"I resize..."）や二人称（"You can use this to..."）は discovery problem を引き起こす。

**C2（What + When）**  
Skill が「何をするか (what)」だけでなく、「いつ呼ばれるべきか (when / triggers / contexts)」も書け。

**C3（具体性 / Specificity）**  
`Helps with documents` や `Processes data` のような抽象語ではなく、具体的なファイル拡張子・キーワード・フレーズを列挙しろ。

**C4（曖昧さ / Vagueness）**  
`Helps with images.` のような汎称だけの description は最悪の例として名指しされている。

C1〜C4 はそれぞれ独立した dimension なので、1 つずつ最小変更で違反させれば、「その主張だけで性能がどれだけ変わるか」を切り分けられます。

## 実験設計

### ターゲット Skill

`image-resize` という架空の Skill を使います。画像ファイルをリサイズするだけの単機能 Skill。

### eval set（100 クエリ）

positive 50 件 / negative 50 件の計 100 件。エッジケースも拾えるよう、カテゴリをあらかじめ設計してから埋めました。

**Positive 50（`image-resize` が発動すべき）**

| category | 件数 | 例 |
| --- | --- | --- |
| `direct` | 8 | 「この画像をリサイズしてくれ」「画像サイズの調整をお願いします」 |
| `size_spec` | 10 | 「横幅800pxにしたい」「50%に縮小して」「1024x768にして」 |
| `preset` | 10 | 「Twitterのヘッダーサイズにしたい」「YouTubeサムネイルのサイズに」 |
| `slang` | 8 | 「画像ちっちゃくして」「もうちょっとデカくできる？」「ちっさくしたい」 |
| `indirect` | 8 | 「Slackに貼れるサイズに」「2MB以下に」「LINEで送れるサイズに」 |
| `usecase` | 6 | 「プレゼン資料に差し込む用のサイズに」「Qiita記事用に画像サイズ揃えたい」 |

**Negative 50（発動すべきでない）**

| category | 件数 | 例 |
| --- | --- | --- |
| `color` | 8 | 「白黒に」「彩度上げて」「セピア調」 |
| `crop` | 6 | 「被写体を切り抜いて」「余白をクロップして」 |
| `bg` | 5 | 「背景を透過に」「背景を白に差し替え」 |
| `ocr` | 5 | 「画像の文字を読み取って」「スクショの文字起こし」 |
| `format_convert` | 6 | 「HEICをJPGに」「SVGをPNGに変換」 |
| `composite` | 5 | 「コラージュして」「2枚を横並びに配置」 |
| `quality` | 5 | 「ノイズ除去」「シャープに」 |
| `other_media` | 4 | 「動画の解像度を下げて」「音声のビットレートを」 |
| `size_unrelated` | 4 | 「フォントサイズ大きく」「ウィンドウサイズ調整」 |
| `image_other` | 2 | 「似た画像を生成」「画像にタグをつけて分類」 |

`format_convert` と `size_unrelated` は、C4 の `Helps with images.` がどれくらい誤爆するかを観測するためのトラップカテゴリとして多めに入れています。

### Harness — binary LLM judge × 3 runs 多数決

Anthropic 公式の [skill-creator](https://github.com/anthropics/claude-code-plugins) の `run_loop.py` は、実際に `claude -p` サブプロセスを立ち上げて stream event を監視する方式で、trigger threshold で YES/NO を判定します。1 クエリあたり 10〜30 秒かかるため、今回はその判定ロジックだけ LLM judge で模倣した軽量版を使いました。

具体的には、system prompt に「この Skill を invoke すべきか YES/NO だけで答えろ」と指示し、user message に eval クエリを入れて、答えが `YES` で始まるかどうかだけ見る、という構造です。

harness の system prompt（クリックで展開）

```
def make_system_prompt(test_description: str) -> str:
    return f"""You are the skill discovery router inside Claude Code.

A skill is installed:
  name: image-resize
  description: {test_description.strip()}

Given the user's message, decide whether Claude Code should load and invoke
this skill to handle the request.

Answer rules:
- Output exactly "YES" if the skill should be invoked.
- Output exactly "NO" if the skill should NOT be invoked.
- Output nothing else — no explanation, no punctuation."""
```

1 クエリあたり 3 回叩いて多数決。揺らぎを吸収します。100 クエリ × 3 runs × 6 variants = **1,800 API call** を `ThreadPoolExecutor(max_workers=8)` で並列化して、全部で 5〜10 分、コスト 1.5 ドル程度でした。モデルは `claude-sonnet-4-6` 固定。

### Variant — baseline + 5 反例

6 つの description を用意しました。**baseline は公式 doc のルールを全部守ったもの**で、他の 5 つは 1 つずつ違反させています。

| variant | 壊した dimension | 内容 |
| --- | --- | --- |
| `baseline` | — | 三人称 + What + When + 具体的 triggers（gold standard） |
| `C1-1st` | 視点 | baseline を一人称（"I resize..."）に書き直した |
| `C1-2nd` | 視点 | baseline を二人称（"You can use this to..."）に書き直した |
| `C2-what-only` | What + When | baseline から When / triggers 節を削除。What のみ |
| `C3-abstract` | 具体性 | `Handles image size adjustment work.` だけ。拡張子もキーワードも無し |
| `C4-vague` | 曖昧さ | `Helps with images.` だけ（公式 doc の anti-example そのもの） |

baseline の中身はこれです。

```
Resizes image files (.png, .jpg, .jpeg, .webp, .gif) to a user-specified
pixel size, percentage, or preset (thumbnail, Slack-ready, Twitter card).
Use this skill when the user asks to make an image smaller, scale it up,
fit to a specific dimension, compress for upload, or generate a
social-media-ready crop. Triggers include: 「リサイズ」「サイズ変更」
「小さくして」「〇〇pxにして」「サムネ作って」「Slackに貼れるサイズに」.
```

## 結果 — まず全体像

| variant | trigger rate | FP rate | precision | accuracy |
| --- | --- | --- | --- | --- |
| `baseline` | **0.62** | 0.00 | 1.00 | **0.81** |
| `C1-1st` | 0.40 | 0.00 | 1.00 | 0.70 |
| `C1-2nd` | 0.52 | 0.00 | 1.00 | 0.76 |
| `C2-what-only` | 0.56 | 0.00 | 1.00 | 0.78 |
| `C3-abstract` | **0.26** | 0.00 | 1.00 | 0.63 |
| `C4-vague` | 0.28 | **0.12** | 0.70 | **0.58** |

インパクトで並べると **C3 ≫ C4 ≈ C1-1st ≫ C1-2nd ≈ C2** の順です。公式 doc は 4 つを一律で列挙していましたが、**実測では 6 倍以上の温度差があります**。

以下、効き目の大きい順に 1 つずつ見ていきます。

## 最大の効き目 — C3（具体性）

公式 doc の 4 主張のうち、実測で最も効いていた dimension がここでした。

* `baseline`: 拡張子（`.png .jpg .jpeg .webp .gif`）、プリセット名（`thumbnail`, `Slack-ready`, `Twitter card`）、具体的フレーズを全部書く
* `C3-abstract`: 「`Handles image size adjustment work. Use when the user wants to change an image's size.`」だけ

結果：

| variant | trigger rate | baseline との差 |
| --- | --- | --- |
| `baseline` | 0.62 | — |
| `C3-abstract` | **0.26** | **−36pt** |

**trigger が 36pt 落ちました**。全 variant 中で最大の落ち込みです。

驚くのは、C3-abstract では **「この画像をリサイズしてくれ」「画像サイズの調整をお願いします」のような直接語彙クエリすら落ちる** こと。

| クエリ | baseline | C3-abstract |
| --- | --- | --- |
| この画像をリサイズしてくれ | 3/3 | **0/3** |
| この画像リサイズかけて | 3/3 | **0/3** |
| 画像サイズの調整をお願いします | 3/3 | 2/3 |
| サムネ作って | 3/3 | **0/3** |
| Instagram投稿用に正方形リサイズして | 3/3 | **0/3** |
| 画像を1920px幅にそろえて | 3/3 | **0/3** |
| アイコン用にリサイズして | 3/3 | **0/3** |

description が `Handles image size adjustment work` だけだと、**"resize" "リサイズ" という単語そのものが description に登場していない** ため、LLM judge は「リサイズ = size adjustment」の推論を省略して NO に倒す傾向が出るようです。

つまり、**抽象的な概念語は LLM から見て triggers として弱い**。`image size adjustment work` よりも `Resizes image files ... Triggers include: 「リサイズ」「サイズ変更」...` の方が遥かに引っかかりやすい。拡張子とキーワードをべた書きする戦略は、単なる「丁寧に書く」ではなく **直接的な語彙マッチを増やす** という効果がある、というのが今回の観察です。

## 2 方向で壊れる — C4（曖昧さ）

次にインパクトが大きかったのが C4。`Helps with images.` だけ、という公式 doc 名指しの anti-example です。

| variant | trigger rate | FP rate | accuracy |
| --- | --- | --- | --- |
| `baseline` | 0.62 | 0.00 | 0.81 |
| `C4-vague` | **0.28** | **0.12** | **0.58** |

trigger rate が 34pt 下がり、**同時に FP rate が 12pt 上がっています**。他の variant はどれか片方しか悪化しませんが、C4 だけは 2 方向で壊れる。

**FP 側（誤爆）の具体例**（C4-vague で fire した negative クエリ）：

| クエリ | 本来の領域 | C4-vague |
| --- | --- | --- |
| このSVGをPNGに変換 | format\_convert | **3/3** |
| ビフォーアフターで2枚を横並びに配置 | composite | **3/3** |
| 画像の中央部分だけトリミング | crop | 2/3 |
| 背景を白に差し替えたい | bg | 2/3 |
| この画像の拡張子を変換したい | format\_convert | 2/3 |
| 写真を3枚並べて1枚にまとめて | composite | 2/3 |

**画像関連の別タスクを「images の何か」として拾ってしまう**。SVG→PNG も、コラージュも、全部「images の作業」です。`Helps with images.` は字義通り「画像を手伝う」なので、「リサイズ」という具体的な領域に絞れていません。

**trigger 側（漏れ）の具体例**（C4-vague で fire しなかった positive クエリ）：

| クエリ | baseline | C4-vague |
| --- | --- | --- |
| 画像サイズの調整をお願いします | 3/3 | **0/3** |
| 画像のサイズ変更してほしい | 3/3 | **0/3** |
| 50%に縮小して | 2/3 | **0/3** |
| 2MB以下のサイズにしたい | 3/3 | **0/3** |

description が `images` という単語しか含まないので、クエリに "image" "画像" がなかったり、あっても typical な resize 表現だと「これが `image-resize` 固有か？」を判定できず落ちる、という挙動に見えます。

`Helps with images.` は**広すぎる description** です。画像関連の何でも吸うくせに、具体的に何をする Skill なのかが分からないので「確信を持って invoke すべき」と判断されにくい。**広さが逆に発動確率を下げる** という直感に反する現象が可視化されました。

## 一人称が効く / 二人称は軽度 — C1（視点）

公式 doc の主張：三人称以外は discovery problem を起こす。ここは再現したのですが、一人称と二人称で効き方が違いました。

| variant | trigger rate | baseline との差 |
| --- | --- | --- |
| `baseline`（三人称） | 0.62 | — |
| `C1-1st`（一人称） | 0.40 | **−22pt** |
| `C1-2nd`（二人称） | 0.52 | −10pt |

**C1-1st（一人称）は trigger rate が 22pt 落ちます**。二人称は 10pt 低下で軽度以上。

具体例を見ると壊れ方がはっきり分かります。baseline で 3/3 で拾えていたクエリが、一人称版では 0/3 になる現象が連発します。

| クエリ | baseline | C1-1st |
| --- | --- | --- |
| この画像、Slackに貼れるサイズに小さくして | 3/3 | **0/3** |
| アイコン用にリサイズして | 3/3 | **0/3** |
| サムネ作って | 3/3 | **0/3** |
| この写真小さくしてSlackに貼りたい | 3/3 | **0/3** |
| サイズを変えたい画像がある | 3/3 | **0/3** |
| 画像のサイズ変更してほしい | 3/3 | **0/3** |
| 50%に縮小して | 2/3 | **0/3** |
| 2倍に拡大してほしい | 2/3 | **0/3** |

description を三人称から一人称に書き換えただけ。内容は同じ、それで trigger が 3/3 から 0/3 に落ちます。POV の不一致が discovery に効く、というのは体感できました。

二人称（`You can use this to...`）の方は一人称ほどは壊れません。**LLM が "I" という一人称に対して特に discovery を渋る傾向がある**、と読めます。二人称はまだ「マニュアル的な説明文」として受け流される余地があるが、一人称は「Skill 自身が喋っている」という不整合を強く感じさせる、のかもしれません。

## When 節の追加リターンは意外と小さい — C2（What + When）

最後は C2。What だけで When を書かないと Skill が呼ばれにくくなるか。

* `baseline`: What（リサイズする）+ When（小さくしたい／〇〇pxにしたい／サムネ作りたい、etc.）
* `C2-what-only`: What だけ（`Resizes image files ... presets.` で切る）

結果：

| variant | trigger rate | baseline との差 |
| --- | --- | --- |
| `baseline` | 0.62 | — |
| `C2-what-only` | 0.56 | **−6pt** |

**−6pt なので軽度**。When を削ったのに 3/6 クエリしか余計に漏れていません。

むしろ興味深いのは、C2-what-only だとエッジ気味のクエリ（「画像でかすぎるから縮めて」「もうちょい小さくしてほしい」）の一部は落ちるものの、**「png 400x400 にして」「1500pxまでサイズダウンして」のような数値指定系は baseline よりよく拾っている** 点です。

直感的解釈：`Resizes image files to a user-specified pixel size, percentage, or preset.` という What は、数値指定の発動条件を既に内包しています。triggers リスト（「Slackに貼れるサイズに」「サムネ作って」）が追加で効くのは、**語彙が triggers と完全に一致するクエリ** に対してだけ。その意味で、What 節がしっかり書けていれば、When 節の追加リターンは実は小さい、というのが今回の示唆です。

## baseline の天井 — description だけでは救えないクエリ

ここが N=100 で初めて見えた、今回いちばん面白かった観察です。

**公式ルールを完全遵守した baseline ですら trigger rate は 0.62**。つまり positive 50 問のうち 19 問は、どれだけ description をちゃんと書いても（少なくとも 3 runs 多数決の threshold では）拾えていません。

baseline が落とした 19 問を眺めると、共通のパターンが見えます。

**用途指定系**（pos\_usecase / preset）

* LinkedInのカバー画像サイズ用意したい (0/3)
* Zoomのプロフアイコンサイズに合わせて (1/3)
* Instagram投稿用に正方形リサイズして (0/3)
* GitHubのREADMEに貼るのにちょうどいいサイズにして (1/3)
* Qiita記事用に画像サイズそろえたい (1/3)
* Discord投稿用にリサイズしておいて (1/3)
* 名刺に載せる顔写真サイズに調整 (0/3)
* プレゼン資料に差し込む用のサイズに画像調整 (1/3)

**間接表現系**（pos\_indirect）

* メールに添付できるサイズに画像落として (0/3)
* LINEで送れるサイズにしたい (0/3)

**俗語系**（pos\_slang）

* 画像でかすぎるから縮めて (0/3)
* もうちょい小さくしてほしい (0/3)
* 画像めっちゃでかいからコンパクトにして (2/3 ✓)
* もうちょっとデカくできる？ (0/3)
* でかくしたい画像あるんだけど (1/3)
* ちっさくしたい (3/3 ✓)

**数値指定系の一部**（pos\_size\_spec）

* 1500pxまでサイズダウンして (0/3)
* この写真のピクセル数を半分にしたい (0/3)
* 解像度を640x480に変更 (1/3)

これらのクエリは、description に「LinkedIn」「名刺」「メール」「縮めて」「でかすぎる」を全部列挙すれば拾える可能性があります。ただ実運用でそれをやるのは現実的じゃない──キリがないし、triggers リストが 300 行になったら別の意味で不健全です。

ここから読める実務的な含意：

1. **「良い description」の効能には天井がある**。公式ルールを守り切っても trigger 0.6 前後。それ以上を狙うなら description の改善ではなく、別のアプローチ（Skill 名の工夫、skill-creator の run\_loop での iterative refinement、複数 Skill 協調）に踏み込む必要がある
2. **description 最適化の ROI は dimension によって違う**。C3（具体性）を壊すと −36pt、一方で When 節追加（C2 の逆方向）は +6pt。**ひとつでも dimension を壊すと効果が大きく、全部守っても頭打ちにぶつかる**
3. **「拾えないクエリ」にはパターンがある**。用途指定・間接表現・俗語。これを description 側で救う代わりに、ユーザー側に「画像」「サイズ」「リサイズ」の語彙を期待する、という割り切りが実務的

## 総括 — 公式 doc の主張にはインパクトの順位がある

まとめるとこうなります。

| クレーム | baseline 比 | 判定 |
| --- | --- | --- |
| C3 具体性（抽象語 vs 具体語） | **trigger −36pt** | **最大** |
| C4 曖昧さ（`Helps with images.`） | accuracy −23pt（trigger −34pt + FP +12pt） | **2 方向で壊れる** |
| C1-1st 一人称 | trigger −22pt | 中程度 |
| C1-2nd 二人称 | trigger −10pt | 軽度 |
| C2 What + When（When 削除） | trigger −6pt | 軽度 |

公式 doc は 4 つを等並列で列挙していましたが、**実測のインパクトは 6 倍以上違います**。description を書くときの優先順位は次のようになります。

1. **汎称は絶対に避ける**（`Helps with ...` / `Works with ...`）。これは trigger と FP の両方を壊す
2. **具体的な語彙を書く**。拡張子・プリセット名・ユーザーが実際に使うキーワードをべた書きする。抽象的な概念語は LLM にとって triggers として弱い
3. **三人称で揃える**。特に一人称は discovery を大きく下げるので避ける
4. **When / triggers 節の追加はおまけ**。What をちゃんと書いていれば、When の追加リターンは案外小さい

それでも baseline で trigger 0.62 なので、**description 最適化でカバーできない領域がある** ことは受け入れる必要があります。用途指定（`LinkedIn の〜`）や俗語（`でかすぎる`）は description 側では救いにくく、「ユーザー側の語彙」に頼る部分です。

## おわりに

ドキュメントが「こう書け」と列挙している主張が、**等しく効いているとは限らない**、というのが今回の実験で一番の学びでした。特に `Helps with ...` のような汎称を避けることと、具体的な語彙を書くことは実測で大きく効きます。逆に、What + When の When 節を追加で足す効能は、What をちゃんと書いていればかなり小さい。

それから、**公式ルールを完全遵守した baseline ですら trigger rate は 0.62** という事実。description 最適化には天井があって、それ以上の discovery 精度を求めるなら別レイヤーの工夫（Skill 名、複数 Skill 協調、run\_loop による iterative refinement）に踏み込む必要がある、というのが次に検証したい方向です。
