---
id: "2026-05-20-claude-code-hooks実例集-本番運用で書いた6つの設定-01"
title: "Claude Code hooks実例集 — 本番運用で書いた6つの設定"
url: "https://note.com/coyote154/n/n1b4027360360"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "note"]
date_published: "2026-05-20"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

## この記事で扱うこと

Claude Codeを業務で使い始めると、ある時点で必ずぶつかる壁があります。Claudeに任せた作業のなかで、人間にやられたら一瞬でキレる種類のミスが起きる場面です。force-pushでローカルの未push分が吹き飛びます。マイグレーションファイルを消されます。pre-commitフックを--no-verifyで素通りされて、壊れたコードがcommitされます。

私の手元では、これらをすべてhooksで物理的に防いでいます。CLAUDE.mdに「やらないで」と書くだけでは足りません。Claudeは時々忘れますし、忘れたときの代償が大きすぎます。hooksはこの代償をゼロにする層です。

この記事では、私が業務システムの本番プロジェクトで実際に動かしているhooks設定を6つ、すべて動くJSONとシェル例つきで紹介します。コピペで効かせられる粒度で書きました。

対象読者は次のような人を想定しています。

* Claude Codeを業務で使っていて、任せた結果の事故を1回以上経験したことがある人
* settings.jsonのhooks欄を開いてはみたが、書き方の例が薄くて止まった人
* チームに配布できる「Claudeの危険行動を止める」設定セットがほしい人

なお、本記事はシリーズ「Claude Code運用ノウハウ」の2本目です。1本目はskillのdescription設計について書いています。あわせて読むと、Claudeを呼び出す側（skills）と止める側（hooks）の両輪が見えます。

## なぜhooksなのか

昨日の記事で扱ったのは、Claudeに「やってほしいこと」を確実に呼び出させる設計、すなわちskillでした。今日の記事は逆方向の力を扱います。「やってほしくないこと」を物理的にさせない仕組みです。

skillsやCLAUDE.mdは説得と誘導の道具で、無視されることがあります。hooksは違います。stdinで動くシェルコマンドが介在し、exit codeで実行をブロックできます。

具体的には、ClaudeがBashやEditなどのツールを呼ぼうとするタイミングで、こちらが書いた任意のシェルコマンドが先に走ります。そのコマンドがexit 2を返すと、ツール呼び出しはブロックされ、stderrの内容がClaudeに「これはやるな、理由はこれ」と伝えられます。Claudeはそれを読んで諦めるか、別の手段を試します。

つまりhooksは、CLAUDE.mdに「force-pushしないでね」と書いてClaudeの善意に頼るのではなく、「force-pushは絶対できない」とOS層に近いところで強制する仕組みです。事故を一度でも経験すると、この差は大きいです。

## hooksの仕組みざっくり

設定は~/.claude/settings.json（全プロジェクト共通）か、プロジェクトの .claude/settings.json（そのリポジトリだけ）に書きます。形はこんな感じになります。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "ここにシェルコマンド"
          }
        ]
      }
    ]
  }
}
```

イベントの種類は主に5つあります。PreToolUseはツール呼び出し直前、PostToolUseは呼び出し直後、UserPromptSubmitはユーザーのプロンプト送信時、Notificationは通知時、Stopはセッション終了時です。今日の例ではPreToolUseとUserPromptSubmitを使います。

matcherは反応するツール名のパターンです。Bashなら全Bash呼び出し、Edit|Writeなら編集系両方、空文字なら全部に反応します。tool\_nameは大文字始まりで一致する点に注意してください。Bashは効きますがbashは効きません。

commandの中では、stdinからJSONを受け取れます。BashのPreToolUseならこんなJSONが来ます。

```
{
  "session_id": "...",
  "tool_name": "Bash",
  "tool_input": {
    "command": "git status"
  }
}
```

これをjqで抜いて検査します。exit 0なら通します。exit 2ならブロックしてstderrをClaudeに送ります。exit 1は一般エラー扱いで、Claudeが「謎に失敗した」と再試行する可能性があるので避けます。ブロックしたいなら必ずexit 2と覚えてください。

この基礎だけで、以下の6例は全部読めます。

---

## 実例1 force-pushを物理的に禁止する

事故の現場。Claudeにブランチの整理を任せたら、main上でgit push --forceを実行されました。リモートにある同僚のコミットを吹き飛ばす一歩手前で気づきました。CLAUDE.mdには「force-push禁止」と明記していました。Claudeは時々忘れます。

このhookで止めます。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "cmd=$(jq -r '.tool_input.command'); if echo \"$cmd\" | grep -qE 'git push.*(--force|--force-with-lease|-f)( |$)'; then echo 'force-push is forbidden in this project. Use a separate branch and PR instead.' >&2; exit 2; fi; exit 0"
          }
        ]
      }
    ]
  }
}
```

