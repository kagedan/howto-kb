---
id: "2026-06-08-claude-code-tmux-でバックグラウンド実行とエージェント管理を整理する-01"
title: "Claude Code × tmux でバックグラウンド実行とエージェント管理を整理する"
url: "https://qiita.com/goki602/items/4a44eceb28c5cbbcbab6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "qiita"]
date_published: "2026-06-08"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

> 本記事は Claude Code(Anthropic)を活用して執筆しています。
> 検証可能な範囲で公開情報を整理したものですが、
> コード例等は実環境での動作確認をおすすめします。

AIコーディングエージェントに長時間タスクを任せるワークフローが普及するにつれ、「タスクを投げたまま離席できる環境」の整備が課題になってきた。そこで再注目されているのが、2007年から存在するターミナルマルチプレクサ **tmux** だ。2026年6月4日のはてブITで[tmuxがコーディングエージェントのランタイムになった背景を解説する記事](https://pasqualepillitteri.it/en/news/3493/tmux-runtime-coding-agents-2026)が267ブックマークを集めたことが、この関心の広がりを象徴している。

本記事は、**Claude Code × tmuxの組み合わせで何が解決するか**を公開情報から整理する。長時間エージェントタスクの管理方法を探している個人開発者・エンジニアが「tmuxを入れるかどうか」の判断材料にできることを目的とする。

## なぜ今 tmux が選ばれるのか

[DEV Communityの解説](https://dev.to/battyterm/how-tmux-became-the-runtime-for-ai-agent-teams-gmi)が整理している通り、tmuxの以下4つの特性がAIエージェント時代のニーズにそのまま当てはまる。

- **セッション継続性**: SSH接続が切れてもプロセスが生き続ける。クラウドVMでエージェントを走らせたまま帰宅できる
- **ペイン分割による可視化**: 複数エージェントを並列で動かし、それぞれの標準出力をリアルタイムで観察できる
- **対話型シェルの分離**: 通常の開発ターミナルとエージェント実行ペインを分けることで、誤ってエージェントへの入力を中断するリスクを下げられる
- **リソースオーバーヘッドの小ささ**: tmuxはCで書かれたPTYマルチプレクサで、1GB RAMのVMでもシステム負荷への影響は微小

「セッション継続性・並列可視化・プロセス隔離・リモートアタッチ」は、tmuxが2007年に設計されたときの要件とまったく同じで、それがそのままエージェントオーケストレーションの要件に一致している、というのが注目が高まっている背景だ。

## Claude Code との組み合わせパターン

Claude Code公式ドキュメントの[Agent Teams](https://code.claude.com/docs/en/agent-teams)では、`--teammate-mode tmux`オプションが記載されている。これを指定すると、研究・設計・実装など役割分担した複数のClaudeエージェントが、tmuxのペインにそれぞれ分かれて動作する。

実際の使い方は大きく3パターンに整理できる。

### パターン1: `/bg` コマンドでAgent Viewに流す

Claude Codeの`/bg`コマンドを使い、バックグラウンドセッションをAgent Viewで管理する方法。短時間かつシンプルなタスクには十分で、tmuxを別途用意する必要がない。接続元のターミナルウィンドウを閉じる場合などは次のパターンが安定する。

### パターン2: tmuxセッション内でインタラクティブ実行

tmuxセッションを作成して`claude`を起動し、`Ctrl-b d`でデタッチ。後からいつでも`tmux attach`で途中経過を確認できる。[Implicator.ai](https://www.implicator.ai/tmux-keeps-ai-coding-agents-running-for-days-after-you-disconnect/)が紹介しているように、この構成では数日間エージェントを動かし続けることが可能で、「夜に投げて朝確認」の運用に向く。

```bash
# セッション作成して claude を起動
tmux new-session -s agent-work -d
tmux send-keys -t agent-work 'claude' Enter

# 作業後にデタッチ (または Ctrl-b d)
# 後から再アタッチ
tmux attach -t agent-work
```

※ 上記コマンドはtmuxの一般的な操作手順。Claude Code固有の動作については[公式ドキュメント](https://code.claude.com/docs/en/agent-teams)を参照。

### パターン3: チームエージェント × tmuxペイン

`--teammate-mode tmux`を指定し、役割ごとに列ペインを配置する構成。各エージェントの出力がリアルタイムで流れるため、並列処理の進捗をひと目で把握できる。[クラスメソッドのブログ](https://dev.classmethod.jp/articles/shuntaka-claude-code-tmux-personal-tips/)では具体的なペイン配置の実践例が紹介されている。

## 注意点と制限

**tmuxはデフォルト未インストールの環境がある。** macOSでは`brew install tmux`、Debian/Ubuntuでは`apt install tmux`で導入できる。Windowsの場合はWSL2経由での利用になる。

**Agent Viewとの補完関係を意識する。** Claude CodeのAgent Viewは複数バックグラウンドセッションをGUIライクに一覧管理する機能で、tmuxとは排他でなく補完的な関係にある。「Agent Viewで俯瞰し、tmuxでロー出力を追う」という使い方が現実的だ。

**ペイン数が増えると管理コストも上がる。** 10ペインを超えると何が動いているかの把握が難しくなる。tmux-agentsのような管理ツールや、名前付きセッション(`tmux new -s agent-task-name`)の命名規則を決めておくことが推奨される。

**Claude Codeの`--teammate-mode`オプションの可用性はバージョンにより異なる。** 最新の対応状況は[公式リリースノート](https://github.com/anthropics/claude-code/releases)で確認するのが確実だ。

## まとめ

tmuxの「セッション継続・並列可視化・ゼロオーバーヘッド」という特性は、AIコーディングエージェントの「長時間・並列・途中確認」というニーズと相性がいい。Claude Codeを使い始めて「タスクを投げっぱなしにしたい」「複数エージェントを並べて動かしたい」と感じた段階で、tmuxの導入を検討する価値がある。公開事例が増えてきたら、具体的なセットアップを深掘りしたいところだ。
