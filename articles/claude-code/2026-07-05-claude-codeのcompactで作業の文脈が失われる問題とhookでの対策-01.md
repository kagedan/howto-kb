---
id: "2026-07-05-claude-codeのcompactで作業の文脈が失われる問題とhookでの対策-01"
title: "Claude Codeのcompactで作業の文脈が失われる問題とhookでの対策"
url: "https://qiita.com/hiranuma/items/60cd5dbf642e346f8be7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "LLM", "Python", "qiita"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-rss"
query: ""
---

Claude Codeで少し長い作業をしていると、あるタイミングからエージェントの挙動が急に変わることがあります。さっきまで実機で確認してから配置すると合意していたはずなのに、次のターンでは検証を飛ばして配置先を上書きしにいく。一度失敗して取り下げたショートカットを、また同じ手順で試そうとする。plan modeを抜けた状態で勝手に実装を続行する。

これはモデルの能力が落ちたわけではありません。会話履歴の圧縮、いわゆるcompactが間に挟まっているからです。エージェントに長い仕事を任せるほど、この現象は避けて通れなくなります。ここでは、compactでエージェントが何を失うのか、そしてそれをhookと状態ファイルでどう補えるのかを、実際に運用している構成に沿って書いていきます。プロンプトを工夫する話ではなく、エージェントの記憶をどう永続化して復旧させるかという、環境側の設計の話です。

## compactが実際にやっていること

Claude Codeのcompactは2つの経路で走ります。1つは手動で、`/compact`を明示的に叩くと任意のタイミングで発火します。もう1つは自動で、セッションのcontext使用率が上限近くに達すると、Claude Code側の判断でターンの区切りに割り込んで走ります。自動のほうは宣言なしに動くので、体感としては気付いたら圧縮されていたという形になります。発火点はおおむね上限の9割前後で、環境変数（`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`で割合指定）によって前後にずらせます。

どちらの経路でも中身は同じです。それまでの会話履歴をLLMに渡して自然文の要約を作らせ、要約と直近のターンとsystem promptを組み合わせて新しいcontextを組み直します。つまりcompact後のエージェントが見ているのは、生の履歴ではなく圧縮された物語です。しかも一度圧縮が走ると、圧縮前の生ログには戻れません。非可逆な操作である点が、後で重要になります。

仕組みとしてはこれだけですが、やっかいなのは要約というやり方そのものです。

## compactの要約では、判断や理由が抜け落ちる

compactの要約は、何をやったかを物語のようにまとめたものになります。ファイルをこう変更した、この案を検討した、テストを走らせた、といった行動の記録は比較的よく残ります。ところが、なぜその選択をしたのか、どの案を却下したのか、今どのフェーズにいるのか、といった判断のほうは要約の過程で薄まっていきます。要約はあくまで過去の作業記録で、次に何をすべきかという指示ではありません。このズレが、圧縮後の誤動作につながります。

私が実際にやられたパターンは、だいたい次の4つです。抽象論ではなく、直近のセッションで起きた具体的な事故として並べます。

- 採用案と却下案の取り違え。セッション途中で案Aを捨てて案Bに切り替えたのに、要約には案Aを検討したことだけが残る。圧縮後のエージェントはその案Aを実装し始める
- フェーズの混同。実機で確認してから配置すると合意していたのに、要約からその順序制約が抜け、圧縮後は完成イメージだけを見て検証を飛ばし、配置先をそのまま上書きする
- 却下理由の消失。一度試して失敗し撤回したショートカットを、要約は試みた手順としてだけ残す。なぜダメだったかが持ち帰られないので、圧縮後に同じ手順を再実行して同じ地雷を踏む
- 原則とセッション状態の喪失。配置先を直接編集せず管理元のrepositoryを編集して配布する、といったセッション中に確立した原則が抜け落ち、短期的には動くが再現できない直接編集に走る。plan modeを抜けた状態で作業を続行したり、tmuxで並走中のworkerの存在を忘れて自分で手を動かし始めたり、固定していたテストの目的を見失って周辺調査へ脱線したりもする

