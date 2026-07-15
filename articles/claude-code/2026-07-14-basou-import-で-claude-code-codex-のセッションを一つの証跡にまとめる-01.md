---
id: "2026-07-14-basou-import-で-claude-code-codex-のセッションを一つの証跡にまとめる-01"
title: "basou import で Claude Code / Codex のセッションを一つの証跡にまとめる"
url: "https://zenn.dev/takashi_m_jp/articles/65710c150ce47a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "zenn"]
date_published: "2026-07-14"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

> 🔗 この記事は <https://blog.tak3.jp/ja/blog/basou-agent-session-trail/> からの転載です（一次情報源）。

Claude Code は、あなたのリポジトリで既に日記をつけている。Codex も同じだ。ただしそれは、読み返されることのないベンダーログの山としてだ — 別々の形式で、別々の場所に、読めず、検証できない形で。

5分後、それが変わる。両方のセッションが、コードの隣の**一つの証跡**に、同じ形式で並ぶ。ワークフローは何も変えない。過去のセッションも、遡って対象になる。

## 5分後に手に入るもの

対象リポジトリの隣に `.basou/` ができて、中にこれらが入る:

* 人間が読む `handoff.md` — どこまで進み、何が起き、どこから再開するか
* 正本の `events.jsonl`（セッションごとに `.basou/sessions/` 配下）— 追記専用・hash chain で連結されたイベントログ。**Claude Code のセッションも Codex のセッションも、ここでは同じ形になる**
* `basou verify` が「この記録は改竄されていないか」に機械的に答えられる状態

