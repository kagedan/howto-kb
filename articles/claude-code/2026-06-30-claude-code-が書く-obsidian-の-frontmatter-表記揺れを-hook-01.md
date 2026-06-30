---
id: "2026-06-30-claude-code-が書く-obsidian-の-frontmatter-表記揺れを-hook-01"
title: "Claude Code が書く Obsidian の frontmatter 表記揺れを Hook と Templater で根絶する"
url: "https://zenn.dev/k_yoshiya/articles/claude-code-obsidian-frontmatter"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "LLM", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code に Obsidian の vault を触らせていると、**ノートを作るたびに frontmatter（プロパティ）の書き方が微妙に揺れる**問題に悩まされます。人間が UI から作れば Templater がテンプレートを当ててくれますが、Claude Code は `Write` でファイルを直接書き起こすため、CLAUDE.md などにルールを書いていたとしても、結構な頻度でテンプレート適用を素通りしてしまうのです。

この揺れは地味に効きます。キー名や値のフォーマットがブレると、**Dataview のクエリや Obsidian のプロパティ検索から本来ヒットすべきノートが漏れ**、vault の検索性が静かに損なわれていきます。

解決策はシンプルで、**frontmatter を Claude に書かせるのをやめ、Templater を通る経路でしかノートを作れないように縛る**ことです。道具は Claude Code の**フック**、Obsidian の**公式 CLI（`obsidian` コマンド）**、そして frontmatter を生成する **Templater**。第1部で frontmatter の形を固定し、第2部で残りの動的な値・Enum を扱います。

## なぜ frontmatter が揺れるのか

Claude Code がノートを新規作成するとき、典型的には `Write` ツールでファイル全体を一気に書き出します。frontmatter もその一部として、その場で「それっぽく」生成されます。

問題は、LLM の出力が本質的に確率的だという点です。指示やコンテキスト次第で、同じ意図でも出力がブレます。frontmatter で言えば、こういった揺れが起きます。

```
# あるときはこう
---
tags: [memo]
created: 2026/06/08
---
```

```
# 別のときはこう
---
created: 2026-06-08
tags:
  - memo
status: ""
---
```

キーの順序、日付の区切り文字、リストのスタイル、余計なキーの有無——どれも「間違い」ではないからこそ、プロンプトで完全に矯正するのは難しい。レビューで毎回直すのも現実的ではありません。

そこで方針を変えます。frontmatter を Claude に書かせるのをやめ、Templater のテンプレートから決定論的に生成させます。

## 第1部：frontmatter の形式を Templater と user スコープのフックで固定する

frontmatter の「決まった形」——キーの構成・順序・`created` の日付フォーマット——を、Templater で生成し、フックで「Templater を通る経路」以外を塞いで固定します。使うフックはどの vault でも共通なので、user スコープの `~/.claude/settings.json` に置きます。

### 仕組み① Templater で frontmatter を決定論的に生成する

まず土台として、Templater のフォルダテンプレートを用意します。Templater には「特定フォルダにノートが作られたら、対応するテンプレートを自動で当てる」機能があります。

プラグイン設定（`.obsidian/plugins/templater-obsidian/data.json`）で、次の2つを有効にしておきます。

* `trigger_on_file_creation: true` — ファイル作成をトリガーにテンプレートを自動適用する
* `enable_folder_templates: true` — フォルダごとにテンプレートを割り当てる

そのうえで、フォルダとテンプレートの対応を定義します。

```
{
  "trigger_on_file_creation": true,
  "enable_folder_templates": true,
  "folder_templates": [
    { "folder": "memo", "template": "templates/memo.md" },
    { "folder": "daily", "template": "templates/daily.md" }
  ]
}
```

テンプレート本体はこんな具合です。frontmatter を含めて、出力の形が完全に固定されています。

```
---
created: <% tp.date.now("YYYY-MM-DD") %>
status: draft
summary: ""
tags:
  - memo
---
## メモ

## タスク

## 関連リンク
```

`memo` フォルダにノートが作られると、Templater が自動でこのテンプレートを流し込み、`<% tp.date.now("YYYY-MM-DD") %>` を当日の日付に展開します。**誰が（人間でも Claude でも）作っても、frontmatter は寸分違わず同じ形になる。** これが表記揺れ対策の土台です。

