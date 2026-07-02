---
id: "2026-07-02-fable-5を効率的に使うアドバイザー機能とclaudeでopenaiのモデルを呼び出す方法-01"
title: "Fable 5を効率的に使う―アドバイザー機能と、ClaudeでOpenAIのモデルを呼び出す方法"
url: "https://zenn.dev/kotoda_ma/articles/c3c56c1b7bff26"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "OpenAI", "GPT", "zenn"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

輸出規制の影響で一時停止していた Claude Fable 5 が、2026年7月1日に[グローバルで復活しました](https://www.anthropic.com/news/redeploying-fable-5)。Anthropic が「最も高い能力が必要なワークロード向け」と位置づける、現時点で最上位の広く提供されているモデルです。

うれしくなって Claude Code のデフォルトを Fable 5 にすると、財布と使用枠が溶けていきます😭😭  
Fable 5 の料金は入力 $10 / 出力 $50（100万トークンあたり）で、Opus 4.8 のちょうど2倍。Anthropic の開発者自身も、[ITmedia のインタビュー](https://www.itmedia.co.jp/aiplus/article/2606/30/2000000137/)で「一番賢いモデルをすべてのタスクに使う必要はない」と語っています。

ではどうするか！  
この記事では、私が Claude Code で採っている次の運用を紹介します。

* 普段は安いモデルで動かし、Fable 5 は「アドバイザー（相談役）」として脇に置く
* コードレビューは OpenAI の Codex に逃がして、Claude 側の枠を節約する

## 要旨

1. アドバイザーを設定する。Claude Code のセッションで `/advisor claude-fable-5` と打つだけ。以降は普段使いのモデルのまま、要所で Fable 5 が助言に入ります。
2. レビューは Codex に任せる。公式プラグイン [`codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) を入れる。  
   お好みで後述のプロンプトを一度貼れば、あとは「レビューして」と言うだけ。(まあ、なくてよい)

これで、Fable 5 の判断力をコストを抑えながら、必要なところにだけ効かせられます。

## なぜ「アドバイザー」に据えるのか

Claude Code には「[アドバイザー](https://code.claude.com/docs/en/advisor)」という仕組みがあります。メインで動くモデル（実行役）とは別に、もう一段賢いモデルを相談役として登録しておくと、実行役が方針を決める前・エラーで詰まったとき・完了を宣言する前といった要所で、その相談役に意見を仰ぎます。相談役は会話の全文（ツールの呼び出しと結果を含む）を受け取り、短い助言を返す。いつ相談するかは実行役の側が判断します。

この形がコスト面で効くのは、生成されるトークンの大半が安い実行役の料金で済むからです。Fable 5 が担うのは要所での短い助言だけなので、Fable 5 に近い判断力を、ほぼ実行役モデルのコストで引き出せます。

これは、Anthropic が公式ブログ「[The advisor strategy](https://claude.com/blog/the-advisor-strategy)」でも勧めている方法です。同ブログの評価では、Sonnet に Opus をアドバイザーとして付けると SWE-bench Multilingual のスコアが Sonnet 単独より 2.7 ポイント上がり、タスクあたりのコストはむしろ約12%下がった、と報告されています。「賢いモデルを常用する」のではなく「賢いモデルを相談役に回す」ほうが、質とコストの両取りになりうるわけです。

実行役には Sonnet を選ぶのが素直です。とくに現在の Sonnet 5 は2026年8月31日まで入力 $2 / 出力 $10 の導入価格なので、この組み合わせはいっそう割安になります。(まあopusでもよいと思います)

設定はセッション内のコマンドが一番かんたんです。

この選択は `advisorModel` としてユーザー設定に保存され、次のセッションでも有効です。設定ファイルに直接書くなら、`~/.claude/settings.json`（チームで共有するならプロジェクト直下の `.claude/settings.json`）に次のように書きます。

```
{
  "model": "claude-sonnet-5",
  "advisorModel": "claude-fable-5"
}
```

前提が一つあります。アドバイザーはサーバー側で実行されるツールで、Anthropic API 経由でのみ動きます（Amazon Bedrock・Google Vertex AI・Microsoft Foundry では使えません）。また Fable 5 をアドバイザーにするには Claude Code v2.1.170 以降が必要なので、`claude update` で更新しておきましょう。

## 注意点

ここで、ほぼ全員が一度は踏む落とし穴を先に共有しておきます。

Fable 5 を `/model claude-fable-5` で主役に切り替えると、 400 エラーが延々と出ることがあります。

```
API Error: 400 tools.10.model: 'claude-opus-4-8' cannot be used as an
advisor when the request model is 'claude-fable-5'.
```

原因は Fable 5 ではなくアドバイザー設定です。アドバイザーには「実行役より強いモデルでなければならない」という規則があり、実行役を最上位の Fable 5 にした瞬間、格下の Opus 4.8 が助言役のままだと組み合わせが成立しなくなります。新入社員が CEO に経営戦略を助言できない、というイメージです。

対処はどれか一つでOKです。

* アドバイザーをいったん切る：`/advisor off`
* Fable 5 を主役にしたまま助言もほしいなら、アドバイザーを Fable 5 相当以上に上げる（そもそも同格以上でないと付きません）
* 挙動が安定しないときは、`~/.claude/settings.json` の `advisorModel` と `fallbackModel` を両方確認する

最後の `fallbackModel` はとくに厄介で、これが有効だと上の 400 エラーが画面に出ないまま、勝手に Opus へ切り替わることがあります。「なぜかモデルが Fable 5 にならない」という混乱の多くは、この自動フォールバックが真因を隠しているせいです。原因を切り分けたい場合は`fallbackModel` を外すとエラーが表に出て追いやすくなります。

## レビューは Codex に逃がす

もう一つは、Claude 側の枠を守る工夫です。レビューのように「別の視点で一度見てもらう」作業は、あえて OpenAI の Codex に振ってしまいます。Fable 5 や Opus のトークンをレビューで消費せずに済むうえ、別ベンダーの AI からセカンドオピニオンが得られるというメリットがあります！

Codex は、OpenAI 公式の Claude Code 用プラグイン [`codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) から呼び出せます。導入は最初の一度だけコマンドが必要です（Claude Code に順に貼るだけ）。

※基本skillsは安心できる配布先か確認してください。これはOpenAIのものなので私はダウンロードしました。

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

前提は、ChatGPT のサブスク（無料プランでも可）または OpenAI の API キーと  
Node.js 18.18 以降です。Codex 本体が入っていなければ `npm install -g @openai/codex`、未ログインなら`!codex login`。`/codex:setup` を打てば、使える状態か確認してくれます。

このプラグインは、手元にある `codex`（Codex CLI）をそのまま呼び出す薄いラッパーです。別のランタイムが増えるわけではなく、既存の Codex のログインや設定をそのまま引き継ぎます。

導入できたら、あとはコマンドを覚える必要はありません。次のプロンプトを一度だけ会話の冒頭（または `CLAUDE.md`）に置いておけば、以降は自然な言葉で「レビューして」と頼むだけで、通常レビュー・批判的レビュー・タスクの委譲を自動で使い分けてくれます。まあ、CLAUDE.mdに貼るより、プロンプトで今後よろしく〜とかでもいいじゃないかな(しらんけど)

```
あなたは Claude Code です。これから、コードレビューと第2意見はすべて OpenAI Codex に任せます。
Codex は OpenAI 公式の Claude Code 用プラグイン「codex-plugin-cc」で呼び出せます。
リポジトリ: https://github.com/openai/codex-plugin-cc

【最初にやること：使える状態か確認】
1. Codex プラグイン／Codex CLI が使えるか確認してください。
2. まだ使えない場合は、私が実行すべき手順を「コマンドだけ」箇条書きで示してください:
   - プラグイン導入:
       /plugin marketplace add openai/codex-plugin-cc
       /plugin install codex@openai-codex
       /reload-plugins
       /codex:setup
   - Codex 本体が無ければ: npm install -g @openai/codex （要 Node.js 18.18 以降）
   - 未ログインなら: !codex login （ChatGPT サブスク＝無料でも可／または OpenAI API キー）
   準備ができたら「準備OK」とだけ教えてください。

   これで、codex、たのむ！でcodexがなんとかしてくれます

【いつ Codex を使うか】
- 私が「レビューして」と言ったら → Codex に通常のコードレビューを依頼する。
  対象は原則、未コミットの変更。ブランチ比較が必要なら、比較元（例: main）を確認してから。
- 変更が複数ファイルにまたがる／時間がかかりそうなら → レビューを背景実行で走らせ、
  完了したら結果を報告する。
- 移行・認証・インフラ・大規模リファクタなど「隠れた前提」が危険な変更のときは →
  通常レビューではなく「実装方針そのものを疑う批判的レビュー」を依頼する。
  観点は 代替案・失敗モード・ロールバック・競合状態・データ損失。私が重点テーマを渡したら最優先で。
- 作業が行き詰まった／別の視点で一気に進めたいときは → タスクを Codex に委譲する。

【守ること】
- Codex はレビューと調査が中心。コードの書き換えや破壊的操作（コミット/push/削除/外部送信）は、
  私の明示的な承認なしに行わない。
- Codex の生の出力をそのまま貼らず、日本語で要点を3〜7点に要約し、
  各指摘に「対応する/しない＋理由」を必ず添える。
- 背景ジョブを走らせたら進捗と最終結果を知らせ、中断が必要なら私に確認する。
```

たとえば、こんな言い方をします。

* 「このPRをレビューして」→ 通常のコードレビュー
* 「この移行を批判的に見て。ロールバックと競合状態を重点的に」→ 実装方針そのものを疑う批判的レビュー
* 「テストが落ちる原因を調べて、いちばん小さくて安全な修正を当てて」→ Codex に作業ごと委譲

移行・認証まわり・インフラ・大規模リファクタのように「隠れた前提」が危険な変更ほど、批判的レビューが効きます。

## まとめ

結局のところ、Fable 5 との付き合い方は「常時使わない」に尽きます。普段は `/advisor claude-fable-5` で相談役として控えさせ、レビューは Codex に逃がして、Claude 側の枠を効くところに温存する。この使い分けだけで、最上位モデルの判断力を現実的なコストで日々の開発に組み込めます。

提供枠についても一点だけ。復活初週は、Pro / Max / Team および一部の Enterprise で7月7日まで週次上限の最大50%まで Fable 5 が含まれ、それ以降は usage credits（従量課金）に切り替わります。枠が限られるいまだからこそ、「難所だけに集中投下」できるアドバイザー運用が効いてきます。

## 参考リンク
