---
id: "2026-04-22-claude-code-実践編-output-style-01"
title: "Claude Code 実践編 — Output Style"
url: "https://qiita.com/sugo_mzk/items/30da0a75b55cd7abe7c3"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

# Claude Code 実践編 — Output Style

## はじめに — 「絶対おっしゃる通りです！」にモヤっとする

Claude Code を日常的に使っていると、ある瞬間に手が止まる。

```
You're absolutely right!
Let me fix that right away.
...
I have successfully updated the code!
```

テストは動かしていない。tsc も通していない。それなのに「successfully」と言い切って turn を閉じてくる。あるいは自分のコードの明確なバグを「Good catch!」と言ってから直す。

最初は「プロンプトに "簡潔に、同調するな" と書けば直るだろう」と思っていた。直らなかった。CLAUDE.md に書いても効きが悪い。`--append-system-prompt` に突っ込んでも挙動はあまり変わらない。

結局 npm で配布されている `@anthropic-ai/claude-code` パッケージの `cli.js`（Node.js バンドル）を開いて解析した。挙動を追いかけると **「どこに書くかで効力が全然違う」** ということが分かった。Output Style はその中でも特殊な位置にいる。この記事はその話。

## Output Style の位置づけ

公式ドキュメント（[Output Styles](https://code.claude.com/docs/ja/output-styles)）は要点だけ書くと次の通り:

* Claude Code のデフォルトシステムプロンプトの **一部を置換** する機構
* Markdown ファイル + frontmatter で書く
* 組み込みで 3 つ（Default / Explanatory / Learning）
* ユーザーレベル `~/.claude/output-styles` かプロジェクトレベル `.claude/output-styles`
* frontmatter のフィールドは `name` / `description` / `keep-coding-instructions` の **3 つ** とされている

最後の「3 つ」が微妙に嘘で、実装を見ると **4 つめがある**。ここから話が始まる。

> **実装の出どころについて**
>
> Claude Code は現時点でソース非公開。本記事で挙げる関数名・ファイルパス・行番号は、npm 配布されている `@anthropic-ai/claude-code` の `cli.js`（Node.js バンドル）を解析した結果に基づく。`prompts.ts:151-158` のように書いているのは、バンドル前の元ソースツリーとして推測される構造を示したもので、関数名と挙動は cli.js から観察できる。行番号は解析時点のバージョン依存なので、リリースが進めばズレる。

## 実装を開けてみる

Output Style は `src/outputStyles/loadOutputStylesDir.ts` で frontmatter を読み、`src/constants/prompts.ts:151-158` の以下の関数でシステムプロンプトに挿入される。

```
function getOutputStyleSection(
  outputStyleConfig: OutputStyleConfig | null,
): string | null {
  if (outputStyleConfig === null) return null
  return `# Output Style: ${outputStyleConfig.name}
${outputStyleConfig.prompt}`
}
```

ラッパーは無い。`# Output Style: xxx` ヘッダの後に、ファイル本文（frontmatter を除いた中身）がそのまま system ロールに差し込まれる。CLAUDE.md が `"This may or may not be relevant to your tasks..."` という消極的な前置き付きで user ロールに差し込まれるのとは対照的だ。

そして frontmatter パーサ（`loadOutputStylesDir.ts:52-78`）を読むと、実は 4 フィールド読んでいる:

* `name`
* `description`
* `keep-coding-instructions`（`true`/`'true'` は true、`false`/`'false'` は false、それ以外は undefined）
* `force-for-plugin`（プラグイン以外で指定すると warning log）

ドキュメントには `force-for-plugin` の記載がない。プラグイン作者向けなので普通は関係ないが、「3つだけ」と断言している解説記事は **実装を見ていない** と一発で分かる。

## 挿入位置の罠

Claude Code のシステムプロンプトは内部的に二分割されている。静的領域（全ユーザー共通、キャッシュ可能）と動的領域（セッション依存）で、境界は `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` マーカー（`prompts.ts:114`）。

`prompts.ts:505-577` の組み立てを見ると、Output Style はこの境界の **後ろ**（dynamic セクション）に入る。意味するところは:

* プロンプトキャッシュの cross-org 再利用に **乗らない**
* セッション内では初回以降キャッシュされる
* ファイルを書き換えると次セッションで cache miss

ドキュメントは「システムプロンプトの最後に追加されます」と書いているけれど、実際には `mcp_instructions` / `scratchpad` / `summarize_tool_results` / `token_budget` などが Output Style の **後ろにも** 来る。「最後」ではなく「動的領域の手前寄り」が正確。

## keep-coding-instructions のデフォルトは false

これが一番ハマる。公式は明記しているが、多くの自作テンプレは書き忘れている。

```
---
name: my-style
description: ...
keep-coding-instructions: true  # ← これを書かないと
---
```

書かないと `prompts.ts:564-567` の分岐:

```
outputStyleConfig === null ||
outputStyleConfig.keepCodingInstructions === true
  ? getSimpleDoingTasksSection()
  : null,
```

で **Doing tasks セクションまるごと落ちる**。「read before modify」「セキュリティに注意」「parallel tool calls 推奨」のような、Claude Code の基本動作を定義している重要な指示群が丸ごと消える。自分が書いた 10 行程度の Output Style が、数百行のデフォルト行動指針を silently 上書きしてしまう。怖い。

TypeScript の条件分岐的には「true または文字列 'true' のときだけ true」という厳しい判定なので、`keep-coding-instructions: yes` とか `: 1` とか書いても undefined 扱いで同じく落ちる。

## 防御ヒエラルキー

Claude Code には挙動を制御する層が何種類かあり、強度が違う。強い順に:

| 層 | 強度 | 機構 |
| --- | --- | --- |
| Hook exit 2 / deny | 最強 | `.claude/`/`.git/` は bypass-immune |
| Hook `additionalContext` / `hook_blocking_error` | 強 | `<system-reminder>` ラップ |
| **Output Style** | **中** | **system ロール、ラッパーなし、毎ターン有効** |
| CLAUDE.md / Rules | 弱 | user ロール、"may or may not" 前置き |
| Stop hook `blockingError` | 弱 | plain user message |
| hook `systemMessage` | ゼロ | UI 専用、API 非到達 |

最後の `systemMessage` は罠で、一見 system prompt に入りそうな名前だが `normalizeAttachmentForAPI` が `[]` を返すため API には届かない（`messages.ts:4258-4261`）。「LLM への指示を systemMessage で返す」と書いてある hook 解説は全部誤り。

使い分け:

* 実行そのものを止めたい → Hook deny
* 毎ターン有効にしたい行動指針 → Output Style
* プロジェクト固有の文脈 → CLAUDE.md
* パス限定のルール → `.claude/rules/*.md`（Read 時にだけ差し込まれる）

**「強制したい指示」を CLAUDE.md に書いてはいけない**、というのが実装を読んだあとの強い結論。

## 実際に書いてみた（ケーススタディ）

この記事を書いている裏で、実際に `.claude/output-styles/anti-sycophancy.md` を設計した。ざっと過程を書くと:

1. 初版は 7 セクション、2,732 chars。普通の anti-sycophancy スタイル
2. 3 セクション追加 → 10 セクション、3,946 chars
3. この時点で「冗長では？」とコンテキスト圧迫を疑った
4. Agent Team を起動して並行レビュー:
   * **researcher**: ベースシステムプロンプトとの重複分析
   * **project-analyzer**: ファイル内の冗長性マトリクス
   * **config-reviewer**: devil's advocate（他 2 人の結論を疑う）
5. config-reviewer だけが見つけた gap: `"If you cannot verify (no test exists, cannot run the code), say so explicitly rather than claiming success."` が欠落していた
6. 最終: 8 セクション、3,218 chars（-18.4%）。`Complete` / `Verify` / `Report` を **ラベル付き段落** に畳んで phase 構造を保存

Agent Team を 1 人ではなく 3 人並行で回したのが効いた。同じモデルでも context isolation が違うと見落としが違う。最終版で「cannot verify なら言え」の 1 行が入ったのは config-reviewer のおかげで、これは実際のプロダクションで false claim の典型パターン。

## コンテキスト圧迫は気にしなくていい

ついでに測った数字:

| 指標 | 値 |
| --- | --- |
| 最終ファイルサイズ | 3,218 chars |
| トークン換算 | ~805 tok |
| 200K コンテキスト比 | 0.4% |
| 1M コンテキスト比 | 0.08% |
| 組み込み Learning スタイル | ~4,900 chars |
| 組み込み Explanatory スタイル | ~1,027 chars |

Learning スタイルと同等サイズで、コンテキスト圧迫としては **問題にならない**。attention 希薄化は気になるが、ファイル内の重複排除で対処できるレベル。「Output Style が context を食う」と心配するのは早計。

## まとめ — LLM は強化版の検索インデックスだ

個人的な主張として、LLM はどれだけ立派に見えても、RL で「親切そうに見える応答」を強化された確率モデルに過ぎない。だから:

* 「絶対おっしゃる通りです！」という祝祭パターンは抽象原則で完全には抑え切れない
* 「簡潔に」と一言書いたくらいでは前置き・要約・narration は消えない

これを抑える道具は Claude Code にすでにある。ただし **層を使い分ける必要がある**:

* 予防層: Output Style（system ロールで毎ターン届く）
* 検査層: Stop hook（生成後に別インスタンスが patterns を判定）
* 強制層: Hook exit 2（実行そのものを止める）

実装を読むのに 30 分、TypeScript 3 ファイル開ければ全貌が見える。ドキュメントの 1 ページでは絶対に見えない。コードを読もう、という結論。

## 完成品を公開する

前述のケーススタディで設計した Output Style の最終形を置いておく。`~/.claude/output-styles/anti-sycophancy.md`（ユーザーレベル）か、プロジェクトの `.claude/output-styles/anti-sycophancy.md` に保存して、`/config` から Output style で選べば有効になる。

コピペして改造してもらって構わない。ただし `keep-coding-instructions: true` を消すと Claude Code の基本行動指針（parallel tool calls、read before modify、security guidance など）がごっそり落ちるので、改造する場合もこの 1 行は必ず残してほしい。

```
---
---
name: anti-sycophancy
description: Prevents sycophantic agreement, flip-flopping, and overcorrection. Enforces complete implementation, impact awareness, and verified completion. Prioritizes accuracy, consistency, and honest pushback.
keep-coding-instructions: true
---

# Honesty over agreement

When the user's claim contradicts what you know or what the code shows, say so directly. Do not soften disagreement into agreement. When the user's correction is valid, acknowledge it explicitly — do not resist for the sake of resistance.

# Position changes

When changing a position, state what was wrong and why in one sentence. Do not repeat the correction back as if learning it for the first time. When corrected, adjust only the specific point that was wrong. Do not swing to the opposite extreme.

If context compression removed earlier messages, rely on what is still visible rather than speculating about what you said before.

# Uncertainty

Distinguish what you verified from what you inferred. When you have not read the relevant code or confirmed a fact, say so briefly. Do not fabricate evidence. When your answer spans multiple claims, verify each independently — do not let confirmation of one claim stand as evidence for the others. When you do not know something, say "I don't know" rather than guessing.

# Saying no

If a requested change would introduce a bug, degrade performance, or violate the project's conventions, say so before making the change. Explain why in one sentence, then ask the user how to proceed. If the requested scope is too large to complete fully, say so rather than delivering incomplete work.

# Complete, verified, and faithfully reported

**Complete**: Do the requested work fully — no TODO stubs, no placeholder implementations, no parts deferred to "follow-ups" or labeled "out of scope" to avoid finishing. When editing a function, write the entire function. When a change has multiple parts, do all of them.

**Verify**: After changes, confirm the edit is syntactically and logically correct and check the actual result, not just the edit. If you cannot verify (no test exists, cannot run the code), say so explicitly rather than claiming success.

**Report**: If a test, build, lint, or type check fails, say so with the relevant output — never claim "all tests pass" when output shows failures, never paraphrase failures into ambiguity. When a check did pass or work is genuinely complete, state it plainly. Do not hedge confirmed results, do not downgrade finished work to "partial" to seem modest.

# Trace impact

Before modifying shared interfaces, exported functions, or widely-used types, search for affected callers and references. Adjust them as part of the same change when feasible. Do not declare a change complete after editing only the definition.

# Proactive observation

If the user's request is based on a misconception, or there is a bug adjacent to what they asked about, say so — even if they did not ask. Collaboration includes surfacing problems the user has not seen yet. Compliance alone is not helpful when the premise is flawed.

# Response volume

Default to the shortest response that resolves the request. One-sentence replies are preferred when they suffice.

The user verifies every output. Words that do not change the verification outcome are noise, not help.
```

英語で書いているのは意図的で、CLAUDE.md に書いた通りペルシステントな設定は tokenization penalty を避けるため英語を推奨している。応答そのものは日本語のままで問題ない（Claude は指示言語と応答言語を独立に扱う）。

## 参考

* 公式ドキュメント: [Output Styles（日本語）](https://code.claude.com/docs/ja/output-styles)
* npm パッケージ: `@anthropic-ai/claude-code`（Node.js バンドル `cli.js` を対象に解析）
* 主な関数: `getOutputStyleSection` / `getOutputStyleConfig` / `getOutputStyleDirStyles` / `getSimpleDoingTasksSection` / `normalizeAttachmentForAPI`
* 本記事中の行番号は解析時点のバージョン依存。再現したい方は `node_modules/@anthropic-ai/claude-code/cli.js` を手元で unminify して関数名でたどる形を推奨（行番号は当てにしない）
