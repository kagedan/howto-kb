---
id: "2026-07-14-herdr-を活用した-codex-とのオーケストレーション用-claude-code-plugin-01"
title: "herdr を活用した Codex とのオーケストレーション用 Claude Code Plugin を作ってみた"
url: "https://zenn.dev/genda_jp/articles/46745564b7a9dd"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-07-14"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

## はじめに

株式会社GENDA 開発部エンジニアの奥山です。  
先日、「Claude Code サブエージェントのネスト機能で `.claude/agents/` の定義が効いた話」を書きました。  
あちらはサブエージェントを「深さ方向」に積む話でしたが、今回は「並走」の話を含んでいます。

<https://zenn.dev/genda_jp/articles/16d35ffa464d65>

Claude Code をメインに業務している私ですが、直近その作業セッションの隣に Codex を常駐させて相談役にするオーケストレーションを herdr という terminal multiplexer 上に組みました。  
その仕組みを plugin としてまとめたので、そこに至る流れを書き残しておきます。

## きっかけになった 3 つの流れ

タイミングとして 3 つの流れが同時に重なりました。

### herdr の存在を知った

以前までは Supacode を使ってコーディングエージェントとともに開発を行っていました。  
Git Repository をフォルダのように扱い、Worktree を Workspace としてその中で管理するような UI になっていたのが個人的に好きでした。  
Worktree 作成を検知して自動的に管理に入れてくれる点もよかったです。

<https://supacode.sh/>

最近 herdr という tmux のような terminal multiplexer の存在を知り、今はこれに乗り換えています。  
以前 tmux に関する記事を書きましたが、直近は Claude Code 自体がサブエージェントをうまく活用してくれるようになったため、tmux で自作のオーケストレーションを組む需要も自分の中では薄れてきていました。

<https://herdr.dev/>

初感として以下の点に惹かれました。

#### tmux にワークスペース管理を標準機能として追加したようなもの

Supacode のような "Repository > Worktree" のような管理もできるようになっているため、この点は自分にフィットしました。

#### 動いているエージェントの一覧が左下に集約

複数のコーディングエージェントを同時に動かしていてもステータス(working / blocked / done / idle)が 1 箇所で追えるので、multiplexer 上での現状把握コストが下がるのが嬉しいポイントでした。  
クリックすることで該当する terminal にジャンプできるのもありがたいです。

#### 公式のコーディングエージェント向け skill

最初からコーディングエージェント向けのドキュメントが備わっていることになり、skill 経由で自然言語による herdr 操作ができる点がユーザー体験として良かったです。  
例えば「先述のステータスが idle になるまで待機する」といったコマンドも作れます。  
skill にも待機や pane 操作の記述例が備わっているため、オーケストレーションを組み立てやすそうだと感じました。

### Codex の使いどころに悩んでいた

私は業務で Claude Code と Codex を使っていますが、契約しているプランは Claude Code の方が上のためこれをメインに使っています。  
Codex はレビュー品質が良いように感じていたため Claude Code で実装した内容を `codex exec` でレビューさせることが多かったです。

技術記事やSNSを見ていると実装の速度や品質もいいという話があったりして実装役を任せてみたいという気持ちがあった中、 Claude Code で整備した custom sub-agent や hooks 等を引き続き使いたいという気持ちもあり、結局 Claude Code ばかり使っていました。

### GPT 5.6 の登場

そんな時に GPT 5.6 (Sol, Terra, Luna)が登場しました。  
Sol の統合力・Terra の安定性・Luna のコストパフォーマンスなどが評価されているように見えています。  
Claude Code に勝る点が多くあると感じたのでこれは活用したいと思い、直近知った herdr も活用したオーケストレーションの仕組みを考えよう、となったのが本記事の経緯です。

## 目指した形

Claude Code をメインに使っている自分にとって、まず思い浮かんだのは「Claude Code に Codex を添えて、相談役と実装のレビュー・担保役を任せる」という構成でした。  
Claude Code が要件整理から実装まで進めつつ、判断が重い場面や書き上げた実装のレビューが必要な場面で Codex に振る形です。

