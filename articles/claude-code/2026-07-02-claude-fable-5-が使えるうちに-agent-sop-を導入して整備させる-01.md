---
id: "2026-07-02-claude-fable-5-が使えるうちに-agent-sop-を導入して整備させる-01"
title: "Claude Fable 5 が使えるうちに Agent SOP を導入して整備させる"
url: "https://zenn.dev/ryu1maniwa25/articles/fable5-agent-sop-setup"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-07-02"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Fable 5 が復活しましたね。皆さん使ってみましたでしょうか。

筆者も Claude Code で使ってみましたが、明確に指示していないことでも適切な判断で進めてくれるため、使っていてとても気持ちが良かったです。  
ただ、サブスクプランで使えるのは 2026 年 7 月 7 日 (太平洋時間) まで、しかも週間利用上限の 50% までです。実際、筆者の環境では軽く使っただけで 5 時間あたりの制限の半分が消費されました。この記事を読まれている方の中には、既に利用制限が来てしまい使えなくなってしまった方がいるかもしれません。  
この限られた枠で何をやらせるかが重要となります。筆者の答えは Agent SOP の整備でした。コード生成の結果はいずれ書き換わりますが、手順書の整備なら期限後もチームの資産として残ります。

筆者の開発リポジトリには Claude Code に書かせてきた作業ログが 100 本以上あり、Claude Code が普段から繰り返し実施している手順が埋もれていました。これを Fable 5 に調査させて再利用可能な手順書として抽出させたところ、13 本の SOP が生成され、Claude Code の skill としてチーム全員が使える状態になりました。

この記事では Agent SOP の簡単な説明と導入方法、そして Fable 5 への頼み方を整理します。

## Agent SOP とは

SOP (Standard Operating Procedure) とは、誰がやっても同じ結果になるよう作業を文書化した標準作業手順書のことです。Agent SOP はその AI エージェント版で、AWS の Strands Agents チームが 2025 年 11 月に OSS として公開しました。Amazon 社内で 5,000 以上の SOP が使われていた仕組みの外部公開版です。

実体は `.sop.md` という拡張子のマークダウンファイルで、書式が標準化されています。必須セクションは Title、Overview、Parameters、Steps の 4 つ。特徴的なのは制約を RFC 2119 キーワード (You MUST / SHOULD / MAY) で書く点で、禁止事項 (MUST NOT) には必ず理由を添えるルールがあります。  
書式の実物として、組み込み SOP のひとつ code-assist の冒頭を引用します。

<https://github.com/strands-agents/agent-sop/blob/0da00cf5a88dd6a9c7ef60db0db6c8fd5bdfd15a/agent-sops/code-assist.sop.md#L1-L25>

CLAUDE.md や skills といった既存の仕組みとの違いも整理しておきます。CLAUDE.md は毎回コンテキストに注入されるため、手順を書き足すほど肥大化します。SOP は後述する skill 変換を経て、必要なときだけ読み込まれるオンデマンドの手順書になるので、恒常ルールを薄く保てます。

では skills とは何が違うのかというと、実行時の能力は同じで、違いは書く側にあります。skills の仕様は本文の書き方を何も定めていませんが、Agent SOP は必須セクションや「禁止には理由を添える」といった品質の規範と validator を持ち、1 つのファイルから skills や MCP prompts、Cursor commands を生成できます。CLAUDE.md から手順を切り出す先であり、skill の中身を標準化する層、というのが Agent SOP の位置づけです。

## インストールと Claude Code での使い方

組み込みの SOP (TDD 実装の code-assist、設計の pdd など 5 本) を試すだけなら、plugin marketplace 経由の 2 コマンドで済みます。

```
claude plugin marketplace add strands-agents/agent-sop
claude plugin install agent-sops@agent-sop
```

これで `/code-assist` や `/pdd` がスラッシュコマンドとして使えるようになります。SOP を自作するための公式 skill `agent-sop-author` も同梱されます。

自作 SOP をプロジェクトで使う方法は 2 つあります。どちらも SOP ファイルはリポジトリの `agent-sops/` ディレクトリに置きます。

1 つ目は MCP server 方式で、リポジトリ直下の `.mcp.json` に登録します。

.mcp.json

```
{
  "mcpServers": {
    "agent-sops": {
      "command": "uvx",
      "args": ["strands-agents-sops", "mcp", "--sop-paths", "agent-sops"]
    }
  }
}
```

`agent-sops/` に SOP を置くだけで (変換なしで) 反映されるのが利点ですが、メンバーごとに MCP server の初回承認が必要になります。