どれも原因は同じで、判断と状態が要約から抜け落ちることにあります。たまたま起きた事故ではなく、標準のcompactの仕組み上どうしても出てくる失敗です。だとすれば、対策もプロンプトの工夫ではなく、仕組みで押さえるしかありません。

## 要約に残らない情報を、圧縮の前に書き出しておく

やることはシンプルです。要約には残りにくい判断やセッションの状態だけを、圧縮が走る前に外部ファイルへ書き出しておく。そして圧縮の直後に、そのファイルを必ず読み直させる。この2つが噛み合えば、要約で薄まった情報を圧縮の外側から補えます。

私の環境では、これを3つのパーツで組んでいます。圧縮前に状態を書き出すskill、圧縮の直後に保存した状態を読み直させるhook、そして自動compactに先を越されないための通知です。順に見ていきます。

## 圧縮前に判断や状態を書き出すskill

`/compact`を叩く前に、user側から明示的に起動するslash commandとしてskillを1つ用意しています。名前は`/pre-compact-save`。やることは、現セッションから圧縮サマリーへ残りにくい情報だけを抜き出し、固定パスの状態ファイル（`${TMPDIR}/claude-session-state/<session_id>.md`）へ決まったフォーマットで保存することです。

保存する項目は、要約に載りにくいものを優先します。

- 現在のplan（planファイルの絶対パスと現在フェーズ）
- 現在フェーズ（今どの段階にいるか）
- タスク状況（in-progressのタスクと補足）
- 判断ログ（採用した案、却下した案、そして却下した理由）
- 制約・ブロッカー（検証してからデプロイ、のような順序制約を含む）
- worker構成（tmuxなどで並走中のpane、role、担当）
- 編集中ファイル（未保存・未検証のファイルと注意点）
- 復旧メモ（圧縮後の自分への手紙。次の一手と、踏んではいけない地雷）

設計でいちばん気をつけているのは、書いたつもりで中身が壊れているのを防ぐことです。ここは人間の善意に頼らず、機械的に強制します。session_idが取れなければ推測名でファイルを作らせずに停止させるhard gate。見出しの順番を固定して、書き終わったあとにファイルを読み返し、必須の見出しが欠けていないか検知させるforcing function。副作用を絞るためにallowed-toolsを最小限に制限する。この3点で、状態ファイルが中途半端なまま残る経路を閉じています。

要約をAI任せにするのではなく、決まった形式で記録を書かせる。この一手間で、圧縮後にどこまで戻せるかが変わってきます。

skillの実体は次のとおりです。`~/.claude/skills/pre-compact-save/SKILL.md` に置きます。frontmatterの`strict_procedure`と`allowed-tools`が強制の要で、手順の各ステップは判断と状態を漏れなく書き出すことに寄せています。

