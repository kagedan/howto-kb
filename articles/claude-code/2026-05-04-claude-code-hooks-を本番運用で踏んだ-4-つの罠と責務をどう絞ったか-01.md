---
id: "2026-05-04-claude-code-hooks-を本番運用で踏んだ-4-つの罠と責務をどう絞ったか-01"
title: "Claude Code Hooks を本番運用で踏んだ 4 つの罠と、責務をどう絞ったか"
url: "https://zenn.dev/zoetaka38/articles/d78cc822e4bde2"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

前回(zenn-012)で Skill とコマンドの分業を書いたあと、@kawai\_design さんとのやり取りで「優先順は CLAUDE.md → Skill → MCP → GitHub → Hooks」という話を貰った。並びとしてはほぼ同意で、自分の運用も大体この順に効きを足していった結果になっている。ただ Hooks だけは触り始めてから 「効きすぎる側」 の罠を結構踏んだので、そこを切り出して書いておきたい。

Hooks は Claude Code の中で唯一、「Claude の判断を待たずに必ず走る」 レイヤだ。CLAUDE.md は方針、Skill は手順、Hooks は強制 ── という構造になっていて、deterministic に挿し込めるという点では preset workflow と並ぶ。preset が「この workflow に乗せたタスクには必ず適用される」のに対し、Hooks は 「Claude Code セッションそのものに張り付く」 ので、誰がどう起動したセッションでも問答無用で発火する。

その「問答無用で発火する」のが諸刃で、止めたい時に止められなかったり、副作用を撒いてしまったりする。Codens では各サービス(red / blue / green / purple / yellow / auth / template) の `.claude/` 配下にそれぞれ hooks 設定があり、もう半年ほど運用してきた。そこで踏んだ罠を 4 つに絞って書く。

## まずは Hooks が効く場面

罠の話の前に、Hooks がちゃんと効く場面から。Codens で実際に動いている設定はこういう形になっている。

```
// red-codens/.claude/settings.json 抜粋
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": ".claude/scripts/security-check.sh" }]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": ".claude/scripts/protect-files.sh" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": ".claude/scripts/auto-format.sh" }]
      }
    ]
  }
}
```

`PreToolUse` で危険コマンド・保護ファイルを弾き、`PostToolUse` で書いたコードを自動 format する。この 2 つは Hooks で書く価値がはっきりある。

`security-check.sh` の実体はこんな感じ。

```
# red-codens/.claude/scripts/security-check.sh 抜粋
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

DANGEROUS_PATTERNS=(
  "rm -rf /"
  "git push.*--force"
  "terraform destroy"
  "mkfs"
  "dd if="
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$CMD" | grep -qE "$pattern"; then
    echo '{"status": "blocked", "reason": "危険なコマンドが検出されました: '"$pattern"'"}'
    exit 2
  fi
done
```

これは典型的な PreToolUse の使い方で、 「Claude の判断に委ねたくない」 安全網だ。`terraform destroy` を Claude にうっかり呼ばれた時、CLAUDE.md に「呼ぶな」と書いておくだけでは保証として弱い。Hook は exit 2 で問答無用で止まる。CLAUDE.md → Skill → MCP のラインでは決定論にできない部分を、最後にここで塞ぐ。

`protect-files.sh` も同じ思想で、`.env` 系や本番 tfvars, ロックファイルへの書き込みを止める。

```
# red-codens/.claude/scripts/protect-files.sh 抜粋
PROTECTED_PATTERNS=(
  "\.env$"
  "credentials\.json$"
  "\.pem$"
  "infrastructure/terraform/environments/prod/.*\.tfvars$"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qE "$pattern"; then
    echo '{"status": "blocked", "reason": "保護されたファイルです: '"$FILE_PATH"'"}'
    exit 2
  fi
done
```

本番環境の `.tfvars` を Claude が試しに開いて編集しようとした時に、ここで止まる。Skill で「気をつけて」と書くより圧倒的に効く。

## ハマり 1: Hook の終了コードが workflow を支配する

Hooks の最大の強みは「exit 2 で Claude のターン自体を中断できる」こと。だが、これは同時に最大の罠でもある。 **Hook の exit code が、その上で走っている agent workflow 全体を支配してしまう。**

具体的には、PreToolUse hook が non-zero を返すと Claude は当該ツール呼び出しを中断し、エラーメッセージを受け取る。そこから「では別の方法を試します」と続けてくれる時もあれば、ターン自体を打ち切ってしまう時もある。前者ならいいのだが、後者の挙動になった場合、agent が **「半分やって戻る」** 状態になる。実装は途中、テストも書きかけ、commit もしていない、という中途半端な完了。

