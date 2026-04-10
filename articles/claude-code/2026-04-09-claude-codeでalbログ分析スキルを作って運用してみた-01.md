---
id: "2026-04-09-claude-codeでalbログ分析スキルを作って運用してみた-01"
title: "Claude CodeでALBログ分析スキルを作って運用してみた"
url: "https://zenn.dev/dely_jp/articles/82c25c727be94e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

はじめに
こんにちは、クラシルでクラシルリテールネットワークの開発をしている akawai11 です。
ALBのアクセスログを定期的に分析する必要があるのですが、これが毎回結構な手間になっていました。
ALBのアクセスログ機能を有効化し、S3に保存しています。
実作業としてはS3からログをダウンロードして、解凍して、集計する。
やること自体は毎回ほぼ同じなのに、都度CLIでコマンドを組み立てていました。期間指定を変えてダウンロードして、パスのフィルタを調整して、集計軸を変えたりといった作業が定常化していたんです。
今回、この分析作業をClaude Codeのスキルとしてまとめました。...
