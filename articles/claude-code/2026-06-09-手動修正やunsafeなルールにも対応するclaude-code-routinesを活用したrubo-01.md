---
id: "2026-06-09-手動修正やunsafeなルールにも対応するclaude-code-routinesを活用したrubo-01"
title: "手動修正やunsafeなルールにも対応する、Claude Code Routinesを活用したRuboCop TODO解消の仕組み"
url: "https://zenn.dev/tsukulink/articles/4057a83ea2217b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

こんにちは、[ツクリンク株式会社](https://tsukulink.co.jp/)でソフトウェアエンジニアをしている[千葉](https://x.com/yoshi_chibaaa)です。

今回は、ツクリンクに溜まったRuboCop TODOを減らすため、Claudeにコード修正からRSpecのデバッグ、PR説明文の作成までを任せる自動化ルーティンを構築しました。

本記事では、その具体的な運用の仕組みについてご紹介します。

## ✅ はじめに

大規模なRailsアプリを運用・開発していく中で、ついつい後回しになりがちなのが「**RuboCop TODOの解消**」です。

いつかやろうと思ってはいるものの、いざ手をつけると「自動修正でコードの意味が変わらないか心配」「テストが落ちたときの原因調査が面倒」「修正箇所が多すぎてどこまで影響が出るか把握しきれない」など、エンジニアの認知負荷が地味に高い作業でもあります。

ツクリンクでは、この「面倒だけど大切な作業」をClaudeを使って効率化する仕組みを作りました。ただコマンドを機械的に叩くだけではなく、コードの修正からRSpecの検証、さらには週次の進捗レポート生成や完了予測までをClaudeが自律的に行い、エンジニアは最後のレビューと手動修正の判断に集中できる「半自動化」のルーティンです。

## ✅ RuboCop / RuboCop TODOとは

![](https://static.zenn.studio/user-upload/2bd5974f19ed-20260604.png)

前提として、[RuboCop](https://rubocop.org/)とはRubyのコードが標準的なスタイルに沿っているかをチェックし、バグの原因になりそうな箇所を検出してくれる静的解析ツールです。

既存の歴史があるプロジェクトに新しくRuboCopを導入したり、新しいルールを追加したりすると、数千件規模の膨大なコード規約違反が一気に検出され、CI（継続的インテグレーション）が落ちてしまうことがあります。これらを1つずつ直していては、本来の機能開発が止まってしまいます。

**そこで活躍するのが`.rubocop_todo.yml`（通称：RuboCop TODO） です。**

これは、「現在出ている既存のエラーを一時的にホワイトリストとして退避させ、CIをパスさせる」ための仕組みです。新しく書くコードには最新の規約を強制しつつ、既存の違反コードは「TODO（いつか直すもの）」としてファイルに封じ込めることができます。

実際のファイルは、以下のように違反している「ルール（Cop）」ごとに、検知をスキップするファイル（除外リスト）や違反件数が記録されたブロックが並ぶ構造になっています。

```
# Offense count: 12
# This cop supports safe autocorrection (--autocorrect).
Style/HashSelect:
  Exclude:
    - 'app/models/user.rb'
    - 'app/controllers/users_controller.rb'
    - 'app/services/user_search_service.rb'
```

しかし、このTODOファイルは意識して計画的に消していかないと、ルールが新しく追加されるたびに行数が増え続け、永遠に終わらない「**技術負債の山**」になってしまうという課題を抱えています。

## ✅ RuboCop Challengerとは

`.rubocop_todo.yml` を自動で少しずつ解消していく定番のツールとして、広く知られているのが[RuboCop Challenger](https://github.com/ryz310/rubocop_challenger)です。

これは定期実行によって、主に以下の作業を自動で行ってくれるライブラリになります。

* `.rubocop_todo.yml` からルールを1つピックアップして削除
* `rubocop --autocorrect` を実行してコードを自動修正
* 修正差分をブランチにコミットし、Pull Requestを作成

RuboCop TODOの解消に非常に強力なツールですが、運用を続ける中でいくつかの「限界」に直面することがあります。

### 1. safeな自動修正しか対応できない

RuboCop Challengerをはじめとする標準的な自動化スクリプトでは、安全に一括置換できるルール（safe autocorrect）のみを対象に実行するのが一般的です。

そのため、`--autocorrect-all` が必要な「unsafe」なルール（コードの挙動や戻り値が変わるリスクがあるもの）や、そもそも自動修正に対応していないルールは、TODOに残されたままになりがちです。

結果として、対応が難しい複雑な警告ほど、いつまでも `.rubocop_todo.yml` の中に残り続けてしまう課題があります。

### 2. CIが落ちたときのリカバリが手動

どれだけ安全なルールであっても、機械的な自動修正によって意図せず既存のテスト（RSpec）が落ちてしまうことがあります。

もしCIが落ちてしまった場合、人間がそのブランチをローカルに持ってきてデバッグするか、あるいは諦めてPRをクローズするしかありません。

この「落ちたテストの原因をわざわざ調べて追加のパッチを当てる」という作業が、地味にエンジニアの手間と時間を奪う原因になります。

### 3. PRの文脈が薄い

機械的に生成されたPRの概要欄はテンプレート通りになりがちなため、具体的な変更の理由や文脈がどうしても薄くなってしまいます。

レビュアーは、複数ファイルに及ぶ差分を上から下まで眺め、「このCopは具体的にどのコードを、どういう意図で変えたのか」を毎回脳内で解析しなければなりません。

これが積み重なると、チーム全体のレビュー負荷が高まり、PRが放置される原因にもなってしまいます。

**こうした定番ツールの限界や運用の手間を考慮し、ツクリンクでは最初からClaude Code Routinesを活用した仕組みを構築・導入することにしました。**

## ✅ Claude Code Routinesとは

![](https://static.zenn.studio/user-upload/d365c8240768-20260605.png)

[Claude Code Routines](https://code.claude.com/docs/ja/routines)とは、Anthropic社が提供するAI agentツール「Claude Code」をベースに、一連の開発タスクを定型ジョブとして自律実行（ルーティン化）させる仕組みです。

従来のCIや自動化スクリプトは、あらかじめ定義されたコマンドを静的に上から順に実行するだけでした。そのため、コマンドがエラーを返せばそこで処理がストップしてしまいます。

一方でClaude Code Routinesは「コンテキストの理解」と「状態に応じた自律的な試行錯誤」を行えるのが特徴です。

プロジェクト全体のコードベースや直前のコマンドの実行結果（エラーログなど）をコンテキストとして自ら読み解き、ターミナル操作、ファイル編集、テスト実行といった一連のアクションを、ゴールに到達するまでエージェントが自律的にループを回して処理します。

## ✅ Claude Code RoutinesによるTODO解消と可視化の仕組み

ツクリンクではこのClaude Code Routinesの自律性を活かし、日々の開発プロセスの中に以下の2つの運用を組み込んでいます。

### 1. RuboCop TODOの解消

1セッションで修正PRを作成するループを回しています。

処理の確実性を担保するため、TODO内のCop（ルール）を以下の3つのTier（優先度）に分類し、先頭から順に処理するよう指示しています。

| 優先度 | 対象となるCopの特徴 | 修正アプローチ |
| --- | --- | --- |
| **Tier 1** | safe autocorrect 対応Cop | `--autocorrect` を実行 |
| **Tier 2** | unsafe autocorrect 対応Cop | `--autocorrect-all` を実行 |
| **Tier 3** | 手動修正が必要なCop（違反数30件以下） | 1件ずつコードを読んで手動修正 |

このルーティンの中では、Claude Codeのコンテキスト理解や推論の強みを活かし、1セッションの中で以下のような判断や修正をClaudeに実行させています。

* 手動修正への対応（Tier 3）  
  自動修正が効かないコードに対し、Claudeがソースコードを読み込んで、意味を変えない範囲でのリファクタリングを1件ずつ試みます。
* RSpecの失敗原因の3分類  
  修正後に変更箇所から影響のあるRSpecを自動推定して実行し、もしテストが落ちた際は、Claudeがスタックトレースとコードを解析して以下の3つに分類して対処します。
  + 修正起因: 修正内容が原因でテストが落ちたと判断した場合、その場で追加の修正パッチを当てて再テストを試みます。
  + flakyテスト: ネットワークや時刻依存など、今回の修正と無関係な失敗と判断した場合、1回だけ再実行して検証します。
  + 環境問題: 依存gemやDB等、セッション内で解決できない問題と判断した場合、安全のためにDraft PRとして作成します。
* PR説明文の生成  
  `git diff` をClaude自らが解析し、「主な変更パターン」の要約や「Before / Afterのスニペット」をPRの概要欄に自動で記述します。

これにより、以下のような人間のレビューコストが最小限で済む状態のPRが作成されます。

![](https://static.zenn.studio/user-upload/512a7630ca68-20260605.png)

Claude Code Routines スクリプト例（一部抜粋）

```
<リポジトリ名> の rubocop 修正 PR を **1セッションで最大5本** 作成してください。Rubocop Challenger gem より一歩進んだ AI 活用型ルーティンです。

## 準拠規約
- コミット: 準拠させたいコミット方式
- PR description: 準拠させたいPR descriptionの記載方式

## 前提
- <リポジトリ名> の master ブランチが checkout 済みで開始
- gh, git, ruby, bundler 利用可能

## ステップ

### 0. 環境準備 (セッション開始時に1回)
```
bundle install --jobs 4 --retry 3
[ -f package-lock.json ] && npm ci --no-audit --no-fund || true
```

### 1. 候補 cop リストの構築 (セッション開始時に1回)

`.rubocop_todo.yml` と open PR タイトル一覧を読み、Tier 1 → 2 → 3 の順に並べた候補リストを作る:
```
open_titles=$(gh pr list --state open --search 'rubocop自動修正 in:title' --json title --jq '.[].title')
```

**Tier 1: safe autocorrect**
- 直前コメントに `# This cop supports safe autocorrection (--autocorrect)`
- `Enabled: false` は除外
- offense count 昇順
- open PR 重複は除外

**Tier 2: unsafe autocorrect**
- 直前コメントに `# This cop supports unsafe autocorrection (--autocorrect-all)`
- `Enabled: false` は除外
- offense count 昇順
- open PR 重複は除外

**Tier 3: 手動修正**
- autocorrect コメントが無い cop または `Enabled: false` の cop
- **offense count ≤ 30 のもののみ**
- offense count 昇順
- open PR 重複は除外

`candidates = [Tier1全部, Tier2全部, Tier3全部]` の順で結合し、先頭から処理。候補リストが空なら「本日は対象なし」と出力して終了。

### 2. 5本 PR 生成ループ

`created_count = 0`、`created_count < 5` かつ候補が空でない間ループ:

1. 候補先頭から1つ取り出す
2. 2a、2g を実行
3. PR 作成成功なら `created_count += 1`
4. 失敗ならそのcopを捨てて次へ。作業ツリーは `git reset --hard origin/master` で破棄
5. RSpec fail で draft PR にした場合も PR 生成されたので `created_count += 1`

#### 2a. ブランチ作成
cop-slug = CopName を小文字化し `/` と `_` を `-` に置換
```
git fetch origin master
git checkout -B "feature/rubocop-<cop-slug>-$(date +%Y%m%d)" origin/master
```

#### 2b. 修正実行
**Tier 1**: `bundle exec rubocop --autocorrect --only <CopName> <files...>`
**Tier 2**: `bundle exec rubocop --autocorrect-all --only <CopName> <files...>`
**Tier 3** (手動):
```
bundle exec rubocop --only <CopName> --format json > /tmp/rubocop_offenses.json
```
JSON をパースし AI が各違反を Read → Edit で 1件ずつ修正。意味が変わらないリファクタに徹する。不安な箇所はスキップ。修正後 `bundle exec rubocop --only <CopName>` で再確認。

差分が空ならこのcopはスキップしてループの次へ。

#### 2c. .rubocop_todo.yml の更新
選んだ cop の `# Offense count: ...` から始まるコメントブロック + cop 定義 (次ブロックの空行手前まで) を削除。

#### 2d. rubocop 再確認
```
bundle exec rubocop --only <CopName>   # 違反ゼロ確認
bundle exec rubocop                    # 他copへの巻き込み回帰が無いこと
```

#### 2e. 関連RSpec 自動実行 + 原因分類+補正 (A2)
`git diff --name-only origin/master..HEAD` で修正 Ruby ファイルを取り、spec を推定:
- `app/models/X.rb` → `spec/models/X_spec.rb`
- `app/controllers/X.rb` → `spec/controllers/X_spec.rb`, `spec/requests/...`
- `app/jobs/X.rb` → `spec/jobs/X_spec.rb`
- `app/services/X.rb` → `spec/services/X_spec.rb`
- `app/decorators|helpers|mailers|policies/X.rb` → 同応ディレクトリ下の `X_spec.rb`
- `lib/X.rb` → `spec/lib/X_spec.rb`
- `packs/<pack>/app/...X.rb` → `packs/<pack>/spec/...X_spec.rb`
- `spec/...` の変更はその spec 自身
- 推定 spec が存在しなければスキップ
```
bundle exec rspec <推定 spec のうち存在するもの>
```

**全 spec を pass なら 2f コミットへ**。fail があれば以下の A2 分類ロジックを実行:

##### A2. fail 原因の3分類と対処

各 fail を AI がコードと stack trace を読んで以下に分類:

**(a) 修正起因** — 失敗箇所が今回の rubocop 修正範囲 (diff のファイル/行) と関連する
- AI が追加パッチを Edit で当て、`bundle exec rspec <該当spec>` で再実行
- pass したら normal PR ルートを続行 (修正パッチは別コミット `fix(spec): adjust <spec_name> for <CopName>` でステージング)
- さらに fail なら draft 化

**(b) flaky** — ActiveRecord/Capybara のタイミング系、ネットワーク、時刻依存 etc. で diff と無関係
- `bundle exec rspec <failed_only>` で1回だけ再実行
- pass したら spec OK 扱い、なお落ちるなら draft で「flaky 疑い」記載

**(c) 環境** — gem 依存・DB migration 欠落・bundle install 失敗 etc.
- このセッションで修復不可。draft で「環境差分疑い」記載

#### Draft 判定基準
以下いずれかなら PR は `--draft` で作成:
- Tier 2 を使った
- Tier 3 を使った
- rubocop 再実行で違反残存
- 他copへの巻き込み回帰が発生
- A2 分類で (a) の追加パッチを当ててもなお fail 、(b) の再実行でも fail、(c) 環境問題

それ以外は通常 PR。

#### 2f. コミット
A2 (a) で追加パッチを当てた場合はそれも別コミットとして追加:
```
git add -A
git commit -m "$(cat <<'EOF'
refactor(rubocop): <CopName> の修正

<使ったコマンド> による修正。
対象ファイル数: <N>, 修正件数: <M>
EOF
)"
```

#### 2g. PR 作成 (本文は diff 解析でリッチ化)
本文生成前に `git diff origin/master..HEAD` を取得し、AI が以下を構築:
- 「主な変更パターン」の自然言語要約 (1～3 bullet)
- 修正例として before/after を 1～2件抽粋

PRタイトル: `rubocop自動修正: <CopName>`

```
git push -u origin HEAD
gh pr create [--draft] --base master --title "rubocop自動修正: <CopName>" --body "$(cat <<'EOF'
## 変更内容

\`<CopName>\` の違反 <M> 件を解消した (対象 <N> ファイル)。修正手段: \`<実行コマンド>\`。あわせて \`.rubocop_todo.yml\` から該当ブロックを削除した。

主な変更パターン:
- <AI が diff を読んで要約 1、3個>

修正例:
\`\`\`diff
<before/after スニペット 1～2件>
\`\`\`

本PRは Claude Code Routines (rubocop-daily-autocorrect) による自動生成。同日セッションで最大5本まで作成される。

## 確認方法

CI上の rubocop ジョブと RSpec ジョブが全てパスしていることを確認してください。

[draft の場合のみ末尾に追記:]
- Tier: <1/2/3>
- RSpec 結果: <pass数/fail数>
- A2 分類: <(a)修正起因 / (b)flaky / (c)環境 / N/A>
- 追加パッチ: <(a)のとき当てたパッチの説明、もしくは「なし」>
- AI 解析: <原因詳細>
```

### 3. セッション末尾のサマリ
作成した PR 本数、それぞれの CopName、A2分類結果、スキップしたcopと理由をログ出力して終了。

## 注意
- ループ内エラーは cop スキップでセッション中断しない
- ループ外エラーはセッション中断 OK
- 出力は最小限に
```

### 2. RuboCop TODO消化のウィークリーレポート生成

毎日作成されるPRの成果や、現在のTODOの減少傾向をエンジニアチーム全体へ可視化するため、週次でのレポート生成も自動化しています。

毎週1回、Claudeが以下のステップを自律的に実行します。

1. 過去7日間のPR集計: 作成数・マージ数・クローズ数・Draft数の集計に加え、「マージまでにかかった中央時間」や「解消されたCop（ルール）の上位5件」を算出します。
2. Revertの自動検出: `git log`から過去7日間に発生したRuboCop自動修正のRevertコミットを検知し、デグレードが発生していないかを監視します。
3. `.rubocop_todo.yml` の残件集計: 現時点のTODOファイルをパースし、Tier 1〜3および未着手ゾーン（offense数30件超の手動修正）の「残りのCop数」と「offense総数」を集計します。
4. バーンダウン（完了予測）の計算: 直近4週間の「週あたり解消Cop数の中央値」を自動計算。残りのTODOが「あと何週間で全消化できるか」「具体的な完了予定日はいつか」をリアルタイムに算出します。

これにより、単に「PRを投げて終わり」ではなく、「今週はマージまで〇時間だった」「このペースなら〇年〇月〇日にTODOが全滅する」というプロジェクトの進捗が、毎週自動的にGitHub Issueとしてドキュメント化されます。

![](https://static.zenn.studio/user-upload/3a428001d2d9-20260605.png)

Claude Code Routines スクリプト例（一部抜粋）

```
<リポジトリ名> の rubocop 自動修正ルーティン (rubocop-daily-autocorrect) の週次サマリを GitHub Issue として起票してください。週次の進捗可視化が目的です。

## 前提
- <リポジトリ名> の master ブランチが checkout 済みで開始
- gh, git, ruby 利用可能
- コード変更・PR作成はしない (読み取りと Issue 起票のみ)

## ステップ

### 1. 過去7日の PR 集計
```
since=$(date -d '7 days ago' --iso-8601)
gh pr list --search "rubocop自動修正 in:title created:>${since}" --state all --limit 100 --json title,state,mergedAt,closedAt,createdAt,number,isDraft
```
以下を集計:
- 作成数 (作成 PR 総数)
- merge済み (state == MERGED)
- close (no merge) (state == CLOSED && !mergedAt)
- open (state == OPEN)
- draft (isDraft == true の open)
- merge までの中央時間 (mergedAt - createdAt)
- 解消 cop 上位5件 (tilte から CopName を抽出し、mergeされたものをカウント)

複数ページ以上あれば適宜 `--limit` を上げる。

### 2. revert 検出
```
git fetch origin master --depth=200
git log origin/master --since="7 days ago" --grep="Revert.*rubocop自動修正" --pretty=oneline
```
検出された revert commit をリスト化。

### 3. .rubocop_todo.yml の残件集計

`.rubocop_todo.yml` をパースし、全 cop を分類:
- Tier 1 (safe autocorrect, Enabled不問, コメントに `safe autocorrection`)
- Tier 2 (unsafe autocorrect, コメントに `unsafe autocorrection`)
- Tier 3 (autocorrectなし or Enabled: false, offense count ≤ 30)
- その他 (autocorrectなしで offense > 30 のもの: 現状未着手ゾーン)

各ティアについて:
- cop 数
- offense count 総計

### 4. 完了予測
週次サマリ Issue の過去 4 本分を取り、週あたりの解消 cop 件数の中央値を計算 (1本目なら今週の merge数 をそのまま使う):
```
gh issue list --search "rubocop自動修正 週次サマリ in:title" --state all --limit 4 --json title,body,createdAt
```
中央値 N cop/週 をもとに、残りの Tier 1+2+3 合計 cop 数 ÷ N = W 週と、今日から W 週後の日付を推定。N=0 なら「予測不可」と出力。

### 5. Issue 起票
```
week_label=$(date '+%Y-%m-%d')
gh issue create --title "rubocop自動修正 週次サマリ (${week_label} の週)" --body "$(cat <<'EOF'
## 先週の成果 (<開始日>、<終了日>)

- 作成 PR: <N>本 (内 merge済み <M>本 / open <R>本 / close <P>本 / draft <D>本)
- 平均 merge 時間: <H>時間
- revert: <V>件 (<該当PR番号リスト、無ければ「none」>)

### 解消 cop 上位
1. <CopName> (<count>件)
2. ...

## 残件状況

| Tier | cop数 | offense総数 |
| --- | --- | --- |
| Tier 1 (safe) | <数> | <数> |
| Tier 2 (unsafe) | <数> | <数> |
| Tier 3 (manual, ≤30) | <数> | <数> |
| その他 (>30 で manual) | <数> | <数> |

### 完了予測

直近4週の中央値消化速度 <N> cop/週 → あと <W>週 で TODO 全消化見込み (着想 <日付>)

---
本Issueは Claude Code Routines (rubocop-weekly-summary) による自動生成。
EOF
)" --label automation --label rubocop || gh issue create --title "rubocop自動修正 週次サマリ (${week_label} の週)" --body "$(...)"
```
ラベル `automation` / `rubocop` が無ければラベルなしで fallback して issue を作ってください。

### 6. セッションサマリ
起票した Issue の URL と集計結果をサマリとして出力して終了。

## 注意
- コード・PRは一切変更しない
- Issue 重複は OK (同じタイトルに日付が含まれるため)
- gh コマンドがエラーならセッションをエラーログと出力して終了 (リトライしない)
- 1週間で1回実行されるルーティン
```

この定期的なレポート化によって、「開発を止めずに、データドリブンに負債が減っている」という事実を開発者自身が実感でき、かつチーム全体にも共有できるようになりました。

## ✅ まとめ

今回導入したClaude Code Routinesは、従来の命令型スクリプトでは難しかった「エラー時の試行錯誤」や「コンテキストに応じた修正」を可能にし、RuboCop TODO解消の運用コストを大きく下げてくれました。

さらに、週次のレポート生成によって完了予測（バーンダウン）を可視化したことで、チーム全体でデータドリブンに負債の減少を実感できる体制が整いました。

将来的にプロダクトがスケールしても耐えられるコードベースを維持するために、AI agentをどこまで業務に組み込めるか、今後も活用の幅を広げていきたいと考えています。

「unsafeなルールや手動修正が必要なTODOが溜まり続けている」「静的なスクリプトでの自動化に限界を感じている」といった、同じように技術負債の解消に悩まされている方の参考になれば幸いです。
