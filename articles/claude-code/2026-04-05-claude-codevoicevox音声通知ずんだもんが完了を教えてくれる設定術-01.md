---
id: "2026-04-05-claude-codevoicevox音声通知ずんだもんが完了を教えてくれる設定術-01"
title: "Claude Code×VOICEVOX音声通知｜ずんだもんが完了を教えてくれる設定術"
url: "https://zenn.dev/kobarutosato/articles/938fd0df1d22aa"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

Claude Codeで長いタスクを投げて、別の作業をしている。
ふと気づくと、もう終わっていた。
いつ終わったかわからない。
この「気づかない問題」、音声通知で解決できます。
Claude CodeのHooks機構を使えば、タスク完了のたびにVOICEVOXで音声を鳴らせます。
ずんだもん、春日部つむぎ、ナースロボなど5キャラがランダムで「できました！」と教えてくれる。
この記事でわかること：

Claude Code Stop Hook の仕組みと設定方法
VOICEVOX APIの2段階呼び出し（audio_query → synthesis）

ランダムキャラ選択で毎回違う声を鳴...