2 つ目は skill 変換方式です。SOP を Claude Code の skill 形式に変換してコミットします。

```
uvx strands-agents-sops skills --sop-paths ./agent-sops --output-dir .claude/skills
```

変換コマンドを 1 回挟むだけで、clone した全員が追加セットアップも承認もなしで skill を使えます。組み込み 5 本も一緒に生成されるので、まとめてコミットすればチームは plugin install すら不要になります。変換は静的コピーなので、SOP を編集したら再実行が必要です。筆者は再変換をシェルスクリプト 1 本にまとめて運用しています。公式リポジトリ自身はこの再生成を [GitHub Actions で自動化している](https://github.com/strands-agents/agent-sop/blob/main/.github/workflows/publish-skills.yml)ので、編集頻度が上がったらそれに倣うのが良さそうです。

## Fable 5 への頼み方

ここからが本題で、この整備を人間がやらずに Fable 5 へ丸投げします。前提として、筆者のプロジェクトでは日頃から作業セッションの終わりに Claude Code へ作業ログ (worklog) を書かせていました。デプロイ手順、ハマった原因、回避策がコマンドレベルで記録されており、この蓄積がそのまま SOP の抽出元になりました。

意識したのは、作業手順を細かく指示するのではなく「仕様 + 素材 + 検証方法」を渡して設計判断ごと任せることです。実際に使ったプロンプトを汎用化すると次のようになります。

```
Agent SOP (https://github.com/strands-agents/agent-sop) をこのプロジェクトに整備してください。

1. Agent SOP の仕様を一次ソース (リポジトリの spec と README) で調査する
2. 過去の作業記録をすべて読み、複数回繰り返されている作業や、今後確実に
   再実施される手順を抽出する。対象は docs/worklog/ のような作業ログ、
   なければ git log や PR の説明文、issue を使う。純粋な調査レポートや
   戦略文書は手順ではないので除外する
3. 抽出した候補から再利用頻度の高いものを選び、agent-sops/ に .sop.md として
   作成する。作業記録に残っている失敗やハマりポイントを Constraints の理由として
   埋め込むこと
4. チーム全員が Claude Code から使える配布方法を調査して導入する
5. 公式の書式検証を通し、結果を報告する
```

## Fable 5 は何をしたか

このプロンプトに対して Fable 5 が実際にやったことを挙げます。

まず調査を並列化しました。仕様の一次ソース調査と作業ログの読解を複数の subagent に分割して同時に走らせ、100 本超のログから約 40 の手順候補を抽出したうえで、「複数回繰り返されている」「今後確実に再実施される」ものだけに絞り込みました。採用されたのはデプロイ、DB migration、staging 環境の追加、モデルのベンチマーク、公開前セキュリティレビューといった顔ぶれです。

次に、指示していない設計判断をいくつも行いました。たとえば作成した SOP の 1 つが Claude Code の組み込み skill と同名だと自分で気づいて改名しました。配布方式も MCP と skill 変換の両方を調査して比較し、チーム共有に向く後者を選んで理由とともに提案してきました。

成果物の質を支えているのは、作業ログの失敗が禁止事項の「理由」として埋め込まれている点です。

```
**Constraints:**
- You MUST NOT add or change `primary_location_hint` on an existing D1 in Terraform,
  because the attribute is create-only and the plan becomes destroy+recreate (データ全損)
```

一般論の手順書ではなく、「このプロジェクトで実際に踏んだ罠」が制約の根拠になっています。これは過去ログを素材として渡したからこそ出てくる内容で、人間がゼロから書くと抜け落ちる部分です。

最後に公式の `agent-sop-author` skill で全 SOP を点検していました。Parameters セクションに公式が要求する定型文言が欠けているという不備を自分で見つけて修正し、最終的に公式 validator で 13 本すべてをエラーゼロで通しています。書きっぱなしにせず、公式の検証手段を探してきて自分の仕事を採点させる、という動きが印象的でした。

## まとめ

Agent SOP は「エージェントにやらせたい定型作業」を標準書式の手順書にして、skill や MCP として配布できる仕組みです。そしてその整備を今しか使えない Claude Fable 5 にやらせることで、利用期限終了後も成果物をチームの資産として残すことができます。

Fable 5 が使えるうちに試すのが一番ですが、この頼み方自体はモデルを選びません。まずは自分のプロジェクトの作業ログや git log を読ませて、何が SOP になり得るかを聞いてみてください。