* Claude Code: メイン。要件整理から実装までを進める主体。実装の具体作業自体は sub-agent に委譲する
* Codex buddy: 高リスク判断（アーキテクチャ選定・セキュリティ判断・原因特定が難航しているケース）の独立検証と、書き上げた実装のレビュー・担保を担う。同じタブ内の別 pane に常駐する
* Claude Code sub-agent: 探索・実装・テスト実行など具体作業の委譲先

なお、この Claude Code + Codex + sub-agent の構成は、複数 Issue を並行して進めたい場面でも軸として活用します。  
1 層目 Claude Code に「Issue 分解」「複数の 2 層目 Claude Code のオーケストレーション」役を追加し、分解した Issue 単位で 2 層目 (Claude Code + Codex の同構成) を並列に立ち上げる形にします。

* **1 層目**: 要件整理と Issue 分解に加え、複数の 2 層目 Claude Code をオーケストレーションする役目を担う
* **2 層目 (Issue × N)**: 1 層構成と同じく Claude Code に Codex を横付けし、実装作業は sub-agent に委譲する。分解された Issue 単位で必要な数を並列に立ち上げる
* **タブ間**: 1 層目が各実装タブを立ち上げ、実装タブが詰まったら 1 層目にエスカレーションで返す

## plugin にした経緯

最初は個人の CLAUDE.md や skill にこの契約を直書きしようとしていました。  
ただ、この構成は自分の環境の他の部分と疎結合に保ちたい、という意識がありました。  
密結合のまま埋め込むと、次の 2 点の問題が出ます。

* **改修コスト**: 契約（役割分担・相談基準・実装タブ立ち上げ時の初期 prompt など）が CLAUDE.md や複数の skill に散らばると、少しの調整のたびに横断編集が必要になる
* **将来の切り離し**: 今は herdr を使っているが、multiplexer を乗り換えたり、そもそも使わなくなる可能性はある。CLAUDE.md や skill に埋め込んでしまうと関連する記述だけを選んで剥がすのは骨が折れる

これらを避けるため plugin として切り出すことにしました。  
plugin 開発の経験もなかったのでちょうど良かったです。

plugin と聞くとオンラインの marketplace から取ってくるイメージが強いですが、ローカルの marketplace として運用することもできます。  
`/plugin marketplace add ~/path/to/marketplace` (`.claude-plugin/marketplace.json` を含むディレクトリを指定) を一度だけ叩けば、あとは plugin 変更後に `/plugin marketplace update` で更新が反映されます。  
検証時も `claude --plugin-dir <path>` で読み込ませて叩けるので、取り外しも自由です。

## できたもの

名前の候補は `baton` / `tandem` / `maestro` / `ensemble` などが出てきましたが、最終的に `baton` を採用しました。  
指揮棒（階層オーケストレーション）とリレーのバトン（要件 → 実装のハンドオフ）のダブルミーニングで、両方の意味が本 plugin の構造とちょうど重なっていたためです。  
短くて呼びやすく、愛着が沸きそうな名前を選ぶのも隠れたポイントだと思います。

次のようなレイアウトで置いています。

```
.claude-plugin/
  marketplace.json          # ローカル marketplace
plugins/
  baton/
    .claude-plugin/
      plugin.json           # plugin メタデータ
    skills/
      kickoff/SKILL.md
      codex-buddy/SKILL.md
      escalate/SKILL.md
```

skill は 3 本構成に落ち着いています。

* `baton:kickoff`: 意図的に呼ぶ唯一のエントリポイント
* `baton:codex-buddy`: 各 Claude Code が「今 Codex に聞くべきか」の基準と、聞いたときの契約（結論のみ返してもらう等）を持つ
* `baton:escalate`: 実装タブの Claude Code が詰まったときに、要件タブへ送るメッセージの書式と経路

