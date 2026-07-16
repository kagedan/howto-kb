---
id: "2026-07-16-claude-code-の-plan-モードをループエンジニアリングで楽にする-01"
title: "Claude Code の Plan モードをループエンジニアリングで楽にする"
url: "https://zenn.dev/k_yoshiya/articles/claude-code-plan-mode-loop"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code の Plan モードを、人間の労力を少なくして使いこなすためのループエンジニアリングをしてみました。この記事を読むと、hook を使って Plan モードに「質問による要件詰め」「実装のサブエージェント委譲」「計画の HTML 確認」を自動で組み込む方法がわかります。

## ねらい

Plan モードの運用に、次の 3 つを組み込みます。うち 1 と 3 の一部（reject 時の再生成サイクル）が反復＝ループ、2 はモデル/セッションの割り当て設計（いわゆるハーネス寄り）です。

1. Plan モードの初回プロンプト以降のタイピング負荷を `AskUserQuestion` で落とす（曖昧点がなくなるまで質問を繰り返す反復構造）
2. 作業効率化を自動的なオーケストレーションで実現する。同時にセッション context の汚れを防止し、トークン使用量を削減（Sonnet 利用）する
3. Plan の出力を視覚的な HTML にレンダリングしてブラウザで確認する（reject 時は plan 修正→再生成→再確認のループに入る）

1 と 3 は、それっぽい計画を作ることを防止します。計画承認後は基本的に auto mode に入るので、計画をちゃんとしないと後々大変な修正量になるからです。3 は公式推奨ではないと思いますが、割と流行っている確認方法だと思っています。  
2 はよく言う「考える部分は Fable や Opus で、実装は Sonnet で」と、セッションの切り分けを同時に行う方法です。これも、Plan モードのような大規模タスクにおいては公式で推奨されています。

## 全体像

構築後の Plan モードは次の流れで進みます。

1. Plan モードに入ると、hook が運用ルールをコンテキストに注入する。Claude はこのルールに従って動く
   * `AskUserQuestion` で曖昧な点がなくなるまでインタビューする
   * plan md の確定時、末尾にマーカー行を書く
   * 承認後の実装はメインセッションで行わず、モデルを明示したサブエージェントや `claude --bg` に委譲する
2. マーカーを検知した hook が headless の `claude -p` でプランを HTML に変換する
3. Claude が HTML を Claude Artifact として公開し、その URL をブラウザで自動的に開いてから `ExitPlanMode` を呼ぶ
   * reject すると Claude が plan md を修正し、HTML が自動で再生成・再公開されて再び `ExitPlanMode` が来る
   * 以降の実装は 1. のルールに従って委譲で進み、メインセッションは指示と検収に徹する

## 1. Plan モード限定で運用ルールを Hook で注入する

ここでは hook を使用して、Plan モードの初回プロンプトを打ち込んだ際に、全セッション共通の運用ルールを差し込みます。  
次の 2 点はこの hook に固定するので、毎回指示する必要がなくなります。

> 1. Plan モードの初回プロンプト以降のタイピング負荷を `AskUserQuestion` で落とす
> 2. 作業効率化を自動的なオーケストレーションで実現する。同時にセッション context の汚れを防止し、トークン使用量を削減する

すべての hook は stdin の JSON で `permission_mode` を受け取ります（Plan モード時の値は `"plan"`）。  
これを使うと「Plan モードのときだけ効く指示」を `UserPromptSubmit` hook で注入できます。`~/.claude/settings.json` への登録は次のとおりです。

```
"UserPromptSubmit": [
  {
    "hooks": [
      { "type": "command",
        "command": "/Users/you/.claude/hooks/plan-mode-workflow.sh" }
    ]
  }
]
```

hook スクリプト本体は折りたたみに載せます。やっていることは次の 2 点です。

* 要件の曖昧な点がなくなるまで `AskUserQuestion` で繰り返し質問する
* 実行は `claude --bg` と `claude -p` およびサブエージェントに委任する。モデルは公式推奨の `Sonnet` をベースにする。今回は触れないが、エージェントのデフォルトモデルを `Opus` にしておけば、複雑な処理は Opus にできる

plan-mode-workflow.sh（クリックで展開）