ポイントは3つあります。

ひとつめ、grep -qEで正規表現マッチさせています。--forceと--force-with-leaseと-fの3パターンを並べました。--force-with-leaseは比較的安全な選択肢として勧められることがありますが、それでも事故は起きるので私は両方止めています。

ふたつめ、stderrに理由を書いてexit 2します。理由文はClaudeへのメッセージとして機能します。Claudeはこの文を読んで「force-pushはダメ、別ブランチとPRに切り替えよう」と判断します。理由を書かずexit 2だけすると、Claudeは「謎に失敗した」と認識して別のコマンドで再試行することがあるので、必ず人間に書くつもりで理由文を書いてください。

みっつめ、マッチしなかった場合のexit 0を忘れないでください。これを書き忘れると最後のif終了ステータスがそのまま返り、無関係なBashが死にます。コピペするときも末尾のexit 0は省かないでください。

## 実例2 cat / head / tailでファイルを読ませない

Claude CodeにはRead toolがあります。これを使うと行番号つきで構造化された出力が返り、画像やPDFも見られます。一方、ClaudeはたまにBashでcat foo.mdなどと書いてしまいます。これは行番号もつかず、ページングもなく、レビューしづらいです。Read toolを使わせたいです。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "cmd=$(jq -r '.tool_input.command'); if echo \"$cmd\" | grep -qE '^[[:space:]]*(cat|head|tail)[[:space:]]+[^|]+\\.(md|ts|tsx|json|yaml|yml|py|sql)[[:space:]]*$'; then echo 'Use Read tool for file inspection. cat / head / tail produces unstructured output and is harder to review.' >&2; exit 2; fi; exit 0"
          }
        ]
      }
    ]
  }
}
```

このhookには2つの工夫が入っています。

ひとつ、ファイル拡張子で対象を絞っています。.md, .ts, .tsx, .json, .yaml, .yml, .py, .sqlを列挙しました。これをやらないとcat /etc/hostsのような正当な用途まで止まります。拡張子は自分のスタックに合わせて足し引きしてください。

ふたつ、パイプ込みのコマンド（cat [foo.md](http://foo.md) | grep bar）は通しています。正規表現の[^|]+がパイプ前で止まる役目を果たしています。生のテキスト表示だけを止めたい意図です。grepやフィルタリングに使うcatはそのまま動きます。

## 実例3 マイグレーションファイルの削除を禁止する

マイグレーションファイルは履歴そのものです。「一度commitしたら削除しない、修正するならdown-migrationを新規作成する」が普遍ルールですが、Claudeは時々「不要そうな古いマイグレーションを整理しますね」と消そうとします。これを止めます。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "cmd=$(jq -r '.tool_input.command'); if echo \"$cmd\" | grep -qE 'rm[[:space:]].+(supabase/migrations|prisma/migrations|/migrations/)'; then echo 'Migration files must never be deleted. They are append-only history. To revert a schema change, write a new down-migration.' >&2; exit 2; fi; exit 0"
          }
        ]
      }
    ]
  }
}
```

Supabase, Prisma, またはmigrations/という共通ディレクトリ名にヒットさせています。プロジェクトのDBスタックに合わせて並べてください。

Bash rm以外に、Editで空にする攻撃ベクトルもあります。完全に防ぐにはmatcherにEditを足してファイルパスを検査する必要がありますが、私の経験では事故のほぼ全部がBash rmで来るので、まずはこの形で十分です。

## 実例4 実装計画書なしの実装着手を警告する

私の運用では、実装に入る前に必ずObsidianに計画書を書くルールにしています。これを守られないと、何を変えたか後で追えなくなります。UserPromptSubmitフックで警告します。

```
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "prompt=$(jq -r '.user_prompt' 2>/dev/null || echo ''); if echo \"$prompt\" | grep -qE '実装して|機能を追加|作って|書いて'; then today=$(date +%y%m%d); vault=\"$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents\"; if ! find \"$vault\" -name \"${today}_*.md\" -mmin -1440 2>/dev/null | grep -q .; then echo \"今日の計画書 (${today}_*.md) が見当たりません。先にObsidianで計画書を作成してから着手することを推奨します。\" >&2; fi; fi; exit 0"
          }
        ]
      }
    ]
  }
}
```

このhookはexit 0にしています。実装プロンプトと判定したときも、ブロックではなく警告を出すだけです。理由は「ちょっと調べてほしい」のような探索系プロンプトまで巻き込むと使いづらいからです。stderrに出した警告はClaudeに届くので、Claudeが「あ、計画書がないから先に書こう」と動く確率が上がります。

vaultのパスとプロンプト判定のキーワードは、自分の運用に合わせてください。「実装して」「機能を追加」「作って」「書いて」のいずれかが含まれるプロンプトを実装着手とみなしています。