```markdown
---
name: pre-compact-save
description: |
  Claude Code の /compact 実行前に、現セッションの作業状態を一時 state file へ保存する。
  MANDATORY TRIGGERS: /pre-compact-save, pre-compact-save, 圧縮準備, compact 準備, コンパクト準備, 圧縮前状態保存, セッション引き継ぎ準備。
  DO NOT TRIGGER: compact 後の復旧、通常の進捗報告、plan 作成、context 使用率の雑談。
strict_procedure: true
argument-hint: "[復旧メモ]"
allowed-tools: Read Write Bash(~/.claude/scripts/get-session-id.sh *) Bash(mkdir *) Bash(date *) Bash(pwd) Bash(ls ~/.claude/plans/*) TaskList
---

# pre-compact-save

Claude Code の `/compact` 前に、圧縮サマリーへ残りにくい作業状態を
`${TMPDIR}/claude-session-state/${SESSION_ID}.md` へ保存する。

圧縮の要約は「何をやったか」の物語になり、「なぜその選択をしたか」「どの案を却下したか」
「今どのフェーズか」「どの worker に何を委譲したか」といった判断構造・セッション状態が薄まる。
このスキルはそれらを構造化して先に書き出し、圧縮後の自分が確実に復元できるようにする。

## Strict procedure profile

- Strictness: strict-procedure。圧縮前 state file の内容と保存完了報告が成果そのもの。
- Hard gate: session_id が取得できない場合は state file を推測名で作らず、取得不能として停止する。
- Forcing function: 保存先パスを固定し、保存後にファイルを読み返して必須見出しの有無を確認する。
- Completion receipt: state file パス、保存した主要項目、未確認項目、次に実行する `/compact` 案内を報告する。

## 手順

1. session_id を取得する。
   - `~/.claude/scripts/get-session-id.sh` を実行する。
   - 取得できない（空 or exit 1）場合は state file を作らず、
     「session_id が取得できないため準備未完了」と報告して停止する（Hard gate）。
2. 保存先を `${TMPDIR:-/tmp}/claude-session-state/${SESSION_ID}.md` に決める。
   - 事前に `mkdir -p "${TMPDIR:-/tmp}/claude-session-state"` を実行する。
3. TaskList、active plan file、tmux/worker 状態、編集中ファイルを確認する。
   - active plan file は `~/.claude/plans/` 配下の該当ファイルを Read で読む。
   - plan / worker を使っていない場合は各項目に「未使用」と記録する。
4. state file に以下の見出しをこの順で保存する（欠けさせない）。
   - `# セッション引き継ぎ状態`
   - `## 現在の plan`（plan file の絶対パスと現在フェーズ／ステップ）
   - `## 現在フェーズ`
   - `## タスク状況`（in-progress タスクと補足）
   - `## 判断ログ`（採用した案／却下した案／却下した理由）
   - `## 制約・ブロッカー`
   - `## worker 構成`（tmux などで並走中の pane / role / 担当。無ければ「未使用」）
   - `## 編集中ファイル`（未保存・未検証の注意点）
   - `## 復旧メモ`（圧縮後の自分への手紙。引数の復旧メモがあれば必ず含める）
5. active plan file がある場合は、そのパスを
   `${TMPDIR:-/tmp}/claude-session-plan/${SESSION_ID}` にも書く（復旧 hook が読む pointer file）。
   - `mkdir -p "${TMPDIR:-/tmp}/claude-session-plan"` の後に書く。
6. 保存後に state file を Read で読み直し、上記見出しがすべて存在することを確認する。
   - 欠けている見出しがあれば追記して再確認する。
7. ユーザーに「準備完了。`/compact` を実行してください。」と伝える。
```

`get-session-id.sh`はセッション固有のIDを返す小さな補助スクリプトで、状態ファイルの名前をセッションごとに一意にするために使います。hard gateがここに掛かっているのは、IDが取れないまま推測名でファイルを作ると、圧縮後に別セッションの状態を読み込む事故につながるからです。

## 圧縮の直後に、保存した状態を読み直させるhook

状態ファイルを書いても、圧縮後のエージェントがそれを読まなければ意味がありません。ここがいちばん厄介なところで、Claude Codeのhookの仕様がそのまま設計の制約になります。

圧縮はPostCompactというイベントで拾えます。ところがPostCompact hookはadditionalContext、つまりcontextへ差し込むテキストを返せない仕様です。圧縮直後のエージェントに指示を直接注入する経路がここにはありません。圧縮の前に走るPreCompact hookはadditionalContextを返せますが、これは要約がまだ存在しない段階で動くので、圧縮後の復旧指示を届ける用途には向きません。結局、圧縮後のエージェントへ指示を差し込めるのは、次のuserの発話を受けるUserPromptSubmitイベントだけになります。

そこで2段に分けます。

1. PostCompact hookは、session_idでmarkerファイルを1つ書くだけにする。指示は入れず、圧縮が起きたという事実だけを記録する
2. 次のUserPromptSubmit hookがそのmarkerを検出したら、additionalContextで復旧指示を注入し、markerを消す（一度きりの発火）

注入する復旧指示は、planファイルを読み直してフェーズと制約を確認せよ、状態ファイルを読んで判断ログと復旧メモを最優先で復元せよ、TaskListで現在のタスクを確認せよ、そして圧縮サマリーの次の一手は仮説として扱い、planと状態ファイルとrulesのほうを正とせよ、という内容です。additionalContextには1万文字という上限があるので、生ログを丸ごと戻すのではなく、読み直すべき場所を指し示すポインタとして使うのが現実的です。

ここで工夫が要るのが、hook同士のつなぎ方です。Claude Codeには、hook同士で状態を共有する共通の仕組みがありません。だからファイルシステム上のmarkerが唯一の通信路になります。PostCompactは圧縮が起きたかどうかだけを知り、UserPromptSubmitは復旧指示を注入するかどうかだけを知る。それぞれの責務は単一で、状態はmarkerが存在するかしないかだけで表現されます。圧縮が起きていない通常のターンでは、UserPromptSubmit hookはファイルの有無を1回確認して即座に抜けるので、実質的なコストはありません。全体をfail-openにしてあるので、hookが壊れてもClaude Code本体は止まりません。

1段目のPostCompact hookは、markerを書くだけの薄い実装です。`~/.claude/hooks/mark-compaction.sh` に置きます。

```bash
#!/bin/bash
# PostCompact フック: 圧縮が起きたことだけを marker で記録する薄い hook。
# PostCompact は additionalContext を返せないため、ここで指示は注入しない。
# 実際の復旧指示は次ターンの UserPromptSubmit フック (restore-after-compaction.sh)
# がこの marker を見つけて注入する。
#
# fail-open: 何があっても exit 0 で抜け、Claude Code 本体を止めない。