ユーザーは要件付きで `baton:kickoff` を呼ぶだけ、`baton:codex-buddy` と `baton:escalate` は Claude Code の自律判断で発火します。

各 skill の SKILL.md も貼っておきます。

baton:kickoff の SKILL.md

```
---
name: kickoff
description: >-
  Launch the work phase of the orchestration: ensure the requirements tab
  has its own Codex buddy pane, then either short-circuit and continue in
  the current tab (single-scope work) or generate the contract files, spawn
  one herdr work tab per scope (work-phase Claude + Codex buddy each), and
  hand off via a thin kickoff prompt (multi-scope work). Invoke explicitly
  by name once requirements are finalized (plan approved or scope agreed)
  and the session runs inside herdr (HERDR_ENV=1). This is the only
  deliberately-invoked skill of the baton plugin; codex-buddy and escalate
  fire autonomously afterwards.
---

# Kickoff

The single deliberate entry point of the orchestration. Everything downstream
(`codex-buddy`, `escalate`) fires autonomously — but only because this skill
embeds their names and fire conditions in the contract files. Never omit
them from the contracts.

baton is herdr-native and prescribes **contracts, not commands**: load the
herdr skill and drive the herdr CLI with your own judgment. This file states
what must be guaranteed; the herdr skill is the authority on how.

## Model defaults (configurable — edit here, nowhere else)

| Role | Default |
|------|---------|
| Main axis (requirements tab and work tabs) | Claude Fable, high reasoning |
| Buddy (all tabs) | Codex GPT-5.6, Sol high reasoning |

These are recommended defaults, not hardcoded requirements. Override only on
explicit user instruction. If the account rejects the pinned buddy model,
fall back to the buddy CLI's default resolution and note it — do not stop.

## Preconditions

1. **Requirements are finalized** — a plan file or design doc exists, or the
   scope is explicitly agreed in conversation. If not, stop and finish the
   requirements phase first.
2. **You are running inside herdr** — `HERDR_ENV` is set to `1`. If it is
   not, report that kickoff requires herdr and stop — do not improvise a
   fallback on any other multiplexer.
3. **Dependencies are present — check, don't assume.** Verify cheaply
   before spawning anything:
   - the `herdr` CLI responds (a pane list succeeds);
   - the **herdr skill** is available — baton defers all CLI mechanics to
     it, so a missing herdr skill is a hard stop (companion skills are
     installed separately per machine);
   - the buddy CLI (`codex`) is on PATH.
   If anything is missing, report exactly what is missing and how to
   install it, then stop.

## Flow

1. **Resolve the handoff artifacts and split into scopes**: the plan/design
   doc path and, when one exists, a session knowledge-base or notes folder.
   Split the plan into independent scopes (one scope ≈ one issue/branch).
   **If the split yields a single scope, do step 3 only and then jump to
   the Single-scope short-circuit below — do not spawn a work tab.** Two
   or more scopes proceed through steps 2-7 as the multi-scope path.
2. **Pick a slug and label the tabs** (multi-scope only). Choose a short
   kebab-case slug per scope. Label your own tab `req:<slug>` (pick the
   primary slug when there are several scopes; the exact label you choose
   is recorded verbatim in the common contract, step 4) and each work tab
   `work:<slug>`. Tab labels are the
   durable routing identity: herdr pane/tab **ids compact** (are renumbered)
   when panes or tabs close, so never hardcode a raw pane id in anything
   long-lived — every delivery re-resolves the current id from the label.
3. **Ensure your own buddy pane.** The requirements tab needs its Codex
   buddy too (`codex-buddy` applies to both tiers). If your tab has no
   buddy pane, split one and start the buddy model in it, pointed at a
   short parent-buddy brief you write first. The brief covers: the full
   **Buddy operating brief** from `codex-buddy` (peer stance, read-only,
   conclusion-only, paired-Claude scope), this buddy's specific context
   (requirements-side, plan/design doc path), and the promise that a
   `[req] consult:` question may arrive later. Do not skip pane
   creation — a kickoff that only equips the work tabs leaves the
   requirements side without its second opinion.
4. **Write the contract files** (multi-scope only; two layers, in a repo-local orch
   directory — somewhere every worker can read without extra permission
   grants; pointing workers at another session's scratchpad triggers
   avoidable prompts):
   - **Common contract** (one file, shared by all scopes):
     - Upward message format: `[<slug>] <type>: <one line>` where `<type>`
       is a small open vocabulary — at minimum `consult`, `progress`,
       `done`, `pr` (skills may add derivatives). There is deliberately no
       `blocked` type: a blocked *state* is herdr's status channel's job,
       and a block that needs a decision is a `consult`. The scope tag
       doubles as the sender signature. Routine reporting
       (`progress`/`done`/`pr`) is a duty, not an option: the parent
       supervises by these reports. One example per type:
       - `[auth-api] consult: need a decision on the session-store choice`
       - `[auth-api] progress: step 2/5 done, targeted tests green`
       - `[auth-api] done: all steps complete, full suite green`
       - `[auth-api] pr: #123 open, push was parent-approved`
     - Escalation: embed the `baton:escalate` and `baton:codex-buddy`
       skill names and their fire conditions, plus the parent tab label
       verbatim (the `req:` label from step 2). Escalation target = the
       Claude pane in that recorded tab. Workers must never construct the
       label from their own slug — with multiple scopes the parent label
       carries the primary slug, not theirs — and the pane id is
       re-resolved from the recorded label at every delivery.
     - Delegation rules: sub-agent mapping (explore/implement/reason/test),
       named spawns, stop-and-report on ambiguity. **Buddy scope: the
       work Claude consults only its own tab's sibling Codex pane;
       never talks to the parent buddy or to another work tab's
       buddy** (mirror of the buddy's paired-Claude rule from
       `codex-buddy`).
     - Guardrails for parallel scopes: hub files (barrel exports, route
       registration, shared config wiring) owned by the parent and
       off-limits to workers; per-worktree port allocation; never kill
       processes outside your own worktree; push and PR creation gated on
       parent instruction.
   - **Per-scope brief**: the scope's goal, its plan steps, its branch and
     worktree instruction, anything scope-specific.
