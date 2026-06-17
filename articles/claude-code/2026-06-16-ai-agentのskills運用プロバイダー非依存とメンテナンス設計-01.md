---
id: "2026-06-16-ai-agentのskills運用プロバイダー非依存とメンテナンス設計-01"
title: "AI Agentのskills運用：プロバイダー非依存とメンテナンス設計"
url: "https://zenn.dev/salt2/articles/a618f381e058bb"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "Gemini", "Python", "zenn"]
date_published: "2026-06-16"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

AI Agentの `Skills` は業務を再利用する仕組みで、定型業務自動化などに特に便利です。  
（今までは、Difyなどでワークフローを組んでいたものを自然言語で自動化できるなど）

一方で、実際に運用し始めるとすぐに別の問題が出ます。Codex、Claude Code、Gemini CLI、Cursorでは、Skillsの置き場所、読み込み方、発動方法、補助ファイルの扱いが少しずつ違います。Providerごとの仕様に合わせて個別に管理すると、Skillを更新するたびに同期漏れ、古い手順の残存、triggerの誤発火が起きやすくなります。

この記事の主題は、Providerの優劣比較ではありません。Skillsを継続運用するために、正本、同期メカニズム、メンテナンス、PDCAをどう扱うのかについてです。私の運用を一例にしていますが、唯一の正解として提示するものではありません。各チーム,個人が業務に合わせて調整するのが大切です。

本稿では、Provider別の形式に変換する層を便宜上 `adapter` と呼びます。`Skills Maintenance`、`Subagent Maintenance`、`Core Rule Maintenance` も、本稿上の設計用語です。

## 目次

1. Skills運用で起きる問題
2. 同期メカニズム：`.agents/skills` を正本にする
3. Codexで変更したSkillを他環境へ反映する流れ
4. Provider別の同期・参照方法
5. メンテナンス設計：3つのメンテナンスを分ける
6. Skills Maintenanceで行うこと
7. Subagent Maintenanceで行うこと
8. Core Rule Maintenanceで行うこと
9. SkillsのPDCAサイクル
10. 今後のSkills運用：粒度と目的で書き方は変わる
11. まとめ：Skillsは設定ではなく運用資産
12. Appendix：組織でSkillsを運用する場合

## 1. Skills運用で起きる問題

Skillsは、Providerごとに同じ形で扱えるわけではありません。Codexはリポジトリ階層の `.agents/skills` を読みます。Claude CodeのProject Skillは `.claude/skills/<skill-name>/SKILL.md` に置きます。Gemini CLIは `.gemini/skills` と `.agents/skills` の両方を扱い、Cursorも `.agents/skills` と `.cursor/skills` を読みます。

この差分は小さく見えますが、運用では効いてきます。たとえば同じSkillをProvider別フォルダにコピーして管理すると、片方だけ古いテンプレートが残ります。triggerだけ直して本文が古い、補助資料だけ更新されて検証スクリプトが古い、subagent定義だけProvider固有形式に残る、といったズレも起きます。

私の運用では、このズレを避けるために、Providerごとの配置ルールをそのまま運用ルールにしない方針にしています。業務知識の正本は一箇所に置き、Provider差分は同期層や互換パスに逃がします。

問題はProvider差分そのものではありません。業務知識、テンプレート、評価基準、検証手順がProvider固有層に散らばることです。散った瞬間に、SkillsのPDCAは回りにくくなります。

## 2. 同期メカニズム：`.agents/skills` を正本にする

私の運用では、Skillsの編集対象を `.agents/skills/<skill-name>/SKILL.md` に寄せています。各Skillの標準構成は次の形です。

```
.agents/skills/<skill-name>/
├── SKILL.md
├── assets/
├── references/
├── evolution/
├── scripts/
└── agents/
```

`SKILL.md` には、Skillの目的、発動条件、対象外、実行手順を書きます。出力テンプレートは `assets/`、必要時だけ読む詳細資料は `references/`、評価基準や品質ゲートは `evolution/`、決定的に実行したい処理や検証処理は `scripts/` に置きます。

この構成にすると、Skill本文に全てを書き込む必要がなくなります。モデルに読ませたい内容は `SKILL.md` に残し、長い資料やテンプレートは別ファイルに逃がします。検証できる部分はPythonなどのスクリプトに落とします。

