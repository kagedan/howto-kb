---
id: "2026-05-17-claude-codeのskillsは個人設定がプロジェクトに勝つ-01"
title: "Claude Codeの「Skills」は個人設定がプロジェクトに勝つ"
url: "https://qiita.com/yohei-aoki/items/8a98a630c98e7d0d4990"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

## 背景

[Claude Certified Architect](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request)について[こちらのGitHubでまとめられた学習ガイドライン](https://github.com/paullarionov/claude-certified-architect/blob/main/guide_ja.md#%E5%95%8F%E9%A1%8C36%E3%82%B7%E3%83%8A%E3%83%AA%E3%82%AAclaude-code%E3%81%AB%E3%82%88%E3%82%8B%E3%82%B3%E3%83%BC%E3%83%89%E7%94%9F%E6%88%90)を見ていたときのこと。Skillsの章で、こんな記述を見かけた。

> 個人スキルは同じ名前のプロジェクトスキルよりも優先されます。`~/.claude/skills/commit/SKILL.md`にある個人スキルはチームのプロジェクトスキルをオーバーライドする

一方、CLAUDE.mdはプロジェクトの指示がユーザーの指示より後に読み込まれるので、チームの標準が優先される設計だったはずだ。それなのにSkillsでは個人がプロジェクトに勝つのか。プロジェクトで作ったスキルを強制できないのは困るのでは？

## 公式ドキュメントの記載

### Skills の優先順位

Anthropicの[Skills公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code/skills)には、Skillsの格納場所と優先順位が以下のように記載されている。

| Location   | Path                                     | Applies to                     |
| :--------- | :--------------------------------------- | :----------------------------- |
| Enterprise | See managed settings                     | All users in your organization |
| Personal   | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects              |
| Project    | `.claude/skills/<skill-name>/SKILL.md`   | This project only              |
| Plugin     | `<plugin>/skills/<skill-name>/SKILL.md`  | Where plugin is enabled        |

そして、同名スキルの優先順位については、こう書いてある。

> （日本語訳）スキルがレベル間で同じ名前を共有する場合、**Enterpriseは個人をオーバーライドし、個人はプロジェクトをオーバーライドします。** プラグインスキルは`plugin-name:skill-name`の名前空間を使用するため、他のレベルと競合しません。
> [原文](https://docs.anthropic.com/en/docs/claude-code/skills)

確かに、個人スキルは同じ名前のプロジェクトスキルよりも優先されるようになっている。

### CLAUDE.md の優先順位

一方、[CLAUDE.mdに関する公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code/memory)には、CLAUDE.mdの読み込み順序が以下のように記載されている。

| Scope                | Location                               | Purpose                                             |
| -------------------- | -------------------------------------- | --------------------------------------------------- |
| Managed policy       | OS固有のパス                           | Organization-wide instructions managed by IT/DevOps |
| User instructions    | `~/.claude/CLAUDE.md`                  | Personal preferences for all projects               |
| Project instructions | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared instructions for the project            |
| Local instructions   | `./CLAUDE.local.md`                    | Personal project-specific preferences               |

そして、複数ファイルの扱いについては、こう書いてある。

> （日本語訳）発見されたすべてのファイルは、互いをオーバーライドするのではなく、**コンテキストに連結されます。** ディレクトリツリー全体で、コンテンツはファイルシステムのルートから作業ディレクトリの順に並べられます。（...）**Claudeを起動した場所に近い指示が最後に読み込まれます。**
[原文](https://docs.anthropic.com/en/docs/claude-code/memory)


ここで注意すべきなのは、公式ドキュメントは「連結される」「最後に読み込まれる」とは言っているが、**「後に読み込まれたほど優先度が高い」とは明言していない**ということだ。「overriding each other」ではないと明確に否定すらしている。

ただし、実質的にはプロジェクトのCLAUDE.mdはユーザーのCLAUDE.mdより後にコンテキストへ投入され、かつプロジェクト固有の具体的な指示を含むことが多い。Claudeの性質として具体的な指示ほど従いやすいのであれば、実質的にプロジェクトの指示がユーザーの指示より影響力を持つケースが多いと思われる。

## Skillsの優先順位は直感に反する

前述の通り、CLAUDE.mdの仕組みではプロジェクト固有の指示がユーザーの汎用的な指示より後にコンテキストへ投入され、実質的にはよりローカルな指示が優先されやすいと思われる。これは一般的なソフトウェアの設定解決（`.gitconfig`、`node_modules`、環境変数など）と同じ方向だ。

直感的にはSkillsも同じ方向、つまりプロジェクトのスキルが個人のスキルより優先されると思うだろう。しかし実際は逆で、個人のスキルがプロジェクトのスキルをオーバーライドする。

この挙動については、[GitHubのissue](https://github.com/anthropics/claude-code/issues/20309)でも「よりローカルなスキルが優先されるべきではないか」という議論がされている。

## まとめ

現状の仕様では、チームがプロジェクトに`.claude/skills/commit/SKILL.md`を用意していても、あるメンバーが`~/.claude/skills/commit/SKILL.md`を持っていると、そのメンバーだけプロジェクトのスキルが無視される。しかも、本人もチームもそのことに気付きにくい。

意図しないオーバーライドを避けるためには、プロジェクトのスキルにプロジェクト固有の接頭辞をつけて名前の衝突を防ぐのが現実的な対策になる。

```
# 汎用的な名前（衝突リスクあり）
.claude/skills/commit/SKILL.md

# プロジェクト固有の名前（衝突しにくい）
.claude/skills/myapp-commit/SKILL.md
```