## 実例5 --no-verifyを禁止する

git commit --no-verifyはpre-commitフックを飛ばします。これを許すと、lintやtypecheckが通っていないコードがcommitされます。フックが失敗した正当な理由がある場合は、フック自体を一時的に無効化するか、内容を修正するべきで、--no-verifyで素通りさせるのは別の問題を呼びます。

```
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "cmd=$(jq -r '.tool_input.command'); if echo \"$cmd\" | grep -qE 'git[[:space:]]+(commit|push).*--no-verify'; then echo '--no-verify is forbidden. If a hook is failing, fix the underlying issue or temporarily disable the hook in .husky/, do not bypass it.' >&2; exit 2; fi; exit 0"
    }
  ]
}
```

このhookと実例1のforce-push禁止は、同じmatcher (Bash)の下に並べて書けます。settings.jsonの"hooks"配列に複数のエントリを置けば、ClaudeがBashを呼ぶたびに全部が順に評価されます。どれかがexit 2した時点でブロックされます。

## 実例6 .envを誤ってcommitするのを防ぐ

これは本来 .gitignoreで防ぐべきです。ですが、新しいプロジェクトでまだgitignoreが整っていないとき、あるいは既存プロジェクトでgitignoreから漏れている.env.localのようなファイルがあるとき、hooks側で二重に止めると安心できます。

```
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "cmd=$(jq -r '.tool_input.command'); if echo \"$cmd\" | grep -qE '(git[[:space:]]+add|git[[:space:]]+commit).*\\.env(\\.|[[:space:]]|$)'; then echo '.env files contain secrets and must not be committed. Add to .gitignore if not already.' >&2; exit 2; fi; exit 0"
    }
  ]
}
```

正規表現で .envと .env.localと .env.productionなどを拾うようにしています。git add .envもgit commit -m "..." .envも両方対象です。

実例5と6は実例1と同じmatcherでまとめられます。私のsettings.jsonではBash matcherの下に複数のhooksエントリを並べ、それぞれが独立に判断する形にしています。

## デバッグの落とし穴

hooksを書き始めて最初にハマるところを5つ。

ひとつ。jqがないと動きません。macOSならbrew install jq、Linuxならapt install jqです。Claude Codeはsystem shellで動くので、PATH上にjqが必要です。

ふたつ。bashのクオートが面倒です。JSONのcommand文字列の中でダブルクオートを使うと、JSON側のエスケープと衝突します。基本はシングルクオートで囲みます。複雑になりそうなら、コマンドを別ファイルのシェルスクリプトに切り出して、commandを"/path/to/check.sh"で呼ぶほうが保守しやすいです。

みっつ。exit 2でブロックできるのはPreToolUseとUserPromptSubmitだけです。PostToolUseでexit 2しても「もう実行は終わっている」のでブロックにはなりません。事前防止はPreToolUse、事後通知はPostToolUseと使い分けてください。

よっつ。hookが本当に動いているか確認したいときは、commandの冒頭にdate >> /tmp/claude-hooks.logを入れて発火を観察するのが速いです。Claude Codeのデバッグログでも見えますが、まず自分で書いた行がファイルに記録されるかを確認してください。

いつつ。matcherを書き間違えると無発火になります。Bashは効きますがbashは効きません。Edit, Write, Read, Bashすべて大文字始まりです。複数ならEdit|Writeのようにパイプで並べます。

## 自分のプロジェクトに1つだけ入れるなら

6つ全部入れるのは大変だと感じたら、まずforce-push禁止だけを入れることをお勧めします。これ1つで防げる事故の質が桁違いに大きいです。チームのコミット履歴破壊は復旧コストが極端に重く、信頼関係の毀損まで含めると数日仕事になります。

慣れたら2番目に--no-verify禁止です。3番目にmigration削除禁止です。4番目以降は自分の運用に合わせて入れてください。

cat / head / tail禁止はClaude側のクセを矯正したい人向けで、優先度は下がります。

## まとめ

Claude Code hooksは、CLAUDE.mdに書いた「お願い」を「強制」に変える層です。文章で説得するより、シェルで止めるほうが信頼できる場面があります。

6例の中から、自分のプロジェクトに必要なものを1つずつ入れていけばよいです。settings.jsonに数行追加するだけで、Claudeへの信頼の質が変わります。事故が起きうる経路を1つずつ塞ぐ作業は、面倒ですが、後から戻ってきて感謝します。

## コメント歓迎

自分のプロジェクトで実際に動かしているhooks設定があれば、ぜひコメントで教えてください。「うちはこれで救われた」「この事故をhookで防ぎたい」というネタもお待ちしています。次回以降の記事に反映していきます。

---

この記事はAIコーディングエージェント(Claude)に推敲してもらっています。事例・所感は私自身の運用経験に基づきます。コードは各自の環境でテストしてから本番運用してください。