これを Codens で最初にやらかしたのは `protect-files.sh` の matcher を雑に書いた時で、「Edit / Write の対象が `.env` を含むパス」を全部弾いていた。すると `tests/test_env_loader.py` のような `env` を文字列として含むファイルすら止まってしまい、Claude が「テスト書こうとした → 弾かれた → 別の名前にしようとした → max\_turns 切れ」 で何も commit せず終わるケースが出た。CLAUDE.md にも `verify_commands` にも「テストを必ず書け」と書いてあるが、書こうとして塞がれている時の救済はない。

教訓として、Hook 内では fail-soft / fail-loud を意図的に切り分けるようにした。具体的には:

* **本当に止めたい(セキュリティ系) → exit 2 + 明確な reason**
* **観測だけしたい(ログ取り、format) → 必ず exit 0、stderr にメッセージ**

Codens の `auto-format.sh` は後者の代表で、format に失敗しても絶対に exit 0 で抜ける。

```
# red-codens/.claude/scripts/auto-format.sh 抜粋
if [[ "$FILE_PATH" == *.py ]]; then
  cd "$PROJECT_ROOT/backend" 2>/dev/null || exit 0

  if command -v black &> /dev/null; then
    black --quiet "$FILE_PATH" 2>/dev/null || true
  fi

  if command -v ruff &> /dev/null; then
    ruff check --fix --quiet "$FILE_PATH" 2>/dev/null || true
  fi
fi

exit 0
```

`|| true` を黒で塗りたくっているのと、最後の `exit 0` は意図的。format hook が失敗したぐらいで Claude のターンを止められたら、agent の進捗が format ツールの体調に支配される。observation 系の Hook はとにかく ターンを止めない という規律が要る。

逆に `security-check.sh` 側は exit 2 で確信を持って止める。「terraform destroy をかけられて困るのは Hook が止めなかった時」 なので、ここで agent が困惑して 1 ターン無駄にするのは安いコスト。

## ハマり 2: Hook 内の副作用が retry に乗らない

これは preset workflow と組み合わせた時に痛い。Codens の workflow runner は失敗時に `fix_verify` を回したり、ステップ単位でリトライしたりするのだが、 **Hook で発生した副作用は、リトライ前提で設計された workflow の外側で起きる。**

最初に踏んだのは「PostToolUse hook 内で git commit を打っていた時期」だ。idea としては、Edit/Write の直後に「ここまで Claude が書いた変更」を WIP commit しておけば、後で巻き戻せて便利、という発想。実装も短く済むし、最初の数日はうまく動いた。

問題は Claude のリトライと組み合わさった時に出た。`fix_verify` が落ちて develop ステップを再実行 → Claude が同じファイルを書き直す → PostToolUse が発火 → また WIP commit、という動きを 3 周ぐらいすると、git log が WIP まみれになる。本来の commit message が WIP の山に埋もれて、後で `git log --oneline` で何が起きたか追えない。

別系統で踏んだのは PostToolUse hook 内で外部 API を叩いていた時。「Edit するたびに Slack に notify」という設定を入れていたら、Claude のリトライで Slack rate limit に当たった。Slack は秒間メッセージ数の上限が地味に厳しく、agent が 30 ターン回ると 30 通飛ぶ。これは下流で「リトライ可能」 と思っているけれど、実際には Hook 側で副作用がもう外に出てしまっているので巻き戻せない。

教訓: **Hook の責務は「観測」と「拒否」だけにする**。副作用は workflow 側に置く。Codens でも今は WIP commit は workflow runner 側のステップ(`develop` ステップが終わるごとに 1 回 commit するロジック)に移してあって、Hook は format と log と block しかやっていない。`auto-format.sh` は git に触らないし、`security-check.sh` は exit code と reason を返すだけで何も書き込まない。`log-test-execution.sh` も append-only のローカルログだけ。

```
# blue-codens/.claude/scripts/log-test-execution.sh 抜粋
if [[ "$TOOL_INPUT" == *"pytest"* ]] || \
   [[ "$TOOL_INPUT" == *"npm test"* ]] || \
   [[ "$TOOL_INPUT" == *"playwright"* ]]; then

    LOG_FILE="$LOG_DIR/test-execution.log"
    {
        echo "Timestamp: $TIMESTAMP"
        echo "Command: $TOOL_INPUT"
        # 出力が長い場合は最後の50行のみ
        if [[ ${#TOOL_OUTPUT} -gt 2000 ]]; then
            echo "$TOOL_OUTPUT" | tail -50
        else
            echo "$TOOL_OUTPUT"
        fi
    } >> "$LOG_FILE"
fi

echo '{"continue": true}'
```

これも append-only のテキストログだけ。`continue: true` を必ず返して、絶対にターンを止めない。Hook が外部 state(git, Slack, DB, S3) を触らないように律儀に守ると、リトライとの噛み合わせ事故は激減した。