同期の全体像は次の通りです。

ここで守るべきことは、generated fileを正本にしないことです。`.claude`、`.codex`、`.gemini` は実行用の読み込み層です。編集したい内容は `.agents/skills`、subagentなら `ai/agents/*.yaml`、共通ルールなら `AGENTS.md` に戻します。

## 3. Codexで変更したSkillを他環境へ反映する流れ

CodexでSkillを変更する場合も、編集対象は `.agents/skills` の正本に限定します。Codex上で作業しているからといって、`.codex` 配下をSkill本文の正本にしません。

私の運用では、Claude Code向けの `.claude/skills/<skill-name>` を `.agents/skills/<skill-name>` へのsymlinkとして扱っています。Claude Codeの公式DocsではProject Skillの配置は `.claude/skills/<skill-name>/SKILL.md` ですが、symlinkを使えば、実体は `.agents/skills` に置いたままClaude Codeから読めます。Claude CodeはSkillディレクトリの変更を監視するため、`SKILL.md` の変更は現在のセッションにも反映されやすいです。

CodexとGemini CLIについては、hooks、settings、subagent adapterなどの生成物があります。私の運用では `ai/scripts/sync_adapters.py` が、`.codex/agents/*.toml`、`.gemini/agents/*.md`、hook wrapper、settings類を生成・同期します。同期後はdriftが残っていないかを確認します。

Cursorは、公式Docs上で `.agents/skills` と `.cursor/skills` の両方を読みます。現状では `.agents/skills` を共通正本として使えます。チーム運用上、Cursor専用の見え方やスコープを分けたい場合は、`.cursor/skills` へcopy、symlink、生成する選択肢もあります。

この流れは「Codexで変更すると完全自動で全環境へ同期される」という話ではありません。実態は、正本、symlink、互換パス、生成スクリプトを分けた運用です。どこが即時反映で、どこが生成対象で、どこが互換パスとして読まれるのかを分けておくと、ズレたときの修正箇所が見えます。

## 4. メンテナンス設計：3つのメンテナンスを分ける

私の運用では、AI Agent運用のメンテナンスを大きく3つに分けています。

1. `Skills Maintenance`
2. `Subagent Maintenance`
3. `Core Rule Maintenance`

これは役割の分離です。Skill本文の更新、subagent定義の更新、AGENTS.mdやhooks/settingsの更新を同じ作業として扱うと、どこを正本にすべきかが曖昧になります。

Skillだけを直しても、関連するsubagentや共通ルールが古いままだと運用は壊れます。逆にAGENTS.mdだけに細かい手順を書き込むと、常時読む入口が肥大化します。対象ごとにメンテナンスの入口を分けることで、編集範囲と検証範囲を絞れます。

## 5. Skills Maintenanceで行うこと

`Skills Maintenance` は、`.agents/skills` 配下のSkillを作成、更新、統合、削除するための運用です。

主な作業は、Skillの標準構成を守ることです。`SKILL.md` に全てを詰め込まず、テンプレートは `assets/`、詳細資料は `references/`、評価基準は `evolution/`、決定的処理や検証処理は `scripts/` に置きます。

実務上は、新規Skillを作るよりも、既存Skillに吸収する判断の方が難しくなります。似たSkillが増えると、どれが正本か分からなくなります。triggerが増えすぎると、意図しない場面でSkill候補が出ます。使われなくなったSkillを残すと、古い手順が再び読まれます。

`Skills Maintenance` で見る作業は次の通りです。

| 作業 | 見るもの |
| --- | --- |
| 新規作成 | 名前、用途、対象外、出力契約、標準ディレクトリ構成 |
| 更新 | 本文、template、references、評価基準、scripts |
| 統合 | 似たSkillを1つに寄せられるか |
| 削除・凍結 | 使われていないSkillや古い手順を残していないか |
| trigger整理 | 自然発火させるか、明示実行に寄せるか |
| 検証 | frontmatter、ディレクトリ構成、adapter drift |