5. **Spawn the work tabs** (multi-scope only) — per scope: a workspace/worktree on the scope's
   branch, a work-phase Claude pane, a sibling Codex buddy pane. The
   work-tab buddy is briefed with the same **Buddy operating brief**
   from `codex-buddy` as the parent buddy — same standing rules,
   including paired-Claude scope (its paired Claude is the work Claude
   in its tab, not the parent). Workers themselves may run in **auto
   mode**; grant what else they need via spawn-time flags (allowed
   tools, permission mode), not by writing settings files from the
   parent — a live run showed such writes get denied by the auto-mode
   permission classifier (the automatic gate that approves or denies a
   session's actions while it runs in auto mode). Remote-approving prompts pane-by-pane is the single
   largest friction; design most of it away at spawn time, and the
   user-consent gate (step 7) covers what remains. Wait until the
   Claude TUI is actually ready before sending anything.
6. **Send the thin kickoff** (multi-scope only; template below) and **verify it arrived**.
   Text pushed into a pane while its agent is mid-execution can be
   silently swallowed — after submitting, confirm the message shows as
   queued/accepted in that pane before trusting delivery; a content grep
   alone can false-negative once the message scrolls out of the viewport.
7. **Supervise event-driven, not by reading transcripts** (multi-scope only). herdr surfaces
   agent status natively (`idle`, `working`, `blocked`, `done`) and idle
   notifications arrive on their own; optionally keep a background
   agent-status watcher for the work panes. Steer on the workers' `[slug]`
   reports. If a work pane shows `blocked`/`done` with no report received,
   the worker may be unable to act (permission prompt, crash) — that is
   the one case where you read its pane and the escalation file
   (`/tmp/baton-escalation-work-<slug>.txt`) to recover.

   **User-consent gate.** When the recovery read shows the worker was
   denied by the auto-mode permission classifier, or is waiting on
   anything that needs the user's consent (a prompt auto mode would not
   grant, a trust dialog, an irreversible action), do not approve it
   yourself. Surface it to the user, obtain their consent, and only then resume the worker
   — by remote-approving or by sending corrected instructions. The
   parent's remote hands are for delivery and recovery, never for
   consenting on the user's behalf.