set -uo pipefail

INPUT=$(cat)
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty' 2>/dev/null || true)
[[ -z "${SESSION_ID:-}" ]] && exit 0

# 「直前に圧縮が走った」印を置く（次ターンの UserPromptSubmit が回収する）
MARK_DIR="${TMPDIR:-/tmp}/claude-compaction-mark"
mkdir -p "$MARK_DIR" 2>/dev/null || true
printf '%s\n' "$(date +%s)" > "$MARK_DIR/$SESSION_ID" 2>/dev/null || true

# 圧縮が走ったら context 警告の cooldown を解除し、次サイクルで再通知できるようにする
SENT_DIR="${TMPDIR:-/tmp}/claude-ctxwarn-sent"
rm -f "$SENT_DIR/$SESSION_ID" 2>/dev/null || true

exit 0
```

2段目のUserPromptSubmit hookが、そのmarkerを検出したときだけ復旧指示を注入します。`~/.claude/hooks/restore-after-compaction.sh` に置きます。planファイルと状態ファイルの存在を確認し、あるものだけを読み直し対象として指し示します。

```bash
#!/bin/bash
# UserPromptSubmit フック: PostCompact が残した圧縮 marker を検出したら、
# additionalContext で復旧手順を一度だけ注入する。
#
# marker が無ければ test -f 一回で即抜けるので、通常ターンのコストはほぼ 0。
# fail-open: 常に exit 0。

set -uo pipefail

INPUT=$(cat)
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty' 2>/dev/null || true)
[[ -z "${SESSION_ID:-}" ]] && exit 0

# 圧縮 marker が無ければ何もしない
MARK="${TMPDIR:-/tmp}/claude-compaction-mark/$SESSION_ID"
[[ -f "$MARK" ]] || exit 0
rm -f "$MARK" 2>/dev/null || true   # 一度きり（次ターンでは発火しない）

# plan pointer から現在の plan ファイルパスを引く
PLAN_FILE=""
PTR="${TMPDIR:-/tmp}/claude-session-plan/$SESSION_ID"
if [[ -f "$PTR" ]]; then
  PLAN_FILE=$(cat "$PTR" 2>/dev/null || true)
  [[ -f "$PLAN_FILE" ]] || PLAN_FILE=""
fi

MSG="[復旧] 直前に圧縮が走った。作業を再開する前に次を必ず実行すること。"
if [[ -n "$PLAN_FILE" ]]; then
  MSG+=$'\n'"- plan ファイル \`${PLAN_FILE}\` を読み直し、現在フェーズと制約を確認する"
  MSG+=$'\n'"- plan mode が解けていたら、plan が残っているのでユーザーに再突入の要否を尋ねる"
fi
STATE="${TMPDIR:-/tmp}/claude-session-state/$SESSION_ID.md"
if [[ -f "$STATE" ]]; then
  MSG+=$'\n'"- 状態ファイル \`${STATE}\` を読み、判断ログと復旧メモを最優先で復元する"
