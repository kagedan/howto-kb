---
id: "2026-05-30-claude-code-skill-のベストプラクティス-公式仕様とコミュニティ-linter-で自-01"
title: "Claude Code skill のベストプラクティス ── 公式仕様とコミュニティ linter で自己レビューする"
url: "https://zenn.dev/gudezou/articles/9defb66939bc85"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "OpenAI"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

![サムネイル](https://static.zenn.studio/user-upload/25be38afb6ba-20260530.png)

* Claude Code 本体には、自作 skill が公式の仕様に沿っているかを自動で見てくれる linter (表記やルール違反を検査する道具) は付いていません。
* Anthropic の Skill authoring best practices ページには、`name` は64文字以内、`description` は1024文字以内、`SKILL.md` 本文は500行以内、という具体的な数字が載っています。
* もう一歩自動化したいときは、コミュニティ製の linter が複数並列で公開されているので、検査対象や検査ルールを見比べて自分の skill 構成に合うものを選びます。

---

## Claude Code 本体に skill 専用の linter は付いていない

Claude Code の Extend Claude with skills ページは、`SKILL.md` の構造を基準となる形で定めています。  
`frontmatter` の各フィールドと、本文 `markdown` の書式を1ページにまとめた仕様です。  
ただし、書式の違反やベストプラクティス逸脱を機械的に検出するコマンドは付属していません。

代わりに Anthropic の Skill authoring best practices ページが、ベストプラクティスを具体的な数字つきで列挙しています。  
こちらは「どこまで守れば skill として良い形になるか」を判断するための参照先です。

機械チェックを1コマンドで済ませたいときは、コミュニティ製の linter が選択肢になります。  
個人や小規模なチームが独自に複数の linter を公開しており、いずれも Anthropic 公式のリリースではありません。

![3層の役割分担: 公式 docs とコミュニティ製 linter](https://static.zenn.studio/user-upload/4ff582ff7f4e-20260530.png)

---

## 公式の数字と複数のコミュニティ製 linter で skill を点検する

1つ目は `name` フィールドです。  
Anthropic の Skill authoring best practices ページは、`name` は64文字以内と定めています。  
文字種は小文字と数字とハイフンだけで、予約語の `anthropic` と `claude` は含められません。

2つ目は `description` フィールドです。  
`description` は1024文字以内で、必ず三人称で書きます。  
`description` は `system prompt` に注入されるので、視点がブレると skill が見つかりにくくなる、と同ページが説明しています。  
他人の skill 集を読むときも、`description` が三人称かどうかが品質の目安になります。

3つ目は `SKILL.md` の本文行数です。  
本文は500行以内に収めると性能が出やすい、と同ページが推奨しています。  
超えそうなときは、別のリファレンスファイルに分けます。  
必要なときだけ読み込まれる `progressive disclosure` 型に組み替えるのが定石です。

4つ目は `disable-model-invocation` フィールドです。  
Claude Code の Extend Claude with skills ページは、このフィールドの役割を説明しています。  
`disable-model-invocation: true` を付けると、Claude が自分の判断ではこの skill を起動しなくなります。  
手動でだけ起動したい skill には付け忘れないようにします。  
スラッシュコマンドからの起動は、このフィールドの影響を受けずに従来どおり動きます。

5つ目は `paths` フィールドです。  
同ページは、`glob` パターンに一致するファイルを扱っているときだけ skill が自動で読み込まれる、と説明しています。  
特定のディレクトリに紐づく skill では、`paths` を書いておくと意図しない発火を防げます。

ここまでをまとめて検査したいときは、コミュニティ製の linter を使う選択肢があります。  
個人や小規模なチームが独自に linter を公開しています。  
検査対象 (skill 単体か、`CLAUDE.md` / agent / 設定まで横断するか) や検査ルール数はツールごとに違います。  
複数のツールを見比べて、自分の skill 構成に合うものを選びます。

![5項目チェックリスト:  /  / 本文行数 /  / ](https://static.zenn.studio/user-upload/66c8a579c842-20260530.png)

業界全体で見ると、Claude Code の skill 設計は層によって標準化の度合いが違います。  
skill から呼ぶ tool の規格である Model Context Protocol (MCP) は組織を跨いだ共通土台です。  
Anthropic が2024年11月に発表した後、OpenAI Agents SDK などが採用しています。  
一方で、`CLAUDE.md` や `SKILL.md` の置き場所と書式は Anthropic 独自の設計で、業界共通の決まりはありません。  
Cursor は `.cursor/rules` ディレクトリに `.mdc` ファイルを置く形式です。  
GitHub Copilot は `.github/copilot-instructions.md` という `Markdown` ファイルを置く形式です。  
linter についても業界共通のものはなく、複数のコミュニティ製ツールが並列に存在します。  
Anthropic 公式の skill linter は現時点では提供されていません。  
それぞれの読者が自分の skill 構成と相談して取捨選択することになります。

![業界共通の層 (MCP) と各社独自の層 (instruction file / linter)](https://static.zenn.studio/user-upload/3588e5e4ccd2-20260530.png)

---

## 参考文献

1. Anthropic. *Skill authoring best practices*. Anthropic Documentation. <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
2. Anthropic. *Extend Claude with skills*. Claude Code Documentation. <https://code.claude.com/docs/en/skills>
3. Anthropic. *Introducing the Model Context Protocol*. Anthropic News. <https://www.anthropic.com/news/model-context-protocol>
4. Cursor. *Rules*. Cursor Docs. <https://cursor.com/docs/context/rules>
5. GitHub. *Adding repository custom instructions for GitHub Copilot*. GitHub Docs. <https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot>
