---
id: "2026-05-02-ai-agent-の半分しかやってないを検出するのにdiff-の正規表現を入れて剥がした話-01"
title: "AI agent の「半分しかやってない」を検出するのに、diff の正規表現を入れて剥がした話"
url: "https://zenn.dev/zoetaka38/articles/5f28338d908dd2"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

AI agent(うちでは Claude Code)に「このチケットを実装しろ」と渡すと、たまに「動いた、commit した、push した」までは進むのに **チケットの半分しか触ってない** ことがある。テストファイルだけ書いて実装ファイルがない、とか、実装はしたがマイグレーションが抜けてる、とか。exit\_code は 0、commit もある、PR も開ける。下流から見ると成功にしか見えない。

この「形式上は完了、内容は未達」をどう検出するかという問題に、自分は半年かけて 2 回設計を変えた。最初は **agent が出した diff の形を見て、チケット本文に書かれてるファイル名が含まれてるかを正規表現で照合する**「diff shape guard」を入れた。最近そのコードを丸ごと剥がして、もともと走らせてた `verify_commands`(チケットごとに「これが通ったら完了」と書いてある shell コマンド) の振る舞い検証だけに一本化した。コミット 1 本で 703 行 net 削除、テスト 280+ 件削除。

shape で見るのを諦めて behavior で見るほうへ収束した、という典型的な話なんだけど、剥がすまでに何回か「もう少し正規表現を直せばいける」と思って粘ったので、その粘った跡と諦めた根拠を残しておく。

## Codens / Purple Codens の前提

うちの Purple Codens は、Notion のチケットを起点に Claude Code を VPS で起動して branch 切って実装させて PR 作る、というワークフローエンジン。ステップは preset で宣言してあって、本記事に出てくる develop / verify は `notion_compatible.json` に書かれている。

```
// backend/src/infrastructure/workflow/presets/notion_compatible.json 抜粋
{
  "id": "develop",
  "type": "claude_code",
  "config": { "model": "opus", "max_turns": 30, "timeout_seconds": 1800 },
  "on_success": "verify",
  "on_failure": "notify_failure"
},
{
  "id": "verify",
  "type": "run_tests",
  "config": {
    "test_command": "{verify_commands}",
    "timeout_seconds": 300
  },
  "on_success": "notify_success",
  "on_failure": "fix_verify"
},
{
  "id": "fix_verify",
  "type": "claude_code",
  "config": {
    "prompt_override": "Verification failed. Fix the issues.\nOutput:\n{previous_step_output}"
  },
  "on_success": "verify",
  "on_failure": "notify_failure"
}
```

`verify_commands` は Notion チケットの property から流し込まれる shell 文字列で、「テスト走らせる」「型チェック走らせる」「ビルドする」のチケット固有のレシピが書いてある。develop が成功したら verify を回し、verify が落ちたら fix\_verify として claude\_code を再起動するループ。これが「振る舞いベース」の検証。

問題は **develop が緑で帰ってきたが diff の中身がスカスカ** という状況をどう拾うかで、当初うちはここに別系統の guard を入れていた。

## 最初に試した: diff shape guard

仕組みはこう。

1. Notion のチケット本文(`notion_body`) を正規表現でスキャンして、書かれているファイル名を抽出する(これを expected\_files と呼ぶ)。
2. develop ステップが終わって commit があった時、agent service から返ってくる `result["diff_files"]`(実際の `git diff --name-only`) と突き合わせる。
3. expected\_files のうち diff に出てこないものがあったら、ステップを fail させる。

中心の正規表現はこれだった。

```
# backend/src/utils/expected_files.py (削除済)
# Matches relative file paths with known source-code extensions.
# Accepts optional leading directory segments (lowercase, hyphens, underscores,
# digits) followed by a filename that may begin with uppercase or digits.
_FILE_PATH_RE = re.compile(
    r"(?:[a-z][a-z0-9_-]*/)*[a-zA-Z0-9][a-zA-Z0-9_.-]*\.(?:py|tsx?|md|sh|ya?ml)"
)
```

抽出対象を `.py` / `.ts` / `.tsx` / `.md` / `.sh` / `.yaml` / `.yml` に絞っている。`docs/design.docx` や `assets/logo.png` を拾うとノイズが増えるので、コードに直接効く拡張子だけ。

カバレッジ判定は suffix match で寛容にしてある。

```
# (削除済) _diff_covers_expected
def _diff_covers_expected(
    diff_files: List[str],
    expected_files: List[str],
) -> Tuple[bool, List[str]]:
    """Return (all_covered, missing_files)."""
    if not expected_files:
        return True, []
    missing = [
        ef
        for ef in expected_files
        if not any(
            df == ef
            or df.endswith("/" + ef)
            or ef.endswith("/" + df)
            for df in diff_files
        )
    ]
    return len(missing) == 0, missing
```