fi
MSG+=$'\n'"- TaskList で現在のタスクを確認する"
MSG+=$'\n'"- 圧縮サマリーの次の一手はあくまで仮説。plan・状態ファイル・rules を正とする"

jq -n --arg m "$MSG" '{
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext: $m
  }
}'
exit 0
```

これで圧縮直後の1ターン目から、自分は今planのこのフェーズの途中で、このworkerにこれを委譲済みだ、という状態に戻れます。

## 自動compactに先を越されないための通知

ここまでの2つは、手動`/compact`の前後で何かをする設計です。user自身が状態を書き出してから`/compact`を叩く、という順番が前提になっています。ところが自動compactは宣言なしに走るので、この順番を守れません。自動compactに先を越されると、状態ファイルが保存されないまま生ログが要約に潰され、復旧の材料そのものが消えます。

対策は、自動compactが走る前に、user自身が手動で状態を書き出してから圧縮に入れる状態を作ることです。そのために、context使用率が一定を超えたら通知を出すようにしています。

閾値は60%に置いています。自動compactの発火点である9割前後からは十分に手前です。通知が発火点に近すぎると、userがそのターンで気付いても、次の作業ターンで自動compactが先に走ってしまう余地が残ります。安全側に振って3割分のマージンを取っておく。加えて、60%で通知が来た時点でまだ3割分の作業余力があるので、中途半端な状態で即座に圧縮へ飛ばず、区切りの良いところまで進めてから状態を書き出せます。集中していると使用率には気付きにくいので、主観の区切りではなくタイマーとして機械的に割り込ませる、という狙いもあります。

この60%という数字は、1M contextを前提にしてはじめて意味を持ちます。標準の200K contextだと60%は120K tokenで、通知が来た時点で残り枠が少なすぎて即圧縮するしかありません。1M contextであれば60%は約600K tokenに相当し、通知を受けてから区切りまで作業を続けても、余裕を持って状態の書き出しと圧縮に持ち込めます。1M contextは現時点でOpus 4.7や4.8、Sonnet 5、Fable 5で有効にできるので、長時間のエージェント運用を本気でやるなら、まず枠を広げる前提を整えるのが先になります。

実装は既存の部品への追加で足ります。毎ターンのstatusLine更新時にcontext使用率を計算しているので（statusLineにはinput token基準の使用率が渡ってきます）、そこに閾値超過でwarn markerを書く分岐を足す。もう1つのUserPromptSubmit hookがそのwarn markerを検出したら、区切りの良いところで状態を書き出すことを提案せよ、という指示を注入する。使うmarkerは、これから通知したいというwarn marker、もう通知したというcooldown marker、そして圧縮直後を表すmarkerの3種類です。それぞれのhookは自分の責務に対応する1種類のmarkerだけを読み書きします。

statusLine側は、使用率を計算している既存の処理の末尾に、閾値超過でwarn markerを書く分岐を足すだけです。context使用率はinput token基準（`total_input_tokens / context_window_size`）で出しています。cooldown marker（`claude-ctxwarn-sent`）があるときは書かないので、1サイクルで何度も通知が飛ぶことはありません。

```python
# --- context window 使用率: バー表示 + pre-compact-save 60% warn marker ---
pct_ctx = None
try:
    cw = d.get("context_window") or {}
    total_in = cw.get("total_input_tokens")
    size = cw.get("context_window_size")
    if total_in and size:
        pct_ctx = float(total_in) / float(size) * 100.0
except Exception:
    pct_ctx = None

# 60% 超で pre-compact-save 警告 marker を書く（cooldown 中は書かない）。
# UserPromptSubmit hook (context-budget-warn.sh) が拾う。
try:
    sid = d.get("session_id")
    if sid and pct_ctx is not None and pct_ctx >= 60.0:
        tmp = os.environ.get("TMPDIR", "/tmp")
        warned = os.path.join(tmp, "claude-ctxwarn-sent", sid)
        if not os.path.exists(warned):
            warn_dir = os.path.join(tmp, "claude-ctxwarn")
            os.makedirs(warn_dir, exist_ok=True)
            with open(os.path.join(warn_dir, sid), "w") as f:
                f.write(str(int(round(pct_ctx))))
