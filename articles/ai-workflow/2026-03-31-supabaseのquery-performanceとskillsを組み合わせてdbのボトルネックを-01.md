---
id: "2026-03-31-supabaseのquery-performanceとskillsを組み合わせてdbのボトルネックを-01"
title: "SupabaseのQuery PerformanceとSkillsを組み合わせてDBのボトルネックを解消しよう！"
url: "https://zenn.dev/sasatech/articles/5ecd2b229dc7e1"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

こんにちは。株式会社SasaTechの佐々木です。

SasaTechでは、SupabaseとVercelをインフラとした、アプリケーションの開発を得意としています。

直近で、SupabaseのQuery Performanceと、[supabase-postgres-best-practices](https://skills.sh/supabase/agent-skills/supabase-postgres-best-practices)を使用して、SQLの処理速度を高速化した際のナレッジを記載します。

## Supabase Postgres Best Practices

該当リポジトリで以下のコマンドを実行する。

`npx skills add https://github.com/supabase/agent-skills --skill supabase-postgres-best-practices`

<https://skills.sh/supabase/agent-skills/supabase-postgres-best-practices>

## Query Performance

Supabaseの管理画面のObservability > Query Performanceから見ることが出来ます。

![](https://static.zenn.studio/user-upload/73685b62e2e2-20260331.png)

Index Advisorをオンにして、「Copy as markdown」でコピー。  
![](https://static.zenn.studio/user-upload/fa3fd871f98a-20260331.png)

## Claude Code

Supabase Postgres Best PracticesをSkillsとして登録している環境  
Query PerformanceでコピーしたMarkdownをClaude Codeにペースト

![](https://static.zenn.studio/user-upload/cd61bc117b6a-20260331.png)

あとはいい感じにmigrationファイルを作成してくれます😄