チケットに `notion_sync.py` とだけ書いてあって、agent が `src/infrastructure/notion_sync.py` を触っていたら、suffix match で OK にする。逆も OK。bare filename と full path のどちらが書かれていても拾えるようにしたかった。

呼び出し側は `claude_code.py` で develop ステップ完了直後に挟まっていた(これも削除済)。

```
# backend/src/infrastructure/workflow/steps/claude_code.py (削除済ブロック)
if exit_code == 0 and repos_committed_set and step_type != "resolve_conflicts":
    _guard_body = (
        context.get_var("notion_body", "")
        or context.get_var("task_goal", "")
        or ""
    )
    _guard_expected = _extract_expected_files(_guard_body)
    if _guard_expected:
        _guard_diff_raw = result.get("diff_files")
        if _guard_diff_raw is not None:
            _guard_diff = [f.strip() for f in _guard_diff_raw.split(",") if f.strip()]
        else:
            # VPS が diff_files を返さない場合の fallback
            _guard_diff = _parse_modified_files_marker(output) or _extract_expected_files(output)
        _guard_ok, _guard_missing = _diff_covers_expected(_guard_diff, _guard_expected)
        if not _guard_ok:
            return StepResult.error(
                "チケットが期待する次のファイルが diff に含まれていません: "
                + ", ".join(_guard_missing)
            )
```

最初に入れた時は気持ちが良かった。実例として、チケットに「`src/notion_sync.py` の `_normalize_uv_venv` を呼ぶこと」とあるのに agent がテストファイルしか触っていなかったケースを、guard が "src/notion\_sync.py" と名指しで止めてくれた。fix\_verify ループに乗せれば agent 自身が直しに行く。**振る舞い検証の前にもう一段「ファイルすら触ってない」で落とせる**、というのが投資の動機だった。

## 何が問題だったか — 正規表現を粘ったぶん全部嘘だった

入れてから運用してるうちに、false positive と false negative の両方が継続的に出続けた。直そうとして patch を当てるたびに、「もう一個別の例外パターンがある」と気付く構造で、コードがどんどん厚くなった。

### 1. expected\_files が 0 件で guard 自体が無効化される

最初の落とし穴。チケット本文に **ファイル名が一切書かれていない** ものが、運用してみると半分くらいあった。「○○ の挙動を直す」「○○ のレイアウトを調整する」みたいな自然言語チケット。`_FILE_PATH_RE` は何もマッチしないので `expected_files=[]` になる。

```
# (削除済 docstring)
"""Returns an empty list when no paths are found, which causes the shape guard
to skip (false-positive avoidance for tickets that don't mention specific files)."""
```

意図的にスキップしている。「expected\_files が 0 件のチケットで guard を発火させると false positive で詰む」という選択を上流で迫られた結果なので、これ自体は妥当なんだが、**結果として guard が効くチケットは半分以下** になる。「半分しか守らない網」を維持コストを払って維持している状態。

### 2. 「References」「備考」セクションのファイル名を拾ってしまう

PRD ライクな構造化チケットほどこれを踏む。`## Implementation` と `## References` が並んでいると `_FILE_PATH_RE` は両方拾い、Implementation だけ触って commit すると、References のファイルが diff に無いから guard が fail する。

これに対する patch が直前のコミットで入った除外セクション機構。

```
# (削除済) _EXCLUDED_SECTION_TITLES
_EXCLUDED_SECTION_TITLES = (
    "verification checklist",
    "verify",
    "verification",
    "test plan",
    "tests",
    "テスト",
    "検証",
    "checklist",
    "references",
    "参考",
    "notes",
    "備考",
)
```

これと併せて `_strip_excluded_sections` という関数を導入し、Markdown 見出しを parse して、除外セクション(と subsection)を本文から削ってから regex を回す形にした。`_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)` で見出しを順に走査し、除外見出しに当たったらその下の subsection も `excluded_depth` で propagate して落とす、という実装。日本語(「検証」「備考」「参考」) も英語(「References」「Notes」) も入れた。

これが入った後に CDTSK-1138 の type のチケットでは止まったが、運用してると **「Notes」や「References」じゃない見出しでも参考ファイルが書かれてる** チケットが普通に出てきた。「## Background」「## 背景」「## 関連 PR」「## 過去の議論」。除外セクション一覧は、現場のチケット書き方の流派が増えるたびに膨らむ前提で、自分が `_EXCLUDED_SECTION_TITLES` を追記するか、人間にチケットの見出しを直してもらうか、の二択になっていた。