## Single-scope short-circuit

When step 1 yields a single scope, the second tier adds no parallelism —
handing off to a separate work tab only trades one seat's context for
two, plus a delivery contract to maintain between them. Stay in the
current tab and implement from here, keeping only what still earns its
place:

- **Kept**: step 3 (your Codex buddy pane) — `codex-buddy` remains the
  same second-opinion channel it always is. Implementation still
  delegates to sub-agents as usual.
- **Skipped**: steps 2, 4-7 — no `work:<slug>` label, no common
  contract, no per-scope brief, no spawn, no kickoff prompt, no
  cross-tab supervision.
- **Escalation**: `baton:escalate` does not apply — its Prereq (a
  common contract in scope) is deliberately not met, and there is no
  parent tab above this one anyway. The escalation target is the user
  in the same conversation; surface unrecoverable blockers to them
  directly.

If a single-scope run later grows a second scope (mid-flight scope
split), rerun kickoff from step 1 — do not retrofit a partial contract
onto the existing tab.

## Kickoff prompt template

Multi-scope only. Keep it thin — the contract lives in the files, not
the prompt:

```
You are the work-phase Claude for <scope> (tab work:<slug>; the
requirements tab is <parent tab label>). Read <common contract path> and
<per-scope brief path>, then start with <first step / phase 1>.
```

## Anti-patterns

- Invoking on casual phrasing — this skill activates by name or by an
  explicit "start the work tab" instruction only.
- A fat kickoff prompt that inlines the contract — the prompt is a pointer;
  duplicated contract text drifts.
- Hardcoding raw pane ids in prompts or contract files — ids compact;
  labels are the only durable identity.
- Skipping arrival verification after any cross-pane send.
- Equipping only the work tabs with buddies and leaving the requirements
  tab without one.
- Reading a work tab's transcript as routine supervision — status signals
  and `[slug]` reports are the channel; a full pane read is for
  blocked/done recovery only.
- Approving a classifier-denied or consent-class prompt on the user's
  behalf — the consent gate exists precisely there.
- Omitting the skill names and fire conditions from the common contract —
  without them, autonomous firing of codex-buddy/escalate degrades to
  chance.
- Spawning a work tab for a single-scope run without an explicit user
  request — the second tier only earns its keep when there is
  parallelism to gain; forcing it otherwise doubles the seats and adds
  a contract to maintain for no throughput.
```

baton:codex-buddy の SKILL.md

```
---
name: codex-buddy
description: >-
  Consult the Codex buddy running in a sibling pane of the current herdr tab.
  Use when a high-stakes decision needs an independent second opinion —
  architecture selection, security judgment, hard root-cause — or when a
  mechanical stuck-trigger fires (same failure twice, two consecutive
  re-delegations). Applies to both the requirements-phase Claude and the
  work-phase Claude. Do not use for routine questions a sub-agent or a quick
  search can answer.
---

# Codex Buddy

**Prereq**: `baton:kickoff` has run and placed a Codex buddy pane in
your tab (both tiers get one). If your tab has no buddy pane, split one
and start the buddy model in it before the first consultation — the
kickoff should have done this, so treat a missing pane as a recovery
step, not the norm.

A Codex agent (GPT-5.6, Sol high reasoning — configurable default, see
`kickoff`) runs in a sibling pane of your herdr tab as a
**peer engineer, not a reviewer**. It exists as insurance: going an entire
session without consulting it is a normal, acceptable outcome. Never consult
it out of formality.