```
#!/bin/bash
# ~/.claude/hooks/plan-mode-workflow.sh
# UserPromptSubmit hook: permission_mode が plan のときだけ Plan モード運用指示を注入する
input=$(cat)
mode=$(printf '%s' "$input" | jq -r '.permission_mode // empty')
[ "$mode" = "plan" ] || exit 0

context=$(cat <<'EOF'
# Plan モード運用ルール（このセッションで必ず適用する）
1. インタビュー: 初回プロンプトの後、要件の曖昧な点がなくなるまで AskUserQuestion で繰り返し質問する。1ラウンドで打ち切らず、回答から新たな曖昧点が生じたら追加で質問する。
2. plan 確定シグナル: plan ファイルが確定したら、ExitPlanMode を呼ぶ前に plan md の末尾にマーカー行 <!-- render --> を追記して保存する。その直後に届くシステム通知の手順に従い、それが完了するまで ExitPlanMode を呼ばない。
3. 実行の委譲: ExitPlanMode 承認後、メインセッションではファイル編集・実装コマンドを直接実行しない。通常タスクは Agent ツール（model は 4. の基準で扱う）、長時間・独立性が高い・別ディレクトリの作業は claude --bg --model <model>、単発の非対話処理は claude -p --model <model> に委譲する。メインセッションの役割はタスク分割・指示・結果の検収・統合・報告のみ。例外: 会話全体の文脈を把握していないと実施できないタスク（plan 全体との整合が必要な統合・最終調整など）に限りメインセッションで実施してよい。それ以外の実装作業をメインセッションで行うことは不可。
4. モデル振り分け: 汎用エージェント（general-purpose 等）は model を明示し、基本は sonnet、設計判断・複雑なデバッグ・広範囲の変更など高難度タスクは opus を指定する。plan 策定のための調査・設計サブエージェント（Explore / Plan）には opus を使う。カスタムエージェントは model を渡さず frontmatter の定義に任せる。上書きしてよいのは高難度タスクで opus に引き上げる場合のみで、sonnet への引き下げ上書きはしない。
EOF
)
jq -n --arg ctx "$context" '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $ctx}}'
```

> 通常モードのセッションでは何も出力せず終わるので、副作用はゼロです。CLAUDE.md に書かないため、環境を汚しません。

## 2. Plan モードで HTML を作成する

### HTML の出力と問題点

Plan モードは計画が固まると、最終確認として万里の長城よりなっがいマークダウンと `ExitPlanMode` の承認が最後に出力されます。  
図解されていないマークダウンを読むのは結構しんどいので、HTML で確認したいです。

しかし、**ここで問題が生じます。Plan モードはファイル作成ができないモードのため、HTML ファイルも作れません**。  
ちなみに、今回使う Claude Artifacts も一度ローカルに HTML ファイルを作らないといけない仕様のため、ローカルに作らずに確認することはできません。

### 対策

最初は Plan モードから一度抜ける以外に方法がなさそうだと思っていましたが、実は Plan モードが作る md ファイルは、裏側では Write / Edit ツールが `/Users/you/.claude/plans/xxxxx.md` へ書き込む形で作られていました。

そこで `PostToolUse` hook を使い、`plans/xxxxx.md` への書き込みを検知して headless の `claude -p` に変換させる方法で対処しました。  
hook が起動するのは別プロセス（別セッション）なので、Plan モードの「ファイルを作成できない」制約にはひっかかりません。  
`~/.claude/settings.json` への登録は次のとおりです（`matcher` で `Write|Edit` に反応させ、変換の同期実行に備えて `timeout` を延ばしておきます）。

```
"PostToolUse": [
  {
    "matcher": "Write|Edit",
    "hooks": [
      { "type": "command",
        "command": "/Users/you/.claude/hooks/plan-html-render.sh",
        "timeout": 240,
        "statusMessage": "plan HTML 生成中..." }
    ]
  }
]
```

hook スクリプト本体は折りたたみに載せます。  
Claude には「確定したら `<!-- render -->` を末尾に書け」とだけ教えておき（この指示は 1 章の hook に入れてあります）、hook はマーカーがあるときだけ動きます。

plan-html-render.sh（クリックで展開）