これをやり続ければ false positive は減るが、**チケット本文の構造を guard 側が把握しにいく** という方向に振っているので、増分のメンテコストが事業価値より重くなる感触があった。

### 3. agent stdout から path を抜くフォールバックが truncation で壊れる

`result["diff_files"]`(VPS の agent service が返してくる real git diff) が無い時のフォールバックとして、agent の stdout を `_extract_expected_files()` で正規表現スキャンしていた。

```
# (削除済 fallback)
_guard_diff = _parse_modified_files_marker(output) or _extract_expected_files(output)
```

これは VPS 側が古い build で `diff_files` を返してこないケースの後方互換用なんだが、stdout が **truncate されている** とパスが途中で切れる。`src/utils/expected_files.py` が `src/utils/expe…` で切れていれば regex は当然マッチしない。「agent はちゃんとファイルを触ったし stdout に出してたが、truncator が刈った」という理由で guard が fail する。

これに対しては、agent に prompt で **`[PURPLE-MODIFIED-FILES] ... [/PURPLE-MODIFIED-FILES]` の marker を最後に出させる** という追加対策を打った(`_parse_modified_files_marker` は今回も剥がさず残してある)。 決定論的に切り出せるし、bracket segment(`app/[locale]/...` のような Next.js dynamic route) のファイルもそのまま通る。`_FILE_PATH_RE` は `[locale]` のせいで拾えなかった。

これで truncation には強くなったが、新しい問題が来る。**agent が marker を出し忘れる**。あるいは出すには出すが範囲が雑(無関係なパスを混ぜる、touched じゃないものまで列挙する) ことがある。Claude は instruction を守ろうとするので守るが、`max_turns` を使い切った時や stop\_reason が `tool_use` のままの時に最後の summary block を出さずに終わる事故が一定確率で発生する。

### 4. lockfile-only diff で no-op marker と組み合わせるパターン

これが一番ややこしくて、guard 設計の前提条件を壊しに来た。

agent が「もうやってあった、何もしない」と判断した時、`[PURPLE-NO-OP-VERIFIED-OK]` という marker を出す約束になっている。これが出ていれば `repos_committed_set` を空にして no-op success として処理する経路がある。

ところが verify\_commands に `npm install` が入っていると、agent が verify 確認のために走らせた `npm install` で `package-lock.json` が再生成されて、それが commit される。 つまり「agent としては no-op を判断したのに、副作用で lockfile が 1 個 commit に乗る」。 このとき shape guard はチケットに書かれている `ReactionBar.tsx` が diff に無いと言って fail させる。チケット側から見るとどこにも問題が起きていないのに `expected files missing: ReactionBar.tsx` で停止する。

これに対しては、shape guard を発火させる前に `_has_already_done_marker(output)` をチェックして、あれば `repos_committed_set = set()` で空にして no-op 経路に流す、という再ルーティングを足した。

shape guard を発火させない条件に **agent の self-report である `[PURPLE-NO-OP-VERIFIED-OK]` を信じる** という分岐を追加した時点で、自分の中で気持ちが折れた。「diff の形を見て partial を検出する」ためのコードが、**agent の自己申告 marker を読んで shape 判定をスキップする方向の分岐** を抱え込み始めた。これは shape guard が前提としていた「agent の出力に依存しない外部観測」とは逆向き。

## verify\_commands に一本化した

ここで一旦立ち止まると、**チケットに `verify_commands` が書いてあるなら、partial implementation の症状は verify が落ちた瞬間に出る** という事実に気付く。

* 「テストだけ書いて実装してない」→ verify でテスト走らせると test\_runner が import error か assertion failure で落ちる
* 「実装だけしてマイグレーション足してない」→ verify で起動すると schema mismatch で落ちる
* 「型注釈と関数本体が食い違う」→ verify で `mypy` か `tsc` が落ちる

shape guard で守りたかった失敗ケースは、ほぼ全部 verify\_commands を真面目に書けば自然に検出される。`run_tests` は `{verify_commands}` を context から取ってきて、`set -x` で trace ON、`(...)` の subshell で囲んで、デフォルト verify とタスク verify を `&&` で繋いで VPS で実行する。

```
# backend/src/infrastructure/workflow/steps/run_tests.py 抜粋
default_verify = context.get_var("default_verify_commands")
task_verify = context.get_var("verify_commands")
if default_verify or task_verify:
    # 各 chunk を subshell で包んで set -x trace
    parts = [f"(set -x; {p}) 2>&1" for p in [default_verify, task_verify] if p]
    test_command = " && ".join(parts)
```

subshell で囲むのは、project-level default の `cd dir` が次の chunk に漏れない(dash で `cd` 失敗が exit 2 を返す事故を避ける) ため。`set -x` の trace 行は `_parse_step_failure` で「最後に走った command = 落ちた command」を抜き出す材料になる。