ここでいう検証はProvider公式の共通機能ではありません。多くは `scripts/` や `ai/scripts/` に置くPythonなどのスクリプトです。たとえば `SKILL.md` のfrontmatter、標準ディレクトリ、テンプレート準拠、生成物との差分を機械的に見ます。

## 6. Subagent Maintenanceで行うこと

`Subagent Maintenance` は、subagentの共通定義を保守するための運用です。私の運用では `ai/agents/*.yaml` を正本にし、Claude / Codex / Gemini向けのagent定義を生成します。

subagentはProviderごとに形式が違います。Claude CodeはMarkdown frontmatter、CodexはTOML、Gemini CLIは別形式のMarkdownを扱うため、どれか1つのProvider形式を正本にすると、他Providerへコピーしたときに崩れます。

そこで、共通定義には次のような情報を置きます。

| 項目 | 役割 |
| --- | --- |
| `name` | agent名 |
| `description` | いつ使うagentか |
| `source_skill` | どのSkillに紐づくか |
| `tools` | 必要なツール範囲 |
| `instructions` | 役割、入力、出力、禁止事項 |

この正本から、各Provider向けのadapterを生成します。生成物の先頭に `GENERATED FROM ai/agents - DO NOT EDIT DIRECTLY.` のような注記を入れておけば、どのファイルを直接編集してはいけないかが明確になります。

## 7. Core Rule Maintenanceで行うこと

`Core Rule Maintenance` は、共通ルールと入口ファイルを保守するための運用です。

私の運用では `AGENTS.md` を共通ルール正本にし、`CLAUDE.md` と `GEMINI.md` は `AGENTS.md` へのsymlinkとして維持します。`.claude`、`.codex`、`.gemini` のgenerated adapterは直接編集しません。

ここで扱うのは、詳細な業務手順ではありません。常時読む入口に置くのは、正本パス、adapterパス、同期手順、検証コマンド、禁止事項のような共通ルールだけです。詳細な業務手順は各Skillへ、subagentの役割は `ai/agents/*.yaml` へ逃がします。

`Core Rule Maintenance` で見る作業は次の通りです。

| 作業 | 見るもの |
| --- | --- |
| 入口維持 | `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` の関係 |
| 共通ルール更新 | AI Agent運用全体の禁止事項、正本パス、検証コマンド |
| adapter整合 | `.claude`、`.codex`、`.gemini` の生成物が正本とズレていないか |
| hook整合 | Skill候補提示やtrigger注入の経路が壊れていないか |
| 一覧更新 | Skillやsubagentを追加したときに説明が古くないか |

AGENTS.mdに全てを書けば一見わかりやすくなります。ただし、入口ファイルが肥大化すると、Agentは毎回大量の文脈を読むことになります。共通ルールは薄く保ち、詳細はSkillとsubagentに寄せる方が、長期運用では扱いやすくなります。

## 8. SkillsのPDCAサイクル

Skills運用は、作成よりも更新の方が長く続きます。実務で一度使うと、出力がズレる、テンプレート違反が出る、triggerが反応しすぎる、別Providerでは読み方が違う、といった改善点が見つかります。

そのたびに会話内で注意するだけでは、同じ失敗が残ります。失敗はSkill本文、テンプレート、評価基準、script、triggerへ戻します。

PDCAを実務に落とすと、次の流れになります。

| フェーズ | やること | 戻す場所 |
| --- | --- | --- |
| Plan | Skillの目的、対象外、出力契約を決める | `SKILL.md` |
| Do | 実務で使う | 実タスクの成果物 |
| Check | 出力のズレ、使いにくさ、trigger誤発火を確認する | レビュー結果、失敗ログ |
| Act | 本文、template、評価基準、scriptを直す | `SKILL.md`、`assets/`、`evolution/`、`scripts/` |
| Sync | adapterを生成し、driftを確認する | `sync_adapters.py`、検証スクリプト |
| Maintain | 統合、削除、明示実行専用化を判断する | `Skills Maintenance` |

たとえば議事録SkillでNext Actionの表が毎回崩れるなら、プロンプトで毎回注意するより、テンプレートと検証スクリプトに落とします。提案書レビューで内部向け文言が混ざるなら、禁止事項をSkill本文に入れるだけでなく、検出できる表現はscript側にも寄せます。