Load the herdr skill for pane mechanics — this file states the consultation
contract, not which commands to type.

## Buddy operating brief

Every buddy is spawned with a short brief that fixes its stance and the
rules below. This is the canonical list; the kickoff Step 3 (parent
buddy) and Step 5 (work-tab buddy) instructions reference it, and any
future tier that adds a buddy uses the same set.

1. **Peer engineer, not a reviewer.** You are one independent sample of
   judgment for your paired Claude, not a gate on its output.
2. **Read-only.** No file edits, no file creation. If a question implies
   producing artifacts, describe them; do not write them.
3. **Conclusion-only reply.** A position plus a few reasoning bullets is
   the right shape. Long exploratory prose is your context to spend, not
   your paired Claude's context to read back.
4. **Talk only to your paired Claude.** Your paired Claude is the one
   Claude Code session in the same herdr tab as you — reachable as the
   sibling pane. Answer only questions from that Claude, and send
   replies only back to it. Do not initiate messages to any other pane
   (other tabs' Claudes, other tabs' buddies, worker sub-panes), and if
   a `[<slug>] ...` message from another tab lands in your pane, ignore
   it: the sender should be routing through its own paired Claude. This
   rule is what keeps the two-tier structure from degenerating into a
   mesh where every buddy talks to every other participant and the
   independent-sample property is lost.

## When to consult

Consult the buddy only when one of these fires:

- **High-stakes judgment**: architecture selection, security judgment, or a
  root-cause you cannot pin down.
- **Mechanical stuck-triggers**: the same failure occurred twice in a row, or
  you have re-delegated the same chunk twice without convergence.

If neither fires, do not consult. For blocking that no consultation can
resolve (missing permissions, contradictory requirements, scope changes), use
the `baton:escalate` skill instead — the buddy advises, it cannot unblock.

## How to consult

The consultation contract keeps your context lean and the answer sharp:

1. **Write the question to a file, not into the pane.** A short,
   self-contained brief in the scratchpad: the background (what is in
   flight, relevant PRs/paths), how to investigate (it can run git/gh and
   read files itself — point it at paths instead of pasting logs), and the
   numbered questions with the single constraint that matters. State two
   standing rules in the brief: **read-only — no file edits or creation**,
   and **conclusion-only reply** (a position plus a few reasoning bullets;
   long exploration is the buddy's context to spend, not yours to read
   back).
2. **Send the file path to the buddy pane and verify arrival.** Re-resolve
   the buddy's current pane id first (the Codex pane in your own tab — ids
   compact, locate it fresh). The delivery guarantees from the kickoff
   contract apply here too (queued/accepted verification, no
   fire-and-forget) — sends into a mid-execution pane get silently
   swallowed otherwise.
3. **Wait on agent status, then read the reply.** Wait for the buddy's
   pane to report done/idle rather than sleeping on a timer or grepping
   for UI chrome, then read the conclusion from the pane.
4. **Treat the reply as one independent sample.** You own the synthesis. On
   a blind-parallel first pass alongside any other reasoning agent, do not
   show the buddy another agent's answer; cross-examine in a second round
   only if the synthesis exposes a real tension, passing it the synthesized
   position and the counter-proposal.

## Stance by tab

- **Requirements tab**: the buddy backs your proposals with independent
  verification before they harden into a plan. Typical trigger is the user
  asking for a second opinion, or a high-stakes judgment surfacing during
  requirement shaping.
- **Work tab**: the buddy is a lifeline for judgment calls that block
  implementation. Consult before escalating to the parent tab; escalate
  anyway if the buddy's answer does not unblock you.

## Anti-patterns

- Consulting because a session has gone quiet without one — silence is
  fine, formality is not a trigger.
- Pasting logs, diffs, or files into the buddy pane — put paths in the
  brief and let it read them itself; your context is the scarce one.
- Sleeping on a timer or grepping for `Working`/`esc to interrupt` UI
  chrome to detect completion — wait on agent status, which is what
  herdr publishes for exactly this.