落ちたら preset の `on_failure: fix_verify` で claude\_code に戻る。`prompt_override` に `previous_step_output`(verify の stderr tail)を埋め込んで、agent に「これが落ちてるから直せ」と渡す。fix\_verify の on\_success は再び verify に戻り、また落ちたら fix\_verify…という最大 2 回までのループ。

つまり、shape guard が「**ファイルが diff に存在するか**」を構文的に見ていたのに対して、verify\_commands は「**チケットに書かれた完了条件が実際に true になるか**」を意味的に見ている。重なってるどころか、後者のほうが厳密に強い。shape guard で守れて verify\_commands で守れない例を探したが、思いつくのは「verify\_commands を書き忘れたチケット」だけで、それは guard を入れる側の議論ではなく **チケット入力の必須項目** を増やす側の議論だった。

## 結果と残った教訓

コミット 1 本(911005fd)で:

* `backend/src/utils/expected_files.py`: 130 行削除、`_FILE_PATH_RE` / `_HEADING_RE` / `_EXCLUDED_SECTION_TITLES` / `_strip_excluded_sections` / `_extract_expected_files` / `_diff_covers_expected` を全削除
* `backend/src/infrastructure/workflow/steps/claude_code.py`: 66 行差(削除主体)、shape guard 呼び出しブロックを丸ごと削除
* `backend/tests/unit/utils/test_expected_files.py`: 264 行削除(`_extract_expected_files` の正規表現バリエーション、`_strip_excluded_sections` の見出しスコープ、`_diff_covers_expected` の suffix match パターン)
* `backend/tests/unit/infrastructure/workflow/steps/test_claude_code_step.py`: 200 行以上削除(integration test 2 本含む)

合計で 742 行削除、39 行追加、net 703 行マイナス。テスト 280+ 件削除。半年弱前の `d3027d19 feat: diff-based shape guard` で入れて、何度か直して、最後は丸ごと取った。

得た教訓は 3 つ。

**1. AI 出力検証で shape heuristic は false positive で運用コストが膨れる。** 正規表現は最初の 1 本目を書いた時点では「これで何ケース守れる」と数えられるが、運用に出すと「正しく fail させたいケース」と「fail させたくないケース」を切り分けるための除外条件が増え続ける。除外条件はチケットの書き方の流派(References セクションの位置、見出しの言語、bracket segment の有無、副作用ファイルの種類) に依存していて、**agent や human が書く自然言語の構造** を guard 側が引き受けることになる。これは sustainable じゃない。

**2. behavior 検証は重いが意味的に強い。** verify\_commands は VPS で実プロセスを起動するので shape guard より圧倒的にコストがかかる(数秒〜数百秒)。だが「テストが通る」「ビルドが通る」「型が通る」は **何も書かなくても agent 自身が実装の正しさを判定できる** 言語非依存の signal で、partial 実装はほぼ確実にこのどれかで落ちる。shape は「どこを変えたか」、behavior は「何ができるようになったか」を見る。partial 実装の本質は後者の欠落なので、後者で見ればいい。

**3. agent self-report marker は限定スコープなら残せる。** `[PURPLE-NO-OP-VERIFIED-OK]` は今回も剥がさず残した。これは「shape を判定する」のではなく「**no-op fallthrough という限定された経路を agent から手動で開ける**」用途に使う marker で、 信じる範囲を `repos_committed_set` を空にして no-op success に流すという 1 個の決定だけに絞ってある。 shape guard を agent self-report に依存させた瞬間に責務が広がりすぎて破綻したのとは対照的に、こちらは「agent が `[PURPLE-NO-OP-VERIFIED-OK]` を出さなかったらこの分岐に入らない」というだけのスイッチで、failure mode が予測できる。 self-report の責務範囲は **fail-safe な方向(=何もしない、success に倒す)** だけにする、という運用ルールに落ちた。

## まとめ

AI dev pipeline で「shape で判断したくなる衝動」と「behavior で判断する判断」のバランスは、感覚的には **shape を入れたくなった時点で、その shape は behavior 検証の代用になっていないか** を疑うのがちょうどいい。今回も「ファイルが diff にあるか」は「verify が通るか」の弱い proxy で、proxy だけ強化していくと False positive 除外の patch を重ねるだけになった。最終的に proxy を捨てて本体だけ回せば、コードは 700 行軽くなり、テストは 280 本減り、運用ルールは 1 本に減った。

似たような diff-shape guard を入れて hama った人いれば、何で剥がしましたか(あるいは粘り続けてますか)。「除外セクション一覧が膨らみ続けている」現象は同種の guard なら必ず通る道だと思っていて、自分以外の決着の付け方を聞いてみたい。