なお `created` や `status` のように決定論的に決まる値は、ここで確定します。一方 `summary`（そのノートの1行要約）のように**内容に依存する値はテンプレートには書けません**。これは空のプレースホルダにしておき、作成直後に埋めます（仕組み④）。

問題は「**Claude Code にこの経路を必ず通させる**にはどうするか」。`Write` ツールで直接ファイルを書かれてしまっては、Templater のトリガーは発火しません。ここで Hook の出番です。

### 仕組み② Write を塞いで `obsidian create` へ誘導する

Claude Code の Hooks を使い、`PreToolUse`（ツール実行直前）で `Write` をインターセプトします。`~/.claude/settings.json` に次のように登録します。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "if": "Write(/Users/you/ObsidianVault/MyVault/**)",
            "command": "~/.claude/hooks/obsidian-md-guard.sh",
            "statusMessage": "Obsidian vault ガード確認中..."
          }
        ]
      }
    ]
  }
}
```

ここで効くのが `if` フィールドです。`matcher` はツール名でしかフィルタできないため、`"matcher": "Write"` だけだと無関係な `Write` でもフックが起動し、`statusMessage` のスピナー（「Obsidian vault ガード確認中...」）が毎回出てしまいます。スクリプト側で早期 return しても、起動後なので表示は止められません。

そこで `if`（Claude Code v2.1.85 以降）で、**起動前に**パスを見て絞り込みます。permission ルールと同じ構文で、`tool_input.file_path` が `Write(/Users/you/ObsidianVault/MyVault/**)` にマッチしたときだけ起動。これで無関係な `Write` ではスピナーすら出ません。

フック本体は、**vault 内の `.md` の「新規作成」だけ**を `deny` し、代わりに `obsidian create` を使うよう Claude に伝えるスクリプトです。`if` でパスは vault 配下に絞れていますが、`.md` 以外・既存ファイル・ドットディレクトリの除外まではフィルタしきれないので、最終的な判定はスクリプト側で行います。

```
#!/usr/bin/env bash
# Obsidian vault 内での Markdown「新規作成」を Write ツールではなく
# Obsidian CLI (obsidian create) に誘導する PreToolUse フック。
# テンプレート適用を強制するのが目的。

vault="$HOME/ObsidianVault/MyVault"

input="$(cat)"
tool="$(printf '%s' "$input" | jq -r '.tool_name // empty')"
path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

# Write 以外・vault 外・.md 以外は対象外
[ "$tool" = "Write" ] || exit 0
[ -n "$path" ] || exit 0
case "$path" in "$vault"/*) ;; *) exit 0 ;; esac
case "$path" in *.md) ;; *) exit 0 ;; esac

# ドットディレクトリ配下（.obsidian / .claude / .git など）は除外
case "$path" in */.*/*) exit 0 ;; esac

# 新規作成のみブロック（既存ファイルの上書き・編集は許可）
if [ -e "$path" ]; then
  exit 0
fi

rel="${path#"$vault"/}"

reason="このパスは Obsidian vault 内です。Write ツールではなく Obsidian CLI でノートを作成してください（Templater のフォルダテンプレートを効かせるため）。

  cd \"$vault\" && obsidian create path=\"$rel\"

CLI の template= は使わないこと。テンプレートは Templater が作成時に自動適用する。"

jq -n --arg r "$reason" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: $r
  }
}'
```

ポイントは4つです。

* **二段構えのフィルタ**: `if` でパスを見て起動を判定し、その先の細かい除外（`.md` 限定・新規のみ・ドットディレクトリ除外）はスクリプトが担う。
* **新規作成だけを塞ぐ**: `[ -e "$path" ]` で既存ファイルは素通り。frontmatter が確定するのは作成時だけなので、**既存ノートの編集は今まで通り `Write`/`Edit` でできる**。
* **ドットディレクトリを除外**: `.obsidian`・`.claude`・`.git` などの設定ファイルは CLI 経由だと不便なので、`*/.*/*` を対象外に。
* **`deny` + 理由文で誘導**: 返した理由文（`permissionDecisionReason`）が Claude にフィードバックされ、Claude は「では `obsidian create` を使おう」と**自分で経路を切り替えます**。ブロックして終わりではなく、正しいやり方をその場で教えるのがコツです。

なお `obsidian create` は Obsidian 1.12 系の**公式 CLI**です。`/Applications/Obsidian.app/Contents/MacOS/obsidian` を `obsidian` として PATH に通せば使えます。

```
obsidian create path="memo/新しいメモ.md"
```

ファイルが作られると Obsidian 本体が検知し、Templater の `trigger_on_file_creation` が発火。`memo` フォルダ配下なので `templates/memo.md` が自動適用され、frontmatter が決定論的に流し込まれます。

### 仕組み③ `template=` を禁止してハマりどころを塞ぐ

ここで一つ罠があります。`obsidian create` には `template=<name>` というオプションがあり、一見「テンプレートを指定して作る」ために使いたくなります。

しかし、`template=` が参照するのは Obsidian の**コアプラグイン**「**Templates**」であって、**Templater（コミュニティプラグイン）ではありません**。Templater 運用でコア Templates を無効にしていると、`template=` を付けた瞬間にこうなります。

```
Error: Templates plugin is not enabled
```

しかも厄介なことに、Templater のフォルダテンプレートは `path=` だけで作成すれば自動で当たるので、**`template=` はそもそも不要**です。不要なうえにエラーを招く、純粋に有害なオプションというわけです。

Claude が気を利かせて `template=` を付けてしまうのを防ぐため、もう一つ `PreToolUse` Hook を足します。今度は `Bash` ツールが対象です。②と同じ考え方で、ここでも `if` を使って**フックの起動そのものを `obsidian create` を含むコマンドだけに絞り込みます**。

```
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "~/.claude/hooks/obsidian-template-guard.sh",
      "if": "Bash(obsidian create:*)",
      "statusMessage": "obsidian create ガード確認中..."
    }
  ]
}
```

`matcher` は `Bash` でしかフィルタできないので、`if` を付けないと**あらゆる Bash コマンドのたびにこのフックが起動し**、「obsidian create ガード確認中...」のスピナーが毎回出てしまいます。`if: "Bash(obsidian create:*)"` で、`obsidian create` から始まるコマンドのときだけフックを起動するようにします（`Bash(...:*)` は末尾ワイルドカードのプレフィックス指定で、`Bash(obsidian create *)` と等価です）。

フック本体は、`if` で `obsidian create` 入りに絞られたうえで、さらに `template=` も**含むときだけ** `deny` します（`obsidian create` の判定は `if` と二重になりますが、フック単体でも安全側に倒れるよう残しています）。

```
#!/usr/bin/env bash
# Bash で `obsidian create ... template=...` を実行しようとしたらブロックする。
# この vault のテンプレートは Templater。コア「Templates」は無効なので
# CLI の template= は `Templates plugin is not enabled` になる。
# Templater は folder templates + trigger_on_file_creation で
# 対象フォルダにファイルを作るだけで自動適用される。template= は不要かつ有害。

input="$(cat)"
tool="$(printf '%s' "$input" | jq -r '.tool_name // empty')"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

[ "$tool" = "Bash" ] || exit 0
[ -n "$cmd" ] || exit 0

# `obsidian create` と `template=` の両方を含むときだけブロック
printf '%s' "$cmd" | grep -q 'obsidian[[:space:]]\+create' || exit 0
printf '%s' "$cmd" | grep -q 'template=' || exit 0

reason="obsidian create の template= は使わないでください。この vault は core「Templates」プラグインが無効なので template= はエラー（Templates plugin is not enabled）になります。

代わりに template= を外し、path= だけで作成してください:

  obsidian create path=\"<vault相対パス>\"

テンプレートは Templater が作成時に自動適用します。"

jq -n --arg r "$reason" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: $r
  }
}'
```

これで、`obsidian create path=... template=...` のような呼び出しは未然に弾かれ、理由文で「`path=` だけにしてね」と誘導されます。

**ここまでが第1部です。** 作成の入口を Templater 経由に縛ったことで、frontmatter の形式は誰が作っても決定論的に揃うようになりました。表記揺れのほとんどは、これで消えます。

## 第2部（応用）：動的な値と Enum を、プロジェクトローカルのフックで扱う

ここで、frontmatter の値を3種類に整理しておきます。種類によって扱い方が変わるからです。

1. **静的・決定論的な値**（`created` など）: 常に同じルールで決まる。**第1部の Templater で固定済み**。
2. **Enum 値**（`status` など）: 取りうる値は `draft` / `in-progress` / `done` のように決まっている。決定論的ではあるが、Templater は作成後の編集まで強制できず、編集の際に Claude が `done` を `finished` に書き換えるなど、許容値の同義語へ勝手にずらしてしまいがち。
3. **動的な値**（`summary` など）: ノートの内容に依存し、人間がつけても煩雑。**中身は Claude に任せてよい**。ただし形式（キー名・1行・クォート）は揃えたい。

第1部が 1 を固定しました。第2部で扱うのは 2 と 3 で、**動的な値（3）を④で促し、Enum（2）を⑤で検証します**。これらは「`summary` をどう埋めるか」「`status` の許容値は何か」といったプロジェクトごとに変わるルールなので、user スコープではなく対象フォルダ直下の**プロジェクトローカル `.claude/settings.json`** に置きます。

使うのは `PostToolUse` フックです。ツール実行の**直後**に走り、`deny`（実行を止める）ではなく `additionalContext` に文字列を返すと、それが Claude のコンテキストに注入され、Claude が次の行動でそれを読んで動きます。「ブロックする」のではなく「次にやることを差し込む」のが、第1部の `PreToolUse` との違いです。

### 仕組み④ 作成直後に「動的な値」を埋める

Templater は `created` のような決定論的な値は展開できますが、「そのノートが何のメモか」といった**内容に依存する値**は埋められません。これは Claude に書いてもらうしかない。とはいえテンプレートにプレースホルダ（`summary: ""`）を置いて「埋めてね」と祈るだけでは、しばしば素通りされます。

ここがこの仕組みの肝です。`PostToolUse`（Bash）で、`obsidian create` の**直後に、埋め方そのものをプロンプトで具体的に指示します**。テンプレートに「あとで埋めてね」と書いておくだけだと素通りされがちですが、作成された瞬間に「この値を・この形式で入れて」と渡すと、Claude の記入精度は驚くほど上がります。これはプロジェクトローカルの `.claude/settings.json` に登録します。

```
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-note-create.sh",
      "statusMessage": "ノート後処理を案内中..."
    }
  ]
}
```

フック本体は、作成パスが `memo` 配下のときだけ、`summary` を埋めるよう **`additionalContext` で指示**します。フォーマット（1行・ダブルクォート）まで文面で指定するのがポイントです。

```
#!/usr/bin/env bash
# PostToolUse (Bash) フック:
# obsidian create でノートを作成した直後に、テンプレートでは固定できない
# 動的な frontmatter（summary など）を埋めるよう Claude に促す。

input="$(cat)"
tool="$(printf '%s' "$input" | jq -r '.tool_name // empty')"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

[ "$tool" = "Bash" ] || exit 0
[ -n "$cmd" ] || exit 0
printf '%s' "$cmd" | grep -q 'obsidian[[:space:]]\+create' || exit 0

# 作成パス（path="..."）を取り出し、memo 配下の .md のみ対象
notepath="$(printf '%s' "$cmd" | grep -oE 'path="[^"]+"' | head -1 | sed -E 's/^path="//; s/"$//')"
case "$notepath" in
  memo/*.md | */memo/*.md) ;;
  *) exit 0 ;;
esac

reason="memo にノートを作成しました: ${notepath}
frontmatter の summary を、このノートの内容に沿った1行要約で埋めてください（形式: summary: \"...\"）。"

jq -n --arg r "$reason" '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: $r
  }
}'
exit 0
```

これで、**値そのもの**（ノートごとに違う要約）は Claude が書きつつ、**形式**（キー名・1行・クォート）はフック側で固定されます。「動的だが揃っている」frontmatter になるわけです。

### 仕組み⑤ 更新時に Enum を検証する

新規作成時は、実は心配いりません。作成は `obsidian create` 経由（②③）で、Templater が `status: draft` のような**正しい既定値**を書き込むので、Enum は作られた時点で必ず許容値です。そもそも作成は `Edit`/`Write` を通らない（`obsidian create` は Bash）ので、このフックは作成時には起動しませんし、起動する必要もありません。

問題は**作成後の編集**です。後からノートを直すうちに、たとえば `done` を `finished` と書いてしまうなど、Enum が許容値の同義語へずれることがあります。これを `Edit`/`Write` の**たびに**検証し、許容値から外れていれば指摘するのが、もう一つの `PostToolUse` フックです。これも④と同じくプロジェクトローカルの `.claude/settings.json` に置きます。

```
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/frontmatter-validate.sh",
      "statusMessage": "frontmatter 検証中..."
    }
  ]
}
```

`matcher` の `Edit|Write` は「`Edit` か `Write`」の意味で、どちらの編集後にも走ります。対象フォルダの絞り込みはローカル設定＋スクリプト冒頭のパス判定に任せ、ここでも `if` は使いません。

フック本体は、`memo` 配下のノートの frontmatter を取り出し、`status` が許容値から外れていれば `additionalContext` で指摘します。**値が入っているのに許容値から外れている場合だけ**を対象にし、空・未設定は見逃します。

```
#!/usr/bin/env bash
# PostToolUse (Edit|Write) フック:
# memo 配下のノートを編集した後、frontmatter の status が許容値から
# 外れていれば Claude に指摘する。作成後の編集で値が崩れるのを防ぐ。

input="$(cat)"
tool="$(printf '%s' "$input" | jq -r '.tool_name // empty')"
fp="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

case "$tool" in Edit|Write) ;; *) exit 0 ;; esac
[ -n "$fp" ] || exit 0
[ -f "$fp" ] || exit 0
case "$fp" in */memo/*.md) ;; *) exit 0 ;; esac

# frontmatter ブロック（先頭 --- 〜 次の ---）を抽出
fm="$(awk 'NR==1{if($0!="---")exit; next} /^---[[:space:]]*$/{exit} {print}' "$fp")"
[ -n "$fm" ] || exit 0

status="$(printf '%s\n' "$fm" | grep -E '^status:' | head -1 | sed -E 's/^status:[[:space:]]*//; s/[[:space:]]+$//')"

problems=""
case "$status" in
  ""|draft|in-progress|done) ;;
  *) problems="- status: \"$status\" は許容値外 → draft / in-progress / done のいずれかにする\n" ;;