- Showing the buddy another agent's answer on the first pass — the
  value of the second opinion depends on independence; cross-examine
  only if the synthesis exposes a real tension.
```

baton:escalate の SKILL.md

```
---
name: escalate
description: >-
  Escalate an unrecoverable blocker from the work-phase Claude to the parent
  (requirements-phase) Claude in another herdr tab — the `consult` type of
  the upward channel defined in the kickoff contract. Use when blocking
  cannot be resolved by sub-agents or a codex-buddy consultation. Not for
  questions a buddy consultation could answer, and not for routine
  progress/done reports (those are a contract duty, not this skill).
---

# Escalate

**Prereq**: `baton:kickoff` has run, so the common contract exists and
records the parent tab label. If you cannot find that contract in your
scope, you are not in a baton orchestration and this skill does not apply.

Escalation is the `consult` type of the upward channel. Message format,
delivery guarantees (re-resolve the parent pane from the parent tab label
recorded in the contract — never construct it from your own slug — and
verify queued/accepted after sending), and the embedded skill names and
fire conditions already live in your kickoff contract; this skill adds
only what is specific to consulting:
**when to fire, the durable-record contract that survives your own
incapacity, and bump semantics**.

Why a message at all, when the parent already watches agent status?
Because status carries no content — acting on it alone would force the
parent to read your transcript, which the contract forbids — and because
a worker that parks the blocked step and continues independent work (the
expected shape, see the return path below) still reports `working`. In
that case this message is the only signal the parent gets.

## When to escalate

- A `codex-buddy` consultation (or two) did not unblock you.
- The blocker is outside your authority: missing permissions/credentials,
  contradictory or incomplete requirements, a scope change, or a decision
  that belongs to the requirements context.
- A mechanical trigger fired with no path forward: the same failure twice,
  or two consecutive corrected re-delegations of the same chunk both
  diverged.

Do not escalate what a targeted sub-agent, a search, or a buddy
consultation can resolve — escalation interrupts the requirements
conversation.

The consult body — beyond the `[<slug>] consult: <one line>` header the
kickoff contract specifies — needs enough for the parent to answer
without re-investigation. Keep the whole message under ~15 lines,
referencing paths rather than pasting content:

- **Context**: plan/design doc path and step.
- **Tried**: what you attempted (name the buddy result if any).
- **Options**: 2-3 you see, with your recommendation.
- **Need**: the specific decision or resource you need back.

A filled example:

```
[auth-api] consult: session-store choice blocks step 3
Context: plans/auth-api.md step 3 (session persistence).
Tried: buddy consultation — recommends Redis; the plan assumes
DynamoDB. A sub-agent spike confirmed both work against our API.
Options: (1) Redis — matches infra the team already runs
(recommended); (2) DynamoDB — matches the plan, adds a new dependency.
Need: a decision between (1) and (2).
```

## Durable record — the half that survives your incapacity

**Every escalation is written to `/tmp/baton-escalation-work-<slug>.txt`
(keyed by your tab label, overwritten each time) in addition to being
delivered.** This is not a fallback — write it even when delivery
succeeds. It lives in `/tmp`, not the repo-local orch directory, so it
survives worktree teardown and never lands in a commit.

The reason: the delivery path only works while you can still act.
Permission prompts, crashes, exhausted context, or the parent tab
disappearing all take out the active channel. The file survives all of
them. It is what the parent reads on the recovery path when herdr
reports your pane `blocked` with no message received, and what a bump
(below) or a later reader can rely on.

If delivery is skipped or fails outright (parent tab gone, `HERDR_ENV`
missing, verification failed twice), the file is still written and you
surface the escalation in your own pane's output — the user watches both
tabs and herdr marks your pane in the sidebar. A visible, well-formed
escalation that waits is a success, not a failure.

## Return path and bump