except Exception:
    pass
```

warn markerを拾って提案を注入するのが、もう1つのUserPromptSubmit hookです。`~/.claude/hooks/context-budget-warn.sh` に置きます。注入後にwarn markerを消してcooldown markerを立て、次の圧縮まで再通知を止めます。

```bash
#!/bin/bash
# UserPromptSubmit フック: statusline が置いた context 警告 marker を検出したら、
# 区切りで /pre-compact-save を促すメッセージを一度だけ注入する。
#
# marker が無ければ即抜け。fail-open で常に exit 0。

set -uo pipefail

INPUT=$(cat)
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty' 2>/dev/null || true)
[[ -z "${SESSION_ID:-}" ]] && exit 0

WARN="${TMPDIR:-/tmp}/claude-ctxwarn/$SESSION_ID"
[[ -f "$WARN" ]] || exit 0

PCT=$(cat "$WARN" 2>/dev/null || true); PCT=${PCT:-"?"}
rm -f "$WARN" 2>/dev/null || true   # 一度きり

# cooldown を立て、次の圧縮まで再通知しない
SENT_DIR="${TMPDIR:-/tmp}/claude-ctxwarn-sent"
mkdir -p "$SENT_DIR" 2>/dev/null || true
printf '%s\n' "$(date +%s)" > "$SENT_DIR/$SESSION_ID" 2>/dev/null || true

MSG="[context 残量] 使用率が ${PCT}% に達した。"
MSG+=$'\n'"- 作業の区切りで、ユーザーに \`/pre-compact-save\` の実行を勧める"
MSG+=$'\n'"- 実行後は \`/compact\` を案内する"
MSG+=$'\n'"- scope 縮小や別セッション化ではなく、圧縮前の状態保存で対処する"

jq -n --arg m "$MSG" '{
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext: $m
  }
}'
exit 0
```

最後に、これらのhookを`~/.claude/settings.json`へ登録します。PostCompactに1つ、UserPromptSubmitに2つ（圧縮直後の復旧とcontext残量の通知）を並べます。UserPromptSubmitは複数登録でき、毎ターン両方が走りますが、markerが無ければ即座に抜けるので通常時のコストは無視できます。

```json
{
  "hooks": {
    "PostCompact": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/mark-compaction.sh" }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/restore-after-compaction.sh" }
        ]
      },
      {
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/context-budget-warn.sh" }
        ]
      }
    ]
  }
}
```

## 運用してみて変わったこと

この構成に落ち着いてから、1セッションで10回近くcompactが挟まっても、論理の破綻がほとんど起きなくなりました。圧縮起因の作業ロスはほぼゼロになり、却下したはずの案を再提案してくる現象は消え、plan modeの維持もできるようになりました。複数workerを並走させているときのtopology忘却もなくなっています。

派生的な効果もあります。context残量の通知は、今どのフェーズにいて何を残しているのかを強制的に棚卸しさせるので、区切りの判断そのものが整理されます。エージェントのために状態を書き出す作業が、そのまま自分の頭の整理にもなっている、という副産物です。

## 判断を残す設計が、これからの仕事になる

compactの問題は、つい書き方の工夫で直そうとしがちです。しかし要約が判断を薄めるのは仕組み上の性質なので、プロンプトを変えても解決しません。実際に役立つのは、判断を圧縮の外側に保存しておき、圧縮後に必ず読み直させるやり方のほうです。エージェントのcontextを、放っておけば消える会話ログではなく、きちんと保存して戻すべき作業状態として扱う。まずはこの見方に切り替えるところからだと思います。

コードを書く比重をAIに移せば移すほど、人間の仕事は現場のこまごました制約と判断を、AIが忘れない形で残す設計へと寄っていきます。案を却下した理由、検証してからデプロイするという順序、直接触ってはいけない配置先。こうした判断こそ、人間がその場に持ち込んでいる価値です。それをどう引き継ぐかを設計することが、これからのエンジニアリングの中身になっていくのではないでしょうか。
