---
id: "2026-07-16-claude-codeのskillをskillでレビューする-静的チェックllmレビューgit-ho-01"
title: "Claude Codeのskillをskillでレビューする ― 静的チェック×LLMレビュー×git hooksの3層ゲート"
url: "https://zenn.dev/aldagram_tech/articles/c407ae672c9c0e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

こんにちは！アルダグラムでQAエンジニアをしている千葉です。

私たちのQAチームでは、テスト分析からテスト設計までのQAプロセスをClaude Codeの[skill（スキル）](https://code.claude.com/docs/en/skills)として整備し、チームで共同運用しています。  
その中心が、これらのQAプロセスを丸ごと任せられるAIエージェント「qa-orchestrator」です。  
仕組みと効果は、弊社QAメンバーが記事にしていますのでそちらもご参考ください。

<https://zenn.dev/aldagram_tech/articles/4aea4b13671ae3>  
今ではqa-orchestratorの存在を前提に、[固定制インプロセスQAからプール制QAへの体制再設計](https://zenn.dev/aldagram_tech/articles/e3f8d39f6eb5a1)も実現していて、skillは「あると便利なツール」を超えてQA体制を支えるインフラになっています。  
使ってみると効果が大きく、テスト設計まわりにとどまらず周辺業務も含めて次々にskill化が進みました。  
その結果skillの数が増え、複数人が日常的に改修するようになると、今度は **skill自体の品質をどう保つか** という問題が出てきました。

この記事では、その解決策として作った「skillをレビューするskill」と、それをチームに強制するgit hooksの仕組みを紹介します。

静的チェック×LLMレビュー×pre-pushゲートの3層でskillの品質を守る、という構成です。

# 課題：skillは放っておくと劣化する

Anthropicは [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) という公式ドキュメントと、より実践的なガイド [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)（PDF）を出しています。  
「descriptionにはwhatとwhenの両方を書く」「SKILL.mdは500行以下に保ち、詳細はreferencesへ分離する」「時間依存の表現を書かない」といった実践的な内容で、この記事で紹介するレビュー観点もこの2つをベースにしています。

問題は、**これを読んだだけでは守れない**ことです。  
実際にチームでskillを運用していると、こんな劣化が起きます。

* 改修を重ねるうちにSKILL.mdが肥大化していく（詳細手順やテンプレート全文が本体に直書きされる）
* referencesのファイルをリネームしたのに、SKILL.md内のリンクが古いまま（参照切れ）
* descriptionに「何をするか」しか書かれておらず、「いつ使うか」が無い。skillが自動起動しない
* 「テストケース」「テスト項目」「ケース」のような表記ゆれが混在し、LLMの解釈がブレる
* 「2026年7月以降は〜」「最近の変更で〜」のような、時間が経つと意味が変わる・古くなる表現が紛れ込む

人間のコードと同じで、レビューなしの変更は積み重なると壊れます。  
しかもskillの「バグ」はテストで落ちない——LLMの挙動が微妙に悪くなるだけなので、気づきにくいのです。  
さらにskillは自然言語の指示書なので、コードのように共通化・変数化してまとめることが難しく、1回の改修で修正箇所が多くなりがちという事情もあります。

かといって人間が毎回ベストプラクティス全文と突き合わせてレビューするのは現実的ではありません。  
観点も属人化します。  
「AIエージェント向けの手順書を書く」話は最近増えてきましたが（AWSのStrands Agentsチームが公開している[Agent SOP](https://github.com/strands-agents/agent-sop)には、検証込みの公式オーサリングスキルが用意されていたりとか）、**Claude Codeのskillには、記述内容をチェックしてくれる公式のvalidatorやlinterが執筆時点では見当たりません**。  
無いなら作ろう、ということで、レビュー自体を自動化・仕組み化しました。

# 全体像：3層ゲート

![skill品質ゲートの全体像](https://static.zenn.studio/user-upload/a101ff5c86e6-20260710.png)

ポイントは役割分担です。

| 層 | 実行タイミング | 担当 | 判定 |
| --- | --- | --- | --- |
| 静的チェック（S01〜S10） | pre-commit | Pythonスクリプト | 決定的（機械判定） |
| LLMレビュー（L01〜L11） | `/skill-review` 実行時 | サブエージェント | 文脈依存（LLM判定） |
| レビュー完了ゲート | pre-push | シェルスクリプト | 決定的（marker照合） |

設計方針は次の3つです。

* 機械で判定できるものはLLMに聞かない（静的チェック）
* LLMにしか判定できないものだけをLLMに任せる（LLMレビュー）
* 「レビューを通したか」自体はgitの仕組みで強制する（pre-pushゲート）

# 第1層：静的チェック（S01〜S10）

pre-commit hookから呼ばれるPythonスクリプトです。  
標準ライブラリのみで動くようにして、依存インストールなしでチームメンバー全員の環境で動くようにしています。

チェック観点はこの10個です。

| ID | 内容 | severity |
| --- | --- | --- |
| S01 | frontmatter `name` が小文字+数字+ハイフン、64文字以内 | error |
| S02 | `name` にreserved word（anthropic/claude）を含まない | error |
| S03 | `description` が1024文字以内・空でない | error |
| S04 | SKILL.md本文が500行以下 | warn |
| S05 | 参照パスがSKILL.mdから1階層以内 | warn |
| S06 | Windowsパス区切り（`\`）が含まれない | error |
| S07 | references/配下の`.md`が全てSKILL.mdから参照されている | warn |
| S08 | SKILL.md内のリンク先ファイルが実在する | error |
| S09 | 参照に`..`（親方向traversal）を含まない | warn |
| S10 | バッククォート内の`.md`パス記述が実在する | warn |

S07（未参照ファイル検知）とS10（バッククォート内のパスtypo検知）は、リネーム時の「参照の直し忘れ」を拾うための観点です。  
リンク記法（`[text](path)`）だけでなく、`references/foo.md` のようにバッククォートで囲んだパス記述もチェック対象にしているのがミソです。  
skillの本文では、リンク記法よりこちらの書き方が意外と多いからです。

pre-commitでは **error級のみcommitをブロック** します。  
warn/infoはcommit自体を止めませんが警告として表示されるので、直すかどうかをその場で判断できます（Claude Codeにcommitさせている場合は、AIが警告を拾って修正するか確認してきます）。  
warnでも止める設計にするとチームが `--no-verify` を常用するようになり、ゲート自体が形骸化する——そう考えて、ブロックはerror級に絞りました。

# 第2層：LLMレビュー（L01〜L11）

静的チェックでは判定できない「文脈を読まないとわからない観点」は、LLMにレビューさせます。  
観点は公式ベストプラクティス由来のものに、運用の中で課題を感じて独自に追加したものを足して、11個に整理しました（表の「出典」列を参照）。

| ID | 観点 | severity | 出典 |
| --- | --- | --- | --- |
| L01 | descriptionにwhat（何をするか）とwhen（いつ使うか）の両方があるか | warn | 公式 |
| L02 | descriptionが3人称か（"I can..." になっていないか） | warn | 公式 |
| L03 | 命名が動詞形か（`helper` `utils` 等の汎用名詞でないか） | info | 公式 |
| L04 | Progressive Disclosure：詳細がreferencesに分離されているか | warn | 公式＋独自拡張 |
| L05 | 用語統一（同一概念への表記ゆれ） | warn | 公式 |
| L06 | 時間依存表現（「今後」「2026年7月以降」等）が無いか | warn | 公式 |
| L07 | 選択肢過剰／デフォルト明示（推奨を1つ示しているか） | info | 公式 |
| L08 | 同梱スクリプトの品質（エラーをClaudeに丸投げしていないか等） | warn | 公式 |
| L09 | 配置整合性（CLAUDE.md／SKILL.md／referencesの置き場所が適切か） | warn | 独自 |
| L10 | 重複ルールのDRY戦略整合性 | info | 独自 |
| L11 | 冗長性：Claudeが既に知っている一般論や導出可能な情報を書いていないか | warn | 公式の"Concise is key"を独自拡張 |

L09〜L11のような独自観点は、公式ベストプラクティスにない・書かれている以上の内容です。  
運用しているうちに「配置場所がバラバラで探しにくい」「同じルールがあちこちに書かれて改修が大変」といった課題を感じて追加しました。

## レビュアーは「読み取り専用のサブエージェント」にする

LLMレビューは、メインの会話ではなく専用のサブエージェント（agent定義）に任せています。  
frontmatterはこうです。

```
---
name: skill-reviewer
description: >-
  指定されたskill関連ファイル群をAnthropic公式skill authoring best practicesに
  照らしてレビューする読み取り専用エージェント。指摘箇所と修正diffを含む
  構造化JSONを返却する。skill-reviewスキルからのみspawnされる。
disable-model-invocation: true
tools: Read, Glob, Grep
---
```

設計判断は3つあります。

**1. ツールをRead/Glob/Grepに制限する。**  
レビュアーには修正させません。  
「見つけたついでに直しました」をエージェントに許すと、人間が確認しないまま変更が入ります。  
修正は後述の対話フェーズで、指摘1件ずつ人間が承認してから行います。

**2. `disable-model-invocation: true` で自動起動を止める。**  
このエージェントはskill-review skillからのみspawnされる部品なので、会話の文脈から勝手に起動してほしくありません。

**3. コンテキストを分離する。**  
skillを改修した本人（のセッション）にそのままレビューさせると、改修時の思い込みごと素通しになります。  
まっさらなコンテキストのサブエージェントに、対象ファイルと観点だけを渡してレビューさせることで、フレッシュな目を確保しています。

## 指摘には「原因」と「再発防止ルール」を必ず付けさせる

レビュー結果の各指摘には、修正案(suggestion)やdiffに加えて、次の2フィールドを必須にしています。

* **cause**：なぜこの問題が発生したか（例：テンプレ流用時の置換漏れ／参照ガイド未読／似た既存skillの慣習に流された）
* **general\_rule**：同じパターンの再発を防ぐ汎用ルール候補（既存観点で拾えるなら観点ID、拾えないなら新規ルール案）

個別の指摘を潰して終わりにせず、「観点表そのものを改訂する」ループを回すためです。  
レビューの成果物が「修正」だけでなく「次のレビュー基準」になる、という点はQAプロセスの考え方そのままです。

## 自己言及問題：観点定義ファイルはレビュー対象から除外する

面白い（面倒な）問題がひとつあります。  
観点L01〜L11を定義したドキュメント自体が、検出基準の説明として **意図的に違反例を含んでいる** のです。  
「悪い例：`I can help you...`」のような記述ですね。

これを機械的にレビューすると、違反例の引用を違反として検出する誤検出が起きます。  
skillをskillでレビューする以上、どこかで自己言及のループを断ち切る必要があり、観点定義ファイル群は明示的にL評価の対象外としています。

# 第3層：pre-pushのレビュー完了ゲート

静的チェックとLLMレビューを用意しても、**実行されなければ意味がありません**。  
そこで「レビューを通していないskill変更はpushできない」ゲートをpre-push hookで作りました。

仕組みは単純で、`/skill-review` が完了するたびにレビュー済みのHEADハッシュをmarkerファイル（`last-reviewed-head`）に記録し、pre-push時に「markerから push対象までの差分」にskill関連の `.md` が含まれていたらブロックします。

```
# pre-push.sh（抜粋・簡略化）
while IFS=' ' read -r local_ref local_sha remote_ref remote_sha; do
    # base決定: リモート既知ならremote_sha、レビュー済みHEADが
    # その範囲内ならさらに絞り込み、どちらも無ければ空ツリー
    ...
    changed=$(git diff "${base}..${local_sha}" --name-only \
        | grep -E '^\.claude/(skills|agents)/.+\.md$' || true)
done
```

ブロック時にはこんな案内を出します。

```
[skill-review] 未レビューの skill 変更があります:
  - .claude/skills/foo/SKILL.md

push 前に以下のいずれかを実行してください:
  1. /skill-review を実行してレビューを完了する（推奨）
  2. 明示的スキップ: SKIP_SKILL_REVIEW=1 git push
  3. hook全体をバイパス: git push --no-verify
```

比較のbase（どこからの差分を「未レビュー」とみなすか）の決定は、pushの状況によって次のように分岐させています。

![baseの決定フロー](https://static.zenn.studio/user-upload/eef186bd13ca-20260710.png)

## ハマりどころ：markerを更新するタイミング

このmarker方式には罠が1つありました。  
レビューで指摘を1件でも適用すると、修正はworking treeに入ります（未コミット）。  
このタイミングでmarkerを現HEADに更新してしまうと、**ユーザーが修正をコミットした瞬間にHEADが進み、そのレビュー済みの修正が次回pushで「未レビュー変更」として誤検出される** のです。

そのため、適用1件以上の場合は次の2択をユーザーに確認します。

* **skill内でそのままコミットする（推奨）**：コミット後の新HEADをmarkerに記録。次のpushはそのまま通る
* **あとで手動コミットする**：markerは更新しない。コミット後に再度 `/skill-review` を空実行するか手動でmarkerを更新してもらう（案内を表示）

「レビュー済み」という状態をgitのどの時点に紐付けるか、は単純そうで意外と落とし穴があります。

## 逃げ道は必ず用意する

ゲートには必ず明示的なスキップ手段を付けています（`SKIP_SKILL_REVIEW=1` と `--no-verify`）。  
緊急時に迂回できないゲートは、チームに嫌われて無効化されて終わりです。  
「原則ブロック、ただし意図的なスキップは1コマンドでできて、それがログ（コマンド履歴）に残る」くらいのバランスが運用として現実的でした。

# おまけ：git hooksのdispatcherパターン

hookの置き方にも1つ工夫があります。  
gitの `core.hooksPath` は **1ディレクトリしか指定できない** ため、素朴に作ると「skill-review用のpre-push」と「将来の別チェック用のpre-push」が衝突します。

そこでtop-levelのhookは「配下のチェック種類ごとのサブディレクトリを順に呼ぶだけ」のdispatcherにしました。

```
.claude/hooks/
├── pre-commit                  # dispatcher: */pre-commit.sh を順に実行
├── pre-push                    # dispatcher: */pre-push.sh を順に実行
└── skill-review/
    ├── pre-commit.sh           # 静的チェック実体
    └── pre-push.sh             # レビュー完了ゲート実体
```

新しいチェックを足したいときはディレクトリを追加するだけで、既存ファイルの編集は不要です。

# 運用してみて

* **レビューの観点が属人化しなくなりました。** 「なんとなく読みにくい」ではなく、S01〜S10／L01〜L11のどれに該当するかで会話できます
* **指摘のcause／general\_ruleから観点表が育ちます。** レビューで見つかった新パターンが次回から静的チェックやLLM観点に昇格する、という改善ループが回っています
* **誤検出の抑制は明示的に指示が必要でした。** LLMレビュアーには「確実に該当する場合のみ報告、迷ったらseverityをinfoに下げる」「観点ID外の指摘は出さない」を厳守事項にしています。放っておくとLLMは「気になる点」を無限に出してきて、ノイズでゲートが嫌われる原因になります

# まとめ

* Claude Codeのskillには公式validatorが見当たらないので、静的チェック（S01〜S10）＋LLMレビュー（L01〜L11）＋git hooksの3層ゲートを自作した
* 機械で判定できるものはLLMに聞かない。LLMにしか判定できないものだけを、読み取り専用・コンテキスト分離のサブエージェントに任せる
* ゲートは「原則ブロック＋明示的な逃げ道」のバランスが大事。逃げ道の無いゲートは無効化されて終わる
* 指摘に原因と再発防止ルールを付けさせると、レビュー基準自体が育っていく

skillは「AIへの指示書」であると同時に、チームで保守するコード資産でもあります。  
コードにlintとレビューとCIがあるように、skillにも同じ品質ゲートを——という話でした。  
ご参考になれば幸いです。