```
#!/bin/bash
# ~/.claude/hooks/plan-html-render.sh
# PostToolUse hook (Write|Edit): Plan モード中に ~/.claude/plans/ の plan md へ
# 確定マーカー <!-- render --> が書かれたら、claude -p で確認用 HTML を同期生成する
input=$(cat)
mode=$(printf '%s' "$input" | jq -r '.permission_mode // empty')
[ "$mode" = "plan" ] || exit 0

file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')
case "$file" in
  /Users/you/.claude/plans/*.md) ;;
  *) exit 0 ;;
esac
[ -f "$file" ] || exit 0
grep -q '<!-- render -->' "$file" || exit 0

# ~/.claude/ 配下は設定ディレクトリ保護で headless の Write が機械的にブロックされるため外に置く
html_dir="/Users/you/plan-html"
mkdir -p "$html_dir"
base=$(basename "$file" .md)
html="$html_dir/$base.html"

prompt="次のプラン md を、レビュー用の self-contained HTML に変換してください。この HTML は Claude Artifact として公開するページなので、Artifact のデザインガイダンス（design fundamentals）に従い、プラン内容は図解を交えて視覚化すること。
入力: $file を Read する（末尾のマーカー行 <!-- render --> は出力に含めない）。
出力: $html に Write する。
要件:
- DOCTYPE / html / head / body タグは書かない。<title> と <style> とコンテンツを直接書く。
- 外部リソース（CDN・外部フォント・外部画像）は一切使わない。インライン CSS / SVG のみ。
- 色は :root の CSS カスタムプロパティで定義し、prefers-color-scheme と :root[data-theme=\"dark\"] / :root[data-theme=\"light\"] の両方に対応してライト/ダーク両テーマで読めるようにする。
- 手順・フロー・構成・スケジュールなど、順序や関係が本質の内容は図（CSS ステップフロー / インライン SVG のボックス＋矢印 / CSS ガント）で視覚化する。比較・列挙は表にする。装飾目的の図は作らない。
- 見出し階層・余白・タイポグラフィを整え、日本語で読みやすくする。横に広い要素は overflow-x: auto のコンテナに入れる。
Artifact としての公開はメインセッションが行う。あなたはファイルを Write するだけで、公開はしないこと。
変換して Write したら done とだけ出力して終了すること。"

if claude -p "$prompt" --model sonnet --allowedTools "Read,Write" --disallowedTools "Artifact" > /dev/null 2>&1 && [ -f "$html" ] && [ "$html" -nt "$file" ]; then
  ctx="plan の確認用 HTML を自動生成した: $html
(1) Artifact ツールで $html を公開し、その URL を Bash の「open <URL>」でブラウザで開いてから ExitPlanMode に進む。AskUserQuestion での確認は挟まない（承認/修正はユーザーが ExitPlanMode のダイアログで行う。同じパスで再公開すれば URL は維持される。再公開時はブラウザ側のリロードで反映されるため open し直さなくてよい）
(2) reject で修正指示が返ってきたら plan md を修正する。マーカー <!-- render --> は残し、修正はできるだけ1回の Edit にまとめる（Edit のたびに再変換が走るため）
(3) Artifact は所有者のみ閲覧できる非公開のまま扱うこと。共有リンクの発行・public 公開・第三者への共有設定は、ツールの仕様上可能であっても一切行わない"
else
  ctx="plan HTML の自動生成に失敗した（$html が更新されていない）。ユーザーにその旨を伝え、plan md をそのまま Artifact ツールで公開して確認を取ること（Artifact は非公開のまま扱い、共有リンクの発行や public 公開はしない）。"
fi
jq -n --arg ctx "$ctx" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
```

マーキングにより、plan md が編集されるたびに毎回変換が走らないように作り込んでいます。  
マーキング後の書き込みで hook が走り、stdin の情報から Plan モードの Claude Code が Write / Edit したファイルを特定し、マーカーをチェックして、イベント駆動で `claude -p` を実行します。

> `claude -p` に渡すプロンプト（`$prompt`）は、headless セッション側で Skill の description が発火するように書いてください。ただし built-in の `artifact-design` は、headless セッションにはスキル一覧として提示されないため、キーワードを工夫しても発火しません（仕様か不具合かは未確認）。図解の意図やデザイン原則まで組み込みたい場合は、自作 Skill を用意してください（本記事では `plan-artifact` という自作 Skill に、図の使い分け基準・カラートークン・インライン CSS / SVG の実装パターンといった artifact-design の要点ごと持たせています）。

## 3. Claude Artifact として公開する

HTML に変換したら、hook スクリプトの最終行（次の 1 行）が、結果を Plan モード側のメインセッションに返します。ここから Plan 側がタスクを引き継ぎます。

```
jq -n --arg ctx "$ctx" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
```

タスクを引き継ぐと、Claude Artifacts（ブラウザ）が開きます。

![plan を図解した HTML が Claude Artifact としてブラウザで開かれた画面](https://static.zenn.studio/user-upload/deployed-images/628b43e63a4249ed942b4377.png?sha=a48eecd7098d03a21aa844fd4259ef6b521d52b7)

> Artifact の URL を `open` で自動的に開くには allow ルールが要ります。Plan モード中の Bash は権限プロンプトの対象なので、`permissions.allow` に `"Bash(open https://claude.ai/*)"` を足しておかないと、開くたびに承認を求められます。

ターミナル側は普段と何も変わらず、マークダウンが出力され、`ExitPlanMode` が呼ばれます。

![ターミナル側では通常どおり plan のマークダウンと ExitPlanMode の承認ダイアログが表示される](https://static.zenn.studio/user-upload/deployed-images/c7477b5729062adaaf1fa4c3.png?sha=db35349780ff702d342ab3355658a9e0d0aadaf1)

## まとめ

以下の 3 つを組み込んだことで、結構楽になるんじゃないかと思っています。

1. Plan モードの初回プロンプト以降のタイピング負荷を `AskUserQuestion` で落とす
2. 作業効率化を自動的なオーケストレーションで実現する。同時にセッション context の汚れを防止し、トークン使用量を削減する
3. Plan の出力を視覚的な HTML にレンダリングしてブラウザで確認する