basou 自体の全体像は[紹介記事](https://blog.tak3.jp/ja/blog/introducing-basou/)に書いた。一言でいえば AI コーディングエージェントのためのローカルファーストな馬装（ハーネス）— 鞍（宣言的ワークスペース）と手綱（意図を運ぶオリエンテーション）、そしてその足元に置かれた再生可能な記録からなる。今日はその足元、セッションの**証跡**だけを、手を動かして試す。

## 前提と Step 1: インストールと init（30秒）

前提は3つ。Node.js 20.10.0 以上、Claude Code か Codex（どちらか一方でいい。両方ならこの記事の全部が試せる）、そしてそれらを使ってきた実リポジトリがあること。

```
npm install -g @basou/cli
cd path/to/your-repo
basou init
```

本記事は basou **v0.34.0**（2026-07-14 時点）を基準にしている。

git に何が入るかを先に言っておく。既定では、basou はノイズの多い側を git の外に置く — 生イベントログ、内部ログ、揮発的な orientation ビュー。追跡対象として残るのは永続的な要約だ: manifest、`handoff.md`、`decisions.md`、それに各セッションの `session.yaml`。つまり PR の diff でレビューできる。ただしこれらの要約には実作業の中身 — セッションのラベル、決定のタイトル、handoff の本文そのもの — が含まれるので、公開リポジトリなどで何ひとつ commit したくなければ `basou init --local-only` — `.basou/` 全体を gitignore する側に倒せる。

## Step 2: Claude Code の過去分を取り込む — `basou import`

ここが今日の山場だ。

```
basou import claude-code --all
```

```
Imported sessions: 20 path(s) sanitized
Imported 4 session(s) (101 events)
```

1コマンドで、このリポジトリで過去に走らせた Claude Code のセッション4つが、101 イベントの証跡として遡って取り込まれた。`--all` は「見つかった過去分を全部」の明示で、パス指定も設定ファイルも要らない — basou が各ツール固有のログをディスク上から自動検出する。慎重に行きたければ先に `--dry-run` を付ける — 何も書かずに `Dry run: would import …` とプレビューだけが返る。

取り込みの細部やつまずきどころは [quickstart](https://basou.dev/ja/quickstart/) に譲る。ここで押さえてほしいのは1点だけ — **ワークフローを何も変えていない**のに、過去分が証跡になった、ということだ。

## Step 3: Codex も、同じ証跡へ

タイトルの「一つの証跡にまとめる」はここからだ。同じリポジトリで Codex も使っていたなら、コマンドはこう変わるだけ:

```
Imported sessions: 1 path(s) sanitized
Imported 1 session(s) (01KXFP) (15 events)
```

これで証跡は 5 セッション・116 イベントになった。取り込まれたものは、次の Step で `handoff.md` を生成すると、その末尾のセッション一覧でこう見える:

```
| short_id | status | started_at | label |
|---|---|---|---|
| 01KXFPWTJG | imported | 2026-05-14T23:56:54.061Z | codex 2026-05-14: 13 commands |
| 01KXFPWT97 | imported | 2026-07-06T03:42:36.504Z | claude-code 2026-07-06: 1 command, 0 files |
| 01KXFPWT95 | imported | 2026-05-25T04:19:07.538Z | claude-code 2026-05-25..2026-05-27: 24 commands, 9 files |
| 01KXFPWT8Y | imported | 2026-05-27T13:53:53.125Z | claude-code 2026-05-27..2026-06-10: 12 commands, 4 files |
| 01KXFPWT8S | imported | 2026-06-14T06:10:20.317Z | claude-code 2026-06-14: 23 commands, 3 files |

Sessions: 5 (imported 5). Tasks: 0.
```

`codex` と `claude-code` が同じ表に並んでいる。別々のツールの、別々の時期のセッションが、一つのワークスペースの一つの時系列に入った。ツールごとにログの置き場所と形式を思い出す必要は、もう無い。

## Step 4: handoff を生成して読む — そして "replayable" の意味

import が書いたのは**記録**だ。`.basou/sessions/` の下にある、追記専用で hash chain された JSONL。人間が読むビューは、こう頼んで作る:

```
# Handoff

> Generated at 2026-07-14T07:02:06.205Z from ses_01KXFPWT8S..ses_01KXFPWTJG

## 現在の状態

- 最終 session: claude-code 2026-06-14: 23 commands, 3 files (imported) [ses_01KXFPWT8S]

## 直近の判断

- ████████ の AGENTS.md 文書そのもの（散文本文）の言語をどう改定しますか？ … -> 本文は日本語のまま維持 [decision_01KXFPWT8P]

(3 decisions total — see decisions.md)
```

これが `.basou/handoff.md` の抜粋 — どこまで進み、直近で何が起き、どこから再開するか。チームメイトに渡せる。明日の自分に渡せる。次のエージェントセッションに渡せる。

（見出しが日本語なのは、workspace の manifest でこのリポジトリに `language: ja` を宣言してあるからだ。生成ビューの見出しなどの定型文は既定では英語。宣言が変えるのはその定型文だけで、ユーザーデータには触れない — あなたが書いたもの・エージェントがやったことは verbatim のまま。）

さて、この節の見出しにある *replayable*（再生可能）がここで意味を持つ。いま読んだ Markdown は記録ではない — 記録から導出された**ビュー**だ。つまり、使い捨てられる。証明しよう。`rm` してもいいのだが、あとで diff を取るために脇へ移す:

```
mv .basou/handoff.md /tmp/before.md
basou handoff generate
diff /tmp/before.md .basou/handoff.md
```

```
4c4
< > Generated at 2026-07-14T07:02:06.205Z from ses_01KXFPWT8S..ses_01KXFPWTJG
---
> > Generated at 2026-07-14T07:03:24.276Z from ses_01KXFPWT8S..ses_01KXFPWTJG
```

動いたのは1行 — 生成タイムスタンプだけ。**残りは byte 単位で同一のまま戻ってきた**。`events.jsonl` から、決定論的に、オフラインで、LLM なしで再導出された。同じコマンドが、同じビューを、正本から蘇らせる。

ここでいう replayable はそういう意味だ。ステップ実行のプレイヤーがあるわけではない — **いつでも再消費できる正本ログ**があり、人間可読のビューはすべてそこから再構築できる、ということ。handoff も、decision log も、orientation も、どれも1つの検証可能なログの安価な投影にすぎない。ビューは手で編集して構わない。正本側の版が欲しくなったら、再生成すればいい。

## Step 5: 検証する — "verifiable" の意味

セッションの `events.jsonl` を覗くと、各イベントが直前のイベントのハッシュを握っているのが見える:

```
{"schema_version":"0.1.0","id":"evt_01KXFPWT8S…","session_id":"ses_01KXFPWT8S…","occurred_at":"2026-06-14T06:10:20.317Z","source":"claude-code-import","type":"session_started","prev_hash":"cc5b28d0…7118a77"}
{"schema_version":"0.1.0","id":"evt_01KXFPWT8S…","session_id":"ses_01KXFPWT8S…","occurred_at":"2026-06-14T06:10:25.021Z","source":"claude-code-import","type":"command_executed","command":"bash", … ,"prev_hash":"309256a7…148fa84"}
```

だからこの問いに、機械が答えられる — 「この記録は、書かれたあとに改竄されていないか」。

```
ses_01KXFPWT8S…  verified (34 events)
ses_01KXFPWT8Y…  verified (19 events)
ses_01KXFPWT95…  verified (45 events)
ses_01KXFPWT97…  verified (3 events)
ses_01KXFPWTJG…  verified (15 events)
Sessions: 5 total — 5 verified, 0 unchained, 0 empty, 0 incomplete, 0 in_progress, 0 tampered
```

Codex のセッション（検証行の最後・15 events）も、Claude Code の4つと同じ鎖の検証を、同じコマンドで通っている。見たいのは、集計行の末尾が `0 tampered` で終わる形だ。もし1件でも改竄があれば該当セッションが `TAMPERED (...)` になり、exit code が 1 になる — つまりスクリプトにも組める。ちなみにこの鎖は、import が書き込んだ瞬間から既に繋がっている。あとから祝福する工程は無い。

## 「一つの証跡」を支える設計 — adapter とベンダー中立な証跡フォーマット

Step 3 で起きたことを、少しだけ設計側から見ておく。ツールが増えても証跡が一つでいられるのは、役割が2層に分かれているからだ。

**adapter は、ベンダー固有ログの reader だ。** Claude Code のトランスクリプトと Codex のセッションログは、形式も置き場所もまったく違う。その差異を知っているのは各 adapter だけで、仕事は「読んで、共通の形に写す」ことに尽きる。

**証跡フォーマットは、中立で統一されている。** adapter を通過した先は、どのツール由来でも同じ共通スキーマの `events.jsonl` に落ちる — 同じフィールド、同じ hash chain。さっきの Step 5 のイベント行と見比べてほしい。Codex 由来のイベントはこうなっている:

```
{"schema_version":"0.1.0","id":"evt_01KXFPWTJG…","session_id":"ses_01KXFPWTJG…","occurred_at":"2026-05-14T23:56:54.061Z","source":"codex-import","type":"session_started","prev_hash":"3906bbc4…2d59cb1"}
```

フィールドの形は Claude Code 由来のものと同一で、由来（provenance）は `source` フィールドがデータ自身として名乗る — この行では `codex-import`。各セッションの `session.yaml` には `source.external_id` としてベンダー側のセッション id も残るので、元ログへ遡ることもできる。

この分離が効いてくるのは下流だ。`handoff` も `verify` もさっきの `diff` も、ソースが何だったかを知らないまま、一つの形式だけを相手に動いている。だからツールを足しても、検証や再生の仕組みは1系統のまま増えない。

## これからのセッション

ここまでは過去分の話。これからの分は、もっと簡単だ。

朝いちは `basou orient` — 「どこまでやったっけ」に記録が答える。日々の取り込みとビュー更新は `basou refresh` の一発 — Claude Code も Codex も、実装済みの adapter をまとめて処理する（ソースログが無いツールは skip される）。設計判断が下りたら `basou decision capture`、離席前に `basou note "次はここから"`。セッションを最初からライブで記録したければ、`basou run claude-code` でプロセスごと包む手もある。

## これは何では「ない」か

ダッシュボード SaaS ではない。何もマシンの外に出ない。実行時に LLM を呼ばない。証跡はすべて `.basou/` の中に閉じ、やめたくなればそのディレクトリを消すだけでいい。ローカルで眺めたければ `basou view`（127.0.0.1 のみに束縛）もあるが、それも任意。

## 結び

5分の内訳はこうだった — install と `init`、`import` を2回（Claude Code と Codex）、`handoff generate`、`verify`。これで2つのツールのセッションがコードの隣の一つの証跡に並び、ビューは消しても正本から戻り、改竄されれば機械が気づく。

続きは [quickstart](https://basou.dev/ja/quickstart/) と CLI リファレンスに。0.x で引っかかったら [issue](https://github.com/basou-dev/basou) をどうぞ — 歓迎する。