## ハマり 3: Hook の登録が局所的すぎて分散する

Codens は monorepo 構成ではなく、サービスごとに別リポジトリで運用している(red-codens, blue-codens, green-codens, purple-codens, yellow-codens, auth-codens, codens-template)。同じ思想の Hook を全部に配るのだが、これを愚直にやると **同じ目的の Hook が 6 ヶ所に複製される**。

実際 `find ./codens-main -path '*/.claude/scripts/*'` を打つと、こうなる。

```
./auth-codens/.claude/scripts/security-check.sh
./auth-codens/.claude/scripts/protect-files.sh
./auth-codens/.claude/scripts/auto-format.sh
./purple-codens/.claude/scripts/security-check.sh
./purple-codens/.claude/scripts/protect-files.sh
./purple-codens/.claude/scripts/auto-format.sh
./codens-template/.claude/scripts/security-check.sh
./codens-template/.claude/scripts/protect-files.sh
./codens-template/.claude/scripts/auto-format.sh
./red-codens/.claude/scripts/security-check.sh
./red-codens/.claude/scripts/protect-files.sh
./red-codens/.claude/scripts/auto-format.sh
./green-codens/.claude/scripts/security-check.sh
./green-codens/.claude/scripts/protect-files.sh
./green-codens/.claude/scripts/auto-format.sh
./yellow-codens/.claude/scripts/security-check.sh
./yellow-codens/.claude/scripts/protect-files.sh
./yellow-codens/.claude/scripts/auto-format.sh
```

`security-check.sh` の `DANGEROUS_PATTERNS` に `terraform destroy` を足したい時に、これを 6 回手動で更新する事態になる。当然どこかで漏れる。yellow-codens だけ古い版が残っていて、yellow に対するセッションだけ destroy が通る、ということが起きうる。

Codens では `codens-template` をテンプレートリポジトリとして真ん中に置いて、ここから他に複製する設計にしているのだが、テンプレートを更新したからといって既存リポジトリには波及しない。これは monorepo 化していない以上、構造的に避けられない。

緩和策として今やっているのは:

1. **`.claude/scripts/` 配下を「テンプレートからの逸脱はゼロにする」 ルールにして、各サービス固有のロジックは hook 内に書かない。** 例えば「red-codens 固有の本番チェック」を `security-check.sh` に追加するのは禁止で、本当に red-codens 固有の保護が要るなら別の `.sh` を新設する。共通ロジックの hook が 6 ヶ所で diff るのが一番厄介。
2. **PR で `.claude/scripts/` に対する変更があったら、横展開チェックリストを description に貼らせる。** 「この変更は他の 5 リポジトリにも入れた」を確認する human gate を残す。これは未だに完全には自動化できていない。
3. **テンプレートリポジトリの `track-claude-md.sh` のような追跡スクリプトを使って、各リポジトリの Hook の最終更新日を可視化する。** Codens の各サービスには `track-claude-md.sh` が入っていて、CLAUDE.md だけでなく `.claude/scripts/` の最終更新も追えるようにしてある。

```
# red-codens/.claude/scripts/track-claude-md.sh 抜粋
case "$action" in
  log)
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$LOG_FILE"
    ;;
  show)
    if [ -f "$LOG_FILE" ]; then
      tail -20 "$LOG_FILE"
    fi
    ;;
  diff)
    git -C "$PROJECT_ROOT" diff -- "**/CLAUDE.md" "CLAUDE.md"
    ;;
esac
```

これを `.claude/scripts/` にも適用して、 「いつ最後に security-check.sh を触ったか」 を各リポジトリで追えるようにしている。完全な解ではないが、 「6 リポジトリで Hook がいつのまにか乖離していた」 事故の発見が早くなった。

monorepo に切り替えれば一発で解決するのは分かっているが、それぞれのサービスのデプロイサイクルや AWS アカウントを分けている関係で、現状はリポジトリも分けたままにしている。Hook の同期コストは monorepo / multi-repo の選択を迫る隠れたコストとして、最初に思っていたより重い。

## ハマり 4: Hook が Skill / verify\_commands と相互作用する

これは前回(zenn-012)の記事の続きとして書きたい部分。Skill / Hook / verify\_commands は全部 「Claude の出力を検証する」 という似た目的を持っているので、責務が被ると順序の事故が起きる。

具体例: ある日、Skill 側で「変更したファイルを読み返して構文をチェックする」 自前の verify Skill を書いていた時のこと。Skill が `Read` ツールを呼んで対象ファイルを読みに行く。ところが PostToolUse の `auto-format.sh` Hook が **その直前の Edit のタイミングですでに発火していて、ファイルを書き換えている**。Skill が読んだのは「自分が編集した版」 ではなく「format 後の版」だった。空白とか import 順は変わるだけなので大事には至らないが、Skill の言う「ここはこう書き換えた」 と実ファイルの内容が微妙にずれて、後段の commit message と diff が一致しなくなる。