この循環がないと、Skillsは増えるほど扱いづらくなります。Skillを増やす力と同じくらい、統合、削除、明示実行専用化を判断する力が必要です。

## 9. 今後のSkills運用：粒度と目的で書き方は変わる

モデル性能が上がるほど、Skillに何を書くべきかも変わります。

以前は、手順を細かく書くほど安定する場面が多くありました。今後は、強いモデルに細かすぎる手順を渡すことで、かえって柔軟な判断を潰す場面も増えます。反対に、保存先、禁止事項、品質基準、テンプレート、検証条件は、モデル性能が上がっても曖昧にしない方がよい領域です。

Skillの粒度は、目的で変えます。

| 目的 | 記載粒度 | 書くもの | 避けること |
| --- | --- | --- | --- |
| アイデア発散 | 抽象度高め | 目的、制約、観点、評価軸、避けたい方向 | 手順を固定しすぎる |
| 調査・レビュー | 中間 | 比較軸、出典ルール、評価基準、出力形式 | 事実確認を曖昧にする |
| 定型業務 | 具体度高め | 保存先、手順、テンプレート、禁止事項、検証条件 | モデル任せにしすぎる |
| 品質保証 | 非常に具体的 | NG例、検証スクリプト、再実行条件、品質ゲート | 評価を感覚に寄せる |

アイデア発散用のSkillなら、細かな手順よりも、問いの立て方、制約、評価軸を渡す方が使いやすくなります。定型業務の自動化なら、保存先、上書き禁止、テンプレート、検証条件まで具体的に書きます。

Skillは、常に詳しく書けばよいものではありません。モデルに委ねる部分と、運用上固定する部分を分ける必要があります。今後のSkills運用では、この粒度調整がさらに重要になります。

## 10. まとめ：Skillsは設定ではなく運用資産

Skills運用は、Provider仕様を覚える作業ではありません。  
複数環境で壊れにくい形に保ち、しっかりと業務効果が出ることが最重要です。

Providerごとの差分を消すことはできません。できるのは、差分を正本に混ぜず、adapter、symlink、互換パス、生成スクリプトに逃がすことです。そのうえで、`Skills Maintenance`、`Subagent Maintenance`、`Core Rule Maintenance` を分け、作成、更新、検証、同期、棚卸しを回します。

Skillsは一度作って終わる設定ではありません。実務で失敗し、直し、同期し、整理することで価値が出ます。個々のSkillの巧さだけでなく、同期・メンテナンス・PDCAを回す運用力が、AI Agent活用の土台になります。

SALT2では、AI Agent開発や業務特化型AIプロダクト開発に関心のあるメンバーを募集しています。本稿のような運用設計や実務実装に関心がある方は、[SALT2 Careers](https://salt-2.com/careers) を参照してください。

## 11. Appendix：組織でSkillsを運用する場合

個人が作ったSkillを組織で使う場合、単に共有repoへ置くだけでは足りません。  
誰が作り、誰がレビューし、どのバージョンを使い、問題があったときにどう戻すかを決める必要があります。

組織運用で考える論点は次の通りです。

| 論点 | 見ること |
| --- | --- |
| 権限 | 誰がSkillを作成・更新・削除できるか |
| 承認 | 共有前に誰がレビューするか |
| バージョン管理 | どのSkillがどの業務で使われているか |
| ロールバック | 失敗したSkillをどう戻すか |
| 監査 | いつ誰が何を変えたか |
| 機密情報 | Skill本文やassetsに入れてはいけない情報は何か |
| 配布 | repo、plugin、Managed Agent、team-wide rulesのどれで配るか |

たとえば [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) のようなクラウド実行環境にSkillsを置き、組織のメンバーが共通で使う形も考えられます。その場合、個人のローカルSkillをそのまま上げるのではなく、レビュー済みのSkillだけを共有対象にする方が安全です。

CursorのTeam Rulesは、組織でルールを配布・適用する考え方の参考になります。Vercelの [v0](https://v0.app/docs/) のような生成環境も、チームで生成文脈や再利用資産を持つ方向性の参考になります。ただし、この記事の主題は製品比較ではありません。組織でSkillsを使うなら、便利な共有方法より先に、正本、承認、検証、ロールバックを決める必要があります。
