---
id: "2026-07-15-claude-codeでおなじみのagent-skillsmicrosoft-agent-frame-01"
title: "Claude CodeでおなじみのAgent Skills、Microsoft Agent Frameworkで正式版になった"
url: "https://zenn.dev/kazu_aiengineer/articles/agent-framework-skills-stable"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-07-15"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## 先に結論

* **Agent Skills**（`SKILL.md` にエージェント向けの手順書・スクリプト・資料をまとめて配る仕組み）が、Microsoft Agent Framework で **experimental 指定を卒業して正式版**になった
* .NET は 7/7、Python は 7/15 に公式ブログでリリース宣言。実体としては dotnet-1.13.0 / python-1.11.0 で experimental マーカーが除去されている
* 準拠しているのは Claude Code の Skills と同じオープン仕様（[agentskills.io](https://agentskills.io/)）。**Claude Code 向けに書き溜めた SKILL.md 資産を、自作の業務エージェントへ持ち込む道が公式にサポートされた**格好だ

## 何が起きたか

Microsoft Agent Framework（AutoGen と Semantic Kernel を統合した MS 製エージェント開発フレームワーク。2026年4月に [1.0 到達](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)）には、3月から experimental 扱いで Agent Skills 対応が入っていた。それが今月、.NET → Python の順で stable に切り替わった。

| 日付 | 出来事 | ソース |
| --- | --- | --- |
| 2026-03-02 | Agent Skills 対応の初出（experimental） | [公式ブログ](https://devblogs.microsoft.com/agent-framework/give-your-agents-domain-expertise-with-agent-skills-in-microsoft-agent-framework/) |
| 2026-07-03 | dotnet-1.13.0 で Skills API から Experimental 属性を除去 | [リリースノート](https://github.com/microsoft/agent-framework/releases/tag/dotnet-1.13.0)（[#6861](https://github.com/microsoft/agent-framework/pull/6861)） |
| 2026-07-07 | 「Agent Skills for .NET Is Now Released」公開 | [公式ブログ](https://devblogs.microsoft.com/agent-framework/agent-skills-for-net-is-now-released/) |
| 2026-07-10 | python-1.11.0 で Skills API の experimental マーカーを除去 | [リリースノート](https://github.com/microsoft/agent-framework/releases/tag/python-1.11.0)（[#6974](https://github.com/microsoft/agent-framework/pull/6974)） |
| 2026-07-15 | 「Agent Skills for Python Is Now Released」公開 | [公式ブログ](https://devblogs.microsoft.com/agent-framework/agent-skills-for-python-is-now-released/) |

Python 版のブログには「コアの Skills API に experimental ゲートはもうないので本番で使ってよい」と明言がある。プレビュー機能を本番に入れられなかったチームには、この一文が今回の実質的なニュースだと思う。

## Agent Skills を知らない人向けの最短説明

エージェントに「経費精算のやり方」「社内コーディング規約」のような**ドメイン知識を、プロンプト改修なしで後付けする**仕組みだ。実体はただのディレクトリで、中心にあるのは `SKILL.md` という Markdown ファイル。

```
expense-report/
├── SKILL.md                 # 必須: frontmatter + 手順書
├── scripts/
│   └── validate.py          # エージェントが実行できるスクリプト
├── references/
│   └── POLICY_FAQ.md        # 必要時だけ読まれる参照資料
└── assets/
    └── template.md          # テンプレート等の静的リソース
```

`SKILL.md` の frontmatter は `name` と `description` の2つが必須。この形式は Microsoft 独自ではなく、Claude Code などが採用しているオープン仕様 [agentskills.io](https://agentskills.io/specification) そのものだ（[Learn ドキュメント](https://learn.microsoft.com/en-us/agent-framework/agents/skills)にも仕様準拠が明記されている）。

| フィールド | 必須 | 内容 |
| --- | --- | --- |
| `name` | ✅ | 64字以内・小文字英数とハイフン。親ディレクトリ名と一致させる |
| `description` | ✅ | 1024字以内。「何をするスキルか・いつ使うか」。エージェントのスキル選択はここで決まる |
| `license` / `compatibility` / `metadata` | – | 任意メタデータ |
| `allowed-tools` | – | 事前承認済みツールのリスト。**これだけはまだ experimental** |

## 仕組みの肝は「段階的開示」

スキルを全部システムプロンプトに突っ込むとコンテキストが溢れる。Agent Skills は4段階の progressive disclosure でこれを避ける。

普段エージェントが払うコストはスキルあたり約100トークンの「見出し」だけで、本文・資料・スクリプトは使う瞬間まで読み込まれない。`SKILL.md` を500行以内に抑えて詳細は `references/` へ逃がせ、という公式ガイドもこの設計から来ている。

## 使い方の入口（Python）

ディレクトリを指すだけでスキルが自動発見される。[Learn ドキュメントのサンプル](https://learn.microsoft.com/en-us/agent-framework/agents/skills)から要点を抜くとこうなる。

```
from pathlib import Path
from agent_framework import Agent, SkillsProvider

# skills/ 配下の SKILL.md を持つサブディレクトリが自動発見される
skills_provider = SkillsProvider.from_paths(
    skill_paths=Path(__file__).parent / "skills",
)

agent = Agent(
    client=client,  # FoundryChatClient 等、任意のチャットクライアント
    instructions="You are a helpful assistant.",
    context_providers=[skills_provider],
)
```

ファイル置き場を用意できない場面のために、書き方は3通り用意されている。

| 方式 | クラス（Python） | 向いている場面 |
| --- | --- | --- |
| ファイルベース | `SkillsProvider.from_paths()` | 標準。Claude Code 等と資産を共用したい場合もこれ |
| クラスベース | `ClassSkill` | 社内 PyPI/NuGet でスキルをパッケージ配布したいチーム |
| インライン | `InlineSkill` + `SkillFrontmatter` | プロトタイピング、コード内で完結させたい小物 |

3方式とも同じプロバイダーに混載でき、実行時の挙動は変わらない。.NET は `AgentSkillsProvider`、さらに Go にも `agent/skills` パッケージがある。

## 本番向けと感じたのは承認モデル

Claude Code の Skills と使い勝手は同じでも、デフォルトの安全側の倒し方が違う。Agent Framework では **`load_skill`・`read_skill_resource`・`run_skill_script` の3ツールすべてが、デフォルトでホスト承認必須**になっている。承認が要るツール呼び出しはその場で実行されず、承認リクエストとして返ってくる。

そのうえで緩め方が段階的に用意されている。

* 読み取り系（load / read）だけ自動承認し、**スクリプト実行だけ人間の承認を残す**ルール（.NET の `ReadOnlyToolsAutoApprovalRule` など）
* 全部自動承認するルール、あるいは `from_paths()` のフラグで個別に無効化

外部から持ち込んだスキルに任意スクリプトが同梱される仕組みである以上、実行だけ承認ゲートを残す構成が現実的な落とし所だと私は見ている。

## preview 時代から使っていた人への注意点

experimental 卒業の直前に、互換性を壊す変更が入っている。python-1.11.0 の[リリースノート](https://github.com/microsoft/agent-framework/releases/tag/python-1.11.0)から2点。

1. **キャッシュの分離**: `SkillsProvider` 内蔵だったキャッシュ機構が `CachingSkillsSource` デコレーターに切り出された（[#6847](https://github.com/microsoft/agent-framework/pull/6847)）。TTL（`refresh_interval`）もこちらに付く
2. **ネストした SKILL.md の扱い変更**: スキルディレクトリ内の下層にある `SKILL.md` は、独立スキルではなく親スキルの一部として扱われるようになった（[#6849](https://github.com/microsoft/agent-framework/pull/6849)）。入れ子構成にしていた場合は発見のされ方が変わる

また、stable になったのは**コアの Skills API だけ**という点も押さえておきたい。

| 機能 | 2026-07-16 時点の状態 |
| --- | --- |
| Skills API（file / class / inline、承認モデル含む） | **stable**（.NET 1.13.0+ / Python 1.11.0+） |
| MCP サーバーからのスキル配信（`skill://` スキーム） | experimental（Python では `FutureWarning` が出る） |
| frontmatter の `allowed-tools` | experimental（実装間で挙動差の可能性あり） |

## どう受け止めたか

個人的に一番大きいのは互換性の話だ。Claude Code のヒットで「スキルを SKILL.md に書き溜める」習慣を持つエンジニアはこの半年でかなり増えた。その資産が、agentskills.io 仕様を介して **Foundry 上の業務エージェントや .NET 製の社内システムにそのまま流し込める**ようになった——ここに Microsoft が公式に乗った意味は大きいとみている。

一方で `allowed-tools` が experimental のまま残っている通り、「同じ SKILL.md がどの実装でも完全に同じ挙動をする」保証はまだない。特にスクリプト実行まわりは実行環境の前提が実装ごとに違うので、持ち込む際は承認モデルを厳しめにして小さく試すのが良さそうだ。

次はこの Skills を Foundry の Hosted Agents（[昨日の記事](https://zenn.dev/kazu_aiengineer/articles/foundry-hosted-agents-ga-check)で GA 判定を書いた）に載せて動かすところまで検証したい。

## 参考リンク（一次ソース）
