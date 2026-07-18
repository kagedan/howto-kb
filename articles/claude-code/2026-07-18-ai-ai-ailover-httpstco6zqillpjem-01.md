---
id: "2026-07-18-ai-ai-ailover-httpstco6zqillpjem-01"
title: "@ai_ai_ailover: https://t.co/6ZQIlLpjEM"
url: "https://x.com/ai_ai_ailover/status/2078421184962572401"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "cowork", "x"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-x"
query: "Cowork スケジュール OR Cowork スキル作成 OR Cowork 自動化"
---

https://t.co/6ZQIlLpjEM


--- Article ---
Claude Codeは、コードを書かせるだけでも強い。しかし、実務で本当に時間を奪うのは、実装そのものだけではない。過去の意思決定を探す、仕様を整理する、SQLを書く、デザインをレビューする、リリース前の確認をする、契約書やPDFを読む、関係者向けの報告を作る。開発者やプロダクトチームの仕事は、コードの外側に大きく広がっている。

そこで使えるのがClaudeの公式プラグインだ。

今回扱うのは、Claude Code CLI専用マーケットプレイスの開発系プラグインではない。画像にあるClaude Desktopの「ディレクトリ → プラグイン → Anthropic」タブから選べる、Anthropic公式の業務別プラグインである。具体的にはEngineering、Product Management、Data、Design、Enterprise Search、PDF Viewerなどだ。

これらは主にClaude DesktopのChatやCowork向けに提供されているが、Anthropicの公式リポジトリではClaude Codeでも動作すると案内されている。同じパッケージをClaude Code側へ導入すれば、スキルやスラッシュコマンド、MCPコネクタを開発ワークフローへ持ち込める。つまり「デスクトップで見つけられる公式プラグインを、Claude Codeでも使う」というのが本記事の前提だ。

2026年7月18日現在、プラグインはPro、Max、Team、Enterpriseの有料プランで利用できる。プラグインにはスキル、コネクタ、サブエージェントなどがまとめられており、インストールしたスキルはWeb版のチャット、Claude DesktopのChat、Coworkで利用できる。一方、フックやサブエージェントはCowork限定のものもあるため、「どこで何が動くか」はプラグインごとに確認したい。

本記事では、単に機能が多いものではなく、開発者、プロダクトマネージャー、デザイナー、技術責任者、個人開発者が実務で繰り返し使えるかを基準に10本を選んだ。

## まず知っておきたい導入方法

Claude Desktopでは、左サイドバーの「カスタマイズ」を開き、「プラグイン」タブから「＋」を押してディレクトリを表示する。その後「Anthropic」タブを選び、対象カードの「＋」またはInstallを押せばよい。インストール後は、入力欄で「/」を打つか「＋」メニューを開くと、追加されたスキルやコマンドを確認できる。

Claude Codeで同じプラグインを使う場合は、公式のKnowledge Workマーケットプレイスを追加し、個別にインストールする。

claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin install engineering@knowledge-work-plugins

engineering の部分を data、design、product-management などへ変えればよい。導入後はスキルが必要な場面で自動的に参照され、明示的なコマンドは /engineering:review や /data:write-query のように名前空間付きで呼び出せる。

なお、プラグインによってはローカルMCPサーバーを起動したり、Google Drive、Slack、GitHub、Figmaなどの外部サービスへ接続したりする。ローカルMCPは通常のプログラムと同等の権限で端末上を動く場合があるため、提供元、要求権限、接続先、書き込みの有無は必ず確認しておきたい。

## 1. Engineering｜まず入れるべき開発チームの基本セット

最優先で入れたいのがEngineeringだ。対象範囲は、スタンドアップ、コードレビュー、デバッグ、アーキテクチャ判断、インシデント対応、デプロイ前確認、技術ドキュメントまで広い。Claude Codeを単なる実装担当ではなく、開発プロセス全体を支える相棒として使うための土台になる。

用意されている代表的なコマンドは、変更内容をレビューする /engineering:review、再現・切り分け・原因特定・修正を順番に進める /engineering:debug、ADR形式で技術判断を整理する /engineering:architecture、障害対応を支援する /engineering:incident、リリース前の抜け漏れを確認する /engineering:deploy