After delivering, park the blocked step and continue any independent
work; if nothing is independent, stop and wait. The parent's answer
arrives as a message in your own pane. Resume when it arrives, and
record any plan change before continuing.

If a reply does not arrive within a reasonable window (roughly ten
minutes, or after your independent work runs out — whichever comes
first), re-deliver once with `[<slug>] consult-bump:` in place of
`consult:` (a `consult` derivative — the contract's type vocabulary is
open, and this skill extends it for the recovery path) and note the bump
in your progress log. The bump follows the
same delivery + file rules. The parent may be paused, off the
requirements tab, or waiting on the user; the bump is a signal, not a
retry — do not spam. If a second bump goes unanswered, stop and surface
the whole situation in your own output for the user to arbitrate
directly.

## Anti-patterns

- Skipping the file write because delivery succeeded — the file is
  what survives your incapacity, so it is not a fallback.
- Stopping all work after delivering — park the blocked step, but keep
  independent work moving; a parked worker is not a stopped one.
- Bumping the moment a reply feels late — the bump is a signal to a
  possibly-diverted parent, not a retry. One bump, then wait; two
  bumps and stop.
- Escalating something a `codex-buddy` consultation or a sub-agent
  could have answered — escalation interrupts the requirements
  conversation, so the bar is real.
```

## 検証方法

作った plugin が意図通り動くかは、2 段階で確認しました。

### /skill-creator を活用したレビューと動作検証

[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) は Anthropic が公開している skill 集の 1 つで、自作 skill の設計や記述レビューに加えて、実際に並列セッションを走らせて意図通りにトリガー・出力するかまで検証してくれるメタ的な skill です。  
本記事では次の 2 通りの使い方で活用しました。

* **記述品質レビュー**: 各 SKILL.md を skill-creator のガイドライン (構造・命令形・why 説明・例示・行数) に照らして評価。合格判定を受けつつ、細かい修正指摘を反映
* **plugin ロード有無の比較**: 同じタスクを 2 通り (plugin をロードしたセッション / ロードなしのセッション) で並列実行し、結果を採点。**plugin ロードあり 24/24、なし 12/24 前後**という差が計測できた

### E2E テスト

herdr の実セッションで一度動かしました。  
`baton:kickoff` で work tab を作り、初期 prompt を送り、作業 Claude Code が step 1 を happy path で完走し、step 2 で意図的にエスカレーション条件を仕込んだところ、`baton:escalate` が発火して要件タブにエスカレーションメッセージが届く、という一連の流れを確認しています。  
LLM に multiplexer 操作を任せる部分が動くのかは正直やってみるまで自信がなかったのですが、想定通り機能しました。

## 実運用した結果

kickoff として5,6個の Issue を渡してみたところ、Issue 毎に Claude Code + Codex のグループを作成して作業を進めることができていました。  
必要に応じて buddy 役の Codex に確認やレビュー依頼をしていたりユーザーへのエスカレーションも適宜行われていたので、オーケストレーションの構築はひとまず成功に終えられたと思います。  
もちろん実装内容の品質についても十分 Approve できるものになっていました。

## 今後の課題

### Codex に実装役を担わせる流れの設計

現状は Claude Code が主体で Codex は相談・レビュー担保役ですが、GPT 5.6 の性能を存分に引き出せている構成とは言えません。  
Codex を実装役に据えるパターンや、Claude Code との立ち位置の入れ替え・分業パターンを見直したいと考えています。

### plugin に設定機能を持たせる

メイン軸のモデル・buddy のモデルなど、コーディングエージェントのモデル選定はこの仕組みの性能に大きく響きます。  
plugin 側の設定として切り替えられるようにしたいと考えています。

## おわりに

Claude Code と Codex を multiplexer 上で並走させるという構成は、実装を進めるほど「輸送は環境に任せて、契約だけ書く」という形に寄っていきました。  
オーケストレーションの自作が今後の開発モチベーションに繋がったので、引き続きコーディングエージェントの情報を追って快適に開発できる環境整備に努め用と思います。
