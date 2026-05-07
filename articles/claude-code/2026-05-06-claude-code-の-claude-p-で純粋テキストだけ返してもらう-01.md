---
id: "2026-05-06-claude-code-の-claude-p-で純粋テキストだけ返してもらう-01"
title: "Claude Code の claude -p で純粋テキストだけ返してもらう"
url: "https://zenn.dev/tbnet/articles/claude-code-headless-text-output"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

普段使いの Claude Code を、スクリプトからもそのまま流用したい場面があった。`claude -p` でヘッドレス(対話を介さない CLI 呼び出し)に動かせれば、ちょっとした自動生成パイプラインに LLM 部分として組み込める。気軽に何度でも叩けるほうが、試行錯誤の回転が早いのも理由のひとつだった。

それでヘッドレス構成を組んだところ、期待した本文が返ってこないという形で、最初のステップで詰まった。

期待していたのは約 1,900 字の記事本文。実際に標準出力に返ってきたのは、こんな短い要約だった。

```
週刊レポート draft を `issues/weekly-2026-w18/draft.md` に
書き出しました(2033 chars、本文は約 1,800 字)。

構成サマリ:
- 今週の傾向: AI とセキュリティが両媒体で同時に上位...
```

スクリプトは `claude -p` の 標準出力をそのまま `draft.md` にリダイレクトする素朴なつくりだったので、生成された記事本文を、エージェントが書いた要約で上書きする事故になった。

理由はわかってみれば単純な話で、`claude -p` はデフォルトでエージェントモードとして動く。Write / Edit / Bash などのツールが有効な状態で、プロンプトに「ファイルに書いて」と頼んでいなくても、モデルが自律的に Write を選んで記事をファイル出力し、標準出力には「保存しました」とだけ返してきた、という流れだった。エージェントとしてはむしろ気の利いた挙動なのだが、標準出力を最終応答として受け取りたいスクリプトとは噛み合わない。

止め方は単純で、`--tools ""` を渡せばよい。使えるツール集合が空になり、モデルは応答テキストを返すしかなくなる。

```
claude -p \
  --append-system-prompt "$(cat system-prompt.md)" \
  --output-format text \
  --tools ""
```

`claude -p --help` の該当箇所を見てもらうのが早い。

```
--tools <tools...>
    Specify the list of available tools from the built-in set.
    Use "" to disable all tools, "default" to use all tools,
    or specify tool names (e.g. "Bash,Edit,Read").
```

Node から呼ぶときの最小はこのくらいになる。

```
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";

const SYSTEM = readFileSync("system-prompt.md", "utf8");
const USER = readFileSync("user-input.md", "utf8");

const r = spawnSync(
  "claude",
  [
    "-p",
    "--append-system-prompt",
    SYSTEM,
    "--output-format",
    "text",
    "--tools",
    "",
  ],
  { input: USER, encoding: "utf8", maxBuffer: 16 * 1024 * 1024 },
);

if (r.status !== 0) throw new Error(r.stderr);
console.log(r.stdout);
```

ちなみに `--allowed-tools` と `--tools` は別物で、後者のほうが優先される。「使えるツール集合そのもの」を置き換える挙動なので、許可リスト方式の `--allowed-tools "Bash(git *) Edit"` とは方向が違う。やりたいことが「全部禁止して純粋テキストが欲しい」だけなら `--tools ""` が最短だった。

`--tools ""` を効かせた後でも、LLM は時々「ファイル出力ツールが利用可能でないため…」のような前置きや、```` ```markdown ``` ```` で全体を包んだ出力を混ぜてくる。記事生成パイプラインで使うなら、標準出力を受け取った後にコードフェンス剥がしや先頭メタ行除去くらいの軽いクリーニングを噛ませておくほうが、プロンプト調整で抑え込もうとするより楽だった。

もう一つだけ、スクリプトで `claude -p` を回すなら `--bare` も併用しておくと安定する。hooks や skills の auto-discovery を skip して起動が早くなり、ローカル環境差の影響も受けにくい(公式は将来こちらをスクリプト用途の default にする方向で動いている)。

CI から Claude Code を動かすときに、最初に踏みやすい落とし穴として共有しておく。

---

参考にしたドキュメント:

* [CLI reference](https://code.claude.com/docs/en/cli-reference) — Claude Code の全フラグの正式リファレンス。`--tools` / `--allowed-tools` / `--disallowed-tools` / `--append-system-prompt` / `--output-format` などの仕様がフラグ単位で並んでいる。`--tools` の「`""` で全無効化」もここに明記されている。
* [Run Claude Code programmatically](https://code.claude.com/docs/en/headless) — `claude -p` をスクリプトや CI から呼び出すときの公式ガイド。`--bare` モードの位置付け、`--allowed-tools` の使い分け、Agent SDK との関係、構造化出力、ストリーミング、commit 自動化のレシピなどがまとまっている。