逆方向の事故もあった。`verify_commands` 側で `ruff check src` を回すと、ローカルではすでに `auto-format.sh` が import を sort してくれているので通る。一方、CI 側では Hook は走らないので、人間が Hook 抜きで書いた PR がローカル green / CI red になる。 「Hook で format に頼った状態」 が、verify と CI の前提条件のずれを生む。

教訓は単純で、 **3 つの責務を干渉しないように分ける**:

* **Hook = 観測 / 拒否 のみ**(format は Hook ではなく `pre-commit` か CI に寄せる方向で再検討中)
* **Skill = 文脈判断 / 自然言語サマリ**(Claude の判断に委ねていい部分)
* **verify\_commands = 必ず通す出口**(exit code が真実、Hook と独立に走る)

`auto-format.sh` をどこに置くかは未だに揺れている。Hook に置くと「Claude が書いた直後に format される」ので人間目線の commit が綺麗になる反面、Skill との順序事故が起きる。`pre-commit` に置けば順序事故はなくなるが、Hook がやっていた「Claude が PostToolUse で見るファイル」 が format 前のままになる(これは多分問題ない、後段が CI で同じことをやるので)。 `verify_commands` の中に `ruff check --fix` を入れるのは、verify が「観測」 と 「修正」 を兼ねてしまって責務が膨らむので嫌だ。

今のところ Codens の各サービスでは Hook に置いたままで、 「format 結果に Skill が依存しないように Skill 側を書く」 というワークアラウンドで済ませている。Skill 内で空白や import 順を気にしない、 必要なら Skill 内で `Read` を再実行する、といった作法を Skill の説明文に書いてある。設計としては綺麗ではない。

## 補足: SessionStart で CLAUDE.md を再注入する hook

罠の本筋ではないが、もう一つだけ書いておきたい設計判断系の Hook がある。`SessionStart` hook は `compact` や `resume` のタイミングで発火する仕組みで、Codens では「`/compact` 後に CLAUDE.md を再注入する」のに使っている。

```
"SessionStart": [
  {
    "matcher": "compact",
    "hooks": [
      { "type": "command", "command": ".claude/hooks/reload-claude-md.sh", "timeout": 10000 }
    ]
  }
]
```

`reload-claude-md.sh` はルートとサブプロジェクトの `CLAUDE.md` を全部 cat して `additionalContext` として返すだけのスクリプトで、`/compact` 後に方針が落ちる事故の対策になっている。これは観測系ではなく **コンテキスト注入系** で、罠というよりはトレードオフの話。注入すると context window を最初から食うので、purple-codens では `assemble_context` でタスク種別ごとに必要な CLAUDE.md セクションだけ assemble する設計を別途持っている。runtime workflow 側は `assemble_context` で絞り、対面 dev-loop 側は SessionStart hook で全注入、と層で分けている。Hook の効きすぎが裏目に出る、という意味では本記事の問題意識と地続き。

## まとめ

Hooks は CLAUDE.md → Skill → MCP → GitHub のラインで詰めきれない 「決定論」 を最後に塞ぐレイヤとして強力で、危険コマンドの拒否 / ファイル保護 / 観測ログ には間違いなく価値がある。一方で:

1. **exit code が workflow を支配する** ので、observation 系は exit 0 を死守する
2. **副作用が retry に乗らない** ので、Hook 内では git や外部 API を叩かない
3. **multi-repo では同期コストが重い** ので、Hook の中身はテンプレ化して逸脱を許さない
4. **Skill / verify\_commands と責務が被ると順序事故が起きる** ので、Hook = 観測 / 拒否 のみに切る

この 4 つを守ると Hook は静かに動く道具になる。逆にここを緩めると、 「セッションが意味不明な理由で止まる」 「リトライで commit が増殖する」 「ローカルとCI の挙動がずれる」 みたいな、原因が特定しづらい事故が一気に増える。

Hook は他の人がどう使っているかの情報がまだ少ないレイヤで、自分も settings.json を 1 つ触るたびに恐る恐る運用している。 Hooks の責務を 「観測 / 拒否 / コンテキスト注入」 のどれかに切ってる人、最近の運用で落ち着いてますか。「format は Hook ではなく pre-commit に降ろした」 とか、 「副作用系の Hook を別 worker に飛ばして fire-and-forget にしてる」 とか、 「multi-repo 同期は CI で diff を強制する仕組みを足した」 とか、設計判断の理由を一番知りたい。
