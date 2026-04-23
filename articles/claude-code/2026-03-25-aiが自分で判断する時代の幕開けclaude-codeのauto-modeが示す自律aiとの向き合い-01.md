---
id: "2026-03-25-aiが自分で判断する時代の幕開けclaude-codeのauto-modeが示す自律aiとの向き合い-01"
title: "AIが自分で判断する時代の幕開け——Claude Codeの「auto mode」が示す、自律AIとの向き合い方"
url: "https://note.com/ai_curator/n/nfe6dbd31b330"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-03-25"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

![](https://assets.st-note.com/img/1774397293-Q5MwEd18eOthaoSsR2HKjG6N.png?width=1200)

2026年3月24日、Anthropicがある新機能をひっそりとリリースしました。Claude Codeへの「auto mode（オートモード）」追加です。チームプラン向けのリサーチプレビューとして公開されたこの機能、エンジニア以外の方にも知っておく価値があると思っています。

なぜかというと、これは「AIがどこまで自律的に動くべきか」という問いに、一つの実践的な答えを出そうとする試みだからです。

まずClaude Codeとは何か、簡単に整理しておきましょう。コマンドラインから操作するAIコーディングツールで、ファイルの編集、シェルコマンドの実行、テストの実施まで、開発作業をAIに任せられます。エンジニアにとっては「AIが隣に座って一緒に作業してくれる」感覚のツールです。

以前この場でも紹介しましたが、Claude Code責任者のBoris Cherny氏が「2ヶ月以上、一行もコードを手書きしていない」と語るほど、現役エンジニアたちの実務に深く根を張りつつあります。

ただ、「AIに任せる」スタイルには、ずっと解決されなかった摩擦がありました。Claude Codeは安全のため、ファイルを書き換えるたびに、コマンドを実行するたびに、ユーザーへの確認を求めます。作業が20ステップ以上になると、もはや人間がひたすら「承認ボタン」を押し続けるだけの時間になってしまう。

![](https://assets.st-note.com/img/1774397405-IBqLT4esayQH1gk2iNG9nPdx.png?width=1200)

そこで一部の開発者が使っていたのが「--dangerously-skip-permissions（危険を承知でパーミッションをスキップ）」というオプションです。名前そのままで、これはリスクの高い回避策です。大事なファイルを誤削除しても、外部に情報が送信されても、AIは止まらなくなります。

![](https://assets.st-note.com/img/1774397423-E5ByCfTY4ejtV8d9JD2aSXxO.png?width=1200)

auto modeは、この二択の間を埋める「第三の道」として設計されました。

![](https://assets.st-note.com/img/1774397432-wDVKm36zAbd2U5Bn4fWFExtG.png?width=1200)

仕組みはこうです。各操作が実行される前に、専用の分類器（classifier）が内容を評価します。大量ファイルの一括削除、機密データの外部送信、悪意あるコードの実行——そういったリスクの高い操作は自動的にブロックされます。問題がなければそのまま処理が進み、繰り返しブロックされる場合にだけユーザーへの確認を求める。

TechCrunchの報道によると、この機能はいわば注意深い請負業者のような振る舞いをするものとされています。明らかに安全な作業は迷わず進め、何か重大なものに触れる前には立ち止まる、という設計です。

![](https://assets.st-note.com/img/1774397450-ShieZO6nw9LQ42mqHzK5AbFU.png?width=1200)

Anthropicは「auto modeは、より少ない中断でより長いタスクを実行できる中間の道筋であり、パーミッションをすべてスキップするよりもリスクが低い」と説明しています。同時に「リスクを完全に排除するものではない」とも明記しており、隔離された環境での使用を推奨しています。この正直さが、Anthropicらしいところだと感じます。

![](https://assets.st-note.com/img/1774397465-YeqHX5zQLUbdkoDpxym7jIhc.png?width=1200)

現在はClaude Sonnet 4.6とOpus 4.6の両モデルに対応していて、CLIで「claude --enable-auto-mode」を実行し、その後Shift+Tabでオン・オフを切り替えられます。

もう一点、重要な安全機能として「プロンプトインジェクション対策」が組み込まれています。これは、処理するファイルやコマンド出力の中に悪意ある指示を埋め込み、AIをだまして不正な操作を承認させる攻撃手法です。Anthropicはこの保護が不完全であることも認めており、本番環境の認証情報や本物のAPIアクセス権限がある状態での使用は依然として避けるよう呼びかけています。

この設計思想の背景には、Anthropicが長年取り組んできた安全対策の積み重ねがあります。Anthropicのセーフガードチームは、ポリシー策定からモデルのトレーニング、リアルタイムの検知・執行まで複数の層で対策を講じており、分類器を複数並列で動かしてリアルタイムに有害な操作を検知する仕組みを構築しています。

![](https://assets.st-note.com/img/1774397483-kbuMfFyj2D5C0RgHGTBE6maI.png?width=1200)

auto modeにも同様の考え方が反映されています。ただし、分類器はトークン消費量、コスト、レイテンシにわずかながら影響を及ぼすため、大規模な自動パイプラインで使う場合は費用対効果を事前に見積もっておく必要があります。個人の試用レベルでは気にならない差ですが、チームで本格運用するなら念頭に置いておきたい点です。

企業にとって参考になるのは、管理者がMDMポリシーやファイルベースのOSポリシーを通じてauto modeを組織全体で無効化できる点です。新機能が便利でも、セキュリティポリシーとの兼ね合いで運用を絞り込む選択肢が用意されているのは、企業利用を真剣に考えている証拠でしょう。

リリース時点ではチームプランのユーザーがリサーチプレビューとして利用でき、エンタープライズとAPIユーザーへのアクセスは数日以内に順次展開予定とされています。

この機能がとくに興味深いのは、AIと人間の関係について一つの実装例を示している点です。「全部承認させる（安全だが遅い）」でも「全部任せる（速いが危ない）」でもなく、AIが自分でリスクを判断しながら、でも危険なところでは立ち止まる。人間の監督をゼロにするのではなく、本当に必要な場面だけに集中させる、という発想です。

![](https://assets.st-note.com/img/1774397506-up8vhQ6E3zeso5nTMZjdOqaY.png?width=1200)

「ヴァイブ・コーディング」という言葉が2025年のコリンズ辞書で今年の言葉に選ばれたほど、AIとともに作業するスタイルは急速に広まっています。その流れの中で、「どれだけAIを信頼し、どこで人間が確認するか」のバランス設計は、エンジニアだけでなく、あらゆる業務でAIを使う人に共通の課題になっていきます。

まだリサーチプレビューの段階ではありますが、auto modeはその問いに向き合うための具体的な参考事例として、注目しておく価値がありそうです。

![](https://assets.st-note.com/img/1774397514-bCUPK7v4J9OXFByQo8V0tAsL.png?width=1200)

---

[#生成AIキュレーター](https://note.com/hashtag/%E7%94%9F%E6%88%90AI%E3%82%AD%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%BF%E3%83%BC) [#Anthropic](https://note.com/hashtag/Anthropic) [#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#AIエージェント](https://note.com/hashtag/AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88) [#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#テック最前線](https://note.com/hashtag/%E3%83%86%E3%83%83%E3%82%AF%E6%9C%80%E5%89%8D%E7%B7%9A) [#AIセーフティ](https://note.com/hashtag/AI%E3%82%BB%E3%83%BC%E3%83%95%E3%83%86%E3%82%A3) [#ヴァイブコーディング](https://note.com/hashtag/%E3%83%B4%E3%82%A1%E3%82%A4%E3%83%96%E3%82%B3%E3%83%BC%E3%83%87%E3%82%A3%E3%83%B3%E3%82%B0) [#自律AI](https://note.com/hashtag/%E8%87%AA%E5%BE%8BAI)

---

## 参考記事

〇Anthropic hands Claude Code more control, but keeps it on a leash（2026年3月24日）

〇Anthropic Adds Auto Mode to Claude Code to Reduce Permission Prompts（2026年3月24日）

<https://www.macobserver.com/news/anthropic-adds-auto-mode-to-claude-code-to-reduce-permission-prompts/>

〇Anthropic Launches Auto Mode for Claude Code to Cut Developer Interruptions（2026年3月24日）

〇Building safeguards for Claude（2025年8月12日）

<https://www.anthropic.com/news/building-safeguards-for-claude>

〇コードを書かないエンジニアたち――Anthropic・OpenAIで起きている静かな革命（2026年2月8日）