esac

[ -z "$problems" ] && exit 0

reason="$(printf '%b' "frontmatter の値に問題があります（${fp}）:\n${problems}許容値に合わせて修正してください。")"
jq -n --arg r "$reason" '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: $r
  }
}'
exit 0
```

実フックでは `status` 以外にも、内部リンクの `"[[...]]"` 形式や必須キーの有無などをまとめて検査できます。要は「作成時のガードをすり抜けた値・後から崩れた値」を編集のたびに拾い、Claude に直させる仕組みです。

## まとめ：作成から更新まで一貫して揃える

5つが揃うと、ノートの作成から更新までが次のように一本道に収束します。

```
【作成時】
Claude が memo/新しいメモ.md を Write で作ろうとする
  └─ ②の Write フックが deny → 「obsidian create を使って」と誘導
       └─ Claude が `obsidian create path="memo/新しいメモ.md"` を実行
            ├─ template= を付けたら ③の Bash フックが deny → path= だけに誘導
            └─ 作成成功
                 ├─ ①の Templater が発火 → frontmatter の形式が決定論的に確定
                 └─ ④の PostToolUse フックが促す → Claude が summary を指定形式で記入

【更新時】
Claude / 人間が memo のノートを Edit/Write
  └─ ⑤の PostToolUse フックが frontmatter を検証
       └─ 許容値・形式から外れていれば指摘 → Claude が修正 🎉
```

重要なのは、**frontmatter を生成・維持する主体が Claude から「テンプレート＋フック」に移った**ことです。Claude がどんなに気まぐれでも、frontmatter の形式は Templater が固定し、動的な値は④が形式を揃え、後からの崩れは⑤が拾う。プロンプトでお願いするのではなく、**経路を絞って構造で担保した**わけです。`deny` も `additionalContext` も、ブロックして終わりにせず正しい手順を文面で返すのがコツで、**Hook は「禁止」より「ガードレール」として設計するのが効きます**。

## おわりに

突き詰めると、この記事の本質は frontmatter よりも、「**AI の出力を揃えたいなら、プロンプトで矯正するより、揃った経路しか通れないようにする**」という考え方にあります。Templater のような決定論的な生成器と Hook を組み合わせるこの型は、Obsidian に限らず「決まったやり方を守らせたい」あらゆる場面で効くはずです。
